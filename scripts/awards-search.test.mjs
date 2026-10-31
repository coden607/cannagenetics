import test from 'node:test';
import assert from 'node:assert/strict';
import { matchesAward } from '../web/awards-search.mjs';

const row = { search: 'NuWu Cup 2026 Member Berry High Heads', year: 2026, competition: 'nuwu', country: 'United States', evidence: 'organizer-record', contributors: 'high-heads' };
test('cross-reference search combines words across entrant, event, year and cultivar', () => {
  assert.equal(matchesAward(row, { q: 'high 2026 berry' }), true);
  assert.equal(matchesAward(row, { q: 'high 2025 berry' }), false);
});
test('year, competition, country, evidence and participant filters combine exactly', () => {
  assert.equal(matchesAward(row, { year: '2026', competition: 'nuwu', contributor: 'high-heads' }), true);
  assert.equal(matchesAward(row, { contributor: 'heads' }), false);
  assert.equal(matchesAward(row, { evidence: 'publisher-report' }), false);
  assert.equal(matchesAward(row, { country: 'Canada' }), false);
});
test('search handles diacritics and punctuation without treating input as markup', () => {
  assert.equal(matchesAward({ search: 'El Niño — High Times' }, { q: 'nino high' }), true);
  assert.equal(matchesAward(row, { q: '<script>missing</script>' }), false);
  assert.equal(matchesAward(row, {}), true);
});
