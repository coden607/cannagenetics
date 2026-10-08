# CannaGenetics — Execution Plan

**Version:** 0.1 · **Companion:** [`PRD.md`](./PRD.md) · [`docs/dark-factory.md`](./docs/dark-factory.md)

This is the operating manual: start → flawless deploy → dark-factory maintenance → update cadence. It assumes the PRD's phases and adds the *how* of running the thing forever with minimal human touch.

---

## 1. Start (Week 0–2): Repo → Schema → Seed

1. **Ratify the spec.** Run `plan-architecture` against `PRD.md` to convert recommendations (stack, API shape, hosting region) into decisions. Output: `spec/` in the implementation repo.
2. **Stand up the data layer.** Postgres from `data/schema.sql`. Migrations from day one (no schema drift by drift).
3. **Hand-curate the MVP seed** (no scraping): 50 cultivars × all Phase-1 suppliers, each listing with a source URL + `first_seen`/`last_verified` timestamp. This is intentionally slow — it builds the curation muscle and the trust baseline.
4. **Age gate + jurisdiction gate skeleton** before any real data is reachable. The legal firewall is built *first*, not last.

**Exit criteria:** schema migrated; seed loaded; gates enforced in a dev environment.

## 2. Flawless Deploy (Week 3–6): Thin, Sourced, Observable

- **Scope lock:** only what Phase 1 acceptance requires — cultivar/supplier pages, comparison, search+filter, gates, link-out. Anything else is a distraction and a legal-surface increase.
- **Deploy checklist (the "flawless" part):**
  - [ ] Migrations run automatically on deploy; rollback path tested.
  - [ ] Every listing row renders its source URL + verification date visibly.
  - [ ] Jurisdiction gate tested against a matrix of known-legal / known-illegal cases (seed-only vs. banned vs. clone-only).
  - [ ] Age gate server-side enforced (curl-level test, not just UI test).
  - [ ] Uptime + error alerting on; dark-factory job failure alerts on.
  - [ ] Seed data freshness verified on deploy day — nothing stale ships.
- **Soft launch:** to a handful of growers + the CannaIntel audience. Watch the PRD success metrics from hour one.

**Exit criteria:** PRD Phase 1 acceptance met end to end by a real external user.

## 3. Dark-Factory Maintenance (forever)

The dark factory is the set of scheduled jobs that keeps the database alive without heroics. Full detail in [`docs/dark-factory.md`](./docs/dark-factory.md); the workflow itself lives at [`.github/workflows/maintenance.yml`](./.github/workflows/maintenance.yml).

### Jobs

| Job | Schedule (UTC) | What it does |
|---|---|---|
| `price-refresh` | Daily 04:17 | Re-verify every live listing: price, stock status, page-alive check. Updates `last_verified`, flags stale/dead. |
| `new-drop-detection` | Daily 04:47 | Diff supplier catalog pages vs. known listings → open "new listing" records with source URLs into a review queue. |
| `dead-link-sweep` | Daily 05:13 | Crawl all listing source URLs; mark dead; open correction issue; notify if a supplier's dead-link ratio spikes. |
| `tos-reaudit` | Weekly, Monday 06:23 | Re-check ToS posture fields for top-25 suppliers; diff vs. stored posture; flag changes for human review. |
| `jurisdiction-config-review` | Weekly, Monday 06:47 | Queue the `jurisdictions` table for human legal re-review (no auto-changes — this table is the firewall). |
| `schema-drift-check` | Weekly, Monday 07:13 | Assert live schema matches `data/schema.sql`; open issue on drift. |

### Principles

- **Human-in-the-loop for new data, machine for refresh.** New listings land in a review queue; refreshes of existing listings auto-commit. This keeps the sourced-data trust contract intact while staying dark-factory cheap.
- **Everything alert-shaped.** A failed job pages Steve. A data-quality gate failure opens a GitHub issue. Silence = health.
- **Idempotent jobs.** Every job can be re-run safely; timestamps and diffs make re-runs no-ops.
- **Never auto-modify the legal firewall.** `jurisdictions` table changes require explicit human merge. Always.

## 4. Update Cadence

| Surface | Cadence | Owner |
|---|---|---|
| Listing prices/stock | Daily (dark factory) | Bot |
| New listings review queue | 3×/week human pass (15 min) | Steve |
| Supplier registry / ToS posture | Weekly re-audit + on-change review | Bot flags → Steve |
| Jurisdiction config | Weekly queue + immediate on legal news | Steve (with counsel) |
| New cultivar deep-dives | 2 per week, hand-curated | Steve |
| PRD/PLAN revision | Monthly, or on hypothesis result | Steve |
| Public changelog | Monthly rollup | Bot-drafted → Steve approves |

## 5. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Supplier ToS forbids price display | PRD open question — fallback to "available at" linking; registry tracks posture per supplier. |
| Legal shift in a jurisdiction | Jurisdiction review queue fires weekly; firewall table is human-gated; rendering is strictly driven by it. |
| Data rot (stale listings) | Staleness badge renders to users; success-metric target is ≥95% verified ≤14 days; sweep escalates on breach. |
| Affiliate-revenue trust erosion | Transparency labels; measure click-diversity metric; be ready to drop affiliate program (it's P2 monetization, not core). |
| Dark-factory silent failure | Job failure alerts + weekly human review queue; success metrics dashboard watched monthly. |
