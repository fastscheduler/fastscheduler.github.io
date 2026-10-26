/* =====================================================================
   Scroll-jump FAB: a round button appears after scrolling down; tapping it
   opens a small menu (Go up / Jump a screen / Go to the end). The keyboard
   shortcuts (F, Shift+Space, U, J, Shift+Enter) live here too and are
   switchable in Settings > Hotkeys. (F, not G: G belongs to the Blog —
   see jumpMenuKey below.)

   The hotkeys editor drives the actions through window.FS_JUMP, so a
   remapped key fires the same code the menu rows do.
   ===================================================================== */
(function () {
  'use strict';

  /* On phones the legal pages don't scroll the document — they use an
     app-shell where main.legal is the inner scroller. Track THAT element
     there, so the FAB appears, tracks position and jumps correctly. */
  function scroller() {
    var legal = document.querySelector('main.legal');
    if (legal && document.body.classList.contains('legal') &&
        window.matchMedia && matchMedia('(max-width: 760px)').matches) return legal;
    return document.scrollingElement || document.documentElement;
  }
  function y() {
    var s = scroller();
    return s === document.scrollingElement ? (window.scrollY || 0) : s.scrollTop;
  }
  function maxY() {
    var s = scroller();
    return Math.max(0, (s.scrollHeight || 0) - s.clientHeight);
  }
  function go(target) {
    var s = scroller();
    if (s === document.scrollingElement) window.scrollTo({ top: target, behavior: motionOff() ? 'auto' : 'smooth' });
    else s.scrollTo({ top: target, behavior: motionOff() ? 'auto' : 'smooth' });
  }
  function motionOff() {
    return document.documentElement.getAttribute('data-motion') === 'off';
  }

  var btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'jump-fab';
  btn.setAttribute('aria-haspopup', 'menu');
  btn.setAttribute('aria-expanded', 'false');
  btn.setAttribute('aria-label', 'Jump');
  btn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="8 5 12 1 16 5"/><line x1="12" y1="2" x2="12" y2="10"/><polyline points="16 19 12 23 8 19"/><line x1="12" y1="22" x2="12" y2="14"/></svg>';

  var menu = document.createElement('div');
  menu.className = 'glass-pop jump-menu';
  menu.setAttribute('role', 'menu');
  menu.innerHTML =
    '<div class="gp-head">Jump</div>' +
    '<button type="button" class="gp-row" role="menuitem" data-jump="top">' +
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="18 15 12 9 6 15"/></svg>' +
    '<span>Go up</span><span class="tab-kbd">Shift+Space</span></button>' +
    '<button type="button" class="gp-row" role="menuitem" data-jump="pageup">' +
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="18 15 12 9 6 15"/></svg>' +
    '<span>Jump up a screen</span><span class="tab-kbd">U</span></button>' +
    '<button type="button" class="gp-row" role="menuitem" data-jump="pagedown">' +
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="6 9 12 15 18 9"/></svg>' +
    '<span>Jump down a screen</span><span class="tab-kbd">J</span></button>' +
    '<button type="button" class="gp-row" role="menuitem" data-jump="bottom">' +
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="6 9 12 15 18 9"/></svg>' +
    '<span>Go to the end</span><span class="tab-kbd">Shift+Enter</span></button>';

  /* Advertise the keys only while hotkeys are enabled: Settings > Hotkeys
     hides the keycaps, so the accessible names must go quiet with them.
     Custom bindings from the hotkeys editor win over the defaults. */
  var jumpRows = menu.querySelectorAll('.gp-row');
  var DEFAULTS = { top: 'Shift+Space', pageup: 'U', pagedown: 'J', bottom: 'Shift+Enter' };
  var IDS = { top: 'top', pageup: 'pageup', pagedown: 'pagedown', bottom: 'end' };
  /* Custom bindings repaint here; show the whole binding (combos and
     sequences included) exactly like the editor's own keycaps do, so the
     menu never advertises a first-key-only label that fires nothing. */
  function prettyPart(p) { return p === 'Space' ? '␣' : p; }
  function currentLabel(kind) {
    var id = IDS[kind];
    try {
      var c = JSON.parse(localStorage.getItem('fs-hotkey-custom') || '{}');
      if (c[id]) return String(c[id]).split('>').map(function (s) {
        return String(s).split('+').map(prettyPart).join('+');
      }).join(' + ');
    } catch (e) {}
    return DEFAULTS[kind];
  }
  function paintShortcuts() {
    var on = document.documentElement.getAttribute('data-keys') !== 'off';
    jumpRows.forEach(function (row) {
      var kind = row.getAttribute('data-jump');
      var label = currentLabel(kind);
      var cap = row.querySelector('.tab-kbd');
      if (cap) cap.textContent = label;
      if (on) row.setAttribute('aria-keyshortcuts', label);
      else row.removeAttribute('aria-keyshortcuts');
    });
  }
  paintShortcuts();
  window.addEventListener('fs-hotkeys-change', paintShortcuts);
  /* the hotkeys editor repaints the keycaps inside this menu */
  window.addEventListener('fs-hotkeys-remap', paintShortcuts);

  /* actions API — the hotkeys editor fires these for remapped keys */
  window.FS_JUMP = {
    menu: function () { setOpen(!open, true); },
    top: function () { go(0); setOpen(false); },
    bottom: function () { go(maxY()); setOpen(false); },
    pageUp: function () { go(Math.max(0, y() - window.innerHeight * 0.9)); setOpen(false); },
    pageDown: function () { go(Math.min(maxY(), y() + window.innerHeight * 0.9)); setOpen(false); }
  };

  function mount() { document.body.appendChild(menu); document.body.appendChild(btn); }
  if (document.body) mount(); else document.addEventListener('DOMContentLoaded', mount);

  var open = false, forced = false;
  function setOpen(v, focusMenu) {
    open = !!v;
    menu.classList.toggle('open', open);
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    if (open && focusMenu) {
      /* measure while rendered (mobile Safari reports 0 for display:none) */
      var vis = menu.style.visibility;
      menu.style.visibility = 'hidden';
      menu.classList.add('open');
      var mh = menu.offsetHeight, mw = menu.offsetWidth;
      menu.classList.toggle('open', open);
      menu.style.visibility = vis;
      var r = btn.getBoundingClientRect();
      /* prefer above the FAB; if there is no room, drop it below instead */
      var top = r.top - mh - 10;
      if (top < 12) top = Math.min(r.bottom + 10, window.innerHeight - mh - 12);
      menu.style.top = Math.max(12, top) + 'px'; menu.style.bottom = 'auto';
      var left = r.left + r.width / 2 - mw / 2;
      left = Math.max(12, Math.min(window.innerWidth - mw - 12, left));
      menu.style.left = left + 'px';
    }
  }
  btn.addEventListener('click', function () { setOpen(!open, true); });

  menu.addEventListener('click', function (e) {
    var row = e.target.closest && e.target.closest('[data-jump]');
    if (!row) return;
    var kind = row.getAttribute('data-jump');
    if (kind === 'top') go(0);
    else if (kind === 'bottom') go(maxY());
    else if (kind === 'pageup') go(Math.max(0, y() - window.innerHeight * 0.9));
    else if (kind === 'pagedown') go(Math.min(maxY(), y() + window.innerHeight * 0.9));
    setOpen(false);
  });
  document.addEventListener('click', function (e) {
    if (open && !btn.contains(e.target) && !menu.contains(e.target)) setOpen(false);
  });
  /* The menu's toggle key comes from the hotkeys editor (default F). G used
     to own the jump menu unconditionally, but hotkeys.js now binds G to the
     Blog on every page it loads, so G stands down wherever the Blog owns it.
     Remapped combos/sequences are dispatched by hotkeys-modal.js on the
     capture phase; only a plain single-char binding still belongs here. */
  function jumpMenuKey() {
    try {
      var O = window.FS_HOTKEYS_OVERRIDE;
      if (O && O.get) {
        var k = O.get('jumpFab');
        if (k && k.length === 1) return String(k).toLowerCase();
      }
    } catch (err) {}
    return 'f';
  }
  document.addEventListener('keydown', function (e) {
    /* While the hotkeys editor is open (or recording) keys belong to it. */
    if (window.FS_HK_RECORDING) return;
    if (document.querySelector && document.querySelector('.hk-overlay.open')) return;
    if (e.key === 'Escape' && open) { setOpen(false); return; }
    /* Hotkeys (switchable in Settings): F toggles the menu, Shift+Space top,
       U page-up, J page-down, Shift+Enter end. FS_KEYS also keeps shortcuts
       out of the way while typing. NOTE: remapped single keys are dispatched
       by hotkeys-modal.js on the capture phase; if the event reaches us the
       default key still owns its action. */
    var K = window.FS_KEYS;
    var allowed = K ? K.allow(e) : (function () {
      if (document.documentElement.getAttribute('data-keys') === 'off') return false;
      if (e.metaKey || e.ctrlKey || e.altKey) return false;
      var el = document.activeElement, tag = (el && el.tagName) || '';
      return tag !== 'INPUT' && tag !== 'TEXTAREA' && tag !== 'SELECT' && !(el && el.isContentEditable);
    })();
    if (!allowed) return;
    if (e.shiftKey && e.code === 'Space') { e.preventDefault(); go(0); setOpen(false); return; }
    if (e.shiftKey && e.key === 'Enter') { e.preventDefault(); go(maxY()); setOpen(false); return; }
    /* Every key below this line is unshifted: Shift+U / Shift+J / Shift+G
       must not page or toggle (Shift combos belong to the editor). The
       'G' spelling also covers Caps Lock; a real Shift is already returned
       above, so Caps-Lock users keep their hotkeys. */
    if (e.shiftKey) return;
    var k = (e.key || '').toLowerCase();
    if (k === jumpMenuKey()) { e.preventDefault(); setOpen(!open, true); return; }
    /* legacy: pages without hotkeys.js never rebound G to the Blog */
    if (k === 'g') {
      var owned = window.FS_HOTKEYS && window.FS_HOTKEYS.map &&
                  window.FS_HOTKEYS.map.some(function (r) { return r.key === 'g'; });
      if (!owned) { e.preventDefault(); setOpen(!open, true); }
      return;
    }
    if (k === 'j') { e.preventDefault(); go(Math.min(maxY(), y() + window.innerHeight * 0.9)); setOpen(false); return; }
    if (k === 'u') { e.preventDefault(); go(Math.max(0, y() - window.innerHeight * 0.9)); setOpen(false); return; }
  });

  /* The FAB fades out after a few seconds without scrolling, tapping or
     typing, and comes straight back on the next interaction — the legal pages
     already behaved like this and the rest of the site looked stuck by
     comparison. It never hides while its own menu is open or while a field
     has focus, so it cannot vanish mid-task. */
  var idleT = null;
  function goIdle() {
    if (open) return;
    var a = document.activeElement;
    var tag = (a && a.tagName) || '';
    if (tag === 'INPUT' || tag === 'TEXTAREA' || (a && a.isContentEditable)) return;
    document.documentElement.classList.add('jump-idle');
  }
  function awake() {
    document.documentElement.classList.remove('jump-idle');
    clearTimeout(idleT);
    idleT = setTimeout(goIdle, 4200);
    tick();
  }
  function tick() { btn.classList.toggle('show', forced || y() > 480); }
  ['scroll', 'touchstart', 'pointerdown', 'keydown', 'wheel'].forEach(function (ev) {
    window.addEventListener(ev, function () { awake(); tick(); }, { passive: true });
  });
  var s = scroller();
  var lastScroller = s;
  function bindScroller() {
    var cur = scroller();
    if (cur === lastScroller) return;
    lastScroller = cur;
    cur.addEventListener('scroll', onScroll, { passive: true });
  }
  function onScroll() { awake(); tick(); }
  if (s) s.addEventListener('scroll', onScroll, { passive: true });
  /* the legal app-shell swaps its scroller between breakpoints — re-bind
     after a resize so the FAB keeps tracking the right container */
  window.addEventListener('resize', function () { bindScroller(); awake(); tick(); });
  document.addEventListener('click', function (e) {
    if (btn.contains(e.target) || menu.contains(e.target)) { awake(); tick(); }
  });
  awake();
  tick();
})();
