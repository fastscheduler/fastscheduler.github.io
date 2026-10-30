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
    var doc = (SCOPE === 'legal')
      ? document.querySelector('main.legal .doc, main .doc, article.doc')
      : pageRoot();
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

  /* Help article pages: a visible magnifier in the navbar, so the article's
     search is one click away instead of waiting for a scroll. */
  (function helpNavButton() {
    if (SCOPE !== 'helpnav' || !form) return;
    var navRight = document.querySelector('header.site .nav-right');
    if (!navRight || navRight.querySelector('.nav-search-btn')) return;
    var st = document.createElement('style');
    st.id = 'fs-nav-search-help-css';
    st.textContent =
      '.nav-unified .nav-link.nav-search-btn{display:inline-flex;width:42px;height:42px;' +
      'padding:0;justify-content:center;align-items:center;flex:none}' +
      '@media (max-width:700px){.nav-unified .nav-link.nav-search-btn{width:38px;height:38px}}';
    document.head.appendChild(st);
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'nav-link nav-search-btn';
    btn.setAttribute('aria-label', T.helpAria);
    btn.title = T.helpAria;
    btn.innerHTML = SEARCH_ICON;
    btn.addEventListener('click', function (ev) {
      ev.preventDefault();
      focusBar();
    });
    navRight.insertBefore(btn, navRight.firstChild);
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

  /* ---------------- legal: highlight every match + walk them ----------------
     The popover used to list the sections and jump to one of them, then blur
     the field, so nobody could see what else matched or keep going. Now every
     occurrence inside a matching block is wrapped in <mark>, the head shows
     how many there are, and Enter / the arrows step through them while the
     input keeps focus. */
  var LG = { q: '', marks: [], i: -1, blocks: [] };

  (function findCss() {
    if (SCOPE !== 'legal' || document.getElementById('fs-find-css')) return;
    var st = document.createElement('style');
    st.id = 'fs-find-css';
    st.textContent =
      'mark.fs-find{background:color-mix(in srgb,#ffd84d 55%,transparent);color:inherit;' +
      'border-radius:3px;padding:0 1px;scroll-margin-top:120px;' +
      'transition:background .18s ease,box-shadow .18s ease}' +
      'mark.fs-find-cur{background:var(--green-strong,#1faa59);color:#fff;' +
      'box-shadow:0 0 0 2px color-mix(in srgb,var(--green) 45%,transparent)}' +
      '.ns-hit-all{background:color-mix(in srgb,var(--green) 7%,transparent)}' +
      '.ns-head{display:flex;align-items:center;gap:10px;justify-content:space-between}' +
      '.ns-nav{display:inline-flex;gap:4px;flex:none}' +
      '.ns-navbtn{width:26px;height:26px;border-radius:8px;border:1px solid var(--border);' +
      'background:var(--surface-2);color:var(--text);font:inherit;font-size:.78rem;' +
      'font-weight:700;cursor:pointer;display:grid;place-items:center;padding:0}' +
      '.ns-navbtn:hover{border-color:var(--green);color:var(--green-strong)}';
    document.head.appendChild(st);
  })();

  /* One content root per page type: the same find engine drives the legal
     clauses, a blog article and the open help view. */
  function pageRoot() {
    if (SCOPE === 'legal') return document.querySelector('article.doc') || document.body;
    if (SCOPE === 'blog') return document.querySelector('.blog-doc, .blog-art, article.doc, main') || document.body;
    if (SCOPE === 'help') return document.querySelector('section.view:not([hidden]) .hc-art, section.view:not([hidden])') || document.body;
    /* a static help article: search its body, never the chrome around it */
    if (SCOPE === 'helpnav') return document.querySelector('main.legal article.doc, main article.doc, article.doc') || document.body;
    return document.body;
  }
  function legalRoot() { return pageRoot(); }
  function clearLegalMarks() {
    var root = legalRoot();
    Array.prototype.forEach.call(root.querySelectorAll('mark.fs-find'), function (m) {
      var p = m.parentNode; if (!p) return;
      p.replaceChild(document.createTextNode(m.textContent), m);
      p.normalize();
    });
    Array.prototype.forEach.call(root.querySelectorAll('.ns-hit, .ns-hit-all'), function (b) {
      b.classList.remove('ns-hit', 'ns-hit-all');
    });
    LG.marks = []; LG.i = -1; LG.blocks = [];
  }

  function termRegex(q) {
    var words = String(q).toLowerCase().split(/\s+/).filter(function (w) { return w.length > 1 && !LEGAL_STOP[w]; });
    if (!words.length) words = String(q).toLowerCase().split(/\s+/).filter(function (w) { return w.length > 1; });
    if (!words.length) return null;
    var src = words.map(function (w) { return esc(w).replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); })
      .sort(function (a, b) { return b.length - a.length; }).join('|');
    return new RegExp('(' + src + ')', 'gi');
  }

  function markNode(node, re) {
    var text = node.nodeValue;
    re.lastIndex = 0;
    if (!re.test(text)) return 0;
    re.lastIndex = 0;
    var pieces = text.split(new RegExp(re.source, 'gi'));
    if (pieces.length < 2) return 0;
    var frag = document.createDocumentFragment(), made = 0;
    pieces.forEach(function (piece, i) {
      if (!piece) return;
      if (i % 2) {
        var mk = document.createElement('mark');
        mk.className = 'fs-find';
        mk.textContent = piece;
        frag.appendChild(mk);
        made++;
      } else {
        frag.appendChild(document.createTextNode(piece));
      }
    });
    if (!made) return 0;
    node.parentNode.replaceChild(frag, node);
    return made;
  }

  function markBlock(el, re) {
    var walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, null, false);
    var list = [], n;
    while ((n = walker.nextNode())) {
      var p = n.parentNode, skip = false;
      while (p && p !== el) {
        var t = (p.tagName || '').toLowerCase();
        if (t === 'code' || t === 'pre' || t === 'script' || t === 'style' || t === 'mark') { skip = true; break; }
        p = p.parentNode;
      }
      if (!skip && n.nodeValue && /\S/.test(n.nodeValue)) list.push(n);
    }
    var count = 0;
    list.forEach(function (node) { count += markNode(node, re); });
    return count;
  }

  function focusMark(i, smooth) {
    if (!LG.marks.length) return;
    var n = LG.marks.length;
    LG.i = ((i % n) + n) % n;
    Array.prototype.forEach.call(LG.marks, function (m, k) { m.classList.toggle('fs-find-cur', k === LG.i); });
    var m = LG.marks[LG.i];
    try { m.scrollIntoView({ behavior: smooth === false ? 'auto' : 'smooth', block: 'center' }); }
    catch (e) { m.scrollIntoView(); }
    /* the block flash lives on the enclosing block, the mark carries the ring */
    var b = m.closest('p, li, td, h2, h3, dt, dd');
    if (b) {
      Array.prototype.forEach.call(legalRoot().querySelectorAll('.ns-hit'), function (x) { x.classList.remove('ns-hit'); });
      b.classList.add('ns-hit');
    }
    paintHead();
  }

  function paintHead() {
    var head = pop && pop.querySelector('.ns-head');
    if (!head) return;
    var total = LG.marks.length;
    var label = head.querySelector('.ns-head-t');
    if (!label) return;
    label.textContent = total
      ? (LG.i >= 0 ? (LG.i + 1) + ' / ' + nMatches(total) : nMatches(total))
      : label.textContent;
  }

  var rows = [], cur = -1;
  function paintLegal(q) {
    var hits = legalSearch(q);
    clearLegalMarks();
    LG.q = q;
    if (!hits.length) {
      pop.innerHTML = '<div class="ns-empty">' + esc(T.noMatch) + '</div>';
      pop.hidden = false;
      input.setAttribute('aria-expanded', 'true');
      rows = []; cur = -1;
      return;
    }
    /* highlight every occurrence inside every matching block, in place */
    var re = termRegex(q);
    if (re) {
      hits.forEach(function (h) {
        if (markBlock(h.block.el, re)) h.block.el.classList.add('ns-hit-all');
      });
      LG.marks = Array.prototype.slice.call(legalRoot().querySelectorAll('mark.fs-find'));
    }
    var total = LG.marks.length || hits.length;
    var head = '<div class="ns-head"><span class="ns-head-t">' + esc(nMatches(total)) + '</span>' +
      '<span class="ns-nav"><button type="button" class="ns-navbtn" data-find="prev" aria-label="' + esc(T.prevMatch || 'Previous match') + '">\u2191</button>' +
      '<button type="button" class="ns-navbtn" data-find="next" aria-label="' + esc(T.nextMatch || 'Next match') + '">\u2193</button></span></div>';
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
      r.addEventListener('click', function (e) {
        e.preventDefault();
        var i = parseInt(r.getAttribute('data-i'), 10);
        var hit = hits[i];
        if (!hit) return;
        /* land on the first occurrence in that block and keep the field
           focused so Enter can carry on from there */
        var k = -1;
        LG.marks.forEach(function (m, idx) {
          if (k === -1 && hit.block.el.contains(m)) k = idx;
        });
        if (k >= 0) focusMark(k);
        else jumpTo(hit.block.el);
        try { input.focus({ preventScroll: true }); } catch (err) {}
      });
    });
    var prev = pop.querySelector('[data-find="prev"]');
    var next = pop.querySelector('[data-find="next"]');
    if (prev) { prev.addEventListener('mousedown', function (e) { e.preventDefault(); }); prev.addEventListener('click', function () { focusMark(LG.i < 0 ? 0 : LG.i - 1); }); }
    if (next) { next.addEventListener('mousedown', function (e) { e.preventDefault(); }); next.addEventListener('click', function () { focusMark(LG.i < 0 ? 0 : LG.i + 1); }); }
  }

  /* ---------------- Articles / On this page ----------------
     One bar, two targets. "Articles" searches the hub or the blog index;
     "On this page" finds text inside the document you are reading, exactly
     like the legal pages: every hit highlighted, a live count, Enter/arrows
     to step through them. */
  var MODE = 'articles';
  var ML = IS_RU
    ? { a: 'Статьи', h: 'В справке', p: 'На странице', n: 'совпадений', one: 'совпадение', none: 'На этой странице ничего не найдено', in: 'Где искать' }
    : { a: 'Articles', h: 'In help center', p: 'On this page', n: 'matches', one: 'match', none: 'Nothing on this page matches', in: 'Search in' };
  function nMatches(n) { return n + ' ' + (n === 1 ? ML.one : ML.n); }

  function buildModeSeg(labelArticles) {
    var seg = document.createElement('div');
    seg.className = 'ns-mode';
    seg.setAttribute('role', 'group');
    seg.setAttribute('aria-label', ML.in);
    seg.innerHTML = '<button type="button" data-mode="articles" aria-pressed="true">' + esc(labelArticles || ML.a) +
      '</button><button type="button" data-mode="page" aria-pressed="false">' + esc(ML.p) + '</button>';
    return seg;
  }

  /* highlight + count inside the current document */
  function pageFind(q) {
    legalBlocks = null;                 /* the help hub swaps views in place */
    clearLegalMarks();
    if (!q || q.length < 2) return 0;
    var re = termRegex(q);
    if (!re) return 0;
    var hits = legalSearch(q);
    hits.forEach(function (h) {
      if (markBlock(h.block.el, re)) h.block.el.classList.add('ns-hit-all');
    });
    LG.marks = Array.prototype.slice.call(legalRoot().querySelectorAll('mark.fs-find'));
    LG.i = -1;
    return LG.marks.length;
  }

  function setMode(m, seg, inputEl) {
    MODE = m === 'page' ? 'page' : 'articles';
    if (seg) {
      Array.prototype.forEach.call(seg.querySelectorAll('[data-mode]'), function (b) {
        b.setAttribute('aria-pressed', b.getAttribute('data-mode') === MODE ? 'true' : 'false');
      });
    }
    if (inputEl) {
      inputEl.placeholder = MODE === 'page' ? ML.p + '…' : (SCOPE === 'blog' ? (T.blogPh || '') : (T.helpPh || ''));
      inputEl.value = '';
    }
    clearLegalMarks();
    closePop();
  }

  (function modeCss() {
    if (document.getElementById('fs-mode-css')) return;
    var st = document.createElement('style');
    st.id = 'fs-mode-css';
    st.textContent =
      '.ns-mode{display:inline-flex;align-items:center;flex:none;gap:2px;padding:2px;' +
      'border-radius:9px;background:var(--surface-2);border:1px solid var(--border)}' +
      '.ns-mode button{font:inherit;font-size:.72rem;font-weight:700;line-height:1;' +
      'padding:5px 8px;border-radius:7px;border:0;background:transparent;color:var(--text-dim);cursor:pointer;white-space:nowrap}' +
      '.ns-mode button[aria-pressed="true"]{background:var(--surface);color:var(--green-strong);box-shadow:var(--shadow-sm)}' +
      '.ns-mode button:hover{color:var(--green-strong)}' +
      '.fs-find-count{margin:8px 2px 0;font-size:.78rem;font-weight:700;color:var(--text-dim)}' +
      '.hc-search .ns-mode{margin:8px 0 0;order:9}' +
      '.ns-mode[hidden]{display:none!important}' +
      '.nav-search.ns-wide{width:min(560px, calc(100vw - 24px))}' +
      '.nav-search.ns-wide .ns-mode{display:inline-flex}' +
      '@media (max-width:700px){.nav-search .ns-mode{display:none}' +
      /* phones: the scope switch gets its own full-width row instead of
         squeezing the query field into ~100px */
      '.nav-search.ns-wide{width:calc(100vw - 32px);height:auto;flex-wrap:wrap;' +
      'padding:8px 10px;row-gap:2px;border-radius:18px}' +
      '.nav-search.ns-wide input{height:34px;flex:1 1 110px;font-size:.9rem}' +
      '.nav-search.ns-wide .ns-kbd{display:none}' +
      '.nav-search.ns-wide .ns-mode{order:9;display:flex;width:100%;justify-content:center;' +
      'margin-top:2px;padding:2px}' +
      '.nav-search.ns-wide .ns-mode button{flex:1;font-size:.72rem;padding:7px 6px}}';
    document.head.appendChild(st);
  })();

  /* blog: the switch lives in the navbar bar */
  if (SCOPE === 'blog' && form && input) {
    var bseg = buildModeSeg();
    form.insertBefore(bseg, form.querySelector('.ns-ic'));
    bseg.addEventListener('click', function (ev) {
      var b = ev.target.closest && ev.target.closest('[data-mode]');
      if (!b) return;
      setMode(b.getAttribute('data-mode'), bseg, input);
      try { input.focus({ preventScroll: true }); } catch (e) {}
    });
  }

  /* help article pages: the bar carries the switch — "In help center" runs the
     query against the hub, "On this page" highlights matches in the article
     itself (with a live count and Enter to step through them) */
  if (SCOPE === 'helpnav' && form && input) {
    var heSeg = buildModeSeg(ML.h);
    form.insertBefore(heSeg, form.querySelector('.ns-ic'));
    form.classList.add('ns-wide');
    heSeg.addEventListener('click', function (ev) {
      var b = ev.target.closest && ev.target.closest('[data-mode]');
      if (!b) return;
      setMode(b.getAttribute('data-mode'), heSeg, input);
      try { input.focus({ preventScroll: true }); } catch (e) {}
    });
  }

  /* help: the switch rides under the hub's own field; in page mode the hub's
     routing is bypassed (document-level capture runs before its handlers) */
  if (SCOPE === 'help') {
    var hIn = document.getElementById('hcSearch'),
        hIn2 = document.getElementById('hcSearchH');
    var hHost = hIn && hIn.closest('.hc-search');
    if (hHost) {
      var hseg = buildModeSeg();
      hHost.appendChild(hseg);
      /* The hub home has no document to search inside, so the switch only
         exists while an article (or legal) page is open. On the front page it
         was two buttons that could only ever do nothing. */
      function syncHelpSegVisibility() {
        var onPage = /^#\/(a|c)\//.test(location.hash || '');
        hseg.hidden = !onPage;
        hseg.setAttribute('aria-hidden', onPage ? 'false' : 'true');
        if (!onPage && MODE === 'page') setMode('articles', hseg, hIn);
      }
      syncHelpSegVisibility();
      window.addEventListener('hashchange', syncHelpSegVisibility);
      window.addEventListener('popstate', syncHelpSegVisibility);
      var chip = document.createElement('div');
      chip.className = 'fs-find-count';
      chip.hidden = true;
      hHost.parentNode.insertBefore(chip, hHost.nextSibling);
      hseg.addEventListener('click', function (ev) {
        var b = ev.target.closest && ev.target.closest('[data-mode]');
        if (!b) return;
        setMode(b.getAttribute('data-mode'), hseg, hIn);
        chip.hidden = true;
        try { hIn.focus({ preventScroll: true }); } catch (e) {}
      });
      document.addEventListener('input', function (ev) {
        if (MODE !== 'page' || (ev.target !== hIn && ev.target !== hIn2)) return;
        ev.stopPropagation();
        var q = ev.target.value.trim();
        var n = pageFind(q);
        chip.hidden = !q;
        chip.textContent = n ? nMatches(n) : ML.none;
      }, true);
      document.addEventListener('keydown', function (ev) {
        if (MODE !== 'page' || (ev.target !== hIn && ev.target !== hIn2)) return;
        if (ev.key === 'Enter') {
          ev.preventDefault();
          ev.stopPropagation();
          if (!LG.marks.length) pageFind(ev.target.value.trim());
          if (LG.marks.length) focusMark(LG.i + 1);
          chip.hidden = false;
          chip.textContent = LG.marks.length ? ((LG.i + 1) + ' / ' + nMatches(LG.marks.length)) : ML.none;
        } else if (ev.key === 'Escape') {
          clearLegalMarks();
          chip.hidden = true;
        }
      }, true);
    }
  }

  /* ---------------- blog suggestions ---------------- */
  function paintBlog(q) {
    var docs = window.__BLOG_DOCS || [];
    if (!window.HelpAI || !docs.length) { closePop(); return; }
    var ranked = window.HelpAI.scoreAll(q, docs).slice(0, 5);
    if (!ranked.length) { closePop(); return; }
    pop.innerHTML = '<div class="ns-head">' + esc(T.sections) + '</div>' + ranked.map(function (r, i) {
      var d = r.doc;
      return '<a class="ns-res" role="option" data-i="' + i + '" href="' + esc(d.href || ('help/a/' + d.id + '.html')) + '">' +
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
    if (SCOPE === 'legal' || MODE === 'page') paintLegal(q);
    else if (SCOPE === 'blog') paintBlog(q);
    else closePop();
  }

  function submitQuery() {
    if (!input) return;
    var q = input.value.trim();
    if (!q) return;
    if (MODE === 'page') {
      update();
      if (LG.marks.length) focusMark(0);
      return;
    }
    if (SCOPE === 'legal') {
      /* stay in the field: the popover keeps the count and the arrows live */
      update();
      if (LG.marks.length) focusMark(0);
      return;
    }
    var hash = encodeURIComponent(q.slice(0, 160)).replace(/%20/g, '+');
    if (SCOPE === 'blog') {
      var onHub = /\/blog\/(index\.html)?$/.test(PATH);
      if (onHub) { location.hash = '#q=' + hash; }
      else { location.href = ROOT + 'blog/#q=' + hash; }
    } else if (SCOPE === 'helpnav') {
      location.href = ROOT + 'help.html#/s/' + hash;
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
        if (SCOPE === 'legal' || MODE === 'page') {
          /* Enter walks the matches: first press lands on the highlighted
             row, every press after that steps to the next occurrence. The
             field keeps focus the whole time, so it can be repeated. */
          if (LG.marks.length && LG.i >= 0) { focusMark(LG.i + 1); return; }
          if (rows.length && cur > -1) {
            var i = parseInt(rows[cur].getAttribute('data-i'), 10);
            var hits = legalSearch(input.value.trim());
            var hit = hits[i];
            var k = -1;
            if (hit) {
              LG.marks.forEach(function (m, idx) {
                if (k === -1 && hit.block.el.contains(m)) k = idx;
              });
              if (k >= 0) focusMark(k); else jumpTo(hit.block.el);
            }
            return;
          }
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
        if (scrollPos() < REVEAL_AT || phoneBlog()) hideBar();
      }
    });
    input.addEventListener('focus', function () { form.classList.add('focus'); });
    input.addEventListener('blur', function () {
      form.classList.remove('focus');
      setTimeout(closePop, 120);
      if (scrollPos() < REVEAL_AT || phoneBlog()) hideBar();
    });
    document.addEventListener('click', function (e) {
      if (form.contains(e.target)) return;
      closePop();
    });
  }

  /* Reveal on scroll. Legal pages on phones scroll inside main.legal.
     Phones on the blog are the exception: there the bar is opened on purpose
     (the navbar magnifier), so scrolling an article must NOT slide a search
     field over the text. */
  var REVEAL_AT = 200;
  var ticking = false;
  function phoneBlog() {
    return SCOPE === 'blog' && (window.innerWidth || 9999) <= 700;
  }
  function onScroll() {
    if (ticking || !form) return;
    ticking = true;
    /* setTimeout, not rAF: rAF is throttled to never inside some embedded
       webviews, which would leave the bar permanently hidden */
    setTimeout(function () {
      ticking = false;
      if (phoneBlog()) {
        if (document.activeElement !== input) hideBar();
        return;
      }
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
  var HELP_URL = ROOT + 'help.html';
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
