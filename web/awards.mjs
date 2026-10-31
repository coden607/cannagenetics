import { matchesAward } from './awards-search.mjs';

const form = document.getElementById('award-filters');
const rows = [...document.querySelectorAll('[data-award-row]')];
const keys = ['q', 'competition', 'year', 'country', 'evidence', 'contributor'];
const params = new URLSearchParams(location.search);
for (const key of keys) {
  const field = form.elements.namedItem(key);
  if (params.has(key)) field.value = params.get(key);
}
function render() {
  const filters = Object.fromEntries(keys.map(key => [key, form.elements.namedItem(key).value]));
  let count = 0;
  for (const row of rows) {
    row.hidden = !matchesAward(row.dataset, filters);
    if (!row.hidden) count++;
  }
  document.getElementById('award-count').textContent = `${count} of ${rows.length} records`;
  document.getElementById('award-empty').hidden = count !== 0;
  const query = new URLSearchParams(Object.entries(filters).filter(([, value]) => value));
  history.replaceState(null, '', `${location.pathname}${query.size ? '?' + query : ''}${location.hash}`);
}
form.addEventListener('input', render);
form.addEventListener('submit', event => { event.preventDefault(); render(); });
form.addEventListener('reset', () => setTimeout(render, 0));
render();
