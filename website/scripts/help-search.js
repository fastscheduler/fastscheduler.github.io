/* =====================================================================
   Site-wide search entry points.

   The nav search bar is intentionally page-scoped — it searches what the
   page is about, never the whole site:

     • legal pages  → the text of THAT legal document (headings, clauses,
                      paragraphs). Results scroll to the passage and flash
                      it, so "refund", "termination" or "13 years" can be
                      found without reading 20 sections.
     • blog pages   → blog articles only (never help articles).
     • help pages   → the help center's own search field in the navbar
                      (help-hub.js owns it), so no second bar is drawn.

   The bar stays out of the way at the top of the page, slides in once the
   visitor scrolls, and Ctrl/Cmd + K focuses it — or the page's own search
   field — with preventScroll, so the page never jumps back to the top.

   The Help pill's hover popover keeps its own input + recent searches.
   ===================================================================== */
(function () {
  'use strict';

  var root = document.documentElement;
  var PATH = location.pathname || '';
  var IS_RU = false;
  try {
    IS_RU = root.lang === 'ru' || /(^|\/)ru(\/|$)/.test(PATH);
  } catch (e) {}

  var HAS_DOC_SEARCH = !!document.getElementById('hcSearchH');
  var IS_BLOG = /\/blog\//.test(PATH) || !!document.getElementById('blog-q');
  var IS_HELP_PAGE = /\/help(\/|\.html)/.test(PATH) || /\/help$/.test(PATH);
  var IS_LEGAL = !IS_BLOG && !IS_HELP_PAGE && (
    (document.body && document.body.classList.contains('legal')) ||
    /\/legal\//.test(PATH) ||
    !!document.getElementById('tocSideNav')
  );
  /* help  = the help center page, which owns its own search field
     helpnav = a static help article (help/a/*), which needs the bar and
               sends the query to the help center results
     blog  = blog hub + blog articles
     legal = one legal document, searched in place */
  var SCOPE = HAS_DOC_SEARCH ? 'help'
    : (IS_BLOG ? 'blog'
      : (IS_HELP_PAGE ? 'helpnav'
        : (IS_LEGAL ? 'legal' : 'none')));

  var T = {
    helpPh: IS_RU ? 'Поиск по справке…' : 'Search help articles…',
    blogPh: IS_RU ? 'Поиск по блогу…' : 'Search blog articles…',
    legalPh: IS_RU ? 'Поиск по этому документу…' : 'Search this page…',
    helpAria: IS_RU ? 'Поиск по статьям справки' : 'Search help articles',
    blogAria: IS_RU ? 'Поиск по статьям блога' : 'Search blog articles',
    legalAria: IS_RU ? 'Поиск по этому документу' : 'Search this page',
    matches: IS_RU ? 'совпадений' : 'matches',
    noMatch: IS_RU ? 'Ничего не найдено на этой странице' : 'No matches on this page',
    sections: IS_RU ? 'Разделы' : 'Sections',
    goHelp: IS_RU ? 'Искать в справке' : 'Search the help center',
    goBlog: IS_RU ? 'Искать в блоге' : 'Search the blog'
  };

  /* Site root from this script's own src (works at every depth). */
  var ROOT = '';
  try {
    var self = document.querySelector('script[src*="help-search.js"]');
    var src = (self && self.getAttribute('src')) || '';
    var i = src.indexOf('scripts/help-search.js');
    if (i > -1) ROOT = src.slice(0, i);
  } catch (e) {}

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  /* Unicode-aware: legal pages ship in English and Russian, so stripping to
     a-z would erase every Russian word. */
  var STRIP = (function () {
    try { new RegExp('[^\\p{L}\\p{N}\\s]', 'u'); return /[^\p{L}\p{N}\s]/gu; }
    catch (e) { return /[^a-zA-Z0-9\s]/g; }
  })();
  function norm(s) {
    return String(s == null ? '' : s).toLowerCase()
      .replace(/[\u2018\u2019\u201c\u201d]/g, "'")
      .replace(/\b(what|that|it|there|here|how|why|where|when|who)'s\b/g, '$1 is')
      .replace(/\bcan't\b/g, 'can not')
      .replace(/\bwon't\b/g, 'will not')
      .replace(/\b(did|do|does|is|are|was|were|has|have|could|should|would)n't\b/g, '$1 not')
      .replace(/\bidk\b/g, ' ')
      .replace(/\bbtw\b|\btbh\b|\bimo\b|\bpls\b|\bplz\b|\bthx\b/g, ' ')
      .replace(STRIP, ' ')
      .replace(/\s+/g, ' ')
      .trim();
  }

  /* ------------------------------------------------------------------
     Legal-page index: every heading and text block of this document
  ------------------------------------------------------------------ */
  var legalBlocks = null;
  function buildLegalIndex() {
    if (legalBlocks) return legalBlocks;
    legalBlocks = [];
    var doc = document.querySelector('main.legal .doc, main .doc, article.doc');
    if (!doc) return legalBlocks;
    var seen = {};
    var heading = '';
    var nodes = doc.querySelectorAll('h2, h3, p, li, td, th, dt, dd');
    Array.prototype.forEach.call(nodes, function (el) {
      /* skip containers that only wrap other blocks (nested <li><p>) */
      if (el.querySelector && el.querySelector('h2,h3,p,li')) return;
      /* skip navigation/chrome: table of contents, "last updated", see-also
         lines — they are not document content and outranked real clauses */
      if (el.closest && el.closest('.toc-box, .toc-side, .toc-sheet, nav, .see-also, .updated')) return;
      if (el.classList && (el.classList.contains('see-also') || el.classList.contains('updated'))) return;
      var text = (el.textContent || '').replace(/\s+/g, ' ').trim();
      if (text.length < 12) return;
      if (seen[text]) return;
      seen[text] = 1;
      var tag = el.tagName.toLowerCase();
      if (tag === 'h2' || tag === 'h3') heading = text;
      legalBlocks.push({
        el: el,
        text: text,
        low: norm(text),
        heading: heading && heading !== text ? heading : '',
        tag: tag
      });
    });
    return legalBlocks;
  }

  /* questions typed into a document search: "what's the refund policy"
     must look for refund+policy, not for "what is the" */
  var LEGAL_STOP = {
    what: 1, whats: 1, is: 1, are: 1, was: 1, were: 1, be: 1, been: 1,
    the: 1, a: 1, an: 1, of: 1, to: 1, in: 1, on: 1, at: 1, for: 1, with: 1,
    and: 1, or: 1, but: 1, if: 1, so: 1, then: 1, than: 1, as: 1, by: 1,
    i: 1, my: 1, me: 1, we: 1, our: 1, you: 1, your: 1, it: 1, its: 1,
    this: 1, that: 1, these: 1, those: 1, there: 1, here: 1,
    do: 1, does: 1, did: 1, how: 1, why: 1, when: 1, where: 1, which: 1, who: 1,
    can: 1, could: 1, would: 1, should: 1, will: 1, shall: 1, may: 1, might: 1,
    not: 1, no: 1, any: 1, some: 1, all: 1, about: 1, from: 1, into: 1,
    please: 1, thanks: 1, under: 1, over: 1, per: 1, also: 1
  };

  function legalSearch(q) {
    var blocks = buildLegalIndex();
    var nq = norm(q);
    if (!nq) return [];
    var words = nq.split(' ').filter(function (w) { return w.length > 1 && !LEGAL_STOP[w]; });
    if (!words.length) words = nq.split(' ').filter(function (w) { return w.length > 1; });
    if (!words.length) words = [nq];
    var out = [];
    blocks.forEach(function (b) {
      if (!b.low) return;
      var hits = 0;
      for (var i = 0; i < words.length; i++) {
        if (b.low.indexOf(words[i]) !== -1) hits++;
        else { hits = -1; break; }
      }
      if (hits < 0) return;
      var s = 0;
      if (b.low.indexOf(nq) !== -1) s += 60;
      if (b.tag === 'h2' || b.tag === 'h3') s += 70;
      /* a hit in a section that already names the word is a better landing
         spot than a passing mention */
      if (b.heading && words.some(function (w) { return b.heading.toLowerCase().indexOf(w) !== -1; })) s += 30;
      if (b.tag === 'dt' || b.tag === 'th') s += 12;
      s += Math.min(20, hits * 5);
      out.push({ block: b, score: s });
    });
    out.sort(function (a, b) { return b.score - a.score; });
    return out;
  }

  /* ------------------------------------------------------------------
     Nav search bar
  ------------------------------------------------------------------ */
  var MAC = false;
  try {
    MAC = /Mac|iPhone|iPad|iPod/.test(navigator.platform || navigator.userAgent || '');
  } catch (e) {}
  var KBD = MAC ? '\u2318K' : 'Ctrl K';

  var form = null, input = null, pop = null;
  if (SCOPE === 'legal' || SCOPE === 'blog' || SCOPE === 'helpnav') {
    form = document.createElement('form');
    form.className = 'nav-search';
    form.id = 'navSearch';
    form.setAttribute('role', 'search');
    form.setAttribute('autocomplete', 'off');
    form.innerHTML =
      '<svg class="ns-ic" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
      'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
      '<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>' +
      '<input id="navSearchInput" type="search" enterkeyhint="search" aria-keyshortcuts="Control+K Meta+K" ' +
      'role="combobox" aria-expanded="false" aria-controls="navSearchResults">' +
      '<kbd class="ns-kbd" aria-hidden="true"></kbd>' +
      '<div class="ns-pop" id="navSearchResults" role="listbox" aria-label="Search results" hidden></div>';
    (document.body || document.documentElement).appendChild(form);
    input = document.getElementById('navSearchInput');
    pop = document.getElementById('navSearchResults');

    var ph = SCOPE === 'legal' ? T.legalPh : (SCOPE === 'helpnav' ? T.helpPh : T.blogPh);
    var aria = SCOPE === 'legal' ? T.legalAria : (SCOPE === 'helpnav' ? T.helpAria : T.blogAria);
    input.setAttribute('placeholder', ph);
    input.setAttribute('aria-label', aria);
    form.setAttribute('aria-label', aria);
    form.querySelector('.ns-kbd').textContent = KBD;
  }

  /* Phones: the blog's hero search box is too tall to sit above the cards, so
     it is replaced by a compact magnifier in the navbar, just left of the Help
     Center pill. Same search bar, same results — the styles ride along with
     the button so no generated page has to be touched. */
  var SEARCH_ICON =
    '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
    '<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>';
  (function blogNavButton() {
    if (SCOPE !== 'blog' || !form) return;
    var navRight = document.querySelector('header.site .nav-right');
    if (!navRight || navRight.querySelector('.nav-search-btn')) return;
    var st = document.createElement('style');
    st.id = 'fs-nav-search-css';
    st.textContent =
      '.nav-search-btn{display:none}' +
      '@media (max-width:700px){' +
      '.nav-unified .nav-link.nav-search-btn{display:inline-flex;width:42px;height:42px;' +
      'padding:0;justify-content:center;align-items:center;flex:none}' +
      '.blog-search{display:none !important}}';
    document.head.appendChild(st);
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'nav-link nav-search-btn';
    btn.setAttribute('aria-label', T.blogAria);
    btn.title = T.blogAria;
    btn.innerHTML = SEARCH_ICON;
    btn.addEventListener('click', function (ev) {
      ev.preventDefault();
      focusBar();
    });
    var helpWrap = navRight.querySelector('.site-menu-wrap');
    if (helpWrap) navRight.insertBefore(btn, helpWrap);
    else navRight.appendChild(btn);
  })();

  function showBar() {
    if (!form) return;
    form.classList.add('show');
  }
  function hideBar() {
    if (!form) return;
    if (document.activeElement === input) return;
    form.classList.remove('show');
  }
  function closePop() {
    if (!pop) return;
    pop.hidden = true;
    pop.innerHTML = '';
    input.setAttribute('aria-expanded', 'false');
  }
  function focusBar() {
    if (!form) return;
    showBar();
    form.classList.add('focus');
    try { input.focus({ preventScroll: true }); } catch (e) { try { input.focus(); } catch (e2) {} }
    try { input.select(); } catch (e) {}
  }

  function scrollPos() {
    var y = window.scrollY || window.pageYOffset || 0;
    var sc = document.querySelector('main.legal');
    if (sc && document.body && document.body.classList.contains('legal')) y += sc.scrollTop || 0;
    return y;
  }

  /* ---------------- legal: jump + flash ---------------- */
  var flashTimer = null;
  function jumpTo(el) {
    if (!el) return;
    try { el.scrollIntoView({ behavior: 'smooth', block: 'center' }); }
    catch (e) { el.scrollIntoView(); }
    /* the legal pages on phones scroll inside main.legal — scrollIntoView
       already handles that container in modern browsers */
    el.classList.remove('ns-hit');
    void el.offsetWidth;
    el.classList.add('ns-hit');
    clearTimeout(flashTimer);
    flashTimer = setTimeout(function () { el.classList.remove('ns-hit'); }, 2600);
    try { window.dispatchEvent(new CustomEvent('fs-jump')); } catch (e) {}
  }

  /* ---------------- legal results ---------------- */
  function snippet(text, q) {
    var low = text.toLowerCase();
    var i = low.indexOf(String(q || '').toLowerCase());
    if (i === -1) return text.slice(0, 130) + (text.length > 130 ? '\u2026' : '');
    var s = Math.max(0, i - 45);
    return (s > 0 ? '\u2026' : '') + text.slice(s, s + 140) + (s + 140 < text.length ? '\u2026' : '');
  }
  function markText(raw, q) {
    if (!q) return esc(raw);
    var out = '', low = String(raw).toLowerCase(), term = String(q).toLowerCase(), i = 0, idx;
    while ((idx = low.indexOf(term, i)) !== -1) {
      out += esc(raw.slice(i, idx)) + '<mark>' + esc(raw.slice(idx, idx + term.length)) + '</mark>';
      i = idx + term.length;
    }
    return out + esc(raw.slice(i));
  }

  var rows = [], cur = -1;
  function paintLegal(q) {
    var hits = legalSearch(q);
    if (!hits.length) {
      pop.innerHTML = '<div class="ns-empty">' + esc(T.noMatch) + '</div>';
      pop.hidden = false;
      input.setAttribute('aria-expanded', 'true');
      rows = []; cur = -1;
      return;
    }
    var head = '<div class="ns-head">' + hits.length + ' ' + esc(T.matches) + '</div>';
    pop.innerHTML = head + hits.slice(0, 8).map(function (h, i) {
      var b = h.block;
      var label = (b.tag === 'h2' || b.tag === 'h3') ? '' : b.heading;
      return '<button type="button" class="ns-res" role="option" data-i="' + i + '">' +
        (label ? '<span class="ns-tag">' + esc(label) + '</span>' : '') +
        '<span class="ns-s">' + markText(snippet(b.text, q), q) + '</span></button>';
    }).join('');
    pop.hidden = false;
    input.setAttribute('aria-expanded', 'true');
    rows = Array.prototype.slice.call(pop.querySelectorAll('.ns-res'));
    cur = rows.length ? 0 : -1;
    if (rows[0]) rows[0].classList.add('cur');
    rows.forEach(function (r) {
      r.addEventListener('mousedown', function (e) { e.preventDefault(); });
      r.addEventListener('click', function () {
        var i = parseInt(r.getAttribute('data-i'), 10);
        if (hits[i]) { jumpTo(hits[i].block.el); closePop(); input.blur(); }
      });
    });
  }

  /* ---------------- blog suggestions ---------------- */
  function paintBlog(q) {
    var docs = window.__BLOG_DOCS || [];
    if (!window.HelpAI || !docs.length) { closePop(); return; }
    var ranked = window.HelpAI.scoreAll(q, docs).slice(0, 5);
    if (!ranked.length) { closePop(); return; }
    pop.innerHTML = '<div class="ns-head">' + esc(T.sections) + '</div>' + ranked.map(function (r, i) {
      var d = r.doc;
      return '<a class="ns-res" role="option" data-i="' + i + '" href="' + esc(d.href || ('a/' + d.id + '/)')) + '">' +
        '<span class="ns-s">' + markText(d.t || '', q) + '</span>' +
        (d.d ? '<span class="ns-tag">' + esc(String(d.d).slice(0, 90)) + '</span>' : '') +
        '</a>';
    }).join('');
    pop.hidden = false;
    input.setAttribute('aria-expanded', 'true');
    rows = Array.prototype.slice.call(pop.querySelectorAll('.ns-res'));
    cur = -1;
  }

  function update() {
    if (!input || !pop) return;
    var q = input.value.trim();
    if (q.length < 2) { closePop(); return; }
    if (SCOPE === 'legal') paintLegal(q);
    else if (SCOPE === 'blog') paintBlog(q);
    else closePop();
  }

  function submitQuery() {
    if (!input) return;
    var q = input.value.trim();
    if (!q) return;
    if (SCOPE === 'legal') {
      var hits = legalSearch(q);
      if (hits.length) { jumpTo(hits[0].block.el); closePop(); return; }
      return;
    }
    var hash = encodeURIComponent(q.slice(0, 160)).replace(/%20/g, '+');
    if (SCOPE === 'blog') {
      var onHub = /\/blog\/(index\.html)?$/.test(PATH);
      if (onHub) { location.hash = '#q=' + hash; }
      else { location.href = ROOT + 'blog/#q=' + hash; }
    } else if (SCOPE === 'helpnav') {
      location.href = ROOT + 'help/#/s/' + hash;
    }
  }

  if (form) {
    var timer = null;
    /* mobile keyboards' "Go/Search" key submits the form natively — keep
       that path (and any click on a submit control) on our router */
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      submitQuery();
    });
    input.addEventListener('input', function () {
      clearTimeout(timer);
      timer = setTimeout(update, 110);
    });
    input.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        if (!rows.length) return;
        e.preventDefault();
        cur = (cur + (e.key === 'ArrowDown' ? 1 : -1) + rows.length) % rows.length;
        rows.forEach(function (r, i) { r.classList.toggle('cur', i === cur); });
        rows[cur].scrollIntoView({ block: 'nearest' });
        return;
      }
      if (e.key === 'Enter') {
        e.preventDefault();
        if (rows.length && cur > -1 && SCOPE === 'legal') {
          var i = parseInt(rows[cur].getAttribute('data-i'), 10);
          var hits = legalSearch(input.value.trim());
          if (hits[i]) { jumpTo(hits[i].block.el); closePop(); input.blur(); }
          return;
        }
        if (SCOPE === 'blog' && rows.length && cur > -1 && rows[cur].getAttribute('href')) {
          location.href = rows[cur].getAttribute('href');
          return;
        }
        submitQuery();
        return;
      }
      if (e.key === 'Escape' || e.key === 'Esc') {
        e.preventDefault();
        input.value = '';
        closePop();
        input.blur();
        form.classList.remove('focus');
        if (scrollPos() < REVEAL_AT) hideBar();
      }
    });
    input.addEventListener('focus', function () { form.classList.add('focus'); });
    input.addEventListener('blur', function () {
      form.classList.remove('focus');
      setTimeout(closePop, 120);
      if (scrollPos() < REVEAL_AT) hideBar();
    });
    document.addEventListener('click', function (e) {
      if (form.contains(e.target)) return;
      closePop();
    });
  }

  /* Reveal on scroll. Legal pages on phones scroll inside main.legal. */
  var REVEAL_AT = 200;
  var ticking = false;
  function onScroll() {
    if (ticking || !form) return;
    ticking = true;
    /* setTimeout, not rAF: rAF is throttled to never inside some embedded
       webviews, which would leave the bar permanently hidden */
    setTimeout(function () {
      ticking = false;
      var y = scrollPos();
      if (y > REVEAL_AT) showBar();
      else if (document.activeElement !== input) hideBar();
    }, 60);
  }
  if (form) {
    window.addEventListener('scroll', onScroll, { passive: true });
    document.addEventListener('scroll', onScroll, { passive: true, capture: true });
    onScroll();
  }

  /* ------------------------------------------------------------------
     Ctrl/Cmd + K
       help  → the docs-header / hero search
       blog  → the navbar bar, so a scrolled page never jumps to the top
       legal → the bar (this document)
       home  → untouched (no search on the landing page)
  ------------------------------------------------------------------ */
  function onScreen(el) {
    if (!el) return false;
    var r = el.getBoundingClientRect();
    if (r.width <= 0 || r.height <= 0) return false;
    return r.bottom > 8 && r.top < (window.innerHeight || 800);
  }
  function putCaret(el) {
    try { el.focus({ preventScroll: true }); } catch (e) { try { el.focus(); } catch (e2) {} }
    /* Ctrl+K then typing should replace the old query, not append to it */
    try {
      if (el.value) { el.select(); return; }
      var n = (el.value || '').length; el.setSelectionRange(n, n);
    } catch (e) {}
  }
  if (SCOPE !== 'none') {
    document.addEventListener('keydown', function (e) {
      if (e.defaultPrevented) return;
      if (!(e.ctrlKey || e.metaKey) || e.altKey || e.shiftKey) return;
      if (String(e.key || '').toLowerCase() !== 'k' && e.code !== 'KeyK') return;
      if (window.FS_HK_RECORDING || document.querySelector('.hk-overlay.open')) return;
      e.preventDefault();
      e.stopPropagation();

      if (SCOPE === 'help') {
        var head = document.getElementById('hcSearchH');
        var hero = document.getElementById('hcSearch');
        if (head && onScreen(head)) { putCaret(head); return; }
        if (hero && onScreen(hero)) { putCaret(hero); return; }
        if (head) { putCaret(head); return; }
        if (hero) { putCaret(hero); return; }
        return;
      }
      if (SCOPE === 'blog') {
        /* The navbar bar, not the hub's hero field: scrolling the hero back
           into view yanked the page upward, which is exactly what Ctrl+K
           should never do. The bar submits into the same results view. */
        if (form) { focusBar(); return; }
      }
      if (form) focusBar();
    }, true);
  }

  /* ------------------------------------------------------------------
     Settings > Help popover (existing behaviour, unchanged routing)
  ------------------------------------------------------------------ */
  var menu = document.getElementById('siteMenu');
  var hform = document.getElementById('helpSearchForm');
  var hinput = document.getElementById('helpSearchInput');
  var list = document.getElementById('helpRecentList');
  var title = document.getElementById('helpRecentTitle');
  if (!menu || !hform || !hinput || !list) return;

  var KEY = 'fs-help-recents';
  var HELP_URL = ROOT + 'help/';
  (function () {
    var open = menu.querySelector('a.help-menu-open');
    if (open && open.getAttribute('href')) HELP_URL = open.getAttribute('href');
  })();
  var SUGGESTED = [
    { t: 'Getting Started', q: 'getting started' },
    { t: 'Connecting a Channel', q: 'connecting a channel' },
    { t: 'Recurring Messages', q: 'recurring messages' },
    { t: 'Premium & Billing', q: 'premium billing' },
    { t: 'Media & Photo Posts', q: 'photo video posts' },
    { t: 'Fix: Post Not Sent', q: 'post not sent' },
    { t: 'Edit or Delete a Post', q: 'edit delete scheduled' }
  ];

  function readRecents() {
    try { return JSON.parse(localStorage.getItem(KEY) || '[]'); } catch (e) { return []; }
  }
  /* pick n random items (Fisher-Yates on a copy) — the list rotates on
     every open instead of always showing the same seven entries */
  function pickRandom(arr, n) {
    var a = arr.slice();
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var t = a[i]; a[i] = a[j]; a[j] = t;
    }
    return a.slice(0, n);
  }
  function render() {
    var rec = readRecents().slice(0, 5);
    list.textContent = '';
    if (rec.length) {
      title.textContent = 'Recent searches';
      rec.forEach(function (q) {
        var a = document.createElement('a');
        a.href = HELP_URL + '#/s/' + encodeURIComponent(q);
        a.textContent = q;
        list.appendChild(a);
      });
    } else {
      title.textContent = 'Popular articles';
      pickRandom(SUGGESTED, 3).forEach(function (s) {
        var a = document.createElement('a');
        a.href = HELP_URL + '#/s/' + encodeURIComponent(s.q);
        a.textContent = s.t;
        list.appendChild(a);
      });
    }
  }

  /* prefill as soon as the submenu opens (settings.js toggles .open) */
  var obs = new MutationObserver(function () {
    if (menu.classList.contains('open')) render();
  });
  obs.observe(menu, { attributes: true, attributeFilter: ['class'] });

  hform.addEventListener('submit', function (e) {
    e.preventDefault();
    var q = hinput.value.trim();
    if (!q) return;
    try {
      var rec = readRecents().filter(function (x) { return x !== q; });
      rec.unshift(q);
      localStorage.setItem(KEY, JSON.stringify(rec.slice(0, 6)));
    } catch (err) {}
    window.open(HELP_URL + '#/s/' + encodeURIComponent(q), '_blank', 'noopener');
  });
})();
