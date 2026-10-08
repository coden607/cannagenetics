# CannaGenetics — Product Requirements Document

**Version:** 0.1 · **Status:** Planning · **Owner:** Steve (coden607)
**Companion docs:** [`PLAN.md`](./PLAN.md) · [`SUPPLIERS.md`](./SUPPLIERS.md) · [`data/schema.sql`](./data/schema.sql)

> This PRD follows the `plan-create-prd` discipline: it is **intent (what/why)**, not engineering instructions (how). Where a recommendation is made (e.g. tech stack), it is framed as a recommendation to be ratified at the spec stage.

---

## 1. Problem Statement

**Who:** Home and small-commercial cultivators, breeders tracking provenance, and genetics collectors — worldwide.

**The pain:** Cannabis genetics information is fragmented across dozens of breeder sites, seed-bank storefronts, forums, and spreadsheets. A cultivar's real lineage is often disputed or marketing-inflated; prices for the *same* cultivar vary 2–4× between suppliers; drops (especially limited autoflower and clone releases) sell out in hours with no single alerting surface; and clones — where legal at all — live in a separate, even murkier information ecosystem from seeds. Nobody can currently answer, in one place: *"What are the best-documented genetics I can legally obtain where I live, from whom, at what price, right now — and what's the real family tree behind them?"*

**Cost of not solving it:** Growers overpay or get counterfeits; breeders can't verify provenance; limited drops are missed; and buyers in restricted jurisdictions accidentally land on storefronts that will not ship to them anyway — wasted time at best, legal exposure at worst.

## 2. Evidence

- *Assumption — validate via [market scan + 20 grower interviews].* Price dispersion for identical cultivars across major seed banks is observable by hand-sampling; turn this into measured data during MVP discovery.
- *Assumption — validate via [community audit].* Lineage disputes (e.g. forum threads contradicting breeder marketing) are widespread; sample 50 popular cultivars and count discrepancies.
- *Assumption — validate via [drop-tracking pilot].* Limited releases (Mephisto-style drops, clone drops) sell out fast enough that a centralized alert surface plausibly has real value; measure via a mailing-list pilot before building the full alert system.

## 3. Thesis (why build it, why now)

**Why this:** The catalog layer of cannabis genetics doesn't exist in structured, sourced, jurisdiction-aware form. Forums have the knowledge but not the structure; seed banks have the listings but not the cross-supplier comparison and not the lineage rigor. A neutral, comparison-first database with mandatory source citations is a genuinely different product from every storefront — and storefronts can't build it without favoring themselves.

**Why now:** Genetic provenance matters more as markets mature and regulation tightens; growers increasingly treat cultivar selection like the data problem it is; and automated maintenance (the dark factory) has only recently become cheap enough that a one-person operation can keep a worldwide database current indefinitely.

**Why it beats the current cope:** The cope today is "open 15 tabs, trust the breeder's marketing, hope the forum thread is right." CannaGenetics replaces that with one searchable, sourced, price-comparing surface — and wins if it is trusted *because* it cites everything and takes no supplier's side.

## 4. Hypothesis (the falsifiable bet)

```
We believe that a jurisdiction-aware, fully-sourced genetics database with live
cross-supplier price comparison will cause serious home growers to use it as their
FIRST stop when choosing genetics, resulting in repeat comparison behavior that
supersedes tab-hopping across seed banks.

We'll know we're RIGHT if, within 6 months of MVP launch, ≥30% of weekly active
users run ≥2 comparison searches per session AND ≥25% of listing clicks go to
suppliers other than the single cheapest-visible default (i.e. users are engaging
with comparison, not just bouncing through).

We'll know we're WRONG if usage is one-and-done (median sessions/user < 2 in the
first 90 days) or if trust collapses (sourced-citation error reports exceed
corrected records per month) — meaning growers don't trust or don't need a
neutral catalog.
```

## 5. Target Users & JTBD

### Personas

| Persona | Role / context | Trigger |
|---|---|---|
| **The Home Grower** ("Maya") | Grows 2–6 plants per cycle at home, legal jurisdiction, budget-conscious. | Needs seeds for next cycle; hears hype about a cultivar; wants the best price on a verified pack. |
| **The Provenance Nerd** ("Dev") | Breeder / collector. Tracks lineage, hunts keeper phenos, cross-references parentage claims. | Disputes a breeder's lineage claim; plans a cross; verifies a clone's identity before buying. |
| **The Drop Hunter** ("Kai") | Autoflower/limited-release chaser (Mephisto-style drops, clone drops). | A limited drop is announced; wants an alert and a list of every supplier carrying it, instantly. |
| **The Cautious Buyer** ("Rosa") | Lives in a jurisdiction with tight rules; wants zero legal friction. | Wants to see only what's legal to *obtain where she lives*, and to be stopped if it's not. |

### JTBD (primary)

> **When** I'm planning my next grow and I've heard about a cultivar, **I want to** see its verified lineage, real chemotype stats, and every supplier that carries it with live prices — filtered to what I can legally buy where I live — **so that** I can order the right genetics from a trustworthy source without tab-hopping or legal guesswork.

### Non-users (explicitly NOT for)

- People seeking grow advice / cultivation tutorials (not this product; out of scope to avoid content-law surface).
- Anyone in a jurisdiction where possession/purchase is illegal — the product must *exclude* them by design, not serve them.
- Buyers wanting a direct storefront experience (CannaGenetics is comparison + compliant link-out, see §7).

## 6. Features

Priority: **P0** = MVP-critical · **P1** = shortly after MVP · **P2** = later.

### 6.1 Genetics Database (P0)
- **Cultivar records** with: name, aliases, breeder, type (photoperiod / autoflower / feminized / regular), **lineage as a directed graph** (parent cultivars as edges, with breeder-claimed vs. community-verified distinction), THC/CBD ranges, flowering time, yield class, difficulty, terpene profile (top 3–5 terpenes), and descriptive notes.
- **Genotype vs. chemotype separation:** lab-tested figures are labeled as such; breeder-claimed figures are labeled as claims. Never blur the two — this is the trust contract.
- **Clone vs. seed tracking:** a cultivar may exist as seed lines (multiple suppliers) *and* clone lines (nurseries, where legal). Both are first-class, with distinct listing types.

### 6.2 Supplier Registry (P0)
- Every supplier is a structured record: name, HQ jurisdiction, ships-to list, product types (seeds/clones), payment methods, reputation score, affiliate program status, and **terms-of-service posture** (linking allowed? price display allowed? scraping allowed?).
- Registry maintenance is a dark-factory job (see `PLAN.md`); ToS posture is reviewed on cadence.

### 6.3 Listings & Price Comparison (P0)
- A **listing** = one supplier's offer of one cultivar (seed pack size / clone unit), with: source URL, price in native currency, currency-normalized price, pack size, stock status, and **first_seen / last_verified timestamps**.
- Comparison view: same cultivar, all suppliers, sorted by normalized price; staleness badge when `last_verified` exceeds threshold.
- **Sourcing rule (hard requirement):** every listing row carries a source URL and a verification timestamp. No source → no listing. This is non-negotiable and is what separates this from scraped spam sites.

### 6.4 Search + Filter (P0)
- Filter by: breeder, type, THC/CBD range, flowering time, terpene, seed vs. clone, supplier, price band, in-stock only.
- **Jurisdiction filter is mandatory infrastructure** (see §7), not an optional facet.
- Full-text search over names + aliases ("GG4" finds "Gorilla Glue #4").

### 6.5 Alerts (P1)
- Drop alerts: new cultivar by tracked breeder, restock of watched cultivar, or new supplier carrying a watched cultivar.
- Price-drop alerts and "back under $X" alerts.
- Channel: email first, RSS/Discord later.

### 6.6 Lineage Explorer (P1)
- Graph view: cultivar → parents → grandparents, with claimed-vs-verified edge styling. The killer feature for the Provenance Nerd persona; also exposes breeding-project overlap.

### 6.7 Reputation & Community Signal (P2)
- Grower-reported outcomes (structured: actual flowering time observed, actual tested THC, grew-well-in-climate X) attached to cultivars, with abuse controls.
- Supplier rating aggregation with review provenance.

## 7. Compliance-First Architecture (requirements, not suggestions)

The product is designed *around* legal constraints, not retrofitted:

1. **Age gate:** hard age-verification gate (18+/21+ by jurisdiction) before any content access; server-side enforced, not a client-side modal joke.
2. **Jurisdiction filtering:** every user session is scoped to a declared jurisdiction; the database only ever *renders* cultivars, suppliers, and listings that are legal to obtain there. Where a cultivar exists as seeds but clones are banned (or vice versa), only the lawful form is shown. Where neither is lawful, the user is told — politely and plainly — that nothing is available.
3. **Link-out ordering, not direct sales:** CannaGenetics never takes payment, never holds inventory, never facilitates a transaction. It links out to the supplier's own storefront. This is both a legal-simplification and a trust decision.
4. **Seed-only where required:** per-jurisdiction configuration drives whether seeds, clones, both, or neither are listed. Config lives in the `jurisdictions` table (see `data/schema.sql`) and is reviewed on cadence — **this table is the legal firewall.**
5. **No cultivation content:** no grow guides, no grow logs. The product is about genetics provenance and sourcing only. Deliberately shrinks the content-law surface.
6. **Affiliate transparency:** if/when affiliate links exist, they are labeled as such, per FTC and EU consumer-protection rules.
7. **Right-to-be-delisted:** breeders/suppliers can claim their records and request corrections; a documented correction SLA exists. Being citable is a feature; being accurate is the contract.

## 8. Tech Stack (recommendation — ratify at spec stage)

> The PRD discipline says intent, not engineering. This section is a **recommendation** with the reasoning visible, for the `plan-architecture` stage to ratify or overturn.

- **Data store:** PostgreSQL (relational core: cultivars, lineage edges, listings, jurisdictions) — the schema in `data/schema.sql` assumes it. Full-text search via `tsvector` to start; dedicated search (Meilisearch/Typesense) only if P1 search demands it.
- **Backend/API:** a thin typed API layer (Node/TypeScript or Python/FastAPI — spec-stage call) with read-mostly endpoints; writes flow almost exclusively through the dark-factory ingestion jobs.
- **Frontend:** Next.js (SSR for SEO — this catalog lives or dies on search traffic), TypeScript, Tailwind. Static-first pages for cultivar/supplier detail, revalidated by the maintenance loop.
- **Hosting:** single VPS or serverless (hosting region = Steve's call, see README approval paragraph). Postgres managed or containerized.
- **Dark factory:** GitHub Actions cron (see `.github/workflows/maintenance.yml`) running the refresh/detect/sweep jobs; job runners call the ingestion pipeline against the live DB.
- **Seeded data:** none scraped at launch. Initial catalog is hand-curated from public breeder data + supplier catalogs *with per-record source URLs*, sized to prove the hypothesis (MVP: ~50 cultivars × all major suppliers, per §10).

## 9. Success Metrics

Outcome-shaped, not vanity:

| Metric | Target | How measured |
|---|---|---|
| Comparison engagement | ≥30% of WAU run ≥2 comparison searches/session | Server-side search events |
| Listing diversity | ≥25% of listing clicks go to non-default suppliers | Click-through events with ranking context |
| Data trust | Sourced-citation error reports ≤ corrected records/month | Correction queue vs. records fixed |
| Staleness | ≥95% of in-stock listings verified ≤14 days old | `last_verified` distribution (dark-factory telemetry) |
| Alert value (P1) | ≥20% of drop-alert emails drive a click within 24h | Email click tracking |
| Wrong-condition guardrail | median sessions/user ≥2 in first 90 days (else hypothesis falsified) | Session analytics |

## 10. Phases & Acceptance Criteria

### Phase 0 — Legal & Foundations (gate before any build)
- Lawyer review of jurisdiction-filtering, age-gate, and link-out model. **Exit:** written sign-off, or documented scope reduction.
- Supplier ToS posture audit for the top-10 registry entries. **Exit:** `SUPPLIERS.md` entries have ToS fields filled.
- **Acceptance:** README approval paragraph items 1–2 cleared.

### Phase 1 — MVP (the thinnest end-to-end proof)
- Postgres schema deployed; hand-curated seed: **50 cultivars × every listed supplier, each with source URLs.**
- Public read-only site: cultivar pages, supplier pages, comparison view, search+filter, jurisdiction gate, age gate.
- Dark factory v1: weekly listing verification, dead-link sweep.
- **Acceptance:** a real user can pick a jurisdiction, search a cultivar, see sourced live comparison, and click out to a supplier — end to end, on real data, legally filtered. Success metrics instrumentation live.

### Phase 2 — Alerts + Clone Tracking
- Alert system (drop/restock/price) for registered users; clone listings tracked as first-class (legal jurisdictions only).
- **Acceptance:** a limited drop is indexed and alerted ≤60 min after appearing on a supplier site; clone-vs-seed filtering works per jurisdiction.

### Phase 3 — Lineage Explorer + Scale
- Lineage graph UI; cultivar count to 500+; supplier registry to 25+; community outcome reports (abuse controls on).
- **Acceptance:** graph renders 3 generations for any cultivar with claimed/verified distinction; dark factory runs full loop unattended for 30 days with <5% job failure rate.

## 11. Non-goals (explicit)

- ❌ Direct sales, payments, carts, or inventory — ever (link-out only).
- ❌ Cultivation content, grow guides, or grow-log hosting.
- ❌ User-to-user trading or marketplace features.
- ❌ Medical/therapeutic claims about cultivars (chemotype data yes, health claims no).
- ❌ Mobile native apps in MVP (web-first; PWA if at all).
- ❌ Unsourced data at any point. If a fact can't be cited, it doesn't ship.

## 12. Open Questions

- [ ] Which jurisdictions does the MVP *launch* with? (Recommend: start where seeds are unambiguously legal.)
- [ ] How do we handle suppliers whose ToS forbid price display but allow linking? (N-th price? "available at" without number?)
- [ ] Breeder-verified program: what's the verification burden of proof for a breeder claiming a record?
- [ ] Currency normalization: daily FX from which source, and is a normalized price still "sourced"?
- [ ] Affiliate vs. neutrality: does taking affiliate revenue from supplier X impair comparison trust? Measure.
- [ ] Clone data sourcing: nurseries rarely publish structured data — what ingestion method survives ToS review?
- [ ] Hosting region final call (Steve).
