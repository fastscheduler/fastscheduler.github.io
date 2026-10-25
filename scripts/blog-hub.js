
/* Blog search: Enter opens a help-style results view (no live filtering).
   Ranking via window.HelpAI (scripts/help-ai.js): typo tolerance, synonyms,
   intent matching — the same engine the help center uses. */
(function () {
  var q = document.getElementById('blog-q');
  if (!q) return;
  var bar = document.getElementById('blog-search-bar'),
      chips = [].slice.call(document.querySelectorAll('.blog-chip')),
      secs = [].slice.call(document.querySelectorAll('.blog-sec')),
      view = document.getElementById('blog-results'),
      feat = document.getElementById('blog-featured'),
      grid = document.getElementById('blog-res-grid'),
      meta = document.getElementById('blog-res-meta'),
      title = document.getElementById('blog-res-title'),
      filtersEl = document.getElementById('blog-res-filters'),
      backBtn = document.getElementById('blog-results-back');
  var CATS = {};
  chips.forEach(function (c) { CATS[c.getAttribute('data-cat')] = c.textContent.trim(); });
  var CAT_ORDER = ['all', 'growth', 'content', 'tools', 'premium', 'platform', 'money', 'releases', 'updates', 'company'];
  var kinds = [].slice.call(document.querySelectorAll('.blog-kindtab'));
  var hubState = { kind: 'all', cat: 'all' };
  var DOCS = [];
  try { DOCS = window.__BLOG_DOCS || []; } catch (e) {}
  DOCS.forEach(function (d) { d.intent = d.c; });
  var state = { q: '', cat: 'all' };
  function isRU() {
    try {
      if (document.documentElement.lang === 'ru') return true;
      return localStorage.getItem('fs-lang') === 'ru';
    } catch (e) { return document.documentElement.lang === 'ru'; }
  }
  var T = {
    results: function () { return isRU() ? 'Результаты поиска' : 'Search results'; },
    resMeta: function (n, raw) {
      if (isRU()) return n ? n + ' ' + pluralRU(n) + ' по запросу «' + raw + '»' : 'Ничего не найдено по запросу «' + raw + '»';
      return n ? n + ' result' + (n > 1 ? 's' : '') + ' for “' + raw + '”' : '0 results for “' + raw + '”';
    },
    noAll: function (raw) {
      return isRU() ? 'Статей по запросу «' + raw + '» нет. Попробуйте другой запрос — или выберите тему выше.'
        : 'No articles found for “' + raw + '”. Try a different search — or pick a topic above.';
    },
    noCat: function (cat, raw) {
      return isRU() ? 'В теме «' + cat + '» по запросу «' + raw + '» ничего нет — попробуйте другую тему.'
        : 'No ' + cat.toLowerCase() + ' articles match “' + raw + '” — try another topic.';
    },
    allTopics: function () { return isRU() ? 'Все темы' : 'All topics'; }
  };
  function pluralRU(n) {
    var m = n % 10, h = n % 100;
    if (m === 1 && h !== 11) return 'результат';
    if (m >= 2 && m <= 4 && (h < 12 || h > 14)) return 'результата';
    return 'результатов';
  }

  function esc(x) {
    return String(x == null ? '' : x).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function mark(raw, term) {
    if (!term) return esc(raw);
    var out = '', low = String(raw).toLowerCase(), i = 0, idx;
    while ((idx = low.indexOf(term, i)) !== -1) {
      out += esc(raw.slice(i, idx)) + '<mark>' + esc(raw.slice(idx, idx + term.length)) + '</mark>';
      i = idx + term.length;
    }
    return out + esc(raw.slice(i));
  }
  function snippet(text, term) {
    var low = String(text).toLowerCase(), i = low.indexOf(term);
    if (i === -1) return String(text).slice(0, 150) + '…';
    var startT = Math.max(0, i - 50);
    return (startT > 0 ? '…' : '') + text.slice(startT, startT + 160) + '…';
  }

  function runSearch() {
    var raw = q.value.trim();
    state.q = raw.toLowerCase();
    state.cat = 'all';
    if (!raw) { showHub(); return; }
    var hits;
    if (window.HelpAI) {
      var ranked = window.HelpAI.scoreAll(raw, DOCS).map(function (x) { return { doc: x.doc, s: x.score }; });
      var seen = {};
      ranked.forEach(function (r) { seen[r.doc.id] = true; });
      DOCS.forEach(function (d) {
        if (seen[d.id]) return;
        var low = (d.t + ' ' + d.d + ' ' + d.b + ' ' + d.f).toLowerCase();
        if (low.indexOf(state.q) !== -1) ranked.push({ doc: d, s: 10 });
      });
      ranked = ranked.filter(function (r) { return r.s > 0; })
        .sort(function (a, b) { return b.s - a.s; });
      /* relevance floor: one weak shared word ("post" is in nearly every
         article) must not pull the whole blog into the results */
      if (ranked.length) {
        var floor = Math.max(25, ranked[0].s * 0.5);
        ranked = ranked.filter(function (r) { return r.s >= floor; });
      }
      hits = ranked.map(function (r) { return r.doc; });
    } else {
      hits = DOCS.filter(function (d) {
        var low = (d.t + ' ' + d.d + ' ' + d.b + ' ' + d.f).toLowerCase();
        return state.q.split(/\s+/).every(function (w) { return low.indexOf(w) !== -1; });
      });
    }
    renderResults(hits, raw);
  }

  function renderResults(hits, raw) {
    secs.forEach(function (s) { s.style.display = 'none'; });
    if (feat) feat.style.display = 'none';
    chips.forEach(function (c) { c.classList.remove('on'); });
    chips.forEach(function (c) { c.style.display = 'none'; });
    view.hidden = false;
    window.scrollTo(0, 0);
    title.textContent = T.results();
    meta.textContent = T.resMeta(hits.length, raw);
    var counts = { all: hits.length };
    hits.forEach(function (h) { counts[h.c] = (counts[h.c] || 0) + 1; });
    var fhtml = '';
    CAT_ORDER.forEach(function (cid) {
      var n = counts[cid] || 0;
      var label = (cid === 'all' ? T.allTopics() : (CATS[cid] || cid));
      fhtml += '<button type="button" class="blog-fchip' + (cid === state.cat ? ' on' : '') +
        (n === 0 ? ' zero' : '') + '" data-fcat="' + cid + '">' + esc(label) +
        ' <span class="blog-fcount">' + n + '</span></button>';
    });
    filtersEl.innerHTML = fhtml;
    filtersEl.querySelectorAll('.blog-fchip').forEach(function (b) {
      b.addEventListener('click', function () {
        state.cat = b.getAttribute('data-fcat');
        filtersEl.querySelectorAll('.blog-fchip').forEach(function (x) {
          x.classList.toggle('on', x.getAttribute('data-fcat') === state.cat);
        });
        paintGrid(hits, raw);
      });
    });
    paintGrid(hits, raw);
    try { history.replaceState(null, '', '#q=' + encodeURIComponent(raw)); } catch (e) {}
    window.scrollTo(0, 0);
  }

  function paintGrid(hits, raw) {
    var shown = hits.filter(function (h) { return state.cat === 'all' || h.c === state.cat; });
    if (!hits.length) {
      grid.innerHTML = '<p class="blog-nores">' + esc(T.noAll(raw)) + '</p>';
      return;
    }
    if (!shown.length) {
      grid.innerHTML = '<p class="blog-nores">' + esc(T.noCat(CATS[state.cat] || '', raw)) + '</p>';
      return;
    }
    grid.innerHTML = shown.map(function (d) {
      return '<a class="bcard bcard-text" href="a/' + esc(d.id) + '.html">' +
        '<span class="bcard-body"><b>' + mark(d.t, state.q) + '</b>' +
        '<span class="bcard-desc">' + mark(snippet(d.d + ' ' + d.b, state.q), state.q) + '</span>' +
        '<span class="bcard-meta">' + esc(CATS[d.c] || '') + '</span></span></a>';
    }).join('');
  }

  function paintHub() {
    var filtered = hubState.kind !== 'all' || hubState.cat !== 'all';
    if (feat) feat.style.display = filtered ? 'none' : '';
    secs.forEach(function (s) {
      var okK = hubState.kind === 'all' || s.getAttribute('data-kind') === hubState.kind;
      var okC = hubState.cat === 'all' || s.getAttribute('data-cat') === hubState.cat;
      s.style.display = (okK && okC) ? '' : 'none';
    });
    chips.forEach(function (c) {
      var ck = c.getAttribute('data-kind') || 'all';
      c.style.display = (hubState.kind === 'all' || ck === 'all' || ck === hubState.kind) ? '' : 'none';
    });
  }

  function showHub() {
    view.hidden = true;
    if (feat) feat.style.display = '';
    bar.style.display = '';
    chips.forEach(function (c) { c.style.display = ''; });
    secs.forEach(function (s) { s.style.display = ''; });
    try { history.replaceState(null, '', location.pathname); } catch (e) {}
    window.scrollTo(0, 0);
  }

  /* kind tabs + topic chips filter the hub sections together */
  kinds.forEach(function (k) {
    k.addEventListener('click', function () {
      kinds.forEach(function (x) { x.classList.toggle('on', x === k); });
      hubState.kind = k.getAttribute('data-kind') || 'all';
      hubState.cat = 'all';
      chips.forEach(function (c) { c.classList.toggle('on', c.getAttribute('data-cat') === 'all'); });
      paintHub();
      try {
        var h = hubState.kind === 'all' ? location.pathname : '#kind=' + hubState.kind;
        history.replaceState(null, '', h);
      } catch (e) {}
    });
  });
  chips.forEach(function (ch) {
    ch.addEventListener('click', function () {
      chips.forEach(function (c) { c.classList.toggle('on', c === ch); });
      hubState.cat = ch.getAttribute('data-cat') || 'all';
      paintHub();
    });
  });

  /* Enter-only search; Esc or the breadcrumb returns to the hub */
  q.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') { e.preventDefault(); runSearch(); }
    if (e.key === 'Escape') { q.value = ''; showHub(); q.blur(); }
  });
  if (backBtn) backBtn.addEventListener('click', function (e) { e.preventDefault(); showHub(); });

  /* deep links: #q=<query> opens results; #cat=<id> pre-selects a chip */
  function applyHash() {
    var h = location.hash || '';
    if (h.indexOf('#q=') === 0) {
      var query = '';
      try { query = decodeURIComponent(h.slice(3)).replace(/\+/g, ' '); } catch (err) {}
      if (query) { q.value = query; runSearch(); return true; }
    }
    if (h.indexOf('#cat=') === 0) {
      var cid = h.slice(5);
      var chip = chips.filter(function (c) { return c.getAttribute('data-cat') === cid; })[0];
      if (chip) {
        var need = chip.getAttribute('data-kind') || 'all';
        var ktab = kinds.filter(function (k) { return k.getAttribute('data-kind') === need; })[0];
        if (ktab && need !== 'all') ktab.click();
        chip.click(); window.scrollTo(0, 0); return true;
      }
    }
    if (h.indexOf('#kind=') === 0) {
      var kd = h.slice(6);
      var kt = kinds.filter(function (k) { return k.getAttribute('data-kind') === kd; })[0];
      if (kt) { kt.click(); window.scrollTo(0, 0); return true; }
    }
    return false;
  }
  window.addEventListener('hashchange', function () { applyHash(); });
  if (!applyHash()) {
    /* a stray hash (or leftover #q= after navigating back) shouldn't leave a
       broken half-searched page: restore the plain hub view */
    q.value = '';
    showHub();
    chips.forEach(function (c) { c.classList.toggle('on', c.getAttribute('data-cat') === 'all'); });
  }
})();
