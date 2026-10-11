# compare/ — Cross-Source Comparison Engine Spec

The atlas's core job: when **strain X is sold by N seedbanks**, tell the reader what
*actually differs* between those offers — and how much to trust each claim.

## Input

- `data/strains.json` — the strain's baseline record
- `data/seedbanks.json` — the banks selling it (`available_at_seedbanks`)
- `data/pheno_reports.json` — community expression data per source
- `data/sources.json` — trust tier of every cited claim
- Future: price/seed-count data per bank (connector-gathered, see `pipelines/`)

## What gets compared

| axis | description | data needed |
|---|---|---|
| **Identity / lineage delta** | Does bank A's "Durban Poison" match bank B's? Compare parent claims against the consensus lineage; flag renames, IBLs, "S1"/"BX" reworkings, or obvious rebrands. | breeder_claim sources (tier 3) vs cup/academic |
| **Claimed chem vs lab chem** | Bank's printed THC range vs COA-measured results (tier 1 overrides everything lower). | lab_test sources vs catalog copy |
| **Phenotype consistency** | Height/structure/flower-week distributions across `pheno_reports` grouped by seedbank source. Are two banks' versions even growing alike? | pheno_reports (tier 4 aggregate) |
| **Availability & value** | Pack size, price/seed, stock status, single-vs-multi-breeder storefront. | connector data (future) |
| **Provenance quality** | How much of the bank's claim chain is lab-verified vs marketing copy? Score from `sources.json` tier mix. | sources.json |

## Scoring model (proposal — v0.2 is spec-only)

Each offer gets **0–100 per axis**, weighted:

```
identity_match     30%   (exact lineage claim match to consensus)
chem_verified      25%   (lab-confirmed = full marks; breeder claim = 60%; unknown = 20%)
pheno_consistency  20%   (variance of reported expressions vs strain baseline)
value              15%   (normalized price/seed vs cohort median)
provenance         10%   (tier-weighted source quality)
```

- **Composite** = weighted sum → letter grade (A ≥ 85, B ≥ 70, C ≥ 55, D < 55).
- Tiers apply as multipliers: a tier-1 (lab) conflict **overrides** any number of
  lower-tier claims. Ties break toward more `lab_test`-backed entries.

## Worked example (HYPOTHETICAL — illustrative numbers only)

**Strain:** Northern Lights #5 (`northern-lights-5`) × 3 banks.

| axis | sensi-seeds | seedsman (house brand) | nirvana-seeds |
|---|---|---|---|
| identity | claims canonical Afghani×Thai lineage (breeder_claim, tier 3) — 28/30 | house label, lineage copy thin — 20/30 | claims NL lineage, no parents named — 18/30 |
| chem | breeder-published range 16–21%; no public COA → 15/25 | published 15–20%; community labs seen ~17% avg (tier 4) → 13/25 | published 14–19%; no COA → 12/25 |
| pheno | 2 example-template-consistent reports, dense/8wk cluster → 17/20 | wide spread, 7–10 wk → 12/20 | moderate spread → 14/20 |
| value | premium €/seed (pack of 10) → 9/15 | mid €/seed, multi-pack discounts → 12/15 | budget €/seed → 14/15 |
| provenance | catalog + cup heritage cited → 8/10 | house-brand opacity → 5/10 | reseller, sources thin → 4/10 |
| **composite** | **77 (B)** | **62 (C+)** | **62 (C+)** |

Reader takeaway: "All three plausibly sell NL#5 genetics; the catalog-backed line
has the cleanest claim chain; the budget line wins on value. No lab COAs exist
for any of them — treat all potency numbers as unverified."

> This example uses invented numbers to demonstrate the engine's output shape.
> Real scores only get computed once curation adds source-cited inputs.

## Status

v0.2 = specification only. Implementation roadmap lives in `../pipelines/README.md`.
