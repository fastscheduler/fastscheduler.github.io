/* Hide-on-scroll chrome (shared, every page, mobile + desktop).
   - html.nav-hidden slides the navbar off-screen with a transform (GPU,
     animated — never display:none, so the layout never jumps or reflows).
   - Elements that sit below the navbar and hug the same edge (bottom bars:
     toc-bar, cookie banner, Contents FAB, jump FAB) get .nav-slide-up /
     .nav-slide-down so they slide away/together with the bar instead of
     leaving an empty strip where the navbar used to be.
   - Desktop and mobile behave the same; "down" hides, scrolling up reveals.
   - Never hides while a popover/sheet/menu is open, while typing, or within
     350ms of a programmatic jump (anchor links, scroll-jump FAB).
*/
(function () {
  var doc = document.documentElement;
  var body = document.body;
  if (!body) return;

  var bar = document.querySelector('.home-nav') || document.querySelector('header.site');
  if (!bar) return;

  var HIDE_AFTER = 140;   /* px of downward travel before hiding */
  var SHOW_DELTA = 6;     /* px of upward travel before showing */
  var SNAP_AT_TOP = 40;   /* always show near the top of the page */
  var PIN = 350;          /* grace period after programmatic scrolls */

  var lastY = currentY(), pinned = 0, hidden = false, ticking = false;

  /* Publish the bar's height so CSS can release its reserved space when it
     hides (fixed bars on the homepage use padding-top; the legal app-shell
     is a flex column where the header owns a layout slot). */
  function measure() {
    doc.style.setProperty('--nav-h', bar.offsetHeight + 'px');
  }
  measure();
  window.addEventListener('resize', measure, { passive: true });

  function inner() {
    /* legal pages on phones scroll inside main.legal (app shell) */
    if (body.classList.contains('legal') && window.matchMedia &&
        matchMedia('(max-width: 760px)').matches) {
      var m = document.querySelector('main.legal');
      if (m) return m;
    }
    return null;
  }
  function currentY() {
    var sc = inner();
    return sc ? sc.scrollTop : (window.scrollY || window.pageYOffset || 0);
  }
  function maxY() {
    var sc = inner();
    if (sc) return sc.scrollHeight - sc.clientHeight;
    return document.documentElement.scrollHeight - window.innerHeight;
  }

  function openPopoverOpen() {
    /* don't fight an open menu/sheet — it may be anchored to the bar */
    if (document.querySelector('.glass-pop.open, .nav-mobile.open, .toc-sheet.open, .site-menu-pop.open, .hc-toc-sheet.open, .blog-toc-sheet.open')) return true;
    var el = document.activeElement;
    if (el && (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA' || el.isContentEditable)) return true;
    return false;
  }

  function show() {
    if (!hidden) return;
    hidden = false;
    doc.classList.remove('nav-hidden');
  }
  function hide() {
    if (hidden) return;
    hidden = true;
    doc.classList.add('nav-hidden');
  }

  function update() {
    ticking = false;
    var y = currentY();
    var delta = y - lastY;

    if (Date.now() < pinned || openPopoverOpen()) { lastY = y; show(); return; }
    if (y <= SNAP_AT_TOP) { lastY = y; show(); return; }

    if (delta > 0 && y > HIDE_AFTER) {
      if (delta > SHOW_DELTA || !hidden) hide();
    } else if (delta < -SHOW_DELTA) {
      show();
    }
    lastY = y;
  }

  function onScroll() {
    if (!ticking) { ticking = true; requestAnimationFrame(update); }
  }

  window.addEventListener('scroll', onScroll, { passive: true });
  var sc = inner();
  if (sc) sc.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', function () {
    /* scroller may change between mobile/desktop layouts */
    measure();
    var n = inner();
    if (n !== sc) { if (sc) sc.removeEventListener('scroll', onScroll); sc = n; if (sc) sc.addEventListener('scroll', onScroll, { passive: true }); }
    lastY = currentY(); show();
  }, { passive: true });

  /* anchor links and the jump FAB scroll programmatically — never fight them */
  document.addEventListener('click', function (e) {
    if (e.target.closest && e.target.closest('a[href^="#"], .jump-fab, .hc-fab, .toc-burger')) pinned = Date.now() + PIN;
  });
  window.addEventListener('fs-jump', function () { pinned = Date.now() + PIN; });

  /* keyboard scroll keys: reveal immediately so focus is never lost */
  window.addEventListener('keydown', function (e) {
    var k = e.key;
    if (k === 'ArrowUp' || k === 'PageUp' || k === 'Home' || k === 'End' || k === 'ArrowDown' || k === 'PageDown') show();
  });

  /* touch: a touchend followed by upward momentum is handled by scroll events;
     a simple tap on the page near the top restores the bar */
  body.addEventListener('touchstart', function () { pinned = Date.now() + 120; }, { passive: true });

  lastY = currentY();
})();
