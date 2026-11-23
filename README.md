# Collett: website

The new website for **www.collettre.com**. It is a static site (plain HTML, CSS and JavaScript) with no server code and no database, so it can be hosted on any static host: Netlify, Cloudflare Pages, Vercel, GitHub Pages, Amazon S3, or an ordinary web server (Apache, Nginx, IIS).

The content (properties, team, news, services and offices) was carried over from the existing collettre.com in November 2026.

## What's where

```
public/                 ← the website. This folder is what gets hosted.
  index.html            home
  about-us/             about, leadership, rankings, offices
  services/             services overview
  development/ management/ tenant-representation/ brokerage/   one page per service
  properties/           searchable property list + map
  properties/<name>/    one page per property (196)
  team/                 filterable team list
  team/<name>/          one page per person (48)
  press/                news archive
  press/<name>/         one page per article (146)
  contact-us/  legal/  privacy-policy/  404.html
  assets/css/site.css   all styles
  assets/js/            menus, property search, map, gallery, team/news filters, contact form
  assets/img/           logos, property photos, headshots, client logos, news images
  _redirects            redirects for Netlify / Cloudflare Pages
  sitemap.xml, robots.txt

content/                ← the content the pages are built from
  site.json             company info, offices, phone numbers, service text, homepage picks
  properties.json       every property (name, address, type, availability, photos, contacts…)
  team.json             every team member (title, office, phone, photo, bio)
  press.json            news articles
  clients.json          tenant-representation client logos
  legal.json            legal notice and privacy policy text
  usmap.json            map shapes and property map positions

tools/build.py          turns content/ into the pages in public/
```

The page addresses match the old site (for example `/properties/lewis-crossing-1260-s-amity-road-conway-ar-72032`, `/team/john-collett-charlotte`, `/press/cheers-to-13-years-in-greenville-sc`), so existing links and search results keep working after the switch.

## Updating content

1. Edit the relevant file in `content/` (any text editor works; keep the JSON format intact).
2. Put any new photos in `public/assets/img/…` and reference them by path, e.g. `assets/img/team/jane-doe-charlotte.jpg`.
3. Rebuild the pages:

   ```sh
   python3 tools/build.py
   ```

   Requires Python 3.8 or newer; nothing to install.
4. Commit and push. If the host is connected to this repository it will publish automatically.

Common edits:

- **Add or update a property:** add or edit an entry in `content/properties.json`. Set `"hasPage": true` to give it its own page. `availability` is `"For Lease"`, `"For Sale"`, `"For Sale or Lease"` or `null`. `types` is a list containing `Retail`, `Industrial`, `Office`, `Land Listings` or `Other`. `card` is the image used on property cards (640 px wide is plenty) and `photos` is the gallery. A new property only shows on the map once its map position is added to `content/usmap.json` (ask a developer, or leave it off the map).
- **Feature different properties on the homepage:** change `home.featured` (property slugs, first one is the large feature) and `home.heroPhotos` in `content/site.json`.
- **Team changes:** edit `content/team.json`. A person's group on the Team page (Leadership, Development, Brokerage, Management, Accounting & Administration) is worked out from their title.
- **News:** add an entry at the top of `content/press.json` with a `date` (YYYY-MM-DD), `title`, `body` (simple HTML: `<p>`, `<a>`, `<strong>`, `<ul>`) and optional `images`.
- **Phone numbers, offices, tenant portal link:** `content/site.json`.

## Contact form setup (needed before launch)

Static sites can't send email by themselves. In `content/site.json` under `contactForm`, choose one:

- **`endpoint`** (recommended): the URL of a form service such as Formspree, Basin, Getform or Netlify Forms. Submissions are emailed to whoever you choose in that service.
- **`email`**: an address such as `info@collettre.com`. The visitor's own email app opens with the message filled in.

Until one is set, the form asks visitors to call 704.206.8300. Rebuild after changing it.

## Local preview

```sh
cd public
python3 -m http.server 8000
# open http://localhost:8000
```

Page links start with `/`, so open the site through a local server rather than by double-clicking the files.

## Deploying

1. Point the host at the **`public`** folder:
   - Netlify / Cloudflare Pages / Vercel: connect this repository, leave the build command empty, and set the publish/output directory to `public`.
   - A regular web server: copy the contents of `public/` to the web root.
2. Add `collettre.com` and `www.collettre.com` as custom domains and enable HTTPS.
3. Update DNS to the values the host gives you. Keep the current site running until the new one is confirmed live.

### Redirects

`public/_redirects` handles the few old addresses that changed (`/home`, `/tenant-portal`, `/collett-capital`, `/properties_csv.html`) on Netlify and Cloudflare Pages. Small redirect pages are also generated for `/home`, `/tenant-portal` and `/collett-capital`, so those work on any host.

### Property flyers

The old site hosts about 170 property flyer PDFs (roughly 700 MB) under `collettre.com/images/Properties/…`. They are **not** in this repository because of their size. Property pages offer a "Request the property flyer" button instead, and each property's original flyer address is kept in `content/properties.json` (`flyers[].source`). Before the old site is switched off, decide whether to:
- host the flyers somewhere (e.g. SharePoint, Dropbox or a storage bucket) and add links, or
- keep the request-a-flyer flow.

Flyer links already sent to clients point at the old site and will stop working once it is turned off.

## External services the pages load

- Fonts: Google Fonts (Fraunces, Figtree)
- Property pages: an embedded Google Map (no API key needed)

Everything else is served from this site.
