#!/usr/bin/env python3
"""Build the Collett website.

Reads the content files in content/ and writes every HTML page into public/.
Uses only the Python standard library (Python 3.8+).

    python3 tools/build.py

The generated pages are committed, so the host never needs to run this:
run it after editing anything in content/ (or the templates below) and
commit the result.
"""
import html
import json
import os
import re
import shutil
from datetime import date, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(ROOT, "content")
OUT = os.path.join(ROOT, "public")


def load(name):
    with open(os.path.join(CONTENT, name), encoding="utf-8") as f:
        return json.load(f)


SITE = load("site.json")
PROPS = load("properties.json")
TEAM = load("team.json")
PRESS = load("press.json")
CLIENTS = load("clients.json")
USMAP = load("usmap.json")

PROP_BY_SLUG = {p["slug"]: p for p in PROPS}
TEAM_BY_SLUG = {t["slug"]: t for t in TEAM}
OFFICE_BY_TEAM = {o["teamOffice"]: o for o in SITE["offices"]}
YEAR = date.today().year


def _asset_version():
    """Short hash of the CSS/JS so browsers fetch new copies only when they change."""
    import hashlib
    h = hashlib.sha1()
    for sub in ("assets/css", "assets/js"):
        folder = os.path.join(OUT, sub)
        for name in sorted(os.listdir(folder)) if os.path.isdir(folder) else []:
            if name != "properties-data.js":
                with open(os.path.join(folder, name), "rb") as fh:
                    h.update(fh.read())
    with open(os.path.join(CONTENT, "properties.json"), "rb") as fh:  # feeds properties-data.js
        h.update(fh.read())
    return h.hexdigest()[:10]


ASSET_VERSION = _asset_version()

STATE_NAMES = {
    "AL": "Alabama", "AR": "Arkansas", "AZ": "Arizona", "FL": "Florida", "GA": "Georgia",
    "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "MD": "Maryland", "MO": "Missouri",
    "MS": "Mississippi", "NC": "North Carolina", "OK": "Oklahoma", "SC": "South Carolina",
    "TN": "Tennessee", "TX": "Texas", "VA": "Virginia", "WV": "West Virginia",
}


def e(s):
    return html.escape(str(s or ""), quote=True)


def u(path):
    """Root-relative URL for a path inside public/."""
    return "/" + path.lstrip("/")


def write(path, content):
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)


def fmt_date(iso, style="long"):
    d = datetime.strptime(iso, "%Y-%m-%d")
    if style == "short":
        return "%s %d, %d" % (d.strftime("%b"), d.day, d.year)
    return "%s %d, %d" % (d.strftime("%B"), d.day, d.year)


def excerpt(htmltext, n=180):
    t = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", htmltext))).strip()
    if len(t) <= n:
        return t
    return t[:n].rsplit(" ", 1)[0].rstrip(",.;:–-") + "…"


def initials(name):
    parts = [p for p in re.sub(r",.*$", "", name).split() if p[0].isalpha()]
    return (parts[0][0] + parts[-1][0]).upper() if len(parts) > 1 else name[:2].upper()


# ---------------------------------------------------------------- icons
ICONS = {
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "phone": '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/>',
    "pin": '<path d="M12 22s7-6.2 7-12a7 7 0 1 0-14 0c0 5.8 7 12 7 12z"/><circle cx="12" cy="10" r="2.5"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
    "external": '<path d="M14 4h6v6M20 4l-9 9M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"/>',
    "grid": '<rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/>',
    "map": '<path d="M9 4 3 6v14l6-2 6 2 6-2V4l-6 2-6-2zM9 4v14M15 6v14"/>',
    "close": '<path d="M6 6l12 12M18 6 6 18"/>',
    "chev": '<path d="m6 9 6 6 6-6"/>',
    "left": '<path d="m15 18-6-6 6-6"/>',
    "right": '<path d="m9 18 6-6-6-6"/>',
    "menu": '<path d="M3 7h18M3 12h18M3 17h18"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="1"/><path d="m3 7 9 6 9-6"/>',
    "alert": '<path d="M12 3 2 20h20L12 3z"/><path d="M12 10v4M12 17h.01"/>',
    "wrench": '<path d="M14.7 6.3a4 4 0 0 0 5 5L22 14l-8 8-2.3-2.3a4 4 0 0 0-5-5L2 10l8-8 2.3 2.3a4 4 0 0 0 2.4 2z"/>',
    "key": '<circle cx="7.5" cy="15.5" r="4.5"/><path d="m10.7 12.3 9.3-9.3M17 6l3 3M14 9l2 2"/>',
    "linkedin": '<path d="M4 9h3.5v11H4zM5.7 3.5a2 2 0 1 1 0 4 2 2 0 0 1 0-4zM10 9h3.4v1.6c.5-.9 1.7-1.9 3.5-1.9 3.6 0 4.3 2.4 4.3 5.4V20h-3.5v-5.2c0-1.3 0-2.9-1.8-2.9s-2.1 1.4-2.1 2.8V20H10z" fill="currentColor" stroke="none"/>',
    "facebook": '<path d="M14 8.5V6.8c0-.8.2-1.3 1.4-1.3H17V2.2c-.3 0-1.3-.2-2.5-.2-2.5 0-4.2 1.5-4.2 4.3v2.2H7.5v3.7h2.8V22H14v-9.8h2.8l.4-3.7H14z" fill="currentColor" stroke="none"/>',
    "x": '<path d="M17.8 3h3.1l-6.8 7.7L22 21h-6.3l-4.9-6.4L5.2 21H2.1l7.3-8.3L1.8 3h6.4l4.4 5.9L17.8 3zm-1.1 16.2h1.7L7.4 4.7H5.6l11.1 14.5z" fill="currentColor" stroke="none"/>',
}


def icon(name, cls="i"):
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true">{ICONS[name]}</svg>'


# ---------------------------------------------------------------- layout
NAV = [
    ("About", "about-us/", "about"),
    ("Services", "services/", "services"),
    ("Properties", "properties/", "properties"),
    ("Team", "team/", "team"),
    ("News", "press/", "press"),
    ("Contact", "contact-us/", "contact"),
]


def header(active):
    items = []
    for label, href, key in NAV:
        cur = ' aria-current="page"' if key == active else ""
        if key == "services":
            sub = "".join(
                f'<li><a href="{u(s["slug"] + "/")}">{e(s["name"])}</a></li>' for s in SITE["services"]
            )
            sub += '<li class="sep"></li>' + "".join(
                f'<li><a href="{e(c["url"])}" target="_blank" rel="noopener">{e(c["name"])} {icon("external", "i i-xs")}</a></li>'
                for c in SITE["companies"]
            )
            items.append(
                f'<li class="has-sub"><a href="{u(href)}"{cur}>{label}</a>'
                f'<button class="sub-toggle" aria-expanded="false" aria-label="Show services">{icon("chev")}</button>'
                f'<ul class="sub">{sub}</ul></li>'
            )
        else:
            items.append(f'<li><a href="{u(href)}"{cur}>{label}</a></li>')
    return f"""<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="/" aria-label="Collett home">
      <img src="/assets/img/brand/collett-logo-navy.png" width="170" height="44" alt="Collett">
    </a>
    <nav class="primary" aria-label="Main">
      <ul>{''.join(items)}</ul>
    </nav>
    <div class="header-actions">
      <a class="btn btn-ghost btn-sm" href="{e(SITE['tenantPortal'])}" target="_blank" rel="noopener">{icon('key')}<span>Tenant Portal</span></a>
      <button class="nav-toggle" aria-expanded="false" aria-controls="mobile-nav" aria-label="Open menu">{icon('menu')}</button>
    </div>
  </div>
  <div class="mobile-nav" id="mobile-nav" hidden>
    <ul>
      {''.join(f'<li><a href="{u(h)}">{l}</a></li>' for l, h, k in NAV)}
      {''.join(f'<li class="sub-item"><a href="{u(s["slug"] + "/")}">{e(s["name"])}</a></li>' for s in SITE["services"])}
      <li><a href="{e(SITE['tenantPortal'])}" target="_blank" rel="noopener">Tenant Portal</a></li>
    </ul>
  </div>
</header>"""


def footer():
    offices = "".join(
        f"""<div class="f-office">
          <h3>{e(o['name'])}</h3>
          <p>{'<br>'.join(e(l) for l in o['lines'])}</p>
          <p><a href="tel:{o['phone'].replace('.', '')}">{e(o['phone'])}</a></p>
        </div>"""
        for o in SITE["offices"]
    )
    soc = SITE["social"]
    return f"""<footer class="site-footer">
  <div class="wrap">
    <div class="f-top">
      <div class="f-brand">
        <img src="/assets/img/brand/collett-logo-white.png" width="150" height="39" alt="Collett" loading="lazy">
        <p>Full-service commercial real estate since {SITE['founded']}: development, management, tenant representation and brokerage.</p>
        <div class="social">
          <a href="{e(soc['linkedin'])}" target="_blank" rel="noopener" aria-label="LinkedIn">{icon('linkedin')}</a>
          <a href="{e(soc['facebook'])}" target="_blank" rel="noopener" aria-label="Facebook">{icon('facebook')}</a>
          <a href="{e(soc['x'])}" target="_blank" rel="noopener" aria-label="X (Twitter)">{icon('x')}</a>
        </div>
      </div>
      <div class="f-offices">{offices}</div>
    </div>
    <div class="f-mid">
      <ul class="f-links">
        {''.join(f'<li><a href="{u(h)}">{l}</a></li>' for l, h, k in NAV)}
        <li><a href="{e(SITE['tenantPortal'])}" target="_blank" rel="noopener">Tenant Portal</a></li>
      </ul>
      <p class="f-emergency">{icon('alert')} After-hours maintenance emergency: <a href="tel:{SITE['phones']['emergency'].replace('.', '')}">{e(SITE['phones']['emergency'])}</a></p>
    </div>
    <div class="f-bottom">
      <p>&copy; {YEAR} Collett. All rights reserved.</p>
      <p><a href="/privacy-policy/">Privacy Policy</a><a href="/legal/">Legal</a></p>
    </div>
  </div>
</footer>"""


def page(path, title, body, active="", description=None, canonical=None, og_image=None, extra_head="", scripts=()):
    desc = description or SITE["description"]
    full_title = f"{title} | Collett" if title else "Collett | Commercial Real Estate Since 1987"
    canon = SITE["domain"] + "/" + (canonical if canonical is not None else path.replace("index.html", ""))
    og = SITE["domain"] + u(og_image) if og_image else SITE["domain"] + "/assets/img/og-default.jpg"
    script_tags = "".join(f'<script src="/assets/js/{s}?v={ASSET_VERSION}" defer></script>' for s in scripts)
    doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{e(canon)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Collett">
<meta property="og:title" content="{e(title or 'Collett')}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{e(canon)}">
<meta property="og:image" content="{e(og)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#082f43">
<link rel="icon" href="/assets/img/brand/favicon-32.png" sizes="32x32" type="image/png">
<link rel="icon" href="/assets/img/brand/favicon-64.png" sizes="64x64" type="image/png">
<link rel="apple-touch-icon" href="/assets/img/brand/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Figtree:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/css/site.css?v={ASSET_VERSION}">
{extra_head}
</head>
<body>
{header(active)}
<main id="main">
{body}
</main>
{footer()}
<script src="/assets/js/site.js?v={ASSET_VERSION}" defer></script>
{script_tags}
</body>
</html>
"""
    write(path, doc)


def redirect_page(path, target, title):
    write(path, f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>{e(title)} | Collett</title>
<meta name="robots" content="noindex"><link rel="canonical" href="{e(target)}">
<meta http-equiv="refresh" content="0; url={e(target)}"></head>
<body><p>This page has moved to <a href="{e(target)}">{e(target)}</a>.</p></body></html>
""")


def page_head(eyebrow, title, lead="", crumbs=None, cls=""):
    bc = ""
    if crumbs:
        bc = '<nav class="crumbs" aria-label="Breadcrumb"><ol>' + "".join(
            f'<li><a href="{e(h)}">{e(l)}</a></li>' if h else f'<li aria-current="page">{e(l)}</li>' for l, h in crumbs
        ) + "</ol></nav>"
    return f"""<section class="page-head {cls}">
  <div class="wrap">
    {bc}
    <p class="eyebrow">{e(eyebrow)}</p>
    <h1>{title}</h1>
    {f'<p class="lead">{lead}</p>' if lead else ''}
  </div>
</section>"""


def cta_band(title="Have a site, a space or a project in mind?", text="Talk with the Collett team about development, leasing, management or tenant representation.", btn="Contact us", href="/contact-us/"):
    return f"""<section class="cta-band">
  <div class="wrap cta-inner">
    <div>
      <h2>{e(title)}</h2>
      <p>{e(text)}</p>
    </div>
    <div class="cta-actions">
      <a class="btn btn-light" href="{href}">{e(btn)} {icon('arrow')}</a>
      <a class="btn btn-outline-light" href="tel:{SITE['phones']['main'].replace('.', '')}">{icon('phone')} {e(SITE['phones']['main'])}</a>
    </div>
  </div>
</section>"""


# ---------------------------------------------------------------- property helpers
def prop_type(p):
    t = p["types"]
    for k in ("Retail", "Industrial", "Office", "Land Listings", "Other"):
        if k in t:
            return k
    return "Other"


TYPE_LABEL = {"Retail": "Retail", "Industrial": "Industrial", "Office": "Office", "Land Listings": "Land", "Other": "Other"}


def prop_url(p):
    return f"/properties/{p['slug']}/" if p["hasPage"] else None


def prop_tags(p, limit=3):
    tags = []
    if p.get("availability"):
        tags.append(("avail", p["availability"]))
    if p.get("underConstruction"):
        tags.append(("uc", "Under construction"))
    if p.get("developed"):
        tags.append(("dev", "Developed by Collett"))
    if p.get("managed"):
        tags.append(("man", "Managed by Collett"))
    return "".join(f'<span class="tag tag-{k}">{e(v)}</span>' for k, v in tags[:limit])


def placeholder(p, cls="ph"):
    return f'<div class="{cls}" aria-hidden="true"><span>{e(initials(p["name"]))}</span></div>'


def prop_card(p, size=""):
    href = prop_url(p)
    img = (
        f'<img src="{u(p["card"])}" alt="" loading="lazy" decoding="async">' if p.get("card") else placeholder(p)
    )
    title = f'<a href="{href}">{e(p["name"])}</a>' if href else e(p["name"])
    return f"""<article class="p-card {size}">
  <div class="p-media">{img}<span class="p-type">{e(TYPE_LABEL[prop_type(p)])}</span></div>
  <div class="p-body">
    <h3>{title}</h3>
    <p class="p-loc">{icon('pin', 'i i-xs')}{e(p['city'])}, {e(p['state'])}</p>
    <div class="tags">{prop_tags(p, 2)}</div>
  </div>
</article>"""


def contact_person(name):
    """Match a property contact name to a team member."""
    key = re.sub(r"[^a-z]", "", name.lower())
    for t in TEAM:
        if re.sub(r"[^a-z]", "", t["name"].lower()) == key:
            return t
    first_last = name.split()
    for t in TEAM:
        tn = t["name"].split()
        if first_last and tn and first_last[0].lower() == tn[0].lower() and first_last[-1].lower().strip(",") == tn[1].lower().strip(","):
            return t
    return None


# ---------------------------------------------------------------- map
ACTIVE_STATES = sorted({p["state"] for p in PROPS})


def map_svg_file():
    paths = []
    for st, d in USMAP["states"].items():
        cls = "on" if st in ACTIVE_STATES else "off"
        paths.append(f'<path class="{cls}" d="{d}"/>')
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {USMAP['width']} {USMAP['height']}">
<style>.off{{fill:#e3ddd1}}.on{{fill:#cfdbe1}}.b{{fill:none;stroke:#f7f4ee;stroke-width:1.1;stroke-linejoin:round}}</style>
{''.join(paths)}<path class="b" d="{USMAP['borders']}"/></svg>"""
    write("assets/img/us-map.svg", svg)


def map_point(p):
    return USMAP["points"].get(p["slug"])


def portfolio_map(points_id="map-points", interactive=True):
    w, h = USMAP["width"], USMAP["height"]
    return f"""<div class="us-map" data-map>
  <img src="/assets/img/us-map.svg" alt="" class="us-map-base" width="{w}" height="{h}">
  <svg class="us-map-dots" viewBox="0 0 {w} {h}" id="{points_id}" role="img" aria-label="Map of Collett properties"></svg>
  <div class="map-tip" hidden></div>
</div>
<p class="map-legend"><span><i style="background:var(--blue)"></i>Retail</span><span><i style="background:var(--navy)"></i>Industrial</span><span><i style="background:#6b8a99"></i>Office</span><span><i style="background:#c29a52"></i>Land</span></p>"""


# ---------------------------------------------------------------- data file for the browser
def write_props_js():
    rows = []
    for p in PROPS:
        xy = map_point(p)
        rows.append({
            "s": p["slug"], "n": p["name"], "c": p["city"], "st": p["state"],
            "t": TYPE_LABEL[prop_type(p)], "a": p.get("availability") or "",
            "d": 1 if p.get("developed") else 0, "m": 1 if p.get("managed") else 0,
            "uc": 1 if p.get("underConstruction") else 0,
            "img": u(p["card"]) if p.get("card") else "",
            "xy": xy or None, "pg": 1 if p["hasPage"] else 0,
            "k": " ".join([p["name"], p.get("address") or "", p["city"], STATE_NAMES.get(p["state"], ""), p.get("summary") or "", (p.get("facts") or {}).get("Tenants", "")]).lower(),
        })
    write("assets/js/properties-data.js", "window.COLLETT_PROPERTIES=" + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n")


# ---------------------------------------------------------------- team helpers
LEADER_ORDER = ["john-collett-charlotte", "robert-collett-morganton"]


def last_name(t):
    n = re.sub(r",.*$", "", t["name"]).split()
    return n[-1].lower() if n else t["name"].lower()


def team_group(t):
    title = t["title"].lower()
    if title in ("partner", "cfo") or "vice president" in title:
        return "Leadership"
    if "develop" in title and "coordinator" not in title:
        return "Development"
    if "broker" in title or "leasing" in title or "brokerage" in title:
        return "Brokerage"
    if "manager" in title and ("real estate" in title or "lease" in title) or "property admin" in title:
        return "Management"
    if any(k in title for k in ("account", "controller", "admin")):
        return "Accounting & Administration"
    # untitled: place by the role they hold on property listings
    for p in PROPS:
        for c in p.get("contacts", []):
            if contact_person(c["name"]) is t:
                return "Brokerage" if "Broker" in c["role"] else "Management"
    return "Accounting & Administration"


GROUPS = ["Leadership", "Development", "Brokerage", "Management", "Accounting & Administration"]


def team_sorted():
    def key(t):
        if t["slug"] in LEADER_ORDER:
            return (0, LEADER_ORDER.index(t["slug"]), "")
        g = team_group(t)
        return (1 if g == "Leadership" else 2, 0, last_name(t))
    return sorted(TEAM, key=key)


def person_photo(t, cls="avatar", lazy=True):
    if t.get("photo"):
        return f'<img class="{cls}" src="{u(t["photo"])}" alt="" {"loading=lazy" if lazy else ""} decoding="async">'
    return f'<div class="{cls} avatar-ph" aria-hidden="true"><span>{e(initials(t["name"]))}</span></div>'


def office_name(t):
    o = OFFICE_BY_TEAM.get(t["office"])
    return o["name"] if o else t["office"]


def person_card(t):
    tel = t["phone"].replace(".", "").replace(" ", "")
    return f"""<article class="person" data-group="{e(team_group(t))}" data-office="{e(t['office'])}" data-name="{e(t['name'].lower())} {e(t['title'].lower())}">
  <a href="/team/{t['slug']}/" class="person-link">
    {person_photo(t)}
    <h3>{e(t['name'])}</h3>
    <p class="role">{e(t['title'])}</p>
  </a>
  <p class="meta">{e(office_name(t))}{f' · <a href="tel:{tel}">{e(t["phone"])}</a>' if t['phone'] else ''}</p>
</article>"""


def props_for_person(t):
    out = []
    for p in PROPS:
        for c in p.get("contacts", []):
            if contact_person(c["name"]) is t:
                out.append((p, c["role"]))
                break
    return out


# ---------------------------------------------------------------- pages
def build_home():
    n_props = len(PROPS)
    n_states = len(ACTIVE_STATES)
    hero_imgs = SITE["home"]["heroPhotos"]
    hero_caps = []
    for path in hero_imgs:
        slug = path.split("/")[-2]
        p = PROP_BY_SLUG.get(slug)
        hero_caps.append((path, p))
    figs = []
    for i, (path, p) in enumerate(hero_caps):
        load_attr = "fetchpriority=high" if i == 0 else "loading=lazy"
        cap = ""
        if p:
            cap = "<figcaption>%s<span>%s, %s</span></figcaption>" % (e(p["name"]), e(p["city"]), e(p["state"]))
        figs.append('<figure class="m%d"><img src="%s" alt="" %s decoding="async">%s</figure>' % (i + 1, u(path), load_attr, cap))
    mosaic = "".join(figs)
    type_opts = "".join(f'<option value="{v}">{v}</option>' for v in ["Retail", "Industrial", "Office", "Land"])
    state_opts = "".join(
        f'<option value="{s}">{e(STATE_NAMES.get(s, s))}</option>' for s in sorted(ACTIVE_STATES, key=lambda s: STATE_NAMES.get(s, s))
    )

    services = "".join(
        f"""<a class="svc" href="/{s['slug']}/">
      <span class="svc-num">0{i + 1}</span>
      <h3>{e(s['name'])}</h3>
      <p>{e(s['short'])}</p>
      <span class="svc-more">Learn more {icon('arrow')}</span>
    </a>"""
        for i, s in enumerate(SITE["services"])
    )

    feat = [PROP_BY_SLUG[s] for s in SITE["home"]["featured"] if s in PROP_BY_SLUG]
    lead, rest = feat[0], feat[1:]
    lead_desc = lead.get("summary") or " ".join(lead.get("paras", [])[:1])
    lead_html = f"""<article class="feature">
      <a class="feature-media" href="{prop_url(lead)}"><img src="{u(lead['photos'][0])}" alt="{e(lead['name'])}" loading="lazy" decoding="async"></a>
      <div class="feature-body">
        <p class="eyebrow">Featured property</p>
        <h3><a href="{prop_url(lead)}">{e(lead['name'])}</a></h3>
        <p class="p-loc">{icon('pin', 'i i-xs')}{e(lead.get('address') or '')}{', ' if lead.get('address') else ''}{e(lead['city'])}, {e(lead['state'])}</p>
        <p>{e(lead_desc)}</p>
        <div class="tags">{prop_tags(lead)}</div>
        <a class="btn btn-primary" href="{prop_url(lead)}">View property {icon('arrow')}</a>
      </div>
    </article>"""

    # top states for the map sidebar
    counts = {}
    for p in PROPS:
        counts[p["state"]] = counts.get(p["state"], 0) + 1
    top = sorted(counts.items(), key=lambda x: -x[1])[:6]
    top_html = "".join(
        f'<li><a href="/properties/?state={s}"><span>{e(STATE_NAMES.get(s, s))}</span><b>{c}</b></a></li>' for s, c in top
    )

    clients = "".join(f'<li><img src="{u(c["logo"])}" alt="{e(c["name"])}" loading="lazy"></li>' for c in CLIENTS)

    news = "".join(news_card(a) for a in PRESS[:3])

    companies = "".join(
        f"""<a class="co" href="{e(c['url'])}" target="_blank" rel="noopener">
      <h3>{e(c['name'])} {icon('external', 'i i-sm')}</h3>
      <p>{e(c['text'])}</p>
    </a>"""
        for c in SITE["companies"]
    )

    body = f"""
<section class="hero">
  <div class="wrap hero-grid">
    <div class="hero-copy">
      <p class="eyebrow">Commercial real estate · Since {SITE['founded']}</p>
      <h1>Building the centers <br class="br-lg">communities count on.</h1>
      <p class="lead">Collett develops, manages and leases retail and mixed-use properties across the Southeast and Southwest, from a single pad site to a million-square-foot town center.</p>
      <div class="hero-actions">
        <a class="btn btn-primary" href="/properties/">Browse properties {icon('arrow')}</a>
        <a class="btn btn-ghost" href="/contact-us/">Talk to our team</a>
      </div>
      <form class="quick-search" action="/properties/" method="get" role="search" aria-label="Quick property search">
        <label><span>State</span><select name="state"><option value="">All states</option>{state_opts}</select></label>
        <label><span>Property type</span><select name="type"><option value="">All types</option>{type_opts}</select></label>
        <label><span>Availability</span><select name="avail"><option value="">Any</option><option value="lease">For lease</option><option value="sale">For sale</option></select></label>
        <button class="btn btn-navy" type="submit">{icon('search')}<span>Search</span></button>
      </form>
    </div>
    <div class="mosaic">{mosaic}</div>
  </div>
</section>

<section class="stats" aria-label="Collett at a glance">
  <div class="wrap stats-grid">
    <div><b>{SITE['founded']}</b><span>Founded in Charlotte, NC</span></div>
    <div><b>{SITE['retailSfDeveloped']}</b><span>Square feet of retail developed</span></div>
    <div><b>{n_props}</b><span>Properties in our portfolio</span></div>
    <div><b>{n_states}</b><span>States</span></div>
    <div><b>{len(SITE['offices'])}</b><span>Offices across NC, SC and TX</span></div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="sec-head">
      <div>
        <p class="eyebrow">What we do</p>
        <h2>One firm for every stage of a property’s life.</h2>
      </div>
      <p>Institutions, corporations and individuals, whether developers, owners or tenants, rely on our team for development, leasing, property management, asset management, investment sales and brokerage.</p>
    </div>
    <div class="svc-grid">{services}</div>
  </div>
</section>

<section class="section section-paper">
  <div class="wrap">
    <div class="sec-head">
      <div>
        <p class="eyebrow">Properties</p>
        <h2>Where we’re building and leasing now.</h2>
      </div>
      <a class="text-link" href="/properties/">See all {n_props} properties {icon('arrow')}</a>
    </div>
    {lead_html}
    <div class="p-grid p-grid-3">{''.join(prop_card(p) for p in rest)}</div>
  </div>
</section>

<section class="section footprint">
  <div class="wrap fp-grid">
    <div class="fp-copy">
      <p class="eyebrow">Our footprint</p>
      <h2>Rooted in the Carolinas, active across {n_states} states.</h2>
      <p>Each dot is a property Collett has developed, manages or is marketing today. Hover a dot for details, or open the full map on the Properties page.</p>
      <ul class="fp-list">{top_html}</ul>
      <a class="text-link" href="/properties/?view=map">Open the property map {icon('arrow')}</a>
    </div>
    <div>{portfolio_map()}</div>
  </div>
</section>

<section class="section clients">
  <div class="wrap">
    <div class="sec-head sec-head-center">
      <p class="eyebrow">Tenant representation</p>
      <h2>Retailers we’ve helped find their next location.</h2>
    </div>
    <ul class="logo-wall">{clients}</ul>
  </div>
</section>

<section class="section section-paper">
  <div class="wrap two-col">
    <div>
      <p class="eyebrow">The Collett family</p>
      <h2>Specialized platforms, one shared foundation.</h2>
      <p>Alongside our core retail and mixed-use business, affiliated Collett companies focus on industrial development and real estate investment.</p>
    </div>
    <div class="co-grid">{companies}</div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="sec-head">
      <div>
        <p class="eyebrow">News</p>
        <h2>Latest from Collett.</h2>
      </div>
      <a class="text-link" href="/press/">All news {icon('arrow')}</a>
    </div>
    <div class="news-grid">{news}</div>
  </div>
</section>
{cta_band()}
"""
    page("index.html", "", body, active="home", canonical="", og_image=hero_imgs[0], scripts=("properties-data.js", "map.js"))


def news_card(a, show_img=True):
    img = ""
    if show_img and a.get("images"):
        img = f'<div class="n-media"><img src="{u(a["images"][0])}" alt="" loading="lazy" decoding="async"></div>'
    return f"""<article class="n-card" data-year="{a['date'][:4]}">
  {img}
  <div class="n-body">
    <time datetime="{a['date']}">{fmt_date(a['date'])}</time>
    <h3><a href="/press/{a['slug']}/">{e(a['title'])}</a></h3>
    <p>{e(excerpt(a['body'], 150))}</p>
  </div>
</article>"""


def build_about():
    leaders = [t for t in team_sorted() if team_group(t) == "Leadership"]
    leader_cards = "".join(person_card(t) for t in leaders)
    ranks = "".join(f"<li>{e(r)}</li>" for r in SITE["rankings"])
    offices = "".join(office_block(o) for o in SITE["offices"])
    paras = "".join(f"<p>{e(p)}</p>" for p in SITE["about"])
    quote_src = TEAM_BY_SLUG.get("john-collett-charlotte")
    quote = ""
    if quote_src:
        for b in quote_src["bio"]:
            if b.get("p", "").startswith("“We have grown"):
                quote = b["p"].strip("“”\" .")
    timeline = [
        (str(SITE["founded"]), "Brothers John and Robert Collett found the firm in Charlotte, North Carolina."),
        ("2012", "Collett opens its Greenville, South Carolina office."),
        ("2019", "Collett Industrial launches to pursue industrial development and acquisitions."),
        ("Today", f"{SITE['retailSfDeveloped']} square feet of retail developed, with offices in Charlotte, Greenville, Dallas and Morganton."),
    ]
    tl = "".join(f'<li><span class="tl-year">{e(y)}</span><p>{e(t)}</p></li>' for y, t in timeline)
    body = f"""
{page_head('About Collett', 'A Charlotte firm built on relationships, since 1987.', 'Development, leasing, property management, strategic asset management, investment sales and brokerage, delivered by one team.', [('Home', '/'), ('About', None)])}
<section class="section">
  <div class="wrap about-grid">
    <div class="prose">{paras}
      <p>Today Collett continues its long history of developing first-class projects across a wide swath of the country. With key personnel in Charlotte, NC, Dallas, TX, and Greenville, SC, we are ideally suited to address the needs of our clients throughout the Southeast and Southwest.</p>
    </div>
    <aside class="about-aside">
      {f'<blockquote class="quote"><p>“{e(quote)}.”</p><footer>John Collett, Partner</footer></blockquote>' if quote else ''}
    </aside>
  </div>
</section>
<section class="section section-paper">
  <div class="wrap two-col">
    <div>
      <p class="eyebrow">Milestones</p>
      <h2>Steady growth, one deal at a time.</h2>
      <p>As John Collett likes to say, “we are only as good as our last deal.”</p>
    </div>
    <ol class="timeline">{tl}</ol>
  </div>
</section>
<section class="section">
  <div class="wrap">
    <div class="sec-head">
      <div>
        <p class="eyebrow">Leadership</p>
        <h2>The partners behind Collett.</h2>
      </div>
      <a class="text-link" href="/team/">Meet the whole team {icon('arrow')}</a>
    </div>
    <div class="people-grid">{leader_cards}</div>
  </div>
</section>
<section class="section section-navy">
  <div class="wrap two-col">
    <div>
      <p class="eyebrow">Leaders in the industry</p>
      <h2>Recognized among the Charlotte area’s largest firms.</h2>
      <p>Collett has appeared repeatedly in regional rankings of commercial real estate developers, brokerages and property managers.</p>
    </div>
    <ul class="rank-list">{ranks}</ul>
  </div>
</section>
<section class="section">
  <div class="wrap">
    <div class="sec-head"><div><p class="eyebrow">Offices</p><h2>Four offices, one team.</h2></div></div>
    <div class="office-grid">{offices}</div>
  </div>
</section>
{cta_band()}
"""
    page("about-us/index.html", "About", body, active="about",
         description="Founded in 1987 in Charlotte, NC by John and Robert Collett, Collett is a full-service commercial real estate firm serving the Southeast and Southwest.")


def office_block(o):
    tel = o["phone"].replace(".", "")
    maps = "https://www.google.com/maps/search/?api=1&query=" + o["map"].replace(" ", "+")
    return f"""<div class="office">
  <p class="eyebrow">{e(o['label'])}</p>
  <h3>{e(o['name'])}</h3>
  <p>{'<br>'.join(e(l) for l in o['lines'])}</p>
  <p class="office-links">
    <a href="tel:{tel}">{icon('phone', 'i i-sm')}{e(o['phone'])}</a>
    <a href="{e(maps)}" target="_blank" rel="noopener">{icon('pin', 'i i-sm')}Directions</a>
  </p>
  {f'<p class="small">Fax {e(o["fax"])}</p>' if o.get('fax') else ''}
  {f'<p class="small">Mailing: {", ".join(e(l) for l in o["mailing"])}</p>' if o.get('mailing') else ''}
</div>"""


def build_services():
    cards = "".join(
        f"""<a class="svc svc-lg" href="/{s['slug']}/">
      <span class="svc-num">0{i + 1}</span>
      <h2>{e(s['name'])}</h2>
      <p>{e(s['lead'])}</p>
      <ul>{''.join(f'<li>{e(x)}</li>' for x in s['points'])}</ul>
      <span class="svc-more">Explore {e(s['name'].lower())} {icon('arrow')}</span>
    </a>"""
        for i, s in enumerate(SITE["services"])
    )
    companies = "".join(
        f"""<a class="co" href="{e(c['url'])}" target="_blank" rel="noopener">
      <h3>{e(c['name'])} {icon('external', 'i i-sm')}</h3>
      <p>{e(c['text'])}</p>
    </a>"""
        for c in SITE["companies"]
    )
    body = f"""
{page_head('Services', 'Full-service commercial real estate.', 'Our team members work together across development, management, tenant representation and brokerage, so every client gets the depth of the whole firm.', [('Home', '/'), ('Services', None)])}
<section class="section">
  <div class="wrap svc-grid svc-grid-2">{cards}</div>
</section>
<section class="section section-paper" id="companies">
  <div class="wrap two-col">
    <div>
      <p class="eyebrow">The Collett family</p>
      <h2>Collett Industrial and Collett Capital.</h2>
      <p>Affiliated companies extend Collett’s experience into industrial development and real estate investment.</p>
    </div>
    <div class="co-grid">{companies}</div>
  </div>
</section>
{cta_band()}
"""
    page("services/index.html", "Services", body, active="services")

    for i, s in enumerate(SITE["services"]):
        build_service(s, i)

    redirect_page("collett-capital/index.html", "http://collettcapital.com/", "Collett Capital")


def build_service(s, i):
    paras = "".join(f"<p>{e(p)}</p>" for p in s["body"])
    points = "".join(f"<li>{e(x)}</li>" for x in s["points"])
    extra = ""
    if s.get("showClients"):
        logos = "".join(f'<li><img src="{u(c["logo"])}" alt="{e(c["name"])}" loading="lazy"></li>' for c in CLIENTS)
        extra += f"""<section class="section section-paper clients">
  <div class="wrap">
    <div class="sec-head sec-head-center"><p class="eyebrow">Clients</p><h2>Retailers we’ve represented.</h2></div>
    <ul class="logo-wall">{logos}</ul>
  </div>
</section>"""
    if s.get("licenses"):
        lic = "".join(
            f'<li><a href="{e(l["url"])}" target="_blank" rel="noopener">{e(l["name"])} {icon("external", "i i-xs")}</a></li>' for l in s["licenses"]
        )
        points_extra = f'<h3 class="side-h">Licensed with</h3><ul class="link-list">{lic}</ul>'
    else:
        points_extra = ""
    # related properties
    f = s.get("propertyFilter")
    rel = []
    if f == "developed":
        rel = [p for p in PROPS if p.get("developed") and p.get("card") and p["hasPage"]]
    elif f == "managed":
        rel = [p for p in PROPS if p.get("managed") and p.get("card") and p["hasPage"]]
    elif f == "available":
        rel = [p for p in PROPS if p.get("availability") and p.get("card") and p["hasPage"]]
    rel = rel[:6] if not rel else sorted(rel, key=lambda p: (-len(p["photos"]), p["name"]))[:3]
    qs = {"developed": "dev=1", "managed": "man=1", "available": "avail=any"}.get(f, "")
    if rel:
        extra += f"""<section class="section">
  <div class="wrap">
    <div class="sec-head"><div><p class="eyebrow">Properties</p><h2>{e(s['name'])} in practice.</h2></div>
    <a class="text-link" href="/properties/?{qs}">See related properties {icon('arrow')}</a></div>
    <div class="p-grid p-grid-3">{''.join(prop_card(p) for p in rel)}</div>
  </div>
</section>"""
    people = [t for t in team_sorted() if team_group(t) == s.get("teamGroup")][:8]
    if people:
        extra += f"""<section class="section section-paper">
  <div class="wrap">
    <div class="sec-head"><div><p class="eyebrow">People</p><h2>Who you’ll work with.</h2></div>
    <a class="text-link" href="/team/?group={e(s['teamGroup'])}">See the full team {icon('arrow')}</a></div>
    <div class="people-grid">{''.join(person_card(t) for t in people)}</div>
  </div>
</section>"""
    others = "".join(
        f'<li><a href="/{o["slug"]}/"{" aria-current=page" if o is s else ""}>{e(o["name"])}</a></li>' for o in SITE["services"]
    )
    body = f"""
{page_head(f'Services · 0{i + 1}', e(s['name']), e(s['lead']), [('Home', '/'), ('Services', '/services/'), (s['name'], None)])}
<section class="section">
  <div class="wrap svc-detail">
    <div class="prose">{paras}</div>
    <aside class="svc-aside">
      <h3 class="side-h">What’s included</h3>
      <ul class="check-list">{points}</ul>
      {points_extra}
      <h3 class="side-h">All services</h3>
      <ul class="link-list">{others}</ul>
    </aside>
  </div>
</section>
{extra}
{cta_band()}
"""
    page(f"{s['slug']}/index.html", s["name"], body, active="services", description=s["body"][0][:300])


def build_properties():
    type_opts = "".join(f'<option value="{v}">{v}</option>' for v in ["Retail", "Industrial", "Office", "Land", "Other"])
    state_opts = "".join(
        f'<option value="{s}">{e(STATE_NAMES.get(s, s))}</option>' for s in sorted(ACTIVE_STATES, key=lambda s: STATE_NAMES.get(s, s))
    )
    # server-rendered list for no-JS and SEO; JS replaces it
    noscript_list = "".join(
        f'<li><a href="/properties/{p["slug"]}/">{e(p["name"])}</a>, {e(p["city"])}, {e(p["state"])}</li>' for p in PROPS if p["hasPage"]
    )
    body = f"""
{page_head('Properties', 'Find space, sites and investments.', f'Search {len(PROPS)} retail, mixed-use, industrial, office and land properties Collett has developed, manages or is marketing.', [('Home', '/'), ('Properties', None)], cls='page-head-tight')}
<section class="section section-tight">
  <div class="wrap">
    <form class="filters" id="filters" role="search" aria-label="Filter properties">
      <label class="f-search"><span class="sr-only">Keyword</span>{icon('search')}<input type="search" name="q" placeholder="Search name, city, street or tenant" autocomplete="off"></label>
      <label><span>State</span><select name="state"><option value="">All states</option>{state_opts}</select></label>
      <label><span>Type</span><select name="type"><option value="">All types</option>{type_opts}</select></label>
      <label><span>Availability</span><select name="avail"><option value="">Any</option><option value="any">Available now</option><option value="lease">For lease</option><option value="sale">For sale</option></select></label>
      <fieldset class="f-checks">
        <legend class="sr-only">Show only</legend>
        <label class="chk"><input type="checkbox" name="dev" value="1"><span>Developed by Collett</span></label>
        <label class="chk"><input type="checkbox" name="man" value="1"><span>Managed by Collett</span></label>
        <label class="chk"><input type="checkbox" name="uc" value="1"><span>Under construction</span></label>
      </fieldset>
    </form>
    <div class="results-bar">
      <p id="result-count" aria-live="polite"></p>
      <div class="results-tools">
        <button type="button" class="link-btn" id="clear-filters" hidden>Clear filters</button>
        <div class="seg" role="group" aria-label="View">
          <button type="button" data-view="grid" aria-pressed="true">{icon('grid', 'i i-sm')}Grid</button>
          <button type="button" data-view="map" aria-pressed="false">{icon('map', 'i i-sm')}Map</button>
        </div>
      </div>
    </div>
    <div id="view-grid" class="p-grid p-grid-4"></div>
    <div id="view-map" class="map-view" hidden>
      {portfolio_map('map-points')}
      <div class="map-side"><p class="small">Showing properties with a mapped location. Select a dot to open the property.</p><ol id="map-list"></ol></div>
    </div>
    <div class="more-wrap"><button type="button" class="btn btn-ghost" id="load-more" hidden>Show more properties</button></div>
    <noscript><ul class="plain-list">{noscript_list}</ul></noscript>
  </div>
</section>
{cta_band('Don’t see what you need?', 'Our brokers know what’s coming to market before it’s listed. Tell us what you’re looking for.', 'Tell us what you need')}
"""
    page("properties/index.html", "Properties", body, active="properties",
         description="Search Collett's retail, mixed-use, industrial, office and land properties for lease and sale across the Southeast and Southwest.",
         scripts=("properties-data.js", "map.js", "properties.js"))
    for p in PROPS:
        if p["hasPage"]:
            build_property(p)


def build_property(p):
    photos = p["photos"]
    if photos:
        thumbs = ""
        if len(photos) > 1:
            thumbs = '<div class="g-thumbs">' + "".join(
                f'<button type="button" data-i="{i}" aria-label="Show photo {i + 1}"{" aria-current=true" if i == 0 else ""}><img src="{u(ph)}" alt="" loading="lazy" decoding="async"></button>'
                for i, ph in enumerate(photos)
            ) + "</div>"
        gallery = f"""<div class="gallery" data-gallery='{e(json.dumps([u(x) for x in photos]))}'>
      <button type="button" class="g-main" aria-label="Open photo viewer"><img src="{u(photos[0])}" alt="{e(p['name'])}" fetchpriority="high"></button>
      {f'<span class="g-count">{len(photos)} photos</span>' if len(photos) > 1 else ''}
      {thumbs}
    </div>"""
    elif p.get("thumb"):
        gallery = f'<div class="gallery"><div class="g-main"><img src="{u(p["thumb"])}" alt="{e(p["name"])}"></div></div>'
    else:
        gallery = f'<div class="gallery">{placeholder(p, "ph ph-lg")}</div>'

    text = ""
    if p.get("summary") and p["summary"] not in " ".join(p.get("paras", [])):
        text += f'<p class="lead-sm">{e(p["summary"])}</p>'
    text += "".join(f"<p>{e(x)}</p>" for x in p.get("paras", []))
    if p.get("highlights"):
        text += '<h2 class="h-sm">Highlights</h2><ul class="check-list">' + "".join(f"<li>{e(x)}</li>" for x in p["highlights"]) + "</ul>"

    facts = [("Type", TYPE_LABEL[prop_type(p)])]
    if p.get("availability"):
        facts.append(("Availability", p["availability"].replace("For ", "")))
    for k, v in (p.get("facts") or {}).items():
        if k == "Tenants":
            continue
        facts.append((k.replace("Square Footage", "SF"), v))
    if p.get("developed"):
        facts.append(("Developer", "Collett"))
    if p.get("managed"):
        facts.append(("Management", "Collett"))
    facts_html = "".join(f"<div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>" for k, v in facts)
    tenants = (p.get("facts") or {}).get("Tenants")
    tenants_html = f'<h2 class="h-sm">Tenants</h2><p class="tenants">{e(tenants)}</p>' if tenants else ""

    contacts = ""
    for c in p.get("contacts", []):
        t = contact_person(c["name"])
        role = re.sub(r"s$", "", c["role"]) if c["role"] == "Brokers" else c["role"]
        tel = re.sub(r"[^0-9]", "", c["phone"])
        name_html = f'<a href="/team/{t["slug"]}/">{e(t["name"])}</a>' if t else e(c["name"])
        ph = person_photo(t, "avatar avatar-sm") if t else f'<div class="avatar avatar-sm avatar-ph"><span>{e(initials(c["name"]))}</span></div>'
        contacts += f"""<li class="contact">{ph}<div><p class="c-role">{e(role)}</p><p class="c-name">{name_html}</p>
        {f'<p><a href="tel:{tel}">{e(c["phone"])}</a></p>' if c['phone'] else ''}</div></li>"""
    if contacts:
        contacts = f'<h2 class="side-h">Contacts</h2><ul class="contacts">{contacts}</ul>'

    addr = ", ".join(x for x in [p.get("address"), f"{p['city']}, {p['state']}"] if x)
    q = f"{p['lat']},{p['lng']}" if p.get("lat") else addr
    gmap = ""
    if p.get("lat"):
        gmap = f'<div class="mini-map"><iframe title="Map of {e(p["name"])}" src="https://maps.google.com/maps?q={e(q)}&amp;z=14&amp;output=embed" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe></div>'
    directions = "https://www.google.com/maps/search/?api=1&query=" + (q if p.get("lat") else addr.replace(" ", "+"))

    flyer_btn = f'<a class="btn btn-ghost btn-block" href="/contact-us/?property={p["slug"]}&amp;subject=flyer">Request the property flyer</a>' if p.get("flyers") else ""

    nearby = [x for x in PROPS if x is not p and x["state"] == p["state"] and x["hasPage"] and x.get("card")]
    nearby.sort(key=lambda x: (x["city"] != p["city"], x["name"]))
    nearby_html = ""
    if nearby:
        nearby_html = f"""<section class="section section-paper">
  <div class="wrap">
    <div class="sec-head"><div><p class="eyebrow">Nearby</p><h2>More in {e(STATE_NAMES.get(p['state'], p['state']))}.</h2></div>
    <a class="text-link" href="/properties/?state={p['state']}">All {e(p['state'])} properties {icon('arrow')}</a></div>
    <div class="p-grid p-grid-3">{''.join(prop_card(x) for x in nearby[:3])}</div>
  </div>
</section>"""

    body = f"""
<section class="prop-head">
  <div class="wrap">
    <nav class="crumbs" aria-label="Breadcrumb"><ol><li><a href="/">Home</a></li><li><a href="/properties/">Properties</a></li><li><a href="/properties/?state={p['state']}">{e(STATE_NAMES.get(p['state'], p['state']))}</a></li><li aria-current="page">{e(p['name'])}</li></ol></nav>
    <div class="prop-title">
      <div>
        <h1>{e(p['name'])}</h1>
        <p class="p-loc">{icon('pin', 'i i-sm')}{e(addr)}</p>
      </div>
      <div class="tags">{prop_tags(p, 4)}</div>
    </div>
  </div>
</section>
<section class="section section-tight">
  <div class="wrap prop-grid">
    <div class="prop-main">
      {gallery}
      <div class="prose prop-text">{text}{tenants_html}</div>
    </div>
    <aside class="prop-side">
      <div class="side-card">
        <dl class="facts">{facts_html}</dl>
        <a class="btn btn-primary btn-block" href="/contact-us/?property={p['slug']}">Request information {icon('arrow')}</a>
        {flyer_btn}
      </div>
      {f'<div class="side-card">{contacts}</div>' if contacts else ''}
      <div class="side-card">
        {gmap}
        <a class="text-link" href="{e(directions)}" target="_blank" rel="noopener">Get directions {icon('external', 'i i-xs')}</a>
      </div>
    </aside>
  </div>
</section>
{nearby_html}
"""
    desc = p.get("summary") or (p.get("highlights") or [""])[0] or f"{p['name']} in {p['city']}, {p['state']}. A Collett property."
    page(f"properties/{p['slug']}/index.html", f"{p['name']}, {p['city']}, {p['state']}", body, active="properties",
         description=desc[:300], og_image=photos[0] if photos else p.get("thumb"),
         scripts=("gallery.js",))


def build_team():
    ordered = team_sorted()
    leaders = [t for t in ordered if team_group(t) == "Leadership"]
    chips = '<button type="button" class="chip" data-group="" aria-pressed="true">Everyone</button>' + "".join(
        f'<button type="button" class="chip" data-group="{e(g)}" aria-pressed="false">{e(g)}</button>' for g in GROUPS
    )
    office_opts = "".join(f'<option value="{e(o["teamOffice"])}">{e(o["name"])}</option>' for o in SITE["offices"])
    body = f"""
{page_head('Team', 'The people of Collett.', f'{len(TEAM)} professionals across Charlotte, Greenville, Dallas and Morganton, working together on every project.', [('Home', '/'), ('Team', None)])}
<section class="section section-tight">
  <div class="wrap">
    <div class="team-filters" id="team-filters">
      <div class="chips" role="group" aria-label="Filter by group">{chips}</div>
      <div class="team-tools">
        <label><span class="sr-only">Office</span><select name="office"><option value="">All offices</option>{office_opts}</select></label>
        <label class="f-search"><span class="sr-only">Search the team</span>{icon('search')}<input type="search" name="q" placeholder="Search by name or title"></label>
      </div>
    </div>
    <p class="small" id="team-count" aria-live="polite"></p>
    <div class="people-grid" id="people">{''.join(person_card(t) for t in ordered)}</div>
    <p class="empty" id="team-empty" hidden>No one matches those filters.</p>
  </div>
</section>
{cta_band('Want to join the team?', 'We are always glad to hear from talented real estate professionals.', 'Get in touch', '/contact-us/?subject=careers')}
"""
    page("team/index.html", "Team", body, active="team",
         description="Meet the Collett team: partners, developers, brokers, property managers and accounting professionals in Charlotte, Greenville, Dallas and Morganton.",
         scripts=("team.js",))
    for t in TEAM:
        build_person(t)


def bio_html(blocks):
    out = []
    for b in blocks:
        if "h" in b:
            out.append(f'<h2 class="h-sm">{e(b["h"])}</h2>')
        elif "list" in b:
            out.append("<ul>" + "".join(f"<li>{e(x)}</li>" for x in b["list"]) + "</ul>")
        else:
            out.append(f"<p>{e(b['p'])}</p>")
    return "".join(out)


def build_person(t):
    tel = re.sub(r"[^0-9]", "", t["phone"])
    office = OFFICE_BY_TEAM.get(t["office"])
    props = props_for_person(t)
    props_html = ""
    if props:
        items = "".join(
            f'<li><a href="/properties/{p["slug"]}/">{e(p["name"])}</a><span>{e(p["city"])}, {e(p["state"])} · {e(re.sub("s$", "", r) if r == "Brokers" else r)}</span></li>'
            for p, r in sorted(props, key=lambda x: x[0]["name"])
        )
        props_html = f'<div class="side-card"><h2 class="side-h">Properties ({len(props)})</h2><ul class="prop-list">{items}</ul></div>'
    bio = bio_html(t["bio"]) or f"<p>{e(t['name'])} is part of Collett’s {e(office['name'] if office else t['office'])} team.</p>"
    group = team_group(t)
    peers = [x for x in team_sorted() if x is not t and team_group(x) == group][:4]
    body = f"""
<section class="person-head">
  <div class="wrap person-grid">
    <div class="person-photo">{person_photo(t, 'avatar avatar-xl', lazy=False)}</div>
    <div>
      <nav class="crumbs" aria-label="Breadcrumb"><ol><li><a href="/">Home</a></li><li><a href="/team/">Team</a></li><li aria-current="page">{e(t['name'])}</li></ol></nav>
      <p class="eyebrow">{e(group)}</p>
      <h1>{e(t['name'])}</h1>
      <p class="lead">{e(t['title'])}</p>
      <ul class="person-meta">
        {f'<li><a href="tel:{tel}">{icon("phone", "i i-sm")}{e(t["phone"])}</a></li>' if tel else ''}
        <li>{icon('pin', 'i i-sm')}{e(office['name'] + ' office' if office else t['office'])}</li>
      </ul>
    </div>
  </div>
</section>
<section class="section section-tight">
  <div class="wrap person-body">
    <div class="prose">{bio}</div>
    <aside>
      {props_html}
      {f'<div class="side-card">{office_block(office)}</div>' if office else ''}
    </aside>
  </div>
</section>
{f'''<section class="section section-paper"><div class="wrap"><div class="sec-head"><div><p class="eyebrow">{e(group)}</p><h2>Colleagues.</h2></div><a class="text-link" href="/team/">Full team {icon('arrow')}</a></div><div class="people-grid">{''.join(person_card(x) for x in peers)}</div></div></section>''' if peers else ''}
"""
    first = next((b["p"] for b in t["bio"] if "p" in b), "")
    desc = first[:300] if first else f"{t['name']}, {t['title']} at Collett."
    page(f"team/{t['slug']}/index.html", f"{t['name']}, {t['title']}" if t["title"] else t["name"], body, active="team",
         description=desc, og_image=t.get("photo"))


def build_press():
    years = sorted({a["date"][:4] for a in PRESS}, reverse=True)
    chips = '<button type="button" class="chip" data-year="" aria-pressed="true">All</button>' + "".join(
        f'<button type="button" class="chip" data-year="{y}" aria-pressed="false">{y}</button>' for y in years
    )
    top = PRESS[:3]
    rest = PRESS[3:]
    lead = top[0]
    lead_img = f'<div class="n-media"><img src="{u(lead["images"][0])}" alt="" decoding="async"></div>' if lead.get("images") else ""
    lead_html = f"""<article class="n-lead">
  {lead_img}
  <div class="n-body">
    <time datetime="{lead['date']}">{fmt_date(lead['date'])}</time>
    <h2><a href="/press/{lead['slug']}/">{e(lead['title'])}</a></h2>
    <p>{e(excerpt(lead['body'], 260))}</p>
    <a class="text-link" href="/press/{lead['slug']}/">Read more {icon('arrow')}</a>
  </div>
</article>"""
    rows = "".join(
        f"""<li class="n-row" data-year="{a['date'][:4]}"><time datetime="{a['date']}">{fmt_date(a['date'], 'short')}</time>
      <div><h3><a href="/press/{a['slug']}/">{e(a['title'])}</a></h3><p>{e(excerpt(a['body'], 160))}</p></div></li>"""
        for a in rest
    )
    body = f"""
{page_head('News', 'News and announcements.', 'New developments, leasing activity, awards and people at Collett.', [('Home', '/'), ('News', None)])}
<section class="section section-tight">
  <div class="wrap">
    <div class="news-top">{lead_html}<div class="news-side">{''.join(news_card(a, False) for a in top[1:])}</div></div>
  </div>
</section>
<section class="section section-paper">
  <div class="wrap">
    <div class="sec-head"><div><p class="eyebrow">Archive</p><h2>Every story since 2008.</h2></div></div>
    <div class="chips chips-scroll" id="year-chips" role="group" aria-label="Filter by year">{chips}</div>
    <ol class="n-list" id="news-list">{rows}</ol>
    <div class="more-wrap"><button type="button" class="btn btn-ghost" id="news-more" hidden>Show older news</button></div>
  </div>
</section>
"""
    page("press/index.html", "News", body, active="press",
         description="News and announcements from Collett: new developments, leasing activity, awards and team news.",
         scripts=("news.js",))
    for i, a in enumerate(PRESS):
        build_article(a, PRESS[i - 1] if i > 0 else None, PRESS[i + 1] if i + 1 < len(PRESS) else None)


def build_article(a, newer, older):
    imgs = "".join(f'<figure><img src="{u(x)}" alt="" loading="lazy" decoding="async"></figure>' for x in a.get("images", []))
    nav = '<nav class="art-nav" aria-label="More news">'
    nav += f'<a class="prev" href="/press/{older["slug"]}/"><span>{icon("left", "i i-sm")} Older</span>{e(older["title"])}</a>' if older else "<span></span>"
    nav += f'<a class="next" href="/press/{newer["slug"]}/"><span>Newer {icon("right", "i i-sm")}</span>{e(newer["title"])}</a>' if newer else "<span></span>"
    nav += "</nav>"
    body = f"""
<article class="article">
  <header class="art-head">
    <div class="wrap wrap-narrow">
      <nav class="crumbs" aria-label="Breadcrumb"><ol><li><a href="/">Home</a></li><li><a href="/press/">News</a></li><li aria-current="page">{e(a['title'][:60])}</li></ol></nav>
      <time datetime="{a['date']}">{fmt_date(a['date'])}</time>
      <h1>{e(a['title'])}</h1>
    </div>
  </header>
  <div class="wrap wrap-narrow">
    <div class="prose art-body">{a['body'] or '<p></p>'}</div>
    {f'<div class="art-imgs">{imgs}</div>' if imgs else ''}
    {nav}
  </div>
</article>
"""
    page(f"press/{a['slug']}/index.html", a["title"], body, active="press",
         description=excerpt(a["body"], 200) or a["title"], og_image=(a.get("images") or [None])[0])


def build_contact():
    offices = "".join(office_block(o) for o in SITE["offices"])
    cf = SITE["contactForm"]
    subjects = ["General inquiry", "Leasing", "Property for sale", "Property management", "Tenant representation", "Development", "Property flyer", "Careers", "Media"]
    subj_opts = "".join(f"<option>{e(s)}</option>" for s in subjects)
    prop_opts = "".join(f'<option value="{p["slug"]}">{e(p["name"])} ({e(p["city"])}, {e(p["state"])})</option>' for p in sorted(PROPS, key=lambda p: p["name"].lower()) if p["hasPage"])
    ph = SITE["phones"]
    body = f"""
{page_head('Contact', 'Let’s talk.', 'Questions about a property, a site or a project? Send us a note and the right person on our team will follow up.', [('Home', '/'), ('Contact', None)])}
<section class="section section-tight">
  <div class="wrap contact-grid">
    <form class="contact-form" id="contact-form" data-endpoint="{e(cf.get('endpoint', ''))}" data-email="{e(cf.get('email', ''))}" novalidate>
      <div class="form-row">
        <label><span class="lbl">First name<span class="req" aria-hidden="true">*</span></span><input name="first_name" required autocomplete="given-name"></label>
        <label><span class="lbl">Last name<span class="req" aria-hidden="true">*</span></span><input name="last_name" required autocomplete="family-name"></label>
      </div>
      <div class="form-row">
        <label><span class="lbl">Email<span class="req" aria-hidden="true">*</span></span><input type="email" name="email" required autocomplete="email"></label>
        <label><span class="lbl">Phone</span><input type="tel" name="phone" autocomplete="tel"></label>
      </div>
      <label><span class="lbl">Company</span><input name="company" autocomplete="organization"></label>
      <div class="form-row">
        <label><span class="lbl">Subject<span class="req" aria-hidden="true">*</span></span><select name="subject" required>{subj_opts}</select></label>
        <label><span class="lbl">Property (optional)</span><select name="property"><option value="">None</option>{prop_opts}</select></label>
      </div>
      <label><span class="lbl">Message<span class="req" aria-hidden="true">*</span></span><textarea name="message" rows="6" required></textarea></label>
      <label class="hp" aria-hidden="true">Leave this empty<input name="website" tabindex="-1" autocomplete="off"></label>
      <label class="chk"><input type="checkbox" name="opt_in" value="yes"><span>Send me occasional news and property updates from Collett.</span></label>
      <div class="form-foot">
        <button class="btn btn-primary" type="submit">Send message {icon('arrow')}</button>
        <p class="small">* Required. See our <a href="/privacy-policy/">privacy policy</a>.</p>
      </div>
      <div class="form-status" role="status" aria-live="polite" hidden></div>
    </form>
    <aside class="contact-side">
      <div class="side-card side-card-navy">
        <h2 class="side-h">Tenants</h2>
        <ul class="t-help">
          <li>{icon('wrench')}<div><b>Maintenance and management</b><span>Non-emergency requests and general questions</span><a href="tel:{ph['maintenance'].replace('.', '')}">{e(ph['maintenance'])}</a></div></li>
          <li>{icon('alert')}<div><b>After-hours emergency</b><span>Available 24/7 for urgent maintenance</span><a href="tel:{ph['emergency'].replace('.', '')}">{e(ph['emergency'])}</a></div></li>
          <li>{icon('key')}<div><b>Tenant portal</b><span>Payments, requests and documents</span><a href="{e(SITE['tenantPortal'])}" target="_blank" rel="noopener">Open the portal</a></div></li>
        </ul>
      </div>
      <div class="side-card">
        <h2 class="side-h">Leasing questions</h2>
        <p>Call <a href="tel:{ph['leasing'].replace('.', '')}">{e(ph['leasing'])}</a> or browse <a href="/properties/?avail=any">available properties</a>.</p>
      </div>
    </aside>
  </div>
</section>
<section class="section section-paper">
  <div class="wrap">
    <div class="sec-head"><div><p class="eyebrow">Offices</p><h2>Visit us.</h2></div></div>
    <div class="office-grid">{offices}</div>
  </div>
</section>
"""
    page("contact-us/index.html", "Contact", body, active="contact",
         description="Contact Collett in Charlotte, Greenville, Dallas or Morganton. Leasing, property management, development and tenant representation inquiries.",
         scripts=("properties-data.js", "contact.js"))


def build_legal():
    legal = load("legal.json")
    for key, title in (("legal", "Legal"), ("privacy-policy", "Privacy Policy")):
        body = f"""
{page_head(title, e(title), '', [('Home', '/'), (title, None)], cls='page-head-tight')}
<section class="section section-tight"><div class="wrap wrap-narrow prose legal">{legal[key]}</div></section>
"""
        page(f"{key}/index.html", title, body)


def build_404():
    body = f"""
{page_head('Page not found', 'We couldn’t find that page.', 'It may have moved when we launched our new website. Try one of these instead:')}
<section class="section section-tight"><div class="wrap"><ul class="link-list link-list-lg">
<li><a href="/properties/">Search properties</a></li><li><a href="/team/">Find a team member</a></li><li><a href="/press/">Read the news</a></li><li><a href="/contact-us/">Contact us</a></li></ul></div></section>
"""
    page("404.html", "Page not found", body, canonical="404.html")


def build_misc():
    redirect_page("home/index.html", "/", "Home")
    redirect_page("tenant-portal/index.html", SITE["tenantPortal"], "Tenant Portal")
    urls = ["", "about-us/", "services/", "properties/", "team/", "press/", "contact-us/", "legal/", "privacy-policy/"]
    urls += [s["slug"] + "/" for s in SITE["services"]]
    urls += [f"properties/{p['slug']}/" for p in PROPS if p["hasPage"]]
    urls += [f"team/{t['slug']}/" for t in TEAM]
    urls += [f"press/{a['slug']}/" for a in PRESS]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sm += "".join(f"  <url><loc>{SITE['domain']}/{x}</loc></url>\n" for x in urls)
    sm += "</urlset>\n"
    write("sitemap.xml", sm)
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE['domain']}/sitemap.xml\n")


def clean_generated():
    """Remove previously generated HTML so deleted content doesn't linger."""
    keep_top = {"assets", "_redirects", "_headers"}
    for name in os.listdir(OUT):
        if name in keep_top:
            continue
        full = os.path.join(OUT, name)
        if os.path.isdir(full):
            shutil.rmtree(full)
        elif name.endswith((".html", ".xml", ".txt")):
            os.remove(full)
    for f in ("assets/js/properties-data.js", "assets/img/us-map.svg"):
        if os.path.exists(os.path.join(OUT, f)):
            os.remove(os.path.join(OUT, f))


def main():
    os.makedirs(OUT, exist_ok=True)
    clean_generated()
    map_svg_file()
    write_props_js()
    build_home()
    build_about()
    build_services()
    build_properties()
    build_team()
    build_press()
    build_contact()
    build_legal()
    build_404()
    build_misc()
    n = sum(len([f for f in fs if f.endswith(".html")]) for _, _, fs in os.walk(OUT))
    print(f"Built {n} pages into public/")


if __name__ == "__main__":
    main()
