/* ==================================================================
   Fast Scheduler — hero cinema player
   A scripted, After-Effects-style motion graphic that reproduces the
   real bot flow end to end:
     dashboard → schedule → photo mode → file explorer (mouse) →
     drag & drop into Telegram → uploading animation → review →
     scheduled → send time → roulette picks a random photo →
     calendar reminder → iOS home + magnifier clock → channel post →
     bot confirmation → zoom out → finale with big CTA.
   ================================================================== */
(function () {
  var chat      = document.getElementById('tgChat');
  var stream    = document.getElementById('tgStream');
  var typing    = document.getElementById('tgTyping');
  var explorer  = document.getElementById('tgExplorer');
  var fxList    = document.getElementById('fxList');
  var fxCursor  = document.getElementById('fxCursor');
  var dropGlow  = document.getElementById('dropGlow');
  var rlStage   = document.getElementById('rlStage');
  var iosLayer  = document.getElementById('iosLayer');
  var chanLayer = document.getElementById('chanLayer');
  var botLayer  = document.getElementById('botLayer');
  var screenEl  = document.querySelector('#phone3d .phone-screen');
  var phone     = document.getElementById('phone3d');
  var stageEl   = phone ? phone.parentElement : null;
  var heroSec   = document.getElementById('heroSec');
  if (!chat || !stream || !explorer || !fxList || !fxCursor || !screenEl || !phone) return;

  var reduce = (window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches) ||
               document.documentElement.getAttribute('data-motion') === 'off';

  /* Frame loop. A native requestAnimationFrame is paused in background tabs and
     never fires at all in some embedded webviews, which used to freeze the drag,
     roulette and calendar scenes half-way through. Fall back to a timer so the
     timeline always finishes; once one real frame arrives we use the native call
     directly again. */
  var raf = (function () {
    var native = window.requestAnimationFrame && window.requestAnimationFrame.bind(window);
    if (!native) return function (cb) { return setTimeout(function () { cb(performance.now()); }, 16); };
    var strikes = 0, hits = 0, degraded = false, proven = false;
    return function (cb) {
      if (degraded) return setTimeout(function () { cb(performance.now()); }, 16);
      if (proven) return native(cb);            /* normal browser: zero overhead */
      var settled = false;
      var id = native(function (t) {
        if (settled) return;
        settled = true;
        strikes = 0;
        if (++hits >= 3) proven = true;
        cb(t);
      });
      setTimeout(function () {
        if (settled) return;
        settled = true;
        hits = 0;
        strikes++;
        if (strikes >= 2) degraded = true;      /* two misses in a row: stop trusting it */
        cb(performance.now());
      }, 150);
      return id;
    };
  })();

  var SCHEDULED_POSTS = [
    { time: '18:15', text: 'schedule multiple messages at once' },
    { time: '18:16', text: 'see everything in calendar' },
    { time: '18:17', text: 'use stats for advanced statistics' }
  ];

  var PHOTOS = [
    { name: 'image.jpg',  size: '435.6 KB', css: 'linear-gradient(135deg,#e8c66a,#b5762a)' },
    { name: 'image1.jpg', size: '1.0 MB',   css: 'linear-gradient(135deg,#a58757,#5c4630)' },
    { name: 'image3.jpg', size: '916.7 KB', css: 'linear-gradient(135deg,#5d7a52,#2c3f26)' },
    { name: 'image4.jpg', size: '807.9 KB', css: 'linear-gradient(135deg,#d9a557,#8a5a26)' }
  ];

  /* hand-drawn SVG artwork so every photo looks like a real image.
     NOTE: single quotes around the data-URI — these strings are spliced
     into HTML attributes delimited by double quotes. */
  /* Landscape composition on purpose: these photos are mostly shown in wide,
     short frames, and a square drawing cropped to the middle band is a flat
     rectangle of background colour — which is exactly what made the channel
     posts look like empty placeholders. Sun and horizon sit in the band that
     survives that crop. */
  function art(bg, f1, f2) {
    var svg = "<svg xmlns='http://www.w3.org/2000/svg' width='180' height='120'>" +
      "<rect width='180' height='120' fill='" + bg + "'/>" +
      "<rect y='54' width='180' height='66' fill='" + f2 + "' opacity='.3'/>" +
      "<circle cx='135' cy='40' r='15' fill='" + f2 + "' opacity='.92'/>" +
      "<path d='M0 76 Q36 52 72 74 T180 66 V120 H0 Z' fill='" + f1 + "' opacity='.85'/>" +
      "<path d='M0 94 Q44 74 82 92 T180 86 V120 H0 Z' fill='" + f1 + "'/></svg>";
    return "url('data:image/svg+xml," + encodeURIComponent(svg).replace(/'/g, '%27') + "')";
  }
  PHOTOS[0].img = art('#f2c94c', '#7a9d3f', '#e8862e');
  PHOTOS[1].img = art('#8a6a4a', '#5d442e', '#d9b06a');
  PHOTOS[2].img = art('#4e6b46', '#2e4028', '#93b564');
  PHOTOS[3].img = art('#d99a4e', '#8a5a26', '#f2c94c');
  /* Layered photo background: the gradient sits UNDER the artwork, so a
     cell/thumb/media block never renders as an empty box even if its
     data-URI fails to paint in some webview. */
  function bg(p) { return p.img + ', ' + p.css; }

  /* ---------- real user time / date ----------
     Everything on the phone uses the visitor's actual clock and calendar,
     so the demo always tells a true, local story. */
  var NOW = new Date();
  function pad(n) { return (n < 10 ? '0' : '') + n; }
  function hhmm(d) { return pad(d.getHours()) + ':' + pad(d.getMinutes()); }
  function plusMin(base, min) { return new Date(base.getTime() + min * 60000); }
  /* the three demo posts go out at +8, +9 and +10 minutes from "now" */
  var SEND_TIMES = [plusMin(NOW, 8), plusMin(NOW, 9), plusMin(NOW, 10)];
  SCHEDULED_POSTS.forEach(function (p, i) { p.time = hhmm(SEND_TIMES[i]); });
  /* full numeric date the user types: DD.MM.YYYY HH:MM */
  function stamp(d) { return pad(d.getDate()) + '.' + pad(d.getMonth() + 1) + '.' + d.getFullYear() + ' ' + hhmm(d); }
  var BATCH_TEXT = stamp(SEND_TIMES[0]) + '\nschedule multiple messages at once\n\n' +
    stamp(SEND_TIMES[1]) + '\nsee everything in calendar\n\n' +
    stamp(SEND_TIMES[2]) + '\nuse stats for advanced statistics';
  /* chat message timestamps: the story advances a minute or so per phase,
     all anchored on the visitor's real clock */
  function fmt12(d) { var h = d.getHours(), ap = h >= 12 ? 'PM' : 'AM'; h = h % 12 || 12; return h + ':' + pad(d.getMinutes()) + ' ' + ap; }
  function storyTime(min) { return fmt12(new Date(NOW.getTime() + min * 60000)); }
  /* recompute every derived time — called at the start of each play() so
     replays never show stale times */
  function refreshNow() {
    NOW = new Date();
    SEND_TIMES = [plusMin(NOW, 8), plusMin(NOW, 9), plusMin(NOW, 10)];
    SCHEDULED_POSTS.forEach(function (p, i) { p.time = hhmm(SEND_TIMES[i]); });
    BATCH_TEXT = stamp(SEND_TIMES[0]) + '\nschedule multiple messages at once\n\n' +
      stamp(SEND_TIMES[1]) + '\nsee everything in calendar\n\n' +
      stamp(SEND_TIMES[2]) + '\nuse stats for advanced statistics';
  }
  /* countdown from the current time to the first send */
  function countdown() {
    var ms = SEND_TIMES[0] - new Date();
    if (ms < 0) ms = 0;
    var h = Math.floor(ms / 3600000), m = Math.floor((ms % 3600000) / 60000);
    return 'fires in ' + (h ? h + ' h ' : '') + m + ' min — even while you sleep';
  }
  var WEEKDAYS = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
  var MONTHS = ['January','February','March','April','May','June','July','August','September','October','November','December'];
  var TODAY_NUM = NOW.getDate();

  /* ---------- helpers ---------- */
  function el(html) {
    var t = document.createElement('template');
    t.innerHTML = html.trim();
    return t.content.firstElementChild;
  }
  function esc(s) { return s.replace(/&/g, '&amp;').replace(/</g, '&lt;'); }
  function meta(t) { return '<span class="meta">' + t + '</span>'; }
  /* Inline keyboards live INSIDE the bot's own bubble — that is what Telegram's
     inline_keyboard is, and what this bot actually sends. Each kb() call is one
     row of buttons and returns its markup, so the rows land at the bottom of
     the bubble they belong to, spanning it edge to edge. There is no docked
     reply keyboard anywhere in the demo. */
  function kb(rows, accIdx, extraCls) {
    var h = '<span class="ikb">';
    rows.forEach(function (r, i) {
      h += '<span class="ikb-btn ' + (extraCls || '') + (i === accIdx ? ' ikb-acc' : '') + '">' + r + '</span>';
    });
    return h + '</span>';
  }
  /* Find the inline button a tap lands on, so the cursor clicks the button
     instead of the middle of the bubble. Matches on the label with punctuation
     and digits ignored, so '✅ Done (4)' finds '✅ Done (0)'. */
  function inlineKey(m, label) {
    if (!m) return null;
    label = (label || '').trim().toLowerCase();
    if (!label) return null;
    var keys = m.querySelectorAll('.ikb-btn');
    for (var i = 0; i < keys.length; i++) {
      var k = (keys[i].textContent || '').trim().toLowerCase();
      if (!k) continue;
      if (k === label) return keys[i];
      var a = k.replace(/[^a-z\u00c0-\u024f]+/g, '');
      var b = label.replace(/[^a-z\u00c0-\u024f]+/g, '');
      if (a && b && (a.indexOf(b) === 0 || b.indexOf(a) === 0)) return keys[i];
    }
    return null;
  }
  /* Pacing must be identical whether or not motion is reduced — collapsing
     these delays makes every scene after the roulette invisible. Reduced
     motion only removes smooth *transitions* (handled in CSS), never scenes. */
  /* Scenes chain onto each other with sleep(): the calendar hands off to the
     lock screen, the lock screen to the channel. A chain that is still in
     flight when the player resets (a replay, or a QA jump) would otherwise
     land in the middle of the NEW scene and put the wrong screen back on the
     phone, so every sleep checks the generation it was started in. */
  var runGen = 0;
  function sleep(ms) {
    var g = runGen;
    return new Promise(function (r) {
      setTimeout(function () { if (g === runGen) r(); }, ms);
    });
  }
  /* ---------- Telegram delivery ticks (clock -> tick -> double tick -> read) ---------- */
  var TICK_SVG =
    '<svg class="tk-clock" viewBox="0 0 12 12" aria-hidden="true"><circle cx="6" cy="6" r="4.7" fill="none" stroke="currentColor" stroke-width="1.2"/><path d="M6 3.5v2.8l1.9 1.1" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>' +
    '<svg class="tk-one" viewBox="0 0 14 10" aria-hidden="true"><path d="M1.4 5.3l3.2 3.2L12.4 1.3" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>' +
    '<svg class="tk-two" viewBox="0 0 18 10" aria-hidden="true"><path d="M1.1 5.3l3.1 3.2L11.5 1.3" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/><path d="M6.5 5.3l3.1 3.2L16.9 1.3" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  function tickTo(t, state) {
    if (!t) return;
    t.setAttribute('data-s', state);
    t.classList.remove('advance');
    void t.offsetWidth;                              /* restart the pop */
    t.classList.add('advance');
  }
  function addTicks(m) {
    var t = document.createElement('span');
    t.className = 'tg-ticks';
    t.setAttribute('data-s', 'clock');
    t.setAttribute('aria-hidden', 'true');
    t.innerHTML = TICK_SVG;
    m.appendChild(t);
    later(function () { tickTo(t, 'one'); }, 1100);
    later(function () { tickTo(t, 'two'); }, 2200);
    later(function () { t.classList.add('read'); }, 3600);
    return t;
  }

  /* ---------- header preset: show what the bot is doing, like the app ---------- */
  var headerUser = document.querySelector('.tg-user');
  var BOT_PRESET = headerUser ? headerUser.textContent : '@fastschedulebot';
  function setHeaderState(txt) {
    if (!headerUser) return;
    headerUser.textContent = txt || BOT_PRESET;
    headerUser.classList.toggle('state', !!txt);
  }

  function botMsg(html) {
    var m = el('<div class="msg bot">' + html + '</div>');
    /* Telegram draws the text bubble and the inline keyboard as separate
       blocks: the text lives in .bubble (which owns the tail), the .ikb
       rows stay direct children so they render as detached buttons below. */
    var b = document.createElement('div');
    b.className = 'bubble';
    var n = m.firstChild;
    while (n) {
      var nx = n.nextSibling;
      if (n.nodeType === 1 && n.classList.contains('ikb')) break;
      b.appendChild(n);
      n = nx;
    }
    m.insertBefore(b, m.firstChild);
    stream.appendChild(m);
    return m;
  }
  function userMsg(html) {
    var m = el('<div class="msg user">' + html + '</div>');
    /* outgoing bubbles carry their send time left of the ticks, like the app */
    m.insertAdjacentHTML('beforeend', meta(fmt12(new Date())));
    stream.appendChild(m);
    addTicks(m);                       /* every outgoing message carries a status */
    return m;
  }
  /* the client pins a date badge above the day's messages */
  function dateBadge() {
    stream.insertAdjacentHTML('beforeend',
      '<div class="tg-date">' + MONTHS[NOW.getMonth()] + ' ' + NOW.getDate() + '</div>');
  }
  function show(m) { m.classList.add('shown'); scrollEnd(); }
  /* Jump straight to the newest message. rAF is throttled to a stop in some
     embedded views and in background tabs, so set it synchronously too —
     otherwise every new message lands below the fold and the screen looks
     empty while the timeline is actually running. */
  function scrollEnd() {
    chat.scrollTop = chat.scrollHeight;
    raf(function () { chat.scrollTop = chat.scrollHeight; });
    /* mobile Safari/Chrome sometimes lands a beat late (layout settles after
       the scroll), leaving the last message clipped below the fold: clamp
       again on the next frames */
    raf(function () { chat.scrollTop = chat.scrollHeight; });
    /* and once more after the 450ms reveal transition — the bubble's height
       is final only then, so the previous clamps could still leave the tail
       of the last message (the "delivered right on time" line) below the
       compose bar while the chat itself believes it is scrolled to the end */
    setTimeout(function () { chat.scrollTop = chat.scrollHeight; }, 500);
  }
  function showTyping(ms) {
    typing.classList.add('on');
    setHeaderState('typing…');
    scrollEnd();
    return sleep(ms || 850).then(function () {
      typing.classList.remove('on');
      setHeaderState(null);
    });
  }
  function botSay(html, typingMs) {
    return showTyping(typingMs || 900).then(function () {
      show(botMsg(html));
      return sleep(550);
    });
  }
  function bubbleCenter(m) {
    return localPoint(m, .5, .5);
  }
  /* the user sends a message: the bubble is revealed FIRST (so the cursor aims
     at something visible), then the cursor glides to the bubble and presses it */
  function tapMsg(m) {
    return new Promise(function (done) {
      show(m);                                  /* visible before aiming */
      var c = bubbleCenter(m);
      fxCursor.classList.add('on');
      glideCursor(c.x, c.y, 480).then(function () {
        clickFx(c.x, c.y);
        m.classList.add('pressed');
        setTimeout(function () {
          m.classList.remove('pressed');
          done();
        }, 200);
        later(function () { fxCursor.classList.remove('on'); }, 900);
      });
    });
  }
  /* the user taps an INLINE button inside one of the bot's bubbles. Telegram
     answers an inline tap with a callback query, so no outgoing message is
     created — the button just presses in and the bot replies. */
  function tapInline(m, label) {
    return new Promise(function (done) {
      var target = inlineKey(m, label);
      if (!target || !m.parentNode) { done(); return; }
      var c = localPoint(target, .5, .5);
      fxCursor.classList.add('on');
      glideCursor(c.x, c.y, 480).then(function () {
        clickFx(c.x, c.y);
        target.classList.add('pressed');
        setTimeout(function () { target.classList.remove('pressed'); done(); }, 260);
        later(function () { fxCursor.classList.remove('on'); }, 900);
      });
    });
  }
  function glide(from, to, dur) {
    return new Promise(function (done) {
      if (reduce) { from(to, 1); done(); return; }
      var t0 = performance.now();
      (function tick(now) {
        var k = Math.min(1, (now - t0) / dur);
        var e = k < .5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2;   /* easeInOutQuad */
        from({ x: from.x0 + (to.x - from.x0) * e, y: from.y0 + (to.y - from.y0) * e }, k);
        if (k < 1) raf(tick); else done();
      })(t0);
    });
  }
  /* continuous cursor glide between any two points inside the screen */
  function moveCursorTo(x, y, dur) {
    return glide({
      x0: cursorPos().x, y0: cursorPos().y,
      __cur: null,
      // eslint-disable-next-line
      valueOf: function () { return 0; }
    }, { x: x, y: y }, dur).then(function () {});
  }
  function cursorPos() {
    var st = getComputedStyle(fxCursor);
    var tr = st.transform && st.transform !== 'none' ? new DOMMatrix(st.transform) : new DOMMatrix();
    return { x: tr.m41, y: tr.m42 };
  }
  /* glide using per-frame callback (avoids the awkward wrapper above) */
  function glideCursor(x, y, dur) {
    return new Promise(function (done) {
      var from = cursorPos();
      if (reduce) { fxCursor.style.transform = 'translate(' + x + 'px,' + y + 'px)'; done(); return; }
      var t0 = performance.now();
      (function tick(now) {
        var k = Math.min(1, (now - t0) / dur);
        var e = k < .5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2;
        fxCursor.style.transform = 'translate(' + (from.x + (x - from.x) * e) + 'px,' + (from.y + (y - from.y) * e) + 'px)';
        if (k < 1) raf(tick); else done();
      })(t0);
    });
  }
  function clickFx(x, y) {
    var c = el('<span class="fx-click on"></span>');
    c.style.left = x + 'px'; c.style.top = y + 'px';
    screenEl.appendChild(c);
    setTimeout(function () { c.remove(); }, 500);
  }
  function setCursorAt(x, y) { fxCursor.style.transform = 'translate(' + x + 'px,' + y + 'px)'; }
  /* Park the cursor where resetAll() puts it BEFORE the first glide. Without
     this its transform is empty, so it sits at the screen's 0,0 origin and the
     first tap makes a white pointer flash at the phone's top-left corner and
     slide in from there. */
  setCursorAt(320, 300);
  /* TRUE local (untransformed) coordinates inside screenEl. The phone stands
     in a 3D pose, so getBoundingClientRect deltas are wrong — offsetLeft /
     offsetTop walk gives the real layout position. Scroll of intermediate
     containers (the chat) is subtracted so we aim at the VISIBLE spot. */
  function localPoint(el, fx, fy) {
    var x = el.offsetLeft + el.offsetWidth * (fx == null ? .5 : fx);
    var y = el.offsetTop + el.offsetHeight * (fy == null ? .5 : fy);
    var p = el.offsetParent;
    while (p && p !== screenEl) { x += p.offsetLeft; y += p.offsetTop; p = p.offsetParent; }
    var q = el.parentElement;
    while (q && q !== screenEl) {
      x -= q.scrollLeft || 0;
      y -= q.scrollTop || 0;
      q = q.parentElement;
    }
    return { x: x, y: y };
  }
  function itemCenter(item) { return localPoint(item, .62, .6); }

  /* ---------- explorer ---------- */
  function buildExplorer() {
    fxList.innerHTML = '';
    PHOTOS.forEach(function (p, i) {
      fxList.appendChild(el(
        '<div class="fx-item" data-i="' + i + '">' +
          '<span class="fx-ic" style="background-image:' + bg(p) + '"></span>' +
          '<span class="fx-info"><span class="fx-nm">' + esc(p.name) + '</span>' +
          '<span class="fx-sz">' + p.size + '</span></span>' +
        '</div>'));
    });
  }
  function explorerOn(on) { explorer.classList.toggle('on', on); }

  /* ---------- full flow ---------- */
  var started = false;
  var timers = [];
  function later(fn, ms) { timers.push(setTimeout(fn, ms)); }
  function clearTimers() { timers.forEach(clearTimeout); timers = []; }

  /* Replay pill: ONE persistent handler, bound at boot. It used to be
     attached inside the finale beat, so any run that skipped that beat (an
     interrupted demo, a jump, a second finale) left a visible button that
     did nothing when clicked. Bound here, it always works — even while the
     finished demo is still on screen, because resetAll() clears `started`
     BEFORE play() runs. */
  (function bindReplay() {
    var rp = document.querySelector('.hero-copy .hero-replay');
    if (!rp) return;
    rp.addEventListener('click', function () {
      rp.hidden = true;
      resetAll();
      play();
    });
  })();

  function play() {
    if (started) return;
    started = true;
    refreshNow();
    var T = 0;
    function at(dt, fn) { T += dt; later(fn, T); }
    /* bubbles whose inline buttons the cursor taps later in the story */
    var photoMsg = null, doneMsg = null, reviewMsg = null;

    buildExplorer();
    /* the phone's chrome runs on the visitor's real clock and date */
    dateBadge();
    var tgTime = document.querySelector('.tg-time');
    if (tgTime) tgTime.textContent = hhmm(new Date());

    /* every scene below is a closure over this run — hand them to the QA hook
       so one of them can be opened on demand instead of waiting it out */
    if (window.FS_DEMO) window.FS_DEMO.scenes = { calendar: calendarScene, ios: iosScene,
      channel: channelScene, confirm: botConfirmScene, finale: finale };

    /* 1 — user opens the bot */
    at(600, function () { tapMsg(userMsg('📅 Schedule a Message')); });

    /* 2 — bot: main dashboard (exact real text) */
    at(500, function () {
      showTyping(950).then(function () {
        show(botMsg('🤖 <b>Dashboard</b>' + meta(storyTime(0)) +
          kb(['🗓 Schedule a Message', '🔁 Recurring Messages'], 0) +
          kb(['📣 @fastschedule_test3', '📋 My Messages']) +
          kb(['💾 Media Storage']) +
          kb(['➡️ Next'], -1, 'kb-red')));
      });
    });

    /* 3 — bot: Schedule a Message info sheet. The user only STARTS typing
       once the sheet is fully on screen and readable — the old build began
       typing at 3400ms while the sheet was still "typing…", so the format
       help seemed to appear only after the text was written. */
    at(2900, function () {
      showTyping(1050).then(function () {
        show(botMsg('📝 <b>Schedule a Message</b><br>Send me your message with the date and time.<br><br>' +
          '<b>Format:</b><span class="mono">DD.MM.YYYY HH:MM\nYour message</span>' +
          '<b>Features:</b><span class="mono">• Add photos, videos, or documents\n• Create polls and quizzes (anonymous only)\n• Add inline buttons\n• Use formatting (bold, italic, links, etc.)</span>'));
        /* a beat so the visitor actually reads the format, then type */
        later(function () {
          typeInField(BATCH_TEXT).then(function () {
            var m = userMsg('<span class="mono">' + BATCH_TEXT.replace(/\n/g, '<br>') + '</span>');
            show(m);
            tapMsg(m);
          });
        }, 900);
      });
    });

    /* 5 — bot: Select Photo Mode (real expanded text) */
    at(3600, function () {
      showTyping(1100).then(function () {
        photoMsg = botMsg('📷 <b>Select Photo Mode</b><br>Choose how your photos will be attached to scheduled posts:<br><br>' +
          '📷 <b>Normal</b><br>Each post gets the exact same photo. Perfect for branding — use your logo, watermark, or a consistent visual identity across all messages.<br><br>' +
          '🎲 <b>Random</b><br>Each post gets a random photo from the set you upload. Great for variety — keeps your channel visually fresh without repeating the same image.<br><br>' +
          '🔀 <b>Sequential</b><br>Photos are sent in order, one per post. Ideal for story-like content, step-by-step tutorials, or any sequence where order matters.<br><br>' +
          '⏭ <b>Skip Photos</b>' + meta(storyTime(1)) +
          kb(['🎲 Random', '📷 Normal']) + kb(['🔀 Sequential', '⏭ Skip Photos']) +
          kb(['❌ Cancel'], -1, 'kb-red'));
        show(photoMsg);
      });
    });

    /* 6 — the user taps Random: an inline button in the message above, which
       sends a callback query — no outgoing bubble is created */
    at(3000, function () { tapInline(photoMsg, '🎲 Random'); });

    /* 7 — bot asks for photos, then the whole upload flow runs as one
       promise chain so no timed message can race the mouse animation */
    at(1700, function () {
      showTyping(800).then(function () {
        doneMsg = botMsg('📷 <b>Send photos or click Done:</b>' + meta(storyTime(2)) +
          kb(['✅ Done (0)'], -1, 'kb-green') + kb(['❌ Cancel'], -1, 'kb-red'));
        show(doneMsg);
        startExplorerFlow();
      });
    });

    function startExplorerFlow() {
      explorerScene()
        .then(function () { return uploadingScene(); })
        .then(function () { return sleep(600); })
        .then(function () { doneMsg.querySelector('.ikb-btn').textContent = '✅ Done (4)'; return tapInline(doneMsg, '✅ Done (4)'); })
        .then(function () { return botSay('📷 <b>4 photo(s) received.</b>' + meta(storyTime(3)) + kb(['➕ Add More Media']) + kb(['❌ Cancel'], -1, 'kb-red')); })
        .then(function () { return sleep(1000); })
        .then(function () { return botSay('📝 <b>Review</b><br><br>Channels: @fastschedule_test3<br>Time: ' + SCHEDULED_POSTS.map(function (p, i) {
          var d = SEND_TIMES[i];
          var hrs = d.getHours(), ampm = hrs >= 12 ? 'PM' : 'AM';
          var h12 = hrs % 12 || 12;
          return p.text + '<br>' + pad(d.getDate()) + '.' + pad(d.getMonth() + 1) + '.' + d.getFullYear() + ' ' + h12 + ':' + pad(d.getMinutes()) + ' ' + ampm;
        }).join('<br>') + '<br><br>❓ Do you want to change anything?' + meta(storyTime(4)) +
          kb(['✍️ Signature', '✏️ Edit']) +
          kb(['✅ Schedule'], -1, 'kb-green') + kb(['❌ Cancel'], -1, 'kb-red'), 1100); })
        .then(function () { reviewMsg = stream.lastElementChild; return sleep(1000); })
        .then(function () { return tapInline(reviewMsg, '✅ Schedule'); })
        .then(function () { return botSay('✅ <b>3 message(s) scheduled.</b><span class="mono">' + SCHEDULED_POSTS.map(function (p, i) {
          return '📅 s33455' + i + '_' + i + ': ' + p.text + '\n' + stamp(SEND_TIMES[i]).split(' ')[0] + ' — ' + SEND_TIMES[i].getFullYear() + '-' + pad(SEND_TIMES[i].getMonth() + 1) + '-' + pad(SEND_TIMES[i].getDate()) + ' ' + hhmm(SEND_TIMES[i]) + ':00';
        }).join('\n\n') + '</span>' + meta(storyTime(5)) +
          kb(['📤 Schedule a few more']) + kb(['⬅️ Back'])); })
        /* no reactions here: nobody reacts to a bot's own status message, and
           a Telegram bot message never gathers them by itself */
        .then(function () { return sleep(2000); })
        .then(function () { cinemaRoulette(); });
    }

    /* 8 — file explorer opens on the side; the mouse selects everything */
    function explorerScene() {
      return new Promise(function (done) {
        explorerOn(true);
        setCursorAt(320, 300);
        later(function () { fxCursor.classList.add('on'); }, 350);
        later(function () {
          selectAll().then(function () { return dragStack(); }).then(done);
        }, 900);
      });
    }

    /* the visitor's typed text appears in the message input field letter
       by letter, then the cursor taps send — resolves when fully sent */
    function typeInField(text) {
      return new Promise(function (done) {
        var field = document.querySelector('.tg-input-ph');
        if (!field) { done(); return; }
        var input = field.parentElement;
        input.classList.add('composing');
        var i = 0;
        (function step() {
          if (i >= text.length) {
            /* pause, then tap the send plane. The field only clears AFTER the
               tap lands: removing .composing first hides .tg-send (display:none),
               and the cursor used to glide to a zero-size, invisible target —
               which read as "never clicks the send button". */
            setTimeout(function () {
              var plane = document.querySelector('.tg-input .tg-send');
              if (!plane) { field.textContent = 'Message'; input.classList.remove('composing'); done(); return; }
              var c = localPoint(plane, .5, .5);
              fxCursor.classList.add('on');
              glideCursor(c.x, c.y, 420).then(function () {
                clickFx(c.x, c.y);
                plane.classList.add('sent');
                field.textContent = 'Message';
                input.classList.remove('composing');
                setTimeout(function () { plane.classList.remove('sent'); fxCursor.classList.remove('on'); done(); }, 450);
              });
            }, 500);
            return;
          }
          field.textContent = text.slice(0, ++i);
          setTimeout(step, 22);
        })();
      });
    }

    function selectAll() {
      var items = explorer.querySelectorAll('.fx-item');
      var seq = Promise.resolve();
      items.forEach(function (item, i) {
        seq = seq.then(function () {
          var c = itemCenter(item);
          return glideCursor(c.x, c.y, 700).then(function () {
            clickFx(c.x, c.y);
            item.classList.add('selected');
            return sleep(320);
          });
        });
      });
      return seq;
    }

    /* 9 — press-and-hold, then DRAG the whole stack into the chat */
    function pressAndDrag() {
      var stack = explorer.querySelector('.fx-item[data-i="0"]');
      var c = itemCenter(stack);
      return glideCursor(c.x, c.y, 480).then(function () {
        clickFx(c.x, c.y);
        fxCursor.classList.add('holding');
        explorer.classList.add('dragging');
        explorer.querySelectorAll('.fx-item').forEach(function (it) { it.classList.add('lifted'); });
        return sleep(420);
      });
    }

    function dragStack() {
      return pressAndDrag().then(function () {
      return new Promise(function (dragDone) {
      dropGlow.classList.add('on');
      var drag = el('<span class="fx-drag" style="background-image:' + bg(PHOTOS[0]) + '"></span>');
      var g1 = el('<span class="fx-ghost" style="background-image:' + bg(PHOTOS[1]) + '"></span>');
      var g2 = el('<span class="fx-ghost" style="background-image:' + bg(PHOTOS[2]) + '"></span>');
      screenEl.appendChild(g2); screenEl.appendChild(g1); screenEl.appendChild(drag);

      var sr = null; /* all coordinates are now true local space */
      var startX = itemCenter(explorer.querySelector('.fx-item[data-i="0"]')).x;
      var startY = itemCenter(explorer.querySelector('.fx-item[data-i="0"]')).y;
      var drop = localPoint(chat, .5, .72);
      var endX = drop.x;
      var endY = drop.y;

      var t0 = performance.now(), dur = reduce ? 80 : 4200;   /* slow, cinematic drag */
      (function tick(now) {
        var k = Math.min(1, (now - t0) / dur);
        var e = k < .5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2;
        var lift = Math.sin(k * Math.PI) * 44;          /* visible arc */
        var grow = 1 + .22 * Math.sin(k * Math.PI);      /* grows while hovering */
        var x = startX + (endX - startX) * e;
        var y = startY + (endY - startY) * e - lift;
        drag.style.transform = 'translate(' + (x - 27) + 'px,' + (y - 27) + 'px) rotate(' + (k * 6 - 3) + 'deg) scale(' + grow.toFixed(3) + ')';
        g1.style.transform = 'translate(' + (x - 27 - 26 * (1 - e)) + 'px,' + (y - 27 - 22 * (1 - e)) + 'px) scale(' + (grow * .85).toFixed(3) + ')';
        g2.style.transform = 'translate(' + (x - 27 - 50 * (1 - e)) + 'px,' + (y - 27 - 42 * (1 - e)) + 'px) scale(' + (grow * .7).toFixed(3) + ')';
        setCursorAt(x + 8, y + 10);
        if (k < 1) raf(tick); else {
          drag.remove(); g1.remove(); g2.remove();
          fxCursor.classList.remove('holding');
          clickFx(endX, endY);
          /* hover beat so the drop is actually SEEN, then everything
             "pastes" into Telegram at once (a long beat — the old 1150ms
             read as a hiccup between the drop and the upload) */
          later(function () {
            dropGlow.classList.remove('on');
            explorer.classList.remove('dragging');
            clickFx(endX, endY);
            explorerOn(false);
            fxCursor.classList.remove('on');
            dragDone();
          }, 1500);
        }
      })(t0);
      });
      });
    }

    /* 10 — Telegram uploading animation, then the real album message */
    function uploadingScene() {
      return new Promise(function (upDone) {
      var bar = el('<span class="upl-bar">' + PHOTOS.map(function (p) {
        return '<span class="upl-cell" style="background-image:' + bg(p) + '">' +
          '<span class="upl-fill"></span><span class="upl-ring"><i></i></span><span class="upl-pct">0%</span></span>';
      }).join('') + '</span>');
      var m = userMsg('');
      m.appendChild(bar);
      show(m);
      var cells = bar.querySelectorAll('.upl-cell');
      var t0 = performance.now(), dur = reduce ? 60 : 1900;
      (function tick(now) {
        var k = Math.min(1, (now - t0) / dur);
        cells.forEach(function (cell, i) {
          var p = Math.min(1, Math.max(0, k * 1.25 - i * 0.08));
          cell.querySelector('.upl-fill').style.height = (p * 72) + '%';
          cell.querySelector('.upl-pct').textContent = Math.round(p * 100) + '%';
          if (p >= 1) cell.classList.add('done');
        });
        if (k < 1) raf(tick); else {
          sleep(420).then(function () {
            /* swap the uploading bar for the real Telegram album. The bar and
               the strip are the SAME 2-column grid with the same cell size, and
               by now every cell is in its .done state (rings/percent faded), so
               a plain swap is pixel-identical: the photos never leave the
               screen. (The old build swapped in thumbs at opacity 0, so the
               album visibly disappeared and popped back in.) */
            var album = el('<span class="upl-strip">' + PHOTOS.map(function (p) {
              return '<span class="upl-thumb" style="background-image:' + bg(p) + '"></span>';
            }).join('') + '</span>');
            bar.replaceWith(album);
            scrollEnd();
            var thumbs = album.querySelectorAll('.upl-thumb');
            thumbs.forEach(function (th, i) {
              later(function () { th.classList.add('landing'); }, i * 160);
            });
            later(function () { upDone(); }, 3 * 160 + 900);
          });
        }
      })(t0);
      });
    }

    /* steps 11–15 now live inside the startExplorerFlow() chain above */

    function cinemaRoulette() {
      var pick = PHOTOS[Math.floor(Math.random() * PHOTOS.length)];
      document.documentElement.classList.add('demo-cinema');
      phone.classList.add('glare-still');                 /* no light sweep mid-film */
      if (stageEl) stageEl.classList.add('cinema');
      /* hard clear of any finale leftovers: the old "fast scheduler" letters
         used to survive in the overlay and paint straight over the roulette
         scene when a replay re-entered cinema mode */
      rlStage.classList.remove('finale', 'written', 'hero-back');
      rlStage.innerHTML = '';
      if (heroSec) heroSec.classList.remove('hero-back');
      var cineEl0 = document.getElementById('heroCine');
      if (cineEl0) cineEl0.classList.remove('done', 'cine-on');
      var brandEl0 = document.getElementById('cineBrand');
      if (brandEl0) brandEl0.innerHTML = '';   /* no stale letters in the DOM */
      /* glide the phone to the exact CENTER of the hero: measure the real
         offset instead of guessing it in CSS */
      var heroRect = heroSec ? heroSec.getBoundingClientRect() : null;
      var stageRect = stageEl ? stageEl.getBoundingClientRect() : null;
      if (heroRect && stageRect) {
        var dx = Math.round((heroRect.left + heroRect.width / 2) - (stageRect.left + stageRect.width / 2));
        phone.style.setProperty('--cinema-dx', dx + 'px');
      }
      phone.classList.add('cinema');
      phone.classList.remove('idle');
      if (heroSec) heroSec.classList.add('cinema');
      sleep(750).then(function () {
        rlStage.classList.add('on', 'cinema');
        rlStage.innerHTML = '';

        /* the scheduled text message on stage */
        var card = el('<div class="rl-card rl-msg-in"><div class="rl-cap">schedule multiple messages at once' +
          '<span class="cp-time">' + SCHEDULED_POSTS[0].time + ' · @fastschedule_test3</span></div></div>');
        rlStage.appendChild(card);

        /* four photo placeholders above the message */
        var holder = el('<div class="rl-holder"></div>');
        rlStage.appendChild(holder);
        var tiles = PHOTOS.map(function (p, i) {
          var t = el('<span class="rl-tile" style="background-image:' + bg(p) + ';left:' + (34 + i * 64) + 'px"></span>');
          holder.appendChild(t); return t;
        });
        var q = el('<div class="rl-question">🎲 media mode: random — the bot picks one photo for this post</div>');
        rlStage.appendChild(q);
        sleep(900).then(function () {
          /* russian-roulette spin: land on a different tile each run */
          var order = [0, 1, 2, 3].sort(function () { return Math.random() - .5; });
          var steps = 14 + order.indexOf(PHOTOS.indexOf(pick));
          var cur = 0, delay = 90;
          (function spin() {
            tiles.forEach(function (t, i) { t.classList.toggle('focused', i === cur); });
            if (delay < 60 || Math.random() < .12) delay += 26;   /* decelerate */
            cur = (cur + 1) % 4;
            if (--steps > 0) { setTimeout(spin, delay); return; }
            /* winner = a random photo, may differ from last run */
            var win = Math.floor(Math.random() * 4);
            tiles.forEach(function (t, i) {
              t.classList.toggle('winner', i === win);
              t.classList.toggle('dim', i !== win);
            });
            tiles[win].classList.add('focused');
            attachWinner(win);
          })();
        });

        function attachWinner(w) {
          sleep(650).then(function () {
            /* the winning tile lifts off, arcs over and glides into the
               message card, landing with a soft bounce + glow burst */
            var from = localPoint(tiles[w]);
            var big = el('<span class="rl-fly" style="background-image:' + bg(PHOTOS[w]) + '"></span>');
            big.style.left = from.x + 'px';
            big.style.top = from.y + 'px';
            rlStage.appendChild(big);
            /* insert the target image but reveal it only at the MOMENT of
               touchdown: visible from the start, it duplicated the flyer and
               re-flowed the card mid-flight, so the landing looked "strange" */
            var img = el('<span class="rl-img" style="background-image:' + bg(PHOTOS[w]) + ';visibility:hidden"></span>');
            card.insertBefore(img, card.firstChild);
            /* measure from the flyer's TOP-LEFT (what left/top actually
               position), not its centre — scaling about the centre while
               targeting a top-left delta used to make the flyer land offset
               up-left of the real image, then snap */
            var to = { x: img.offsetLeft, y: img.offsetTop };
            var dx = to.x - from.x;
            var dy = to.y - from.y;
            var s0 = 74 / img.offsetWidth;      /* flyer is 74px, target is not */
            var dur = reduce ? 80 : 1050;
            var t0 = performance.now();
            (function fly(now) {
              var k = Math.min(1, (now - t0) / dur);
              var e = k < .5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2;  /* easeInOutCubic */
              var lift = Math.sin(k * Math.PI) * -58;                            /* arc over the card */
              var rot = (1 - k) * 10 - 5;                                        /* settles to straight */
              var sc = 1 + (1 - s0) * e;
              var squash = k > .82 ? 1 + Math.sin((k - .82) / .18 * Math.PI) * .06 * (1 - (k - .82) / .18) : 1;
              big.style.transform = 'translate(' + (dx * e) + 'px,' + (dy * e + lift) + 'px) rotate(' + rot.toFixed(2) + 'deg) scale(' + (sc * squash).toFixed(3) + ')';
              if (k < 1) { raf(fly); return; }
              /* touchdown: the flyer BECOMES the photo — same position, same
                 size — then the real image fades in and the flyer fades out,
                 so there is never a frame where the post has no photo, and
                 never a frame with two copies */
              img.style.visibility = '';
              img.classList.add('settled');
              img.style.opacity = '0';
              img.style.transition = 'opacity .28s ease';
              raf(function () { img.style.opacity = '1'; });
              setTimeout(function () {
                img.style.transition = ''; big.remove();
                card.classList.add('landed');
                var burst = el('<span class="rl-burst"></span>');
                burst.style.left = (to.x + img.offsetWidth / 2) + 'px';
                burst.style.top = (to.y + img.offsetHeight / 2) + 'px';
                rlStage.appendChild(burst);
                setTimeout(function () { burst.remove(); card.classList.remove('landed'); }, 900);
              }, 300);
            })(t0);

            var badge = el('<span class="rl-attach on">🎲 random pick · attached</span>');
            card.appendChild(badge);
            sleep(1500).then(function () { calendarScene(w); });
          });
        }
      });
    }

    /* 16 — calendar reminder motion graphic */
    function calendarScene(w) {
      sleep(500).then(function () {
        rlStage.querySelectorAll('.rl-card,.rl-holder,.rl-question').forEach(function (n) { n.remove(); });
        /* the month view the calendar app on the phone actually draws:
           Sunday-first single-letter weekday row, one disc for today, dots
           for the days that still have posts queued, one event row below */
        var cal = el('<div class="rl-cal">' +
          '<div class="cal-head"><span class="cal-when"><small>' + NOW.getFullYear() + '</small>' +
          '<b>' + MONTHS[NOW.getMonth()] + '</b></span><span class="cal-today">Today</span></div>' +
          '<div class="cal-grid"><b>S</b><b>M</b><b>T</b><b>W</b><b>T</b><b>F</b><b>S</b>' +
          (function () {
            var out = '';
            var dim = new Date(NOW.getFullYear(), NOW.getMonth() + 1, 0).getDate();
            var lead = new Date(NOW.getFullYear(), NOW.getMonth(), 1).getDay();   /* Sunday-first, like the app */
            var queued = [TODAY_NUM + 1, TODAY_NUM + 2];
            for (var b = 0; b < lead; b++) out += '<span class="cal-blank"></span>';
            for (var i = 1; i <= dim; i++) {
              var cls = 'cal-cell';
              if (i === TODAY_NUM) cls += ' today';
              else if (queued.indexOf(i) > -1) cls += ' ev';
              out += '<span class="' + cls + '" style="--i:' + (i - 1) + '">' + i + '</span>';
            }
            return out;
          })() +
          '</div><div class="cal-ev"><div class="cal-row">' +
          '<span class="cal-ic"><i>' + MONTHS[NOW.getMonth()].slice(0, 3).toUpperCase() + '</i><b>' + TODAY_NUM + '</b></span>' +
          '<span class="cal-txt"><b>Channel post — @fastschedule_test3</b><small>Reminder set · ' + SCHEDULED_POSTS[0].text + '</small></span>' +
          '<span class="cal-badge" id="calBadge">' + SCHEDULED_POSTS[0].time + '</span></div></div></div>');
        rlStage.appendChild(cal);
        var count = el('<div class="rl-count" id="rlCount">' + countdown() + '</div>');
        rlStage.appendChild(count);
        raf(function () { raf(function () { cal.classList.add('on'); }); });
        sleep(700).then(function () {
          var b = cal.querySelector('.cal-badge');
          if (b) b.classList.add('on');
          count.classList.add('on');
        });
        sleep(4200).then(function () { iosScene(w); });
      });
    }

    /* 17 — iOS lock screen: the magnifier GLIDES across the screen and grows
       over the clock, the clock winds up to the first send time with a tick
       pulse per minute, the Telegram notification slides down — and then the
       user TAPS it and Telegram zooms open out of the banner. */
    function iosScene(w) {
      rlStage.classList.remove('on');
      iosLayer.classList.add('on');
      var clock = document.getElementById('iosClock');
      var status = document.getElementById('iosStatusTime');
      var dateEl = document.querySelector('.ios-date');
      var target = SCHEDULED_POSTS[0].time;
      var startTime = hhmm(NOW);
      if (dateEl) dateEl.textContent = WEEKDAYS[NOW.getDay()] + ', ' + MONTHS[NOW.getMonth()] + ' ' + TODAY_NUM;
      clock.textContent = startTime;
      status.textContent = startTime;
      sleep(700).then(function () {
        /* slide-in is a real JS animation now: the lens glides from the
           bottom-right corner up onto the digits, while the digits grow
           beneath it. .grow only finalises the landing, .hunt runs the trip. */
        var spot = document.querySelector('.ios-spot');
        spot.classList.add('hunt');
        later(function () { spot.classList.remove('hunt'); spot.classList.add('grow'); }, reduce ? 60 : 900);
        /* wind from the current time to the send time — one visible tick
           per simulated minute; each change pulses the digits so the time
           visibly "ticks" instead of text-swapping */
        var from = NOW.getHours() * 60 + NOW.getMinutes();
          var tparts = target.split(':');
          var to = (+tparts[0]) * 60 + (+tparts[1]);
          if (to <= from) to += 24 * 60;
          var steps = Math.max(1, to - from);   /* 1 step = 1 minute */
          var stepMs = reduce ? 120 : Math.min(500, Math.floor(5600 / steps));
          var tick = 0;
          for (var i = 1; i <= steps; i++) {
            (function (i) {
              later(function () {
                var mins = Math.round(from + (to - from) * (i / steps)) % (24 * 60);
                var f = pad(Math.floor(mins / 60) % 24) + ':' + pad(mins % 60);
                clock.textContent = f; status.textContent = f;
                /* pulse the big clock on every tick (skip the very first) */
                if (i > 1) {
                  clock.classList.remove('tick');
                  void clock.offsetWidth;
                  clock.classList.add('tick');
                  tick++;
                  if (tick === 1) clock.addEventListener('animationend', function h() { clock.classList.remove('tick'); clock.removeEventListener('animationend', h); });
                }
              }, i * stepMs);
            })(i);
          }
      });
      var notifAt = reduce ? 2200 : 3600;
      sleep(notifAt).then(function () {
        document.getElementById('iosNotif').classList.add('on');   /* Telegram banner slides down */
      });
      /* the user taps the banner, then Telegram opens FROM it */
      sleep(notifAt + 2100).then(function () {
        var notif = document.getElementById('iosNotif');
        var c = localPoint(notif, .5, .5);
        fxCursor.classList.add('on');
        glideCursor(c.x, c.y, 520).then(function () {
          clickFx(c.x, c.y);
          notif.classList.add('press');
          later(function () { notif.classList.remove('press'); }, 260);
          /* Telegram launches out of the notification: the whole iOS layer
             zooms toward the banner, then the channel takes over */
          later(function () {
            fxCursor.classList.remove('on');
            iosLayer.classList.add('launch');
            later(function () { channelScene(w); }, 620);
          }, 480);
        });
      });
      /* hard safety: even if the tap animation is interrupted, the scene goes on */
      sleep(notifAt + 5200).then(function () { if (!iosLayer.classList.contains('launch')) channelScene(w); });
    }

    /* ---------- channel helpers ---------- */
    /* A view counter that ticks up. A count that lands complete in the same
       frame as its post is the giveaway that a human typed it into the HTML. */
    function countUp(node, target) {
      if (!node) return;
      var t0 = 0, dur = 1400;
      node.textContent = '0';
      raf(function step(now) {
        if (!t0) t0 = now;
        var p = Math.min(1, (now - t0) / dur);
        node.textContent = String(Math.round(target * (1 - Math.pow(1 - p, 3))));
        if (p < 1) raf(step);
      });
      /* rAF can be throttled to a stop in embedded views — land the real
         number anyway, a fraction of a second later */
      setTimeout(function () { node.textContent = String(target); }, dur + 150);
    }

    /* ---------- channel reaction gathering ----------
       A real channel post does not land with its reactions — they arrive
       over the next minute. Each pill pops in with a spring, its count
       ticks up, and the star pill collects the paid ⭐ reactions. */
    function gatherReacts(msg, spec) {
      if (!msg) return;
      var pills = [].slice.call(msg.querySelectorAll('.cp-reacts .rx'));
      spec.forEach(function (s, i) {
        if (!pills[i]) return;
        later(function () {
          var pill = pills[i];
          pill.classList.add('on');
          var count = pill.querySelector('b');
          if (!count) return;
          var done = 0, target = s.n;
          (function step() {
            done = Math.min(target, done + Math.max(1, Math.round(target / 7)));
            count.textContent = String(done);
            if (done < target) later(step, 120 + Math.random() * 160);
          })();
          later(function () { pill.classList.remove('bump'); }, 520);
        }, s.at);
      });
    }

    /* 18 — the channel: all 3 scheduled posts go out at their own time,
       while the phone's clock ticks forward (18:15 → 18:17). Every counter,
       reaction and reveal is reset FIRST — a double-run used to re-add .on to
       already-visible posts (they replayed their pop-in), zero the view
       counters mid-scene and double-stage every reaction. */
    function channelScene(w) {
      iosLayer.classList.remove('on', 'launch');
      chanLayer.classList.add('on');
      /* Telegram date badge: the real current date, like the client pins it */
      var dateBadgeEl = document.getElementById('chanDate');
      if (dateBadgeEl) dateBadgeEl.textContent = MONTHS[NOW.getMonth()] + ' ' + NOW.getDate();
      var msg = document.getElementById('chanMsg');
      var img = document.getElementById('chanImg');
      var m2 = document.querySelector('.chan-msg2');
      var m3 = document.querySelector('.chan-msg3');
      var timeEl = document.querySelector('.tg-time');
      /* the phone's clock starts at the visitor's REAL current time */
      if (timeEl) timeEl.textContent = hhmm(NOW);

      function setPhoneTime(t) {
        if (timeEl) timeEl.textContent = t;
        var st = document.getElementById('iosStatusTime');
        if (st) st.textContent = t;
      }

      /* full clean slate so the scene can run twice and look identical:
         queued posts out of the flow, counters at zero, reactions hidden */
      [msg, m2, m3].forEach(function (m) {
        if (!m) return;
        m.classList.remove('on', 'loading');
        m.querySelectorAll('.rx').forEach(function (p) { p.classList.remove('on', 'bump'); p.querySelector('b') && (p.querySelector('b').textContent = '0'); });
        var v = m.querySelector('.cp-views b');
        if (v) v.textContent = '0';
        if (m === img.closest('.chan-msg')) return;   /* post 1 settles later */
        var med = m.querySelector('.chan-media');
        if (med) med.classList.remove('settled');
      });
      img.classList.remove('settled');
      document.getElementById('iosNotif').classList.remove('on', 'press');

      /* Every channel timestamp follows the real computed schedule. There is
         deliberately no "@handle · schedule-id" line inside a post: a real
         channel never reprints its own name (the header says it) and it never
         prints its database id. */
      var foot1 = msg.querySelector('.cp-time2');
      if (foot1) foot1.textContent = SCHEDULED_POSTS[0].time;
      var f2 = m2.querySelector('.cp-time2'), f3 = m3.querySelector('.cp-time2');
      if (f2) f2.textContent = SCHEDULED_POSTS[1].time;
      if (f3) f3.textContent = SCHEDULED_POSTS[2].time;

      img.style.backgroundImage = bg(PHOTOS[w]);
      /* each queued post carries one of the uploaded photos, in order */
      [m2, m3].forEach(function (m, i) {
        var med = m.querySelector('.chan-media');
        if (med) med.style.backgroundImage = bg(PHOTOS[(w + i + 1) % PHOTOS.length]);
      });
      /* The channel has a history, dated backwards from the visitor's own
         clock: a feed that opens empty reads as a mock-up, and it also gives
         the new posts something real to push up the screen. */
      document.querySelectorAll('.chan-hist').forEach(function (h, i) {
        var med = h.querySelector('.chan-media');
        if (med) med.style.backgroundImage = bg(PHOTOS[(w + i + 2) % PHOTOS.length]);
        var t = h.querySelector('.cp-time2');
        if (t) t.textContent = hhmm(plusMin(NOW, i ? -41 : -96));
        var v = h.querySelector('.cp-views b');
        if (v) v.textContent = i ? '864' : '1 148';
      });
      msg.classList.add('loading');
      /* phone clock ticks minute-by-minute from the real current time up
         to the first send time — no instant jumps. clockMins tracks the
         story clock so successive ticks always move forward. Each change
         pulses the clock so the time visibly ticks. */
      var clockMins = NOW.getHours() * 60 + NOW.getMinutes();
      function tickTo(tStr, done) {
        var tp = tStr.split(':');
        var to = (+tp[0]) * 60 + (+tp[1]);
        if (to <= clockMins) to += 24 * 60;
        var total = to - clockMins;
        var n = 0;
        (function step() {
          n++;
          clockMins = (clockMins + 1) % (24 * 60);
          var tstr = pad(Math.floor(clockMins / 60) % 24) + ':' + pad(clockMins % 60);
          setPhoneTime(tstr);
          if (timeEl) { timeEl.classList.remove('tick'); void timeEl.offsetWidth; timeEl.classList.add('tick'); }
          if (n < total) later(step, 340); else if (done) done();
        })();
      }
      var started0 = false;
      tickTo(SCHEDULED_POSTS[0].time, function () {
        started0 = true;
        msg.classList.add('on');
      });
      later(function () {
        if (!started0) { msg.classList.add('on'); }   /* safety: never stall the scene */
        msg.classList.remove('loading');
        countUp(document.getElementById('chanViews'), 312);
        /* the photo settles ONCE — what was scheduled is what gets posted.
           (An older build re-painted the image mid-scene, which read as the
           post silently swapping its photo after going out.) */
        img.classList.add('settled');
      }, 4200);
      /* reactions gather on the fresh post while it ages */
      gatherReacts(msg, [
        { at: 4600, n: 24 },   /* 👍 */
        { at: 6200, n: 11 },   /* 🔥 */
        { at: 7900, n: 4 }     /* ⭐ paid */
      ]);

      /* post 2 — its own real send time */
      later(function () {
        tickTo(SCHEDULED_POSTS[1].time);
        m2.querySelector('.chan-post-cap2').textContent = SCHEDULED_POSTS[1].text;
        m2.classList.add('on');
      }, 5400);
      later(function () {
        countUp(m2.querySelector('.cp-views b'), 148);
      }, 6300);
      gatherReacts(m2, [
        { at: 6500, n: 17 },
        { at: 7600, n: 6 },
        { at: 8600, n: 2 }
      ]);

      /* post 3 — its own real send time */
      later(function () {
        tickTo(SCHEDULED_POSTS[2].time);
        m3.querySelector('.chan-post-cap2').textContent = SCHEDULED_POSTS[2].text;
        m3.classList.add('on');
      }, 7400);
      later(function () {
        countUp(m3.querySelector('.cp-views b'), 96);
        chanLayer.querySelector('.sl-sub').textContent = '@fastschedule_test3';
      }, 8200);
      gatherReacts(m3, [
        { at: 8500, n: 12 },
        { at: 9600, n: 5 },
        { at: 10400, n: 3 }
      ]);

      later(function () { botConfirmScene(w); }, 11300);
    }

    /* 19 — back in the bot chat: the confirmation appears below all the
       previous messages, then the finale restores the hero copy */
    function botConfirmScene(w) {
      showTyping(900).then(function () {
        var m = botMsg('✅ <b>Published to @fastschedule_test3</b><span class="mono">📷 1 photo · caption "' + SCHEDULED_POSTS[0].text + '"\n🕒 ' + SCHEDULED_POSTS[0].time + ' — delivered right on time</span>' + meta(SCHEDULED_POSTS[0].time));
        show(m);
        /* the confirmation is the last thing that happens in the chat: clamp
           the scroll once more when the reveal transition ends, so its tail
           is never parked behind the compose bar on phones */
        setTimeout(scrollEnd, 500);
        return sleep(2300);
      }).then(function () { finale(); });
    }

    /* 20 — cinematic finale. Beats:
       1. the channel layer fades, the phone hides;
       2. "fast scheduler" is written right-to-left, letter by letter, the
          word lifting from the ground as it fills;
       3. one sentence fades in under it;
       4. the whole title glides up-left and dissolves;
       5. the phone slides back up from the ground on the right with the
          hero headline + replay menu — the page is whole again. */
    function finale() {
      phone.classList.remove('glare-still');             /* the glass sweep may return */
      chanLayer.classList.remove('on');
      iosLayer.classList.remove('on', 'launch');
      botLayer.classList.remove('on');
      explorerOn(false);
      dropGlow.classList.remove('on');
      fxCursor.classList.remove('on', 'holding');
      rlStage.classList.add('on', 'finale');
      rlStage.classList.remove('written', 'hero-back');
      rlStage.innerHTML = '';
      /* hide the device: it drops away and the stage owns the frame */
      phone.classList.add('cine-hide');
      phone.classList.remove('cinema');

      var brand = document.getElementById('cineBrand');
      var cine = document.getElementById('heroCine');
      if (cine) cine.classList.add('cine-on');   /* the title overlay is ON only for the finale */
      var word = 'fast scheduler';
      if (brand) {
        brand.innerHTML = '';
        word.split('').forEach(function (ch, i) {
          var s = document.createElement('span');
          s.className = 'cl';
          s.textContent = ch === ' ' ? '\u00a0' : ch;
          s.style.animationDelay = (0.25 + i * 0.055).toFixed(3) + 's';
          brand.appendChild(s);
        });
      }
      var writeMs = reduce ? 400 : 700 + word.length * 55;

      /* beat 2: the word is written — now lift it toward the top-left */
      later(function () {
        rlStage.classList.add('written');
        if (cine) cine.classList.add('done');
      }, writeMs + 500);

      /* beat 3: dissolve the title, bring the phone back up from the ground
         on the right, then the hero headline + replay menu. The replay pill
         is appended to the HERO (not the stage) with pointer-events disabled
         until everything has settled — an early click used to grab the whole
         pointer and cover the CTA / headline while the phone was still
         sliding in. */
      later(function () {
        rlStage.classList.add('hero-back');
        if (heroSec) heroSec.classList.add('hero-back');
        phone.classList.remove('cine-hide');
        phone.classList.add('cine-restore');
        /* replay returns as a small pill INSIDE the hero copy (hidden in the
           markup, revealed here), in normal flow under the CTA: it can never
           sit on top of the headline, the CTA or the restored phone (the old
           build appended an overlay button to the stage, which covered the
           hero elements). It stays after the finale teardown, too. */
        var rp = document.querySelector('.hero-copy .hero-replay');
        if (rp) rp.hidden = false;   /* the click handler is bound once at boot */
      }, writeMs + 2400);

      later(function () { phone.classList.remove('finale'); }, writeMs + 2500);
      later(function () { phone.classList.add('idle'); }, writeMs + 3200);   /* resume the float */
      later(function () {
        if (heroSec) heroSec.classList.remove('cinema');
        if (heroSec) heroSec.classList.remove('hero-back');
        if (cine) { cine.classList.remove('done'); cine.classList.remove('cine-on'); }
      }, writeMs + 3500);
      later(function () {
        phone.classList.remove('cine-restore');
        phone.style.removeProperty('--cinema-dx');
      }, writeMs + 4100);
    }
  }

  /* ---------- mono typing ---------- */
  function typeMono(m, text, speed) {
    var block = m.querySelector('.mono');
    if (!block) return;
    if (reduce) { block.textContent = text; return; }
    var caret = el('<span class="mono-caret"></span>');
    block.textContent = '';
    block.appendChild(caret);
    var i = 0;
    (function step() {
      if (i >= text.length) { caret.remove(); return; }
      caret.before(document.createTextNode(text[i++]));
      scrollEnd();
      setTimeout(step, speed || 15);
    })();
  }

  /* ---------- replay / reset ---------- */
  function resetAll() {
    clearTimers();
    runGen++;              /* kill any scene chain still in flight */
    started = false;
    stream.innerHTML = '';
    var staleRp = document.querySelector('.hero-copy .hero-replay');
    if (staleRp) staleRp.hidden = true;
    typing.classList.remove('on');
    explorer.classList.remove('on', 'dragging');
    explorer.querySelectorAll('.fx-item').forEach(function (n) { n.classList.remove('selected', 'lifted'); });
    fxCursor.classList.remove('on', 'holding');
    dropGlow.classList.remove('on');
    rlStage.classList.remove('on', 'cinema', 'finale');
    rlStage.innerHTML = '';
    iosLayer.classList.remove('on');
    chanLayer.classList.remove('on');
    botLayer.classList.remove('on');
    phone.classList.remove('cinema', 'finale', 'cine-hide', 'cine-restore', 'glare-still');
    var stage2 = document.getElementById('rlStage');
    if (stage2) stage2.classList.remove('written', 'hero-back');
    if (stageEl) stageEl.classList.remove('cinema');
    if (heroSec) heroSec.classList.remove('cinema', 'hero-back');
    var cineEl = document.getElementById('heroCine');
    if (cineEl) { cineEl.classList.remove('done', 'cine-on'); }
    /* wipe the finale letters out of the overlay: leftover spans painted
       straight over the roulette scene on the next cinema entry */
    var brandEl = document.getElementById('cineBrand');
    if (brandEl) brandEl.innerHTML = '';
    var notifEl2 = document.getElementById('iosNotif');
    if (notifEl2) notifEl2.classList.remove('on', 'press');
    document.getElementById('iosLayer').classList.remove('launch');
    document.documentElement.classList.remove('demo-cinema');
    /* input field, clock and magnifier back to their initial state */
    var inp = document.querySelector('.tg-input');
    if (inp) { inp.classList.remove('composing'); var ph2 = inp.querySelector('.tg-input-ph'); if (ph2) ph2.textContent = 'Message'; }
    var cl2 = document.getElementById('iosClock');
    if (cl2) cl2.classList.remove('tick');
    var tm2 = document.querySelector('.tg-time');
    if (tm2) tm2.classList.remove('tick');
    var snd = document.querySelector('.tg-input .tg-send');
    if (snd) snd.classList.remove('sent');
    setHeaderState(null);
    var spot = document.querySelector('.ios-spot');
    if (spot) spot.classList.remove('grow');
    var clEl = document.getElementById('iosClock');
    if (clEl) clEl.textContent = hhmm(NOW);
    /* take the reveal off every post, or a replay would open on the whole queue */
    var cmEl = document.getElementById('chanMsg');
    if (cmEl) cmEl.classList.remove('loading', 'on');
    var cvEl = document.getElementById('chanViews');
    if (cvEl) cvEl.textContent = '0';
    document.querySelectorAll('.chan-msg2, .chan-msg3').forEach(function (n) {
      n.classList.remove('on');
      var v = n.querySelector('.cp-views b');
      if (v) v.textContent = '0';
    });
    var tEl = document.querySelector('.tg-time');
    if (tEl) tEl.textContent = hhmm(NOW);
    var dEl = document.querySelector('.ios-date');
    if (dEl) dEl.textContent = WEEKDAYS[NOW.getDay()] + ', ' + MONTHS[NOW.getMonth()] + ' ' + TODAY_NUM;
    setCursorAt(320, 300);
  }
  /* replay lives on the phone screen (finale button); nothing else needed */

  /* Start when the hero phone is visible. The phone is above the fold on every
     layout, but an IntersectionObserver can deliver late (and never fires at
     all for some engines on a preserve-3d transformed subtree), which used to
     leave the screen blank — so we also check once on the first painted frame
     and whenever the page is scrolled back to the top. */
  function startNow() { if (!started) play(); }
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) startNow(); });
    }, { threshold: 0.15 });
    io.observe(phone);
  }
  function kickIfInView() {
    if (started) return;
    var r = phone.getBoundingClientRect();
    var vh = window.innerHeight || document.documentElement.clientHeight;
    if (r.top < vh && r.bottom > 0) later(startNow, 350);
  }
  kickIfInView();                                   /* the layout is ready here */
  raf(kickIfInView);              /* re-check after first paint */
  setTimeout(kickIfInView, 700);                    /* rAF can be throttled to a stop */
  window.addEventListener('scroll', function () {
    if (!started && window.scrollY < 120) kickIfInView();
  }, { passive: true });

  /* ---------- QA hook ----------
     Replay the film, or jump straight to one of its late scenes, so a change
     to the channel / clock / calendar can be checked without sitting through
     the whole timeline. Nothing in the page calls this. */
  window.FS_DEMO = {
    replay: function () { resetAll(); play(); },
    /* stop the scripted run so it cannot fight whatever we open next */
    stop: function () { clearTimers(); resetAll(); started = false; },
    /* holdMs is optional: it drops the scene's own chain after that long, so
       the scene under inspection does not hand off to the next one */
    jump: function (name, holdMs) {
      window.FS_DEMO.stop();        /* clears timers AND invalidates live chains */
      var scenes = window.FS_DEMO.scenes || {};
      if (!scenes[name]) return;
      var w = Math.floor(Math.random() * PHOTOS.length);
      if (name !== 'confirm' && name !== 'finale') {
        phone.classList.add('cinema');
        phone.classList.remove('idle');
        var h = document.querySelector('.hero');
        if (h) h.classList.add('cinema');
      }
      if (name === 'calendar') { rlStage.classList.add('on', 'cinema'); rlStage.innerHTML = ''; }
      scenes[name](w);
      if (holdMs) setTimeout(function () { runGen++; }, holdMs);
    }
  };
})();
