"""The board meeting as a session object, shared by the CLI and the
dashboard (same pattern as BoardroomSession): load the agenda into items,
record rulings (with optional per-item sidebar discussion), then one
synthesis call writes minutes / decision-log entries / directive updates
(tier-ratification guarded) / escalation resolutions.

prepare_close/commit_close are split so the dashboard's tier-ratification
round-trip never re-runs the synthesis model or double-appends decisions —
identical contract to BoardroomSession.prepare_records/commit_records.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date

from brain.actions.models import ActionResult
from brain.config import BrainConfig
from brain.executor import Executor
from brain.governance import DECISION_HEADING_RE, extract_escalation_ref
from brain.hq import HQ
from brain.interaction import Exchange, render_exchanges
from brain.llm import LLM
from brain.models import MeetingRuling
from brain.prompts import build_system_blocks
from brain.records import (
    RESOLVED_LINE_RE,
    extract_directive_updates,
    parse_decision_entries,
    split_sections,
    tier_or_status_changed,
)

PROPOSED_DECISIONS_HEADING_RE = re.compile(r"^## Proposed Decisions\s*$", re.MULTILINE)

MEETING_OUTPUT_SECTIONS = ["Minutes", "Decision Log Entries", "Directive Updates", "Resolved Escalations"]
# Split ONLY on the four known section headings — directive content inside
# the output legitimately contains its own ## headings (## Tier, ## Mandate)
# and must not break the split.
MEETING_SECTION_RE = re.compile(
    r"^## (Minutes|Decision Log Entries|Directive Updates|Resolved Escalations)\s*$", re.MULTILINE
)
TAG_IN_BLOCK_RE = re.compile(r"\[(BRAIN DECIDES|CEO REQUIRED)\]")


def render_rulings(rulings: list[MeetingRuling]) -> str:
    """Render rulings (with any sidebar discussion) for the synthesis call."""
    parts = []
    for r in rulings:
        line = f"- {r.item_title}: {r.action.upper()}"
        if r.ceo_note:
            line += f" — CEO note: {r.ceo_note}"
        if r.discussion:
            line += "\n  Discussion during ruling:\n" + render_exchanges(r.discussion, indent="    ")
        parts.append(line)
    return "\n".join(parts)


@dataclass
class AgendaItem:
    id: int
    title: str
    block_text: str
    tag: str  # "BRAIN DECIDES" | "CEO REQUIRED" | ""
    ruling: MeetingRuling | None = None
    discussion: list[Exchange] = field(default_factory=list)
    escalation_ref: str | None = None  # ESC-XXX this item resolves, if any


class MeetingSession:
    def __init__(self, llm: LLM, config: BrainConfig, hq: HQ):
        self.llm = llm
        self.config = config
        self.hq = hq
        self.week = hq.current_week_key()
        self.agenda: str = ""
        self.items: list[AgendaItem] = []

    def load_agenda(self) -> list[AgendaItem]:
        agenda_path = self.hq.root / "meetings" / f"{self.week}-agenda.md"
        if not agenda_path.exists():
            raise FileNotFoundError(f"No agenda for {self.week}. Run `brain ingest` first.")
        self.agenda = agenda_path.read_text(encoding="utf-8")

        blocks = list(DECISION_HEADING_RE.finditer(self.agenda))
        self.items = []
        for i, m in enumerate(blocks):
            start = m.start()
            end = blocks[i + 1].start() if i + 1 < len(blocks) else len(self.agenda)
            block_text = self.agenda[start:end].strip()
            # The last block otherwise swallows whatever section follows the
            # decisions (Escalation Triage) — trim at the next ## heading.
            next_section = re.search(r"^## ", block_text, re.MULTILINE)
            if next_section:
                block_text = block_text[:next_section.start()].strip()
            tag_m = TAG_IN_BLOCK_RE.search(block_text)
            self.items.append(AgendaItem(
                id=i,
                title=m.group(1).strip(),
                block_text=block_text,
                tag=tag_m.group(1) if tag_m else "",
                escalation_ref=extract_escalation_ref(block_text),
            ))
        return self.items

    def _item(self, item_id: int) -> AgendaItem:
        for item in self.items:
            if item.id == item_id:
                return item
        raise ValueError(f"No agenda item {item_id}")

    def discuss(self, item_id: int, ceo_text: str) -> str:
        """Sidebar conversation about one item; recorded on that item."""
        from brain.main import make_discusser

        item = self._item(item_id)
        item.discussion.append(Exchange("CEO", ceo_text))
        reply = make_discusser(self.llm, self.config, self.hq, item.block_text)(
            ceo_text, item.discussion
        )
        item.discussion.append(Exchange("brain", reply))
        return reply

    def record_ruling(self, item_id: int, action: str, note: str = "") -> None:
        if action not in ("approve", "modify", "reject", "skip"):
            raise ValueError(f"Unknown ruling action {action!r}")
        item = self._item(item_id)
        item.ruling = MeetingRuling(
            item_title=item.title, action=action, ceo_note=note,
            discussion=item.discussion,
        )

    def rulings(self) -> list[MeetingRuling]:
        """Rulings in item order; unruled items count as skipped."""
        result = []
        for item in self.items:
            result.append(item.ruling or MeetingRuling(
                item_title=item.title, action="skip", discussion=item.discussion,
            ))
        return result

    # ------------------------------------------------------------------

    def render_rulings(self) -> str:
        return render_rulings(self.rulings())

    def prepare_close(self) -> dict:
        """The synthesis LLM call + parsing, NO writes."""
        user_message = (
            f"The {self.week} board meeting is over. Here is the agenda:\n\n{self.agenda}\n\n"
            f"---\n\nThe CEO's rulings:\n\n{self.render_rulings()}\n\n"
            f"Today's date is {date.today().isoformat()}. Produce the meeting records."
        )
        system_blocks = build_system_blocks(self.config, self.hq, "meeting_synthesis.md")
        output = self.llm.call(system_blocks, user_message,
                               max_tokens=self.config.max_tokens["meeting"])

        sections = split_sections(output, MEETING_SECTION_RE)
        missing = [s for s in MEETING_OUTPUT_SECTIONS if s not in sections]
        if missing:
            return {"raw_output": output, "missing_sections": missing}

        entries = parse_decision_entries(sections["Decision Log Entries"])
        updates, warnings = extract_directive_updates(
            sections["Directive Updates"], self.hq.list_departments()
        )
        pending_ratifications = []
        for dept, content in updates.items():
            try:
                current = self.hq.read_directive(dept)
            except FileNotFoundError:
                current = ""
            change = tier_or_status_changed(current, content) if current else None
            if change:
                pending_ratifications.append({"dept": dept, "change": change})

        return {
            "sections": sections,
            "entries": entries,
            "updates": updates,
            "warnings": warnings,
            "pending_ratifications": pending_ratifications,
            "missing_sections": [],
        }

    def _execute_ruled_escalations(self, executor: Executor) -> tuple[set[str], list[str], list[str]]:
        """For every ruled agenda item linked to an escalation
        (item.escalation_ref), decide execution from the CEO's structured
        ruling alone — never from LLM-synthesized text. 'approve' replays
        the pending action for real via Executor.approve_action() (the
        same CEO-override primitive the dashboard's single-escalation
        approve button uses) and resolves the escalation; 'reject' denies
        it with no execution. 'modify'/'skip' are deliberately left alone
        here — approve_action() always replays the ORIGINAL rejected
        action's exact params, and a modified price is not the
        department's original proposal, so it falls through to the
        free-text Resolved Escalations path unchanged.

        Returns (handled_escalation_ids, executed_action_ids, warnings)."""
        handled: set[str] = set()
        executed: list[str] = []
        warnings: list[str] = []
        open_escalations = {e.id: e for e in self.hq.read_escalation_queue()}

        for item in self.items:
            if not item.escalation_ref:
                continue
            ruling = item.ruling or MeetingRuling(item_title=item.title, action="skip")
            if ruling.action not in ("approve", "reject"):
                continue

            esc = open_escalations.get(item.escalation_ref)
            if esc is None:
                warnings.append(f"{item.escalation_ref}: no longer in the open queue — skipped")
                continue

            if ruling.action == "reject":
                try:
                    self.hq.resolve_escalation(
                        esc.id, resolution="denied by CEO at board meeting", decided_by="CEO"
                    )
                    handled.add(esc.id)
                except ValueError as e:
                    warnings.append(f"{esc.id}: {e}")
                continue

            # approve
            if not esc.action_ref:
                warnings.append(f"{esc.id}: approved but has no pending action to execute")
                continue
            try:
                record = executor.approve_action(esc.action_ref, escalation_id=esc.id)
            except ValueError as e:
                warnings.append(f"{esc.id}: {e}")
                continue
            if record.result == ActionResult.EXECUTED:
                resolution = f"approved at board meeting — executed as {record.id}"
                executed.append(record.id)
            else:
                resolution = (
                    f"approved at board meeting — execution failed: {'; '.join(record.reasons)}"
                )
            self.hq.resolve_escalation(esc.id, resolution=resolution, decided_by="CEO")
            handled.add(esc.id)

        return handled, executed, warnings

    def commit_close(self, prepared: dict, ratify_fn=None, executor: Executor | None = None) -> dict:
        """All HQ writes for a prepared close. `ratify_fn(dept, change) ->
        bool` gates tier/status changes; default declines (never silent).
        `executor`, if given, replays any CEO-approved escalation actions
        live (see `_execute_ruled_escalations`) — omit it (default None)
        to skip execution entirely, e.g. when no live connectors are
        configured. `changed_paths` in the return value is every HQ file
        this close touched, for the caller to commit/push."""
        if prepared.get("missing_sections"):
            # Don't lose the meeting: raw output becomes the minutes.
            path = self.hq.write_minutes(self.week, prepared["raw_output"])
            return {
                "minutes_path": path,
                "decisions": 0, "directives_updated": [], "escalations_resolved": 0,
                "executed_actions": [],
                "changed_paths": [path],
                "warnings": [
                    f"synthesis output missing sections {prepared['missing_sections']} — "
                    f"raw output saved as minutes; records NOT auto-applied, review manually"
                ],
            }

        sections = prepared["sections"]
        warnings = list(prepared["warnings"])
        pending = {p["dept"]: p["change"] for p in prepared["pending_ratifications"]}
        ratify = ratify_fn or (lambda dept, change: False)

        minutes_path = self.hq.write_minutes(
            self.week, f"# Board Meeting Minutes — {self.week}\n\n{sections['Minutes']}\n"
        )
        changed_paths = [minutes_path]

        for entry in prepared["entries"]:
            self.hq.append_decision(entry)
        if prepared["entries"]:
            changed_paths.append(self.hq.root / "decisions" / "log.md")

        written = []
        for dept, content in prepared["updates"].items():
            change = pending.get(dept)
            if change and not ratify(dept, change):
                warnings.append(
                    f"directive update for {dept} included a tier/status change "
                    f"({change}) the CEO did not ratify — skipped"
                )
                continue
            path = self.hq.write_directive(dept, content)
            written.append(dept)
            changed_paths.append(path)

        handled_by_ruling: set[str] = set()
        executed_actions: list[str] = []
        if executor is not None:
            handled_by_ruling, executed_actions, exec_warnings = self._execute_ruled_escalations(executor)
            warnings.extend(exec_warnings)

        resolved = 0
        for m in RESOLVED_LINE_RE.finditer(sections["Resolved Escalations"]):
            esc_id = m.group(1)
            if esc_id in handled_by_ruling:
                continue  # already handled deterministically above — avoid double-resolve
            try:
                self.hq.resolve_escalation(esc_id, resolution=m.group(2).strip(),
                                           decided_by="CEO")
                resolved += 1
            except ValueError as e:
                warnings.append(f"{e} — skipped")
        resolved += len(handled_by_ruling)

        if handled_by_ruling or resolved:
            changed_paths += [
                self.hq.root / "escalations" / "queue.md",
                self.hq.root / "escalations" / "resolved.md",
            ]

        if executed_actions:
            changed_paths += [self.hq.actions_log_path(), self.hq.llm_usage_log_path()]
            changed_paths += [self.hq.snapshot_path(action_id) for action_id in executed_actions]
            # Refresh the committed catalog so it reflects the live price
            # change immediately, not after the next manual sync-products.
            from brain.main import sync_products  # local import: main.py imports meeting.py
            sync_products(self.hq, executor.connectors)
            changed_paths += list(self.hq.product_catalog_paths())

        return {
            "minutes_path": minutes_path,
            "decisions": len(prepared["entries"]),
            "directives_updated": written,
            "escalations_resolved": resolved,
            "executed_actions": executed_actions,
            "changed_paths": changed_paths,
            "warnings": warnings,
        }

    def close(self, ratify_fn=None, executor: Executor | None = None) -> dict:
        return self.commit_close(self.prepare_close(), ratify_fn, executor=executor)


def _inject_escalation_decisions(raw_agenda: str, hq: HQ) -> str:
    """Deterministically force every open escalation with a pending live
    action (EscalationItem.action_ref set) into its own ruled decision
    block, in code — never left to the ingest LLM's judgment about what
    belongs in Escalation Triage vs. Proposed Decisions. This is what lets
    MeetingSession.commit_close know, from the CEO's structured ruling
    alone, whether to replay the action via the executor (governance is
    code, not prompts). Dedupes on the literal 'Escalation ref: ESC-XXX'
    substring so an LLM that already surfaced one isn't duplicated."""
    open_with_action = [e for e in hq.read_escalation_queue() if e.action_ref]
    if not open_with_action:
        return raw_agenda

    actions_by_id = {a.id: a for a in hq.read_actions()}
    blocks = []
    for esc in open_with_action:
        if f"Escalation ref: {esc.id}" in raw_agenda:
            continue
        action = actions_by_id.get(esc.action_ref)
        pending = f"{action.action_type} {action.params}" if action else esc.action_ref
        blocks.append(
            f"\n#### Decision: Approve pending action for {esc.id} ({esc.raised_by})\n"
            f"- Recommendation: {esc.summary} Pending action: {pending}.\n"
            f"- Checklist: money=yes, brand=no, legal=no, irreversible=no\n"
            f"- Tag: [CEO REQUIRED]\n"
            f"- Reason: escalation-linked live action — always CEO required, forced in code\n"
            f"- Escalation ref: {esc.id}\n"
        )
    if not blocks:
        return raw_agenda

    injected = "".join(blocks)
    heading_m = PROPOSED_DECISIONS_HEADING_RE.search(raw_agenda)
    if heading_m:
        insert_at = heading_m.end()
        return raw_agenda[:insert_at] + "\n" + injected + raw_agenda[insert_at:]
    return raw_agenda.rstrip("\n") + "\n\n## Proposed Decisions\n" + injected


def run_ingest(hq: HQ, llm: LLM, config: BrainConfig, print_fn=print) -> dict:
    """The ingest core (shared CLI/dashboard): discover reports, synthesize
    the agenda, run governance, write it."""
    from brain.governance import apply_governance

    week = hq.current_week_key()
    last_meeting = hq.last_meeting_date()
    since_week = hq.week_key_for_date(last_meeting) if last_meeting else "1970-W01"

    reports = hq.discover_reports(since_week)
    filed = {dept: entries for dept, entries in reports.items() if entries}
    print_fn(f"Reports found since {since_week}: "
             + (", ".join(f"{d} ({len(e)})" for d, e in filed.items()) if filed else "none"))

    system_blocks = build_system_blocks(config, hq, "ingest.md")
    trigger = (
        f"Prepare the board meeting agenda for {week}. "
        f"Reports discovered since the last meeting are already in your context."
    )
    raw_agenda = llm.call(system_blocks, trigger, max_tokens=config.max_tokens["ingest"])
    if len(raw_agenda.strip()) < 50:
        raise RuntimeError(
            f"ingest produced {len(raw_agenda.strip())} chars — not a plausible "
            f"agenda; nothing written (see LLMTruncated in brain/llm.py for the "
            f"usual cause).")

    raw_agenda = _inject_escalation_decisions(raw_agenda, hq)
    corrected_agenda, enforced = apply_governance(raw_agenda)
    upgrades = [e for e in enforced if e.upgraded]
    path = hq.write_agenda(week, corrected_agenda)

    return {
        "week": week,
        "path": path,
        "decisions": len(enforced),
        "upgrades": [{"title": e.title, "reasons": e.reasons} for e in upgrades],
        "reports_found": {d: len(e) for d, e in filed.items()},
    }
