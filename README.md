# 🌱 CannaGenetics

**The worldwide database and ordering hub for the best cannabis genetics — seeds *and* clones — from every major supplier, compared, documented, and sourced.**

CannaGenetics is a living PRD + plan repo. It is where the product is defined, phased, and kept honest before a single line of production code ships. The codebases that eventually get built from this repo will live in their own repos; *this* repo is the source of truth for **what** and **why**, plus the operating manual for how a dark factory keeps the data fresh forever.

Sister project: **[CannaIntel](https://github.com/coden607/cannaintel)** — the intelligence platform. CannaIntel watches the *market* (prices, drops, signals, sentiment); CannaGenetics is the *catalog + ordering layer* (structured genetics data, lineage, supplier registry, compliant link-out ordering).

---

## What this repo contains

| File | What it is |
|---|---|
| [`PRD.md`](./PRD.md) | Full product requirements: problem, thesis, hypothesis, personas, features, compliance-first architecture, tech-stack recommendation, phased delivery with acceptance criteria, non-goals, open questions. |
| [`PLAN.md`](./PLAN.md) | Execution plan: start → flawless deploy → dark-factory maintenance loop → update cadence. |
| [`SUPPLIERS.md`](./SUPPLIERS.md) | Starter supplier registry schema + seed list of major suppliers. Field definitions only — **no scraped data**. |
| [`data/schema.sql`](./data/schema.sql) | Initial relational schema: breeders, cultivars, lineage edges, suppliers, listings (with source URLs + timestamps), jurisdictions. |
| [`docs/dark-factory.md`](./docs/dark-factory.md) | The maintenance loop in detail: jobs, schedules, failure handling, data-quality gates. |
| [`.github/workflows/maintenance.yml`](./.github/workflows/maintenance.yml) | The dark-factory workflow itself: price refresh, new-drop detection, dead-link sweep, schema drift check. |

## Vision

A grower anywhere in the world can open CannaGenetics, filter by *their* jurisdiction and grow setup, and see every noteworthy cultivar — seed or clone — with verified lineage, breeder, chemotype (THC/CBD), flowering time, terpene profile, and live, sourced listings from every major supplier that carries it. They compare. They pick. They order via a compliant link-out. And the database never goes stale, because a dark factory updates it on a fixed cadence — forever.

## What needs Steve's approval before this goes live

This paragraph is the honest gate. **(1) Legal review:** cannabis genetics legality varies wildly by jurisdiction — seeds are legal in much of the EU and some US states, illegal in others, and clones are far more restricted; nothing ships until a qualified lawyer reviews the jurisdiction-filtering and age-gate design, and the decision to be a *link-out ordering hub* rather than a direct seller needs written legal sign-off. **(2) Supplier & affiliate agreements:** linking out to suppliers is one thing; scraping their listings, displaying their prices, and earning affiliate revenue all require their terms to permit it — each major supplier needs its terms reviewed, and affiliate arrangements negotiated before monetization features activate. **(3) Hosting decisions:** the stack choice in the PRD (Postgres + Next.js on a standard VPS/serverless) is a recommendation, not a decision — hosting region matters for both data law and content-law exposure, and Steve owns that call. Until all three are approved, this repo stays a planning artifact.

## Status

🟡 **Planning.** PRD v0.1, no production code exists yet. See `PRD.md → Phases` for the path to a deployable MVP.
