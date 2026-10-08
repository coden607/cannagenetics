# CannaGenetics — Supplier Registry (Starter)

**Status:** Schema + seed names only. **This file contains NO scraped data.** Every field below is a definition of what the registry records; values are populated only via curation with source URLs, during implementation.

The registry lives in the `suppliers` table (see [`data/schema.sql`](./data/schema.sql)). Each entry must eventually satisfy every field in §1 before it may render a live listing.

---

## 1. Required fields for every supplier entry

| Field | Type | Notes |
|---|---|---|
| `name` | text | Canonical name, e.g. "Seedsman". |
| `website_url` | text | Official storefront URL. |
| `hq_jurisdiction` | fk → jurisdictions | Where the business is based. |
| `ships_to` | fk[] → jurisdictions | Derived from their stated shipping policy, each with a source URL. |
| `product_types` | enum[] | `seeds`, `clones`, or both. |
| `seed_types` | enum[] | `photoperiod`, `autoflower`, `feminized`, `regular`, `CBD-rich`. |
| `payment_methods` | text[] | Card, crypto, bank transfer, cash, etc. |
| `breeders_carried` | int | Count of breeders stocked; full edge table in `supplier_breeders`. |
| `tos_posture` | jsonb | **Key compliance field:** `{ linking_allowed, price_display_allowed, scraping_allowed, affiliate_program, notes, source_url, last_audited }`. |
| `reputation_score` | numeric | 0–5, from public review aggregation (source-linked). |
| `founded_year` | int | Where publicly stated. |
| `affiliate_status` | enum | `none`, `applied`, `active`, `rejected`. |
| `source_urls` | text[] | Every claim above must trace to a source URL. |
| `first_seen` / `last_verified` | timestamptz | Dark-factory timestamps. |

**Rule:** a supplier may not appear in listings until `tos_posture.linking_allowed` is confirmed. A supplier may not show *prices* until `price_display_allowed` is confirmed. These are hard gates, not guidelines.

## 2. Starter registry — seed names (no data yet)

Legend: 🌱 seeds · 🌿 clones · ⚡ autoflower specialist

### Seed banks (multi-breeder)

| Supplier | Type | Why on the starter list |
|---|---|---|
| Seedsman | 🌱 | One of the largest selections; long operating history; global shipping reputation. |
| ILGM (I Love Growing Marijuana) | 🌱 | Huge beginner-facing brand; strong US presence; germination-guarantee model. |
| Royal Queen Seeds | 🌱 | Major EU breeder-bank; own catalog + third-party lines. |
| Barney's Farm | 🌱 | Iconic Amsterdam breeder; award-heavy catalog; direct storefront. |
| Seeds Here Now | 🌱 | US-centric distributor carrying many US boutique breeders. |
| Neptune Seed Bank | 🌱 | Carries hype US genetics; useful for drop-tracking comparisons. |
| Great Lakes Genetics | 🌱 | Long-standing US seed source. |
| Attitude Seed Bank | 🌱 | Vast multi-breeder catalog; long history. |
| Herbies | 🌱 | Large EU/global bank with frequent promos — good price-dispersion signal. |

### Breeders selling direct

| Supplier | Type | Why |
|---|---|---|
| Ethos Genetics | 🌱 | Top US breeder; direct drops; strong provenance documentation culture. |
| Mephisto Genetics | ⚡ | The autoflower gold standard; limited-drop model = perfect alert-system test case. |
| FastBuds | ⚡ | High-volume autoflower house; wide international availability. |
| Dutch Passion | 🌱/⚡ | Historic breeder; early feminized/autoflower adopter. |
| Sensi Seeds | 🌱 | Historic Amsterdam institution; deep catalog. |
| Humboldt Seed Company | 🌱 | California mainstream; lab-tested chemotype publishing habit. |
| Exotic Genetix | 🌱 | Hype-forward US breeder; frequent drops. |
| Cannarado Genetics | 🌱 | Cross-heavy catalog; popular with the provenance crowd. |
| Gnome Automatics / Night Owl | ⚡ | Boutique autoflower community favorites. |
| Roc Bud Inc | ⚡ | Community-driven autoflower breeder. |

### Clone / nursery level (only where legal — mostly US legal states)

| Supplier | Type | Why |
|---|---|---|
| Dark Heart Nursery | 🌿 | California's best-known nursery; clones + teens; professional operation. |
| Kind Roots Nursery (CO) | 🌿 | Colorado nursery serving legal market. |
| Local dispensary clone shelves (per-region) | 🌿 | Where legal, dispensaries list clones — tracked as regional listing sources with strict jurisdiction gating. |

> **Clone suppliers are the highest legal-sensitivity tier.** They are registered only where the jurisdiction config explicitly permits clones, and each region is reviewed with counsel before activation. See PRD §7.

## 3. Registry growth rules

1. Additions come from: dark-factory detection queue, community suggestion (with sources), or deliberate curation.
2. Every addition needs §1 fields complete *before* going live.
3. Suppliers whose ToS forbids listing display are excluded or downgraded to no-price mode — never scraped-and-hoped.
4. Reputation scores are recomputed on the weekly audit; sources attached.
