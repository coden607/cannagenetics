function saveStrain(slug, name){
  const key = "cg-saved";
  const items = JSON.parse(localStorage.getItem(key) || "[]");
  if (!items.some(s => s.slug === slug)) items.push({slug, name});
  localStorage.setItem(key, JSON.stringify(items));
  alert(name + " saved");
}
(function(){
  const m = location.pathname.match(/\/cultivars\/([a-z0-9-]+)\.html/);
  if (!m) return;
  const slug = m[1];
  const name = document.querySelector("h1") ? document.querySelector("h1").textContent : slug;
  const key = "cg-recent";
  const items = JSON.parse(localStorage.getItem(key) || "[]").filter(s => s.slug !== slug);
  items.unshift({slug, name});
  localStorage.setItem(key, JSON.stringify(items.slice(0, 8)));
})();
