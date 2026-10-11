# pipelines/ — Ingestion Roadmap

How data gets INTO the atlas, in trust order. The golden rule:

> **Every claim flows through `data/sources.json` provenance. No source id, no merge.**

## Phase 1 — PR-based curation (SHIPPING NOW)

- Humans (or agent-assisted humans) submit PRs adding/editing entries.
- Every new claim carries: `source` (URL or `community-knowledge`) + `verify_status`.
- Maintainers review for: valid JSON, tier-appropriate sourcing, no medical claims,
  community-reported framing on all effect language.
- Conflicts resolve by trust tier: `lab_test > cup_result > breeder_claim > community_report > academic`.

### PR checklist (contributor copy-paste)

- [ ] `python3 -m json.tool data/<file>.json` passes
- [ ] slugs referenced exist in the relevant entity file
- [ ] every new claim has `source` + `verify_status`
- [ ] effect language is community-reported framed, zero medical claims
- [ ] examples/PII: no real grower names, handles only

## Phase 2 — Structured curation tooling (next)

- Validation CI: JSON schema + slug cross-reference checks (the `_check.py` pattern) run on PRs.
- Issue templates per entity (new seedbank / new strain / new compound / pheno report).
- Promotion workflow: `seed-v0` → `verified` requires ≥1 tier-1/2 source or 2+ tier-3
  independent sources confirming the same claim.

## Phase 3 — Connectors (future, gated)

Automated fetchers for catalogs, prices, COA repositories.

**Hard gates before any connector ships:**

1. **ToS check** — written permission or explicit allowance in the target site's terms.
2. **robots.txt** — respected per RFC 9309; no bypassing crawl-delay or disallow rules.
3. **Rate limits** — conservative defaults; backoff on 429.
4. **Provenance stamped at ingest** — every connector record lands with its tier and a
   `source` entry created automatically; unverifiable records are quarantined, never merged.
5. **No PII** — connectors never collect grower identities; only public, published data.

Candidate connector targets (discussion only, no commitment): seedbank public catalogs
(with permission), public COA repositories, cup-results pages.

## Anti-goals

- No scraping behind logins. No CAPTCHA bypass. No mirroring restricted databases.
- No auto-generated medical/therapeutic claims, ever — connector output is held to the
  same language rules as human PRs.
- No entries without provenance. Volume is not the goal; **verifiability** is.
