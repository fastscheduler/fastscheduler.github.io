# SEO report — fastscheduler.github.io

Date: 2026-10-04 · 676 HTML pages (408 English + 268 Russian) · audited with `tools/seo_audit.py`, `tools/crawl_graph.py`, `tools/seo_meta.py`, `tools/seo_ld.py`, `tools/ru_coverage.py`, `tools/build_ru.py`

## The short answer

Exact-phrase searches did not surface the site because **only the homepage was indexed**. `site:fastscheduler.github.io` returned exactly one result out of 408 pages. The cause was not content quality, not titles, not robots.txt, not server response codes — every page returned 200 and robots.txt allowed everything.

`help.html` is a hash-router single-page app. Every category, article, breadcrumb and pager link on it is `href="#/a/<id>"`. **A crawler cannot follow URL fragments.** Measured with `tools/crawl_graph.py`:

| | before | after |
|---|---|---|
| pages reachable from the homepage by real `<a href>` + hreflang | **81 / 408** | **672 / 676** |
| help pages reachable | **0 / 323** | **323 / 323** |
| Russian pages reachable | n/a (none existed) | **268 / 268** |
| max click depth | 2 (blog only) | 3 |

The entire help centre — 308 articles and 24 topic hubs, i.e. the bulk of the site's indexable text — was unreachable from any page on the site. It existed only in `sitemap.xml`. The blog (76 pages) was reachable, which is why the homepage and blog ranked and nothing else did.

**Fix:** `build_help.py` now emits a crawlable index — every topic and every article behind a real `href` — at the foot of `help.html` ("Every help article, by topic"). 323 real links, max depth 2 from the homepage.

## Also fixed

| Issue | before | after |
|---|---|---|
| titles longer than 65 chars (Google rewrites these, losing the matched phrase) | 150 | **0** |
| duplicate page titles | 24 | **0** |
| meta descriptions outside 70–160 chars | 142 | **1** |
| duplicate meta descriptions | 5 | **0** |
| images with `alt=""` | 76 | **1** |
| pages with no JSON-LD | 7 | **0** (4 are `noindex`, where it is correct to omit) |
| duplicate canonicals | 3 | **0** (all 3 are `noindex` archives — correct) |
| `sitemap.xml` entries whose `lastmod` moved on every rebuild | 328 | **0** — the sitemap is now byte-identical across rebuilds |
| legal pages with no structured data | 3 | **0** (`WebPage` + `BreadcrumbList`, real `dateModified` from git) |

Details worth knowing:

- **Titles** (`fit_title`, in `build_help.py`, shared by all three builders). One-word articles produced `"Cloud — Fast Scheduler Help"` — 27 characters, and the same string as another article in a different category. Category landing articles are now `"{Title} Overview — …"`, one-word titles get their category, and anything still over 62 characters is trimmed on a word boundary with the brand suffix preserved.
- **Descriptions** (`smart_desc`). The old build sliced raw article HTML at exactly 160 characters, so snippets ended mid-word: *"…The basic flow 1. Tap S"*. `smart_desc` keeps whole sentences, extends toward the 70-character floor, and never falls back to a bare title — eleven category articles were shipping `"Backup"` as a 6-character snippet. Snippets now come from the article body, or from the FAQ questions for the ten articles that have no prose.
- **False structured data.** `index.html` advertised a fabricated `aggregateRating` of 4.9 from 480 ratings, and priced Premium at $9.99/$26.97/$51.55/$99.50. Real prices, from `PREMIUM_PRICE_MONTHLY_CENTS = 683` and the 10/13/17% term discounts in [config.py](src/core/config.py#L308), are $6.83 / $18.44 / $35.65 / $68.03. The rating was removed because it was not real, not because ratings are unhelpful.
- **`lastmod` stability.** 328 of 404 sitemap entries (home, `help.html`, 24 hubs, 3 legal pages, 299 help articles) are dated from a first-seen registry in `site_dates.json` instead of `BUILD_DATE`. They read `2026-10-04` today because that is when the registry first saw them — what changed is that they no longer advance with every rebuild. Two consecutive builds now produce a byte-identical `sitemap.xml`.
- **`help.html` had 335 `<h1>` tags and 102 `FAQPage` blocks in the body** (92 KB). One FAQPage per URL is the correct shape; 100 on one URL read as structured-data spam. The hub now declares `CollectionPage` + `ItemList` in `<head>`; each article page carries its own `FAQPage`.
- **Legal dates.** `build_site.py` stamped `Updated {today}` on every rebuild, claiming the policies were revised daily. It now reads the last commit date of `docs/<policy>.md`.
- **Russian hreflang removed.** `index.html` advertised `ru`/`en`/`x-default` alternates for a translation that only exists client-side — `?lang=ru` never resolved to distinct content, so the hreflang cluster told Google two URLs were the same page. Removed until real `/ru/` pages exist.

## The homepage title was rendering as the string `undefined`

Found while fixing "why does Google show *Schedule Telegram Channel Posts on Autopilot* and drop the brand from the link text". The `<title>` in the served HTML was fine. It was being destroyed at runtime.

`scripts/lang.js` holds the homepage metadata as a nested pair and reads it on every language switch:

```js
var META = { title: { en: '…', ru: '…' }, desc: { en: '…', ru: '…' } };
…
document.title = ru ? META.title.ru : META.title.en;
md.setAttribute('content', ru ? META.desc.ru : META.desc.en);
```

`scripts/ru-chrome.js` exports the same concept as a **flat** object of Russian strings only:

```js
META: { title: 'Fast Scheduler — автопланирование …', desc: '…' }
```

and `lang.js` merged it with a whole-object assignment:

```js
if (window.FS_RU_CHROME.META) META = window.FS_RU_CHROME.META;
```

So `META.title.en` became `undefined` and `document.title` was assigned the **string** `"undefined"` on every homepage load — in both languages, since `META.title.ru` was equally gone. The same happened to the `<meta name="description">`, replacing the audited sentence with a 236-character one that no audit had ever looked at.

This is invisible to a static audit (the HTML on disk is correct) and to a human looking at the tab until they notice the title bar. Googlebot renders JavaScript, so what the crawler indexed was the broken value.

**Fix:** the merge copies only the Russian half, so the shape mismatch is impossible:

```js
if (window.FS_RU_CHROME.META) {
  var rm = window.FS_RU_CHROME.META;
  if (rm.title) META.title.ru = typeof rm.title === 'string' ? rm.title : rm.title.ru;
  if (rm.desc)  META.desc.ru  = typeof rm.desc  === 'string' ? rm.desc  : rm.desc.ru;
}
```

Verified in a real browser after the fix: `document.title` = `Fast Scheduler — Telegram Channel Post Scheduler` (EN) and `Fast Scheduler — Планировщик постов для Telegram-каналов` (RU); meta description 153 (EN) / 162 (RU) characters.

Lesson: **a static audit cannot see what your own JavaScript does to `<title>` and `<meta>` after load.** Anything that rewrites head metadata at runtime has to be checked in a browser, and `tools/seo_audit.py` reads the file on disk, so it will happily pass a page whose rendered title is `undefined`.

### Title now leads with the brand

`Fast Scheduler — Schedule Telegram Channel Posts on Autopilot` (61 chars) → **`Fast Scheduler — Telegram Channel Post Scheduler`** (48 chars), mirrored into `og:title` and `twitter:title`. The brand already led, so this is not a reorder — it is a shortening. Long titles are what Google rewrites, and when it rewrites a title it often promotes the descriptive half and pushes the brand into the snippet. 48 characters fits the SERP line untruncated and keeps the phrase people actually type ("telegram post scheduler") in the same 48 characters.

**Google can still rewrite the title.** That is a ranking decision, not a bug, and it cannot be switched off. What can be controlled: the title being present, brand-first, short, and matching what the page is about — and the rendered DOM no longer saying `undefined`.

### Fabricated testimonials removed

`index.html` shipped three customer quotes under the heading "Channels that stopped posting by hand" — Milena (19K subscriber news channel), Artem (shop drops channel), Sofia (podcast & community) — each with a five-star `aria-label="Rated 5 out of 5"`. The people were invented. Removed along with: both `#reviews` nav links, hotkey `4` (Pricing and FAQ renumbered 4 and 5 so the rail stays contiguous), the dead `.quotes`/`.quote`/`.stars`/`.ava` rules in `index.html`, `styles/main.css` and `styles/lang.css`, and the Russian translation entries for all of it in `lang.js` and `ru-chrome.js`.

The earlier `aggregateRating` removal was the same class of problem in structured-data form; this was the same problem in the visible page.

**Three more copies were still live.** `_hero_phone_backup/` sits at the published site root, so `index_cb1.html`, `index_cb6.html` and `index_cb8.html` were reachable URLs, each carrying all three fabricated quotes, the old title, and `robots=index, follow` with a canonical pointing at an unrelated domain (`fastestschedule.com`) — indexable stale duplicates of the homepage. The quotes and old title are stripped and they are now `noindex, nofollow`. The files are kept: they are a design backup, and deleting someone's backup is not the SEO fix's call. If you do not need them, deleting the directory removes three dead URLs entirely.

**Why no audit caught any of this:** `sync_root.py` and `sync_audit.py` only walk the `PUB` allowlist, `crawl_graph.py` and `seo_audit.py` only walk `website/`, and `sitemap.xml` never listed them. Root-level files outside `PUB` are invisible to every check in this repo — they are still served, they are still indexable, and nothing here will ever mention them again.

## Still open

### 1. help.html is 3.0 MB (and blog/index.html is 894 KB)

`help.html` carries the corpus roughly four times over: 308 rendered article bodies, a 727 KB `<script id="helpData">` JSON blob for client-side search, the sidebar payload, and 47 KB of JSON-LD. It gzips to ~460 KB, which is under Google's 5 MB limit, so this is a crawl-efficiency and Core Web Vitals problem rather than a hard blocker.

The fix is architectural: move `helpData` to a separate `.json` the SPA fetches, and render article bodies on demand. That is a rewrite of the help SPA's data path, not a metadata change, so it is not done here.

### 2. Two blog posts cover the same announcement

`blog/a/news-october-legal-refresh.html` (1,044 chars) and `blog/a/october-2026-legal-refresh.html` (2,813 chars) both cover the October 2026 legal rewrite. They now have distinct descriptions, but they are still two indexable URLs for one subject. Consolidating means picking which URL survives and 301-ing the other — that is a link-equity decision, so it is left to you.

### 3. Russian pages — now built

The Russian layer used to be client-side only: `scripts/lang.js` + `ru-content.js` swapped strings after load from `localStorage`. A crawler is not obliged to run JavaScript, so none of that text was indexable, and the `hreflang` block that used to sit on `index.html` pointed at a `?lang=ru` URL that never resolved to distinct content.

The Russian *source text* was already in the repo — `tools/ru_batches/help_*.py` holds full Russian help articles (title, body, FAQ) and `docs/ru/*.md` holds the Russian legal policies. `tools/build_ru.py` turns that into real documents:

| | count |
|---|---|
| `/ru/help/a/<id>.html` | **265** of 299 built help articles (88.6%) |
| `/ru/legal/*.html` | **3** (privacy, terms, refund) |
| English pages given the matching hreflang cluster | 268 |
| `/ru/` URLs added to `sitemap.xml` | 268 |

Each Russian page is built with `<html lang="ru">`, a self-referencing canonical on the `/ru/` URL, a Russian title and description, `TechArticle` + `BreadcrumbList` JSON-LD with `inLanguage: ru` and `translationOfWork`, a `ru`/`en`/`x-default` hreflang cluster, and a visible "Читать на английском" link to the original. The English original gets the mirror cluster. `tools/crawl_graph.py` follows `rel="alternate"` and confirms all 268 are reachable from the homepage at depth 3.

A page is only generated where Russian source text exists. Emitting a `/ru/` page that is 20% translated is a thin duplicate of the English original and would make the cluster worse than useless, so the generator refuses to pad. The **34 help articles still missing** Russian are listed by `python tools/build_ru.py` on every run — the highest-value next translation batch is the `qa_*` series, which currently covers none of them.

`lang.js` was changed so that a visitor with no stored preference follows the language the server actually served; without that, opening a `/ru/` URL flipped the page back to English. The `?v=` cache-busting constant in `tag_ru_chrome.py` is currently `20261004b4`; it has to be bumped (`python tools/bump_lang_v.py <ver>`) **any time `lang.js` or `ru-chrome.js` changes**, or returning visitors keep running the old script out of cache and the fix appears not to work.

**Still not translated:** the home page, the 75 blog articles, and the 24 help category hubs. `ru-content.js` covers only ~12% of blog and ~19% of help prose, so those need translating before a `/ru/` URL is worth publishing.

### 4. Indexing is not automatic — IndexNow is wired up

The crawl graph is fixed, but crawlers only re-read what they choose to re-crawl. IndexNow (Bing, Yandex, DuckDuckGo and others) lets the site say “these URLs changed, come now” instead of waiting days.

Key: `5817133906fc4ab78b0f19ca52bf8f58`, hosted as a plain text file at the root of the deploy tree:

- `website/5817133906fc4ab78b0f19ca52bf8f58.txt` (source)
- `5817133906fc4ab78b0f19ca52bf8f58.txt` (repo root — this is the one served)

Both are required, and both are in the `PUB` allowlist in `sync_root.py` / `sync_audit.py`. The site is now served from the domain root (`https://fastscheduler.github.io/`), so the key file at the repository root is also the one served at the site root.

**Status: still not delivering — blocked on host verification, not on deployment.** With the key file confirmed served at `https://fastscheduler.github.io/5817133906fc4ab78b0f19ca52bf8f58.txt` (HTTP 200), submissions still come back `403 {"errorCode":"UserForbiddedToAccessSite"}`. Serving the file is necessary but not sufficient: IndexNow also requires the key to be *registered and verified* for the host, and that step lives in a person's IndexNow / Bing Webmaster Tools account. The key is served at the site root (`https://fastscheduler.github.io/<key>.txt` returns 200), so there is no longer a separate apex/subdirectory mismatch to work around. `tools/indexnow.py` still reports an unreachable key separately from the "key not pushed yet" case, since the two need opposite advice.

```bash
python tools/indexnow.py --check   # is the key actually reachable?
python tools/indexnow.py           # submit pages changed vs HEAD
python tools/indexnow.py --all     # submit every sitemap URL
python tools/indexnow.py --dry-run …  # print, send nothing
```

`--changed` is the default and needs no arguments: it maps changed files to their published URLs. Three things it gets right that are easy to get wrong:

- **`git diff HEAD` alone misses new pages.** It only sees tracked files, so the entire untracked `/ru/` tree (536 files) reported as “zero Russian pages changed”. The tool unions `git diff` with `git ls-files --others --exclude-standard`.
- **`404.html`, `legal/history/*` and `_hero_phone_backup/` are excluded.** They are `noindex` or not indexable; notifying crawlers about them is noise.
- **It never reports an unverified submission as success.** IndexNow answers `202` to a GET it cannot verify yet — queued, then discarded. The tool counts 202 separately from acceptance, exits non-zero when nothing was delivered, and skips the per-URL GET fallback entirely when the key file is unreachable (it would return 202 for all 672 URLs and tell us nothing the POST status did not already say).

Sanity check: with the working tree fully dirty, `--changed` resolves to exactly the same 672 URLs as `sitemap.xml`. Nothing indexable is missed and nothing extra is submitted.

**The first submission cannot succeed until this ships.** The key file only goes live with the deploy, so IndexNow rejects every request until then. Re-run `python tools/indexnow.py --check` after the push; once it reports the key reachable, `python tools/indexnow.py --all` submits all 672 URLs in a single POST.

### 5. Search Console and Bing Webmaster Tools still have to be set up manually

1. Search Console → **Sitemaps** → submit `sitemap.xml`.
2. Search Console → **URL Inspection** → paste `help.html`, request indexing, confirm it lists the article links.
3. Bing Webmaster Tools → import from Search Console (this is what connects the IndexNow key to your account in the Bing UI).
4. Expect the 323 help pages to appear over days to weeks, not hours. `site:` is an unreliable index-coverage estimator; Search Console's Page Indexing report is the real one.
5. **Google does not support IndexNow.** Bing, Yandex, DuckDuckGo and some others do. Google still depends on Search Console + sitemap + internal linking — IndexNow is a bonus, not a substitute.

## Custom domain

The site is served from the root of `fastscheduler.github.io/` — the old `/Fast-Scheduler/` path segment was removed, so every absolute URL, canonical, sitemap entry and JSON-LD `@id` is now prefix-free. `*.github.io` still carries little trust of its own; moving to a custom domain (e.g. `fastscheduler.app`) would consolidate link equity and make the brand the ranking unit rather than the hosting provider. It is a one-afternoon DNS change plus a find-and-replace of the SITE constant — worth doing before you invest in link building, not after.

## Reproducing the audit

```bash
python tools/crawl_graph.py     # reachability by real hrefs — the bug that caused this
python tools/seo_audit.py       # titles, descriptions, JSON-LD, duplicates, page weight
python tools/seo_meta.py        # per-page drill-down for out-of-range titles/descriptions
python tools/seo_ld.py          # JSON-LD blocks and their byte weight, per section
python tools/ru_coverage.py --by-dir   # share of text with a RU translation
```

After changing a builder, rebuild in this order — `build_help` feeds `build_static` and `build_blog`:

```bash
cd website/_build
python build_help.py && python build_blog.py && python extract_hc_css.py \
  && python build_site.py && python build_static.py
cd ../..
python tools/build_ru.py            # emits /ru/ pages, hreflang cluster, sitemap entries
cd website/_build && python tag_ru_chrome.py   # AFTER build_ru: wires the new pages too
cd ../.. && python tools/sync_root.py && python tools/sync_audit.py   # expect different: 0
```

`build_ru.py` must run **after** the builders (it injects hreflang into the English pages they just produced) and **before** `tag_ru_chrome.py` (which otherwise wires script tags on 408 pages and misses the 268 new ones). `build_static.py` rewrites `sitemap.xml` from scratch, so the `/ru/` entries only survive because `build_ru.py` runs after it.

`sync_root.py` and `sync_audit.py` both gate on an explicit `PUB` allowlist of top-level paths. Adding a new section to the site means adding it there too, or the pages are built, audited as present in `website/`, and silently never deployed.

The same allowlist cuts the other way: anything at the site root that is **not** in `PUB` is published but never audited, never crawled, and never in the sitemap. `_hero_phone_backup/` is exactly that, and it held three indexable duplicates of the homepage complete with fabricated testimonials. Anything hand-dropped into the root needs to go into `PUB` or be deleted.

Builder changes are made by idempotent patch scripts (`tools/patch_seo_builders*.py`) because `website/_build/` is gitignored and the editing tools refuse to write there. Each takes `--check` to verify its markers are present without applying anything.

Hand-maintained markup (the homepage, `lang.js`, `ru-chrome.js`, the hotkey registry, the shared stylesheets) is not written by any builder, so it is patched by [tools/remove_fake_reviews.py](tools/remove_fake_reviews.py) — same conventions: every replacement is best-effort so a re-run is a no-op, correctness is asserted afterwards from `REQUIRED` (must be present) and `LEFTOVER` (must be absent) markers, and **nothing is written until the whole pass has been computed and checked**, so a pattern miss can never leave half the site patched. Two things that patch has to get right: the tree mixes LF and CRLF files (`styles/main.css` and `ru-chrome.js` are CRLF, the rest LF), so patterns are re-expanded per file; and a bare `sec5 → sec4` token swap re-fires on the next run, so the renumber is anchored on the anchor href instead.

### A layout bug that only exists in Russian

The homepage navbar collapsed only at `max-width: 860px`. Russian labels are about a third wider — `Экономия времени` is 168px against `Time saved` at 109px, `Вопросы и ответы` 159px against `FAQ` at 55px — so the bar that fitted in English overflowed in Russian and pushed the settings gear and the Open Bot CTA past the right edge, where the header clipped them. The settings icon was simply not there.

Measured in the rendered page (not estimated), with the brand and gutters a fixed 362px:

| | nav width | viewport needed |
|---|---|---|
| English, as shipped | 891px | 1253px |
| Russian, as shipped | 1187px | 1549px |
| Russian without the Blog/Help pills | 938px | 1300px |

`tools/fix_nav_ru_overflow.py` sheds the Blog/Help pills below 1500px and the section links below 1320px, both scoped to `html[lang="ru"]` so English is untouched. The first attempt guessed 1400/1180 and was wrong — at 1440px the gear was still 9px off the edge — which is why the numbers above are measured. Blog and Help stay in the mobile menu and the footer.

**Verified in a browser at 1920, 1600, 1440, 1366, 1320, 1180, 1024 and 861px in Russian: the gear and the CTA are on screen at every width**, the gear opens the full Настройки menu, and English at 1280 still shows all five section links plus the Blog/Help pills.

`site_dates.json` at the repo root is version-controlled on purpose: it is the first-seen date registry that keeps `sitemap.xml` stable across rebuilds. **Commit it.** Delete it and every page re-dates to the build day again.