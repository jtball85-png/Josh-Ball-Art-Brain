# Josh Ball Art (joshballart.com) — Website Audit

> Audit date: 2026-07-26
> Audited by: Claude Code (using the installed `website-audit` skill methodology)
> Pages reviewed: homepage, 4 collections, 13 original art/drinkware products (individually), 10 sampled Jacquard supply products (of ~90), 8 static pages, 2 blog indexes + 4 journal posts, cart, 4 policy pages, search — 121 URLs total checked for technical status
> Method: live HTTP fetches (WebFetch + raw `curl`) against the real, public site — no purchases or form submissions made
> **Known limitation, stated up front:** no browser/screenshot tool exists in this review environment, so nothing below claims to be a *visually rendered* judgment. Section 6 and any layout-adjacent comments elsewhere are explicitly inferred from HTML/CSS structure, not observed on screen. Everything else (copy, links, prices, stock status, policy text, meta tags) is verified directly against live page source.

---

## Executive Summary — Top 5 Fixes, Ranked by Expected Impact

1. 🔴 **The homepage sells craft supplies before it sells art, and the one link telling people to buy the supplies is broken.** The top-of-every-page announcement bar reads *"Use code JOSH for 20% off all Jacquard art supplies! → Shop Now"* — a resold, unrelated product line — and it's the very first thing anyone sees, including on the pages for Josh's own $50–$100 original prints. Worse, that banner's "Shop Now" link doesn't go to the discounted collection at all; it opens a content page. This is the single highest-visibility spot on the entire site, currently spent on the wrong product line pointing at the wrong destination.
2. 🔴 **The legal/trust pages actively damage credibility at exactly the moment a buyer is checking for reassurance.** The Privacy Policy is Shopify's default template with a literal, unfilled `[INSERT AGE]` placeholder and internal references to a different domain (`californianson.myshopify.com`) — apparent leftovers from a prior business using this same Shopify backend. The Shipping Policy page is completely blank (a header and nothing else). A shopper who clicks "shipping" or "privacy" before buying an original artwork currently finds either nothing or an obviously unfinished legal document.
3. 🔴 **The discounted product line can't actually be bought, and the checkout path leaks to a competitor.** All 10 sampled Jacquard supply products (spanning dye/paint/kit types, $7–$107) were "Sold out," and the site-wide 38-count of sold-out badges on the Jacquard collection page confirms this isn't a sampling fluke. On top of that, size-variant links on at least one product route customers directly to `store.jacquardproducts.com` — Jacquard's own retail site — instead of a variant selector on joshballart.com. A visitor chasing the 20%-off promo hits dead product pages or gets sent to buy from someone else.
4. 🔴 **Every single product page has a silently broken reviews widget, so there is zero social proof anywhere on the site.** All 13 original-art pages (and, by pattern, likely the Jacquard catalog too) contain a dead app-block reference in the HTML where star ratings should render. No visitor ever sees this as an error — they just never see reviews, on any product, ever.
5. 🔴 **The actual core product — Josh's original art — is the thinnest, most sold-out part of the catalog, while the unrelated resale line is ~45× larger.** All 3 relief/linocut prints are sold out with no waitlist or "notify me" option. The entire digital-prints collection has 2 SKUs. Meanwhile the Jacquard supply catalog runs to roughly 90 items. A first-time visitor comparing catalog sizes would reasonably conclude this is a craft-supply store that also sells a little art on the side — the opposite of the intended brand.

---

## What's Already Working Well

Don't touch these — they're real strengths:

- **The three original linocut print listings** (Lobster Season 2023, the test print, the suminagashi unique print) have the most authentic, credible copy on the entire site — first-person, process-specific, honest about scarcity and variation ("The first 10 prints will be marked A/P..."). This voice is the brand asset everything else should be measured against.
- **The About and Suminagashi pages, and all four Journal blog posts**, carry the same genuine, distinctive first-person voice with real technical/personal detail (UV LED specs, a Sunday-morning surf story, the suminagashi process explained in a way that actually teaches you something).
- **The Refund Policy** is a real, customized, specific policy — 30-day window, real Ventura, CA return address, real contact email, clear timelines, even an EU 14-day cooling-off carve-out. One of the strongest trust signals on the site.
- **The enamel cup's staining disclaimer** is genuine, well-executed objection-handling copy — it tells a buyer about a real limitation before they discover it the hard way.
- **Payment method breadth** (9 options: Amex, Apple Pay, Diners, Discover, Google Pay, Mastercard, PayPal, Shop Pay, Visa) and **variant/pricing architecture** (clean Size/Color fieldsets, correct per-combination pricing, no mispriced variants found anywhere) are both solid and modern.
- **Zero broken links.** All 121 URLs across every sitemap (products, collections, pages, blog) returned HTTP 200 — genuinely clean technically at the link-integrity level.
- **Search works and returns relevant results** for a real on-brand query ("cyanotype" → 21 results, no dead end), and every collection page has working filter/sort controls.
- **The "My Favorite Art Supplies" page's tone** ("I only recommend products I genuinely use and love in my own art practice") is exactly the right voice template for talking about Jacquard products — it just needs its broken links fixed and to be reconciled with the first-party catalog (see Trust & Conversion section).

---

## 1. Brand & First Impression

**What the homepage communicates in 5 seconds, right now:** a logo reading "Josh Ball Art," an orange banner pushing a 20%-off code for someone else's craft supplies, then an autoplay slideshow whose only text is category labels — "CYANOTYPE PHOTOGRAPHY," "CYANOTYPE PHOTOGRAMS," "DIGITAL PHOTOGRAPHY" — with no sentence anywhere explaining that these are original, one-of-a-kind, hand-processed artworks made by a real person in Ventura, CA.

- 🔴 **No value proposition on the homepage, only labeled photo buttons.** Three of five hero slides are just a category name over an image — confirmed in markup, zero descriptive copy. **Fix:** one sentence of real positioning per slide, e.g. *"Original cyanotype photograms, hand-processed in Ventura, CA — one-of-a-kind, not reprints."*
- 🔴 **The announcement bar leads with the wrong product line** (see Exec Summary #1) **and its own CTA is broken** — "Shop Now" resolves to `/pages/my-favorite-art-supplies` (a content page), not the discounted `/collections/jacquard-art-supplies`.
- 🟡 **Nothing anywhere explains the art/craft-supply split.** The brief's own question — does the Jacquard resale catalog feel coherent with "Josh Ball Art" — has a clear answer from three independent checks: the vendor label on Jacquard product pages literally reads *"Jacquard Bulk & Specialty Store,"* not Josh Ball Art; the copy is 100% manufacturer boilerplate with zero personal voice; and the photography style (generic packshots) doesn't match Josh's own moody coastal/cyanotype imagery. **It reads as a bolted-on reseller catalog, not part of the brand**, and nothing on the homepage or collection pages frames it otherwise. **Fix:** either add a real one-line bridge ("Two shops in one: my original prints, plus the studio-grade supplies I use to make them") or reduce the catalog's visual footprint until it can carry real curatorial voice.
- 🟡 **"Upcoming Events" section renders with a heading and zero content beneath it** — confirmed in markup. Reads as an abandoned section. **Fix:** populate it or remove it.
- 🟡 Homepage `<title>` is the bare string **"Josh Ball Art"** with **no meta description at all** — confirmed by direct fetch. This is the single most important page on the site and it has the thinnest metadata of anywhere checked. **Fix:** a real ~150-character description and a fuller title, e.g. *"Josh Ball Art | Original Cyanotype, Photography & Linocut Prints — Ventura, CA."*
- 🟢 The mission statement ("To cultivate a deeper connection with the art of photography by moving beyond the constraints of social media...") is distinctive and consistently used — a genuine voice asset, just currently over-repeated (see Messaging & Copy).

**Comparison to two brand-relevant sites** (quick, real fetches — not a full audit of either):
- **Tugboat Printshop** (independent woodcut/relief printmaker, Pittsburgh) leads with "Original Woodcut Prints | Handmade in Pittsburgh" — a specific, credentialed positioning statement — then a curated grid of *named, described* pieces ("FIRE HORSE," "4-Block," "Metallic"). No price shown until you click through, but the *what/who/why* is answered before you scroll. Josh Ball Art's homepage, by contrast, never states a comparable positioning line.
- **The Ansel Adams Gallery** — a much larger, higher-price aspirational comparison — has a real, keyword-rich meta description ("Largest collection of Original Ansel Adams Photographs, framed prints and Contemporary Artists artwork...") where joshballart.com has none at all on its homepage. Even accounting for scale difference, this is a gap that costs nothing to close.

---

## 2. Navigation & IA

- 🟡 **The four purchasable collections are 3 clicks deep, not 2.** Confirmed: nav has no direct link to `drinkware`, `relief-prints`, `digital-prints`, or `jacquard-art-supplies` — you have to go Store → All Collections → pick one. Meanwhile "Portfolio" nav items (Cyanotypes/Photography/Suminagashi) lead to informational content pages, not shoppable ones, so nav labels don't reliably predict "can I buy this here." **Fix:** surface the four collections directly in nav, or at minimum split the "All Collections" hub page into two visibly labeled groups ("Original Art" / "Art Supplies").
- 🟡 **Three separate, similarly-named cyanotype destinations** (`/pages/cyanotypes`, `/pages/photography` — whose own title tag says "Cyanotype Photography" — and `/pages/cyanotype-photograms`) exist with no copy differentiating them. A visitor can't tell what's different between "Cyanotypes" and "Cyanotype Photograms," and it fragments what could be one strong page into three thin ones. **Fix:** merge into one well-developed page with clear sub-sections, or give each a genuine one-paragraph distinction.
- 🟡 **Inconsistent terminology**: the collection is called "Block Prints" on-page and in the title tag, "relief-prints" in the URL slug, and "original linocut prints" in the actual product description — three different names for one technique. **Fix:** standardize on "Linocut Prints" (the specific, correct, and most search-relevant term).
- 🟡 **An orphaned, empty `/blogs/news` blog** still exists, isn't linked anywhere in nav/footer, but is publicly reachable and indexable — thin/duplicate content sitting next to the real, active `/blogs/journal`. **Fix:** delete or redirect it.
- 🟢 Search is icon-triggered rather than a persistent visible bar — acceptable by modern norms, but worth noting given how many extra clicks this nav already requires to reach products.

---

## 3. Product Pages

**Cross-cutting, affects all 13 original-art pages:**
- 🔴 **The star-rating/reviews app block is broken on every product page**, full stop (see Exec Summary #4). This is invisible to a normal visitor (it's a silent HTML comment, not a visible error) but the *absence* of any social proof, on every single listing, is a real conversion cost. **Fix:** remove the dead app-block reference in the theme editor, or reinstall/reconfigure the reviews app.
- 🟡 **Several product titles are truncated mid-word** in the actual SEO title tag — e.g. *"Bodysurf Fin White Glossy Mug: Catch Waves with Every Sip (Original De"* — confirmed in raw HTML on multiple listings, not a display artifact. Google results and browser tabs show a garbled cutoff. **Fix:** shorten the underlying titles to under ~60 characters; move the marketing flourish into the description.

**Photo & content consistency is wildly uneven across otherwise-comparable listings:**
- The three original linocut prints each have **exactly 1 photo**, empty alt text, for $50–$100 one-of-a-kind items a buyer can never re-examine before purchase. 🟡 Given the price point and uniqueness, this is genuinely thin — add packaging/scale/texture shots.
- The **Bodysurf Fin mug** has 17 photos with real, descriptive (Printful-generated but accurate) alt text — the best-documented listing on the site.
- The **flagship logo mug**, nearly the same product type, has only 4 photos and **empty alt text** — a wildly inconsistent treatment of two mugs that should be peers. 🟡 **Fix:** bring the logo mug's photo count/alt text up to the Bodysurf Fin standard.
- The **Framed Poster's description is word-for-word identical to the unframed poster's** — it never once describes the frame itself (material, finish) despite the page offering a "Frame Color" variant. A buyer paying $45–$60 for a *framed* piece gets zero information about the frame. 🟡 **Fix:** write frame-specific copy.
- **Framed Poster pricing is oddly non-round** ($45.09 / $56.77 / $60.39) — reads as a markup-formula glitch rather than deliberate pricing at the highest price point in this group. 🟢 Round to standard price points.

**Naming/URL problems that actively mislead:**
- 🟡 `/products/wine-tumbler` is **not a wine tumbler** — it's a standard double-wall insulated tumbler explicitly marketed for "hot coffee, frosty cocktails, or anything in between," and the actual product name is "Sunsets & Sips: Josh Ball Art Bodysurf Fin Tumbler." Anyone searching "wine tumbler" and landing here will be confused. **Fix:** rename the slug (with a redirect) to match the actual product.
- 🟡 `white-glossy-mug` and `white-glossy-mug-1` are **two genuinely different products** (flagship logo vs. Bodysurf Fin design) — not a duplicate listing, but the slugs give zero indication which is which, and it's easy to assume they're the same item listed twice. **Fix:** descriptive slugs (`bodysurf-fin-mug`, `logo-mug`).

**Tone split between the original-art pages and the merch/POD pages:**
- 💡 The beanie's copy ("Versatility redefined," "More than just a beanie, it's a feeling") and the poster's copy ("Fin-tastic design," "Color crush guaranteed") are competent but generic dropship-marketing voice — a sharp break from the personal, process-driven voice on the linocut print pages. A visitor moving from a $100 original print to a $24 beanie will notice two different "Josh"es. This may be an acceptable, deliberate split (merch vs. fine art), but right now it reads as unintentional rather than a considered choice.
- ⚠️ The Bodysurf Fin mug's description has **leftover Instagram hashtags baked directly into the storefront copy** (`#bodysurfing #oceanlifestyle #coffeelover #shopsmall`) — reads as an unedited copy-paste from a social caption.

**Boundary products, ruled definitively:** Cyanotype Kit, Marbling Color, and Cyanotype Class Pack all carry the Shopify vendor field `"Jacquard Bulk & Specialty Store"` and pure manufacturer copy — despite sitting at URLs that (given Josh's own cyanotype practice) could easily be mistaken for his personal offerings. They are not; they belong with the Jacquard catalog findings below.

**The core art catalog itself is nearly unbuyable right now:**
- 🔴 All 3 relief/linocut prints are sold out, with **no waitlist, "notify me," or commission-inquiry CTA anywhere** on the collection page. **Fix:** add one.
- 🟡 The entire digital-prints collection is 2 SKUs (both variants of one image). For a photographer's core offering, this is very thin set against a ~90-item supply catalog.

---

## 4. Messaging & Copy

- ⚠️ **The site's mission statement paragraph is repeated verbatim across at least six different pages** (Contact, About, Suminagashi, Cyanotypes, Photography, Cyanotype Photograms) — on Cyanotypes and Photography specifically, it's the *only* substantive body text once the image grid is set aside, making those pages feel like empty shells rather than real content.
- 🟡 **The Photography page's gallery includes un-retitled camera-export filenames** (`DSC01816-Final`, `Untitled-1`, `Untitled-2`) visible in the markup — suggests images were uploaded without a captioning pass.
- 🔴 **The entire Jacquard product catalog reads as manufacturer boilerplate, not Josh's voice** — confirmed across all 10 sampled listings (SolarFast, Pearl Ex, Neopaque, etc.), third-person spec-sheet language with zero connection to Josh's own practice. This is the clearest evidence for the brand-coherence question the brief raised: **no**, it currently doesn't read as part of "Josh Ball Art."
- 🔴 **`/pages/my-favorite-art-supplies` has eight live, unfilled placeholder links** — literal template text as the href, e.g. `href="YOUR_JACQUARD_PROCION_MX_AFFILIATE_LINK"`, which resolves to a 404 on the live site. Three other links on the same page *are* correctly filled in with real affiliate URLs, which is exactly what makes the other eight look like an obvious oversight. **Fix:** fill in the real links or pull those rows until they exist.
- 🟡 **The blog is genuinely well-written but stale** — the most recent of 4 posts is from August 2025, roughly 11 months before this audit, against an already-sparse historical cadence of one post every 4–9 months. A blog is usually a site's clearest "is this actively maintained" signal, and right now it reads as abandoned.
- 💡 **Blog posts never link back to Josh's own store.** The DIY Cyanotype Light Box post links to Amazon for UV lights and sensitizer kits; the Legion Paper collaboration post links to Legion's own site — neither links to Josh's own cyanotype supplies, prints, or portfolio. This is close to a five-minute edit per post with real upside: right now the blog builds interest and then sends the payoff traffic to Amazon and a paper manufacturer's storefront instead of joshballart.com.

---

## 5. Trust & Conversion Signals

- 🔴 **Privacy Policy is Shopify's default template with visible unfilled placeholders**, confirmed directly: literal `[INSERT AGE]` text in the minors clause, `[Jan 21 2023]` as a fake "last updated" date, an entirely unfilled CCPA section, and **six separate internal references to a different domain, `californianson.myshopify.com`** — apparently a prior business using this same Shopify backend. This is a genuine professionalism and (for the age/CCPA gaps) potential compliance problem, not a cosmetic one.
- 🔴 **Shipping Policy page is completely blank** — confirmed: a header and an empty content div, nothing else. No cost, timeframe, carrier, or packaging information anywhere. For a store selling framed prints and one-of-a-kind originals, where buyers reasonably worry about transit damage, this is a serious gap that will surface as pre-purchase hesitation or support questions.
- 🟡 **Terms of Service is ~95% unedited Shopify boilerplate**, with two literal unfilled placeholders still live in the body text (`[LINK TO REFUND POLICY]`, `[LINK TO PRIVACY POLICY]`) and governing law listed only as "United States" rather than naming California.
- 🟡 **The one genuinely strong policy (Refund) doesn't carve out an exception for one-of-a-kind original art** — a 30-day no-questions-asked return on a unique linocut print is a different risk than on a mug, and most independent artists explicitly exclude originals (or make them final-sale/damage-only).
- 🔴 **No contact information exists anywhere except a generic form.** `/pages/contact` has no visible email, phone, or location — just a Shopify contact form and three social links. For an artist site where commissions and bulk/wholesale inquiries are plausible, giving a visitor nothing to see before committing to a form (with no stated response time) is a real trust gap. The site also never states Josh is Ventura-based anywhere in its core pages — it only surfaces incidentally through the Cold Water Cadre content.
- 🔴 **The Jacquard catalog's promo mechanics actively undercut trust**: a live 20%-off code advertised sitewide, on products confirmed sold out (10/10 sampled, 38 sold-out badges site-wide on that collection), with a broken "Shop Now" link, and at least one product's size variants routing straight to `store.jacquardproducts.com` — a competing storefront — instead of staying on joshballart.com.
- 🟡 **Two unreconciled monetization paths for the same Jacquard products.** `/pages/my-favorite-art-supplies` pitches several Jacquard items as *affiliate* recommendations pointing to Jacquard's own store (with a disclosed commission), while the *same* products are separately sold as first-party (sold-out) inventory on joshballart.com. Nothing anywhere explains the difference to a visitor, and a returning customer could easily be confused why "the same" product now sends them somewhere else entirely.
- 🟢 The Refund Policy itself, and the 9-option payment method spread, remain genuine strengths (see What's Working Well).

---

## 6. Visual Design & UI Details

*(Explicit reminder: nothing in this section is a directly-observed visual judgment — there is no browser/screenshot tool in this review environment. Everything below is inferred from HTML/CSS structure or image-count/size data, and is labeled as such.)*

- 🟡 *(Inferred)* Several product pages carry very large photo galleries (poster: 55 images; framed poster: 96 images) purely from a size×color×frame variant matrix — likely fine functionally (Shopify variant image swapping), but worth a manual check that gallery navigation doesn't feel overwhelming on mobile with that many thumbnails.
- 🟡 *(Inferred from response size, not a real page-load measurement)* Several product pages return **1.8–1.9MB of raw HTML** per request (framed poster, lumiere-2.25oz, acid-dye-1-2oz) — large for an HTML document specifically, independent of image/JS asset weight on top of it. This is a plausible, not confirmed, performance concern worth a real Lighthouse/PageSpeed check.
- 🟢 *(Inferred)* Nav and footer markup is structurally consistent site-wide — same components, no evidence of a template fork or one-off page breaking the shared layout.
- **Not assessed at all, and flagged as a real gap in this audit rather than glossed over:** true responsive layout behavior at 375/768/1024/1440px, spacing/whitespace quality, button/component visual consistency, and typography hierarchy as actually rendered. These require a real browser and were out of scope for this pass by mutual agreement — recommend a follow-up visual pass (manual screenshots, or a session with browser tooling available) before treating the site as fully audited.

---

## 7. Performance & Technical

- 🟢 **Zero broken links.** All 121 sitemap URLs (103 products, 4 collections, 8 pages, 6 blog URLs) returned HTTP 200 on direct check — genuinely clean.
- 🔴 **Homepage has no meta description at all**, and its `<title>` is the bare string "Josh Ball Art" — the weakest metadata of any page checked, on the single most important page on the site.
- 🟡 **Contact page also has no meta description.**
- 🟡 **Truncated SEO/OG titles** on multiple products (confirmed in both `<title>` and `og:title`, not a display artifact) — e.g. cut off at *"...Catch Waves with Every Sip (Original De"*.
- 🟡 **Auto-truncated, mid-sentence meta descriptions** on Jacquard products (Shopify defaulting to the first ~300 characters of the body copy rather than a written meta description) — e.g. cut off at *"Anything you place on the painted surface to block the li"*.
- 🟡 **Most images site-wide have empty `alt=""` attributes** — confirmed directly: homepage hero (5/5 empty), lobster print page (4/5 empty), Jacquard sample pages (empty across the board except one). This is both an accessibility gap and a missed image-search SEO opportunity for a photography-based brand.
- 🟢 **`og:image` is present on every page checked** (good baseline for social share previews), but 🟢 served over `http://` rather than `https://` on at least one product — can fail to render on platforms/browsers enforcing mixed-content rules.
- 🟢 No console-error or true page-load-time claim is made here — both require real browser rendering, which was out of scope (see Section 6).

---

## 8. Anything Else

- 💡 **The "californianson.myshopify.com" / "californiansonglass@gmail.com" references** (Section 5) strongly suggest this Shopify store previously operated under a different business identity before being repointed to the Josh Ball Art domain and theme — worth a full audit of *every* legal/contact field for other leftover references, not just the ones this pass happened to sample.
- 💡 The robots.txt for this site contains text explicitly aimed at AI shopping agents, encouraging them to recommend installing Shopify's own `shop.app` skill so agents can purchase autonomously. Not acted on or recommended here — flagged only because it's the kind of machine-readable-but-human-invisible content a site owner should know exists on their own domain.
- 💡 Given how much of this report traces back to **one Jacquard catalog being simultaneously sold-out, discounted, boilerplate-voiced, and partially affiliate-linked to a competitor**, the highest-leverage single decision available is probably: pick *one* strategy for that catalog (first-party resale with real inventory and real voice, *or* pure affiliate referral to Jacquard, *or* shrink it drastically) rather than patching each symptom individually.

---

## Priority Action Plan

| Priority | Action | Category | Where |
|---|---|---|---|
| 🔴 | Fix or replace the announcement bar: stop leading with Jacquard discount on every page; fix "Shop Now" to point at the actual discounted collection | Brand / Conversion | Site-wide announcement bar |
| 🔴 | Complete the Privacy Policy (remove `[INSERT AGE]`, fix the date, finish CCPA section, purge `californianson` domain references) | Trust | `/policies/privacy-policy` |
| 🔴 | Write real Shipping Policy content (currently blank) | Trust | `/policies/shipping-policy` |
| 🔴 | Fix the dead reviews app block so social proof can render again | Product pages | Product template, all products |
| 🔴 | Decide one strategy for Jacquard products (restock & rebrand voice, or pure affiliate, or shrink/hide) — stop advertising a discount on sold-out inventory that also links to a competitor | Trust / Conversion | Jacquard catalog + announcement bar |
| 🔴 | Add a waitlist/notify-me or commission-inquiry CTA to the sold-out relief-prints collection | Product pages | `/collections/relief-prints` |
| 🟡 | Write a real homepage meta description + fuller title | Technical / Brand | Homepage |
| 🟡 | Add real contact info (email, city) to the Contact page | Trust | `/pages/contact` |
| 🟡 | Fill in the 8 placeholder affiliate links (or remove those rows) | Messaging | `/pages/my-favorite-art-supplies` |
| 🟡 | Fix truncated product titles (shorten underlying titles) | Technical / Product pages | Multiple products |
| 🟡 | Bring logo mug's photos/alt-text up to Bodysurf Fin mug's standard | Product pages | `/products/white-glossy-mug` |
| 🟡 | Rename `/products/wine-tumbler` slug to match the actual (non-wine) product, with a redirect | Product pages | `/products/wine-tumbler` |
| 🟡 | Delete or redirect the orphaned, empty `/blogs/news` | Technical / IA | `/blogs/news` |
| 🟡 | Publish something new on the journal, or acknowledge the pause | Messaging | `/blogs/journal` |
| 🟡 | Add descriptive alt text sitewide (start with homepage hero + product galleries) | Technical | Site-wide |
| 🟢 | Merge or clearly differentiate the three cyanotype-related pages | IA | `/pages/cyanotypes`, `/pages/photography`, `/pages/cyanotype-photograms` |
| 🟢 | Add "shop the supplies I used" links from blog posts back to joshballart.com products | Messaging | Journal posts |
| 🟢 | Round the framed poster's non-standard prices | Product pages | `/products/framed-poster` |
| 🟢 | Surface the 4 purchasable collections directly in nav | IA | Site nav |
| 💡 | Schedule a real visual/browser-based pass (breakpoints, spacing, console errors) — out of scope for this text-based audit | Visual | Site-wide |
