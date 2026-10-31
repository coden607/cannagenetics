# Award-history research archive

The initial archive contains 39 sourced award records from seven competition series, 21 credited participants, and selected years from 1994 to 2026. This is explicitly partial coverage, not every competition or cultivar worldwide.

## Shipped model and search

- `data/awards.json` is the source of truth. IDs distinguish competition series, edition year, original category and placing. Publication year is not substituted for event year.
- Competition, cultivar/entry and credited participant are distinct. A grower winning with a cultivar name is not automatically its original breeder. Collaborations remain credited as published.
- Every result has a source URL, checked date and evidence class: organizer record, publisher report or participant claim. Historical self-reports remain distinguishable from organizer results.
- The generated cup page supports combined text, competition, year, country, evidence and contributor filters, shareable queries, accessible result counts, and a complete static table when JavaScript is unavailable.
- Contributor research pages link back to results and source evidence. Global search includes awards, contributors and competitions. Cultivar pages link to matching name records, without claiming cut authentication.
- Missing data and coverage are visible. An unindexed year does not imply that no competition occurred. Award placement is not a laboratory measurement or universal quality ranking.
- Images are not copied from third parties. Adding an entry image requires source, attribution and verified license or documented permission. No authenticated entry photos have been added in this milestone.

## Validation

Run:

```sh
python3 -m unittest discover -s scripts -p 'test_award_archive.py'
node --test scripts/awards-search.test.mjs
python3 scripts/build_site.py
python3 scripts/check_site.py
```

The pre-existing generator contained literal `\\n` escapes in the `img_for` function declaration and could not parse. The archive integration repairs that syntax and regenerates the previously stale static outputs. Browser visual verification remains separate from the link and logic checks.

## Expansion contract

Use official organizer archives first, then attributed editorial coverage and clearly labeled participant claims. Expand one source/edition at a time. Preserve original category labels, collaborations and uncertain placing; do not infer missing lineage, chemistry, grower identity or image rights from a strain name.

Review terms and access permissions before adding any automated source adapter. Use permitted feeds/APIs or bounded factual extraction. Never copy descriptions, photos or full catalogs wholesale, bypass access controls, or publish a harvested claim as verified. Automated candidates require provenance validation and duplicate/conflict review before entering the curated archive.

The next research milestone is an edition-by-edition coverage ledger with conflicting claims and original-organizer corroboration. An all-time completeness claim requires an enumerated source universe and measured coverage; that evidence does not yet exist.

This change adds research history and cross-reference tools. It adds no purchase/inventory routing, clone ordering, price scraping, cultivation instructions, credentials, schedulers or production deployment. ContinuityOS policy is applied locally; live routing and token savings are not claimed without runtime evidence.
