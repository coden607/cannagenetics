export function normalize(value) {
  return String(value ?? '').normalize('NFKD').replace(/\p{M}/gu, '').toLowerCase();
}

export function matchesAward(row, filters = {}) {
  const terms = normalize(filters.q).split(/[^\p{L}\p{N}]+/u).filter(Boolean);
  const haystack = normalize(row.search);
  return terms.every(term => haystack.includes(term))
    && ['competition', 'year', 'country', 'evidence'].every(key => !filters[key] || String(row[key]) === String(filters[key]))
    && (!filters.contributor || String(row.contributors ?? '').split(' ').includes(filters.contributor));
}
