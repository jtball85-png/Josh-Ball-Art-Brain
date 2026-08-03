# Board Meeting Minutes — 2026-W32

The board convened for the 2026-W32 cycle with two departments (market_intel, creative) silent, two dormant carryovers, and a full storefront report.

**Market_intel:** filed no report this week. Of particular concern, ESC-017 — the ArtWalk Ventura 2026 booth window with an unconfirmed application deadline — has now gone a full week without follow-up from the department that raised it. The board flagged this as urgent, but no ruling was requested or given this cycle on dispatching a check of zapplication.org; the escalation remains open and unresolved, carried forward with its urgent flag intact.

**Creative:** second consecutive missed week (W31 and W32), notable because it comes directly after the 2026-08-03 decision that ordered a scheduler/agent-health check on both creative and storefront for exactly this kind of silence. Storefront has since resumed reporting; creative has not. The board noted this reads as more than a one-off miss and warrants a direct operational check, but no such ruling was tabled as a proposed decision this cycle, so none was made — this is logged as an open concern for the next cycle, not a decision.

**Storefront:** filed a full report. The own-art inversion metric remains stuck at ~2.8% purchasable listings, unchanged week over week, with the priority-2 (giclée) revenue line still at zero live sales. Storefront delivered the CEO-requested drinkware margin review, proposing a size-ladder reprice for both mugs ($9–13 → $12/14/16 across 11/15/20oz) and the tumbler ($19.00 → $26.00) to clear the 30% margin floor, plus SEO/brand copy for the new Bodysurfer print and four carried-over branding renames (mug, beanie, two posters). Every structured action this cycle (ESC-020 through ESC-023) was rejected by the executor on a straightforward params-schema mismatch — the agent emitted `external_id`/`prices`/`price` where the executor's action contract expects `product_id`/`new_price` (and `seo` for copy actions). This is a tooling/plumbing problem, not a pricing or judgment dispute, and the CEO treated it as such.

**Rulings:**

1. **Schema fix** — approved. The CEO agreed this is an internal correction to align storefront's action emission with the executor's actual contract, unblocking ESC-020–023 for clean resubmission next cycle. No pricing or publishing judgment was involved in this ruling itself.

2. **Drinkware margin-floor repricing** — approved as proposed. Mug ladder ($12/14/16 across 11/15/20oz) and tumbler ($26.00) both clear the 30% floor against confirmed Printful costs. Execution still awaits resubmission under the corrected schema.

3. **Giclée publishing (six drafts: five Neptune's Garden + Bodysurfer)** — rejected. The CEO was explicit that this isn't a rejection of the listings' merits or a reopening of the original blocking condition's substance — it's a deliberate hold: the CEO wants to work through the cyanotype-prints-vs-originals positioning question directly before committing these SKUs to live commerce. This line stays undecided and unpurchasable until that broader positioning call is made, likely at a future meeting.

4. **Bodysurfer listing copy/title update** — approved. Brings the new print's title and description into "Josh Ball Art" brand styling per the charter's naming rule. Execution awaits schema-corrected resubmission (tied to ESC-023).

5. **Four carried-over "Josh Ball Art" branding renames** (mug, beanie, two posters) — approved. These have sat proposed, unchanged, for two weeks; the CEO cleared them to bring existing live POD titles into required brand styling.

No tier promotions, brand-identity changes beyond the approved renames, or new spend commitments were made this cycle. The giclée-publish hold means priority-2 revenue remains at zero live listings going into W33.
