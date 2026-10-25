/* Cookie consent + Google Tag Manager loader.
 *
 * Rules this file enforces:
 *   1. Nothing is loaded from Google until the visitor clicks Accept. Declining
 *      loads no script, sets no dataLayer and sends no request at all — the tag
 *      is not merely disabled, it is never injected.
 *   2. The choice is stored in localStorage (`cookie_consent`) and mirrored in
 *      the first-party `consent` cookie, so pages, the legal text and any later
 *      script agree on one value: 'accepted' | 'declined'.
 *   3. A "Cookie settings" link is added to the footer so the choice can be
 *      changed later; choosing Decline after Accept also removes the Google
 *      Analytics cookies the tag may already have written.
 *
 * The banner markup is created here instead of living in 1200+ pages, so a page
 * only needs:  <script src="…/scripts/consent.js?v=…" defer></script>
 */
(function () {
  'use strict';

  var GTM_ID = 'GTM-P9L5JD26';
  var STORE_KEY = 'cookie_consent';
  var COOKIE_MAX_AGE = 31536000; /* 1 year, same as the legal text */

  /* ---------- helpers --------------------------------------------------- */

  function readChoice() {
    var v = null;
    try { v = localStorage.getItem(STORE_KEY); } catch (e) {}
    if (v !== 'accepted' && v !== 'declined') {
      var m = document.cookie.match(/(?:^|;\s*)consent=(accepted|declined)/);
      if (m) v = m[1];
    }
    return (v === 'accepted' || v === 'declined') ? v : null;
  }

  function saveChoice(choice) {
    try { localStorage.setItem(STORE_KEY, choice); } catch (e) {}
    try {
      document.cookie = 'consent=' + choice + ';path=/;max-age=' + COOKIE_MAX_AGE +
        ';samesite=lax;secure';
    } catch (e) {}
  }

  function rootPath() {
    /* scripts/consent.js -> "" at the site root, "../../" two levels deep */
    var el = document.currentScript;
    var src = (el && el.src) || '';
    var i = src.indexOf('/scripts/consent.js');
    if (i < 0) {
      /* currentScript is empty for async/older browsers: derive from the tag */
      var tags = document.getElementsByTagName('script');
      for (var n = 0; n < tags.length; n++) {
        if (tags[n].src && tags[n].src.indexOf('/scripts/consent.js') > -1) {
          src = tags[n].src; i = src.indexOf('/scripts/consent.js'); break;
        }
      }
    }
    return i > -1 ? src.slice(0, i) : '';
  }

  var ROOT = rootPath();

  /* ---------- Google Tag Manager --------------------------------------- */

  var gtmLoaded = false;

  function loadGTM() {
    if (gtmLoaded) return;
    gtmLoaded = true;
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({ 'gtm.start': new Date().getTime(), event: 'gtm.js' });
    var first = document.getElementsByTagName('script')[0];
    var tag = document.createElement('script');
    tag.async = true;
    tag.src = 'https://www.googletagmanager.com/gtm.js?id=' + GTM_ID;
    /* re-push the consent signal once the container has booted, so tags that
       listen for it fire with the right state */
    tag.addEventListener('load', function () {
      window.dataLayer.push({ event: 'consent_update', consent: 'accepted' });
    });
    first.parentNode.insertBefore(tag, first);
  }

  function dropAnalyticsCookies() {
    var host = location.hostname;
    var domains = ['', ';domain=' + host, ';domain=.' + host];
    var names = document.cookie.split(';').map(function (c) {
      return c.split('=')[0].trim();
    }).filter(function (n) {
      return /^(_ga|_ga_.+|_gid|_gat(_|$).*|_gcl_.+)$/.test(n);
    });
    names.forEach(function (name) {
      domains.forEach(function (d) {
        document.cookie = name + '=;path=/;max-age=0;samesite=lax' + d;
      });
    });
  }

  /* ---------- banner ---------------------------------------------------- */

  var COPY = {
    en: {
      text: 'We use cookies to measure how this site is used. Accepting loads ' +
            'Google Tag Manager; if you decline, nothing is loaded and no data ' +
            'is collected.',
      accept: 'Accept',
      decline: 'Decline',
      more: 'Privacy Policy',
      settings: 'Cookie settings',
      title: 'Cookies'
    },
    ru: {
      text: 'Мы используем cookie, чтобы понимать, как используется сайт. При ' +
            'согласии загружается Google Tag Manager; при отказе ничего не ' +
            'загружается и данные не собираются.',
      accept: 'Принять',
      decline: 'Отклонить',
      more: 'Политика конфиденциальности',
      settings: 'Настройки cookie',
      title: 'Cookie'
    },
    es: {
      text: 'Usamos cookies para medir cómo se utiliza este sitio. Al aceptar se ' +
            'carga Google Tag Manager; si lo rechazas, no se carga nada y no se ' +
            'recogen datos.',
      accept: 'Aceptar',
      decline: 'Rechazar',
      more: 'Política de privacidad',
      settings: 'Ajustes de cookies',
      title: 'Cookies'
    }
  };

  function copy() {
    var lang = (document.documentElement.lang || 'en').slice(0, 2).toLowerCase();
    return COPY[lang] || COPY.en;
  }

  var CSS = [
    /* Hidden with display:none, not an off-screen transform: a banner parked
       outside the viewport is unclickable if the animation never runs (reduced
       motion, throttled tab), and a consent banner that cannot be answered is
       a broken gate, not a cosmetic bug. */
    '.fs-cookie{position:fixed;left:16px;right:16px;bottom:16px;z-index:2147483000;',
    'max-width:720px;margin:0 auto;padding:16px 18px;display:none;gap:14px;',
    'align-items:center;flex-wrap:wrap;border-radius:14px;',
    'border:1px solid rgba(120,130,150,.35);',
    'background:var(--surface,#fff);color:var(--text,#12202f);',
    'box-shadow:0 12px 40px rgba(10,20,40,.18);',
    'font:15px/1.45 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}',
    '.fs-cookie.show{display:flex;animation:fs-cookie-in .28s ease}',
    '@keyframes fs-cookie-in{from{transform:translateY(120%);opacity:.5}to{transform:none;opacity:1}}',
    '@media (prefers-reduced-motion:reduce){.fs-cookie.show{animation:none}}',
    '.fs-cookie p{margin:0;flex:1 1 320px;color:inherit;opacity:.85}',
    '.fs-cookie a{color:inherit;text-decoration:underline}',
    /* the actions take a row of their own: Accept sits at the far end of that
       row (margin-left:auto) and is deliberately the larger target, while
       Decline keeps its original weight and position */
    '.fs-cookie .fs-actions{display:flex;gap:10px;flex-wrap:wrap;align-items:center;',
    'flex:1 1 100%}',
    '.fs-cookie button{font:inherit;font-weight:700;padding:9px 16px;border-radius:10px;',
    'cursor:pointer;border:1px solid rgba(120,130,150,.5);background:transparent;color:inherit}',
    '.fs-cookie button.fs-accept{background:#1f9d55;border-color:#1f9d55;color:#fff;',
    'margin-left:auto;min-width:168px;padding:12px 28px;font-size:16px;border-radius:12px}',
    '.fs-cookie button:hover{filter:brightness(1.06)}',
    '@media (prefers-color-scheme:dark){.fs-cookie{background:var(--surface,#141a21);',
    'color:var(--text,#e8eef5);border-color:rgba(140,150,170,.35)}}',
    '.fs-cookie-link{background:none;border:0;padding:0;font:inherit;color:inherit;',
    'opacity:.8;cursor:pointer;text-decoration:underline}'
  ].join('');

  var banner = null;

  function buildBanner() {
    if (banner) return banner;
    var c = copy();
    if (!document.getElementById('fs-cookie-style')) {
      var st = document.createElement('style');
      st.id = 'fs-cookie-style';
      st.textContent = CSS;
      document.head.appendChild(st);
    }
    banner = document.createElement('div');
    banner.className = 'fs-cookie';
    banner.id = 'cookieBanner';
    banner.setAttribute('role', 'dialog');
    banner.setAttribute('aria-label', c.title);
    banner.innerHTML =
      '<p>' + c.text + '<br><a href="' + ROOT + '/legal/privacy.html">' + c.more + '</a></p>' +
      '<div class="fs-actions">' +
      '<button type="button" data-cookie="decline">' + c.decline + '</button>' +
      '<button type="button" class="fs-accept" data-cookie="accept">' + c.accept + '</button>' +
      '</div>';
    /* the choice is written by main.js on the same keys; do it here too so the
       banner works on pages that do not load main.js */
    banner.addEventListener('click', function (ev) {
      var btn = ev.target.closest ? ev.target.closest('[data-cookie]') : null;
      if (!btn) return;
      decide(btn.getAttribute('data-cookie') === 'accept' ? 'accepted' : 'declined');
    });
    document.body.appendChild(banner);
    return banner;
  }

  function showBanner() {
    var el = buildBanner();
    setTimeout(function () { el.classList.add('show'); }, 600);
  }

  function hideBanner() {
    if (banner) banner.classList.remove('show');
  }

  function decide(choice) {
    saveChoice(choice);
    hideBanner();
    if (choice === 'accepted') {
      loadGTM();
    } else {
      dropAnalyticsCookies();
      /* keep the object for pages that probe it, but nothing is sent */
      window.dataLayer = window.dataLayer || [];
      window.dataLayer.push({ event: 'consent_update', consent: 'declined' });
    }
    syncSettingsLink();
  }

  /* ---------- "Cookie settings" entry point ----------------------------- */

  function syncSettingsLink() {
    var host = document.querySelector('[data-cookie-settings]');
    if (!host) {
      var footer = document.querySelector('footer .foot, footer, #site-footer');
      if (!footer) return;
      var wrap = document.createElement('div');
      wrap.className = 'fs-cookie-host';
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'fs-cookie-link';
      btn.setAttribute('data-cookie-settings', '');
      btn.addEventListener('click', function (ev) {
        ev.preventDefault();
        showBanner();
      });
      wrap.appendChild(btn);
      footer.appendChild(wrap);
      host = btn;
    }
    host.textContent = copy().settings;
  }

  /* ---------- boot ------------------------------------------------------ */

  function boot() {
    var choice = readChoice();
    if (choice === 'accepted') {
      loadGTM();
    } else if (choice === 'declined') {
      /* nothing to undo: no tag was ever injected */
    } else {
      showBanner();
    }
    syncSettingsLink();
    /* The footer is injected by site-footer.js after this runs, and on some
       templates it arrives late — without these retries the "Cookie settings"
       entry point would silently be missing on those pages. */
    window.addEventListener('load', syncSettingsLink);
    setTimeout(syncSettingsLink, 1200);
    setTimeout(syncSettingsLink, 3000);
    /* global hook for other scripts / debugging */
    window.fsConsent = {
      get: function () { return readChoice(); },
      accept: function () { decide('accepted'); },
      decline: function () { decide('declined'); },
      reset: function () {
        try { localStorage.removeItem(STORE_KEY); } catch (e) {}
        document.cookie = 'consent=;path=/;max-age=0';
        showBanner();
      },
      gtmId: GTM_ID
    };
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
