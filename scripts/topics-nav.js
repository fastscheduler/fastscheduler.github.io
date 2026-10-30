/* Topics rail for the STATIC help article pages (help/a/*.html and
   ru/help/a/*.html).

   The hub (help/index.html) keeps its own left sidebar; the standalone
   article pages used to have none at all, so opening a search result dropped
   the reader into a page with no way sideways except the pager. This builds
   the same rail from window.__HELP_TOPICS (scripts/help-topics.js, titles
   only) and lists EVERY article of every category — the old hub rail cut each
   category at eight links, which made half the help center unreachable.

   Progressive: no data file (or a non-article page) means nothing happens. */
(function () {
  'use strict';

  var TOPICS = window.__HELP_TOPICS;
  if (!TOPICS || !TOPICS.length) return;
  if (document.getElementById('hcSideNav') || document.querySelector('.hc-side')) return; // hub
  if (!/\/help\/a\/[^\/]+\.html$/.test(location.pathname)) return;

  var file = location.pathname.split('/').pop().replace(/\.html$/, '');
  var isRu = document.documentElement.getAttribute('lang') === 'ru';
  var main = document.querySelector('main.legal') || document.querySelector('main');
  var host = main && (main.querySelector('.wrap, .hc-area') || null);
  if (!main || !host) return;

  var css = document.getElementById('fs-topics-css');
  if (!css) {
    css = document.createElement('style');
    css.id = 'fs-topics-css';
    css.textContent =
      /* Same container as the header/footer (--maxw, 20px gutters), so the
         rail starts under the logo instead of hanging outside the page. */
      '.hc-area{display:grid;grid-template-columns:240px minmax(0,1fr);gap:32px;' +
      'align-items:start;max-width:var(--maxw);margin:0 auto;padding:20px 20px 40px}' +
      '.hc-area>.hc-art-col{min-width:0}' +
      '.hc-area .wrap{max-width:none!important;margin:0!important;padding:0!important}' +
      '.hc-topics{position:sticky;top:78px;max-height:calc(100vh - 100px);overflow-y:auto;' +
      'padding:4px 6px 16px 0;font-size:.88rem;overscroll-behavior:contain}' +
      '.hc-topics-h{font-weight:800;font-size:.95rem;letter-spacing:-.01em;padding:0 8px 10px;color:var(--text)}' +
      '.hc-topics details{border-radius:10px}' +
      '.hc-topics summary{list-style:none;cursor:pointer;display:flex;align-items:center;gap:6px;' +
      'padding:8px;border-radius:8px;font-weight:700;color:var(--text-dim)}' +
      '.hc-topics summary::-webkit-details-marker{display:none}' +
      '.hc-topics summary:hover{color:var(--green-strong);background:color-mix(in srgb,var(--green) 8%,transparent)}' +
      '.hc-topics summary .n{margin-left:auto;font-size:.72rem;font-weight:700;opacity:.7}' +
      '.hc-topics ul{list-style:none;margin:2px 0 8px;padding:0 0 0 10px}' +
      '.hc-topics li a{display:block;padding:5px 8px;border-radius:7px;color:var(--text-dim);' +
      'line-height:1.4;text-decoration:none}' +
      '.hc-topics li a:hover{color:var(--green-strong);background:color-mix(in srgb,var(--green) 8%,transparent);text-decoration:none}' +
      '.hc-topics li a[aria-current="page"]{color:var(--green-strong);font-weight:700;' +
      'background:color-mix(in srgb,var(--green) 12%,transparent)}' +
      '.hc-topics-toggle{display:none}' +
      '@media (max-width:980px){.hc-area{grid-template-columns:minmax(0,1fr);gap:6px}' +
      '.hc-topics{position:static;max-height:none;order:-1;border:1px solid var(--border);' +
      'border-radius:12px;padding:6px 10px;margin-bottom:14px;background:var(--surface)}' +
      '.hc-topics-h{display:none}' +
      '.hc-topics-toggle{display:flex;align-items:center;gap:8px;width:100%;padding:10px 4px;' +
      'font:inherit;font-weight:750;color:var(--text);background:0 0;border:0;cursor:pointer}' +
      '.hc-topics-toggle svg{width:17px;height:17px;color:var(--green-strong)}' +
      '.hc-topics[data-open="0"] details{display:none}}';
    document.head.appendChild(css);
  }

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }

  var curCat = null;
  var open = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>';
  var chev = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>';

  var parts = ['<aside class="hc-topics" data-open="0" aria-label="' +
    (isRu ? 'Все темы' : 'All help topics') + '">',
    '<div class="hc-topics-h">' + (isRu ? 'Все темы' : 'All topics') + '</div>',
    '<button type="button" class="hc-topics-toggle" data-topics-toggle aria-expanded="false">' +
    open + '<span>' + (isRu ? 'Все темы' : 'Browse all topics') + '</span>' + chev + '</button>'];

  TOPICS.forEach(function (cat) {
    var rows = [];
    if (cat.id === file) curCat = cat.id;
    rows.push('<li><a href="' + esc(cat.id) + '.html"' +
      (cat.id === file ? ' aria-current="page"' : '') + '>' + esc(cat.title) + '</a></li>');
    (cat.kids || []).forEach(function (k) {
      if (k.id === file) curCat = cat.id;
      rows.push('<li><a href="' + esc(k.id) + '.html"' +
        (k.id === file ? ' aria-current="page"' : '') + '>' + esc(k.t) + '</a></li>');
    });
    if (!rows.length) return;
    parts.push('<details' + (cat.id === curCat ? ' open' : '') + '><summary>' + esc(cat.title) +
      '<span class="n">' + rows.length + '</span></summary><ul>' + rows.join('') + '</ul></details>');
  });
  parts.push('</aside>');

  var area = document.createElement('div');
  area.className = 'hc-area';
  var col = document.createElement('div');
  col.className = 'hc-art-col';

  // move the page's own wrapper into the article column, rail first
  main.insertBefore(area, host);
  area.innerHTML = parts.join('');
  area.appendChild(col);
  col.appendChild(host);

  var toggle = area.querySelector('[data-topics-toggle]');
  if (toggle) {
    toggle.addEventListener('click', function () {
      var box = toggle.parentElement, on = box.getAttribute('data-open') === '1';
      box.setAttribute('data-open', on ? '0' : '1');
      toggle.setAttribute('aria-expanded', on ? 'false' : 'true');
    });
  }
})();
