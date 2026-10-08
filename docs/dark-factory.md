# The Dark Factory — Maintenance Loop

The dark factory is the scheduled machinery that keeps CannaGenetics current forever without heroics. Defined in [`PLAN.md`](../PLAN.md) §3; this doc is the reference for job behavior, failure handling, and data-quality gates.

## Loop diagram

```
                ┌────────────────────────────────────────────────┐
                │            GitHub Actions (cron)               │
                │                                                │
  daily 04:17 ──┤ price-refresh ──► verify live listings ──► DB  │
  daily 04:47 ──┤ new-drop-detection ──► review_queue (human)    │
  daily 05:13 ──┤ dead-link-sweep ──► mark dead / open issue     │
  weekly 06:23 ─┤ tos-reaudit ──► diff posture ──► review_queue  │
  weekly 06:47 ─┤ jurisdiction-config-review ──► human queue     │
  weekly 07:13 ─┤ schema-drift-check ──► issue on drift          │
                └────────────────────────────────────────────────┘
                          │ failure on any job
                          ▼
                    pages Steve (silent = healthy)
```

## Job contracts

### price-refresh (daily 04:17 UTC)
- For every non-dead listing: fetch `source_url`, extract current price/stock, update row + `last_verified`, write `audit_log`.
- Respects per-site rate limits and crawl-delay; honors robots.txt. A listing that 404s twice across two runs is flagged, not auto-killed.
- Idempotent: re-running with unchanged page data is a no-op.

### new-drop-detection (daily 04:47 UTC)
- Diffs supplier catalog pages against known `listings` + `supplier_breeders`.
- New candidates are inserted into `review_queue` with full payload + source URL. **Nothing auto-publishes.** A human reviews and approves/rejects (target: 3×/week, 15 min).

### dead-link-sweep (daily 05:13 UTC)
- HEAD/GET every listing `source_url` and supplier `website_url`.
- Dead → `is_dead = true` + `audit_log` entry + GitHub issue. If a supplier's dead ratio >10%, escalate to a registry-review issue (possible site move or shutdown).

### tos-reaudit (weekly, Mon 06:23 UTC)
- Re-fetches each active supplier's terms pages; diffs against stored `tos_posture`.
- Any change → `review_queue` with before/after diff. Price-display revocation immediately suppresses prices (renders "available at" mode) pending review — the safe default.

### jurisdiction-config-review (weekly, Mon 06:47 UTC)
- Opens a human-review issue for the `jurisdictions` table. **Automation never edits this table.** It is the legal firewall; changes require Steve (and counsel where flagged).

### schema-drift-check (weekly, Mon 07:13 UTC)
- Asserts the live DB matches `data/schema.sql` in this repo (via migration checksums). Drift → blocking issue + halt on further automated writes.

## Data-quality gates

| Gate | Threshold | Breach action |
|---|---|---|
| Listing staleness | ≥95% of in-stock listings `last_verified` ≤14 days | Page Steve; sweep runs a catch-up pass |
| Dead-link ratio | <10% per supplier | Registry-review issue opened |
| Unsourced rows | 0 — any row missing `source_url` is a bug | Blocking issue; automated writes halt |
| Review queue age | Nothing `pending` >7 days | Nudge; auto-expire at 30 days |

## Why humans stay in the loop

Machines are great at *refreshing what is known* and terrible at *vouching for what is new*. The trust contract ("every fact sourced, every price verified") is only credible if admission of new facts requires a person. So: refresh auto-commits, admission goes through the queue. That is the whole dark-factory philosophy in one sentence.
