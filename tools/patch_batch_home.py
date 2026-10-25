"""Patch the homepage with the batch-scheduling format showcase.

The homepage is hand-maintained markup (no builder writes it), so — like the
other tools/patch_*.py scripts — every replacement is checked before writing
and is a no-op on a second run.

Run from the repo root:

    python tools/patch_batch_home.py            # apply
    python tools/patch_batch_home.py --check    # verify only
"""

import io
import sys

PATH = 'website/index.html'

CSS = """
    /* Batch-format showcase (homepage) */
    .batch-glass { display: grid; grid-template-columns: minmax(0, .82fr) minmax(0, 1.18fr);
      gap: clamp(22px, 3.4vw, 46px); align-items: center; padding: clamp(22px, 3.2vw, 44px); }
    .batch-copy h3 { font-size: clamp(1.15rem, 2.4vw, 1.6rem); margin: 0 0 10px; }
    .batch-copy > p { color: var(--text-dim); line-height: 1.65; margin: 0 0 16px; }
    .batch-list { list-style: none; margin: 0 0 20px; padding: 0; display: grid; gap: 10px; }
    .batch-list li { display: flex; gap: 10px; align-items: flex-start; line-height: 1.5;
      color: var(--text-dim); font-size: .95rem; }
    .batch-list li > span { min-width: 0; }
    .batch-list b { color: var(--text); }
    .batch-list .bl-ic { width: 18px; height: 18px; flex: none; margin-top: 2px; color: var(--green-strong); }
    .batch-list code, .batch-copy code { font-size: .86em; }
    .batch-demo { background: var(--surface-2, var(--surface)); border: 1px solid var(--border);
      border-radius: 16px; overflow: hidden; min-width: 0; }
    .batch-demo-bar { display: flex; align-items: center; gap: 10px; padding: 10px 14px;
      border-bottom: 1px solid var(--border); font-size: .74rem; letter-spacing: .05em;
      text-transform: uppercase; color: var(--text-dim); }
    .bd-dots { display: inline-flex; gap: 5px; }
    .bd-dots i { width: 7px; height: 7px; border-radius: 50%; background: var(--border); }
    .batch-demo pre { margin: 0; padding: 14px 16px; font-family: ui-monospace, SFMono-Regular, Menlo,
      Consolas, monospace; font-size: clamp(.72rem, 1.55vw, .84rem); line-height: 1.55;
      white-space: pre; overflow-x: auto; -webkit-overflow-scrolling: touch; color: var(--text); }
    .batch-demo .bd-d { color: var(--green-strong); font-weight: 700; }
    .batch-demo .bd-b { color: var(--text-dim); }
    .batch-demo-foot { display: flex; flex-wrap: wrap; gap: 8px 12px; align-items: center;
      padding: 10px 14px; border-top: 1px solid var(--border); font-size: .78rem; color: var(--text-dim); }
    .batch-demo-foot .chip { background: rgba(31, 170, 89, .14);
      background: color-mix(in srgb, var(--green) 14%, transparent); color: var(--green-strong);
      border-radius: 999px; padding: 3px 10px; font-weight: 700; }
    /* One column until there is genuinely room for both the copy and the
       unwrapped code sample (it must not wrap: a wrapped line would read like
       a new post block). */
    @media (max-width: 1120px) { .batch-glass { grid-template-columns: minmax(0, 1fr); } }
    @media (max-width: 520px) {
      .batch-demo pre { font-size: .7rem; white-space: pre-wrap; overflow-wrap: anywhere; }
    }
"""

SECTION = """  <!-- ============ BATCH FORMAT ============ -->
  <section class="block" id="batch">
    <div class="sec-head reveal">
      <h2>One message. Your whole week.</h2>
      <p>Write the date, then the post. Leave a blank line and write the next one. That is the whole format.</p>
    </div>
    <div class="glass batch-glass reveal">
      <div class="batch-copy">
        <h3>Paste a batch. Queue a batch.</h3>
        <p>Fast Scheduler reads your message block by block: <b>the first line is when</b>, everything below it is <b>what gets published</b>. Five blocks in one message create five scheduled posts — and you can send another batch whenever you like.</p>
        <ul class="batch-list">
          <li><svg class="bl-ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="17" rx="2"/><path d="M3 9h18M8 2v4M16 2v4"/></svg><span><b>Any date you already write</b> — <code>today 10:23</code>, <code>tomorrow 7:24 PM</code>, <code>12.12.2026 18:28</code>, <code>23-10-2027 15:34</code>, <code>2026-12-12 18:28</code> or a bare <code>18:28</code>.</span></li>
          <li><svg class="bl-ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.5.5l2-2a5 5 0 0 0-7-7l-1 1"/><path d="M14 11a5 5 0 0 0-7.5-.5l-2 2a5 5 0 0 0 7 7l1-1"/></svg><span><b>Buttons per post</b> — <code>&lt;inline&gt;Text&lt;link="https://example.com"&gt;</code>, with <code>--</code> for one row and <code>//</code> for a new row.</span></li>
          <li><svg class="bl-ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M8 13h8M8 17h5"/></svg><span><b>Too long for one message?</b> Save the same text as a <code>.txt</code> file and upload it while scheduling — one blank line between posts.</span></li>
          <li><svg class="bl-ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg><span><b>Free and Premium</b> — batches are not paywalled. On Free the only ceiling is the 100-message pending queue.</span></li>
        </ul>
        <a class="btn btn-primary" href="help/a/qa_schedule_many_at_once.html">See the full batch format</a>
      </div>
      <div class="batch-demo" aria-label="Example batch message sent to the bot">
        <div class="batch-demo-bar"><span class="bd-dots" aria-hidden="true"><i></i><i></i><i></i></span><span>One message to @FastSchedulerBot</span></div>
        <pre><span class="bd-d">today 10:23</span>
Morning news digest: three stories worth your time
<span class="bd-b">&lt;inline&gt;Read more&lt;link="https://example.com/news"&gt;</span>

<span class="bd-d">tomorrow 7:24 PM</span>
Poll day — which topic should we cover next?

<span class="bd-d">12.12.2026 18:28</span>
New drop is live. Limited stock, 24 hours only.
<span class="bd-b">&lt;inline&gt;Shop now&lt;link="https://example.com/shop" style="success"&gt;</span>

<span class="bd-d">23-10-2027 15:34</span>
Reminder: the community call starts in 30 minutes.

<span class="bd-d">14/04/2027 4:05 PM</span>
Weekend recap: the five most-read posts this week.</pre>
        <div class="batch-demo-foot"><span class="chip">5 posts scheduled</span><span>a blank line starts the next post</span></div>
      </div>
    </div>
  </section>

"""

# An earlier revision of this patch inserted a second Organization block; strip it
# if present so the page keeps exactly one entity for "Fast Scheduler".
ORG_LD_DUP = """  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "Organization",
    "@id": "https://fastscheduler.github.io/#organization",
    "name": "Fast Scheduler",
    "alternateName": ["FastScheduler", "Fast Scheduler Telegram bot", "@FastSchedulerBot"],
    "url": "https://fastscheduler.github.io/",
    "logo": "https://fastscheduler.github.io/icon-512.png",
    "description": "Fast Scheduler builds the Telegram post scheduler bot @FastSchedulerBot, which queues and auto-publishes channel posts.",
    "sameAs": [
      "https://t.me/FastSchedulerBot",
      "https://t.me/FastSchedulerSupport_bot",
      "https://fastscheduler.github.io/blog/",
      "https://fastscheduler.github.io/llms.txt"
    ]
  }
  </script>
"""

OLD_ORG = ('<script type="application/ld+json">{"@context": "https://schema.org", "@type": "Organization", '
           '"name": "Fast Scheduler", "url": "https://fastscheduler.github.io/", '
           '"logo": "https://fastscheduler.github.io/og-cover-v2.png", '
           '"description": "Telegram bot that schedules and auto-publishes channel posts: batch scheduling, '
           'recurring messages, sender bots, statistics and backups.", '
           '"sameAs": ["https://t.me/FastSchedulerBot"], '
           '"contactPoint": {"@type": "ContactPoint", "contactType": "customer support", '
           '"email": "fastschedulebot@gmail.com"}}</script>')

NEW_ORG = ('<script type="application/ld+json">{"@context": "https://schema.org", "@type": "Organization", '
           '"@id": "https://fastscheduler.github.io/#organization", '
           '"name": "Fast Scheduler", '
           '"alternateName": ["FastScheduler", "Fast Scheduler Telegram bot", "@FastSchedulerBot"], '
           '"url": "https://fastscheduler.github.io/", '
           '"logo": "https://fastscheduler.github.io/icon-512.png", '
           '"description": "Fast Scheduler builds the Telegram post scheduler bot @FastSchedulerBot, '
           'which queues and auto-publishes channel posts.", '
           '"sameAs": ["https://t.me/FastSchedulerBot", "https://t.me/FastSchedulerSupport_bot", '
           '"https://fastscheduler.github.io/blog/", '
           '"https://fastscheduler.github.io/llms.txt"], '
           '"contactPoint": {"@type": "ContactPoint", "contactType": "customer support", '
           '"email": "fastschedulebot@gmail.com"}}</script>')

REPLACEMENTS = [
    # --- identity: make the page state plainly what Fast Scheduler is -------------
    (
        '<title>Fast Scheduler | Telegram Fast Scheduler Bot</title>',
        '<title>Fast Scheduler — Telegram Post Scheduler Bot (@FastSchedulerBot)</title>',
    ),
    (
        '<meta name="description" content="Fast Scheduler is a free Telegram bot that schedules, publishes and tracks your channel posts. Batch-schedule a week in one chat, post from your own bot.">',
        '<meta name="description" content="Fast Scheduler (@FastSchedulerBot) is a free Telegram post scheduler bot. Paste many date + post blocks in one message — or upload a .txt — and it publishes each at the right time from your own bot.">',
    ),
    (
        '<meta property="og:title" content="Fast Scheduler | Telegram Fast Scheduler Bot">',
        '<meta property="og:title" content="Fast Scheduler — Telegram Post Scheduler Bot">',
    ),
    (
        '<h1>Fast Scheduler <span class="grad">| Telegram Fast Scheduler Bot</span></h1>',
        '<h1>Fast Scheduler <span class="grad">| Telegram post scheduler bot</span></h1>',
    ),
    (
        '<p class="sub">Paste a week of posts into one chat — <b>Fast Scheduler</b> publishes each one at the exact time you chose, in your timezone, from <b>your own bot</b>. Set it once, then get on with life.</p>',
        '<p class="sub"><b>Fast Scheduler</b> is a Telegram bot that schedules and publishes your channel posts for you. Paste a week of posts into one chat — one block per post, a blank line between them — and it publishes each one at the exact time you chose, in your timezone, from <b>your own bot</b>. Set it once, then get on with life.</p>',
    ),
    # --- entity schema: alternate names, official profiles, publisher ------------
    (
        '    "name": "Fast Scheduler",\n    "applicationCategory": "SocialMediaApplication",',
        '    "name": "Fast Scheduler",\n    "@id": "https://fastscheduler.github.io/#app",\n    "alternateName": ["FastScheduler", "Fast Scheduler Telegram bot", "@FastSchedulerBot"],\n    "applicationCategory": "SocialMediaApplication",\n    "isAccessibleForFree": true,\n    "sameAs": ["https://t.me/FastSchedulerBot", "https://t.me/FastSchedulerSupport_bot", "https://fastscheduler.github.io/llms.txt"],\n    "publisher": {"@id": "https://fastscheduler.github.io/#organization"},',
    ),
    (OLD_ORG, NEW_ORG),
    # --- batch format section ---------------------------------------------------
    ('  <!-- ============ PRICING ============ -->', SECTION + '  <!-- ============ PRICING ============ -->'),
    # --- CSS --------------------------------------------------------------------
    ('</style>', CSS + '</style>'),
    # --- FAQ: say the free plan accepts batches and name the format -------------
    (
        '<details><summary>How does it save me time?</summary><p>Batch-scheduling turns "post every day" into one weekly 10-minute session: paste a week of date+message pairs in a single chat. Recurring posts make daily digests fully automatic, and reports come to you instead of you hunting analytics.</p></details>',
        '<details><summary>How does it save me time?</summary><p>Batch scheduling turns "post every day" into one weekly 10-minute session. Paste several date + message blocks in a single message — a blank line between posts — and every block becomes its own scheduled post. The same text can be uploaded as a .txt file, and batches work on Free and Premium. Recurring posts make daily digests fully automatic, and reports come to you instead of you hunting analytics.</p></details>',
    ),
]


# Insertions keep their anchor in the result, so they need an explicit sentinel:
# seeing the sentinel means the block is already there and must not be added twice.
SENTINELS = {
    6: 'Fast-Scheduler/icon-512.png',  # only the enriched Organization block has it
    7: 'id="batch"',
    8: '.batch-glass {',
}


def main():
    check = '--check' in sys.argv
    with io.open(PATH, encoding='utf-8', newline='') as f:
        html = f.read()

    # Normalise CRLF for matching, restore it on write (this file is CRLF).
    text = html.replace('\r\n', '\n')
    pending = []
    for i, (old, new) in enumerate(REPLACEMENTS):
        sentinel = SENTINELS.get(i)
        if sentinel and sentinel in text:
            continue  # insertion already present
        if new in text and old not in text:
            continue  # already applied
        if old not in text:
            raise SystemExit('marker not found: %r' % old[:80])
        pending.append((old, new))

    # Guard against double-applying the section/CSS if a partial run happened.
    if 'id="batch"' in text and SECTION not in text:
        raise SystemExit('id="batch" exists with unexpected markup — inspect manually')

    removed = 0
    if ORG_LD_DUP in text:
        text = text.replace(ORG_LD_DUP, '', 1)
        removed = 1
        print('removed duplicate Organization block')

    for old, new in pending:
        text = text.replace(old, new, 1)

    print(('would apply %d replacement(s)' if check else 'applied %d replacement(s)')
          % len(pending))
    if check:
        return
    if pending or removed:
        with io.open(PATH, 'w', encoding='utf-8', newline='') as f:
            f.write(text.replace('\n', '\r\n'))


if __name__ == '__main__':
    main()
