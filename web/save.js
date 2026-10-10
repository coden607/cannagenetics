function saveStrain(slug, name){
  const key = "cg-saved";
  const items = JSON.parse(localStorage.getItem(key) || "[]");
  if (!items.some(s => s.slug === slug)) items.push({slug, name});
  localStorage.setItem(key, JSON.stringify(items));
  alert(name + " saved");
}
