/* =====================================================================
   Site-wide keyboard shortcuts.

   One registry owns three things for each control:
     1. the key that activates it,
     2. the keycap hint shown next to it,
     3. its aria-keyshortcuts attribute.

   Settings > Hotkeys switches the whole set off by putting
   data-keys="off" on <html>. When that happens shortcuts stop firing AND
   every keycap hint is hidden, so the interface never advertises a key that
   would do nothing (the CSS half of that lives in main.css).

   Conventions
     - single letters and digits need no modifier AND no Shift; nothing
       fires while the visitor is typing in a field. Shift-held presses never
       trigger the unshifted action (Shift+1 is '!', not '1'; Shift+letter
       combos belong to the hotkeys editor) and are left for the editor's
       override dispatcher (capture phase) and scroll-jump's Shift+Space /
       Shift+Enter
     - the first *visible* match of a selector wins, so one key can back both
       a desktop and a mobile control (only one is ever on screen)
     - hints are hidden below 860px, where there is no hardware keyboard

   Other scripts own their own keys and already respect FS_KEYS: the glass
   rail's panel toggle (S, liquid-nav.js), the jump button (G / Home / End,
   scroll-jump.js) and the help center's search + topics keys (S / K / T).
   ===================================================================== */
(function () {
  var root = document.documentElement;

  /* ---------- the map -------------------------------------------------
     key  : compared against event.key, lower-cased for single characters
     sel  : the control(s) to activate; the first visible match is clicked
     run  : for shortcuts that have no single control
     hint : 'inline' next to the control | 'rail' only once the link has moved
            into the glass rail (in the top bar it would crowd the navbar) |
            false for a bare shortcut
     name : accessible label; also the source of aria-keyshortcuts
  --------------------------------------------------------------------- */
  var MAP = [
    /* the one conversion action: navbar button, mobile CTA or hero button —
       whichever is on screen at this width */
    { key: 'b', sel: '.nav-cta-sm, .nav-cta-m, .nav-cta, .cta-big', name: 'Open Bot', hint: 'inline' },

    /* navbar. The rail carries the same two controls once the nav liquefies,
       so both advertise their key there ('rail' hints are hidden in the top
       bar, where a keycap would crowd the row). */
    { key: 'm', sel: '#navBurger', name: 'Menu', hint: false },
    { key: ',', sel: '#settingsBtn', name: 'Settings', hint: 'rail', tip: true },
    /* H = Help on every page (on the home page the old H entry answered the
       help-row, which holds BOTH the Blog and the Help link and picked the
       first visible one — so H went to the Blog). G = Blog on every page.
       On the home page G used to toggle the jump menu (scroll-jump.js); the
       hotkeys editor's 'jumpFab' entry keeps that remappable there. */

    /* in-page sections, numbered in the order they appear in the navbar.
       The keycap is revealed once the link has poured into the rail. */
    { key: '1', always: true, sel: 'a[href="#time"]',     name: 'Time saved',   hint: 'rail' },
    { key: '2', always: true, sel: 'a[href="#features"]', name: 'Features',     hint: 'rail' },
    { key: '3', always: true, sel: 'a[href="#how"]',      name: 'How it works', hint: 'rail' },
    { key: '4', always: true, sel: 'a[href="#pricing"]',  name: 'Pricing',      hint: 'rail' },
    { key: '5', always: true, sel: 'a[href="#faq"]',      name: 'FAQ',          hint: 'rail' },

    /* settings menu rows. 'always': the row lives inside the settings menu,
       which is usually CLOSED when the key is pressed — a visibility-gated
       resolve() found nothing and the hotkey silently did nothing. These
       click their row directly instead, open menu or not. */
    { key: 'd', sel: '#rowDark', name: 'Dark mode',  hint: 'inline', always: true },
    { key: 'a', sel: '#rowAnim', name: 'Animations', hint: 'inline', always: true },
    { key: 'x', sel: '#rowFx',   name: 'Effects',    hint: 'inline', always: true },
    { key: 'k', sel: '#rowKeys', name: 'Hotkeys',    hint: 'inline', always: true },

    { key: 'g', sel: 'a.nav-link[href*="blog"], .help-row a[href*="blog"], a[href$="blog/"], a[href$="/blog/"], #navMobile a[href*="blog"], footer a[href$="blog/"]',
      name: 'Blog', hint: 'rail' },
    /* S = search on blog pages: focuses the sticky search bar. Pressing S
       while already typing stands down (allow() normally guards this, but
       the field itself must not steal focus back mid-typing). */
    { key: 's', name: 'Search the blog', hint: false, run: function () {
        var f = document.getElementById('blog-q');
        if (!f) return;
        if (window.FS_KEYS && FS_KEYS.typing()) return;
        f.focus();
        try { f.setSelectionRange(f.value.length, f.value.length); } catch (err) {}
      } },
    { key: 'h', sel: 'a.nav-link[href*="help"], .site-menu-row, a.gp-row[href*="help"], .help-row a[href*="help"], #navMobile a[href*="help"], footer a[href$="help.html"]',
      name: 'Help', hint: 'rail' },

    /* pricing: billing period, then act on whichever plan is centred */
    { key: 'y', sel: '#billYearly',  name: 'Yearly billing',  hint: false },
    { key: 'n', sel: '#billMonthly', name: 'Monthly billing', hint: false },
    { key: 'p', name: 'Choose the centred plan', hint: false, run: function () {
        var btn = document.querySelector('.pricing-stage .plan-g[data-pos="0"] .btn');
        if (btn) btn.click();
      } }
  ];

  /* ---------- helpers ---------- */
  function keyLabel(key) {
    if (key === ',') return ',';
    if (key.length === 1) return key.toUpperCase();
    return key;
  }
  /* aria-keyshortcuts wants full key names, not glyphs */
  function ariaName(key) {
    if (key === ',') return 'Comma';
    if (key.length === 1) return key.toUpperCase();
    return key;
  }
  /* A control only counts from here when the visitor could actually reach it.
     A rect test alone is not enough: popovers on this site fade out with
     opacity + pointer-events instead of display:none, so the rows inside a
     closed menu keep their box and used to answer their hotkey anyway. A
     shut menu is therefore treated as hidden for the whole subtree, and only
     a menu that is genuinely open lets its rows answer. */
  var POPOVERS = '.glass-pop, .site-menu-pop, .help-pop';
  function isVisible(el) {
    if (!el) return false;
    var r = el.getBoundingClientRect();
    if (r.width <= 0 || r.height <= 0) return false;
    for (var n = el; n && n.nodeType === 1; n = n.parentElement) {
      if (n.matches && n.matches(POPOVERS) && !n.classList.contains('open')) return false;
      var cs = window.getComputedStyle(n);
      if (cs.display === 'none' || cs.visibility === 'hidden') return false;
      if (n === root) break;
    }
    return true;
  }
  function resolve(sel) {
    if (!sel) return null;
    var list = document.querySelectorAll(sel);
    for (var i = 0; i < list.length; i++) {
      if (isVisible(list[i])) return list[i];
    }
    return null;
  }
  /* Standdown rules, in order: settings.js's switch, any modifier, and the
     "never fire while typing" rule. Falls back to reading data-keys directly
     on pages that do not load settings.js. */
  function allow(e) {
    var K = window.FS_KEYS;
    if (K) return K.allow(e);
    if (root.getAttribute('data-keys') === 'off') return false;
    if (e.metaKey || e.ctrlKey || e.altKey) return false;
    var el = document.activeElement;
    var tag = ((el && el.tagName) || '').toUpperCase();
    return tag !== 'INPUT' && tag !== 'TEXTAREA' && tag !== 'SELECT' &&
           !(el && el.isContentEditable === true);
  }
  function norm(k) { return k && k.length === 1 ? k.toLowerCase() : k; }
  /* Non-Latin layouts (e.g. RU) produce Cyrillic chars in e.key, so letter
     shortcuts silently die. Fall back to the PHYSICAL key (e.code), which
     is layout-independent: KeyG fires 'g' even when it types 'п'. */
  function codeKey(code) {
    if (!code) return null;
    var m = /^Key([A-Z])$/.exec(code);
    if (m) return m[1].toLowerCase();
    var d = /^Digit([0-9])$/.exec(code);
    if (d) return d[1];
    if (code === 'Comma') return ',';
    if (code === 'Period') return '.';
    if (code === 'Slash') return '/';
    if (code === 'Semicolon') return ';';
    if (code === "Quote") return String.fromCharCode(39);
    return null;
  }
  function hotkeysOn() {
    var K = window.FS_KEYS;
    return K ? K.enabled() : root.getAttribute('data-keys') !== 'off';
  }

  /* ---------- keycap hints ---------- */
  /* keys remapped in the hotkeys editor must stop firing here: the editor's
     override dispatcher (hotkeys-modal.js) owns them instead */
  var stolenKeys = {};
  function refreshStolen() {
    stolenKeys = {};
    var c;
    try { c = JSON.parse(localStorage.getItem('fs-hotkey-custom') || '{}'); } catch (e) { return; }
    Object.keys(c).forEach(function (id) {
      MAP.forEach(function (reg, i) {
        /* ids are positional in the same order the editor's registry was
           modelled on; match by hint/selector semantics where possible */
      });
    });
    /* simple + robust: the editor calls FS_HOTKEYS.remap(custom) with
       { mapId: oldKey } derived from its registry; mark those keys stolen */
    if (window.FS_HOTKEYS_STOLEN) {
      window.FS_HOTKEYS_STOLEN.forEach(function (k) { stolenKeys[String(k).toLowerCase()] = true; });
    }
  }
  function keycap(reg) {
    var k = document.createElement('kbd');
    k.className = 'tab-kbd' + (reg.hint === 'rail' ? ' tab-kbd-rail' : '');
    k.setAttribute('aria-hidden', 'true');
    k.textContent = keyLabel(reg.key);
    return k;
  }
  /* Hints are injected once per page load. Element order matters for the
     settings rows: the iOS switch carries margin-left:auto, so the keycap
     lands to its right, matching the jump menu's rows. */
  function paintHints() {
    MAP.forEach(function (reg) {
      if (!reg.hint || !reg.sel) return;
      var el = resolve(reg.sel) || document.querySelector(reg.sel);
      if (!el) return;
      if (el.querySelector(':scope > .tab-kbd')) return;   /* already hinted */
      el.appendChild(keycap(reg));
    });
  }
  /* aria-keyshortcuts must not advertise keys that are switched off */
  function paintAria() {
    var on = hotkeysOn();
    MAP.forEach(function (reg) {
      if (!reg.sel) return;
      var list = document.querySelectorAll(reg.sel);
      for (var i = 0; i < list.length; i++) {
        if (on) {
          if (!list[i].getAttribute('aria-keyshortcuts')) {
            list[i].setAttribute('aria-keyshortcuts', ariaName(reg.key));
          }
          /* icon-only controls get a tooltip, since a keycap will not fit
             (or, for rail hints, because the top bar shows no keycap) */
          if ((reg.hint === false || reg.tip) && !list[i].getAttribute('title')) {
            list[i].setAttribute('title', reg.name + ' (' + keyLabel(reg.key) + ')');
          }
        } else {
          list[i].removeAttribute('aria-keyshortcuts');
        }
      }
    });
  }

  /* ---------- the dispatcher ---------- */
  function fire(mapKey) {
    for (var i = 0; i < MAP.length; i++) {
      var reg = MAP[i];
      if (norm(reg.key) !== mapKey) continue;
      if (reg.run) {
        reg.run();
        return true;
      }
      var el = reg.always ? document.querySelector(reg.sel) : resolve(reg.sel);
      if (el) {
        el.click();
        return true;
      }
    }
    return false;
  }
  /* K is the escape hatch: it must work even while the set is switched off,
     or one accidental press strands the visitor with no keyboard way back
     on (every other key stands down, and the hints hide with the switch). */
  function hatchKey(e) {
    if (e.metaKey || e.ctrlKey || e.altKey || e.shiftKey) return null;
    var K = window.FS_KEYS;
    if (K) { if (K.typing()) return null; }
    else {
      var el = document.activeElement;
      var tag = ((el && el.tagName) || '').toUpperCase();
      if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' ||
          (el && el.isContentEditable === true)) return null;
    }
    var k = norm(e.key);
    if (k === 'k') return 'k';
    var ck = codeKey(e.code);
    if (ck === 'k') return 'k';
    return null;
  }
  document.addEventListener('keydown', function (e) {
    if (e.defaultPrevented || e.repeat) return;
    /* While the hotkeys editor is open (or recording a binding) every key
       belongs to it — never fire page actions behind the dialog. */
    if (window.FS_HK_RECORDING) return;
    if (document.querySelector('.hk-overlay.open')) return;
    var hatch = !hotkeysOn() && hatchKey(e);
    if (!hatch && !allow(e)) return;
    /* Plain shortcuts take no Shift (see Conventions): without this gate
       Shift+B opened the Bot, Shift+, opened Settings, and Shift+digit hit
       the section keys through the layout fallback's physical code. */
    if (e.shiftKey) return;
    var k = hatch || norm(e.key);
    refreshStolen();
    if (stolenKeys[String(k).toLowerCase()] && !(e.ctrlKey || e.metaKey || e.altKey || e.shiftKey)) return;
    if (fire(k)) { e.preventDefault(); return; }
    var ck = codeKey(e.code);
    if (ck && ck !== k && fire(ck)) { e.preventDefault(); }
  });

  /* Settings > Hotkeys flips data-keys; keep the tooltips in step. */
  window.addEventListener('fs-hotkeys-change', function () { paintAria(); });

  function boot() { paintHints(); paintAria(); }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }

  window.FS_HOTKEYS = { map: MAP, paint: boot };
})();
