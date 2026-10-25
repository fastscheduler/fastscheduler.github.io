// Liquid scroll navbar: shared by the homepage, legal pages and help page.
// On scroll-down the navbar liquefies: settings icon flies to a right-side
// glass rail, links follow, the logo docks top-center. Scrolling back up
// pours everything home. Controlled by the site's Animations toggle.
(function () {
'use strict';
/* NOTE: briefly disabled after a misread bug report; restored per site owner
   request — the scroll "liquefy" into the side rail is an intended feature. */
if (!window.matchMedia || matchMedia('(max-width: 860px)').matches) return;
if (!document.documentElement.animate) return;
    /* Reduced motion no longer kills the feature: it switches to an instant,
       animation-free swap, so the nav still works when the OS has its own
       animations turned off. The site's own Animations toggle (Settings menu)
       is the single control that disables it completely. */
    function motionOff() { return document.documentElement.getAttribute('data-motion') === 'off'; }

    var nav = document.querySelector('.home-nav') ||
              (document.querySelector('header.site') && document.querySelector('header.site').querySelector('.nav')) ||
              document.querySelector('.legal-nav');
    if (!nav) return;
    var brand = nav.querySelector(':scope > .brand') || nav.querySelector('.brand');
    var linksBox = nav.querySelector(':scope > nav');
    var settings = (linksBox && linksBox.querySelector(':scope > .settings-wrap')) || nav.querySelector(':scope > .settings-wrap') || nav.querySelector('.settings-wrap');
    var burger = nav.querySelector('#navBurger');
    if (!brand || !settings || !linksBox) return;
    var settingsHome = settings.parentElement;   /* linksBox on index, .home-nav on legal/help */
    var links = Array.prototype.filter.call(linksBox.children, function (c) { return c.tagName === 'A'; });

    /* exact home positions, captured once at init: restoring in reverse
       order guarantees every anchor node is already home when needed */
    var helpRow0 = linksBox.querySelector(':scope > .help-row');
    var cta0 = nav.querySelector(':scope > .nav-cta-sm') || nav.querySelector(':scope > .nav-cta') || (linksBox && linksBox.querySelector(':scope > .nav-cta-sm'));
    var support0 = nav.querySelector(':scope > .support-ib') || (linksBox && linksBox.querySelector(':scope > .support-ib'));
    var homeSpots = [{ el: brand, parent: brand.parentElement, next: brand.nextSibling }];
    links.forEach(function (a) { homeSpots.push({ el: a, parent: a.parentElement, next: a.nextSibling }); });
    if (helpRow0) homeSpots.push({ el: helpRow0, parent: helpRow0.parentElement, next: helpRow0.nextSibling });
    if (cta0) homeSpots.push({ el: cta0, parent: cta0.parentElement, next: cta0.nextSibling });
    if (support0) homeSpots.push({ el: support0, parent: support0.parentElement, next: support0.nextSibling });
    if (burger && linksBox.contains(burger)) homeSpots.push({ el: burger, parent: burger.parentElement, next: burger.nextSibling });
    homeSpots.push({ el: settings, parent: settings.parentElement, next: settings.nextSibling });

    /* stage: liquid layer + rail + dock */
    var blobLayer = document.createElement('div');
    blobLayer.className = 'liquid-layer';
    blobLayer.setAttribute('aria-hidden', 'true');
    var mainBlob = document.createElement('div'); mainBlob.className = 'liquid-blob';
    var dropC = document.createElement('div'); dropC.className = 'liquid-drop drop-center';
    var dropL = document.createElement('div'); dropL.className = 'liquid-drop drop-left';
    blobLayer.appendChild(mainBlob); blobLayer.appendChild(dropC); blobLayer.appendChild(dropL);

    var rail = document.createElement('aside');
    rail.className = 'nav-rail';
    rail.setAttribute('aria-label', 'Sections');
    rail.innerHTML = '<div class="rail-inner"><button type="button" class="rail-tab" aria-label="Hide panel" title="Hide panel (S)"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg><kbd class="tab-kbd" aria-hidden="true">S</kbd></button><span class="rail-pill"></span><div class="rail-links"></div><div class="rail-foot"></div></div>';
    var railInner = rail.querySelector('.rail-inner');
    var railLinks = rail.querySelector('.rail-links');
    var railPill = rail.querySelector('.rail-pill');

    var dock = document.createElement('div');
    dock.className = 'brand-dock';

    document.body.appendChild(blobLayer);
    document.body.appendChild(rail);
    document.body.appendChild(dock);

    var moved = false, busy = false, draining = false, pendingReact = false;
    var ON = 440, OFF = 220;   /* hysteresis thresholds */
    var EASE = 'cubic-bezier(.3,.7,.25,1)';

    function center(r) { return { x: r.left + r.width / 2, y: r.top + r.height / 2 }; }

    /* Smooth FLIP flight: one gentle arc, tiny tilt, barely-there squash.
       One easing for the whole flight — no keyframe easing flips. */
    function fly(el, from, opts) {
      var to = el.getBoundingClientRect();
      var fc = center(from), tc = center(to);
      var dx = fc.x - tc.x, dy = fc.y - tc.y;
      var mx = opts.mx || 0, my = opts.my || 0;
      var rot = opts.rot || 0, sq = opts.sq || 0;
      el.animate([
        { transform: 'translate(' + dx + 'px,' + dy + 'px) rotate(' + rot + 'deg)' },
        { transform: 'translate(' + (dx * .5 + mx) + 'px,' + (dy * .5 + my) + 'px) rotate(' + (rot * .4) + 'deg) scale(' + (1 + sq) + ',' + (1 - sq) + ')', offset: .55 },
        { transform: 'translate(0,0) rotate(0deg) scale(1,1)' }
      ], { duration: opts.dur, delay: opts.delay || 0, easing: EASE, fill: 'both' });
    }

    function killBackdrop(el) { el.style.webkitBackdropFilter = 'none'; el.style.backdropFilter = 'none'; }
    function restoreBackdrop(el) { el.style.webkitBackdropFilter = ''; el.style.backdropFilter = ''; }
    /* A fly() animation holds its end state via fill:'both'. If one ever
       stalls mid-flight (background tab, throttled compositor, toggle
       mid-flight) the item parks off-position permanently — the gear ends
       up floating above the rail with no way back. Every flight ends on an
       identity transform, so forcing stalled flights to completion and then
       dropping them is visually free and guarantees nothing can stick. */
    function settleFlights() {
      var els = [settings, brand, helpRow, supportIb, getCta()].concat(links);
      els.forEach(function (el) {
        if (!el || !el.getAnimations) return;
        el.getAnimations().forEach(function (a) {
          try { a.finish(); } catch (e) {}
          try { a.cancel(); } catch (e) {}
        });
      });
    }

    /* The glass bar pours from the navbar to the rail: short, soft morph
       with a whisper of overshoot. Blur is disabled mid-flight (animating
       backdrop-filter is a GPU killer and the main source of jank).
       Callers skip this entirely when the rail has no box to land on — an
       animation with no destination leaves the glass parked over the page as
       a bare rectangle (that flash at the right edge). */
    function flowBlob(fromR) {
      var toR = rail.getBoundingClientRect();
      if (!toR.width || !toR.height) return;
      /* a zero-size source box turns the scale math into Infinity, which
         the compositor rejects (and logs) while leaving the blob parked */
      if (!fromR.width || !fromR.height) return;
      var fc = center(fromR), tc = center(toR);
      var dx = tc.x - fc.x, dy = tc.y - fc.y;
      var sx = toR.width / fromR.width, sy = toR.height / fromR.height;
      mainBlob.style.left = fromR.left + 'px';
      mainBlob.style.top = fromR.top + 'px';
      mainBlob.style.width = fromR.width + 'px';
      mainBlob.style.height = fromR.height + 'px';
      killBackdrop(mainBlob);
      var anim = mainBlob.animate([
        { transform: 'translate(0,0) scale(1,1)', borderRadius: '18px' },
        { transform: 'translate(' + (dx * .45 + 12) + 'px,' + (dy * .55 - 12) + 'px) scale(' + ((1 + sx) / 2) + ',' + ((1 + sy) / 2) + ')', borderRadius: '30% 70% 60% 40% / 45% 42% 58% 55%', offset: .5 },
        { transform: 'translate(' + dx + 'px,' + dy + 'px) scale(' + sx + ',' + sy + ')', borderRadius: '24px' }
      ], { duration: 640, delay: 40, easing: EASE, fill: 'forwards' });
      anim.onfinish = function () { restoreBackdrop(mainBlob); };
    }    var helpRow = helpRow0;
    var helpWrap = helpRow ? helpRow.querySelector('.help-wrap') : null;
    var supportIb = nav.querySelector(':scope > .support-ib') || (linksBox && linksBox.querySelector(':scope > .help-row .support-ib'));
    var railFoot = rail.querySelector('.rail-foot');
    function getCta() {
      return nav.querySelector(':scope > .nav-cta-sm') ||
             nav.querySelector(':scope > .nav-cta') ||
             (linksBox && linksBox.querySelector(':scope > .nav-cta-sm')) ||
             railFoot.querySelector(':scope > .nav-cta-sm') ||
             railFoot.querySelector(':scope > .nav-cta');
    }
    /* exact home positions, captured once at init: restoring in reverse
       order guarantees every anchor node is already home when needed */
    var homeSpots = (function captureHome() {
      var seq = [{ el: brand, parent: brand.parentElement, next: brand.nextSibling }];
      links.forEach(function (a) { seq.push({ el: a, parent: a.parentElement, next: a.nextSibling }); });
      if (helpRow) seq.push({ el: helpRow, parent: helpRow.parentElement, next: helpRow.nextSibling });
      var cta0 = getCta();
      if (cta0) seq.push({ el: cta0, parent: cta0.parentElement, next: cta0.nextSibling });
      var support0 = nav.querySelector(':scope > .support-ib') || (linksBox && linksBox.querySelector(':scope > .support-ib'));
      if (support0) seq.push({ el: support0, parent: support0.parentElement, next: support0.nextSibling });
      if (burger && linksBox.contains(burger)) seq.push({ el: burger, parent: burger.parentElement, next: burger.nextSibling });
      seq.push({ el: settings, parent: settings.parentElement, next: settings.nextSibling });
      return seq;
    })();
    function relocateOut() {
      var cta = getCta();
      railInner.appendChild(railLinks);
      links.forEach(function (a) { railLinks.appendChild(a); });
      if (helpRow) { railLinks.appendChild(helpRow); }
      /* gear trails the Open Bot CTA in the rail footer, same as the top bar */
      if (supportIb && railFoot) railFoot.appendChild(supportIb);
      if (cta) railFoot.appendChild(cta);
      if (settings && railFoot) railFoot.appendChild(settings);
      dock.appendChild(brand);
    }

    function relocateHome() {
      /* restore every captured node to its exact home spot, in FORWARD
         order: a node whose successor is already home is inserted exactly
         before it; otherwise it is appended (a later node with a valid
         anchor then pushes it into place) */
      homeSpots.forEach(function (s) {
        if (!s.parent || !s.el) return;
        if (s.next && s.next.parentNode === s.parent) s.parent.insertBefore(s.el, s.next);
        else s.parent.appendChild(s.el);
      });
      railFoot.textContent = '';
    }
    function cleanupBlobs() {
      mainBlob.getAnimations().concat(dropC.getAnimations(), dropL.getAnimations(),
        blobLayer.getAnimations(), nav.getAnimations()).forEach(function (a) { a.cancel(); });
      restoreBackdrop(mainBlob);
      /* Forget the box the blob last flew to. A leftover rect is invisible
         while the layer is settled, but the moment the settled class comes off
         (scrolling back up) it would pop back as a dark panel. */
      mainBlob.style.width = '0px';
      mainBlob.style.height = '0px';
    }

    function instantOn() {
      relocateOut();
      document.body.classList.add('liquid-mode', 'liquid-settled');
      moved = true; busy = false;
      updatePill();
    }
    /* center the docked logo against the real layout box (viewport minus
       scrollbar), not the raw viewport — `left: 50%` on Windows sits it
       ~half a scrollbar off the visual center */
    function centerDock() {
      var w = document.documentElement.clientWidth;
      dock.style.left = (w / 2) + 'px';
    }
    window.addEventListener('resize', centerDock);
    centerDock();
    function instantOff() {
      relocateHome();
      document.body.classList.remove('liquid-mode', 'liquid-settled', 'liquid-drain');
      brand.classList.remove('landed');
      cleanupBlobs();
      railPill.style.opacity = '0';
      moved = false; busy = false; draining = false;
    }

    function activate() {
      if (moved || busy) return;
      /* Animations off (site setting): still liquefy, just without motion —
         an instant swap so the nav is always present while scrolled. */
      if (motionOff()) { instantOn(); return; }
      busy = true;
      try {
        var navR = nav.getBoundingClientRect();
        var items = [{ el: settings }].concat(links.map(function (a) { return { el: a }; })).concat([{ el: brand }]);
        var snaps = items.map(function (it) { return { el: it.el, r: it.el.getBoundingClientRect() }; });

        relocateOut();
        document.body.classList.add('liquid-mode');

        /* settings icon leaves FIRST on a gentle curve */
        fly(settings, snaps[0].r, { dur: 640, delay: 0, mx: 30, my: -16, rot: 4 });
        /* links follow, short staggered arcs, almost no tilt */
        links.forEach(function (a, i) {
          fly(a, snaps[i + 1].r, { dur: 600, delay: 80 + i * 45, mx: 22 + (i % 2) * 8, my: -10 + i * 3, rot: i % 2 ? -2 : 2, sq: .03 });
        });
        /* the logo does NOT fly across the page — the dock fades it in
           softly instead (a long cross-screen slide reads as creepy) */
        /* With the panel collapsed there is nothing to pour into — the rail
           is off-screen, so the blob would fly to an empty box and flash as a
           rectangle at the right edge. The tab keeps its own glass; skip it. */
        if (!document.documentElement.classList.contains('rail-off')) flowBlob(navR);
        setTimeout(function () { brand.classList.add('landed'); }, 200);
        setTimeout(function () {
          document.body.classList.add('liquid-settled');
          settleFlights();
          busy = false; moved = true;
          updatePill();
        }, 1100);
      } catch (e) { instantOn(); }
    }

    function deactivate() {
      if (!moved || busy) return;
      if (motionOff()) { instantOff(); return; }
      busy = true; draining = true;
      try {
        var toR = nav.getBoundingClientRect();
        var fromR = rail.getBoundingClientRect();
        var fc = center(fromR), tc = center(toR);
        var dx = tc.x - fc.x, dy = tc.y - fc.y;
        var sx = toR.width / fromR.width, sy = toR.height / fromR.height;
        document.body.classList.add('liquid-drain');
        document.body.classList.remove('liquid-settled');
        /* collapsed panel: there is nothing on screen to pour back out of, and
           whatever the blob last held would show up as a dark panel */
        if (document.documentElement.classList.contains('rail-off')) {
          /* !important: a live animation on the layer would outrank an inline
             declaration, and this has to win */
          blobLayer.style.setProperty('opacity', '0', 'important');
        } else if (!fromR.width || !fromR.height || !toR.width || !toR.height) {
          /* collapsed panel: nothing on screen to pour out of either */
          blobLayer.style.setProperty('opacity', '0', 'important');
        } else {
          mainBlob.style.left = fromR.left + 'px';
          mainBlob.style.top = fromR.top + 'px';
          mainBlob.style.width = fromR.width + 'px';
          mainBlob.style.height = fromR.height + 'px';
          killBackdrop(mainBlob);
          mainBlob.animate([
            { transform: 'translate(0,0) scale(1,1)', borderRadius: '24px' },
            { transform: 'translate(' + (dx * .45 - 10) + 'px,' + (dy * .5 + 12) + 'px) scale(' + (sx * .65) + ',' + (sy * 1.06) + ')', borderRadius: '35% 65% 55% 45% / 44% 48% 52% 56%', offset: .5 },
            { transform: 'translate(' + dx + 'px,' + dy + 'px) scale(' + sx + ',' + sy + ')', borderRadius: '18px' }
          ], { duration: 560, delay: 30, easing: EASE, fill: 'forwards' });
          blobLayer.animate([{ opacity: 1 }, { opacity: 1, offset: .75 }, { opacity: 0 }], { duration: 780, delay: 30, fill: 'forwards' });
        }

        /* snapshot old spots, relocate, then fly everyone home */
        var ctaEl = getCta();
        var brandFrom = brand.getBoundingClientRect();
        var linkFrom = links.map(function (a) { return a.getBoundingClientRect(); });
        var setFrom = settings.getBoundingClientRect();
        var helpFrom = helpRow ? helpRow.getBoundingClientRect() : null;
        var suppFrom = supportIb ? supportIb.getBoundingClientRect() : null;
        var ctaFrom = ctaEl ? ctaEl.getBoundingClientRect() : null;
        relocateHome();
        document.body.classList.remove('liquid-mode');
        nav.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 380, delay: 240, fill: 'both' });
        fly(brand, brandFrom, { dur: 480, delay: 40, mx: 0, my: 0, rot: 0, sq: 0 });
        links.forEach(function (a, i) {
          fly(a, linkFrom[i], { dur: 520, delay: 140 + i * 40, mx: -20 - (i % 2) * 8, my: 18 + i * 3, rot: i % 2 ? 2 : -2, sq: .03 });
        });
        if (helpRow) fly(helpRow, helpFrom, { dur: 520, delay: 260, mx: -20, my: 16, rot: -2, sq: .03 });
        fly(settings, setFrom, { dur: 560, delay: 320, mx: -26, my: 20, rot: -3 });
        if (supportIb) fly(supportIb, suppFrom, { dur: 520, delay: 380, mx: -24, my: 14, rot: 2, sq: .03 });
        if (ctaEl) fly(ctaEl, ctaFrom, { dur: 520, delay: 200, mx: -26, my: 16, rot: -2, sq: .03 });

        setTimeout(function () {
          document.body.classList.remove('liquid-drain');
          brand.classList.remove('landed');
          settleFlights();
          cleanupBlobs();
          blobLayer.style.removeProperty('opacity');
          railPill.style.opacity = '0';
          busy = false; moved = false; draining = false;
          /* user scrolled back down mid-drain: pour forward again */
          if (pendingReact) {
            pendingReact = false;
            if (window.scrollY > ON) { activate(); return; }
          }
        }, 880);
      } catch (e) { instantOff(); }
    }

    /* scrollspy: green pill slides to the active section (legal-pages style).
       Resolve against the rail's own links rather than against a list of
       section ids: #steps is an <h2> *inside* #how, so "the last section above
       the line" could land on a heading that owns no row, which is why the
       "How it works" link never lit up. */
    var spyPairs = [];
    links.forEach(function (a) {
      var id = (a.getAttribute('href') || '').slice(1);
      var sec = id ? document.getElementById(id) : null;
      if (sec) spyPairs.push({ a: a, sec: sec });
    });
    function absTop(el) { return el.getBoundingClientRect().top + window.scrollY; }
    spyPairs.sort(function (p, q) { return absTop(p.sec) - absTop(q.sec); });
    function updatePill() {
      /* scrollspy runs in BOTH states: green text on the top-navbar link
         when home, green text + sliding pill when liquefied */
      var active = null;
      spyPairs.forEach(function (p) {
        if (p.sec.getBoundingClientRect().top <= window.innerHeight * .42) active = p;
      });
      Array.prototype.forEach.call(railLinks.querySelectorAll('a.active'), function (x) {
        x.classList.remove('active');
      });
      if (active) {
        active.a.classList.add('active');
        if (!moved) return;   /* top navbar: no pill to slide */
        railPill.style.transform = 'translateY(' + (active.a.offsetTop - 10) + 'px)';
        railPill.style.height = active.a.offsetHeight + 'px';
        railPill.style.opacity = '1';
        return;
      }
      railPill.style.opacity = '0';
    }
    /* keep in-page nav clicks working after nodes moved into the rail */
    document.addEventListener('click', function (e) {
      var a = e.target.closest && e.target.closest('a[href^="#"]');
      if (!a || !moved) return;
      var id = a.getAttribute('href').slice(1);
      var t = document.getElementById(id);
      if (!t) return;
      e.preventDefault();
      t.scrollIntoView({ behavior: motionOff() ? 'auto' : 'smooth', block: 'start' });
    });

    /* rail collapse arrow: persisted, motion-aware */
    var railTab = rail.querySelector('.rail-tab');
    if (railTab) {
      try { if (localStorage.getItem('fs-rail') === 'off') document.documentElement.classList.add('rail-off'); } catch (e) {}
      railTab.addEventListener('click', function () {
        var off = document.documentElement.classList.toggle('rail-off');
        railTab.setAttribute('aria-label', off ? 'Show panel' : 'Hide panel');
        try { localStorage.setItem('fs-rail', off ? 'off' : 'on'); } catch (e) {}
      });
    }

    /* S = toggle the rail panel (desktop only). FS_KEYS from settings.js owns
       the site-wide Hotkeys switch and the "never fire while typing" rule;
       fall back to an inline guard if the settings script has not loaded. */
    document.addEventListener('keydown', function (e) {
      if (e.key !== 's' && e.key !== 'S') return;
      /* Unshifted S only: Shift+S is a combo for the hotkeys editor, never
         the panel toggle. While the editor is open (or recording) keys
         belong to it. */
      if (e.shiftKey) return;
      if (window.FS_HK_RECORDING) return;
      if (document.querySelector('.hk-overlay.open')) return;
      if (window.innerWidth <= 860) return;
      if (!railTab) return;
      var K = window.FS_KEYS;
      if (K) {
        if (!K.allow(e)) return;
      } else {
        if (e.ctrlKey || e.metaKey || e.altKey) return;
        var el = document.activeElement;
        var tag = (el && el.tagName) || '';
        if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || (el && el.isContentEditable)) return;
      }
      e.preventDefault();
      railTab.click();
    });

    /* Settings > Hotkeys and the rail switch both write fs-rail to localStorage.
       settings.js re-broadcasts cross-tab changes, so the collapsed/shown state
       of the panel now follows the visitor from page to page. */
    window.addEventListener('fs-rail-change', function (e) {
      if (!railTab) return;
      var off = !!(e && e.detail && e.detail.off);
      document.documentElement.classList.toggle('rail-off', off);
      railTab.setAttribute('aria-label', off ? 'Show panel' : 'Hide panel');
    });

    var ticking = false;
    window.addEventListener('scroll', function () {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(function () {
        var y = window.scrollY;
        if (busy && draining && y > ON) { pendingReact = true; }
        else if (!moved && y > ON) activate();
        else if (moved && y < OFF) deactivate();
        updatePill();
        ticking = false;
      });
    }, { passive: true });

    window.addEventListener('resize', function () {
      if (moved && window.innerWidth <= 860) deactivate();
    });
    /* react instantly when the user toggles Animations in Settings */
    new MutationObserver(function () {
      if (moved && motionOff()) deactivate();
    }).observe(document.documentElement, { attributes: true, attributeFilter: ['data-motion'] });
})();
