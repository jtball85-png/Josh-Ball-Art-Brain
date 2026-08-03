# CEO request: full drinkware review — 2026-08-03

The CEO asked for a full review of the store's drinkware, beyond the
enamel cup (already corrected today: $14.00 -> $19.50, 36% margin, per
ESC-016). Cover the remaining three items:

- **Bodysurf Fin White Glossy Mug** (external id `white-glossy-mug-1`) —
  11oz/15oz/20oz, currently $9.00-$13.00
- **Josh Ball Art Logo White Glossy Mug** (external id `white-glossy-mug`) —
  11oz/15oz/20oz, currently $9.00-$13.00
- **Sunsets & Sips Bodysurf Fin Tumbler** (external id `wine-tumbler`) —
  currently $19.00

## What the CEO wants

1. **Collection name** — check how these items are organized/named in the
   Shopify storefront's collection structure (e.g. is there a "Drinkware"
   collection, is it named and described well, does it match the charter's
   brand voice) and recommend changes if warranted.
2. **Pricing for each item** — confirm real per-variant costs and margin
   against the charter's 30% floor, and recommend a specific price for
   each. Propose every price change as a structured `shopify.set_price`
   action per your directive (it will always escalate to the CEO for
   approval — that's expected, not a blocker).

## Prior research already on record (garage/store-review-2026-07-23.md)

Real Printful costs were already pulled for these items during the
2026-07-23 margin audit and, as of this review, no price action was ever
taken on them — the CEO's original decision (2026-07-24 decision log:
"POD mug/enamel-cup margin review and reprice") only executed the enamel
cup. Use these as your starting point; re-verify against the current
synced catalog rather than assuming they're still accurate:

- **Tumbler**: cost $17.29, currently $19.00 retail = 9% margin (nearly
  break-even, $1.71/sale). Recommendation on record: $27-29 (Printful's
  own suggested retail for this blank is $25-30; comparable artist
  tumblers sell $28-35).
- **Bodysurf Fin Mug**: costs vary by size/color combo ($6.95-$8.50),
  21 of the combos priced 23-37% margin, most under the 30% floor.
  Recommendation on record: floor at $12.50-13 flat, or a size ladder
  (11oz $12 / 15oz $14 / 20oz $16).
- **Logo Mug**: same cost structure as the Bodysurf Fin Mug (blank is the
  same product, different design), currently $9-13 on $8.50-9.50 costs.
  Recommendation on record: same ladder as above.

Do not just restate these numbers — confirm they still hold against the
live-synced catalog, and use your own judgment on the final recommended
price per your directive's standing orders.
