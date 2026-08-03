"""Board-meeting close tests. The gap discovered 2026-08-03: a meeting
'resolved' a price escalation in free text while the live price never
changed, because commit_close never checked EscalationItem.action_ref or
called the executor. These tests lock in the fix: whether a live action
executes must come from the CEO's structured ruling (record_ruling),
never from LLM-synthesized "Resolved Escalations" prose."""

from __future__ import annotations

import pytest

from brain.actions.limits import AgentLimits
from brain.actions.models import ActionIntent, ActionType
from brain.executor import Executor
from brain.meeting import AgendaItem, MeetingSession, run_ingest
from brain.models import DepartmentConfig
from tests.fake_connector import FakeConnector
from tests.fake_llm import FakeLLM

FAKE_REGISTRY = {
    "fake.set_price": ActionType(
        name="fake.set_price",
        connector="fake",
        params={"target_id": "str", "new_value": "float"},
        snapshot_params=("target_id",),
    ),
}


@pytest.fixture
def agent_config(config):
    config.departments["storefront"] = DepartmentConfig(
        name="storefront", tier=1, status="active", report_cadence="weekly"
    )
    return config


@pytest.fixture
def prompted(agent_config, tmp_hq_root):
    """Charter + prompt files run_ingest's build_system_blocks needs."""
    (tmp_hq_root / "charter" / "company.md").write_text("# Charter", encoding="utf-8")
    (tmp_hq_root / "charter" / "tiers.md").write_text("# Tiers", encoding="utf-8")
    prompts = agent_config.prompts_root
    prompts.mkdir(parents=True, exist_ok=True)
    for name in ("system_core.md", "ingest.md", "meeting_synthesis.md"):
        (prompts / name).write_text(f"# {name}", encoding="utf-8")
    return agent_config


def make_executor(hq, connector=None, tmp_path=None):
    limits = {"storefront": AgentLimits(allowed_actions=[])}  # absent -> always escalates
    return Executor(
        hq=hq, registry=FAKE_REGISTRY, limits=limits, capabilities={},
        connectors={"fake": connector} if connector else {},
        capabilities_path=(tmp_path / "capabilities.yaml") if tmp_path else None,
        env={},
    )


def reject_a_price_action(hq, tmp_path, new_value=19.5, rationale="Reprice needed"):
    """Real reject-and-escalate flow, mirroring the actual price-escalation
    path: submit -> rejected (not in allowed_actions) -> escalation filed
    with action_ref set. Returns (executor, connector, escalation_id, action_id)."""
    connector = FakeConnector()
    ex = make_executor(hq, connector=connector, tmp_path=tmp_path)
    rejected = ex.submit(ActionIntent(
        agent="storefront", action_type="fake.set_price",
        params={"target_id": "P1", "new_value": new_value}, rationale=rationale,
    ))
    assert rejected.result == "rejected"
    esc = next(e for e in hq.read_escalation_queue() if e.action_ref == rejected.id)
    return ex, connector, esc.id, rejected.id


EMPTY_SYNTHESIS_SECTIONS = {
    "Minutes": "The meeting happened.",
    "Decision Log Entries": "",
    "Directive Updates": "",
    "Resolved Escalations": "None.",
}


def prepared(sections=None):
    return {
        "sections": sections or dict(EMPTY_SYNTHESIS_SECTIONS),
        "entries": [],
        "updates": {},
        "warnings": [],
        "pending_ratifications": [],
        "missing_sections": [],
    }


class TestInjectEscalationDecisions:
    def test_forces_ceo_required_decision_when_llm_ignores_escalation(self, hq, prompted, tmp_path):
        _, _, esc_id, _ = reject_a_price_action(hq, tmp_path)
        agenda_no_mention = (
            "# Board Meeting Agenda — W1\n\n## Department Syntheses\n\n"
            "### storefront\n\nNothing notable.\n\n"
            "## Cross-Department Notes\n\nNone.\n\n"
            "## Proposed Decisions\n\n"
            "#### Decision: Unrelated housekeeping\n"
            "- Recommendation: Tidy up.\n"
            "- Checklist: money=no, brand=no, legal=no, irreversible=no\n"
            "- Tag: [BRAIN DECIDES]\n\n"
            "## Escalation Triage\n\n### Urgent\n- None.\n### This Meeting\n- None.\n### Defer\n- None.\n"
        )
        llm = FakeLLM(responses=[agenda_no_mention])
        run_ingest(hq, llm, prompted, print_fn=lambda s: None)

        session = MeetingSession(llm, prompted, hq)
        items = session.load_agenda()
        injected = next((i for i in items if i.escalation_ref == esc_id), None)
        assert injected is not None, "escalation with a pending action must always be ruled on"
        assert injected.tag == "CEO REQUIRED"

    def test_no_duplicate_when_llm_already_included_it(self, hq, prompted, tmp_path):
        _, _, esc_id, _ = reject_a_price_action(hq, tmp_path)
        agenda_with_mention = (
            "# Board Meeting Agenda — W1\n\n## Department Syntheses\n\n"
            "### storefront\n\nNothing notable.\n\n"
            "## Cross-Department Notes\n\nNone.\n\n"
            "## Proposed Decisions\n\n"
            f"#### Decision: Approve pending action for {esc_id}\n"
            "- Recommendation: Do it.\n"
            "- Checklist: money=yes, brand=no, legal=no, irreversible=no\n"
            "- Tag: [CEO REQUIRED]\n"
            f"- Escalation ref: {esc_id}\n\n"
            "## Escalation Triage\n\n### Urgent\n- None.\n### This Meeting\n- None.\n### Defer\n- None.\n"
        )
        llm = FakeLLM(responses=[agenda_with_mention])
        result = run_ingest(hq, llm, prompted, print_fn=lambda s: None)
        text = result["path"].read_text(encoding="utf-8")
        assert text.count(f"Escalation ref: {esc_id}") == 1


class TestCommitCloseExecution:
    def _ruled_session(self, hq, config, esc_id, action):
        session = MeetingSession(FakeLLM(), config, hq)
        session.items = [AgendaItem(
            id=0, title=f"Approve pending action for {esc_id}",
            block_text=f"#### Decision: Approve pending action for {esc_id}\n"
                       f"- Escalation ref: {esc_id}\n",
            tag="CEO REQUIRED", escalation_ref=esc_id,
        )]
        session.record_ruling(0, action)
        return session

    def test_approve_executes_via_executor_and_resolves(self, hq, agent_config, tmp_path):
        ex, connector, esc_id, _ = reject_a_price_action(hq, tmp_path)
        session = self._ruled_session(hq, agent_config, esc_id, "approve")

        summary = session.commit_close(prepared(), executor=ex)

        assert [c[0] for c in connector.calls] == ["read_state", "execute"]
        assert esc_id not in [e.id for e in hq.read_escalation_queue()]
        resolved = next(e for e in hq.read_resolved_escalations() if e.id == esc_id)
        assert "executed" in resolved.resolution
        assert len(summary["executed_actions"]) == 1
        assert summary["escalations_resolved"] == 1

    def test_reject_denies_without_executing(self, hq, agent_config, tmp_path):
        ex, connector, esc_id, _ = reject_a_price_action(hq, tmp_path)
        session = self._ruled_session(hq, agent_config, esc_id, "reject")

        summary = session.commit_close(prepared(), executor=ex)

        assert connector.calls == []
        resolved = next(e for e in hq.read_resolved_escalations() if e.id == esc_id)
        assert "denied" in resolved.resolution
        assert summary["executed_actions"] == []
        assert summary["escalations_resolved"] == 1

    def test_no_double_resolution_with_free_text_section(self, hq, agent_config, tmp_path):
        ex, connector, esc_id, _ = reject_a_price_action(hq, tmp_path)
        session = self._ruled_session(hq, agent_config, esc_id, "approve")
        sections = dict(EMPTY_SYNTHESIS_SECTIONS)
        sections["Resolved Escalations"] = f"{esc_id}: also mentioned here"

        summary = session.commit_close(prepared(sections), executor=ex)

        resolved = [e for e in hq.read_resolved_escalations() if e.id == esc_id]
        assert len(resolved) == 1
        assert summary["escalations_resolved"] == 1
        assert not any("not found" in w or "skipped" in w for w in summary["warnings"])

    def test_executor_none_skips_gracefully(self, hq, agent_config, tmp_path):
        _, connector, esc_id, _ = reject_a_price_action(hq, tmp_path)
        session = self._ruled_session(hq, agent_config, esc_id, "approve")

        summary = session.commit_close(prepared(), executor=None)

        assert connector.calls == []
        assert esc_id in [e.id for e in hq.read_escalation_queue()]  # still open
        assert summary["executed_actions"] == []
        assert summary["escalations_resolved"] == 0

    def test_modify_falls_through_to_free_text_path(self, hq, agent_config, tmp_path):
        ex, connector, esc_id, _ = reject_a_price_action(hq, tmp_path)
        session = self._ruled_session(hq, agent_config, esc_id, "modify")
        sections = dict(EMPTY_SYNTHESIS_SECTIONS)
        sections["Resolved Escalations"] = f"{esc_id}: CEO wants a different number, follow up"

        summary = session.commit_close(prepared(sections), executor=ex)

        assert connector.calls == []  # never replays approve_action on "modify"
        resolved = next(e for e in hq.read_resolved_escalations() if e.id == esc_id)
        assert "different number" in resolved.resolution
        assert summary["executed_actions"] == []
