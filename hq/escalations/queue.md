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



## ESC-017
- Raised: 2026-07-31
- Raised by: market_intel
- Urgency: normal
- Summary: ArtWalk Ventura 2026 (Sept 26–27, Main Street, $0 application fee via ZAPPlication) is a real, on-brand booth opportunity for originals/prints, but the application deadline could not be confirmed from indexed pages and may be close — CEO or a human should check zapplication.org (event ID 14550) directly this week to avoid missing the window.

## ESC-018
- Raised: 2026-08-03
- Raised by: storefront
- Urgency: normal
- Summary: Six giclée listings (five Neptune's Garden cyanotypes + Complete Collection bundle) plus the new Bodysurfer B&W photography print are all still in draft — the entire priority-2 revenue line is unpurchasable. Confirm what's blocking publish (Prodigi sample approval? copy incomplete?) or approve publishing them.

## ESC-019
- Raised: 2026-08-03
- Raised by: storefront
- Urgency: normal
- Summary: Drinkware pricing — Bodysurf Fin Mug and Logo Mug at $9-13 likely breach the 30% margin floor on several size/color combos (cost $6.95-8.50); Tumbler at $19.00 against $17.29 cost is only ~9% margin. Structured shopify.set_price actions with a size-ladder fix are proposed below for approval.

## ESC-020
- Raised: 2026-08-03
- Raised by: executor/storefront
- Urgency: normal
- Summary: Action rejected: shopify.set_price — missing params: new_price, product_id; unexpected params: external_id, prices. Agent rationale: Current $9-13 pricing falls under the 30% margin floor on several combos against $6.95-8.50 Printful costs; this ladder clears 30%+ even at worst-case cost per size band.
- Action ref: ACT-2026-W32-0002

## ESC-021
- Raised: 2026-08-03
- Raised by: executor/storefront
- Urgency: normal
- Summary: Action rejected: shopify.set_price — missing params: new_price, product_id; unexpected params: external_id, prices. Agent rationale: Same blank/cost structure as the Bodysurf Fin Mug (different design only); same margin shortfall, same fix.
- Action ref: ACT-2026-W32-0003

## ESC-022
- Raised: 2026-08-03
- Raised by: executor/storefront
- Urgency: normal
- Summary: Action rejected: shopify.set_price — missing params: new_price, product_id; unexpected params: external_id, price. Agent rationale: Current $19.00 against $17.29 cost is ~9% margin, far under the 30% floor; $26.00 clears ~33.5% margin while staying close to comparable Printful-tumbler market pricing.
- Action ref: ACT-2026-W32-0004

## ESC-023
- Raised: 2026-08-03
- Raised by: executor/storefront
- Urgency: normal
- Summary: Action rejected: shopify.update_listing_copy — missing params: product_id, seo; unexpected params: external_id. Agent rationale: Standing order 2 requires SEO/brand-voice copy for every new giclée release; current title has no "Josh Ball Art" styling and no description is confirmed present in the sync.
- Action ref: ACT-2026-W32-0005
