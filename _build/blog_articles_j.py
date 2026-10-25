# -*- coding: utf-8 -*-
"""Blog articles, part 10 — recovered release notes.

The original untracked source was lost when the build directory was
overwritten; this file is rebuilt from the generated pages by
tools/recover_blog_j.py so the next build keeps both articles byte-for-byte
(modulo whitespace) instead of dropping them.
"""

BLOG_ARTICLES_J = []


def _a(i, **kw):
    kw['id'] = i
    BLOG_ARTICLES_J.append(kw)


_a("october-2026-legal-refresh",
   category="platform",
   title="Our October 2026 Legal Refresh: What Changed and Where to Find It",
   description="Privacy Policy, Terms and Refund Policy rewritten for clarity in October 2026: what changed, what stayed the same, and where every past version lives.",
   date="2026-10-02",
   content=
       "<p>In October 2026 we rewrote all three legal documents — <a href=\"../../../help/a/legal_privacy/\">Privacy Policy</a>, Terms of Service, and <a href=\"../../../legal/refund-policy/\">Refund Policy</a>. Nothing about the product changed: no new data collection, no new fees, no change to what the bot does. The goal was clarity: shorter sentences, explicit service names, and every past version kept public so changes are auditable.</p><h3 id=\"s-privacy-policy-explicit-services-same-rights\">Privacy Policy: explicit services, same rights</h3><p>The policy now names each service it covers — Fast Scheduler, the SetDate companion bot, the Support bot, and this website — and lists exactly what is stored and why: your Telegram user ID, connected channel IDs, <a href=\"../../../help/a/message_list/\">scheduled messages</a>, settings, and bot tokens. Media stays as Telegram file references, never re-uploaded copies. Your rights are unchanged: export a copy anytime, and delete everything on request. Nothing is sold, and nothing leaves the pipeline except payment processing via Telegram.</p><h3 id=\"s-terms-clearer-rules-announced-changes\">Terms: clearer rules, announced changes</h3><p>Plan limits, fair-use rules, and <a href=\"../../../help/a/security_2fa/\">account safety</a> are now stated plainly, including how future changes work: material changes (pricing, data processing, user rights) are announced in-app, and continued use after the effective date means acceptance. Non-material fixes just update the revision date. If you ever disagree with an update, export or delete your data first — both are one request away.</p><h3 id=\"s-refund-policy-stars-rules-stated-plainly\">Refund Policy: Stars rules, stated plainly</h3><p>Premium is paid in Telegram Stars, and Stars purchases are final under Telegram's own policies — the new text says so outright instead of implying it. Outside mandatory consumer rights, refunds are discretionary and case by case: double charges and genuine technical faults are the classic approved cases. Requests go to fastschedulebot@gmail.com with the transaction ID, username, and reason, and we acknowledge within 7 business days. Monthly plans still cancel via /premium with the paid period running to its end date.</p><h3 id=\"s-where-past-versions-live\">Where past versions live</h3><p>Every document shows its effective date, and previous versions stay published in the version history on the website, reachable from the legal pages. When the next refresh comes, you will be able to diff it yourself instead of taking our word for it.</p>"),


_a("media-storage-premium-toolkit",
   category="tools",
   title="Media Storage Goes Pro: Move, Copy and Download Whole Boxes",
   description="Fast Scheduler Media Storage learned bulk moves: Move All and Copy All with type filters plus whole-box download as one archive.",
   date="2026-10-02",
   content=
       "<p>Media Storage started as a simple shelf: save a photo once, reuse it in any post. It worked — until libraries grew into hundreds of files across a dozen boxes and reorganizing meant tapping through every item one by one. The Premium toolkit fixes exactly that with three bulk tools: <b>Move All</b>, <b>Copy All</b>, and <b>Download Box</b>.</p><h3 id=\"s-move-all-reorganize-a-box-in-one-tap\">Move All: reorganize a box in one tap</h3><p>Open any box and tap <b>Move All</b>. Every item goes to the box you pick — or only one type, with the optional filter for images, videos, or files. The classic use: a mixed “everything” box that grew for months gets split by type in three taps. Another: retiring a finished campaign — move the whole box into an archive box and the working set is clean again. ControllerBot and ManyBot make you do this file by file; here it is one action.</p><h3 id=\"s-copy-all-seed-without-touching-the-original\">Copy All: seed without touching the original</h3><p><b>Copy All</b> follows the same flow, but the source box keeps its items. That is the right tool when a new campaign needs the same starter set — brand banner, price card, disclaimer image — without disturbing the archive they live in. Filter by type the same way: copy only the videos into a video-only box, for example.</p><h3 id=\"s-download-box-the-whole-box-as-one-archive\">Download Box: the whole box as one archive</h3><p><b>Download Box</b> packs the entire box into a single archive. Keep an offline copy before a big restructuring, hand a full asset set to a teammate or designer, or pull everything down before travel. One archive beats twenty forwarded files — names, quality, and order survive the trip.</p><h3 id=\"s-what-stays-free\">What stays free</h3><p>Everything, one file at a time: open any item and <b>Move</b>, <b>Copy</b>, or <b>Download</b> works on the Free plan with no limits on how often. Premium only removes the repetition — the same results, minus the tapping. If your library fits in one box of 100 items and you rarely reorganize, Free remains the right plan.</p><h3 id=\"s-a-cleanup-routine-that-actually-sticks\">A cleanup routine that actually sticks</h3><p>Once a quarter: open each box, <b>Move All</b> by type into sorted boxes, <b>Download Box</b> for the ones you are retiring, delete what is left. Ten minutes, four times a year, and the picker stays a joy instead of an archaeology dig.</p>"),


