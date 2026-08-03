# Board Meeting Agenda — 2026-W32

## Department Syntheses

### market_intel

A report was filed for 2026-W31 (nothing further came in for W32 itself). The cycle substantially filled the workshop-pricing gap with real Santa Barbara/LA comps ($30–$79/seat for a 2-hour popup, with premium multi-day intensives running as high as $720), surfaced a directly relevant Ventura precedent (Patagonia Ventura's paid cyanotype popup with Oriana Poindexter — a strong template match for the charter's retail-popup format), and flagged a live, no-fee ArtWalk Ventura booth opportunity (Sept 26–27) whose application deadline could not be confirmed and may be closing soon (see ESC-017). Brand watch found no visible search confusion with "Artist Josh Ball" this cycle — a partial close of a previously open gap. Two tool checks (Etsy handle, venturacoldwatercadre.com domain) remain inconclusive on platform/network failures, not findings. No follow-up report came in for W32 itself — the ArtWalk deadline and the standing photography-spend trigger metric (owned by market_intel per the 2026-07-16 decision) remain unconfirmed for a second week, and this data is now aging; that silence matters given the live escalation riding on it.

### creative

No report filed. Silence matters: this is the second consecutive missed week for an active, Tier 1 department carrying several open mandates — the backup-handle brand-voice check that's been waiting since creative's 2026-07-19 activation, workshop one-pagers, POD fit-ranking, and the blog backlog — none of which have moved.

### content

Dormant — no agent active.

### product

Dormant — no agent active.

### storefront

No report filed. Silence matters: this is the second consecutive missed week for an active Tier 1 department, and it's sitting on a live, CEO-directed test (ESC-016 — the enamel cup reprice) that's currently blocked on a capability gap, plus the standing inverted-catalog tracking (own-art listings vs. dead Jacquard stock) that has no reported movement.

### customer

Dormant — no agent active.

### paid_ads

Dormant — no agent active.

### finance

Dormant — no agent active.

## Cross-Department Notes

Two active departments (creative, storefront) have now gone silent for two consecutive weekly cycles — worth a direct check on whether their scheduling/agent health is intact rather than assuming it's simply nothing-to-report. Separately, storefront's directive promises that CEO-approved prices execute automatically ("the system applies it"), but ESC-016 shows the executor's allowed-actions list doesn't yet include `shopify.set_price` — a plumbing gap between what the directive promises and what the executor can do, not a department disagreement. No genuine cross-department conflict this cycle; no boardroom topic proposed.

## Proposed Decisions

#### Decision: Grant storefront the `shopify.set_price` governed action
- Recommendation: Authorize adding `shopify.set_price` to storefront's allowed actions so CEO-approved price changes (like the pending enamel cup reprice) execute automatically instead of dead-ending at the executor, matching the directive's stated design.
- Checklist: money=yes, brand=no, legal=no, irreversible=no
- Tag: [CEO REQUIRED]
- Reason: Capability expansion touching a money-moving action requires the explicit per-capability CEO grant the Authority Tiers require, and price-change execution is CEO-only under the charter.

#### Decision: Execute the enamel cup reprice ($14.00 → $19.50) per ESC-016
- Recommendation: Apply the reprice the CEO already directed on 2026-07-24 (11% margin → 36% margin, above the 30% floor) once the action-capability gap above is resolved.
- Checklist: money=yes, brand=no, legal=no, irreversible=no
- Tag: [CEO REQUIRED]
- Reason: Any price change is a spend/pricing guardrail item requiring explicit CEO sign-off.

#### Decision: Confirm creative and storefront agents are still scheduled and running
- Recommendation: Two consecutive missed weekly reports from two active departments warrants a straightforward operational check (scheduler/agent health), not a policy change — no CEO judgment call is needed to simply verify the pipeline is intact.
- Checklist: money=no, brand=no, legal=no, irreversible=no
- Tag: [BRAIN DECIDES]

## Escalation Triage

### Urgent
- **ESC-017** — ArtWalk Ventura 2026 ($0-fee booth, Sept 26–27) has an unconfirmed application deadline that market_intel flags as possibly closing soon, and no new information came in this cycle to resolve it. Proposed ruling: CEO (or a delegate) checks zapplication.org (event ID 14550) directly this week — this is genuinely time-sensitive and, per Phase 1 limits, is only as urgent as the next command run, so flagging it here doesn't guarantee it's seen before the window closes.

### This Meeting
- **ESC-016** — The CEO's 2026-07-24 directive to reprice the enamel cup is blocked because `shopify.set_price` isn't in storefront's allowed actions; this can wait for this meeting's decision (above) rather than needing action before it. Proposed ruling: approve the capability grant and the reprice together (see Proposed Decisions).

### Defer
- None.