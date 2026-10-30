
(function () {
  'use strict';
  var DATA = [];
  try { DATA = window.__HELP_DATA || []; } catch (e) {}
  var SIDE = [];
  try { SIDE = window.__HELP_SIDE || []; } catch (e) {}
  var CATS = {};
  SIDE.forEach(function (c) { CATS[c.id] = c.title; });
  var byId = {};
  DATA.forEach(function (s) { byId[s.id] = s; });
  /* AI intent per article: category id doubles as the intent tag the mini
     engine matches queries against (schedule, media, payment, ...) */
  if (window.HelpAI) {
    var CAT_INTENT = { scheduling: 'schedule', recurring: 'schedule', timezone: 'schedule',
      media: 'media', media_storage: 'media', channels: 'channel', bots: 'bot',
      premium: 'payment', payment: 'payment', backup: 'backup', export: 'backup', import: 'backup',
      statistics: 'stats', errors: 'error', faq: 'error', start: 'account', getting_started: 'account',
      feedback: 'feedback', formatting: 'formatting', tips: 'formatting', limits: 'limits',
      tools: 'schedule', language: 'formatting', misc: 'error', legal: 'payment', commands: 'schedule' };
    DATA.forEach(function (s) { s.intent = CAT_INTENT[s.c] || ''; });
  }
  /* one shared interpreter for the AI "you mean" line */
  function aiLabel(q) {
    if (!window.HelpAI) return '';
    var ex = window.HelpAI.interpret(q);
    return ex.label || '';
  }

  var views = Array.prototype.slice.call(document.querySelectorAll('.view'));
  var sideNav = document.getElementById('hcSideNav');
  var progressBar = document.getElementById('hcProgress');
  var norm = function (s) { return (s || '').toLowerCase(); };

  /* ---------------- router ---------------- */
  function parseHash() {
    var h = location.hash || '', m;
    if ((m = h.match(/^#\/a\/([\w-]+)/)))  return { view: 'article',  id: m[1] };
    if ((m = h.match(/^#\/c\/([\w-]+)/)))  return { view: 'category', id: m[1] };
    if ((m = h.match(/^#\/s\/(.+)$/)))      return { view: 'search',   id: decodeURIComponent(m[1].replace(/\+/g, ' ')) };
    if ((m = h.match(/^#help-([\w-]+)/)))  return { view: 'article',  id: m[1], legacy: true };
    if ((m = h.match(/^#cat-([\w-]+)/)))   return { view: 'category', id: m[1], legacy: true };
    return { view: 'home' };
  }

  function currentTitle(r) {
    if (r.view === 'article' && byId[r.id]) return byId[r.id].t;
    if (r.view === 'category' && CATS[r.id]) return CATS[r.id];
    if (r.view === 'search') return 'Search: ' + r.id;
    return '';
  }

  function activeCatId(r) {
    if (r.view === 'category') return r.id;
    if (r.view === 'article' && byId[r.id]) return byId[r.id].c;
    return null;
  }

  function updateSidebar(r) {
    if (!sideNav) return;
    var cat = activeCatId(r);
    Array.prototype.forEach.call(sideNav.querySelectorAll('[data-cat]'), function (a) {
      var on = a.getAttribute('data-cat') === cat;
      a.classList.toggle('active', on);
      var sub = document.getElementById('hc-sub-' + a.getAttribute('data-cat'));
      /* reveal the active topic's list, but never collapse a list the reader
         opened by hand just because they landed on another page */
      if (sub && on) {
        sub.classList.add('open');
        a.setAttribute('aria-expanded', 'true');
      }
    });
    var home = document.getElementById('hcSideHome');
    if (home) home.classList.toggle('active', r.view === 'home');
    var art = (r.view === 'article') ? r.id : null;
    Array.prototype.forEach.call(sideNav.querySelectorAll('[data-art]'), function (a) {
      a.classList.toggle('active', !!art && a.getAttribute('data-art') === art);
    });
  }

  function navigate() {
    var r = parseHash();
    /* Articles and categories are real pages now. Old hash links (bookmarks,
       search results from before the clean-URL move) redirect instead of
       rendering a second copy of the article inside the hub. */
    if (r.view === 'article' && byId[r.id]) { location.replace('a/' + r.id + '/'); return; }
    if (r.view === 'category' && CATS[r.id]) { location.replace('c/' + r.id + '/'); return; }
    if (r.legacy) {
      var valid = (r.view === 'article' && byId[r.id]) || (r.view === 'category' && CATS[r.id]);
      if (valid) { history.replaceState(null, '', (r.view === 'article' ? '#/a/' : '#/c/') + r.id); }
      else { r = { view: '404' }; }
    }
    if (r.view === 'article' && !byId[r.id]) r = { view: '404' };
    if (r.view === 'category' && !CATS[r.id]) r = { view: '404' };
    if (r.view === 'search') r.id = String(r.id || '').slice(0, 200);

    var sel = '.view[data-view="home"]';
    if (r.view === 'article')  sel = '.view[data-view="article"][data-art="' + r.id + '"]';
    if (r.view === 'category') sel = '.view[data-view="category"][data-cat="' + r.id + '"]';
    if (r.view === 'search')   sel = '.view[data-view="search"]';
    if (r.view === '404')      sel = '.view[data-view="404"]';
    var el = document.querySelector(sel);
    if (!el) { sel = '.view[data-view="404"]'; el = document.querySelector(sel); }

    views.forEach(function (v) { v.hidden = v !== el; });
    if (el) {
      el.classList.remove('anim');
      void el.offsetWidth; /* restart the entrance animation */
      el.classList.add('anim');
    }
    var t = currentTitle(r);
    document.title = r.view === 'search' ? (t + hcTitleSuffix()) :
      (t ? (t + hcTitleSuffix()) : hcT('Help Center — Fast Scheduler for Telegram'));
    try {
      var d = (r.view === 'article' && byId[r.id] && byId[r.id].d) || '';
      var md = document.querySelector('meta[name="description"]');
      var mo = document.querySelector('meta[property="og:title"]');
      var mod = document.querySelector('meta[property="og:description"]');
      if (d && md) md.setAttribute('content', d);
      if (t && mo) mo.setAttribute('content', t + ' — Fast Scheduler Help');
      if (d && mod) mod.setAttribute('content', d);
    } catch (e) {}
    window.scrollTo(0, 0);
    closeAllResults();
    updateSidebar(r);
    document.body.classList.toggle('hc-onhome', r.view === 'home');
    var onArt = r.view === 'article';
    document.body.classList.toggle('hc-onarticle', onArt);
    Array.prototype.forEach.call(document.querySelectorAll('[data-reading]'), function (el) { el.hidden = !onArt; });
    if (!onArt && window.__hcExitFs && document.documentElement.classList.contains('hc-fs')) window.__hcExitFs();
    if (onArt && window.__hcSetupMore) window.__hcSetupMore();
    try { document.dispatchEvent(new CustomEvent('viewchange', { detail: { view: r.view, id: r.id } })); } catch (e) {}
    /* setTimeout, not requestAnimationFrame: rAF can be throttled to never
       inside embedded webviews, which left the search page permanently blank */
    if (r.view === 'search') setTimeout(function () { renderSearchPage(r.id); }, 0);
    document.body.classList.remove('hc-side-open');
    updateProgress();
    if (el) {
      var h1 = el.querySelector('h1, h2');
      if (h1) { h1.setAttribute('tabindex', '-1'); h1.focus({ preventScroll: true }); }
    }
  }

  /* ---------------- docs rail + feedback ---------------- */
  function markRail(scope, key) {
    if (!scope) return;
    var rail = scope.querySelector('[data-rail]');
    if (!rail) return;
    Array.prototype.forEach.call(rail.querySelectorAll('a'), function (a) {
      a.classList.toggle('on', a.getAttribute('data-rk') === key);
    });
  }
  document.addEventListener('click', function (ev) {
    if (!ev.target.closest) return;
    var j = ev.target.closest('[data-jid]');
    if (j) {
      var sec = document.getElementById(j.getAttribute('data-jid'));
      if (sec) {
        ev.preventDefault();
        sec.scrollIntoView({ behavior: 'smooth', block: 'start' });
        markRail(j.closest('section.view'), j.getAttribute('data-jid'));
      }
      return;
    }
    var fq = ev.target.closest('[data-faq-open]');
    if (fq) {
      var d = document.getElementById(fq.getAttribute('data-faq-open'));
      if (d) {
        ev.preventDefault();
        d.open = true;
        d.scrollIntoView({ behavior: 'smooth', block: 'start' });
        markRail(fq.closest('section.view'), fq.getAttribute('data-faq-open'));
      }
      return;
    }
  });
  function initRail() {
    if ('IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (es) {
        es.forEach(function (e) {
          if (e.isIntersecting) markRail(e.target.closest('section.view'), e.target.id);
        });
      }, { rootMargin: '-25% 0px -65% 0px' });
      Array.prototype.forEach.call(
        document.querySelectorAll('section.view h3[id], section.view details[id]'),
        function (s) { io.observe(s); });
    }
  }
  (function () {
    var root = document.documentElement;
    function store(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
    function load(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
    function paintReader() {
      var wide = load('fs-help-wide') === 'on';
      var railOff = load('fs-rail') === 'off';
      var font = load('fs-font') || load('fs-help-font');
      var fs = load('fs-help-fs') === 'on';
      root.classList.toggle('hc-wide', wide);
      root.classList.toggle('rail-off', railOff);
      root.classList.toggle('hc-fs', fs);
      if (wide || fs) root.classList.add('hc-collapsed');
      else if (load('fs-help-side') !== 'closed') root.classList.remove('hc-collapsed');
      if (font) { root.setAttribute('data-font', font); root.setAttribute('data-hcfont', font); } else { root.removeAttribute('data-font'); root.removeAttribute('data-hcfont'); }
      var q = function (sel, fn) { Array.prototype.forEach.call(document.querySelectorAll(sel), fn); };
      q('[data-wide-toggle]', function (b) { b.setAttribute('aria-pressed', wide ? 'true' : 'false'); });
      q('[data-rail-toggle]', function (b) { b.setAttribute('aria-pressed', railOff ? 'false' : 'true'); });
      q('[data-fonts]', function (box) { Array.prototype.forEach.call(box.querySelectorAll('button'), function (b) { b.classList.toggle('on', (font || 'm') === b.getAttribute('data-font')); }); });
      q('[data-fs-btn]', function (b) { b.classList.toggle('on', fs); });
      if (window.__hcReelPaint) { try { window.__hcReelPaint(); } catch (e) {} }
    }
    function exitFs() { store('fs-help-fs', 'off'); paintReader(); }
    document.addEventListener('click', function (ev) {
      if (!ev.target.closest) return;
      var w = ev.target.closest('[data-wide-toggle]');
      if (w) { store('fs-help-wide', w.getAttribute('aria-pressed') !== 'true' ? 'on' : 'off'); paintReader(); return; }
      var r = ev.target.closest('[data-rail-toggle]');
      if (r) { store('fs-rail', r.getAttribute('aria-pressed') === 'true' ? 'off' : 'on'); paintReader(); return; }
      var f = ev.target.closest('[data-fonts] button');
      if (f) { var fv = f.getAttribute('data-font'); store('fs-font', fv); store('fs-help-font', fv); try { window.dispatchEvent(new CustomEvent('fs-font-change', { detail: { font: fv } })); } catch (e2) {} paintReader(); return; }
      var fb2 = ev.target.closest('[data-fs-btn]');
      if (fb2) { store('fs-help-fs', load('fs-help-fs') === 'on' ? 'off' : 'on'); paintReader(); return; }
      var mb = ev.target.closest('[data-more]');
      if (mb) {
        var box = mb.closest('[data-list],[data-others],[data-chips-more]') || mb.previousElementSibling;
        var collapsed = box && box.classList.contains('is-collapsed');
        if (box) { box.classList.toggle('is-collapsed', !collapsed); box.classList.toggle('is-expanded', !!collapsed); }
        var mt = mb.querySelector('[data-more-t]'), lt = mb.querySelector('[data-less-t]');
        if (mt) mt.hidden = !!collapsed;
        if (lt) lt.hidden = !collapsed;
      }
    });
    document.addEventListener('keydown', function (ev) {
      if ((ev.key === 'Escape' || ev.key === 'Esc') && load('fs-help-fs') === 'on') exitFs();
    });
    /* show-more setup: lists with more than N items start collapsed */
    function setupMore(scopeSel, itemSel, keep) {
      Array.prototype.forEach.call(document.querySelectorAll(scopeSel), function (box) {
        var items = box.querySelectorAll(itemSel);
        var btn = box.querySelector(':scope > [data-more]') || box.nextElementSibling;
        if (items.length > keep && btn && btn.hasAttribute('data-more')) {
          box.classList.add('is-collapsed');
          box.classList.add('has-more');
          if (btn.parentElement !== box) box.appendChild(btn);
          btn.hidden = false;
        } else if (btn && btn.hasAttribute('data-more')) {
          btn.hidden = true;
        }
      });
    }
    window.__hcSetupMore = function () {
      setupMore('[data-list]', '.hc-row', 6);
      setupMore('[data-others]', 'a', 5);
      setupMore('[data-chips-more]', '.hc-chip', 3);
    };
    window.__hcExitFs = exitFs;
    window.addEventListener('fs-font-change', function () { paintReader(); });
    window.__hcPaintReader = paintReader;
    try {
      if (load('fs-rail') === 'off') root.classList.add('rail-off');
      if (load('fs-help-wide') === 'on' || load('fs-help-fs') === 'on') root.classList.add('hc-collapsed');
    } catch (e) {}
    paintReader();
    window.__hcSetupMore();
  })();
  initRail();
  /* lang-aware chrome labels: write the final language synchronously so
     freshly injected nodes never flash EN before the RU observer runs. */
  function hcT(en) {
    try {
      if (window.FS_LANG && FS_LANG.get() === 'ru') {
        var m = (FS_LANG.RU_MAP || {})[en];
        if (m) return m;
        if (window.FS_RU_CHROME && FS_RU_CHROME.MAP && FS_RU_CHROME.MAP[en]) return FS_RU_CHROME.MAP[en];
      }
    } catch (e) {}
    return en;
  }
  function hcRuCount(n, q) {
    try {
      if (window.FS_LANG && FS_LANG.get() === 'ru') {
        var w = 'результатов';
        var m10 = n % 10, h10 = n % 100;
        if (m10 === 1 && h10 !== 11) w = 'результат';
        else if (m10 >= 2 && m10 <= 4 && (h10 < 12 || h10 > 14)) w = 'результата';
        return n + ' ' + w + ' по запросу \u201c' + q + '\u201d';
      }
    } catch (e) {}
    return null;
  }
  /* "See all N results" footer under the dropdown (Wise-style). Numbers
     can't travel through the RU dictionary, so branch like hcRuCount. */
  function hcSeeAll(n) {
    try {
      if (window.FS_LANG && FS_LANG.get() === 'ru') {
        var w = 'результат', m10 = n % 10, h10 = n % 100;
        if (m10 >= 2 && m10 <= 4 && (h10 < 12 || h10 > 14)) w = 'результата';
        else if (m10 !== 1 || h10 === 11) w = 'результатов';
        return 'Показать все ' + n + ' ' + w;
      }
    } catch (e) {}
    return 'See all ' + n + ' result' + (n === 1 ? '' : 's');
  }
  /* document.title on the RU hub: brand suffix + search prefix branch
     on FS_LANG like hcSeeAll (composite strings can't use the dict). */
  function hcTitleSuffix() {
    try { if (window.FS_LANG && FS_LANG.get() === 'ru') return ' — Справка Fast Scheduler'; } catch (e) {}
    return ' — Fast Scheduler Help';
  }
  function hcSearchPrefix() {
    try { if (window.FS_LANG && FS_LANG.get() === 'ru') return 'Поиск: '; } catch (e) {}
    return 'Search: ';
  }
  window.__hcDyn = window.__hcDyn || [];
  function hcTrack(n, en) {
    try {
      var arr = window.__hcDyn;
      for (var i = 0; i < arr.length; i++) { if (arr[i].n === n) { arr[i].en = en; return; } }
      arr.push({ n: n, en: en });
    } catch (e) {}
  }
  function hcTranslateNow(root) {
    try {
      if (!(window.FS_LANG && FS_LANG.get() === 'ru')) return;
      var map = FS_LANG.RU_MAP || {};
      var dict = (window.FS_RU_CHROME && FS_RU_CHROME.MAP) || {};
      var w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null, false);
      var batch = [], tn;
      while ((tn = w.nextNode())) batch.push(tn);
      batch.forEach(function (n) {
        try {
          var p = n.parentNode;
          if (!p || (p.closest && p.closest('.fs-lang-seg'))) return;
          var tag = (p.tagName || '').toLowerCase();
          if (tag === 'script' || tag === 'style' || tag === 'code' || tag === 'pre' || tag === 'textarea') return;
          var t = n.nodeValue.trim();
          if (!t) return;
          var m = map[t] || dict[t];
          if (m && n.nodeValue.indexOf(m) === -1) {
            hcTrack(n, n.nodeValue);
            var lead = (n.nodeValue.match(/^\s*/) || [''])[0];
            var trail = (n.nodeValue.match(/\s*$/) || [''])[0];
            n.nodeValue = lead + m + trail;
          }
        } catch (e2) {}
      });
    } catch (e) {}
  }
  window.addEventListener('fs-lang-change', function (e) {
    /* RU->EN: restore synchronously translated dynamic nodes; EN->RU: the
       debounced observer plus hcTranslateNow on next render covers it. */
    try {
      var lang = (e && e.detail && e.detail.lang) || (window.FS_LANG && FS_LANG.get());
      if (lang === 'ru') return;
      var arr = window.__hcDyn || [];
      window.__hcDyn = [];
      arr.forEach(function (rec) { try { rec.n.nodeValue = rec.en; } catch (x) {} });
      /* re-render visible search UI so composite strings (counts) flip now */
      ['hcSearch', 'hcSearchH'].forEach(function (id) {
        var inp = document.getElementById(id);
        if (inp && inp.value && inp.offsetParent !== null) {
          try { inp.dispatchEvent(new Event('input', { bubbles: true })); } catch (x) {}
        }
      });
      if (window.__hcReelPaint) { try { window.__hcReelPaint(); } catch (x) {} }
    } catch (x) {}
  });
  /* floating liquid-glass section reel: prev / current / next */
  (function () {
    var reel = document.querySelector('[data-reel]');
    if (!reel) return;
    var bPrev = reel.querySelector('[data-reel-prev]');
    var bCur = reel.querySelector('[data-reel-cur]');
    var bNext = reel.querySelector('[data-reel-next]');
    var curKey = null, ticking = false;
    function railLinks() {
      var v = document.querySelector('section.view:not([hidden])');
      var nav = v && v.querySelector('[data-rail]');
      return nav ? Array.prototype.slice.call(nav.querySelectorAll('a')) : [];
    }
    function railGone() {
      if (document.documentElement.classList.contains('hc-fs')) return true;
      try { return window.matchMedia('(max-width: 1279px)').matches; } catch (e) { return true; }
    }
    function setLabel(btn, link) {
      btn.querySelector('span').textContent = link ? link.textContent.trim() : '';
      btn._rk = link ? link.getAttribute('data-rk') : null;
    }
    function jump(btn) {
      var el = btn._rk && document.getElementById(btn._rk);
      if (!el) return;
      if (el.tagName === 'DETAILS') el.open = true;
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    function paint() {
      var links = railLinks();
      var idx = -1;
      links.forEach(function (a, i) { if (a.classList.contains('on')) idx = i; });
      var sc = window.scrollY || document.documentElement.scrollTop || 0;
      var show = links.length >= 2 && sc > 480 && railGone();
      reel.hidden = !show;
      reel.setAttribute('aria-hidden', show ? 'false' : 'true');
      if (reel.classList.contains('show') !== show) reel.classList.toggle('show', show);
      if (!show) { curKey = null; return; }
      if (idx === -1) idx = 0;
      var key = links[idx].getAttribute('data-rk');
      if (key === curKey) return;
      curKey = key;
      setLabel(bPrev, links[idx - 1]);
      setLabel(bCur, links[idx]);
      setLabel(bNext, links[idx + 1]);
      bPrev.style.visibility = links[idx - 1] ? 'visible' : 'hidden';
      bNext.style.visibility = links[idx + 1] ? 'visible' : 'hidden';
      reel.classList.remove('swap');
      void reel.offsetWidth;
      reel.classList.add('swap');
    }
    bPrev.addEventListener('click', function () { jump(bPrev); });
    bCur.addEventListener('click', function () { jump(bCur); });
    bNext.addEventListener('click', function () { jump(bNext); });
    window.addEventListener('scroll', function () {
      if (ticking) return;
      ticking = true;
      var raf = window.requestAnimationFrame || function (cb) { setTimeout(cb, 100); };
      raf(function () { ticking = false; paint(); });
    }, { passive: true });
    document.addEventListener('viewchange', function () { curKey = null; paint(); });
    window.__hcReelPaint = function () { curKey = null; paint(); };
    window.addEventListener('fs-lang-change', function () { curKey = null; paint(); });
    window.addEventListener('fs-lang-applied', function () { curKey = null; paint(); });
    paint();
  })();
  window.addEventListener('hashchange', navigate);
  navigate();

  /* ---------------- sidebar ---------------- */
  /* Caret + "open all" row styling rides along with the script: the sidebar
     markup is generated here, and the page's stylesheet is generated too. */
  (function sidebarCss() {
    if (document.getElementById('fs-hc-side-css')) return;
    var st = document.createElement('style');
    st.id = 'fs-hc-side-css';
    st.textContent =
      '.hc-caret{display:inline-flex;flex:none;margin-left:2px;color:var(--text-dim);' +
      'transition:transform .3s var(--ease-apple,cubic-bezier(.3,.7,.3,1))}' +
      '.hc-caret svg{width:14px;height:14px;transform:none}' +
      '.hc-nav-item[aria-expanded="true"] .hc-caret{transform:rotate(90deg)}' +
      '.hc-subnav a.hc-sub-all{padding-left:38px;font-weight:700;font-size:.8rem;' +
      'color:var(--green-strong);margin-top:2px}' +
      '.hc-subnav a.hc-sub-all::before{content:"↗ ";font-weight:600;opacity:.75}';
    document.head.appendChild(st);
  })();

  /* one open topic at a time: the sidebar is a stack of accordions, not a
     second copy of the category pages */
  function openCat(row, sub, open) {
    if (!sideNav) return;
    Array.prototype.forEach.call(sideNav.querySelectorAll('.hc-subnav.open'), function (s) {
      if (s === sub) return;
      s.classList.remove('open');
      var r = sideNav.querySelector('.hc-nav-item[data-cat="' + s.id.replace('hc-sub-', '') + '"]');
      if (r) r.setAttribute('aria-expanded', 'false');
    });
    sub.classList.toggle('open', !!open);
    row.setAttribute('aria-expanded', open ? 'true' : 'false');
    if (open) {
      /* keep the freshly opened list in view inside the sidebar's own scroll
         box (the sidebar is sticky and scrollable on desktop) */
      var side = document.getElementById('hcSide');
      if (side && side.scrollHeight > side.clientHeight + 4) {
        var rr = row.getBoundingClientRect(), sr = side.getBoundingClientRect();
        if (rr.top < sr.top || rr.bottom > sr.bottom) {
          side.scrollTo({ top: side.scrollTop + (rr.top - sr.top) - 12, behavior: 'smooth' });
        }
      }
    }
  }

  function buildSidebar() {
    if (!sideNav) return;
    var html = '<a class="hc-nav-item" id="hcSideHome" href="#/">' +
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 11l9-8 9 8M5 10v10h14V10"/></svg>' +
      '<span>Help Center home</span></a>';
    var GRPS = [{t:'Getting started',ids:['start','scheduling','channels','bots']},{t:'Plans & growth',ids:['admins','premium','referral','limits']},{t:'Setup',ids:['timezone','language','export','import','backup','media_storage']},{t:'Help & reference',ids:['tools','tips','feedback','faq','commands','errors']},{t:'About',ids:['privacy','legal','contact','config']}];
    var byCat = {};
    SIDE.forEach(function (cc) { byCat[cc.id] = cc; });
    var emitted = {};
    function navRow(c) {
      var hasKids = !!(c.kids && c.kids.length);
      html += '<a class="hc-nav-item" data-cat="' + c.id + '" href="c/' + c.id + '/"' +
        (hasKids ? ' aria-expanded="false" aria-controls="hc-sub-' + c.id + '"' : '') + '>' +
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + c.icon + '</svg>' +
        '<span>' + c.title + '</span><span class="n">' + c.n + '</span>' +
        (hasKids ? '<span class="hc-caret" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg></span>' : '') +
        '</a>';
      if (hasKids) {
        html += '<div class="hc-subnav" id="hc-sub-' + c.id + '"><div class="hc-subnav-in">';
        c.kids.forEach(function (k) { html += '<a href="a/' + k.id + '/" data-art="' + k.id + '">' + k.t + '</a>'; });
        /* the category page still exists (it is the browsable "all topics"
           view); this keeps it one click away without making the row itself
           navigate */
        html += '<a class="hc-sub-all" href="c/' + c.id + '/">Open all ' + c.n + ' articles</a>';
        html += '</div></div>';
      }
    }
    GRPS.forEach(function (g) {
      var items = [];
      g.ids.forEach(function (id) { if (byCat[id]) items.push(byCat[id]); });
      if (!items.length) return;
      html += '<div class="hc-grp">' + g.t + '</div>';
      items.forEach(function (c) { emitted[c.id] = 1; navRow(c); });
    });
    SIDE.forEach(function (c) {
      if (emitted[c.id]) return;
      navRow(c);
    });
    sideNav.innerHTML = html;
    sideNav.addEventListener('click', function (ev) {
      var row = ev.target.closest && ev.target.closest('.hc-nav-item[data-cat]');
      var sub = row && document.getElementById('hc-sub-' + row.getAttribute('data-cat'));
      /* A topic row with articles expands its list right here in the sidebar.
         It used to navigate to the category page, so picking a topic threw the
         reader onto another page instead of showing what is inside. */
      if (row && sub) {
        ev.preventDefault();
        openCat(row, sub, !sub.classList.contains('open'));
      }
      document.body.classList.remove('hc-side-open');
    });
    sideNav.addEventListener('keydown', function (ev) {
      if (ev.key !== 'Enter' && ev.key !== ' ') return;
      var row = ev.target.closest && ev.target.closest('.hc-nav-item[data-cat]');
      var sub = row && document.getElementById('hc-sub-' + row.getAttribute('data-cat'));
      if (!sub) return;
      ev.preventDefault();
      openCat(row, sub, !sub.classList.contains('open'));
    });
  }
  buildSidebar();

  /* The search button shows the key that actually opens help search:
     Ctrl/Cmd+K. There is no single-letter search shortcut. */
  (function searchKeyLabel() {
    var b = document.getElementById('hcSBtn');
    if (!b) return;
    var mac = false;
    try { mac = /Mac|iPhone|iPad|iPod/.test(navigator.platform || navigator.userAgent || ''); } catch (e) {}
    var label = mac ? '\u2318K' : 'Ctrl K';
    b.textContent = label;
    b.title = 'Search (' + (mac ? '\u2318' : 'Ctrl') + '+K)';
    b.setAttribute('aria-label', 'Search help topics (' + (mac ? '\u2318' : 'Ctrl') + '+K)');
  })();

  var scrim = document.getElementById('hcScrim');
  var menuBtn = document.getElementById('hcMenuBtn');
  if (menuBtn) menuBtn.addEventListener('click', function () { document.body.classList.toggle('hc-side-open'); });
  if (scrim) scrim.addEventListener('click', function () { document.body.classList.remove('hc-side-open'); });

  /* ---------------- mini-AI natural-language search ----------------
     Understands everyday phrasing: strips filler words, expands synonyms
     ("can't post" -> not posted / sending), tolerates typos on long words,
     and ranks by how much of the question each article actually answers. */
  var STOP = {};
  'the a an and or of to for in on with your you my it is are be can how what when why do does i we they this that at as by from get make if not no want need about'.split(' ').forEach(function (w) { STOP[w] = 1; });
  var SYN = [
    ['sender', 'bot', 'bots', 'own bot', 'custom bot', 'botfather', 'token', 'newbot'],
    ['schedule', 'scheduled', 'scheduling', 'queue', 'queued', 'post later'],
    ['recurring', 'repeat', 'repeating', 'regular', 'auto repost'],
    ['timezone', 'time zone', 'time zones', 'utc', 'gmt'],
    ['delete', 'remove', 'cleanup', 'clean up'],
    ['edit', 'change', 'modify', 'update'],
    ['premium', 'pro', 'paid', 'subscription', 'upgrade'],
    ['limit', 'limits', 'cap', 'quota'],
    ['media', 'photo', 'photos', 'video', 'videos', 'image', 'images', 'album', 'albums', 'gif', 'gifs', 'sticker', 'stickers', 'voice', 'document', 'documents', 'file', 'files', 'poll', 'polls', 'quiz', 'quizzes'],
    ['storage', 'box', 'boxes', 'library', 'media storage'],
    ['channel', 'channels'],
    ['payment', 'pay', 'buy', 'purchase', 'stars', 'invoice', 'refund', 'refunds', 'crypto', 'price', 'pricing', 'cost'],
    ['backup', 'export', 'import', 'restore', 'fsback', 'fspback', 'migrate', 'migration', 'transfer', 'move'],
    ['admin', 'administrators', 'permission', 'permissions', 'rights'],
    ['signature', 'signatures', 'footer'],
    ['language', 'lang', 'english', 'russian', 'translation'],
    ['search', 'find', 'look up'],
    ['calendar', 'month view'],
    ['stats', 'statistics', 'usage', 'counter'],
    ['error', 'errors', 'problem', 'problems', 'issue', 'not working', 'fails', 'failed', 'stuck', 'fix', 'troubleshoot', 'troubleshooting'],
    ['late', 'delay', 'delayed', 'not posted', 'missing', 'skipped'],
    ['referral', 'invite', 'friends', 'bonus', 'promo', 'promocode', 'coupon', 'free days'],
    ['account', 'start', 'begin', 'setup', 'set up', 'onboarding', 'getting started', 'connect'],
    ['cancel', 'stop', 'pause'],
    ['post', 'posts', 'posting', 'publish', 'publishing', 'send', 'sending', 'message', 'messages'],
    ['feedback', 'support', 'contact', 'ticket'],
    ['auto', 'automatically', 'automatic', 'autopilot']
  ];
  function synth(w) {
    for (var i = 0; i < SYN.length; i++) if (SYN[i].indexOf(w) !== -1) return SYN[i];
    return [w];
  }
  function expand(q) {
    var words = q.split(/\s+/).filter(Boolean);
    var sets = [], all = [], key = [];
    words.forEach(function (w) {
      if (STOP[w]) return;
      key.push(w);
      var s = synth(w);
      sets.push(s);
      s.forEach(function (x) { if (all.indexOf(x) === -1) all.push(x); });
    });
    return { words: key, sets: sets, all: all };
  }
  function fuzzyPrefix(word, target) {
    var n = Math.max(4, word.length - 2);
    return target.slice(0, n) === word.slice(0, n);
  }
  function score(sec, q, ex) {
    var t = norm(sec.t), b = norm(sec.b), f = norm(sec.f);
    var s = 0;
    if (q.length > 2) {
      if (b.indexOf(q) !== -1 || f.indexOf(q) !== -1 || t.indexOf(q) !== -1) {
        s += 60;
        if (t.indexOf(q) !== -1) s += 60;
        if (f.indexOf(q) !== -1) s += 10;
      }
    }
    var titleWords = t.split(/\s+/);
    var bodyWords = (t + ' ' + b + ' ' + f).split(/\s+/);
    var matched = 0;
    ex.words.forEach(function (w) {
      var set = [w];
      for (var i = 0; i < ex.sets.length; i++) if (ex.sets[i][0] === w) { set = ex.sets[i]; break; }
      var wordScore = 0;
      titleWords.forEach(function (x) {
        if (x === w) wordScore = Math.max(wordScore, 120);
        else if (x.indexOf(w) === 0) wordScore = Math.max(wordScore, 55);
        else if (x.indexOf(w) !== -1) wordScore = Math.max(wordScore, 34);
        else if (w.length >= 5 && fuzzyPrefix(w, x)) wordScore = Math.max(wordScore, 20);
      });
      if (!wordScore && set.length > 1) {
        set.forEach(function (syn) {
          if (b.indexOf(syn) !== -1 || f.indexOf(syn) !== -1) wordScore = Math.max(wordScore, 15);
          titleWords.forEach(function (x) {
            if (x.indexOf(syn) === 0) wordScore = Math.max(wordScore, 24);
          });
        });
      }
      if (!wordScore && bodyWords.indexOf(w) !== -1) wordScore = 12;
      if (!wordScore && bodyWords.some(function (x) { return x.indexOf(w) === 0; })) wordScore = 22;
      if (wordScore > 0) { s += wordScore; matched++; }
      else s -= 45;
    });
    if (ex.words.length > 1 && matched === ex.words.length) s += 25;
    return s;
  }

  /* SECURITY: entity-encode (never strip) so no raw <, >, &, " or ' can
     reach an innerHTML sink. */
  function escapeHtml(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  /* Mark matches of q in RAW text: every literal segment is escaped, only
     the fixed <mark> tags are inserted as markup - safe by construction. */
  function markText(raw, q) {
    if (!q) return escapeHtml(raw);
    var out = '', low = String(raw).toLowerCase(), i = 0, idx;
    while ((idx = low.indexOf(q, i)) !== -1) {
      out += escapeHtml(raw.slice(i, idx)) + '<mark>' + escapeHtml(raw.slice(idx, idx + q.length)) + '</mark>';
      i = idx + q.length;
    }
    return out + escapeHtml(raw.slice(i));
  }

    function snippet(b, q) {
    var i = norm(b).indexOf(q);
    if (i === -1) return b.slice(0, 120);
    var start = Math.max(0, i - 42);
    var s = b.slice(start, start + 130);
    return (start > 0 ? '\u2026' : '') + s + (start + 130 < b.length ? '\u2026' : '');
  }

  function attachSearch(input, results) {
    if (!input || !results) return;
    var curIdx = -1;
    var resButtons = [];

    function close() {
      results.hidden = true; results.innerHTML = '';
      resButtons = []; curIdx = -1;
      input.setAttribute('aria-expanded', 'false');
    }
    function moveCursor(delta) {
      if (!resButtons.length) return;
      curIdx = (curIdx + delta + resButtons.length) % resButtons.length;
      resButtons.forEach(function (b, i) { b.classList.toggle('cur', i === curIdx); });
      resButtons[curIdx].scrollIntoView({ block: 'nearest' });
    }
    function render(q, ex, scored, total) {
      var html = '';
      /* "You mean" is an empty-state aid only — when there are results, the
         Best result card speaks for itself. */
      var top = scored[0], rest = scored.slice(1);
      /* a section split only makes sense when one result clearly dominates */
      var isClear = top.s >= 150 && (!rest.length || top.s >= rest[0].s + 50);
      if (isClear) {
        html += '<div class="hc-res-sec">' + hcT('Best result') + '</div>';
        html += '<button type="button" class="hc-res hc-res-best" role="option" data-art="' + top.sec.id + '">' +
          '<span class="hc-res-top"><span class="hc-res-t">' + markText(top.sec.t, q) + '</span>' +
          '<span class="hc-res-cat">' + escapeHtml(CATS[top.sec.c] || '') + '</span></span>' +
          '<p class="hc-res-s">' + markText(snippet(top.sec.b, q), q) + '</p></button>';
        if (rest.length) {
          html += '<div class="hc-res-sec">' + hcT('More results') + '</div>';
          rest.forEach(function (x) {
            var s = x.sec;
            html += '<button type="button" class="hc-res" role="option" data-art="' + s.id + '">' +
              '<span class="hc-res-top"><span class="hc-res-t">' + markText(s.t, q) + '</span>' +
              '<span class="hc-res-cat">' + escapeHtml(CATS[s.c] || '') + '</span></span>' +
              '<p class="hc-res-s">' + markText(snippet(s.b, q), q) + '</p></button>';
          });
        }
      } else {
        scored.forEach(function (x) {
          var s = x.sec;
          html += '<button type="button" class="hc-res" role="option" data-art="' + s.id + '">' +
            '<span class="hc-res-top"><span class="hc-res-t">' + markText(s.t, q) + '</span>' +
            '<span class="hc-res-cat">' + escapeHtml(CATS[s.c] || '') + '</span></span>' +
            '<p class="hc-res-s">' + markText(snippet(s.b, q), q) + '</p></button>';
        });
      }
      html += '<a class="hc-res-all" href="#/s/' + encodeURIComponent(q) + '">' +
        hcSeeAll(total) + ' ' + CHEV_SVG + '</a>';
      results.innerHTML = html;
      hcTranslateNow(results);
      results.hidden = false;
      input.setAttribute('aria-expanded', 'true');
      resButtons = Array.prototype.slice.call(results.querySelectorAll('.hc-res'));
      curIdx = 0;
      if (resButtons[0]) resButtons[0].classList.add('cur');
    }
    function renderEmpty(q, ex) {
      var ai = aiLabel(q);
      var aiHtml = ai ? '<div class="hc-ai-line"><span class="hc-ai-dot"></span>' + hcT('You mean:') + ' <b>' + escapeHtml(ai) + '</b></div>' : '';
      var sug = DATA.filter(function (sec) {
        var t = norm(sec.t);
        return ex.all.some(function (w) {
          return w.length > 2 && (t.indexOf(w) !== -1 || t.split(/\s+/).some(function (x) { return x.indexOf(w) === 0; }));
        });
      }).slice(0, 4);
      var html = '<div class="hc-empty-ill">' + ILL_SVG + '</div>' +
        '<div class="hc-empty-q">&ldquo;' + escapeHtml(q) + '&rdquo;</div>' +
        '<div class="hc-empty-t">' + hcT('No results found.') + '</div>' +
        '<div class="hc-empty-s">' + hcT('Try different or more general keywords.') + '</div>';
      if (aiHtml) html += aiHtml;
      if (sug.length) {
        html += '<div class="hc-sug-h">' + hcT('Maybe you meant:') + '</div>';
        sug.forEach(function (sg) {
          html += '<button type="button" class="hc-res" role="option" data-art="' + sg.id + '">' +
            '<span class="hc-res-top"><span class="hc-res-t">' + escapeHtml(sg.t) + '</span>' +
            '<span class="hc-res-cat">' + escapeHtml(CATS[sg.c] || '') + '</span></span></button>';
        });
      }
      html += '<div class="hc-sug-h">' + hcT('Still stuck?') + ' <a href="https://t.me/FastSchedulerSupport_bot" target="_blank" rel="noopener noreferrer">' + hcT('Ask in the bot') + '</a> ' + hcT('\u2014 a human answers every ticket.') + '</div>';
      results.innerHTML = html;
      hcTranslateNow(results);
      results.hidden = false;
      resButtons = Array.prototype.slice.call(results.querySelectorAll('.hc-res'));
      curIdx = resButtons.length ? 0 : -1;
      if (resButtons[0]) resButtons[0].classList.add('cur');
      input.setAttribute('aria-expanded', 'true');
    }
    function run() {
      var q = norm(input.value.trim());
      if (q.length < 2) { close(); return; }
      var ex = expand(q);
      var ranked;
      if (window.HelpAI) {
        ranked = window.HelpAI.scoreAll(q, DATA).map(function (x) { return { sec: x.doc, s: x.score }; });
        DATA.forEach(function (sec) {
          if (ranked.some(function (r) { return r.sec === sec; })) return;
          var s2 = score(sec, q, ex);
          if (s2 > 0) ranked.push({ sec: sec, s: s2 });
        });
        ranked.sort(function (a, b) { return b.s - a.s; });
      } else {
        ranked = DATA.map(function (sec) { return { sec: sec, s: score(sec, q, ex) }; })
          .filter(function (x) { return x.s > 0; })
          .sort(function (a, b) { return b.s - a.s; });
      }
      /* relevance floor: a single word that appears in every article
         ("post") must not make the whole help center a "result" */
      if (ranked.length) {
        var floor = Math.max(30, ranked[0].s * 0.5);
        ranked = ranked.filter(function (x) { return x.s >= floor; });
      }
      var scored = ranked.slice(0, 6);
      if (!scored.length) renderEmpty(q, ex); else render(q, ex, scored, ranked.length);
    }

    var timer = null;
    input.addEventListener('input', function () {
      clearTimeout(timer);
      timer = setTimeout(run, 130);
    });
    input.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown') { e.preventDefault(); moveCursor(1); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); moveCursor(-1); }
      else if (e.key === 'Enter') {
        e.preventDefault();
        var qraw = input.value.trim();
        if (qraw.length >= 2) {
          var dest = '#/s/' + encodeURIComponent(qraw);
          if (location.hash === dest) renderSearchPage(qraw); else location.hash = dest;
        }
      } else if (e.key === 'Escape') {
        input.value = ''; close(); input.blur();
      }
    });
    results.addEventListener('click', function (e) {
      var b = e.target.closest('.hc-res');
      if (b) location.href = 'a/' + b.getAttribute('data-art') + '/';
    });
    document.addEventListener('click', function (e) {
      var box = input.closest('.hc-search, .hc-hsearch');
      if (box && !(e.target.closest && box.contains(e.target))) close();
    });
  }

  var heroInput = document.getElementById('hcSearch');
  var heroResults = document.getElementById('hcResults');
  var headInput = document.getElementById('hcSearchH');
  var headResults = document.getElementById('hcResultsH');
  attachSearch(heroInput, heroResults);
  attachSearch(headInput, headResults);

  function closeAllResults() {
    if (heroResults) { heroResults.hidden = true; }
    if (headResults) { headResults.hidden = true; }
  }

  /* ---------------- full search results page (#/s/<query>) ---------------- */
  var searchList = document.getElementById('hcSearchList');
  var searchEmpty = document.getElementById('hcSearchEmpty');
  var searchQEl = document.getElementById('hcSearchQ');
  var searchMeta = document.getElementById('hcSearchMeta');
  var searchSug = document.getElementById('hcSearchSug');
  var CHEV_SVG = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="9 18 15 12 9 6"/></svg>';
  var ILL_SVG = '<svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><polyline points="13 2 13 9 20 9"/><circle cx="10.5" cy="14" r="2.6"/><line x1="12.4" y1="15.9" x2="14.5" y2="18"/></svg>';

  function docHref(sec) { return sec.href ? sec.href : ('a/' + sec.id + '/'); }
  function resultRow(sec, q) {
    return '<a class="hc-row" href="' + docHref(sec) + '"><span class="hc-row-t">' +
      markText(sec.t, q) + '</span><span class="hc-row-m">' +
      escapeHtml(CATS[sec.c] || '') + '</span>' + CHEV_SVG + '</a>';
  }

  function shuffle(a) {
    var out = a.slice();
    for (var i = out.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var t = out[i]; out[i] = out[j]; out[j] = t;
    }
    return out;
  }
  function suggestionsFor(ex, cap) {
    var sug = DATA.filter(function (sec) {
      var t = norm(sec.t);
      return ex.all.some(function (w) {
        return w.length > 2 && (t.indexOf(w) !== -1 || t.split(/\s+/).some(function (x) { return x.indexOf(w) === 0; }));
      });
    });
    /* "try these instead" is a fresh draw every time, not the same first six
       documents in source order on every empty search */
    sug = shuffle(sug).slice(0, cap);
    if (!sug.length) sug = shuffle(DATA).slice(0, cap);
    return sug.map(function (sg) {
      return '<a class="hc-row" href="a/' + sg.id + '/"><span class="hc-row-t">' +
        escapeHtml(sg.t) + '</span><span class="hc-row-m">' + escapeHtml(CATS[sg.c] || '') +
        '</span>' + CHEV_SVG + '</a>';
    }).join('');
  }

  var searchCat = 'all';
  function renderSearchFilters(hits, q) {
    var el = document.getElementById('hcSearchFilters');
    if (!el) return;
    var present = {};
    hits.forEach(function (x) { present[x.sec.c] = true; });
    var order = Object.keys(present).sort();
    if (order.length < 2) { el.hidden = true; el.innerHTML = ''; return; }
    el.hidden = false;
    var html = '<button type="button" class="hc-fchip' + (searchCat === 'all' ? ' on' : '') +
      '" data-fcat="all">All</button>';
    order.forEach(function (cid) {
      html += '<button type="button" class="hc-fchip' + (searchCat === cid ? ' on' : '') +
        '" data-fcat="' + escapeHtml(cid) + '">' + escapeHtml(CATS[cid] || cid) + '</button>';
    });
    el.innerHTML = html;
    hcTranslateNow(el);
    el.querySelectorAll('.hc-fchip').forEach(function (b) {
      b.addEventListener('click', function () {
        searchCat = b.getAttribute('data-fcat');
        renderSearchPage(q);
      });
    });
  }

  function renderSearchPage(q) {
    if (!searchList || !DATA || !STOP) return;
    q = String(q || '').trim().slice(0, 200);
    if (window.__blogSearchQ !== q) { window.__blogSearchQ = q; searchCat = 'all'; }
    if (searchQEl) searchQEl.textContent = q;
    if (headInput) headInput.value = q;
    document.title = hcSearchPrefix() + q + hcTitleSuffix();
    var ex = expand(norm(q));
    var hits;
    if (window.HelpAI) {
      hits = window.HelpAI.scoreAll(q, DATA).map(function (x) { return { sec: x.doc, s: x.score }; });
      DATA.forEach(function (sec) {
        if (hits.some(function (r) { return r.sec === sec; })) return;
        var s = score(sec, norm(q), ex);
        if (s > 0) hits.push({ sec: sec, s: s });
      });
      hits.sort(function (a, b) { return b.s - a.s; });
    } else {
      hits = DATA.map(function (sec) { return { sec: sec, s: score(sec, norm(q), ex) }; })
        .filter(function (x) { return x.s > 0; })
        .sort(function (a, b) { return b.s - a.s; });
    }
    if (hits.length) {
      var hfloor = Math.max(30, hits[0].s * 0.5);
      hits = hits.filter(function (x) { return x.s >= hfloor; });
    }
    hits = hits.slice(0, 40);
    renderSearchFilters(hits, q);
    if (searchMeta) searchMeta.textContent = hits.length
      ? (hcRuCount(hits.length, q) || (hits.length + ' result' + (hits.length > 1 ? 's' : '') + ' for “' + q + '”'))
      : hcT('0 results');
    if (hits.length) {
      if (searchEmpty) searchEmpty.hidden = true;
      searchList.hidden = false;
      if (searchSug) searchSug.innerHTML = '';
      hits = hits.filter(function (x) { return searchCat === 'all' || x.sec.c === searchCat; });
      var top = hits[0], rest = hits.slice(1);
      /* one clear winner gets a labeled hero card; the rest stay plain rows */
      var isClear = top.s >= 150 && (!rest.length || top.s >= rest[0].s + 50);
      var html = '';
      if (isClear) {
        html += '<a class="hc-best" href="' + docHref(top.sec) + '">' +
          '<span class="hc-best-label">' + hcT('Best result') + '</span>' +
          '<b>' + markText(top.sec.t, norm(q)) + '</b>' +
          '<span class="hc-best-cat">' + escapeHtml(CATS[top.sec.c] || '') + '</span>' +
          '<p>' + markText(snippet(top.sec.b, norm(q)), norm(q)) + '</p></a>';
        if (rest.length) html += '<div class="hc-sempty-h" style="max-width:760px;margin:0 auto 6px;font-size:.8rem;font-weight:700;color:var(--text-dim)">' + hcT('All results') + '</div>';
        html += rest.map(function (x) { return resultRow(x.sec, norm(q)); }).join('');
      } else {
        html = hits.map(function (x) { return resultRow(x.sec, norm(q)); }).join('');
      }
      searchList.innerHTML = html;
      hcTranslateNow(searchList);
    } else {
      searchList.hidden = true;
      searchList.innerHTML = '';
      if (searchEmpty) {
        searchEmpty.hidden = false;
        if (searchSug) searchSug.innerHTML = ex.words.length ? suggestionsFor(ex, 6) : suggestionsFor({ all: [] }, 6);
      }
    }
  }

  /* ---------------- sidebar collapse (desktop, persisted) ---------------- */
  var sideToggle = document.getElementById('hcSideToggle');
  var sideReveal = document.getElementById('hcSideReveal');
  function setSide(collapsed, persist) {
    document.documentElement.classList.toggle('hc-collapsed', !!collapsed);
    if (persist) { try { localStorage.setItem('fs-help-side', collapsed ? 'closed' : 'open'); } catch (e) {} }
  }
  if (sideToggle) sideToggle.addEventListener('click', function () {
    /* phones: the sidebar is a drawer — the ">" close button must close the
       DRAWER, not flip the desktop collapsed flag (which did nothing) */
    if (window.matchMedia('(max-width: 1020px)').matches) {
      document.body.classList.remove('hc-side-open');
      return;
    }
    setSide(true, true);
  });
  if (sideReveal) sideReveal.addEventListener('click', function () { setSide(false, true); });

  function focusSearch() {
    var onHome = !document.querySelector('.view[data-view="home"]') || !document.querySelector('.view[data-view="home"]').hidden;
    var target = onHome && heroInput ? heroInput : (headInput || heroInput);
    if (target) { target.focus(); target.select(); }
  }

  /* keyboard shortcuts: Ctrl/Cmd+K = search, O = topics sidebar.
     There is deliberately NO single-letter search key. */
  document.addEventListener('keydown', function (e) {
    var el = document.activeElement;
    var tag = (el && el.tagName) || '';
    if (tag === 'INPUT' || tag === 'TEXTAREA' || (el && el.isContentEditable)) return;
    var mod = e.ctrlKey || e.metaKey || e.altKey;
    /* Settings > Hotkeys switches the whole set off: these keys stand down
       with every other shortcut, and the keycap hints disappear with them. */
    if (document.documentElement.getAttribute('data-keys') === 'off') return;
    var isK = (e.key === 'k' || e.key === 'K') && (e.ctrlKey || e.metaKey);
    if (isK) { e.preventDefault(); focusSearch(); return; }
    /* O = topics. Guard: ignore chords mid-recording in the hotkeys editor
       (its capture-phase handler stops them; this belt-and-suspenders check
       keeps a sequence like O then B from flipping the sidebar mid-chord). */
    var hk = window.FS_HK_RECORDING;
    if ((e.key === 'o' || e.key === 'O') && !mod && window.innerWidth > 860 && !hk) {
      e.preventDefault();
      setSide(!document.documentElement.classList.contains('hc-collapsed'), true);
      return;
    }
    /* 1-9: jump to the Nth topic in the sidebar (help center) */
    if (/^[1-9]$/.test(e.key) && !mod && window.innerWidth > 860 && !hk) {
      var sideNav = document.getElementById('hcSideNav');
      var item = sideNav && sideNav.children[e.key - 1];
      if (item) {
        e.preventDefault();
        item.click();
        return;
      }
    }
  });

  /* deep link support: help.html?q=... (used by the site SearchAction) */
  try {
    var qs = new URLSearchParams(location.search).get('q');
    if (qs && qs.trim()) {
      location.hash = '#/s/' + encodeURIComponent(qs.trim().slice(0, 200));
      history.replaceState(null, '', location.pathname);  /* keep the URL clean */
    }
  } catch (e) {}

  /* try-asking chips -> prefill + run search */
  document.addEventListener('click', function (e) {
    var chip = e.target.closest && e.target.closest('.hc-chip-q');
    if (!chip) return;
    e.preventDefault();
    var q = chip.getAttribute('data-q') || chip.textContent.trim();
    location.hash = '#/s/' + encodeURIComponent(q);
  });

  /* jump-to-section links inside articles (and the mobile Contents sheet) */
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('.hc-jump-n a, .hc-toc-list a');
    if (!a) return;
    var id = a.getAttribute('data-jid');
    var target = id && document.getElementById(id);
    if (!target) return;
    e.preventDefault();
    var pv = tocParts(a);
    closeToc(pv.sheet, pv.scrim);
    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });

  /* mobile Contents sheet — fully delegated: every article view carries its
     own fab/sheet/scrim, so we always resolve them from the event target */
  function tocParts(el) {
    var view = el.closest && el.closest('.view[data-view="article"]');
    return view
      ? { sheet: view.querySelector('[data-toc-sheet]'), scrim: view.querySelector('[data-toc-scrim]') }
      : { sheet: null, scrim: null };
  }
  function openToc(sheet, scrim) {
    if (!sheet) return;
    sheet.hidden = false; scrim.hidden = false;
    void sheet.offsetWidth; /* reflow so unhide -> open animates */
    sheet.classList.add('open'); scrim.classList.add('open');
  }
  function closeToc(sheet, scrim) {
    if (!sheet || sheet.hidden) return;
    sheet.classList.remove('open'); scrim.classList.remove('open');
    setTimeout(function () { sheet.hidden = true; scrim.hidden = true; }, 400);
  }
  document.addEventListener('click', function (e) {
    var fab = e.target.closest && e.target.closest('[data-toc-fab]');
    if (fab) {
      e.preventDefault();
      var p = tocParts(fab);
      openToc(p.sheet, p.scrim);
      return;
    }
    if (e.target.closest && e.target.closest('[data-toc-close]')) {
      var p2 = tocParts(e.target);
      closeToc(p2.sheet, p2.scrim);
      return;
    }
    if (e.target.classList && e.target.classList.contains('hc-toc-scrim')) {
      var p3 = tocParts(e.target);
      closeToc(p3.sheet, p3.scrim);
    }
  });
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    var view = document.querySelector('.view[data-view="article"]:not([hidden])');
    if (view) { var p = tocParts(view); closeToc(p.sheet, p.scrim); }
  });
  /* show the Contents pill only on article views that actually have sections */
  function syncTocFab() {
    var view = document.querySelector('.view[data-view="article"]:not([hidden])');
    var fab = view && view.querySelector('[data-toc-fab]');
    if (fab) fab.hidden = !view.querySelector('.hc-jump-pop a');
  }
  document.addEventListener('viewchange', syncTocFab);
  setTimeout(syncTocFab, 60);

  /* "Try asking": 3 random chips per visit instead of the full wall */
  (function () {
    var row = document.querySelector('.hc-try .hc-chiprow');
    if (!row) return;
    var kids = Array.prototype.slice.call(row.children);
    kids.sort(function () { return Math.random() - .5; });
    kids.forEach(function (c) { row.appendChild(c); });
    kids.slice(3).forEach(function (c) { c.hidden = true; });
  })();

  /* reading progress on article pages */
  function updateProgress() {
    if (!progressBar) return;
    var el = document.querySelector('.view[data-view="article"]:not([hidden]) .hc-art');
    if (!el) { progressBar.style.width = '0'; return; }
    var rect = el.getBoundingClientRect();
    var total = Math.max(1, el.offsetHeight - window.innerHeight * 0.6);
    var done = Math.min(1, Math.max(0, (80 - rect.top) / total));
    progressBar.style.width = (done * 100).toFixed(2) + '%';
  }
  window.addEventListener('scroll', updateProgress, { passive: true });
  window.addEventListener('resize', updateProgress);

  /* sticky header deepens once the page scrolls (Apple-style elevation) */
  var siteHeader = document.querySelector('header.site');
  function updateHead() {
    if (siteHeader) siteHeader.classList.toggle('scrolled', window.scrollY > 8);
  }
  updateHead();
  window.addEventListener('scroll', updateHead, { passive: true });
})();
