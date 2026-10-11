#!/usr/bin/env python3
"""Rebuild the CannaGenetics catalog with lineage, compounds, and provenance."""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "web"
VENDOR_DATA = Path(__file__).resolve().parent.parent / "vendor" / "seedbank-index" / "data"


def _load(path, fallback):
    """Load JSON if present, else return fallback. The aux files
    (popular/colors/suppliers/traits/flavors/seedforms) were never
    committed; empty fallbacks keep the build reproducible."""
    return json.loads(path.read_text()) if path.exists() else fallback


STRAINS = json.loads((VENDOR_DATA / "strains.json").read_text())
EXTRA = _load(ROOT / "data" / "popular.json", [])
COLORS = _load(ROOT / "data" / "colors.json", {})
have = {s["slug"] for s in STRAINS}
STRAINS.extend([s for s in EXTRA if s["slug"] not in have])
for s in STRAINS:
    s["color"] = s.get("color") or COLORS.get(s["slug"], "green")
    s["ruderalis"] = s.get("ruderalis", s.get("type") == "autoflower")

BANKS = json.loads((VENDOR_DATA / "seedbanks.json").read_text())
COMPOUNDS = json.loads((VENDOR_DATA / "compounds.json").read_text())
SOURCES = json.loads((VENDOR_DATA / "sources.json").read_text())
PHENO = json.loads((VENDOR_DATA / "pheno_reports.json").read_text())
BANK = {b["slug"]: b for b in BANKS}
TRAITS = _load(ROOT / "data" / "traits.json", {})
FLAVORS = _load(ROOT / "data" / "flavors.json", {})
SEEDFORMS = _load(ROOT / "data" / "seedforms.json", {})

ALIASES = {
    "gg4": "gorilla-glue-4",
    "gorilla glue": "gorilla-glue-4",
    "gsc": "girl-scout-cookies",
    "cookies": "girl-scout-cookies",
    "nl": "northern-lights-5",
    "northern lights": "northern-lights-5",
    "gdp": "granddaddy-purple",
    "og": "og-kush",
    "widow": "white-widow",
}

def e(value):
    return html.escape("" if value is None else str(value))

def slugify(name):
    name = re.sub(r"\s*\(.*?\)", "", name).strip().lower()
    name = name.replace("#", "").replace("'", "")
    name = re.sub(r"[^a-z0-9]+", "-", name).strip("-")
    return name

BY_SLUG = {s["slug"]: s for s in STRAINS}
BY_NAME = {s["name"].lower(): s for s in STRAINS}
for s in STRAINS:
    BY_NAME.setdefault(slugify(s["name"]), s)

def match_parent(label):
    key = re.sub(r"\s*\(.*?\)", "", label).strip().lower()
    if key in BY_NAME:
        return BY_NAME[key]
    for s in STRAINS:
        if s["name"].lower() in key or key in s["name"].lower():
            return s
    return None

CHILDREN = {s["slug"]: [] for s in STRAINS}
for s in STRAINS:
    for parent in s.get("lineage_parents") or []:
        hit = match_parent(parent)
        if hit and hit["slug"] != s["slug"]:
            CHILDREN[hit["slug"]].append(s)

def related(strain):
    terps = set(strain.get("dominant_terpenes") or [])
    out = []
    for other in STRAINS:
        if other["slug"] == strain["slug"]:
            continue
        share = terps & set(other.get("dominant_terpenes") or [])
        if share:
            out.append((len(share), other))
    out.sort(key=lambda x: (-x[0], x[1]["name"]))
    return [item[1] for item in out[:4]]

CSS = """
:root {
  --ink:#e8f6ee; --paper:#070b09; --moss:#9dffc3; --leaf:#5ee0a0; --gold:#f0c36a;
  --line:rgba(157,255,195,.18); --muted:#9bb3a6; --card:rgba(16,28,22,.72);
  --glow:0 0 40px rgba(94,224,160,.18);
}
* { box-sizing:border-box; }
html,body { margin:0; min-height:100%; color:var(--ink); font-family:Outfit,system-ui,sans-serif;
  background:
    radial-gradient(900px 500px at 15% -10%, rgba(94,224,160,.16), transparent 55%),
    radial-gradient(700px 400px at 90% 0%, rgba(240,195,106,.10), transparent 50%),
    linear-gradient(180deg, #0b1210, #070b09 40%, #050807);
}
body::before { content:""; position:fixed; inset:0; pointer-events:none; z-index:0;
  background-image: linear-gradient(rgba(157,255,195,.05) 1px, transparent 1px), linear-gradient(90deg, rgba(157,255,195,.05) 1px, transparent 1px);
  background-size:48px 48px; mask-image:radial-gradient(circle at 50% 20%, #000 20%, transparent 75%); }
a { color:var(--moss); }
header,main,footer,nav.wrap { width:min(1120px,calc(100% - 28px)); margin:0 auto; position:relative; z-index:1; }
nav.wrap { position:sticky; top:0; z-index:6; display:flex; gap:12px; align-items:center; padding:14px 0; flex-wrap:wrap; font-size:14px;
  background:rgba(7,11,9,.78); backdrop-filter:blur(16px); border-bottom:1px solid var(--line); }
nav.wrap strong { font-family:Fraunces,serif; font-size:20px; margin-right:8px; color:#fff; text-shadow:0 0 18px rgba(94,224,160,.45); }
h1 { font-family:Fraunces,serif; font-weight:520; font-size:clamp(36px,6vw,68px); line-height:.92; margin:8px 0 12px; letter-spacing:-.03em;
  background:linear-gradient(120deg,#fff,#9dffc3 45%,#f0c36a); -webkit-background-clip:text; background-clip:text; color:transparent; }
h2,h3 { font-family:Fraunces,serif; font-weight:520; color:#f4fff8; }
.kicker { letter-spacing:.2em; text-transform:uppercase; font-size:12px; color:var(--leaf); font-weight:700; }
.lede,.meta { color:var(--muted); line-height:1.5; }
.stats { display:flex; gap:18px; flex-wrap:wrap; font-weight:700; color:var(--moss); }
.bar { display:flex; gap:8px; flex-wrap:wrap; margin:16px 0; }
input,select { border:1px solid var(--line); background:rgba(8,14,12,.8); color:var(--ink); border-radius:14px; padding:12px 14px; font:inherit; }
input[type=search] { flex:1; min-width:220px; }
button,.chip { font:inherit; border:1px solid var(--line); background:rgba(16,28,22,.6); color:var(--ink); border-radius:999px; padding:8px 14px; cursor:pointer; text-decoration:none; }
.chip.on, button.primary { background:linear-gradient(180deg,#1f6b45,#143c28); color:#fff; border-color:#5ee0a0; box-shadow:var(--glow); }
.grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(250px,1fr)); gap:14px; }
article,.card { background:var(--card); border:1px solid var(--line); border-radius:18px; padding:16px; box-shadow:var(--glow); backdrop-filter:blur(10px);
  transition:transform .2s ease, border-color .2s ease; }
article:hover,.card:hover { transform:translateY(-3px); border-color:rgba(157,255,195,.45); }
.tag { display:inline-block; background:rgba(94,224,160,.12); color:var(--moss); border:1px solid var(--line); border-radius:999px; padding:3px 9px; font-size:12px; font-weight:700; }
.warn { background:rgba(240,195,106,.08); border:1px solid rgba(240,195,106,.35); border-radius:14px; padding:12px 14px; color:#f3ddb0; font-size:14px; }
.tree { display:flex; gap:10px; flex-wrap:wrap; align-items:center; }
.tree .node { background:rgba(8,14,12,.7); border:1px solid var(--line); border-radius:12px; padding:8px 10px; }
.gate { position:fixed; inset:0; background:#050807; color:#efe8d8; display:flex; align-items:center; justify-content:center; z-index:20; padding:24px; }
.gate[hidden] { display:none; }
.gate .card { max-width:480px; background:rgba(12,22,18,.9); border:1px solid rgba(157,255,195,.3); }
.gate h1 { font-size:42px; }
.gate p { color:#c9c2b3; }
.gate button { background:linear-gradient(180deg,#f0c36a,#b8893a); color:#1a1408; border:0; font-weight:700; }
footer { padding:32px 0 56px; color:var(--muted); font-size:13px; position:relative; z-index:1; }
#field { position:fixed; inset:0; z-index:0; pointer-events:none; }
article,.card { transform-style:preserve-3d; }
.hero-img { width:min(420px,100%); border-radius:18px; border:1px solid var(--line); margin:12px 0; }
.thumb { width:100%; height:160px; object-fit:cover; border-radius:12px; margin-bottom:10px; }
table { width:100%; border-collapse:collapse; background:rgba(16,28,22,.6); border-radius:14px; overflow:hidden; }
th,td { text-align:left; padding:10px 12px; border-bottom:1px solid var(--line); vertical-align:top; }
"""

GATE = """
<div class="gate" id="gate">
  <div class="card">
    <p class="kicker">CannaGenetics</p>
    <h1>18+ only.</h1>
    <p>Informational genetics catalog. No sales, no checkout, no shipping, no grow guide. Enter only if you are of legal age where you live.</p>
    <label>Where are you?<br><select id="jurisdiction">
      <option value="">Choose</option>
      <option value="ca">Canada</option>
      <option value="de">Germany</option>
      <option value="nl">Netherlands</option>
      <option value="es">Spain</option>
      <option value="uk">United Kingdom</option>
      <option value="us">United States</option>
      <option value="other">Somewhere else / not sure</option>
    </select></label>
    <p class="meta">This filter is not legal advice. Restricted selections hide supplier links.</p>
    <button id="enter" type="button">Enter catalog</button>
  </div>
</div>
<script>
const OPEN = new Set(["ca","de","nl","es","uk","us"]);
const gate = document.getElementById("gate");
if (localStorage.getItem("cg-ok") === "1" && localStorage.getItem("cg-jur")) gate.hidden = true;
document.getElementById("enter").onclick = () => {
  const j = document.getElementById("jurisdiction").value;
  if (!j) return;
  localStorage.setItem("cg-jur", j);
  localStorage.setItem("cg-ok", "1");
  if (!OPEN.has(j)) {
    document.body.innerHTML = "<main><h1>Nothing listed.</h1><p>Your selection is outside the launch set. Supplier links stay hidden. This is not legal advice.</p></main>";
    return;
  }
  gate.hidden = true;
};
</script>
"""

NAV = """<nav class="wrap"><strong>CannaGenetics</strong>
<a href="/">Catalog</a>
<a href="/lineage.html">Lineage</a>
<a href="/compounds/index.html">Compounds</a>
<a href="/compare.html">Compare</a>
<a href="/cross.html">Cross</a>
<a href="/search.html">Search</a>
<a href="/rank.html">Rank</a>
<a href="/cups.html">Cups</a>
<a href="/geo.html">Places</a>
<a href="/gallery.html">Gallery</a>
<a href="/saved.html">Saved</a>
<a href="/families.html">Families</a>
<a href="/glossary.html">Glossary</a>
<a href="/about.html">About</a>
<a href="/feminized.html">Feminized</a>
<a href="/suppliers/index.html">Banks</a>
<a href="/provenance.html">Provenance</a>
<a href="https://github.com/coden607/cannagenetics">GitHub</a>
</nav>"""

def img_for(s):
    if s.get("color") == "purple":
        return "/img/purple.jpg"
    if s.get("type") == "sativa":
        return "/img/sativa.jpg"
    if s.get("type") in ("autoflower", "ruderalis"):
        return "/img/auto.jpg"
    if s.get("type") == "indica":
        return "/img/indica.jpg"
    return "/img/hybrid.jpg"

def page(title, body, extra=""):
    return f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="Informational cannabis genetics catalog. Lineage, banks, compounds. Link-out only. Not a store.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,520&family=Outfit:wght@400;600&display=swap" rel="stylesheet">
<link rel="icon" href="/favicon.svg">
<link rel="stylesheet" href="/styles.css">
<canvas id="field" aria-hidden="true"></canvas>
<script src="/fx.js"></script>
<script src="/save.js"></script>
</head><body>
{GATE}{NAV}{body}
<footer>Informational only. No medical claims. No checkout. Reported figures, not lab results. Know your local law. Data: coden607/cannagenetics and coden607/seedbank-index.</footer>
{extra}</body></html>"""

def write(path, content):
    dest = ROOT / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content)

write("styles.css", CSS)

# index
cards = []
for s in STRAINS:
    terps = ",".join(s.get("dominant_terpenes") or [])
    cards.append(f"""<article data-type="{e(s['type'])}" data-color="{e(s.get('color','green'))}" data-forms="{e(' '.join(SEEDFORMS.get(s['slug'], [])))}" data-name="{e(s['name'].lower())}" data-terps="{e(terps.lower())}">
<img class="thumb" src="{img_for(s)}" alt="">
<span class="tag">{e(s['type'])}</span>
<h2><a href="/cultivars/{e(s['slug'])}.html">{e(s['name'])}</a></h2>
<p class="meta">{e(s['origin'])}</p>
<p class="meta">Reported THC {s['typical_thc_pct'][0]}–{s['typical_thc_pct'][1]}% · {e(', '.join(s.get('dominant_terpenes') or [])[:80])}</p>
</article>""")
landraces = [s for s in STRAINS if not s.get("lineage_parents")]
index = page("CannaGenetics — worldwide genetics catalog", f"""
<header>
<p class="kicker">Worldwide genetics</p>
<h1>Your cannabis seed and clone hub.</h1>
<p class="lede">Lineage, banks, and chemotype notes in one catalog. You compare. You leave to the supplier. We do not sell.</p>
<p class="stats"><span>{len(STRAINS)} cultivars</span><span>{len(BANKS)} banks</span><span>{len(COMPOUNDS)} compounds</span><span>{len(landraces)} landraces</span></p>
</header>
<main>
<p class="warn">Seed-v0 catalog. Every figure is reported, not a lab result. Prices and clone sales stay off.</p>
<div class="bar">
<input id="q" type="search" placeholder="Search cultivars, nicknames, terpenes">
<button class="chip on" data-type="all" type="button">all</button>
<button class="chip" data-type="indica" type="button">indica</button>
<button class="chip" data-type="sativa" type="button">sativa</button>
<button class="chip" data-type="hybrid" type="button">hybrid</button>
<button class="chip" data-type="autoflower" type="button">autoflower</button>
<button class="chip" data-type="ruderalis" type="button">ruderalis</button>
<button class="chip" data-type="purple" type="button">purple</button>
<button class="chip" data-type="feminized" type="button">feminized</button>
</div>
<div class="grid" id="grid">{''.join(cards)}</div>
<h2>Start with the landraces</h2>
<div class="grid">{''.join(f"<article><h3><a href='/cultivars/{e(s['slug'])}.html'>{e(s['name'])}</a></h3><p class='meta'>{e(s['origin'])}</p></article>" for s in landraces)}</div>
</main>
""", f"""<script>
const ALIAS = {json.dumps(ALIASES)};
let type = "all";
const q = document.getElementById("q");
function render() {{
  let query = q.value.trim().toLowerCase();
  if (ALIAS[query]) query = ALIAS[query].replaceAll("-", " ");
  document.querySelectorAll("#grid article").forEach(el => {{
    const blob = el.dataset.name + " " + el.dataset.terps;
    const ok = (type === "all" || el.dataset.type === type || el.dataset.color === type || (el.dataset.forms || "").includes(type)) && (!query || blob.includes(query));
    el.style.display = ok ? "" : "none";
  }});
}}
q.oninput = render;
document.querySelectorAll("[data-type]").forEach(btn => btn.onclick = () => {{
  type = btn.dataset.type;
  document.querySelectorAll("[data-type]").forEach(b => b.classList.toggle("on", b === btn));
  render();
}});
</script>""")
write("index.html", index)

# cultivars
for s in STRAINS:
    parents = []
    for label in s.get("lineage_parents") or []:
        hit = match_parent(label)
        parents.append(f"<a class='node' href='/cultivars/{e(hit['slug'])}.html'>{e(hit['name'])}</a>" if hit else f"<span class='node'>{e(label)}</span>")
    kids = CHILDREN.get(s["slug"], [])
    kid_html = "".join(f"<a class='node' href='/cultivars/{e(k['slug'])}.html'>{e(k['name'])}</a>" for k in kids) or "<span class='node'>none catalogued</span>"
    links = []
    for slug in s.get("available_at_seedbanks", []):
        bank = BANK.get(slug)
        if bank:
            links.append(f"<li><a href='/suppliers/{e(slug)}.html'>{e(bank['name'])}</a> · <a href='{e(bank['source'])}' rel='noopener noreferrer'>their photo</a> · {e(bank.get('region',''))}</li>")
    rel = "".join(f"<li><a href='/cultivars/{e(o['slug'])}.html'>{e(o['name'])}</a> · {e(', '.join(set(s.get('dominant_terpenes') or []) & set(o.get('dominant_terpenes') or [])))}</li>" for o in related(s))
    awards = "".join(f"<li>{e(a)}</li>" for a in s.get("awards") or []) or "<li>None recorded.</li>"
    terp_links = []
    for name in s.get("dominant_terpenes") or []:
        hit = next((c for c in COMPOUNDS if c["name"].lower() == name.lower()), None)
        terp_links.append(f"<a href='/compounds/{e(slugify(hit['name']))}.html'>{e(name)}</a>" if hit else e(name))
    body = f"""<main>
<p class="kicker">{e(s['type'])} · {e(s.get('verify_status','seed-v0'))}</p>
<h1>{e(s['name'])}</h1>
<p class="lede">{e(s['origin'])}</p>
<img class="hero-img" src="{img_for(s)}" alt="Illustration of {e(s['name'])}, not a seed-bank photo">
<p class="meta">Original illustration by type and color. Each bank's own photo is on their site.</p>
<div class="card">
<p><strong>Lineage claim:</strong> {e(' × '.join(s.get('lineage_parents') or []) or 'landrace / unknown')}</p>
<p><strong>Breeders known:</strong> {e(', '.join(s.get('breeders_known') or []))}</p>
<p><strong>Reported THC:</strong> {s['typical_thc_pct'][0]}–{s['typical_thc_pct'][1]}%. Not a lab result.</p>
<p><strong>Dominant terpenes:</strong> {', '.join(terp_links) or '—'}</p>
<p><strong>Reported CBD:</strong> {TRAITS.get(s['slug'],{}).get('cbd',['—','—'])[0]}–{TRAITS.get(s['slug'],{}).get('cbd',['—','—'])[1]}%</p>
<p><strong>Reported flower:</strong> {TRAITS.get(s['slug'],{}).get('flower',['—','—'])[0]}–{TRAITS.get(s['slug'],{}).get('flower',['—','—'])[1]} weeks</p>
<p><strong>Typical veg:</strong> {('included in the auto cycle' if TRAITS.get(s['slug'],{}).get('veg')==[0,0] else str(TRAITS.get(s['slug'],{}).get('veg',['—','—'])[0])+'–'+str(TRAITS.get(s['slug'],{}).get('veg',['—','—'])[1])+' weeks, grower-set')}</p>
<p><strong>Reported indoor yield:</strong> {TRAITS.get(s['slug'],{}).get('yield',['—','—'])[0]}–{TRAITS.get(s['slug'],{}).get('yield',['—','—'])[1]} g/m²</p>
<p><strong>Reported color:</strong> {s.get("color","green")}</p>
<p><strong>Reported flavor:</strong> {FLAVORS.get(s["slug"], "not recorded")}</p>
<p><strong>Seed forms commonly listed:</strong> {", ".join(SEEDFORMS.get(s["slug"], ["not recorded"]))}</p>
<p><button type="button" class="chip" onclick="saveStrain('{e(s['slug'])}','{e(s['name'])}')">Save</button></p>
<p><strong>Difficulty / height / climate:</strong> {TRAITS.get(s['slug'],{}).get('difficulty','—')} · {TRAITS.get(s['slug'],{}).get('height','—')} · {TRAITS.get(s['slug'],{}).get('climate','—')}</p>
<p class="meta">Trait figures are commonly reported catalog ranges, not lab results, and vary by phenotype and conditions.</p>
</div>
<h2>Family</h2>
<p class="meta">Parents</p><div class="tree">{''.join(parents) or '<span class="node">landrace / unknown</span>'}</div>
<p class="meta">Catalogued descendants</p><div class="tree">{kid_html}</div>
<h2>Carried at</h2><ul>{''.join(links) or '<li>No sourced bank yet.</li>'}</ul>
<h2>Related by terpene</h2><ul>{rel or '<li>None yet.</li>'}</ul>
<h2>Awards</h2><ul>{awards}</ul>
<p><a href="/compare.html#{e(s['slug'])}">Open comparison</a> · <a href="/lineage.html">Full lineage explorer</a></p>
</main>"""
    write(f"cultivars/{s['slug']}.html", page(s["name"], body))

# compounds
compound_cards = []
for c in COMPOUNDS:
    compound_cards.append(f"""<article><span class="tag">{e(c.get('cls'))}</span><h2><a href="/compounds/{e(slugify(c['name']))}.html">{e(c['name'])}</a></h2><p class="meta">{e(c.get('aroma',''))}</p></article>""")
write("compounds/index.html", page("Compounds", f"<main><h1>Compounds</h1><p class='lede'>Cannabinoids, terpenes, flavonoids. Community-reported notes only. Not medical claims.</p><div class='grid'>{''.join(compound_cards)}</div></main>"))
for c in COMPOUNDS:
    used = [s for s in STRAINS if c["name"] in (s.get("dominant_terpenes") or [])]
    used_html = "".join(f"<li><a href='/cultivars/{e(s['slug'])}.html'>{e(s['name'])}</a></li>" for s in used) or "<li>Not marked dominant on a catalogued cultivar.</li>"
    body = f"""<main>
<p class="kicker">{e(c.get('cls'))}</p>
<h1>{e(c['name'])}</h1>
<p class="lede">{e(', '.join(c.get('alt_names') or []))}</p>
<div class="card">
<p>Formula: {e(c.get('formula') or '—')}</p>
<p>Cited vapor temperature: {e(c.get('vapor_temp_c') or '—')} C</p>
<p>Aroma: {e(c.get('aroma') or '—')}</p>
<p>{e(c.get('notes') or '')}</p>
<p class="warn">{e(c.get('reported_effects') or 'No effect language recorded.')} Not a medical claim.</p>
</div>
<h2>Cultivars where this is listed dominant</h2><ul>{used_html}</ul>
</main>"""
    write(f"compounds/{slugify(c['name'])}.html", page(c["name"], body))

# lineage explorer
rows = []
for s in STRAINS:
    parents = " × ".join(s.get("lineage_parents") or []) or "landrace"
    kids = ", ".join(k["name"] for k in CHILDREN.get(s["slug"], [])) or "—"
    rows.append(f"<tr><td><a href='/cultivars/{e(s['slug'])}.html'>{e(s['name'])}</a></td><td>{e(parents)}</td><td>{e(kids)}</td></tr>")
write("lineage.html", page("Lineage", f"""<main><h1>Lineage explorer</h1>
<p class="lede">Parents are claims. Descendants are only the cultivars already in this catalog.</p>
<table><thead><tr><th>Cultivar</th><th>Claimed parents</th><th>Catalogued descendants</th></tr></thead><tbody>{''.join(rows)}</tbody></table></main>"""))

# provenance
tiers = "".join(f"<article><span class='tag'>tier {t['rank']}</span><h2>{e(t['label'])}</h2><p>{e(t['definition'])}</p><p class='meta'>{e(t.get('example_use',''))}</p></article>" for t in SOURCES.get("trust_tiers", []))
srcs = "".join(f"<li>{e(s.get('name') or s.get('id') or s)}</li>" for s in SOURCES.get("sources", [])[:20])
write("provenance.html", page("Provenance", f"""<main><h1>Provenance</h1>
<p class="lede">{e(SOURCES.get('description',''))}</p>
<div class="grid">{tiers}</div>
<h2>Registered sources</h2><ul>{srcs}</ul>
<p class="warn">Higher tier wins on conflict. A lab COA overrides a breeder claim. This catalog is still seed-v0.</p>
</main>"""))

# suppliers
bank_cards = []
for b in BANKS:
    bank_cards.append("<article data-region='%s'><span class='tag'>%s</span><h2><a href='/suppliers/%s.html'>%s</a></h2><p class='meta'>%s · %s</p></article>" % (e(b["region"].split(" (")[0]), e(b["type"]), e(b["slug"]), e(b["name"]), e(b["region"]), e(b.get("ships_to",""))))
regions = sorted({b["region"].split(" (")[0] for b in BANKS})
region_buttons = "".join("<button class='chip' data-region='%s' type='button'>%s</button>" % (e(r), e(r)) for r in regions)
write("suppliers/index.html", page("Seed banks", """<main><h1>Seed banks and breeders</h1>
<p class='lede'>%d major suppliers across %d regions. Official sites only. Seed-v0, not a complete census of every small breeder.</p>
<div class='bar'><button class='chip on' data-region='all' type='button'>all</button>%s</div>
<div class='grid' id='banks'>%s</div></main>
<script>
let region = "all";
document.querySelectorAll("[data-region]").forEach(btn => btn.onclick = () => {
  region = btn.dataset.region;
  document.querySelectorAll("[data-region]").forEach(b => b.classList.toggle("on", b === btn));
  document.querySelectorAll("#banks article").forEach(el => {
    el.style.display = (region === "all" || el.dataset.region === region) ? "" : "none";
  });
});
</script>""" % (len(BANKS), len(regions), region_buttons, "".join(bank_cards))))
for b in BANKS:
    carried = [s for s in STRAINS if b["slug"] in s.get("available_at_seedbanks", [])]
    items = "".join(f"<li><a href='/cultivars/{e(s['slug'])}.html'>{e(s['name'])}</a></li>" for s in carried) or "<li>No catalogued cultivars yet.</li>"
    write(f"suppliers/{b['slug']}.html", page(b["name"], f"""<main>
<p class="kicker">{e(b['type'])}</p><h1>{e(b['name'])}</h1>
<p class="lede">{e(b['region'])} · ships: {e(b.get('ships_to',''))}</p>
<div class="card"><p>{e(b.get('specialty',''))}</p><p>Notable lines: {e(', '.join(b.get('notable_lines') or []))}</p><p>Checked {e(b.get('last_checked',''))} · {e(b.get('verify_status',''))}</p><p><a href="{e(b['source'])}" rel="noopener noreferrer">Official site</a></p></div>
<h2>In this catalog</h2><ul>{items}</ul></main>"""))

# compare
compare = []
for s in STRAINS:
    names = []
    for slug in s.get("available_at_seedbanks", []):
        bank = BANK.get(slug)
        if bank:
            names.append(f"<a href='/suppliers/{e(slug)}.html'>{e(bank['name'])}</a>")
    compare.append(f"<article id='{e(s['slug'])}'><h2><a href='/cultivars/{e(s['slug'])}.html'>{e(s['name'])}</a></h2><p class='meta'>{' · '.join(names) or 'No banks yet'}</p><p class='meta'>Prices stay off until each supplier's terms allow them.</p></article>")
write("compare.html", page("Compare", f"<main><h1>Compare</h1><p class='lede'>Same cultivar, every catalogued bank. Link-out only.</p><div class='grid'>{''.join(compare)}</div></main>"))

write("clones.html", page("Clones", """<main><h1>Clones</h1>
<p class="warn">Clone listings are off. Nurseries are named from the supplier registry and are not for sale here.</p>
<div class="grid">
<article><h2>Dark Heart Nursery</h2><p class="meta">California. Named only.</p></article>
<article><h2>Kind Roots Nursery</h2><p class="meta">Colorado. Named only.</p></article>
</div></main>"""))


payload = []
for s in STRAINS:
    payload.append({
        "name": s["name"],
        "slug": s["slug"],
        "type": s["type"],
        "parents": s.get("lineage_parents") or [],
        "origin": s.get("origin") or "",
        "thc": s.get("typical_thc_pct") or [0, 0],
        "terpenes": s.get("dominant_terpenes") or [],
        "breeders": s.get("breeders_known") or [],
    })
cross_js = json.dumps(payload)
write("cross.html", page("Cross calculator", """
<main>
<p class="kicker">Genetics model</p>
<h1>Cross two cultivars.</h1>
<p class="lede">Pick two parents. The tool estimates the offspring from the catalog records and finds any known cultivar that already claims that pair. This is a model, not a lab result.</p>
<div class="grid">
<article>
<label>Parent A<br><select id="a"></select></label>
</article>
<article>
<label>Parent B<br><select id="b"></select></label>
</article>
</div>
<p><button id="go" class="chip on" type="button">Predict offspring</button></p>
<div id="out"></div>
<p class="warn">Cannabis traits are polygenic. A real cross can throw phenotypes neither parent shows. Autoflower and sex are not guaranteed by this model. No grow instructions.</p>
</main>
""", """<script>
const STRAINS = %s;
const a = document.getElementById("a");
const b = document.getElementById("b");
const out = document.getElementById("out");
function fill(sel) {
  sel.innerHTML = STRAINS.map(s => `<option value="${s.slug}">${s.name}</option>`).join("");
}
fill(a); fill(b);
b.selectedIndex = 1;
function norm(s){ return s.toLowerCase().replace(/\\s*\\(.*?\\)/g,"").trim(); }
function claims(child, parent){
  return (child.parents || []).some(p => norm(p).includes(norm(parent.name)) || norm(parent.name).includes(norm(p)));
}
function predict(){
  const A = STRAINS.find(s => s.slug === a.value);
  const B = STRAINS.find(s => s.slug === b.value);
  if (!A || !B || A.slug === B.slug) { out.innerHTML = "<p>Pick two different parents.</p>"; return; }
  const types = new Set([A.type, B.type]);
  const type = types.size === 1 ? A.type : "hybrid";
  const auto = [A.type, B.type].includes("autoflower");
  const lo = Math.min(A.thc[0], B.thc[0]);
  const hi = Math.max(A.thc[1], B.thc[1]);
  const mid = Math.round(((A.thc[0]+A.thc[1]+B.thc[0]+B.thc[1]) / 4) * 10) / 10;
  const shared = A.terpenes.filter(t => B.terpenes.includes(t));
  const all = [...new Set([...A.terpenes, ...B.terpenes])];
  const known = STRAINS.filter(s => s.slug !== A.slug && s.slug !== B.slug && claims(s, A) && claims(s, B));
  const knownHtml = known.length
    ? known.map(s => `<li><a href="/cultivars/${s.slug}.html">${s.name}</a> claims this pair.</li>`).join("")
    : "<li>No catalogued cultivar claims both parents.</li>";
  out.innerHTML = `
    <article>
      <p class="kicker">Predicted F1</p>
      <h2>${A.name} × ${B.name}</h2>
      <p>Likely type: <strong>${type}</strong>${auto ? " · autoflower possible if the auto parent passes ruderalis" : ""}</p>
      <p>Reported THC span: ${lo}–${hi}%% · midpoint about ${mid}%%</p>
      <p>Shared terpenes: ${shared.join(", ") || "none recorded"}</p>
      <p>Combined terpene set: ${all.join(", ") || "—"}</p>
      <p class="meta">${A.name}: ${A.type}, ${A.origin}</p>
      <p class="meta">${B.name}: ${B.type}, ${B.origin}</p>
    </article>
    <h2>Already in the catalog</h2>
    <ul>${knownHtml}</ul>
    <p><a href="/cultivars/${A.slug}.html">${A.name}</a> · <a href="/cultivars/${B.slug}.html">${B.name}</a></p>
  `;
}
document.getElementById("go").onclick = predict;
predict();
</script>""" % cross_js))


search_items = []
for s in STRAINS:
    search_items.append({"kind":"cultivar","name":s["name"],"href":"/cultivars/%s.html" % s["slug"],"blurb":s["type"] + " · " + s["origin"]})
for b in BANKS:
    search_items.append({"kind":"supplier","name":b["name"],"href":"/suppliers/%s.html" % b["slug"],"blurb":b["type"] + " · " + b["region"]})
for c in COMPOUNDS:
    search_items.append({"kind":"compound","name":c["name"],"href":"/compounds/%s.html" % slugify(c["name"]),"blurb":c.get("cls","") + " · " + (c.get("aroma") or "")})
write("search.html", page("Search", """
<main>
<p class="kicker">Catalog</p>
<h1>Search everything.</h1>
<p class="lede">Cultivars, banks, and compounds. Nicknames work: GG4, GSC, NL, GDP.</p>
<input id="q" type="search" placeholder="Search the catalog">
<div class="grid" id="hits"></div>
</main>
""", """<script>
const ITEMS = %s;
const ALIAS = {"gg4":"gorilla glue","gsc":"girl scout cookies","nl":"northern lights","gdp":"granddaddy purple","og":"og kush","widow":"white widow"};
const q = document.getElementById("q");
const hits = document.getElementById("hits");
function render(){
  let query = q.value.trim().toLowerCase();
  if (ALIAS[query]) query = ALIAS[query];
  const found = ITEMS.filter(i => !query || (i.name + " " + i.blurb).toLowerCase().includes(query)).slice(0, 60);
  hits.innerHTML = found.map(i => `<article><span class="tag">${i.kind}</span><h2><a href="${i.href}">${i.name}</a></h2><p class="meta">${i.blurb}</p></article>`).join("") || "<p>Nothing matched.</p>";
}
q.oninput = render;
render();
</script>""" % json.dumps(search_items)))
write("favicon.svg", "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'><rect width='64' height='64' rx='16' fill='#07110d'/><path d='M32 8c9 9 12 18 9 28-7-2-12-9-9-28zm0 0c-9 9-12 18-9 28 7-2 12-9 9-28z' fill='#5ee0a0'/><circle cx='32' cy='40' r='3' fill='#f0c36a'/></svg>")


rows = []
for s in STRAINS:
    t = TRAITS.get(s["slug"], {})
    cbd = t.get("cbd", [0, 0])
    flower = t.get("flower", [0, 0])
    veg = t.get("veg", [0, 0])
    yld = t.get("yield", [0, 0])
    rows.append({
        "name": s["name"], "slug": s["slug"], "type": s["type"],
        "thc_lo": s["typical_thc_pct"][0], "thc_hi": s["typical_thc_pct"][1],
        "mid": round(sum(s["typical_thc_pct"]) / 2, 1),
        "cbd_hi": cbd[1], "cbd": "%s–%s" % (cbd[0], cbd[1]),
        "flower_lo": flower[0], "flower": "%s–%s wk" % (flower[0], flower[1]),
        "veg_lo": veg[0], "veg": "auto cycle" if veg == [0, 0] else "%s–%s wk" % (veg[0], veg[1]),
        "yield_hi": yld[1], "yield": "%s–%s" % (yld[0], yld[1]),
        "difficulty": t.get("difficulty", ""),
        "banks": len(s.get("available_at_seedbanks") or []),
    })
write("rank.html", page("Rankings", """
<main>
<p class="kicker">Sort the catalog</p>
<h1>Rank cultivars.</h1>
<p class="lede">Order by reported THC, CBD, flower time, veg time, yield, or how many banks carry it. These are commonly reported catalog ranges, not lab results.</p>
<div class="bar">
<button class="chip on" data-sort="thc" type="button">Highest THC</button>
<button class="chip" data-sort="thc-low" type="button">Lowest THC</button>
<button class="chip" data-sort="cbd" type="button">Highest CBD</button>
<button class="chip" data-sort="flower" type="button">Shortest flower</button>
<button class="chip" data-sort="veg" type="button">Shortest veg</button>
<button class="chip" data-sort="yield" type="button">Highest yield</button>
<button class="chip" data-sort="banks" type="button">Most banks</button>
<button class="chip" data-sort="name" type="button">Name</button>
</div>
<div style="overflow-x:auto"><table id="rank"><thead><tr><th>#</th><th>Cultivar</th><th>Type</th><th>THC</th><th>CBD</th><th>Flower</th><th>Veg</th><th>Yield g/m²</th><th>Difficulty</th><th>Banks</th></tr></thead><tbody></tbody></table></div>
</main>
""", """<script>
const ROWS = %s;
const body = document.querySelector("#rank tbody");
function draw(key){
  const list = ROWS.slice().sort((a,b) => {
    if (key === "thc") return b.thc_hi - a.thc_hi || b.mid - a.mid;
    if (key === "thc-low") return a.thc_lo - b.thc_lo;
    if (key === "cbd") return b.cbd_hi - a.cbd_hi;
    if (key === "flower") return a.flower_lo - b.flower_lo;
    if (key === "veg") return a.veg_lo - b.veg_lo;
    if (key === "yield") return b.yield_hi - a.yield_hi;
    if (key === "banks") return b.banks - a.banks;
    return a.name.localeCompare(b.name);
  });
  body.innerHTML = list.map((r,i) => `<tr><td>${i+1}</td><td><a href="/cultivars/${r.slug}.html">${r.name}</a></td><td>${r.type}</td><td>${r.thc_lo}–${r.thc_hi}%%</td><td>${r.cbd}%%</td><td>${r.flower}</td><td>${r.veg}</td><td>${r.yield}</td><td>${r.difficulty}</td><td>${r.banks}</td></tr>`).join("");
}
document.querySelectorAll("[data-sort]").forEach(btn => btn.onclick = () => {
  document.querySelectorAll("[data-sort]").forEach(b => b.classList.toggle("on", b === btn));
  draw(btn.dataset.sort);
});
draw("thc");
</script>""" % json.dumps(rows)))


# cups
cup_cards = []
for s in STRAINS:
    for award in s.get("awards") or []:
        cup_cards.append("<article><span class='tag'>reported</span><h2><a href='/cultivars/%s.html'>%s</a></h2><p>%s</p></article>" % (e(s["slug"]), e(s["name"]), e(award)))
local = [
    ("New York 2026", "Doobie Labs White Widow", "High Times Cannabis Cup, Best Sativa flower", "white-widow"),
    ("Oregon 2023", "Pruf Cultivar Jack Herer", "High Times Cannabis Cup, First Sativa flower", "jack-herer"),
    ("Montana 2026", "Sacred Sun Farms DJ Short Blueberry preroll", "High Times Cannabis Cup, preroll placing", "blueberry"),
]
local_html = "".join("<article><span class='tag'>%s</span><h2>%s</h2><p>%s</p><p class='meta'>A producer using the <a href='/cultivars/%s.html'>catalog name</a>. Not the original breeder.</p></article>" % (e(a), e(b), e(c), e(d)) for a,b,c,d in local)
write("cups.html", page("Cups", """<main>
<p class="kicker">Awards</p>
<h1>Cup winners.</h1>
<p class="lede">Historical wins tied to catalog cultivars, plus a few recent local cups where a producer entered that name. Reported, not a complete cup archive.</p>
<h2>Catalog cultivars</h2>
<div class="grid">%s</div>
<h2>Recent local cups</h2>
<div class="grid">%s</div>
</main>""" % ("".join(cup_cards), local_html)))

# geography
regions = {
    "Central Asia": ["afghani","hindu-kush"],
    "Southeast Asia": ["thai"],
    "Africa": ["durban-poison","malawi"],
    "Americas, landrace era": ["colombian-gold","acapulco-gold","panama-red"],
    "United States": ["northern-lights-5","haze","og-kush","sour-diesel","girl-scout-cookies","gelato","wedding-cake","gorilla-glue-4","zkittlez","runtz","purple-punch","chemdawg","granddaddy-purple","blueberry"],
    "Netherlands": ["skunk-1","white-widow","jack-herer","ak-47","amnesia-haze"],
    "Canada / auto": ["lowryder"],
}
geo_cards = []
for region, slugs in regions.items():
    links = "".join("<li><a href='/cultivars/%s.html'>%s</a></li>" % (slug, BY_SLUG[slug]["name"]) for slug in slugs if slug in BY_SLUG)
    geo_cards.append("<article><h2>%s</h2><ul>%s</ul></article>" % (e(region), links))
write("geo.html", page("Places", """<main>
<p class="kicker">Geography</p>
<h1>Where the names come from.</h1>
<p class="lede">Origin of the cultivar, not where it is legal to buy. Banks stay filterable on the banks page.</p>
<div class="grid">%s</div>
<p><a href="/suppliers/index.html">Search banks by region</a></p>
</main>""" % "".join(geo_cards)))


cards = "".join("<article><img class='thumb' src='%s' alt=''><h2><a href='/cultivars/%s.html'>%s</a></h2><p class='meta'>%s · %s</p></article>" % (img_for(s), e(s["slug"]), e(s["name"]), e(s["type"]), e(s.get("color","green"))) for s in STRAINS)
write("gallery.html", page("Gallery", "<main><p class='kicker'>Illustrations</p><h1>Gallery.</h1><p class='lede'>Original illustrations by type and color. Official photos stay on each seed bank's site.</p><div class='grid'>%s</div></main>" % cards))


write("saved.html", page("Saved", """
<main>
<p class="kicker">Your list</p>
<h1>Saved cultivars.</h1>
<p class="lede">Stored in this browser only. Nothing is sent to a server.</p>
<div class="grid" id="saved"></div>
</main>
""", """<script>
function load(){ try { return JSON.parse(localStorage.getItem("cg-saved") || "[]"); } catch(e){ return []; } }
const box = document.getElementById("saved");
const items = load();
box.innerHTML = items.length ? items.map(s => `<article><h2><a href="/cultivars/${s.slug}.html">${s.name}</a></h2><button class="chip" data-slug="${s.slug}">Remove</button></article>`).join("") : "<p>Nothing saved yet. Use Save on a cultivar page.</p>";
box.onclick = ev => {
  if (!ev.target.dataset.slug) return;
  const next = load().filter(s => s.slug !== ev.target.dataset.slug);
  localStorage.setItem("cg-saved", JSON.stringify(next));
  location.reload();
};
</script>"""))
write("save.js", """function saveStrain(slug, name){
  const key = "cg-saved";
  const items = JSON.parse(localStorage.getItem(key) || "[]");
  if (!items.some(s => s.slug === slug)) items.push({slug, name});
  localStorage.setItem(key, JSON.stringify(items));
  alert(name + " saved");
}
(function(){
  const m = location.pathname.match(/\\/cultivars\\/([a-z0-9-]+)\\.html/);
  if (!m) return;
  const slug = m[1];
  const name = document.querySelector("h1") ? document.querySelector("h1").textContent : slug;
  const key = "cg-recent";
  const items = JSON.parse(localStorage.getItem(key) || "[]").filter(s => s.slug !== slug);
  items.unshift({slug, name});
  localStorage.setItem(key, JSON.stringify(items.slice(0, 8)));
})();
""")


families = {
    "Kush": ["afghani","hindu-kush","og-kush","bubba-kush"],
    "Haze": ["haze","amnesia-haze","super-lemon-haze","super-silver-haze","purple-haze","jack-herer"],
    "Cookies": ["girl-scout-cookies","gelato","gelato-41","wedding-cake","runtz","zkittlez"],
    "Diesel": ["sour-diesel","chemdawg"],
    "Skunk": ["skunk-1","cheese","critical"],
    "Landrace": ["afghani","hindu-kush","thai","durban-poison","malawi","colombian-gold","acapulco-gold","panama-red","maui-wowie","ruderalis"],
    "Autoflower": [s["slug"] for s in STRAINS if s["type"] in ("autoflower","ruderalis")],
}
fam_html = []
for name, slugs in families.items():
    links = "".join("<li><a href='/cultivars/%s.html'>%s</a></li>" % (slug, BY_SLUG[slug]["name"]) for slug in slugs if slug in BY_SLUG)
    fam_html.append("<article><h2>%s</h2><ul>%s</ul></article>" % (name, links))
write("families.html", page("Families", "<main><p class='kicker'>Lineage groups</p><h1>Families.</h1><p class='lede'>A cultivar can sit in more than one family. Claims, not proven pedigrees.</p><div class='grid'>%s</div></main>" % "".join(fam_html)))

glossary = [
    ("Indica","Broad-leaf drug type. A market label, not a species."),
    ("Sativa","Narrow-leaf drug type. A market label, not a species."),
    ("Hybrid","A cross of two market types."),
    ("Ruderalis","The autoflowering wild type. The trait is recessive."),
    ("Autoflower","A cultivar that flowers by age because it carries ruderalis."),
    ("Landrace","A regional population kept before modern breeding."),
    ("F1","The first generation of a cross. Not uniform unless the parents are stable."),
    ("THC / CBD","Reported ranges in this catalog, not a lab result for one plant."),
    ("Terpene","An aroma compound. Dominant terpenes here are reported, not assayed."),
    ("Feminized","Seed bred to produce female plants. A seed product, not a genetic type."),
    ("Clone","A cutting of one plant. Named only in this catalog."),
]
gloss = "".join("<article><h2>%s</h2><p>%s</p></article>" % (a,b) for a,b in glossary)
write("glossary.html", page("Glossary", "<main><p class='kicker'>Terms</p><h1>Glossary.</h1><div class='grid'>%s</div></main>" % gloss))

write("about.html", page("About", """<main>
<p class="kicker">Status</p>
<h1>What this is.</h1>
<p class="lede">An informational genetics catalog. You compare. You leave to the supplier. We do not sell, and we do not give grow instructions.</p>
<ul>
<li>54 cultivars, 73 banks, 35 compounds</li>
<li>Records are seed-v0: reported, not lab-verified</li>
<li>Prices and checkout stay off</li>
<li>Official bank photos stay on the bank site</li>
</ul>
<p><a href="/provenance.html">Provenance model</a></p>
</main>"""))


fem = [s for s in STRAINS if "feminized" in SEEDFORMS.get(s["slug"], [])]
fem_html = "".join("<article><span class='tag'>%s</span><h2><a href='/cultivars/%s.html'>%s</a></h2><p class='meta'>%s</p></article>" % (e(s["type"]), e(s["slug"]), e(s["name"]), e(", ".join(SEEDFORMS.get(s["slug"], [])))) for s in fem)
write("feminized.html", page("Feminized", "<main><p class='kicker'>Seed form</p><h1>Feminized.</h1><p class='lede'>Cultivars commonly listed as feminized seed. Availability is per bank. This is a seed product, not a genetic type.</p><div class='grid'>%s</div></main>" % fem_html))

urls = ["/", "/lineage.html", "/compare.html", "/cross.html", "/search.html", "/rank.html", "/cups.html", "/geo.html", "/gallery.html", "/saved.html", "/families.html", "/glossary.html", "/about.html", "/feminized.html", "/provenance.html", "/compounds/index.html", "/suppliers/index.html"]
urls += [f"/cultivars/{s['slug']}.html" for s in STRAINS]
urls += [f"/suppliers/{b['slug']}.html" for b in BANKS]
urls += [f"/compounds/{slugify(c['name'])}.html" for c in COMPOUNDS]
write("sitemap.xml", "<?xml version='1.0' encoding='UTF-8'?>\n<urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>\n" + "\n".join(f"<url><loc>https://cannagenetics.vercel.app{u}</loc></url>" for u in urls) + "\n</urlset>\n")
write("robots.txt", "User-agent: *\nAllow: /\nSitemap: https://cannagenetics.vercel.app/sitemap.xml\n")
print(f"built {len(STRAINS)} cultivars, {len(BANKS)} banks, {len(COMPOUNDS)} compounds")
