"""Command-bar endpoint tests: ingest, meeting flow, consult, directive,
agent, help — FakeLLM only."""

from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

from brain.actions.limits import AgentLimits
from brain.actions.models import ActionIntent, ActionType
from brain.dashboard.app import create_app
from brain.dashboard.chat import register_chat_routes
from brain.executor import Executor
from brain.hq import HQ
from brain.meeting import MeetingSession, render_rulings
from brain.models import DepartmentConfig, MeetingRuling
from tests.fake_connector import FakeConnector
from tests.fake_llm import FakeLLM
from tests.test_sync_and_discuss import git, synced_repos  # noqa: F401 (fixture)


class DashFakeLLM(FakeLLM):
    def stream(self, system_blocks, user_message, max_tokens=1024):
        text = self.call(system_blocks, user_message, max_tokens)
        for i in range(0, len(text), 9):
            yield text[i:i + 9]

    def call_with_web_search(self, system_blocks, user_message,
                             max_tokens=8192, max_searches=8,
                             extra_tools=None, tool_executor=None):
        return self.call(system_blocks, user_message, max_tokens)


AGENDA = """# Board Meeting Agenda — WEEK

## Department Syntheses

### market_intel

The department found competitors circling and quantified trademark costs.

## Proposed Decisions

#### Decision: Approve the sticker
- Recommendation: Ship it.
- Checklist: money=no, brand=no, legal=no, irreversible=no
- Tag: [BRAIN DECIDES]

#### Decision: File the trademark
- Recommendation: File now.
- Checklist: money=yes, brand=yes, legal=yes, irreversible=no
- Tag: [CEO REQUIRED]

## Escalation Triage

### Urgent
- None.
"""

SYNTHESIS = """## Minutes

The meeting happened.

## Decision Log Entries

### Approve the sticker
- Rationale: fine. Dissents: none
- Decided by: brain (ratified at board meeting)
- Affected departments: none

## Directive Updates

None.

## Resolved Escalations

None.
"""


def parse_sse(text):
    return [json.loads(line[6:]) for line in text.split("\n\n") if line.startswith("data: ")]


@pytest.fixture
def env(config, hq, tmp_hq_root):
    (tmp_hq_root / "charter" / "company.md").write_text("# Charter", encoding="utf-8")
    (tmp_hq_root / "charter" / "tiers.md").write_text("# Tiers", encoding="utf-8")
    (tmp_hq_root / "directives" / "market_intel.md").write_text(
        "# Directive: Market Intel\n\nLast updated: 2026-07-16\n\n"
        "## Tier\n\nTier 0 — Read-only\n\n## Status\n\nactive\n", encoding="utf-8"
    )
    (tmp_hq_root / "directives" / "creative.md").write_text("# D", encoding="utf-8")
    prompts = config.prompts_root
    prompts.mkdir(parents=True, exist_ok=True)
    for name in ("system_core.md", "ask.md", "ingest.md", "meeting_synthesis.md",
                 "discussion.md", "consult.md", "directive.md", "agent_core.md",
                 "boardroom_participant.md"):
        (prompts / name).write_text(f"# {name}", encoding="utf-8")
    return config, hq


def make_client(env, responses):
    config, hq = env
    llm = DashFakeLLM(responses=responses)
    app = create_app(config, hq)
    register_chat_routes(app, config, hq, make_llm=lambda command=None: llm)
    return TestClient(app), llm


class TestIngestCommand:
    def test_writes_agenda_and_reports_summary(self, env, hq):
        client, _ = make_client(env, [AGENDA])
        response = client.post("/api/command/ingest")
        events = parse_sse(response.text)
        final = events[-1]
        assert final["done"] is True
        assert final["decisions"] == 2
        agenda_path = hq.root / "meetings" / f"{hq.current_week_key()}-agenda.md"
        assert agenda_path.exists()
        # The CEO must be SHOWN the agenda, not a receipt for it.
        assert "Approve the sticker" in final["agenda"]


class TestMeetingFlow:
    def _start(self, client):
        return client.post("/api/meeting/start").json()

    def test_start_requires_agenda(self, env):
        client, _ = make_client(env, [])
        assert client.post("/api/meeting/start").status_code == 404

    def test_full_flow_writes_records(self, env, hq):
        config, _ = env
        hq.write_agenda(hq.current_week_key(), AGENDA)
        client, _ = make_client(env, [SYNTHESIS])

        data = self._start(client)
        assert [i["title"] for i in data["items"]] == ["Approve the sticker", "File the trademark"]
        assert data["items"][1]["tag"] == "CEO REQUIRED"
        # Briefing = evidence before rulings: syntheses + triage, no decision blocks
        assert "competitors circling" in data["briefing"]
        assert "Escalation Triage" in data["briefing"]
        assert "#### Decision" not in data["briefing"]

        assert client.post("/api/meeting/ruling",
                           json={"item_id": 0, "action": "approve"}).json() == {"recorded": True}
        assert client.post("/api/meeting/ruling",
                           json={"item_id": 1, "action": "modify", "note": "file next week"}).status_code == 200

        result = client.post("/api/meeting/close", json={"ratifications": {}}).json()
        assert result["decisions"] == 1
        assert result["escalations_resolved"] == 0
        assert hq.read_decisions()[-1].title == "Approve the sticker"
        minutes = (hq.root / "meetings" / f"{hq.current_week_key()}-minutes.md").read_text(encoding="utf-8")
        assert "The meeting happened." in minutes
        # Session cleared
        assert client.post("/api/meeting/ruling",
                           json={"item_id": 0, "action": "approve"}).status_code == 409

    def test_discuss_records_on_item(self, env, hq):
        hq.write_agenda(hq.current_week_key(), AGENDA)
        client, llm = make_client(env, ["sidebar counsel", SYNTHESIS])
        self._start(client)
        response = client.post("/api/meeting/discuss", json={"item_id": 0, "text": "is this risky?"})
        assert parse_sse(response.text)[0]["reply"] == "sidebar counsel"
        # The discussion rides into the synthesis call's rulings text
        client.post("/api/meeting/ruling", json={"item_id": 0, "action": "approve"})
        client.post("/api/meeting/close", json={"ratifications": {}})
        synth_call = llm.calls[-1]
        assert "is this risky?" in synth_call.user_message
        assert "sidebar counsel" in synth_call.user_message

    def test_double_start_resumes_with_rulings_intact(self, env, hq):
        # Regression (2026-07-24): a browser reload lost the client-side
        # meeting state and the old 409 left the CEO with no way back in.
        # A second start must RESUME the live session, rulings intact.
        hq.write_agenda(hq.current_week_key(), AGENDA)
        client, _ = make_client(env, [])
        first = self._start(client)
        assert first["resumed"] is False
        client.post("/api/meeting/ruling", json={"item_id": 0, "action": "approve"})

        second = self._start(client)
        assert second["resumed"] is True
        assert [i["title"] for i in second["items"]] == [i["title"] for i in first["items"]]
        assert second["items"][0]["ruled"] is True
        assert second["items"][0]["ruling"] == "approve"
        assert second["items"][1]["ruled"] is False

        assert client.post("/api/meeting/abandon").json() == {"abandoned": True}
        assert client.post("/api/meeting/start").json()["resumed"] is False


FAKE_REGISTRY = {
    "fake.set_price": ActionType(
        name="fake.set_price", connector="fake",
        params={"target_id": "str", "new_value": "float"}, snapshot_params=("target_id",),
    ),
}


class TestMeetingCloseExecutesAndPushes:
    """End-to-end through the dashboard: closing a meeting that approves an
    escalation-linked action must execute it live AND commit/push — the gap
    discovered 2026-08-03 (a meeting recorded 'approved' in text while the
    live price never changed, and nothing was committed)."""

    def test_approve_executes_and_pushes(self, config, synced_repos, monkeypatch, tmp_path):
        clone, origin = synced_repos
        monkeypatch.setenv("BRAIN_ROOT", str(clone))
        config.departments["storefront"] = DepartmentConfig(
            name="storefront", tier=1, status="active", report_cadence="weekly"
        )
        hq = HQ(config)
        (hq.root / "charter" / "tiers.md").write_text("# Tiers", encoding="utf-8")
        prompts = config.prompts_root
        prompts.mkdir(parents=True, exist_ok=True)
        for name in ("system_core.md", "meeting_synthesis.md"):
            (prompts / name).write_text(f"# {name}", encoding="utf-8")

        connector = FakeConnector()
        executor = Executor(
            hq=hq, registry=FAKE_REGISTRY,
            limits={"storefront": AgentLimits(allowed_actions=[])},
            capabilities={}, connectors={"fake": connector},
            capabilities_path=tmp_path / "capabilities.yaml", env={},
        )
        rejected = executor.submit(ActionIntent(
            agent="storefront", action_type="fake.set_price",
            params={"target_id": "P1", "new_value": 19.5}, rationale="Reprice needed",
        ))
        esc_id = next(e.id for e in hq.read_escalation_queue() if e.action_ref == rejected.id)

        hq.write_agenda(hq.current_week_key(), (
            "# Board Meeting Agenda — W1\n\n## Department Syntheses\n\n"
            "### storefront\n\nReprice pending.\n\n"
            "## Proposed Decisions\n\n"
            f"#### Decision: Approve pending action for {esc_id}\n"
            "- Recommendation: Approve it.\n"
            "- Checklist: money=yes, brand=no, legal=no, irreversible=no\n"
            "- Tag: [CEO REQUIRED]\n"
            f"- Escalation ref: {esc_id}\n\n"
            "## Escalation Triage\n\n### Urgent\n- None.\n"
        ))

        llm = DashFakeLLM(responses=[
            "## Minutes\n\nApproved the reprice.\n\n"
            "## Decision Log Entries\n\n## Directive Updates\n\nNone.\n\n"
            "## Resolved Escalations\n\nNone.\n"
        ])
        app = create_app(config, hq, executor)
        register_chat_routes(app, config, hq, make_llm=lambda command=None: llm, executor=executor)
        client = TestClient(app)

        client.post("/api/meeting/start")
        client.post("/api/meeting/ruling", json={"item_id": 0, "action": "approve"})
        result = client.post("/api/meeting/close", json={"ratifications": {}}).json()

        assert result["executed_actions"], result
        assert result["committed"] is True
        assert result["pushed"] is True
        assert [c[0] for c in connector.calls] == ["read_state", "execute"]
        assert esc_id not in [e.id for e in hq.read_escalation_queue()]
        log = git("log", "origin/main", "-1", "--format=%s", cwd=clone)
        assert "Board meeting" in log.stdout


class TestConsult:
    def test_streams_and_flags_dormant(self, env):
        client, llm = make_client(env, ["From my desk: nothing new."])
        response = client.post("/api/consult",
                               json={"department": "creative", "message": "any badge ideas?"})
        events = parse_sse(response.text)
        text = "".join(e.get("delta", "") for e in events)
        assert text == "From my desk: nothing new."
        assert events[-1]["advisory"] is True  # creative is dormant
        # No HQ writes: consult is conversation only
        assert llm.calls[0].system_blocks[1]["text"].startswith("You are DORMANT")

    def test_active_department_not_advisory(self, env):
        client, _ = make_client(env, ["Active answer."])
        response = client.post("/api/consult",
                               json={"department": "market_intel", "message": "status?"})
        assert parse_sse(response.text)[-1]["advisory"] is False

    def test_unknown_department_404(self, env):
        client, _ = make_client(env, [])
        assert client.post("/api/consult",
                           json={"department": "nobody", "message": "hi"}).status_code == 404


class TestDirectiveCommand:
    DRAFT = "Summary of changes.\n\n```markdown\n# Directive: Market Intel\n\nLast updated: 2026-07-16\n\n## Tier\n\nTier 0 — Read-only\n\n## Status\n\nactive\n\n## Standing orders\n\nWatch Reddit too.\n```\n"

    def test_draft_and_confirm(self, env, hq):
        client, _ = make_client(env, [self.DRAFT])
        data = client.post("/api/command/directive",
                           json={"department": "market_intel", "changes": "add Reddit"}).json()
        assert data["writable"] is True
        assert "Watch Reddit too." not in hq.read_directive("market_intel")

        result = client.post("/api/command/directive/confirm",
                             json={"department": "market_intel"}).json()
        assert "written" in result
        assert "Watch Reddit too." in hq.read_directive("market_intel")
        # Draft consumed — second confirm 409s
        assert client.post("/api/command/directive/confirm",
                           json={"department": "market_intel"}).status_code == 409

    def test_board_decision_refused(self, env, hq):
        client, _ = make_client(env, ["[REQUIRES BOARD DECISION] Tier changes are board decisions."])
        data = client.post("/api/command/directive",
                           json={"department": "market_intel", "changes": "promote to tier 2"}).json()
        assert data["board_decision_required"] is True
        assert data["writable"] is False
        assert client.post("/api/command/directive/confirm",
                           json={"department": "market_intel"}).status_code == 409


class TestAgentCommand:
    def test_runs_and_streams_lines(self, env, hq):
        report = "# Report\n\n## Findings\n\n1. x\n\n## Changes since last report\n\nFirst.\n\n## Escalations\n\nNone.\n"
        client, _ = make_client(env, [report])
        response = client.post("/api/command/agent", json={"department": "market_intel"})
        events = parse_sse(response.text)
        assert events[-1] == {"done": True, "exit_code": 0}
        assert hq.read_report("market_intel", hq.current_week_key()) is not None

    def test_dormant_refusal_streams_reason(self, env):
        client, _ = make_client(env, [])
        events = parse_sse(client.post("/api/command/agent",
                                       json={"department": "creative"}).text)
        assert any("dormant" in e.get("line", "") for e in events)
        assert events[-1]["exit_code"] == 0

    def test_unknown_exhibit_slug_is_404(self, env):
        client, _ = make_client(env, [])
        response = client.post("/api/command/agent",
                               json={"department": "market_intel", "exhibit": "nope"})
        assert response.status_code == 404

    def test_exhibit_reaches_the_run(self, env, hq):
        hq.write_research_exhibit("dad-hats", "Olive/navy trucker hats trend across dad brands.")
        report = "# Report\n\n## Findings\n\n1. x\n\n## Changes since last report\n\nFirst.\n\n## Escalations\n\nNone.\n"
        client, llm = make_client(env, [report])
        response = client.post("/api/command/agent",
                               json={"department": "market_intel", "exhibit": "dad-hats"})
        events = parse_sse(response.text)
        assert events[-1] == {"done": True, "exit_code": 0}
        dynamic = llm.calls[0].system_blocks[1]["text"]
        assert "Olive/navy trucker hats trend across dad brands." in dynamic
        assert "dad-hats" in dynamic


class TestStreamErrorGuard:
    def test_api_failure_mid_stream_surfaces_as_error_event(self, env):
        """An Anthropic 500 (or any exception) inside an SSE generator must
        reach the browser as an {error} event — never a silently dead
        stream. Regression for the invisible ingest failure."""
        class ExplodingLLM(DashFakeLLM):
            def call(self, *a, **k):
                raise RuntimeError("Internal server error (simulated API 500)")

        config, hq = env
        llm = ExplodingLLM()
        app = create_app(config, hq)
        register_chat_routes(app, config, hq, make_llm=lambda command=None: llm)
        client = TestClient(app)

        response = client.post("/api/command/ingest")
        assert response.status_code == 200  # stream opened, then failed
        events = parse_sse(response.text)
        assert any("Internal server error" in e.get("error", "") for e in events)
        assert events[-1]["done"] is True


class TestHelp:
    def test_lists_every_bar_command(self, env):
        client, _ = make_client(env, [])
        help_data = client.get("/api/command/help").json()
        commands = {h["command"] for h in help_data}
        assert {"#status", "#ingest", "#meeting", "#boardroom", "#agent",
                "#directive", "#help", "@department"} <= commands


class TestRenderRulings:
    def test_module_level_render(self):
        text = render_rulings([MeetingRuling(item_title="X", action="approve")])
        assert text == "- X: APPROVE"
