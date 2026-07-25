# Escalation Queue

Open items needing CEO judgment. Resolved items move to `resolved.md` —
never delete an item from here, only move it.

Format per entry (urgent items are sorted first by `hq.py`, not by their
position in this file):

```
## ESC-{NNN}
- Raised: YYYY-MM-DD
- Raised by: {department}
- Urgency: urgent | normal
- Summary: ...
```

<!-- new escalations are appended below this line -->



## ESC-016
- Raised: 2026-07-24
- Raised by: executor/storefront
- Urgency: normal
- Summary: Action rejected: shopify.set_price — shopify.set_price is not in storefront's allowed_actions. Agent rationale: Enamel Cup priced at $14.00 against a $12.42 catalog cost is an 11% margin, well under the charter's 30% floor -- flagged urgent in the 2026-07-23 garage margin review (garage/store-review-2026-07-23.md) and echoed in the W30 storefront report escalation. Recommended move to $19.50 (36% margin). CEO directed this specific price change 2026-07-24 as a live test of the approve-and-execute pricing path.
- Action ref: ACT-2026-W30-0014
