# 🌱 Seedbank Index — the open directory of every cannabis seed bank & breeder

Community-curated, source-cited directory. Built for CannaIntel's genetics module,
open to everyone. **v0.1 seed dataset** — entries carry `verify_status` and every
claim must earn a `source` before promotion from `seed-v0` → `verified`.

> ⚠️ **Legal note:** cannabis seed laws vary by jurisdiction and change often.
> This directory is informational only. Know your local laws.

## Schema (data/seedbanks.json)
| field | meaning |
|---|---|
| name / slug | display name / url-safe id |
| type | `breeder` (creates genetics) · `retailer` (sells others') · `bank` (both/house brand) |
| region | HQ country |
| specialty | e.g. autoflowers, landraces, cup winners, CBD |
| ships_to | broad regions, informational |
| notable_lines | flagship strains/series |
| source | public URL backing the entry |
| verify_status | `seed-v0` (community seed) → `verified` (source-checked) |
| last_checked | ISO date |

## Roadmap
- [ ] Grow dataset to exhaustive (every known bank/breeder, worldwide)
- [ ] Breeder ↔ strain cross-reference tables
- [ ] Landrace-focused registry (partner: CannaIntel ROADMAP M3/M4)
- [ ] Cup-winner sourcing index
- [ ] Change-verification workflow (source-cited PRs only)

Part of the **Continuity OS** fleet — data feeds CannaIntel's strain DB.
