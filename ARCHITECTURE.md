# Architecture — CannaGenetics MVP

## Problem & goals
A grower should open one catalog, filter to where they live, and see sourced cultivar and supplier records, then leave to the supplier's own site. No store, no payment, no grow guides.

## Approaches considered
- Planning docs only. Already shipped. Does not meet the deploy request.
- Static catalog generated from the sister seedbank-index data. Ships now on the existing Vercel link. Recommended.
- Next.js plus Postgres from `data/schema.sql`. Right for live prices and the dark factory. Blocked on supplier terms and a lawyer's sign-off, so not this pass.

## Recommended approach
Static read-only site in `web/`, generated from seedbank-index JSON, deployed from `coden607/cannagenetics`. Age gate and a user-declared jurisdiction filter sit in front. Prices and clone sales stay off.

## Key decisions
- **Stack** — plain HTML/CSS/JS. No framework, no database, no secrets. Alternative was Next.js; deferred.
- **Data** — cultivars, banks, lineage text, reported THC ranges. Shape matches the PRD entities. Storage is JSON, not Postgres yet.
- **Boundaries** — link-out only. No checkout. No medical claims. Jurisdiction filter is a user declaration, not a legal determination.
- **Other** — clone tab names nurseries and does not list them for sale.

## Missing pieces
Lawyer review. Supplier terms for price display. Postgres and the dark-factory refresh loop. Verified (not seed-v0) records.

## Spikes & experiments
Question: can the catalog stay useful without prices?
Spike: this MVP.
Decision rule: keep the static shell if people use comparison; add Postgres only after terms allow prices.

## Open questions
Launch jurisdictions. Hosting region. Affiliate versus neutrality.
