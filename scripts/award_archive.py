"""Sourced award-history records and static research views; stdlib only."""
import html
import json
import re
from datetime import date
from urllib.parse import quote, urlsplit

EVIDENCE = {
    'organizer-record': 'Organizer record',
    'publisher-report': 'Publisher report',
    'participant-claim': 'Participant claim',
}


def esc(value):
    return html.escape(str(value), quote=True)


def https_url(value):
    if not isinstance(value, str):
        raise ValueError('Source URL required')
    parsed = urlsplit(value)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError('Expected public HTTPS source URL without credentials')


def validate_archive(data):
    if data.get('version') != 1 or not data.get('coverage'):
        raise ValueError('Archive version and coverage statement required')
    registries = {}
    for kind in ['competitions', 'contributors', 'awards']:
        records = data.get(kind)
        if not isinstance(records, list):
            raise ValueError(f'{kind} must be a list')
        registry = {}
        for record in records:
            key = record.get('id', '')
            if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', key) or key in registry:
                raise ValueError(f'Invalid or duplicate {kind} identifier')
            registry[key] = record
        registries[kind] = registry
    for event in data['competitions']:
        if not event.get('name') or not event.get('country'):
            raise ValueError('Competition name and country required')
    for contributor in data['contributors']:
        if not contributor.get('name') or not contributor.get('roles') or not contributor.get('source_urls'):
            raise ValueError('Contributor credit and evidence required')
        for url in contributor['source_urls']:
            https_url(url)
    slots = set()
    for award in data['awards']:
        if award.get('competition') not in registries['competitions']:
            raise ValueError('Unknown competition')
        if type(award.get('year')) is not int or not 1900 <= award['year'] <= date.today().year:
            raise ValueError('Invalid award year')
        if not award.get('cultivar') or not award.get('category'):
            raise ValueError('Cultivar and original category label required')
        if award.get('place') is not None and (type(award['place']) is not int or award['place'] < 1):
            raise ValueError('Invalid placing')
        if not award.get('contributors') or any(c not in registries['contributors'] for c in award['contributors']):
            raise ValueError('Unknown contributor')
        if award.get('evidence') not in EVIDENCE:
            raise ValueError('Unknown evidence class')
        https_url(award.get('source_url'))
        try:
            checked = date.fromisoformat(award['checked_at'])
            if checked > date.today():
                raise ValueError('Future verification date')
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError('Valid verification date required') from error
        slot = (award['competition'], award['year'], award['category'], award.get('place'), award['cultivar'], tuple(sorted(award['contributors'])))
        if slot in slots:
            raise ValueError('Duplicate award claim')
        slots.add(slot)
        image = award.get('image')
        if image:
            https_url(image.get('url'))
            https_url(image.get('source_url'))
            if image.get('license') not in {'CC0-1.0', 'CC-BY-4.0', 'CC-BY-SA-4.0', 'permission'} or not image.get('attribution'):
                raise ValueError('Verified image license and attribution required')
            if image['license'] == 'permission':
                https_url(image.get('permission_url'))
    return data


def load_archive(path):
    return validate_archive(json.loads(path.read_text()))


def search_entries(data):
    events = {e['id']: e for e in data['competitions']}
    people = {p['id']: p for p in data['contributors']}
    items = []
    for award in data['awards']:
        event = events[award['competition']]
        credit = ' · '.join(people[p]['name'] for p in award['contributors'])
        items.append({'kind': 'award', 'name': award['cultivar'], 'href': '/cups.html#' + award['id'], 'blurb': f"{event['name']} · {event['country']} · {award['year']} · {award['category']} · {credit} · {EVIDENCE[award['evidence']]}"})
    items.extend({'kind': 'contributor', 'name': p['name'], 'href': f"/contributors/{p['id']}.html", 'blurb': 'Award-history contributor · ' + ', '.join(p['roles'])} for p in data['contributors'])
    items.extend({'kind': 'competition', 'name': e['name'], 'href': '/cups.html?competition=' + e['id'], 'blurb': e['country'] + ' · selected sourced award records'} for e in data['competitions'])
    return items


def render_archive(data, cultivars):
    validate_archive(data)
    events = {e['id']: e for e in data['competitions']}
    people = {p['id']: p for p in data['contributors']}
    def select(label, key, choices):
        options = ''.join(f'<option value="{esc(value)}">{esc(name)}</option>' for value, name in choices)
        return f'<label>{label}<select name="{key}" id="award-{key}"><option value="">All</option>{options}</select></label>'
    filters = select('Competition', 'competition', [(e['id'], e['name']) for e in data['competitions']])
    filters += select('Year', 'year', [(y, y) for y in sorted({a['year'] for a in data['awards']}, reverse=True)])
    filters += select('Country', 'country', [(c, c) for c in sorted({e['country'] for e in data['competitions']})])
    filters += select('Evidence', 'evidence', EVIDENCE.items())
    filters += select('Contributor', 'contributor', [(p['id'], p['name']) for p in sorted(data['contributors'], key=lambda p: p['name'])])
    rows = []
    for award in sorted(data['awards'], key=lambda a: (-a['year'], a['competition'], a['category'])):
        event = events[award['competition']]
        cultivar = cultivars.get(award['cultivar'].lower())
        name = f'<a href="/cultivars/{esc(cultivar["slug"])}.html">{esc(award["cultivar"])}</a>' if cultivar else esc(award['cultivar'])
        credit = ', '.join(f'<a href="/contributors/{p}.html">{esc(people[p]["name"])}</a>' for p in award['contributors'])
        search = ' '.join([award['cultivar'], event['name'], event['country'], str(award['year']), award['category'], *(people[p]['name'] for p in award['contributors'])])
        image = award.get('image')
        photo = f'<img loading="lazy" width="120" src="{esc(image["url"])}" alt="{esc(award["cultivar"])}"><small>{esc(image["attribution"])} · {esc(image["license"])}</small>' if image else '<small>No authenticated entry photo</small>'
        rows.append(f'''<tr id="{award['id']}" data-award-row data-search="{esc(search)}" data-competition="{event['id']}" data-year="{award['year']}" data-country="{esc(event['country'])}" data-evidence="{award['evidence']}" data-contributors="{esc(' '.join(award['contributors']))}">
<td>{esc(event['name'])}<br>{award['year']} · {esc(event['country'])}</td><td>{esc(award['category'])}<br>{'Place ' + str(award['place']) if award['place'] else 'Placing unspecified'}</td>
<td>{name}<br>{photo}</td><td>{credit}</td><td>{EVIDENCE[award['evidence']]}<br><a href="{esc(award['source_url'])}" rel="noopener noreferrer">Result source</a><br><small>Checked {award['checked_at']}</small></td></tr>''')
    coverage = ''.join(f'<li>{esc(e["name"])}: {sum(a["competition"] == e["id"] for a in data["awards"])} records; indexed years: {", ".join(str(y) for y in sorted({a["year"] for a in data["awards"] if a["competition"] == e["id"]}))}. Other years unindexed.</li>' for e in data['competitions'])
    return f'''<main><p class="kicker">Research archive</p><h1>Cups, cultivars &amp; contributors.</h1>
<p class="lede">{esc(data['coverage'])}</p>
<p><strong>{len(data['awards'])} award records · {len(events)} competition series · {len(people)} credited contributors</strong></p>
<p>A prize belongs to a specific entry, category and year. Entrant credit does not establish original breeder identity, genetic authenticity or a universal world ranking. Missing chemistry and imagery remain unknown.</p>
<form id="award-filters"><label>Search award history<input name="q" id="award-q" type="search" placeholder="Cup, cultivar, entrant, category or year"></label><div class="grid">{filters}</div><button type="reset">Clear filters</button></form>
<p id="award-count" role="status" aria-live="polite">{len(rows)} records</p><p id="award-empty" hidden>No matching records. Try fewer filters.</p>
<div style="overflow-x:auto"><table><caption>Sourced award history</caption><thead><tr><th scope="col">Competition</th><th scope="col">Category / placing</th><th scope="col">Cultivar / entry</th><th scope="col">Credited participant</th><th scope="col">Evidence</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>
<h2>Coverage &amp; evidence</h2><ul>{coverage}</ul><p>Organizer record = organizer's published result. Publisher report = editorial reporting. Participant claim = self-reported award history requiring independent corroboration. These labels do not validate lineage or laboratory values.</p>
<p><a href="/data/awards.json">Download sourced archive JSON</a></p></main>'''


def render_contributor(person, data):
    awards = [a for a in data['awards'] if person['id'] in a['contributors']]
    events = {e['id']: e for e in data['competitions']}
    results = ''.join(f'<li><a href="/cups.html#{a["id"]}">{a["year"]} · {esc(events[a["competition"]]["name"])} · {esc(a["cultivar"])} · {esc(a["category"])}</a> — {EVIDENCE[a["evidence"]]}</li>' for a in awards)
    sources = ''.join(f'<li><a href="{esc(url)}" rel="noopener noreferrer">Credit source {i + 1}</a></li>' for i, url in enumerate(person['source_urls']))
    return f'<main><p class="kicker">Award-history contributor</p><h1>{esc(person["name"])}</h1><p>Role: {esc(", ".join(person["roles"]))}. Credit is preserved as published, including collaborations; original breeder identity is not inferred.</p><h2>Indexed results</h2><ul>{results}</ul><h2>Evidence</h2><ul>{sources}</ul><p><a href="/cups.html?contributor={quote(person["id"])}">Filter archive to this contributor</a></p></main>'
