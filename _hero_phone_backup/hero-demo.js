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
  function art(bg, f1, f2) {
    var svg = "<svg xmlns='http://www.w3.org/2000/svg' width='120' height='120'>" +
      "<rect width='120' height='120' fill='" + bg + "'/>" +
      "<circle cx='92' cy='26' r='13' fill='" + f2 + "' opacity='.9'/>" +
      "<path d='M0 96 Q30 66 60 92 T120 84 V120 H0 Z' fill='" + f1 + "' opacity='.85'/>" +
      "<path d='M0 106 Q34 82 66 104 T120 98 V120 H0 Z' fill='" + f1 + "'/></svg>";
    return "url('data:image/svg+xml," + encodeURIComponent(svg).replace(/'/g, '%27') + "')";
  }
  PHOTOS[0].img = art('#f2c94c', '#7a9d3f', '#e8862e');
  PHOTOS[1].img = art('#8a6a4a', '#5d442e', '#d9b06a');
  PHOTOS[2].img = art('#4e6b46', '#2e4028', '#93b564');
  PHOTOS[3].img = art('#d99a4e', '#8a5a26', '#f2c94c');

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
  function kb(rows, accIdx, extraCls) {
    return '<span class="kb-row">' + rows.map(function (r, i) {
      return '<span class="kb ' + (extraCls || '') + (i === accIdx ? ' kb-acc' : '') + '">' + r + '</span>';
    }).join('') + '</span>';
  }
  /* Pacing must be identical whether or not motion is reduced — collapsing
     these delays makes every scene after the roulette invisible. Reduced
     motion only removes smooth *transitions* (handled in CSS), never scenes. */
  function sleep(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }
  function botMsg(html) { var m = el('<div class="msg bot">' + html + '</div>'); stream.appendChild(m); return m; }
  function userMsg(html) { var m = el('<div class="msg user">' + html + '</div>'); stream.appendChild(m); return m; }
  function show(m) { m.classList.add('shown'); scrollEnd(); }
  function scrollEnd() { requestAnimationFrame(function () { chat.scrollTop = chat.scrollHeight; }); }
  function showTyping(ms) {
    typing.classList.add('on'); scrollEnd();
    return sleep(ms || 850).then(function () { typing.classList.remove('on'); });
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
  /* the user "taps" a keyboard button: the bubble is revealed FIRST (so the
     cursor aims at something visible), then the cursor glides to the exact
     button pill, clicks it, the bubble presses in */
  function tapMsg(m, btnIdx) {
    return new Promise(function (done) {
      show(m);                                  /* visible before aiming */
      var target = m.querySelector('.kb-row .kb' + (btnIdx != null ? ':nth-child(' + (btnIdx + 1) + ')' : ':first-child'));
      var c = target ? localPoint(target, .5, .5) : bubbleCenter(m);
      fxCursor.classList.add('on');
      glideCursor(c.x, c.y, 480).then(function () {
        clickFx(c.x, c.y);
        m.classList.add('pressed');
        setTimeout(function () { m.classList.remove('pressed'); done(); }, 200);
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
        if (k < 1) requestAnimationFrame(tick); else done();
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
        if (k < 1) requestAnimationFrame(tick); else done();
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
          '<span class="fx-ic" style="background-image:' + p.img + '"></span>' +
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

  function play() {
    if (started) return;
    started = true;
    refreshNow();
    var T = 0;
    function at(dt, fn) { T += dt; later(fn, T); }

    buildExplorer();

    /* 1 — user opens the bot */
    at(600, function () { tapMsg(userMsg('📅 Schedule a Message'), 0); });

    /* 2 — bot: main dashboard (exact real text) */
    at(500, function () {
      showTyping(950).then(function () {
        show(botMsg('🤖 <b>@Fast_Schedule_7e6d96_bot</b> Dashboard' + meta(storyTime(0)) +
          kb(['🗓 Schedule a Message', '🔁 Recurring Messages', '📣 @fastschedule_test3',
              '📋 My Messages', '💾 Media Storage'], 0) +
          kb(['➡️ Next'], -1, 'kb-red')));
      });
    });

    /* 3 — bot: Schedule a Message info sheet */
    at(2900, function () {
      showTyping(1050).then(function () {
        show(botMsg('📝 <b>Schedule a Message</b><br>Send me your message with the date and time.<br><br>' +
          '<b>Format:</b><span class="mono">DD.MM.YYYY HH:MM\nYour message</span>' +
          '<b>Features:</b><span class="mono">• Add photos, videos, or documents\n• Create polls and quizzes (anonymous only)\n• Add inline buttons\n• Use formatting (bold, italic, links, etc.)</span>'));
      });
    });

    /* 4 — user types the real batch (dates built from the visitor's clock)
       — mirrored into the message field letter by letter, and the chat
       bubble only appears once the whole text has been typed + sent */
    at(3400, function () {
      typeInField(BATCH_TEXT).then(function () {
        var m = userMsg('<span class="mono">' + BATCH_TEXT.replace(/\n/g, '<br>') + '</span>');
        show(m);
        tapMsg(m);
      });
    });

    /* 5 — bot: Select Photo Mode (real expanded text) */
    at(3600, function () {
      showTyping(1100).then(function () {
        show(botMsg('📷 <b>Select Photo Mode</b><br>Choose how your photos will be attached to scheduled posts:<br><br>' +
          '📷 <b>Normal</b><br>Each post gets the exact same photo. Perfect for branding — use your logo, watermark, or a consistent visual identity across all messages.<br><br>' +
          '🎲 <b>Random</b><br>Each post gets a random photo from the set you upload. Great for variety — keeps your channel visually fresh without repeating the same image.<br><br>' +
          '🔀 <b>Sequential</b><br>Photos are sent in order, one per post. Ideal for story-like content, step-by-step tutorials, or any sequence where order matters.<br><br>' +
          '⏭ <b>Skip Photos</b>' + meta(storyTime(1)) +
          kb(['🎲 Random', '📷 Normal', '🔀 Sequential', '⏭ Skip Photos']) + kb(['❌ Cancel'], -1, 'kb-red')));
      });
    });

    /* 6 — user taps Random */
    at(3000, function () { tapMsg(userMsg('🎲 Random'), 0); });

    /* 7 — bot asks for photos, then the whole upload flow runs as one
       promise chain so no timed message can race the mouse animation */
    at(1700, function () {
      showTyping(800).then(function () {
        show(botMsg('📷 <b>Send photos or click Done:</b>' + meta(storyTime(2)) +
          kb(['✅ Done (0)'], -1, 'kb-green') + kb(['❌ Cancel'], -1, 'kb-red')));
        startExplorerFlow();
      });
    });

    function startExplorerFlow() {
      explorerScene()
        .then(function () { return uploadingScene(); })
        .then(function () { return sleep(600); })
        .then(function () { return tapMsg(userMsg('✅ Done (4)'), 0); })
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
        .then(function () { return sleep(1000); })
        .then(function () { return tapMsg(userMsg('✅ Schedule'), 0); })
        .then(function () { return botSay('✅ <b>3 message(s) scheduled.</b><span class="mono">' + SCHEDULED_POSTS.map(function (p, i) {
          return '📅 s33455' + i + '_' + i + ': ' + p.text + '\n' + stamp(SEND_TIMES[i]).split(' ')[0] + ' — ' + SEND_TIMES[i].getFullYear() + '-' + pad(SEND_TIMES[i].getMonth() + 1) + '-' + pad(SEND_TIMES[i].getDate()) + ' ' + hhmm(SEND_TIMES[i]) + ':00';
        }).join('\n\n') + '</span>' + meta(storyTime(5)) +
          kb(['📤 Schedule a few more']) + kb(['⬅️ Back'])); })
        .then(function () { return sleep(1600); })
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
            /* pause, then tap the send plane */
            setTimeout(function () {
              var plane = document.querySelector('.tg-input .tg-send');
              field.textContent = 'Message';
              input.classList.remove('composing');
              if (!plane) { done(); return; }
              var c = localPoint(plane, .5, .5);
              fxCursor.classList.add('on');
              glideCursor(c.x, c.y, 420).then(function () {
                clickFx(c.x, c.y);
                plane.classList.add('sent');
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
      var drag = el('<span class="fx-drag" style="background-image:' + PHOTOS[0].img + '"></span>');
      var g1 = el('<span class="fx-ghost" style="background-image:' + PHOTOS[1].img + '"></span>');
      var g2 = el('<span class="fx-ghost" style="background-image:' + PHOTOS[2].img + '"></span>');
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
        if (k < 1) requestAnimationFrame(tick); else {
          drag.remove(); g1.remove(); g2.remove();
          fxCursor.classList.remove('holding');
          clickFx(endX, endY);
          /* hover beat so the drop is actually SEEN, then everything
             "pastes" into Telegram at once */
          later(function () {
            dropGlow.classList.remove('on');
            explorer.classList.remove('dragging');
            clickFx(endX, endY);
            explorerOn(false);
            fxCursor.classList.remove('on');
            dragDone();
          }, 1150);
        }
      })(t0);
      });
      });
    }

    /* 10 — Telegram uploading animation, then the real album message */
    function uploadingScene() {
      return new Promise(function (upDone) {
      var bar = el('<span class="upl-bar">' + PHOTOS.map(function (p) {
        return '<span class="upl-cell" style="background-image:' + p.img + '">' +
          '<span class="upl-fill"></span><span class="upl-ring"><i></i></span><span class="upl-pct">0%</span></span>';
      }).join('') + '</span>');
      var m = userMsg('');
      m.appendChild(bar);
      show(m);
      var cells = bar.querySelectorAll('.upl-cell');
      var t0 = performance.now(), dur = reduce ? 60 : 1500;
      (function tick(now) {
        var k = Math.min(1, (now - t0) / dur);
        cells.forEach(function (cell, i) {
          var p = Math.min(1, Math.max(0, k * 1.25 - i * 0.08));
          cell.querySelector('.upl-fill').style.height = (p * 46) + '%';
          cell.querySelector('.upl-pct').textContent = Math.round(p * 100) + '%';
          if (p >= 1) cell.classList.add('done');
        });
        if (k < 1) requestAnimationFrame(tick); else {
          sleep(360).then(function () {
            /* swap the placeholder bar for the real Telegram album */
            var album = el('<span class="upl-strip">' + PHOTOS.map(function (p) {
              return '<span class="upl-thumb" style="background-image:' + p.img + '"></span>';
            }).join('') + '</span>');
            bar.replaceWith(album);
            scrollEnd();
            var thumbs = album.querySelectorAll('.upl-thumb');
            thumbs.forEach(function (th, i) {
              later(function () { th.classList.add('in', 'landing'); }, i * 110);
            });
            later(function () { upDone(); }, 4 * 110 + 900);
          });
        }
      })(t0);
      });
    }

    /* steps 11–15 now live inside the startExplorerFlow() chain above */

    function cinemaRoulette() {
      var pick = PHOTOS[Math.floor(Math.random() * PHOTOS.length)];
      document.documentElement.classList.add('demo-cinema');
      if (stageEl) stageEl.classList.add('cinema');
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
          '<span class="cp-time">📅 s334559_0 · @fastschedule_test3 · ' + SCHEDULED_POSTS[0].time + '</span></div></div>');
        rlStage.appendChild(card);

        /* four photo placeholders above the message */
        var holder = el('<div class="rl-holder"></div>');
        rlStage.appendChild(holder);
        var tiles = PHOTOS.map(function (p, i) {
          var t = el('<span class="rl-tile" style="background-image:' + p.img + ';left:' + (34 + i * 64) + 'px"></span>');
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
            var big = el('<span class="rl-fly" style="background-image:' + PHOTOS[w].img + '"></span>');
            var from = localPoint(tiles[w]);
            big.style.left = from.x + 'px';
            big.style.top = from.y + 'px';
            rlStage.appendChild(big);
            var img = el('<span class="rl-img" style="background-image:' + PHOTOS[w].img + '"></span>');
            card.insertBefore(img, card.firstChild);
            var to = localPoint(img);
            var dx = to.x - from.x;
            var dy = to.y - from.y;
            var s0 = 1, s1 = img.offsetWidth / 74;
            var dur = reduce ? 80 : 1050;
            var t0 = performance.now();
            (function fly(now) {
              var k = Math.min(1, (now - t0) / dur);
              var e = k < .5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2;  /* easeInOutCubic */
              var lift = Math.sin(k * Math.PI) * -58;                            /* arc over the card */
              var rot = (1 - k) * 10 - 5;                                        /* settles to straight */
              var sc = s0 + (s1 - s0) * e;
              var squash = k > .82 ? 1 + Math.sin((k - .82) / .18 * Math.PI) * .06 * (1 - (k - .82) / .18) : 1;
              big.style.transform = 'translate(' + (dx * e) + 'px,' + (dy * e + lift) + 'px) rotate(' + rot.toFixed(2) + 'deg) scale(' + (sc * squash).toFixed(3) + ')';
              big.style.opacity = k > .94 ? String((1 - k) / .06) : '1';
              if (k < 1) { requestAnimationFrame(fly); return; }
              big.remove();
              /* landing: ripple ring on the photo + card bounce */
              img.classList.add('settled');
              card.classList.add('landed');
              var burst = el('<span class="rl-burst"></span>');
              burst.style.left = to.x + 'px'; burst.style.top = to.y + 'px';
              rlStage.appendChild(burst);
              setTimeout(function () { burst.remove(); card.classList.remove('landed'); }, 900);
            })(t0);

            var badge = el('<span class="rl-attach on">🎲 random pick · attached</span>');
            card.appendChild(badge);
            sleep(1400).then(function () { calendarScene(w); });
          });
        }
      });
    }

    /* 16 — calendar reminder motion graphic */
    function calendarScene(w) {
      sleep(500).then(function () {
        rlStage.querySelectorAll('.rl-card,.rl-holder,.rl-question').forEach(function (n) { n.remove(); });
        var cal = el('<div class="rl-cal"><div class="cal-head"><span class="cal-dot"></span>Fast Schedule · reminder set</div>' +
          '<div class="cal-title"><b>' + MONTHS[NOW.getMonth()] + ' ' + NOW.getFullYear() + '</b></div>' +
          '<div class="cal-grid"><b>MO</b><b>TU</b><b>WE</b><b>TH</b><b>FR</b><b>SA</b><b>SU</b>' +
          (function () {
            var out = '';
            var dim = new Date(NOW.getFullYear(), NOW.getMonth() + 1, 0).getDate();
            var lead = (new Date(NOW.getFullYear(), NOW.getMonth(), 1).getDay() + 6) % 7;  /* MO-first offset */
            for (var b = 0; b < lead; b++) out += '<span class="cal-blank"></span>';
            for (var i = 1; i <= dim; i++) {
              var cls = 'cal-cell' + (i === TODAY_NUM ? ' today ev' : '');
              out += '<span class="' + cls + '" style="--i:' + (i - 1) + '">' + i + '</span>';
            }
            return out;
          })() +
          '</div><div class="cal-ev"><div class="cal-row"><span class="cal-ic"><svg viewBox="0 0 24 24" fill="#fff"><path d="M12 2a6 6 0 0 0-6 6v3.3l-1.6 3.2a1 1 0 0 0 .9 1.5h13.4a1 1 0 0 0 .9-1.5L18 11.3V8a6 6 0 0 0-6-6zm-2.5 15a2.5 2.5 0 0 0 5 0h-5z"/></svg></span>' +
          '<span><b>Channel post — @fastschedule_test3</b><small>' + SCHEDULED_POSTS[0].text + '</small></span>' +
          '<span class="cal-badge" id="calBadge">' + SCHEDULED_POSTS[0].time + ' · reminder</span></div></div></div>');
        rlStage.appendChild(cal);
        var count = el('<div class="rl-count" id="rlCount">' + countdown() + '</div>');
        rlStage.appendChild(count);
        requestAnimationFrame(function () { requestAnimationFrame(function () { cal.classList.add('on'); }); });
        sleep(700).then(function () {
          var b = cal.querySelector('.cal-badge');
          if (b) b.classList.add('on');
          count.classList.add('on');
        });
        sleep(4200).then(function () { iosScene(w); });
      });
    }

    /* 17 — iOS lock screen: magnifier springs in from the corner, grows
       over the clock, and the time winds up to the first real send time */
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
      sleep(800).then(function () {
        /* pin the magnifier lens EXACTLY on the clock (measured, any size) */
        var wrap = document.querySelector('.ios-mag-wrap');
        if (wrap) {
          wrap.style.left = (clock.offsetLeft + clock.offsetWidth / 2) + 'px';
          wrap.style.top = (clock.offsetTop + clock.offsetHeight / 2) + 'px';
        }
        document.querySelector('.ios-spot').classList.add('grow');   /* corner → spring into place */
        clock.classList.add('tick');
        /* wind from the current time to the send time — one visible tick
           per simulated minute so the clock reads like a real clock */
        var from = NOW.getHours() * 60 + NOW.getMinutes();
          var tparts = target.split(':');
          var to = (+tparts[0]) * 60 + (+tparts[1]);
          if (to <= from) to += 24 * 60;
          var steps = Math.max(1, to - from);   /* 1 step = 1 minute */
          var stepMs = reduce ? 120 : Math.min(500, Math.floor(5200 / steps));
          var zoomClock = document.getElementById('iosClockZoom');
          for (var i = 1; i <= steps; i++) {
            (function (i) {
              later(function () {
                var mins = Math.round(from + (to - from) * (i / steps)) % (24 * 60);
                var f = pad(Math.floor(mins / 60) % 24) + ':' + pad(mins % 60);
                clock.textContent = f; status.textContent = f;
                if (zoomClock) zoomClock.textContent = f;
              }, i * stepMs);
            })(i);
          }
      });
      sleep(2800).then(function () {
        document.getElementById('iosNotif').classList.add('on');   /* Telegram banner slides down */
      });
      sleep(4600).then(function () { channelScene(w); });
    }

    /* 18 — the channel: all 3 scheduled posts go out at their own time,
       while the phone's clock ticks forward (18:15 → 18:17) */
    function channelScene(w) {
      iosLayer.classList.remove('on');
      chanLayer.classList.add('on');
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

      /* every channel timestamp follows the real computed schedule */
      var capTime = msg.querySelector('.cp-time');
      if (capTime) capTime.textContent = '📅 s334559_0 · @fastschedule_test3 · ' + SCHEDULED_POSTS[0].time;
      var foot1 = msg.querySelector('.cp-time2');
      if (foot1) foot1.textContent = SCHEDULED_POSTS[0].time;
      var f2 = m2.querySelector('.cp-time2'), f3 = m3.querySelector('.cp-time2');
      if (f2) f2.textContent = SCHEDULED_POSTS[1].time;
      if (f3) f3.textContent = SCHEDULED_POSTS[2].time;

      img.style.backgroundImage = PHOTOS[w].img;
      msg.classList.add('loading');
      /* phone clock ticks minute-by-minute from the real current time up
         to the first send time — no instant jumps. clockMins tracks the
         story clock so successive ticks always move forward. */
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
          setPhoneTime(pad(Math.floor(clockMins / 60) % 24) + ':' + pad(clockMins % 60));
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
        document.getElementById('chanViews').textContent = '312';
      }, 4200);

      /* post 2 — its own real send time */
      later(function () {
        tickTo(SCHEDULED_POSTS[1].time);
        m2.querySelector('.chan-post-cap2').textContent = SCHEDULED_POSTS[1].text;
        m2.classList.add('on');
      }, 5400);
      later(function () {
        var v = m2.querySelector('.cp-views b'); if (v) v.textContent = '148';
      }, 6300);

      /* post 3 — its own real send time */
      later(function () {
        tickTo(SCHEDULED_POSTS[2].time);
        m3.querySelector('.chan-post-cap2').textContent = SCHEDULED_POSTS[2].text;
        m3.classList.add('on');
      }, 7400);
      later(function () {
        var v = m3.querySelector('.cp-views b'); if (v) v.textContent = '96';
        document.querySelector('.sl-sub').textContent = '1 284 subscribers';
      }, 8200);

      later(function () { botConfirmScene(w); }, 11300);
    }

    /* 19 — back in the bot chat: the confirmation appears below all the
       previous messages, then the finale restores the hero copy */
    function botConfirmScene(w) {
      showTyping(900).then(function () {
        show(botMsg('✅ <b>Published to @fastschedule_test3</b><span class="mono">📷 1 photo · caption "' + SCHEDULED_POSTS[0].text + '"\n🕒 ' + SCHEDULED_POSTS[0].time + ' — delivered right on time</span>' + meta(SCHEDULED_POSTS[0].time)));
        return sleep(2000);
      }).then(function () { finale(); });
    }

    /* 20 — zoom out to the full phone, logo on screen, and the hero copy
       comes back so nothing on the page is left hidden */
    function finale() {
      chanLayer.classList.remove('on');
      phone.classList.remove('cinema');
      phone.classList.add('finale');
      rlStage.classList.add('on', 'finale');
      rlStage.innerHTML = '';
      rlStage.appendChild(el('<div class="rl-logo">⚡</div>'));
      var sub = el('<div class="rl-finale-sub">Scheduled once · delivered forever</div>');
      rlStage.appendChild(sub);
      var rp = el('<button type="button" class="rl-replay">↺ Replay</button>');   /* el() keeps only the first node — create separately */
      rlStage.appendChild(rp);
      rp.addEventListener('click', function () { resetAll(); play(); });
      /* cinematic sparkle field around the logo */
      for (var i = 0; i < 12; i++) {
        var pt = el('<span class="rl-spark"></span>');
        pt.style.setProperty('--sx', (Math.random() * 280 - 140).toFixed(0) + 'px');
        pt.style.setProperty('--sy', (Math.random() * -180 - 40).toFixed(0) + 'px');
        pt.style.animationDelay = (Math.random() * 1.6).toFixed(2) + 's';
        pt.style.animationDuration = (2.6 + Math.random() * 2).toFixed(2) + 's';
        rlStage.appendChild(pt);
      }
      /* restore the regular hero copy and let the phone glide back to
         its original standing pose next to the text */
      if (heroSec) heroSec.classList.remove('cinema');
      later(function () { phone.classList.remove('finale'); }, 2500);
      later(function () { phone.style.removeProperty('--cinema-dx'); }, 3800);
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
    started = false;
    stream.innerHTML = '';
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
    phone.classList.remove('cinema', 'finale');
    if (stageEl) stageEl.classList.remove('cinema');
    if (heroSec) heroSec.classList.remove('cinema');
    document.documentElement.classList.remove('demo-cinema');
    /* input field, clock and magnifier back to their initial state */
    var inp = document.querySelector('.tg-input');
    if (inp) { inp.classList.remove('composing'); var ph2 = inp.querySelector('.tg-input-ph'); if (ph2) ph2.textContent = 'Message'; }
    var snd = document.querySelector('.tg-input .tg-send');
    if (snd) snd.classList.remove('sent');
    var spot = document.querySelector('.ios-spot');
    if (spot) spot.classList.remove('grow');
    var wrapEl = document.querySelector('.ios-mag-wrap');
    if (wrapEl) { wrapEl.style.left = ''; wrapEl.style.top = ''; }
    var tEl = document.querySelector('.tg-time');
    if (tEl) tEl.textContent = hhmm(NOW);
    var dEl = document.querySelector('.ios-date');
    if (dEl) dEl.textContent = WEEKDAYS[NOW.getDay()] + ', ' + MONTHS[NOW.getMonth()] + ' ' + TODAY_NUM;
    var zEl = document.getElementById('iosClockZoom');
    if (zEl) zEl.textContent = hhmm(NOW);
    setCursorAt(320, 300);
  }
  /* replay lives on the phone screen (finale button); nothing else needed */

  /* start when the hero phone is visible */
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      if (en.isIntersecting && !started) play();
    });
  }, { threshold: 0.2 });
  io.observe(phone);
})();
