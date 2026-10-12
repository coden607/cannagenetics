# 🌱 CannaGenetics

**The worldwide database and ordering hub for the best cannabis genetics — seeds *and* clones — from every major supplier, compared, documented, and sourced.**

CannaGenetics is a living PRD + plan repo. It is where the product is defined, phased, and kept honest before a single line of production code ships. The codebases that eventually get built from this repo will live in their own repos; *this* repo is the source of truth for **what** and **why**, plus the operating manual for how a dark factory keeps the data fresh forever.

Sister project: **[CannaIntel](https://github.com/coden607/cannaintel)** — the intelligence platform. CannaIntel watches the *market* (prices, drops, signals, sentiment); CannaGenetics is the *catalog + ordering layer* (structured genetics data, lineage, supplier registry, compliant link-out ordering).

---

## What this repo contains

| File | What it is |
|---|---|
| [`web/`](./web) | The shipped static catalog (plain HTML/CSS/JS) — cultivar, supplier, and compound pages, comparison, lineage explorer, cross calculator, cups, geography, glossary. Generated; do not hand-edit. |
| [`scripts/build_site.py`](./scripts/build_site.py) | The static-site generator. Consumes `vendor/seedbank-index` JSON plus the aux data in `web/data/`, writes every page in `web/`. Rebuild with `python3 scripts/build_site.py`; validate with `python3 scripts/check_site.py`. |
| [`scripts/check_site.py`](./scripts/check_site.py) | Link checker over the generated site: internal links, sitemap entries, and nav links must all resolve. Exit 0 = clean. |
| [`PRD.md`](./PRD.md) | Full product requirements: problem, thesis, hypothesis, personas, features, compliance-first architecture, tech-stack recommendation, phased delivery with acceptance criteria, non-goals, open questions. |
| [`PLAN.md`](./PLAN.md) | Execution plan: start → flawless deploy → dark-factory maintenance loop → update cadence. |
| [`ARCHITECTURE.md`](./ARCHITECTURE.md) | The ratified MVP architecture: static read-only catalog, link-out only, age gate + user-declared jurisdiction filter in front. |
| [`SUPPLIERS.md`](./SUPPLIERS.md) | Starter supplier registry schema + seed list of major suppliers. Field definitions only — **no scraped data**. |
| [`data/schema.sql`](./data/schema.sql) | Relational schema for the future Postgres phase: breeders, cultivars, lineage edges, suppliers, listings (with source URLs + timestamps), jurisdictions. |
| [`docs/dark-factory.md`](./docs/dark-factory.md) | The maintenance loop in detail: jobs, schedules, failure handling, data-quality gates. |
| [`docs/maintenance.yml`](./docs/maintenance.yml) | The dark-factory workflow itself (canonical source; lives in `docs/` until the `workflow` OAuth scope is granted — see its header): price refresh, new-drop detection, dead-link sweep, ToS re-audit, jurisdiction review, schema drift check. |

## Vision

A grower anywhere in the world can open CannaGenetics, filter by *their* jurisdiction and grow setup, and see every noteworthy cultivar — seed or clone — with verified lineage, breeder, chemotype (THC/CBD), flowering time, terpene profile, and live, sourced listings from every major supplier that carries it. They compare. They pick. They order via a compliant link-out. And the database never goes stale, because a dark factory updates it on a fixed cadence — forever.

## What needs Steve's approval before this goes live

This paragraph is the honest gate. **(1) Legal review:** cannabis genetics legality varies wildly by jurisdiction — seeds are legal in much of the EU and some US states, illegal in others, and clones are far more restricted; nothing ships until a qualified lawyer reviews the jurisdiction-filtering and age-gate design, and the decision to be a *link-out ordering hub* rather than a direct seller needs written legal sign-off. **(2) Supplier & affiliate agreements:** linking out to suppliers is one thing; scraping their listings, displaying their prices, and earning affiliate revenue all require their terms to permit it — each major supplier needs its terms reviewed, and affiliate arrangements negotiated before monetization features activate. **(3) Hosting decisions:** the stack choice in the PRD (Postgres + Next.js on a standard VPS/serverless) is a recommendation, not a decision — hosting region matters for both data law and content-law exposure, and Steve owns that call. Until all three are approved, this repo stays a planning artifact.

## Status

🟢 **Static catalog shipped.** The MVP defined in `ARCHITECTURE.md` is live as a generated static site in `web/` (deployed from this repo). Data is seed-v0 — reported, not lab-verified; prices and clone sales stay off; ordering is compliant link-out only. The legal gates in the paragraph above still stand before any monetization or price display. The dark-factory maintenance loop (`docs/maintenance.yml`) is defined but not yet activated, and the Postgres phase remains blocked on lawyer review + supplier terms as described in `ARCHITECTURE.md`. See `PRD.md → Phases` for the full path.
