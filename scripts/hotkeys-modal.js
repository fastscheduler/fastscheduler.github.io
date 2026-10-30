/* =====================================================================
   Hotkeys viewer + editor with a REAL override engine.

   Why: hotkeys used to be hard-coded in several scripts (hotkeys.js,
   scroll-jump.js, liquid-nav.js, help center), so a key saved here never
   actually fired. Now this file owns dispatching for every CUSTOM key:

     · single key          (O)                → fires immediately
     · modifier combo      (Shift+Space)      → fires immediately
     · sequence / chord    (O then B)         → fires when the second key
                                                lands within 1.2s

   Customs live in localStorage (fs-hotkey-custom) so they follow the
   visitor across pages and survive refresh. Defaults keep working through
   their original scripts; this layer only intercepts remapped keys on the
   capture phase and stops the event, so nothing double-fires.

   The modal itself: "Hotkeys on this page" + "Other hotkeys", hover a row
   → pencil → press up to 3 keys one after another (Esc cancels) → saved
   and every keycap on the page repaints to the new binding.
   ===================================================================== */
(function () {
  'use strict';

  var STORE = 'fs-hotkey-custom';
  var CHORD_MS = 1200;          /* window for the 2nd key of a sequence */
  var RECORD_GAP_MS = 750;      /* idle time that closes a recording */

  function thisPage() {
    var p = location.pathname.split('/').pop() || 'index.html';
    if (p === '' || p === 'index.html') return 'home';
    if (p === 'help/' || location.pathname.indexOf('/help/') !== -1) return 'help';
    if (location.pathname.indexOf('/legal/') !== -1) return 'legal';
    if (location.pathname.indexOf('/blog/') !== -1) return 'blog';
    return 'other';
  }
  function onThisPage(entry) {
    var cur = thisPage();
    var pg = entry.page;
    if (pg === 'all') return true;
    if (pg === 'home+legal') return cur === 'home' || cur === 'legal';
    return pg === cur;
  }
  function desktop() { return !window.matchMedia('(max-width: 860px)').matches; }

  /* ---------- actions (resolved lazily — pages differ) ---------- */
  function clickSel(sel) {
    var list = document.querySelectorAll(sel);
    for (var i = 0; i < list.length; i++) {
      var r = list[i].getBoundingClientRect();
      if (r.width > 0 && r.height > 0) { list[i].click(); return true; }
    }
    if (list.length) { list[0].click(); return true; }
    return false;
  }
  function jump(kind) {
    var J = window.FS_JUMP;
    if (J && J[kind]) { J[kind](); return true; }
    return false;
  }

  /* ---------- the registry ---------- */
  var REGISTRY = [
    { id: 'bot',      key: 'B',            page: 'all',  name: 'Open Bot',                  sel: '.nav-cta-sm, .nav-cta-m, .nav-cta, .cta-big' },
    /* M opens the burger, which only exists on narrow screens (the burger is
       display:none on desktop, so the key is hidden there too — the modal
       never advertises a key that would do nothing). */
    { id: 'menu',     key: 'M',            page: 'home', name: 'Open menu',                 sel: '#navBurger', mobileOnly: true },
    { id: 'settings', key: ',',            page: 'all',  name: 'Settings',                  sel: '#settingsBtn' },
    { id: 'blog',     key: 'G',            page: 'all',  name: 'Blog',                      sel: 'a.nav-link[href*="blog"], .help-row a[href*="blog"], a[href$="blog/index.html"], a[href$="/blog/"], #navMobile a[href*="blog"], footer a[href$="blog/index.html"]' },
    { id: 'help',     key: 'H',            page: 'all',  name: 'Help',                      sel: 'a.nav-link[href*="help"], .site-menu-row, a.gp-row[href*="help"], .help-row a[href*="help"], #navMobile a[href*="help"], footer a[href$="help/"]' },
    { id: 'sec1', key: '1', page: 'home', name: 'Time saved',  sel: 'a[href="#time"]' },
    { id: 'sec2', key: '2', page: 'home', name: 'Features',    sel: 'a[href="#features"]' },
    { id: 'sec3', key: '3', page: 'home', name: 'How it works', sel: 'a[href="#how"]' },
    { id: 'sec4', key: '4', page: 'home', name: 'Pricing',     sel: 'a[href="#pricing"]' },
    { id: 'sec5', key: '5', page: 'home', name: 'FAQ',         sel: 'a[href="#faq"]' },
    { id: 'dark',    key: 'D', page: 'all', name: 'Dark mode',  sel: '#rowDark' },
    { id: 'anim',    key: 'A', page: 'all', name: 'Animations', sel: '#rowAnim' },
    { id: 'fx',      key: 'X', page: 'all', name: 'Effects',    sel: '#rowFx' },
    { id: 'keys',    key: 'K', page: 'all', name: 'Hotkeys switch', sel: '#rowKeys' },
    { id: 'yearly',  key: 'Y', page: 'home', name: 'Yearly billing',  sel: '#billYearly' },
    { id: 'monthly', key: 'N', page: 'home', name: 'Monthly billing', sel: '#billMonthly' },
    { id: 'choose',  key: 'P', page: 'home', name: 'Choose the centred plan',
      act: function () { return clickSel('.pricing-stage .plan-g[data-pos="0"] .btn'); } },
    /* F toggles the jump menu. G used to do it, but G belongs to the Blog on
       every page hotkeys.js loads — one default key cannot drive two
       actions, and the Blog won. Remap either entry to get G back. */
    { id: 'jumpFab', key: 'F', page: 'all', name: 'Jump button (round arrow)', act: function () { return jump('menu'); } },
    { id: 'top',     key: 'Shift+Space', page: 'all', name: 'Go to the top',     act: function () { return jump('top'); } },
    { id: 'pageup',  key: 'U',           page: 'all', name: 'Jump up a screen',  act: function () { return jump('pageUp'); }, desktopOnly: true },
    { id: 'pagedown', key: 'J',          page: 'all', name: 'Jump down a screen', act: function () { return jump('pageDown'); }, desktopOnly: true },
    { id: 'end',     key: 'Shift+Enter', page: 'all', name: 'Go to the end',     act: function () { return jump('bottom'); } },
    { id: 'tocToggle',  key: 'C', page: 'legal', name: 'Show/hide contents', act: function () { return clickSel('#tocSideTab'); }, desktopOnly: true },
    { id: 'hcSearch',   key: 'Ctrl+K', page: 'help', name: 'Search the help center',
      act: function () { return clickSel('#hcSearch'); } },
    { id: 'hcTopics',   key: 'O', page: 'help', name: 'Show/hide topics', act: function () { return clickSel('#hcSideToggle'); }, desktopOnly: true }
  ];

  /* ---------- custom key storage ---------- */
  function readCustom() {
    try { return JSON.parse(localStorage.getItem(STORE) || '{}'); } catch (e) { return {}; }
  }
  function writeCustom(map) {
    try { localStorage.setItem(STORE, JSON.stringify(map)); } catch (e) {}
    try { window.dispatchEvent(new CustomEvent('fs-hotkeys-remap')); } catch (e) {}
  }
  function currentKey(entry) {
    var c = readCustom()[entry.id];
    return c || entry.key;
  }
  window.FS_HOTKEYS_OVERRIDE = {
    get: function (id) {
      var e = null;
      REGISTRY.forEach(function (x) { if (x.id === id) e = x; });
      return e ? currentKey(e) : null;
    },
    all: readCustom,
    registry: REGISTRY
  };

  /* ---------- key helpers ---------- */
  function comboOf(e) {
    var parts = [];
    if (e.ctrlKey) parts.push('Ctrl');
    if (e.metaKey) parts.push('Cmd');
    if (e.altKey) parts.push('Alt');
    if (e.shiftKey && e.key !== 'Shift') parts.push('Shift');
    var k = e.key;
    if (k === ' ') k = 'Space';
    else if (k.length === 1) k = k.toUpperCase();
    else if (k === 'Escape' || k === 'Shift' || k === 'Control' || k === 'Alt' || k === 'Meta') return null;
    parts.push(k);
    return parts.join('+');
  }
  function pretty(combo) {
    return String(combo || '').split('>')[0].split('+').map(function (p) {
      return p === 'Space' ? '␣' : p;
    }).join('+');
  }
  function prettySeq(seq) {
    return String(seq || '').split('>').map(pretty).join(' + ');
  }

  function enabled() {
    var K = window.FS_KEYS;
    if (K) return K.enabled();
    return document.documentElement.getAttribute('data-keys') !== 'off';
  }
  function typing(e) {
    var el = document.activeElement;
    var tag = ((el && el.tagName) || '').toUpperCase();
    if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return true;
    return !!(el && el.isContentEditable === true);
  }

  /* ---------- the override dispatcher ---------- */
  var overrides = null;
  function loadOverrides() {
    var c = readCustom();
    overrides = {};
    Object.keys(c).forEach(function (id) {
      var seq = String(c[id]).split('>');
      var entry = null;
      REGISTRY.forEach(function (x) { if (x.id === id) entry = x; });
      if (!entry) return;
      overrides[id] = { seq: seq, entry: entry };
    });
  }
  var pending = null;   /* { id, step, t } — a sequence in progress */

  function fire(entry) {
    if (entry.act) { entry.act(); return; }
    if (entry.sel) clickSel(entry.sel);
  }

  document.addEventListener('keydown', function (e) {
    if (modal && modal.classList.contains('open')) return;   /* modal handles its own */
    if (e.defaultPrevented || e.repeat) return;
    if (!enabled() || typing(e)) { pending = null; return; }
    if (!overrides) loadOverrides();
    var ids = Object.keys(overrides);
    if (!ids.length) { pending = null; return; }
    var combo = comboOf(e);
    if (!combo) return;

    /* finish a running sequence? */
    if (pending && Date.now() - pending.t <= CHORD_MS) {
      var o = overrides[pending.id];
      if (o && o.seq[pending.step] === combo) {
        if (pending.step + 1 >= o.seq.length) {
          pending = null;
          e.preventDefault(); e.stopPropagation(); e.stopImmediatePropagation();
          fire(o.entry);
          return;
        }
        pending.step++; pending.t = Date.now();
        e.preventDefault(); e.stopPropagation(); e.stopImmediatePropagation();
        return;
      }
      pending = null;
    }

    /* single-combo override fires at once */
    for (var i = 0; i < ids.length; i++) {
      var ov = overrides[ids[i]];
      if (ov.seq.length === 1 && ov.seq[0] === combo) {
        e.preventDefault(); e.stopPropagation(); e.stopImmediatePropagation();
        fire(ov.entry);
        return;
      }
    }
    /* otherwise: does this key START a sequence? arm it and wait.
       The first key of a chord is swallowed, or page-level dispatchers
       (help center's O = topics, etc.) would fire on it mid-chord. */
    for (var j = 0; j < ids.length; j++) {
      var ov2 = overrides[ids[j]];
      if (ov2.seq.length > 1 && ov2.seq[0] === combo) {
        pending = { id: ids[j], step: 1, t: Date.now() };
        e.preventDefault(); e.stopPropagation(); e.stopImmediatePropagation();
        return;
      }
    }
  }, true);

  /* ---------- modal ---------- */
  var modal, sheet, listEl, editing = null, prevFocus = null;

  function ensureModal() {
    if (modal) return;
    modal = document.createElement('div');
    modal.className = 'hk-overlay';
    modal.innerHTML =
      '<div class="hk-sheet" role="dialog" aria-modal="true" aria-label="Keyboard shortcuts">' +
        '<div class="hk-head"><b>Keyboard shortcuts</b>' +
        '<button type="button" class="hk-close" aria-label="Close">' +
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg></button></div>' +
        '<div class="hk-hint">Hover a shortcut and press the pencil to remap it. Press one key, or two or three keys one after another (like <b>O</b> then <b>B</b>), or hold Ctrl/Alt/Shift. Esc cancels.</div>' +
        '<div class="hk-note" role="note">' + extNoteHTML('modal') + '</div>' +
        '<div class="hk-body"></div>' +
      '</div>';
    document.body.appendChild(modal);
    extLocalize();          /* modal text is built here — localize it now */
    sheet = modal.querySelector('.hk-sheet');
    listEl = modal.querySelector('.hk-body');
    modal.querySelector('.hk-close').addEventListener('click', close);
    modal.addEventListener('click', function (e) { if (e.target === modal) close(); });
    document.addEventListener('keydown', function (e) {
      if (!modal.classList.contains('open')) return;
      if (editing) {
        e.preventDefault();
        e.stopPropagation();
        if (e.key === 'Escape') { stopEditing(false); return; }
        recordKey(e);
        return;
      }
      if (e.key === 'Escape') close();
    }, true);
  }

  function rowHTML(entry) {
    var key = currentKey(entry);
    var custom = readCustom()[entry.id];
    return '<div class="hk-row" data-id="' + entry.id + '">' +
      '<span class="hk-name">' + entry.name + '</span>' +
      '<span class="hk-key-wrap">' +
      (custom ? '<button type="button" class="hk-reset" aria-label="Reset to default" title="Reset to default">↺</button>' : '') +
      '<kbd class="hk-key" title="Click to edit">' + prettySeq(key) + '</kbd>' +
      '<button type="button" class="hk-edit" aria-label="Edit shortcut" title="Edit shortcut">' +
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z"/></svg>' +
      '</button></span></div>';
  }

  function render() {
    loadOverrides();
    var here = REGISTRY.filter(function (e) {
      if (!onThisPage(e)) return false;
      if (e.desktopOnly && !desktop()) return false;
      if (e.mobileOnly && desktop()) return false;
      return true;
    });
    var others = REGISTRY.filter(function (e) {
      if (onThisPage(e)) return false;
      if (e.desktopOnly && !desktop()) return false;
      if (e.mobileOnly && desktop()) return false;
      return true;
    });
    /* The page's OWN hotkeys first (this page's explicit group wins, then
       the all-pages set), everything else under "Other hotkeys". */
    var ownIds = {};
    try {
      document.querySelectorAll('[data-hk]').forEach(function (el) {
        String(el.getAttribute('data-hk') || '').split(' ').forEach(function (id) {
          if (id) ownIds[id] = true;
        });
      });
    } catch (e) {}
    var own = here.filter(function (e) { return ownIds[e.id]; });
    var restHere = here.filter(function (e) { return !ownIds[e.id]; });

    var html = '';
    if (own.length) {
      html += '<p class="hk-sec">Hotkeys on this page</p>';
      own.forEach(function (e) { html += rowHTML(e); });
    }
    if (restHere.length) {
      html += '<p class="hk-sec">On every page</p>';
      restHere.forEach(function (e) { html += rowHTML(e); });
    }
    if (others.length) {
      html += '<p class="hk-sec">Other hotkeys</p>';
      others.forEach(function (e) { html += rowHTML(e); });
    }
    listEl.innerHTML = html;
    listEl.querySelectorAll('.hk-edit').forEach(function (btn) {
      btn.addEventListener('click', function () { startEditing(btn.closest('.hk-row')); });
    });
    /* the keycap itself is a second, bigger target for opening the editor */
    listEl.querySelectorAll('.hk-key').forEach(function (kbd) {
      kbd.addEventListener('click', function () { startEditing(kbd.closest('.hk-row')); });
    });
    listEl.querySelectorAll('.hk-reset').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var id = btn.closest('.hk-row').getAttribute('data-id');
        var c = readCustom();
        delete c[id];
        writeCustom(c);
        render();
        repaintCaps();
      });
    });
  }

  /* ---------- recording: keys pressed one after another form a sequence ----------
     Every keypress is written to localStorage IMMEDIATELY (as a draft that is
     already the real binding), so a refresh or a closed tab can never roll
     the hotkey back to its default — the old save-on-idle-timer lost the
     change when the page was reloaded within the 750ms window. */
  function startEditing(row) {
    if (editing) stopEditing(false);
    window.FS_HK_RECORDING = true;   /* page-level dispatchers stand down */
    editing = { row: row, id: row.getAttribute('data-id'), kbd: row.querySelector('.hk-key'), parts: [], timer: null };
    editing.kbd.classList.add('rec');
    editing.kbd.textContent = 'press keys…';
  }
  function recordKey(e) {
    if (e.repeat) return;                     /* holding a key must not spam the sequence */
    var combo = comboOf(e);
    if (!combo) return;
    editing.parts.push(combo);
    if (editing.parts.length > 3) editing.parts = editing.parts.slice(-3);
    editing.kbd.textContent = editing.parts.map(pretty).join(' + ') + ' …';
    /* persist NOW — the value is already valid (a single key works too) */
    var custom = readCustom();
    custom[editing.id] = editing.parts.join('>');
    writeCustom(custom);
    syncHotkeysJs();
    repaintCaps();
    clearTimeout(editing.timer);
    editing.timer = setTimeout(function () { stopEditing(true); }, RECORD_GAP_MS);
  }
  function stopEditing(save) {
    if (!editing) return;
    clearTimeout(editing.timer);
    editing.kbd.classList.remove('rec');
    var parts = editing.parts, id = editing.id;
    if (save && parts.length) {
      editing.kbd.textContent = parts.map(pretty).join(' + ') + '  ✓';
    }
    window.FS_HK_RECORDING = false;
    editing = null;
    render();
  }

  /* ---------- keep the other scripts' keycaps in step ---------- */
  /* hotkeys.js still owns the DEFAULT keys; hand it the list of keys that
     are now custom (old key freed unless the custom key IS the old key), so
     a remapped key fires exactly once, through the override dispatcher */
  function syncHotkeysJs() {
    var c = readCustom();
    var stolen = [];
    REGISTRY.forEach(function (entry) {
      var custom = c[entry.id];
      if (!custom) return;
      var oldK = entry.key;
      /* Steal the default whenever the binding stops being exactly it — a
         combo (Shift+B) or a sequence (O>B) frees the plain key too, or the
         old action would still fire on the bare press. Comparing the last
         step only ('B' of 'O>B') missed this and left the default live. */
      if (String(custom).toLowerCase() !== String(oldK).toLowerCase()) stolen.push(oldK);
    });
    window.FS_HOTKEYS_STOLEN = stolen;
  }
  function repaintCaps() {
    loadOverrides();
    var c = readCustom();
    REGISTRY.forEach(function (entry) {
      var key = c[entry.id] || entry.key;
      var label = prettySeq(key);
      /* keycaps inside controls */
      if (entry.sel) {
        document.querySelectorAll(entry.sel).forEach(function (ctrl) {
          var cap = ctrl.querySelector(':scope > .tab-kbd, :scope kbd.tab-kbd');
          if (cap) cap.textContent = label;
        });
      }
      /* jump-menu rows */
      var row = document.querySelector('.jump-menu [data-jump] .tab-kbd');
      if (row) { /* updated via FS_JUMP hook below */ }
      if (entry.id === 'top')     setJumpCap('top', label);
      if (entry.id === 'pageup')  setJumpCap('pageup', label);
      if (entry.id === 'pagedown') setJumpCap('pagedown', label);
      if (entry.id === 'end')     setJumpCap('bottom', label);
    });
  }
  function setJumpCap(kind, label) {
    var row = document.querySelector('.jump-menu [data-jump="' + kind + '"]');
    if (!row) return;
    var cap = row.querySelector('.tab-kbd');
    if (cap) cap.textContent = label;
  }
  window.addEventListener('fs-hotkeys-remap', function () {
    syncHotkeysJs();
    repaintCaps();
  });

  function open() {
    ensureModal();
    render();
    prevFocus = document.activeElement;
    modal.classList.add('open');
    var cs = getComputedStyle(modal);
    if (cs.display === 'none') modal.style.display = 'flex';
  }
  function close() {
    if (!modal) return;
    if (editing) stopEditing(false);
    modal.classList.remove('open');
    if (prevFocus && prevFocus.focus) prevFocus.focus();
  }

  window.FS_HK_MODAL = { open: open, close: close, repaint: repaintCaps };

  /* safety net: if the tab is closed/reloaded mid-recording, the binding is
     already in localStorage from recordKey — nothing to flush. */

  /* apply saved customs to hotkeys.js as soon as we load, so a remapped
     single key follows the visitor to every page */
  function boot() {
    syncHotkeysJs();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();

  /* ---------- extension warning (Vimium) ----------
     Vimium & co. bind single letters in the CAPTURE phase, before any of this
     page's listeners run, so the press is swallowed upstream and the hotkey
     looks broken. Both surfaces carry the warning in one place: the modal
     above, and a line under the Hotkeys rows of the settings menu — whose
     markup is inlined in ~2,200 HTML files, so it is injected from here.
     lang.js translates it back through its EN->RU map (whole text nodes). */
  var EXT_NOTE = {
    lead: 'Keys doing nothing?',
    /* the settings menu is a narrow popup — same warning, trimmed */
    settings: ' An extension like Vimium can capture these keys — right-click its toolbar icon and choose “Pause on this site”.',
    modal: ' An extension like Vimium captures single keys before this page sees them, so the press never reaches the site. Right-click the Vimium icon in the toolbar and choose “Pause on this site” — the hotkeys will work again.'
  };
  /* One text node per part — lang.js translates whole trimmed nodes only, and
     only from EN: injecting RU here would leave the note stranded in Russian
     on a later switch back to EN (chromeRestore has no EN original to put
     back). So the DOM always gets EN, then lang.js is asked to swap it in. */
  function extNoteHTML(surface) {
    return '<b>' + EXT_NOTE.lead + '</b>' + EXT_NOTE[surface];
  }
  function extLocalize() {
    try {
      if (window.FS_LANG && window.FS_LANG.apply && window.FS_LANG.get) window.FS_LANG.apply(window.FS_LANG.get());
    } catch (e) {}
  }
  function injectNote() {
    var btn = document.getElementById('rowKeysHelp');
    if (!btn || document.getElementById('rowKeysNote')) return;
    var note = document.createElement('div');
    note.id = 'rowKeysNote';
    note.className = 'gp-note';
    note.innerHTML = extNoteHTML('settings');
    btn.parentNode.insertBefore(note, btn.nextSibling);
    extLocalize();
  }

  /* wire the "See hotkeys" row on every page that has it */
  function wire() {
    var btn = document.getElementById('rowKeysHelp');
    if (btn) btn.addEventListener('click', function (e) {
      e.stopPropagation();
      document.body.click();          /* close the settings menu */
      setTimeout(open, 60);
    });
    injectNote();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', wire);
  else wire();
})();
