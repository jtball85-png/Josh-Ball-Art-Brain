# Website Audit Skill

A Claude skill that performs comprehensive website content and UX audits. It combines content editing, UX strategy, creative direction, and technical QA into a single structured review.

Recipe skill by [ajota.uk](https://ajota.uk/), sourced from https://github.com/appariciojunior/website-audit-skill and installed into this repo's project-local skills directory (`.claude/skills/website-audit/`), matching the convention already used by `garage-research` and `garage-design`. The original README's `/mnt/skills/user/website-audit/` install path is specific to a different Claude surface and doesn't apply here.

## What it does

Give it a URL and it will crawl every page, read every word, and produce a structured audit document covering:

- **Content & copy quality** — spelling, grammar, dialect consistency, placeholder text, weak copy, missing content
- **UX structure** — page flow, narrative arc, self-selection, cognitive load, missing sections (FAQ, "how it works", final CTA)
- **Conversion** — CTA clarity, pricing presentation, social proof placement, objection handling, urgency signals
- **Creative direction** — brand voice consistency, content hierarchy, pacing, emotional arc
- **Technical QA** — broken links, duplicate content, alt text quality, SEO basics
- **Product/course deep-dive** — for sites with multiple offerings, checks every individual page for completeness and consistency

The output is a markdown file (saved to `garage/research/` in this repo) with every issue categorised by severity, corrected text where applicable, and a priority action plan.

## What's in the box

```
website-audit/
├── SKILL.md        — The main skill (audit methodology + output format)
├── checklist.md     — Detailed checklist with 50+ individual checks
└── README.md        — You're reading it
```

See `SKILL.md` for the full methodology and severity markers.
