# 🌍 World Genetics Atlas (v0.2)

*Formerly "Seedbank Index" — same repo, bigger mission.*

The **World Genetics Atlas** is the open atlas of cannabis genetics: every seed bank
and breeder worldwide, every documented strain and landrace, the phytochemistry that
defines them, community phenotype mapping, and cross-source comparison — from every
major source, everywhere in the world.

Community-curated. Source-cited. Honest about what it doesn't know.

> ⚠️ **Legal note:** cannabis seed and cultivation laws vary by jurisdiction and change
> often. This repository is **informational only** and contains no legal advice.
> Know your local laws.

## Entity map

```
                        ┌────────────────────────────┐
                        │      sources.json           │
                        │  provenance + trust tiers   │
                        │  lab > cup > breeder >      │
                        │  community > academic       │
                        └──────────────┬─────────────┘
                                       │ every claim cites a source
        ┌──────────────┬───────────────┼───────────────┬──────────────────┐
        ▼              ▼               ▼               ▼                  ▼
┌──────────────┐ ┌────────────┐ ┌─────────────┐ ┌──────────────┐ ┌────────────────┐
│ seedbanks    │ │ strains    │ │ compounds   │ │ pheno_reports│ │ compare/       │
│ 23 banks +   │ │ 28 landmark│ │ 35 chems:   │ │ phenotype    │ │ engine spec:   │
│ breeders     │ │ landraces→ │ │ cannabinoids│ │ expressions  │ │ same strain ×  │
│ (v0.1 data,  │ │ cup winners│ │ terpenes    │ │ (example     │ │ N banks,       │
│ moved as-is) │ │            │ │ flavonoids  │ │  templates)  │ │ scored +       │
│              │ │            │ │ alkaloids*  │ │              │ │ explained      │
└──────────────┘ └────────────┘ └─────────────┘ └──────────────┘ └────────────────┘
                                       ▲
                                       │ future: price/COA connectors
                               pipelines/ — ingestion roadmap (PRs first)
```

*Alkaloids flagged honestly: trace occurrence, severely understudied in cannabis.*

## Data files (`data/`)

| file | contents | entries |
|---|---|---|
| `seedbanks.json` | banks/breeders/retailers (carried over from v0.1, unchanged) | 23 |
| `strains.json` | landmark strains: landraces, classics, cup winners, first autoflower | 28 |
| `compounds.json` | cannabinoids, terpenes, flavonoids, alkaloids | 35 |
| `pheno_reports.json` | expression-report schema + 3 clearly-labeled example templates | 3 |
| `sources.json` | provenance registry with 5 trust tiers | 10 sources, 5 tiers |

## Schema versioning

- **v0.1** (2026-10-05): single-entity seedbank directory.
- **v0.2** (2026-10-05): multi-entity platform — strains, compounds, pheno reports,
  provenance registry, comparison + pipeline specs.
- Schemas are additive-first: new fields may appear; existing fields are not renamed
  or removed within a major version. Consumers should ignore unknown fields.

## Trust model

Nothing here is "true" by default. Every entry carries:

- `verify_status`: `seed-v0` (community seed — unverified) → `verified` (source-checked).
- `source`: URL or `community-knowledge`, backed by `sources.json` trust tiers
  (lab COA > cup result > breeder claim > community report > academic).

Conflicts resolve by tier: a lab COA overrides a breeder claim, which overrides
community consensus. Ranges (e.g. `typical_thc_pct`) are published/community-reported
figures, not guarantees — treat them as leads for verification, not facts.

## Language rules (non-negotiable)

- **Zero medical claims.** Nothing here treats, cures, or diagnoses anything.
- Effect language is **community-reported framing** ("users commonly report…"),
  never clinical.
- Uncertainty is stated in-line (`reported`, `disputed`, `flagged for lab sourcing`).
  If we don't know, the entry says so.

## Contributing

See `pipelines/README.md` for the full ingestion roadmap. Short version:

1. PRs only — every claim needs `source` + `verify_status`.
2. `python3 -m json.tool` must pass on every data file.
3. Slugs must cross-reference existing entities.
4. Follow the language rules above.

Part of the **Continuity OS** fleet.
