// Fast Schedule site logic: pricing switcher, plan deep links, cookies, tracking.
(function () {
  var cfg = (typeof SITE_CONFIG !== 'undefined' && SITE_CONFIG) ? SITE_CONFIG
    : { botUsername: 'FastestScheduleBot', prices: {} };
  var bot = 'https://t.me/' + cfg.botUsername;

  /* Site root, derived from this script's own src.
     The site is served from the domain root, but pages live at many depths,
     so a relative path only works at one of them. '../storage_state.json' resolved to /legal/
     storage_state.json on the legal pages and escaped the site entirely on the
     homepage, so the 60s feature-flag poll 404'd on every page that loads
     this file. Same trick lang.js uses to locate ru-content.js. */
  var SITE_ROOT = '';
  try {
    var self = document.querySelector('script[src*="main.js"]');
    if (self) {
      var src = self.getAttribute('src') || '';
      var i = src.indexOf('/scripts/main.js');
      if (i > -1) SITE_ROOT = src.slice(0, i);
    }
  } catch (e) {}

  /* ---------- Editable placeholders (legal docs) ---------- */
  function applyPlaceholders() {
    var ph = cfg.placeholders || {};
    document.querySelectorAll('[data-ph]').forEach(function (el) {
      var key = el.getAttribute('data-ph').trim().toUpperCase().replace(/[^A-Z0-9]+/g, '_');
      var v = ph[key];
      if (v !== undefined && v !== null && v !== '') el.textContent = v;
    });
  }

  /* ---------- Full plan comparison table on the homepage ---------- */
  function fillComparison() {
    var box = document.getElementById('comparison');
    if (!box) return;
    var rows = cfg.comparisonRows || [];
    if (rows.length) {
      /* headline limits first - these are what people actually compare */
      rows = [
        { label: 'Pending scheduled messages', free: '100', premium: 'Unlimited', freeIncluded: true, premiumIncluded: true },
        { label: 'Messages sent / month', free: '100 per channel', premium: 'Unlimited', freeIncluded: true, premiumIncluded: true }
      ].concat(rows);
      var esc = function (v) {
        return String(v).replace(/[&<>"]/g, function (c) {
          return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
        });
      };
      var html = '<table><thead><tr><th>Feature</th><th>Free</th><th>Premium</th></tr></thead><tbody>';
      rows.forEach(function (r) {
        if (r.storage && cfg.mediaStorageEnabled === false) return;
        var fv = esc(r.free), pv = esc(r.premium);
        if (!r.freeIncluded) fv = '<span class="mut">' + fv + '</span>';
        if (!r.premiumIncluded) pv = '<span class="mut">' + pv + '</span>';
        html += '<tr><td>' + esc(r.label) + '</td><td>' + fv + '</td><td>' + pv + '</td></tr>';
      });
      html += '</tbody></table>';
      box.innerHTML = html;
    } else if (cfg.comparisonHTML) {
      box.innerHTML = cfg.comparisonHTML;  /* fallback: pre-rendered table */
    }
  }

  /* ---------- Pricing switcher (default: yearly) ---------- */
  var sw = document.querySelector('.switch');
  function updatePrices(isYearly) {
    var p = cfg.prices;
    var set = function (sel, txt) {
      document.querySelectorAll(sel).forEach(function (el) { el.textContent = txt; });
    };
    set('[data-price="premium"]', isYearly ? p.yearlyUSD : p.monthlyUSD);
    set('[data-price="per"]', isYearly ? '/yr' : '/mo');
    set('[data-price="savings"]', p.savingsPercent);
    set('[data-price="premiumNote"]',
      isYearly ? ('Billed yearly · ~' + p.yearlyMonthlyEquivalentUSD + '/mo') : 'Billed monthly');
  }
  function fillFeatures() {
    var rows = (cfg.plans && cfg.plans.rows) || [];
    // Free plan: show allowed features first, then not-allowed.
    rows = rows.slice().sort(function (a, b) {
      return (b.freeIncluded ? 1 : 0) - (a.freeIncluded ? 1 : 0);
    });
    /* Static trusted icons only — config values never touch innerHTML. */
    var ICON_OK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 13l4 4L19 7"/></svg>';
    var ICON_NO = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 6l12 12M18 6L6 18"/></svg>';
    document.querySelectorAll('[data-features]').forEach(function (ul) {
      var kind = ul.getAttribute('data-features'); // 'free' | 'premium'
      ul.innerHTML = '';
      rows.forEach(function (r) {
        // Skip Media-Storage rows when the feature is disabled (live toggle).
        if (r.storage && !effectiveEnabled) return;
        var included = kind === 'premium' ? r.premiumIncluded : r.freeIncluded;
        var value = kind === 'premium' ? r.premium : r.free;
        var li = document.createElement('li');
        if (!included) li.className = 'no';
        var icon = document.createElement('span');
        icon.setAttribute('aria-hidden', 'true');
        icon.innerHTML = included ? ICON_OK : ICON_NO;
        li.appendChild(icon);
        var label = document.createElement('span');
        label.textContent = String(r.label);
        if (included && value !== 'Yes') {
          label.appendChild(document.createTextNode(' \u2014 '));
          var b = document.createElement('b');
          b.textContent = String(value);
          label.appendChild(b);
        }
        li.appendChild(label);
        ul.appendChild(li);
      });
    });
  }
  /* ---------- Hide features disabled in the bot (e.g. Media Storage) ----------
     effectiveEnabled starts from the build-time default and is overridden by the
     live storage_state.json the bot writes on every toggle. */
  var effectiveEnabled = !!(cfg.mediaStorageEnabled);
  function applyFeatureVisibility() {
    document.querySelectorAll('[data-feature="storage"]').forEach(function (el) {
      el.style.display = effectiveEnabled ? '' : 'none';
    });
  }
  function syncStorageState() {
    fillFeatures();
    applyFeatureVisibility();
  }

  if (sw) {
    var m = sw.querySelector('[data-plan="monthly"]');
    var y = sw.querySelector('[data-plan="yearly"]');
    function setPlan(plan) {
      var isYearly = plan === 'yearly';
      y.classList.toggle('active', isYearly);
      m.classList.toggle('active', !isYearly);
      document.body.classList.toggle('show-yearly', isYearly);
      updatePrices(isYearly);
    }
    m.addEventListener('click', function () { setPlan('monthly'); });
    y.addEventListener('click', function () { setPlan('yearly'); });
    setPlan('yearly'); // default
  }
  fillFeatures();
  fillComparison();
  applyPlaceholders();
  applyFeatureVisibility();

  /* ---------- Live storage state from the bot (written on every toggle) ---------- */
  function fetchStorageState() {
    fetch(SITE_ROOT + '/storage_state.json', { cache: 'no-store' })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (s) {
        if (s && typeof s.mediaStorageEnabled === 'boolean' && s.mediaStorageEnabled !== effectiveEnabled) {
          effectiveEnabled = s.mediaStorageEnabled;
          syncStorageState();
        }
      })
      .catch(function () { /* offline / file not present: keep build default */ });
  }
  fetchStorageState();
  // Re-check periodically so the site reflects a toggle without a reload.
  setInterval(fetchStorageState, 60000);

  /* ---------- Plan deep links (open bot with plan preselected) ---------- */
  document.querySelectorAll('[data-plan-link]').forEach(function (a) {
    var plan = a.getAttribute('data-plan-link');
    a.setAttribute('href', bot + '?start=premium_' + plan + '__pricing');
  });

  /* ---------- Tracked links (source recorded by the bot) ---------- */
  function track(source) {
    try {
      var arr = JSON.parse(localStorage.getItem('site_clicks') || '[]');
      arr.push({ ts: new Date().toISOString(), source: source });
      localStorage.setItem('site_clicks', JSON.stringify(arr.slice(-200)));
    } catch (e) {}
  }
  document.querySelectorAll('[data-track]').forEach(function (a) {
    var source = a.getAttribute('data-track');
    if (!a.getAttribute('href') || a.getAttribute('href') === '#') {
      a.setAttribute('href', bot + '?start=__' + source);
    }
    a.addEventListener('click', function () { track(source); });
  });

  /* ---------- Cookie consent banner ---------- */
  var banner = document.getElementById('cookieBanner');
  function closeBanner(choice) {
    try {
      localStorage.setItem('cookie_consent', choice);
      document.cookie = 'consent=' + choice + ';path=/;max-age=31536000;samesite=lax;secure';
    } catch (e) {}
    if (banner) banner.classList.remove('show');
  }
  if (banner) {
    var saved = null;
    try { saved = localStorage.getItem('cookie_consent'); } catch (e) {}
    if (!saved) {
      setTimeout(function () { banner.classList.add('show'); }, 600);
    }
    var accept = banner.querySelector('[data-cookie="accept"]');
    var decline = banner.querySelector('[data-cookie="decline"]');
    if (accept) accept.addEventListener('click', function () { closeBanner('accepted'); });
    if (decline) decline.addEventListener('click', function () { closeBanner('declined'); });
  }
})();
