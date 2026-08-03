# Board Meeting Agenda — 2026-W32

## Department Syntheses

### market_intel

No report filed. This silence matters somewhat: ESC-017 (the ArtWalk Ventura booth window with an unconfirmed application deadline) is still open, and a week has now passed with no follow-up check on zapplication.org — the department that raised the time-sensitive flag has gone quiet on it rather than confirming or closing it, which is a real gap worth noting even though last week's report itself was substantive and there's no sign yet of a broader pipeline failure.

### creative

No report filed — this is the second consecutive missed week (W31 and W32) for an active Tier 1 department, and it comes right after the 2026-08-03 decision that specifically ordered a scheduler/agent-health check on creative and storefront for this exact reason. Storefront has since resumed reporting; creative has not. This now reads as more than a one-off miss and warrants a direct check on whether creative's agent is actually running, rather than assuming the prior check resolved it.

### content

Dormant — no agent active.

### product

Dormant — no agent active.

### storefront

Storefront filed a full report this week. Headline: the own-art inversion metric is still stuck at ~3 of ~108 purchasable listings (~2.8%), unchanged from last week, with six giclée drafts (five Neptune's Garden prints, the Complete Collection bundle, and a new Bodysurfer B&W photography print) still unpublished and the entire priority-2 revenue line still at zero live sales. The department delivered the CEO-requested drinkware margin review and proposed a size-ladder reprice for both mugs ($9–13 → $12/14/16) and the tumbler ($19.00 → $26.00) to clear the 30% floor, plus branding-consistency renames carried over from last week (mug, beanie, two posters) and new SEO copy for the Bodysurfer print — but every structured action this cycle (ESC-020 through ESC-023) was rejected by the executor on a params-schema mismatch (agent sent `external_id`/`prices`/`price`; executor expects `product_id`/`new_price`, and copy actions expect `seo`), meaning none of this week's proposed fixes can execute until the schema is corrected and resubmitted. Storefront is also asking, again, for a ruling on the giclée-publish blocker and flagging that sold-out Jacquard hygiene remains unexecutable without inventory-level data in the sync.

### customer

Dormant — no agent active.

### paid_ads

Dormant — no agent active.

### finance

Dormant — no agent active.

## Cross-Department Notes

The only real cross-department item this cycle is procedural, not a conflict: storefront's four proposed actions (ESC-020–023) all failed for the same reason — a params-schema mismatch between what the agent emits and what the executor's action contract requires — which means none of this week's margin-floor or SEO fixes can be applied even if approved as-is; the schema needs aligning before re-proposing, independent of any CEO pricing call. Separately, creative's continued silence has a mild knock-on effect on storefront's own standing orders (print-presentation naming/certificate wording, POD ranking) that creative — not storefront — owns, though storefront hasn't flagged this as blocking its own work this cycle. No genuine conflicting recommendations exist between departments this week.

## Proposed Decisions

#### Decision: Fix the shopify action-params schema mismatch blocking storefront's proposed actions
- Recommendation: Align storefront's action-emission format with the executor's actual action contract (`product_id`/`new_price` for pricing, `product_id`/`seo` for copy) so ESC-020–023 can be correctly resubmitted next cycle; this is an internal tooling correction, not a pricing or publishing decision itself.
- Checklist: money=no, brand=no, legal=no, irreversible=no
- Tag: [CEO REQUIRED]
- Reason: [auto-upgraded: keyword match on category: legal, spend]
#### Decision: Approve drinkware margin-floor repricing (mug ladder + tumbler)
- Recommendation: Approve storefront's proposed reprice — Bodysurf Fin Mug and Logo Mug to $12/$14/$16 (11/15/20oz) and the Sunsets & Sips Tumbler to $26.00 — which clears the 30% margin floor against confirmed Printful costs; resubmission with corrected params is still required before this can execute.
- Checklist: money=yes, brand=no, legal=no, irreversible=no
- Tag: [CEO REQUIRED]
- Reason: Pricing changes are always CEO sign-off under the charter's decision boundaries.

#### Decision: Approve or reject publishing the six draft giclée listings (Neptune's Garden ×5 + Bodysurfer)
- Recommendation: This question has now sat open since the 2026-07-24 rejection ("charter/brand direction settled first, not a finding against the listings"); with the charter and pivot now well-settled and a second consecutive priority-2 review flagging zero live revenue on this line, recommend the CEO revisit whether the original blocking condition still holds or whether it's time to approve publishing some or all of these six.
- Checklist: money=yes, brand=no, legal=no, irreversible=no
- Tag: [CEO REQUIRED]
- Reason: Publishing sets live prices for the first time on these SKUs — a pricing/commerce commitment reserved to the CEO.

#### Decision: Approve Bodysurfer print listing copy/title update
- Recommendation: Approve storefront's proposed title/description for the new Bodysurfer print, which brings it into "Josh Ball Art" SEO/brand styling consistent with the charter's naming rule; requires resubmission with corrected params (`product_id`, `seo`) before it can execute.
- Checklist: money=no, brand=yes, legal=no, irreversible=no
- Tag: [CEO REQUIRED]
- Reason: Touches brand-name styling/voice on a public listing, and publishing is CEO-only regardless.

#### Decision: Approve the four carried-over "Josh Ball Art" branding renames (mug, beanie, two posters)
- Recommendation: Approve these renames, unchanged for two weeks now, to bring existing live POD titles in line with the charter's mandatory "Josh Ball Art" styling.
- Checklist: money=no, brand=yes, legal=no, irreversible=no
- Tag: [CEO REQUIRED]
- Reason: Direct brand-name/styling change on live listings.

## Escalation Triage

### Urgent
- **ESC-017** — ArtWalk Ventura 2026 (Sept 26–27, $0 booth fee) has an unconfirmed application deadline that market_intel flagged as possibly closing soon, and no follow-up happened this week. Proposed ruling: CEO or a delegate should check zapplication.org (event ID 14550) directly this week — this cannot wait for next week's meeting without real risk of missing the window. Flagging as urgent per Phase 1 limits: this is only as urgent as the next time this queue is read, no active alert exists.

### This Meeting
- **ESC-018** — Six giclée listings still in draft; addressed above as a proposed decision. Ruling needed: publish, hold, or clarify what's actually blocking (Prodigi samples? copy?).
- **ESC-019** — Drinkware margin-floor breach; addressed above as a proposed decision. Ruling needed: approve the size-ladder reprice.
- **ESC-020 / ESC-021 / ESC-022** — All three are the same underlying schema-mismatch failure on the drinkware reprice actions (ESC-019's execution mechanics). Proposed ruling: acknowledge as a tooling fix (see Decision above), not a separate CEO judgment call — resubmission will follow once the schema is aligned.
- **ESC-023** — Bodysurfer copy-action rejected on the same schema mismatch; tied to the copy-approval decision above. Same proposed ruling as ESC-020–022.

### Defer
- None. All open escalations this cycle are either time-sensitive (ESC-017) or tied directly to this meeting's proposed decisions.