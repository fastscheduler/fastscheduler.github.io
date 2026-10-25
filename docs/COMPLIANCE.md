# Site compliance audit

Audited 5 October 2026. Covers the static site served from
`https://fastscheduler.github.io/`. This is the deployed site
only; the Telegram bot has its own data flows, covered by the Privacy Policy.

## Third-party resource loading: none

**No visitor IP is shared with any third party by the website.**

The concern that prompted this audit — that Google Fonts is loaded from
`fonts.googleapis.com`, which sends the visitor's IP address to Google on every
page view without consent (the reason for LG Munich 20 O 17493/20) — **does not
apply to this site.** Google Fonts has never been present here.

Evidence, strongest last:

| Check | Result |
|---|---|
| `fonts.googleapis.com` / `fonts.gstatic.com` in any tracked file | 0 |
| The same, across every commit on every branch (`git log --all -S`) | 0 |
| External `<script src="http...">` | 0 |
| Remote `<img src="http...">` | 0 |
| `<iframe>` | 0 |
| `@import` in CSS | 0 |
| `url(http...)` in CSS | 0 |
| **Live network capture of a help page** | **all 16 requests to this origin** |

The webfonts are self-hosted woff2 files under `/fonts/`, declared in
`styles/main.css` with `@font-face`:

- `Space Grotesk` — 22,288 bytes
- `Inter` — 48,256 bytes

Both are under the SIL Open Font License, which permits self-hosting (and
self-hosting is what the OFL encourages — it is the whole point of the licence
versus embedding a Google CDN URL).

The only external hosts appearing anywhere in the HTML are:

- `fastscheduler.github.io` — `rel="canonical"`, `og:url`, JSON-LD `@id`.
  These are metadata values that are never fetched.
- `schema.org` / `www.w3.org` — XML namespace identifiers in JSON-LD and inline
  SVG. Never fetched.
- `t.me` — outbound links to the bot. No data flows until the visitor clicks.

## Analytics and tracking: none

No Google Analytics, gtag, Yandex Metrika, Plausible, Microsoft Clarity,
Hotjar, Facebook pixel, Matomo, Segment or Mixpanel anywhere in the site.

`track()` in `scripts/main.js` writes click events to `localStorage.site_clicks`
and never transmits them — which is exactly what the Privacy Policy says.

## Cookies and local storage

Only strictly-necessary storage is used, which under ePrivacy Art. 5(3) does
not require consent. The banner is therefore informational rather than a gate:
nothing is enabled on acceptance that was disabled on refusal.

The one cookie, `consent=accepted|declined`, is written only when the visitor
answers the banner. `localStorage` holds theme, language, font size, reader
settings and click history. The Privacy Policy contains a full itemised
inventory of each key.

## GDPR Article 13 — verified present in the Privacy Policy

Controller identity, contact address, lawful basis, retention periods,
recipients, international transfers, data-subject rights, the right to complain
to a supervisory authority, and automated decision-making / profiling.

## EU consumer law

- Terms §3 Eligibility sets a minimum age of 13 (or the higher minimum age of
  digital consent in the user's country).
- Terms §19 Governing Law and Disputes.
- Refund Policy carries an explicit **EU/UK cooling-off / right of withdrawal**
  clause, correctly noting that for digitally supplied services the 14-day right
  generally does not apply once performance has begun with prior explicit
  consent.
- Terms §20 sets out how changes are announced and when they take effect.

## Accessibility (European Accessibility Act, Directive (EU) 2019/882)

The EAA has applied to e-commerce services since 28 June 2025. Verified:

- `<html lang>` present on all 676 pages.
- 150 `<img>` elements, **0** missing an `alt` attribute. 75 use `alt=""`,
  which is the correct treatment for decorative images.
- Search inputs have accessible names.
- Buttons have `aria-label`; the 15 without an explicit `type=` are all
  outside any `<form>`, so their implicit `submit` type is inert.

## Re-verify after any change

```bash
# No third-party resource may be introduced.
grep -rniE "fonts\.(googleapis|gstatic)\.com" website/ --include='*.html' --include='*.css'
grep -rhoE '<(script|img)[^>]+src="https?://[^"]+"' website/ --include='*.html'
grep -rhoE '@import|url\(\s*["'"'"']?https?://' website/styles/*.css
grep -rniE "gtag|googletagmanager|yandex|metrika|hotjar|clarity\.ms|facebook\.net|plausible\.io|matomo|segment\.com|mixpanel" website/ --include='*.html' --include='*.js'
```

All four must return nothing. The greps catch a source-level regression; the
decisive check is a **live network capture** on the deployed site (Preview →
Network), where every request should be to `fastscheduler.github.io`.