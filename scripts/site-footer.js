/* ==========================================================================
   Fast Scheduler — shared site footer.
   Injects the brand footer on every page (one source of truth). Replaces the
   legacy <footer class="site"> / <footer class="home-foot"> if present, and
   appends one before </body> otherwise. Assets are resolved relative to this
   script's own URL, so it works at any page depth. Follows the EN/RU language
   chosen in Settings (fs-lang) and re-renders when it changes.
   ========================================================================== */
(function () {
  'use strict';

  var script = document.currentScript;
  if (!script) {
    var tags = document.getElementsByTagName('script');
    for (var i = tags.length - 1; i >= 0; i--) {
      if (/site-footer\.js(\?|$)/.test(tags[i].src)) { script = tags[i]; break; }
    }
  }

  var BASE = '';
  try {
    if (script && script.src) BASE = script.src.replace(/scripts\/site-footer\.js.*$/, '');
  } catch (e) {}

  var STYLE_ID = 'fs-foot-css';
  var STYLE_HREF = BASE + 'styles/footer.css?v=20261019a5';

  var BOT_URL = 'https://t.me/FastSchedulerBot?start=start__website';
  var SUPPORT_URL = 'https://t.me/FastSchedulerSupport_bot';
  var EMAIL = 'mailto:fastschedulebot@gmail.com';

  var L = {
    en: {
      wordmark: 'Fast Scheduler',
      tagline: 'Schedule your Telegram channel posts once \u2014 they publish themselves, on time, in your timezone.',
      copy: '\u00a9 2026 Fast Scheduler \u00b7 Made for Telegram channels',
      cols: [
        { h: 'Product', links: [
          ['Features', 'index.html#features'],
          ['How it works', 'index.html#how'],
          ['Pricing', 'index.html#pricing'],
          ['Scheduling', 'help/c/scheduling/'],
          ['Batch scheduling', 'help/a/qa_schedule_many_at_once/'],
          ['Sender Bots', 'help/c/bots/'],
          ['Media Storage', 'help/c/media_storage/']
        ] },
        { h: 'Resources', links: [
          ['Help Center', 'help.html'],
          ['Getting Started', 'help/c/start/'],
          ['Blog', 'blog/index.html'],
          ['Premium', 'help/c/premium/'],
          ['Referrals', 'help/c/referral/'],
          ['FAQ', 'index.html#faq']
        ] },
        { h: 'Support', links: [
          ['Open Bot', BOT_URL, 1],
          ['Support chat', SUPPORT_URL, 1],
          ['Feedback', 'help/c/feedback/'],
          ['Contact', 'help/c/contact/'],
          ['Email us', EMAIL, 1]
        ] },
        { h: 'Legal', links: [
          ['Privacy', 'legal/privacy/'],
          ['Terms', 'legal/terms/'],
          ['Refunds', 'legal/refund-policy/'],
          ['Data Deletion', 'help/a/privacy_delete/']
        ] }
      ]
    },
    ru: {
      wordmark: 'Fast Scheduler',
      tagline: '\u041f\u043b\u0430\u043d\u0438\u0440\u0443\u0439\u0442\u0435 \u043f\u043e\u0441\u0442\u044b \u0432 Telegram-\u043a\u0430\u043d\u0430\u043b\u0435 \u043e\u0434\u0438\u043d \u0440\u0430\u0437 \u2014 \u0434\u0430\u043b\u044c\u0448\u0435 \u043e\u043d\u0438 \u043f\u0443\u0431\u043b\u0438\u043a\u0443\u044e\u0442\u0441\u044f \u0441\u0430\u043c\u0438, \u0432\u043e\u0432\u0440\u0435\u043c\u044f \u0438 \u0432 \u0432\u0430\u0448\u0435\u043c \u0447\u0430\u0441\u043e\u0432\u043e\u043c \u043f\u043e\u044f\u0441\u0435.',
      copy: '\u00a9 2026 Fast Scheduler \u00b7 \u0421\u0434\u0435\u043b\u0430\u043d\u043e \u0434\u043b\u044f Telegram-\u043a\u0430\u043d\u0430\u043b\u043e\u0432',
      cols: [
        { h: '\u041f\u0440\u043e\u0434\u0443\u043a\u0442', links: [
          ['\u0412\u043e\u0437\u043c\u043e\u0436\u043d\u043e\u0441\u0442\u0438', 'index.html#features'],
          ['\u041a\u0430\u043a \u044d\u0442\u043e \u0440\u0430\u0431\u043e\u0442\u0430\u0435\u0442', 'index.html#how'],
          ['\u0422\u0430\u0440\u0438\u0444\u044b', 'index.html#pricing'],
          ['\u041f\u043b\u0430\u043d\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435', 'help/c/scheduling/'],
          ['\u041f\u0430\u043a\u0435\u0442\u043d\u043e\u0435 \u043f\u043b\u0430\u043d\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435', 'help/a/qa_schedule_many_at_once/'],
          ['\u0411\u043e\u0442\u044b-\u043e\u0442\u043f\u0440\u0430\u0432\u0438\u0442\u0435\u043b\u0438', 'help/c/bots/'],
          ['\u041c\u0435\u0434\u0438\u0430\u0442\u0435\u043a\u0430', 'help/c/media_storage/']
        ] },
        { h: '\u0420\u0435\u0441\u0443\u0440\u0441\u044b', links: [
          ['\u0426\u0435\u043d\u0442\u0440 \u043f\u043e\u043c\u043e\u0449\u0438', 'help.html'],
          ['\u041d\u0430\u0447\u0430\u043b\u043e \u0440\u0430\u0431\u043e\u0442\u044b', 'help/c/start/'],
          ['\u0411\u043b\u043e\u0433', 'blog/index.html'],
          ['\u041f\u0440\u0435\u043c\u0438\u0443\u043c', 'help/c/premium/'],
          ['\u0420\u0435\u0444\u0435\u0440\u0430\u043b\u044b', 'help/c/referral/'],
          ['\u0412\u043e\u043f\u0440\u043e\u0441\u044b \u0438 \u043e\u0442\u0432\u0435\u0442\u044b', 'index.html#faq']
        ] },
        { h: '\u041f\u043e\u0434\u0434\u0435\u0440\u0436\u043a\u0430', links: [
          ['\u041e\u0442\u043a\u0440\u044b\u0442\u044c \u0431\u043e\u0442\u0430', BOT_URL, 1],
          ['\u0427\u0430\u0442 \u043f\u043e\u0434\u0434\u0435\u0440\u0436\u043a\u0438', SUPPORT_URL, 1],
          ['\u041e\u0431\u0440\u0430\u0442\u043d\u0430\u044f \u0441\u0432\u044f\u0437\u044c', 'help/c/feedback/'],
          ['\u041a\u043e\u043d\u0442\u0430\u043a\u0442\u044b', 'help/c/contact/'],
          ['\u041d\u0430\u043f\u0438\u0441\u0430\u0442\u044c \u043d\u0430\u043c', EMAIL, 1]
        ] },
        { h: '\u041f\u0440\u0430\u0432\u043e\u0432\u0430\u044f \u0438\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0438\u044f', links: [
          ['\u041a\u043e\u043d\u0444\u0438\u0434\u0435\u043d\u0446\u0438\u0430\u043b\u044c\u043d\u043e\u0441\u0442\u044c', 'legal/privacy/'],
          ['\u0423\u0441\u043b\u043e\u0432\u0438\u044f', 'legal/terms/'],
          ['\u0412\u043e\u0437\u0432\u0440\u0430\u0442\u044b', 'legal/refund-policy/'],
          ['\u0423\u0434\u0430\u043b\u0435\u043d\u0438\u0435 \u0434\u0430\u043d\u043d\u044b\u0445', 'help/a/privacy_delete/']
        ] }
      ]
    }
  };

  function esc(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function currentLang() {
    try {
      var saved = localStorage.getItem('fs-lang');
      if (saved === 'ru' || saved === 'en') return saved;
    } catch (e) {}
    return (document.documentElement.getAttribute('lang') === 'ru') ? 'ru' : 'en';
  }

  function hrefFor(href) {
    return /^(https?:|mailto:|tel:|\/)/.test(href) ? href : BASE + href;
  }

  function li(item) {
    var at = item[2] ? ' target="_blank" rel="noopener noreferrer"' : '';
    return '<li><a href="' + esc(hrefFor(item[1])) + '"' + at + '>' + esc(item[0]) + '</a></li>';
  }

  function column(c) {
    return '<div class="fs-foot-col"><h3>' + esc(c.h) + '</h3><ul>' +
      c.links.map(li).join('') + '</ul></div>';
  }

  function html(t) {
    var words = String(t.wordmark).split(' ');
    var line1 = words[0];
    var line2 = words.slice(1).join(' ') || line1;
    var stack = '<tspan x="720" y="140">' + esc(line1) + '</tspan>' +
      '<tspan x="720" y="312">' + esc(line2) + '</tspan>';
    return '<footer class="fs-foot" role="contentinfo">' +
      '<div class="wrap fs-foot-main">' +
        '<div class="fs-foot-brand">' +
          '<a class="fs-foot-logo" href="' + esc(BASE + 'index.html') + '" aria-label="' + esc(t.wordmark) + '">' +
            '<img src="' + esc(BASE + 'brand-logo.png') + '" alt="' + esc(t.wordmark) + '" width="56" height="56" loading="lazy" decoding="async">' +
          '</a>' +
          '<p class="fs-foot-tag">' + esc(t.tagline) + '</p>' +
        '</div>' +
        '<div class="fs-foot-cols">' + t.cols.map(column).join('') + '</div>' +
      '</div>' +
      '<div class="fs-foot-mark" aria-hidden="true">' +
        '<svg class="fs-foot-word" viewBox="0 0 1440 172" preserveAspectRatio="xMidYMid meet" focusable="false" aria-hidden="true">' +
          '<defs>' +
            '<linearGradient id="fsWordGrad" x1="0" y1="0" x2="1" y2="1">' +
              '<stop offset="0" stop-color="#eafff6" stop-opacity="0.07"/>' +
              '<stop offset="0.42" stop-color="#ffffff" stop-opacity="0.18"/>' +
              '<stop offset="0.58" stop-color="#8ff2c6" stop-opacity="0.28"/>' +
              '<stop offset="1" stop-color="#eafff6" stop-opacity="0.07"/>' +
              '<animateTransform attributeName="gradientTransform" type="rotate" from="0 0.5 0.5" to="360 0.5 0.5" dur="30s" repeatCount="indefinite"/>' +
            '</linearGradient>' +
            '<filter id="fsWordBlur" x="-10%" y="-40%" width="120%" height="180%">' +
              '<feGaussianBlur stdDeviation="5"/>' +
            '</filter>' +
          '</defs>' +
          '<g class="fs-word-wide">' +
            '<text class="fs-foot-word-text" x="720" y="140" text-anchor="middle" fill="#7ef0bf" fill-opacity="0.16" filter="url(#fsWordBlur)">' + esc(t.wordmark) + '</text>' +
            '<text class="fs-foot-word-text" x="720" y="140" text-anchor="middle" fill="url(#fsWordGrad)" stroke="rgba(255,255,255,0.05)" stroke-width="1">' + esc(t.wordmark) + '</text>' +
          '</g>' +
          '<g class="fs-word-stack">' +
            '<text class="fs-foot-word-text" text-anchor="middle" fill="#7ef0bf" fill-opacity="0.16" filter="url(#fsWordBlur)">' + stack + '</text>' +
            '<text class="fs-foot-word-text" text-anchor="middle" fill="url(#fsWordGrad)" stroke="rgba(255,255,255,0.05)" stroke-width="1">' + stack + '</text>' +
          '</g>' +
        '</svg>' +
      '</div>' +
      '<div class="wrap fs-foot-base"><span>' + esc(t.copy) + '</span></div>' +
    '</footer>';
  }

  function ensureCSS() {
    if (document.getElementById(STYLE_ID)) return;
    var link = document.createElement('link');
    link.id = STYLE_ID;
    link.rel = 'stylesheet';
    link.href = STYLE_HREF;
    (document.head || document.documentElement).appendChild(link);
  }

  // Scale the wordmark so it always spans the footer width exactly, regardless
  // of which font actually renders, then grow the SVG viewBox vertically to
  // contain the glyphs. Scaling by width alone used to push the tops of the
  // letters above y=0, where the SVG clipped them.
  var WORD_W = 1440;
  var WORD_H = 172;
  var WORD_BASE_Y = 140;
  var WORD_PAD_X = 14;
  var WORD_PAD_Y = 10;

  function narrowWord() {
    try {
      if (window.matchMedia) return window.matchMedia('(max-width: 540px)').matches;
    } catch (e) {}
    return (window.innerWidth || 0) <= 540;
  }

  function setWordLines(text, gap, shift) {
    var lines = text.querySelectorAll('tspan');
    var i;
    if (!lines.length) {
      text.setAttribute('y', (WORD_BASE_Y + shift).toFixed(2));
      return;
    }
    for (i = 0; i < lines.length; i++) {
      lines[i].setAttribute('x', WORD_W / 2);
      lines[i].setAttribute('y', (WORD_BASE_Y + shift + i * gap).toFixed(2));
    }
  }

  function fitWord(root) {
    var svg = root.querySelector('.fs-foot-word');
    if (!svg || !svg.setAttribute) return;
    var wide = root.querySelector('.fs-word-wide');
    var stack = root.querySelector('.fs-word-stack');
    var narrow = narrowWord();
    if (wide) wide.style.display = narrow ? 'none' : 'inline';
    if (stack) stack.style.display = narrow ? 'inline' : 'none';
    var group = narrow ? stack : wide;
    if (!group) return;
    var texts = group.querySelectorAll('.fs-foot-word-text');
    if (!texts.length) return;

    svg.setAttribute('viewBox', '0 0 ' + WORD_W + ' ' + WORD_H);
    var i;
    var gap = WORD_H * 0.98;
    for (i = 0; i < texts.length; i++) {
      texts[i].style.fontSize = WORD_H + 'px';
      setWordLines(texts[i], gap, 0);
    }

    var probe = texts[0].getBBox ? texts[0].getBBox() : null;
    if (!probe || !probe.width) return;

    var target = WORD_W - WORD_PAD_X * 2;
    var size = WORD_H * target / probe.width;
    gap = size * 0.98;
    for (i = 0; i < texts.length; i++) {
      texts[i].style.fontSize = size.toFixed(2) + 'px';
      setWordLines(texts[i], gap, 0);
    }

    var box = texts[0].getBBox ? texts[0].getBBox() : probe;
    var height = Math.max(WORD_H, Math.ceil(box.height + WORD_PAD_Y * 2));
    var shift = WORD_PAD_Y - box.y;
    for (i = 0; i < texts.length; i++) setWordLines(texts[i], gap, shift);
    svg.setAttribute('viewBox', '0 0 ' + WORD_W + ' ' + height);
  }

  function whenFontsReady(fn) {
    try {
      if (document.fonts && document.fonts.ready) {
        document.fonts.load('700 100px "Space Grotesk"').catch(function () {});
        document.fonts.ready.then(fn).catch(fn);
        return;
      }
    } catch (e) {}
    fn();
  }

  function render() {
    var t = L[currentLang()] || L.en;
    ensureCSS();
    var node = new DOMParser().parseFromString(html(t), 'text/html').body.firstChild;
    var old = document.querySelector('footer.fs-foot, footer.site, footer.home-foot');
    if (old && old.parentNode) {
      // The legacy footer usually lives inside .wrap, which made the green
      // background stop at the content column and look cut off on both sides.
      // Move the new footer beside the outermost wrapper so it spans the page.
      var top = old;
      while (top.parentNode && top.parentNode !== document.body) top = top.parentNode;
      if (top.parentNode === document.body) {
        top.parentNode.insertBefore(node, top.nextSibling);
      } else if (document.body) {
        document.body.appendChild(node);
      }
      if (old.parentNode) old.parentNode.removeChild(old);
    } else if (document.body) document.body.appendChild(node);
    fitWord(node);
    whenFontsReady(function () { fitWord(node); });
  }

  render();

  var wordResizeTimer;
  window.addEventListener('resize', function () {
    clearTimeout(wordResizeTimer);
    wordResizeTimer = setTimeout(function () {
      var foot = document.querySelector('footer.fs-foot');
      if (foot) fitWord(foot);
    }, 140);
  });

  window.addEventListener('fs-lang-change', render);
  window.addEventListener('fs-lang-applied', render);
})();
