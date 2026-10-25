// Site settings: theme, motion, effects. One controller for every page —
// state lives in localStorage, so a change here applies site-wide.
// (No-flash reads happen inline in each page's <head>.)
(function () {
  var root = document.documentElement;
  var btn = document.getElementById('settingsBtn');
  var menu = document.getElementById('settingsMenu');
  var wrap = btn ? btn.parentElement : null;
  var closeT = null, hoverT = null;

  /* The menu drops below the gear by default. From the side rail (or any
     short viewport) there may be no room below, which used to park the
     bottom rows off-screen with no way to reach them — flip it above the
     gear instead and let it scroll internally as a last resort. */
  function placeMenu() {
    if (!menu || !wrap || !btn) return;
    menu.classList.remove('menu-up');
    menu.style.maxHeight = '';
    var r = menu.getBoundingClientRect();
    var gearTop = btn.getBoundingClientRect().top;
    var below = window.innerHeight - 8 - r.top;   /* room under the gear */
    var above = gearTop - 12 - 8;                 /* room over the gear  */
    if (r.height > below && above > below) {
      menu.classList.add('menu-up');
      if (r.height > above) menu.style.maxHeight = Math.max(120, above) + 'px';
    } else if (r.height > below) {
      menu.style.maxHeight = Math.max(120, below) + 'px';
    }
  }
  function openMenu() {
    if (menu && !menu.classList.contains('open')) {
      clearTimeout(closeT);
      menu.classList.add('open');
      if (btn) btn.setAttribute('aria-expanded', 'true');
      placeMenu();
    }
  }
  function closeMenu() {
    if (menu && menu.classList.contains('open')) {
      menu.classList.remove('open');
      if (btn) btn.setAttribute('aria-expanded', 'false');
    }
  }

  if (btn && menu && wrap) {
    if (window.matchMedia && matchMedia('(hover: hover) and (pointer: fine)').matches) {
      wrap.addEventListener('mouseenter', function () { clearTimeout(closeT); hoverT = setTimeout(openMenu, 70); });
      wrap.addEventListener('mouseleave', function () { clearTimeout(hoverT); closeT = setTimeout(closeMenu, 160); });
    }
    btn.addEventListener('click', function (e) {
      e.stopPropagation(); clearTimeout(hoverT);
      menu.classList.contains('open') ? closeMenu() : openMenu();
    });
    menu.addEventListener('click', function (e) { if (e.target.closest('a')) closeMenu(); });
    document.addEventListener('click', function (e) { if (!wrap.contains(e.target)) closeMenu(); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') { closeSiteMenu(); closeMenu(); } });
  }

  /* ---------- Help quick-search popover (hangs off the navbar Help pill) ---------- */
  var siteWrap = document.querySelector('.site-menu-wrap');
  var sitePop = document.getElementById('siteMenu');
  function openSiteMenu() {
    if (sitePop && !sitePop.classList.contains('open')) {
      sitePop.classList.add('open');
      var row = siteWrap && siteWrap.querySelector('.site-menu-row');
      if (row) row.setAttribute('aria-expanded', 'true');
    }
  }
  function closeSiteMenu() {
    if (sitePop && sitePop.classList.contains('open')) {
      sitePop.classList.remove('open');
      var row = siteWrap && siteWrap.querySelector('.site-menu-row');
      if (row) row.setAttribute('aria-expanded', 'false');
    }
  }
  if (siteWrap && sitePop) {
    var sCloseT = null, sHoverT = null;
    var finePointer = window.matchMedia && matchMedia('(hover: hover) and (pointer: fine)').matches;

    /* Hovering the Help Center pill opens the quick-search popover (desktop
       fine pointers only). The pill itself stays a plain navigation link. */
    var rowIsHelp = /help\.html|help\//.test(
      (siteWrap.querySelector('.site-menu-row') || {}).getAttribute &&
      siteWrap.querySelector('.site-menu-row').getAttribute('href') || '');
    function keepOpen() { clearTimeout(sCloseT); }
    if (finePointer && rowIsHelp) {
      siteWrap.addEventListener('mouseenter', function () { clearTimeout(sCloseT); sHoverT = setTimeout(openSiteMenu, 60); });
      siteWrap.addEventListener('mouseleave', function () { clearTimeout(sHoverT); sCloseT = setTimeout(closeSiteMenu, 450); });
    }
    sitePop.addEventListener('mouseenter', keepOpen);
    sitePop.addEventListener('pointerdown', keepOpen);
    sitePop.addEventListener('focusin', keepOpen);

    /* The row is a genuine link that should just NAVIGATE — on every page,
       desktop and mobile. It used to intercept plain left clicks on desktop
       and open the quick-search popover instead, which read as "Main site
       opens the help search". The search stays reachable through the chevron
       row and "Open Help Center" inside the popover; direct navigation wins
       here (cmd/ctrl/middle-click still work natively). */
    var siteRow = siteWrap.querySelector('.site-menu-row');
    if (siteRow) {
      /* phones: no hover, popover is cramped and it looks broken */
      var coarse = window.matchMedia && matchMedia('(hover: none), (pointer: coarse)').matches;
      if (coarse) {
        siteRow.addEventListener('click', function () { closeMenu(); closeSiteMenu(); });
      }
    }
    sitePop.addEventListener('click', function (e) {
      if (e.target.closest('a')) { keepOpen(); closeSiteMenu(); }
    });
    document.addEventListener('click', function (e) {
      if (!siteWrap.contains(e.target)) closeSiteMenu();
    });
    /* the chevron on the Help row toggles the quick-search popover without
       navigating (the row itself is a plain navigation link now). On the help
       center page the row is "Main site" — it has no chevron anyway. */
    var chev = siteWrap.querySelector('.site-menu-row .chev');
    if (chev) {
      chev.style.pointerEvents = 'auto';
      chev.addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();
        if (sitePop.classList.contains('open')) closeSiteMenu(); else openSiteMenu();
      });
    }
  }

  /* ---------- Dark mode ---------- */
  var rowDark = document.getElementById('rowDark');
  function syncDark() {
    if (rowDark) rowDark.setAttribute('aria-pressed', root.getAttribute('data-theme') === 'dark' ? 'true' : 'false');
  }
  if (rowDark) {
    rowDark.addEventListener('click', function (e) { e.stopPropagation();
      var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      try { localStorage.setItem('theme', next); } catch (err) {}
      syncDark();
    });
  }

  /* ---------- Animations (motion) ---------- */
  var rowAnim = document.getElementById('rowAnim');
  function syncAnim() {
    if (rowAnim) rowAnim.setAttribute('aria-pressed', root.getAttribute('data-motion') === 'off' ? 'false' : 'true');
  }
  if (rowAnim) {
    rowAnim.addEventListener('click', function (e) { e.stopPropagation();
      var off = root.getAttribute('data-motion') === 'off';
      if (off) { root.removeAttribute('data-motion'); try { localStorage.setItem('fs-motion', 'on'); } catch (err) {} }
      else { root.setAttribute('data-motion', 'off'); try { localStorage.setItem('fs-motion', 'off'); } catch (err) {} }
      syncAnim();
    });
  }

  /* ---------- Effects (shine, hover lifts, breathing, glow) ---------- */
  var rowFx = document.getElementById('rowFx');
  function syncFx() {
    if (rowFx) rowFx.setAttribute('aria-pressed', root.getAttribute('data-fx') === 'off' ? 'false' : 'true');
  }
  if (rowFx) {
    rowFx.addEventListener('click', function (e) { e.stopPropagation();
      var off = root.getAttribute('data-fx') === 'off';
      if (off) { root.removeAttribute('data-fx'); try { localStorage.setItem('fs-fx', 'on'); } catch (err) {} }
      else { root.setAttribute('data-fx', 'off'); try { localStorage.setItem('fs-fx', 'off'); } catch (err) {} }
      syncFx();
    });
  }

  /* ---------- Hotkeys ----------
     One switch for every keyboard shortcut on the site (the rail's "s", the
     jump button's "g"/Home/End, the pricing ring's arrow keys). Other scripts
     read FS_KEYS.enabled() and listen for the change event, so toggling it takes
     effect immediately without a reload. K itself always stays live as the
     escape hatch (see hotkeys.js): an accidental press can never strand the
     visitor with no keyboard way back on. */
  var rowKeys = document.getElementById('rowKeys');
  var FS_KEYS = {
    enabled: function () { return root.getAttribute('data-keys') !== 'off'; },
    /* every shortcut must also stay out of the way while typing */
    typing: function (el) {
      el = el || document.activeElement;
      if (!el) return false;
      var tag = (el.tagName || '').toUpperCase();
      return tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || el.isContentEditable === true;
    },
    /* true when a shortcut may run: enabled, not typing, no modifier held */
    allow: function (e) {
      if (!FS_KEYS.enabled()) return false;
      if (e && (e.metaKey || e.ctrlKey || e.altKey)) return false;
      return !FS_KEYS.typing();
    }
  };
  window.FS_KEYS = FS_KEYS;

  function syncKeys() {
    var on = FS_KEYS.enabled();
    if (rowKeys) rowKeys.setAttribute('aria-pressed', on ? 'true' : 'false');
  }
  if (rowKeys) {
    rowKeys.addEventListener('click', function (e) {
      e.stopPropagation();
      var on = !FS_KEYS.enabled();
      if (on) root.removeAttribute('data-keys'); else root.setAttribute('data-keys', 'off');
      try { localStorage.setItem('fs-hotkeys', on ? 'on' : 'off'); } catch (err) {}
      syncKeys();
      try { window.dispatchEvent(new CustomEvent('fs-hotkeys-change', { detail: { on: on } })); } catch (err) {}
    });
  }

  /* ---------- Font size (global, site-wide) ----------
     One S/M/L control in every settings menu. State lives in `fs-font`
     (migrated once from the old per-section fs-help-font / fs-blog-font
     keys); the size applies through `html[data-font]` + root font-size
     rules in main.css, so it works on every page. Per-section painters
     (help/blog inlines) mirror the legacy attrs and listen for the
     fs-font-change event to repaint their own toggles. */
  function readFont() {
    try {
      var v = localStorage.getItem('fs-font');
      if (v === 's' || v === 'm' || v === 'l') return v;
      v = localStorage.getItem('fs-help-font') || localStorage.getItem('fs-blog-font');
      if (v === 's' || v === 'm' || v === 'l') {
        try { localStorage.setItem('fs-font', v); } catch (err2) {}
        return v;
      }
    } catch (err) {}
    return 'm';
  }
  function applyFont(v) {
    if (v === 's' || v === 'l') {
      root.setAttribute('data-font', v);
      root.setAttribute('data-hcfont', v);
      root.setAttribute('data-blogfont', v);
    } else {
      root.removeAttribute('data-font');
      root.removeAttribute('data-hcfont');
      root.removeAttribute('data-blogfont');
    }
    Array.prototype.forEach.call(
      document.querySelectorAll('[data-fonts] button, [data-blog-fonts] button, [data-global-fonts] button'),
      function (b) { b.classList.toggle('on', (v || 'm') === b.getAttribute('data-font')); });
  }
  function setFont(v) {
    if (v !== 's' && v !== 'l') v = 'm';
    try {
      localStorage.setItem('fs-font', v);
      localStorage.setItem('fs-help-font', v);
      localStorage.setItem('fs-blog-font', v);
    } catch (err) {}
    applyFont(v);
    try { window.dispatchEvent(new CustomEvent('fs-font-change', { detail: { font: v } })); } catch (err) {}
  }
  window.FS_FONT = { get: readFont, set: setFont, apply: applyFont };
  document.addEventListener('click', function (e) {
    if (!e.target.closest) return;
    var f = e.target.closest('[data-fonts] button, [data-blog-fonts] button, [data-global-fonts] button');
    if (f) { e.stopPropagation(); setFont(f.getAttribute('data-font')); }
  });

  /* ---------- Zen mode: double-tap (not on controls) hides/shows chrome ----------
     Hides the navbar and the bottom bars (jump FAB, Contents bar, cookie
     banner) while reading; a second double-tap brings them back. */
  (function () {
    if (window.matchMedia && !matchMedia('(hover: none), (pointer: coarse)').matches) return;
    var last = 0, timer = null;
    document.addEventListener('touchend', function (e) {
      if (e.target.closest && e.target.closest('a, button, input, select, textarea, [role="button"], .hc-fab, .jump-fab, .toc-bar, .hc-toc-fab, .hc-pager')) return;
      var now = Date.now();
      if (now - last < 320) {
        last = 0; clearTimeout(timer);
        document.body.classList.toggle('zen');
      } else {
        last = now;
        clearTimeout(timer);
        timer = setTimeout(function () { last = 0; }, 340);
      }
    }, { passive: true });
  })();

  /* ---------- Fullscreen exit pill (reader focus modes) ----------
     hc-fs (help) and blog-fs (blog) slide the navbar away and let the
     article toolbar scroll off, stranding touch readers with no visible way
     out — Escape exists only on keyboards. A floating exit pill appears
     whenever either mode is on and uses the page's own exit path, so state
     (localStorage + toggle paint) stays in sync. Styled in main.css. */
  (function () {
    var LABELS = { en: 'Exit fullscreen', ru: 'Выйти из полноэкранного' };
    var fab = document.createElement('button');
    fab.type = 'button';
    fab.className = 'fs-exit-fab';
    fab.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M8 3v3a2 2 0 0 1-2 2H3"/><path d="M16 3v3a2 2 0 0 0 2 2h3"/><path d="M8 21v-3a2 2 0 0 1 2-2h3"/><path d="M16 21v-3a2 2 0 0 0-2-2h-3"/></svg><span></span>';
    var label = fab.querySelector('span');
    function lang() { try { return (window.FS_LANG && FS_LANG.get() === 'ru') ? 'ru' : 'en'; } catch (e) { return 'en'; } }
    function paint() {
      var on = root.classList.contains('hc-fs') || root.classList.contains('blog-fs');
      var t = LABELS[lang()];
      label.textContent = t;
      fab.setAttribute('aria-label', t);
      fab.classList.toggle('show', on);
    }
    function exit() {
      try { if (root.classList.contains('hc-fs') && window.__hcExitFs) window.__hcExitFs(); }
      catch (e) {}
      try {
        if (root.classList.contains('blog-fs')) {
          try { localStorage.setItem('fs-blog-fs', 'off'); } catch (e2) {}
          root.classList.remove('blog-fs');
          Array.prototype.forEach.call(document.querySelectorAll('[data-blog-fs]'),
            function (b) { b.classList.remove('on'); b.setAttribute('aria-pressed', 'false'); });
        }
      } catch (e) {}
      paint();
    }
    fab.addEventListener('click', function (e) { e.stopPropagation(); exit(); });
    /* help-hub.js already exits hc-fs on Escape; this covers blog-fs (and
       static pages whose inline reader has no Escape handler). Idempotent. */
    document.addEventListener('keydown', function (e) {
      if ((e.key === 'Escape' || e.key === 'Esc') && root.classList.contains('blog-fs')) exit();
    });
    if (document.body) document.body.appendChild(fab);
    else document.addEventListener('DOMContentLoaded', function () { document.body.appendChild(fab); });
    if ('MutationObserver' in window) {
      new MutationObserver(function () { paint(); })
        .observe(root, { attributes: true, attributeFilter: ['class'] });
    }
    window.addEventListener('fs-lang-change', paint);
    paint();
  })();

  syncDark(); syncAnim(); syncFx(); syncKeys();
  applyFont(readFont());

  // Keep every setting in sync across open tabs/pages.
  window.addEventListener('storage', function (e) {
    if (e.key === 'theme' && e.newValue) { root.setAttribute('data-theme', e.newValue); syncDark(); }
    if (e.key === 'fs-motion') {
      if (e.newValue === 'off') root.setAttribute('data-motion', 'off'); else root.removeAttribute('data-motion');
      syncAnim();
    }
    if (e.key === 'fs-fx') {
      if (e.newValue === 'off') root.setAttribute('data-fx', 'off'); else root.removeAttribute('data-fx');
      syncFx();
    }
    if (e.key === 'fs-hotkeys') {
      if (e.newValue === 'off') root.setAttribute('data-keys', 'off'); else root.removeAttribute('data-keys');
      syncKeys();
      try { window.dispatchEvent(new CustomEvent('fs-hotkeys-change', { detail: { on: e.newValue !== 'off' } })); } catch (err) {}
    }
    if (e.key === 'fs-font' || e.key === 'fs-help-font' || e.key === 'fs-blog-font') {
      applyFont(readFont());
      try { window.dispatchEvent(new CustomEvent('fs-font-change', { detail: { font: readFont() } })); } catch (err) {}
    }
    if (e.key === 'fs-rail') {
      /* the rail lives in liquid-nav.js, which listens for this event */
      try { window.dispatchEvent(new CustomEvent('fs-rail-change', { detail: { off: e.newValue === 'off' } })); } catch (err) {}
    }
  });
})();
