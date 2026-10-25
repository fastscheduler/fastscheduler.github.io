/* =====================================================================
   Mini AI for help search — pure client-side intent matching.
   No server, no API: a small scoring engine that reads the visitor's
   free-text query and answers "what does the user mean". It mirrors the
   Support Bot's analyzer (Support Bot/ai_analyzer.py) so the website and
   the bot suggest the same articles for the same sentence.

     1. normalize: lowercase, straighten apostrophes, expand contractions
        ("what's" → "what is", "can't" → "can not"), expand chat
        abbreviations ("idk", "btw", "pls", "ur", "msg", "pic"), drop
        filler words — so a casually typed sentence becomes real words;
     2. light stemming ("scheduling" / "scheduled" / "schedule" all match,
        "photos" / "photo" all match);
     3. synonym + intent expansion (typos like "chanel" → channel,
        "reccuring" → recurring, phrases like "every week" → recurring);
     4. intent classification (schedule / media / payment / error …);
     5. TF-IDF-weighted ranking over the article index: title > FAQ >
        description > body, with exact-phrase and bigram bonuses;
     6. a human-sounding "interpretation" line: "You mean: how to connect
        your own sender bot".

   Exposed as window.HelpAI = { interpret, scoreAll, expand, tokenize, lev }.
   ===================================================================== */
(function () {
  'use strict';

  /* ---------- vocabulary + intents ---------- */
  /* Words that carry no topic on their own. Chat filler is dropped, but
     query words that matter ("not", "cant" → cannot) are kept: "post not
     sent" must stay an error query, not become a generic post query. */
  var STOP = {
    the: 1, a: 1, an: 1, is: 1, are: 1, was: 1, were: 1, am: 1, be: 1, been: 1,
    do: 1, does: 1, did: 1, how: 1, what: 1, why: 1, when: 1, where: 1, which: 1,
    i: 1, my: 1, me: 1, we: 1, us: 1, our: 1, you: 1, your: 1, it: 1, its: 1,
    this: 1, that: 1, these: 1, those: 1, to: 1, of: 1, in: 1, on: 1, for: 1,
    with: 1, and: 1, or: 1, but: 1, if: 1, so: 1, than: 1, then: 1, from: 1,
    at: 1, as: 1, by: 1, about: 1, into: 1, over: 1, under: 1, again: 1,
    will: 1, would: 1, should: 1, could: 1, shall: 1, may: 1, might: 1, must: 1,
    can: 1, could: 1, able: 1, possible: 1, ok: 1,
    there: 1, here: 1, some: 1, any: 1, all: 1, very: 1, just: 1, really: 1,
    please: 1, pls: 1, plz: 1, thanks: 1, thank: 1, thx: 1, ty: 1, tnx: 1,
    hi: 1, hello: 1, hey: 1, yo: 1, ok: 1, okay: 1, kk: 1, k: 1,
    btw: 1, tbh: 1, imo: 1, imho: 1, fyi: 1, afaik: 1, rn: 1, asap: 1,
    lol: 1, lmao: 1, omg: 1, haha: 1, hmm: 1, um: 1, uh: 1,
    bro: 1, dude: 1, guys: 1, man: 1, friend: 1, admin: 0,
    somehow: 1, anyway: 1, actually: 1, basically: 1, literally: 1,
    want: 1, wanna: 1, need: 1, gotta: 1, help: 1, question: 1,
    thing: 1, stuff: 1, something: 1, anything: 1, everything: 1, nothing: 1,
    get: 1, got: 1, give: 1, let: 1, make: 1, take: 1, use: 1, using: 1,
    like: 1, know: 1, think: 1, see: 1, say: 1, tell: 1, try: 1, trying: 1,
    work: 1, works: 1, working: 1, went: 1, out: 1, also: 1, nvm: 1, either: 1, many: 1,
    yes: 1, yeah: 1, yep: 1, nope: 1, maybe: 1, still: 1, already: 1, ever: 1
  };
  /* "not" family is meaningful for error queries; keep it out of STOP but
     do not let it dominate ranking on its own. */
  var NEGATIONS = { not: 1, no: 1, never: 1, cannot: 1, cant: 1, wont: 1, dont: 1, doesnt: 1, didnt: 1, isnt: 1, arent: 1 };

  var INTENTS = [
    { id: 'schedule', label: 'scheduling posts',
      words: ['schedule', 'scheduled', 'scheduling', 'recurring', 'repeat', 'repeating', 'cron',
        'every', 'weekly', 'daily', 'monthly', 'batch', 'queue', 'queued', 'time', 'date',
        'timezone', 'reccuring', 'shedule', 'sheduling', 'scheduel', 'repaeat', 'everyweek',
        'everyday', 'postpone', 'reschedule', 'calendar', 'delay', 'later', 'tomorrow'] },
    { id: 'media', label: 'photos and media',
      words: ['photo', 'photos', 'pic', 'pics', 'picture', 'pictures', 'image', 'images',
        'video', 'videos', 'album', 'albums', 'gif', 'gifs', 'media', 'file', 'files',
        'document', 'documents', 'upload', 'attach', 'attachment', 'sticker', 'stickers',
        'voice', 'audio', 'poll', 'polls', 'quiz', 'caption', 'storage', 'box', 'boxes',
        'picures', 'poto', 'vid', 'vids', 'photes', 'compress', 'compression'] },
    { id: 'channel', label: 'connecting a channel',
      words: ['channel', 'channels', 'connect', 'connecting', 'admin', 'administrator',
        'add', 'linked', 'link', 'group', 'supergroup', 'chanel', 'channal', 'connct',
        'conect', 'private', 'public', 'subscriber', 'subscribers', 'disconnect', 'unlink'] },
    { id: 'bot', label: 'sender bots',
      words: ['bot', 'bots', 'sender', 'token', 'own', 'custom', 'brand', 'bott', 'sendr',
        'botfather', 'webhook', 'promote', 'permission', 'permissions', 'rights'] },
    { id: 'payment', label: 'premium, billing and refunds',
      words: ['premium', 'pay', 'payment', 'billing', 'buy', 'purchase', 'stars', 'invoice',
        'refund', 'refunds', 'crypto', 'price', 'pricing', 'cost', 'subscription', 'upgrade',
        'plan', 'free', 'money', 'charged', 'charge', 'renew', 'cancel', 'cancell',
        'refound', 'premum', 'subscrition', 'trial', 'promo', 'promocode', 'coupon',
        'discount', 'offer', 'expire', 'expired', 'grace'] },
    { id: 'backup', label: 'backup and export',
      words: ['backup', 'backups', 'export', 'import', 'restore', 'fsback', 'fspback',
        'migrate', 'migration', 'transfer', 'move', 'copy', 'bakup', 'exprot', 'download',
        'data', 'csv', 'json', 'txt', 'rtf'] },
    { id: 'stats', label: 'statistics',
      words: ['stats', 'statistics', 'views', 'view', 'leaderboard', 'report', 'reports',
        'analytics', 'count', 'counter', 'performance', 'statisitcs', 'analitycs',
        'reactions', 'comments', 'err'] },
    { id: 'error', label: 'fixing problems',
      words: ['error', 'errors', 'problem', 'problems', 'issue', 'fail', 'fails', 'failed',
        'failing', 'stuck', 'broken', 'notworking', 'doesnt', 'dont', 'wont', 'cannot',
        'cant', 'fix', 'troubleshoot', 'late', 'delay', 'delayed', 'missing', 'skipped',
        'disappeared', 'wrong', 'bug', 'crash', 'blocked', 'forbidden'] },
    { id: 'account', label: 'getting started',
      words: ['start', 'begin', 'beginner', 'setup', 'onboarding', 'account', 'register',
        'signup', 'first', 'tutorial', 'guide', 'language', 'translate', 'translation',
        'english', 'russian', 'begining', 'stat', 'strat'] },
    { id: 'feedback', label: 'contacting support',
      words: ['support', 'contact', 'ticket', 'feedback', 'human', 'ask', 'report',
        'complain', 'complaint', 'suggestion', 'idea', 'request', 'feature', 'email'] },
    { id: 'formatting', label: 'formatting and buttons',
      words: ['format', 'formatting', 'bold', 'italic', 'underline', 'strike', 'code',
        'button', 'buttons', 'inline', 'markdown', 'html', 'emoji', 'signature', 'footer',
        'spoiler', 'quote', 'link', 'preview', 'mention'] },
    { id: 'limits', label: 'plan limits',
      words: ['limit', 'limits', 'maximum', 'max', 'howmany', 'quota', 'exceed',
        'exceeded', 'cap', 'restriction', 'unlimited'] }
  ];

  /* Chat shorthand → plain English. These are the forms people actually
     type into a search box, and the reason "idk how 2 post pics" has to
     find the media article instead of nothing. */
  var ABBREV = {
    idk: '', dunno: '', idc: '', imo: '', imho: '', tbh: '',
    btw: '', fyi: '', afaik: '', rn: '', asap: '', lol: '', omg: '',
    pls: 'please', plz: 'please', thx: 'thanks', ty: 'thanks', tnx: 'thanks', tysm: 'thanks',
    u: 'you', ur: 'your', yous: 'you', r: 'are', n: 'and', b4: 'before', 2: 'to',
    bc: 'because', bcz: 'because', bcos: 'because', cuz: 'because', coz: 'because',
    msg: 'message', msgs: 'messages', mesg: 'message', dm: 'message',
    pic: 'photo', pics: 'photos', piccy: 'photo', pfp: 'photo', img: 'image', imgs: 'images',
    vid: 'video', vids: 'videos', doc: 'document', docs: 'documents',
    acc: 'account', accs: 'accounts', sub: 'subscriber', subs: 'subscribers',
    ch: 'channel', chs: 'channels', chan: 'channel', tg: 'telegram',
    dl: 'download', prem: 'premium', premmy: 'premium', subscrip: 'subscription',
    w: 'with', wo: 'without', o: 'of', frm: 'from', abt: 'about', wat: 'what',
    hru: 'how are you', wbu: 'what about you', rn1: '',
    info: 'information', adm: 'admin', admins: 'administrators', auth: 'account',
    ppl: 'people', smth: 'something', sth: 'something', nth: 'nothing',
    dont: 'do not', doesnt: 'does not', didnt: 'did not', cant: 'can not',
    cannot: 'can not', wont: 'will not', isnt: 'is not', arent: 'are not',
    wasnt: 'was not', werent: 'were not', hasnt: 'has not', havent: 'have not',
    couldnt: 'could not', shouldnt: 'should not', wouldnt: 'would not'
  };

  /* Multi-word phrases → an intent, checked before single words. */
  var PHRASES = [
    { re: /every\s*(week|day|month|hour|morning|evening|monday|tuesday|wednesday|thursday|friday|saturday|sunday)/, intent: 'schedule', label: 'repeating posts on a schedule' },
    { re: /once\s*a\s*(week|day|month)/, intent: 'schedule', label: 'repeating posts on a schedule' },
    { re: /(every|each)\s+(day|week|month)/, intent: 'schedule', label: 'repeating posts on a schedule' },
    { re: /(not|no|never)\s+(send|sending|sent|post|posted|posting|publish|published|publishing|work|working|appear|appeared)/, intent: 'error', label: 'posts not going out' },
    { re: /(did|does|do)\s*(not|n.t)\s*(send|post|publish|work)/, intent: 'error', label: 'posts not going out' },
    { re: /(my|the)\s*(photo|pic|image|video|media)s?\s*(does|do|is|are)?\s*(not|n.t)?/, intent: null },
    { re: /how\s*(do|to|can|should)/, intent: null },   /* "how do I …" is generic */
    { re: /difference\s*between/, intent: null },
    { re: /(how much|what.*cost|how.*price|price.*plan)/, intent: 'payment', label: 'pricing and plans' },
    { re: /(connect|add|link)\s*(my|a|the)?\s*(own\s*)?(channel|bot)/, intent: 'channel', label: 'connecting something to the bot' },
    { re: /(delete|remove)\s*(all|every)/, intent: 'error', label: 'deleting posts' },
    { re: /(time\s*zone|wrong\s*time|time\s*is\s*wrong)/, intent: 'schedule', label: 'time zone settings' },
    { re: /how\s*many/, intent: 'limits', label: 'plan limits' },
    { re: /(sender|own|my)\s*bot/, intent: 'bot', label: 'sender bots' },
    { re: /(media|photo)\s*storage/, intent: 'media', label: 'media storage' }
  ];

  /* Misspellings we see in real queries → the correctly spelled word. */
  var TYPOS = {
    reccuring: 'recurring', recuring: 'recurring', recurriing: 'recurring', reccurring: 'recurring',
    shedule: 'schedule', sheduled: 'scheduled', sheduel: 'schedule', scheduel: 'schedule',
    scedule: 'schedule', scheduele: 'schedule', schedul: 'schedule', shedul: 'schedule',
    chanel: 'channel', channal: 'channel', channle: 'channel', chanel: 'channel',
    messge: 'message', mesage: 'message', messege: 'message', messgae: 'message',
    recieve: 'receive', recived: 'received', recieved: 'received',
    delet: 'delete', delte: 'delete', delate: 'delete', deleate: 'delete',
    preimum: 'premium', premum: 'premium', peremium: 'premium', premiumm: 'premium',
    refound: 'refund', refun: 'refund', reufnd: 'refund',
    backp: 'backup', bakup: 'backup', backap: 'backup',
    statisitcs: 'statistics', statistcs: 'statistics', statsitics: 'statistics',
    settigns: 'settings', setings: 'settings', sttings: 'settings',
    timezome: 'timezone', timezon: 'timezone', timezome: 'timezone', timeznoe: 'timezone',
    erorr: 'error', eror: 'error', erros: 'errors',
    publsih: 'publish', pulbish: 'publish', pubish: 'publish',
    conected: 'connected', conncet: 'connect', conenct: 'connect',
    evry: 'every', weekli: 'weekly', weak: 'week',
    signture: 'signature', signiture: 'signature', signatue: 'signature',
    foto: 'photo', phot: 'photo', photoo: 'photo', phots: 'photos',
    vidoe: 'video', vidoes: 'videos', vedio: 'video',
    deletee: 'delete', delting: 'deleting', deletd: 'deleted',
    notificaton: 'notification', notifcation: 'notification',
    subscibe: 'subscribe', subscrption: 'subscription'
  };

  /* Synonyms pulled in for ranking even when the query word itself is
     absent from the article body. */
  var SYN = [
    ['sender', 'bot', 'own bot', 'custom bot', 'botfather', 'token', 'newbot'],
    ['schedule', 'scheduled', 'scheduling', 'queue', 'queued', 'post later', 'plan'],
    ['recurring', 'repeat', 'repeating', 'regular', 'auto repost', 'loop'],
    ['timezone', 'time zone', 'utc', 'gmt', 'offset', 'clock', 'local time'],
    ['delete', 'remove', 'cleanup', 'clean up', 'erase', 'trash'],
    ['edit', 'change', 'modify', 'update', 'rename', 'reschedule'],
    ['premium', 'pro', 'paid', 'subscription', 'upgrade', 'plan'],
    ['limit', 'limits', 'cap', 'quota', 'maximum'],
    ['media', 'photo', 'photos', 'video', 'videos', 'image', 'images', 'album', 'gif', 'sticker', 'voice', 'document', 'file', 'poll'],
    ['storage', 'box', 'boxes', 'library', 'media storage'],
    ['channel', 'channels'],
    ['payment', 'pay', 'buy', 'purchase', 'stars', 'invoice', 'refund', 'crypto', 'price', 'pricing', 'cost'],
    ['backup', 'export', 'import', 'restore', 'fsback', 'fspback', 'migrate', 'migration', 'transfer', 'move'],
    ['admin', 'administrators', 'permission', 'permissions', 'rights'],
    ['signature', 'signatures', 'footer'],
    ['language', 'lang', 'english', 'russian', 'translation'],
    ['search', 'find', 'look up', 'filter'],
    ['calendar', 'month view', 'month'],
    ['stats', 'statistics', 'usage', 'counter', 'analytics', 'views'],
    ['error', 'errors', 'problem', 'problems', 'issue', 'not working', 'fails', 'failed', 'stuck', 'fix', 'troubleshoot'],
    ['late', 'delay', 'delayed', 'not posted', 'missing', 'skipped'],
    ['referral', 'invite', 'friends', 'bonus', 'promo', 'promocode', 'coupon', 'free days'],
    ['account', 'start', 'begin', 'setup', 'onboarding', 'getting started'],
    ['cancel', 'stop', 'pause'],
    ['post', 'posts', 'posting', 'publish', 'publishing', 'send', 'sending', 'message', 'messages'],
    ['feedback', 'support', 'contact', 'ticket'],
    ['auto', 'automatically', 'automatic', 'autopilot'],
    ['duplicate', 'duplicates', 'copy', 'copies', 'twice', 'double'],
    ['pause', 'stop', 'hold', 'freeze']
  ];
  function synth(w) {
    for (var i = 0; i < SYN.length; i++) if (SYN[i].indexOf(w) !== -1) return SYN[i];
    return [w];
  }

  /* ---------- normalizer ---------- */
  var CONTRACTIONS = [
    [/\b(what|that|it|there|here|he|she|who|where|how|when|why|this|one|everyone|someone|nobody)'s\b/g, '$1 is'],
    [/\bi'm\b/g, 'i am'], [/\bwe're\b/g, 'we are'], [/\byou're\b/g, 'you are'],
    [/\bthey're\b/g, 'they are'], [/\bhe's\b/g, 'he is'], [/\bshe's\b/g, 'she is'],
    [/\bi've\b/g, 'i have'], [/\bwe've\b/g, 'we have'], [/\byou've\b/g, 'you have'],
    [/\bthey've\b/g, 'they have'],
    [/\bi'll\b/g, 'i will'], [/\bwe'll\b/g, 'we will'], [/\byou'll\b/g, 'you will'],
    [/\bthey'll\b/g, 'they will'], [/\bit'll\b/g, 'it will'],
    [/\bi'd\b/g, 'i would'], [/\bwe'd\b/g, 'we would'], [/\byou'd\b/g, 'you would'],
    [/\bthey'd\b/g, 'they would'],
    [/\blet's\b/g, 'let us'], [/\bcan't\b/g, 'can not'], [/\bcannot\b/g, 'can not'],
    [/\bwon't\b/g, 'will not'], [/\bshan't\b/g, 'shall not'],
    [/\bain't\b/g, 'is not'],
    [/\b(did|do|does|is|are|was|were|has|have|could|should|would|must|need|might)n't\b/g, '$1 not']
  ];

  function normalize(q) {
    var s = String(q == null ? '' : q)
      .toLowerCase()
      .replace(/[\u2018\u2019\u02bc\u2032]/g, "'")
      .replace(/[\u201c\u201d]/g, '"')
      .replace(/\s+/g, ' ')
      .trim();
    for (var i = 0; i < CONTRACTIONS.length; i++) s = s.replace(CONTRACTIONS[i][0], CONTRACTIONS[i][1]);
    /* standalone abbreviations (bounded by non-letters) */
    s = s.replace(/(^|[^a-z0-9])([a-z0-9]+)(?=$|[^a-z0-9])/g, function (m, pre, word) {
      if (ABBREV.hasOwnProperty(word)) {
        var rep = ABBREV[word];
        return pre + (rep ? ' ' + rep + ' ' : ' ');
      }
      if (TYPOS.hasOwnProperty(word)) return pre + ' ' + TYPOS[word] + ' ';
      return m;
    });
    s = s.replace(/[^a-z0-9\s'+-]/g, ' ');
    return s.replace(/\s+/g, ' ').trim();
  }

  /* light stemmer: enough for English nouns/verbs in a search box */
  function stem(w) {
    if (w.length <= 3) return w;
    if (/(ss|us|is)$/.test(w)) return w;
    if (/ies$/.test(w) && w.length > 4) return w.slice(0, -3) + 'y';
    if (/(ches|shes|xes|sses|zes)$/.test(w)) return w.slice(0, -2);
    if (/s$/.test(w) && !/ss$/.test(w)) return w.slice(0, -1);
    if (/ing$/.test(w) && w.length > 5) return w.slice(0, -3);
    if (/edly$/.test(w)) return w.slice(0, -4);
    if (/ed$/.test(w) && w.length > 4) return w.slice(0, -2);
    if (/ly$/.test(w) && w.length > 5) return w.slice(0, -2);
    return w;
  }

  function tokenize(q) {
    var norm = normalize(q);
    var raw = norm.split(/\s+/).filter(Boolean);
    var out = [];
    raw.forEach(function (w) {
      if (STOP[w] || NEGATIONS[w]) return;
      var s = stem(w);
      if (s && out.indexOf(s) === -1) out.push(s);
    });
    return out;
  }

  /* raw words incl. negations — used for error-query detection */
  function rawTokens(q) {
    return normalize(q).split(/\s+/).filter(Boolean);
  }

  /* ---------- fuzzy helpers ---------- */
  function lev(a, b, max) {
    if (a === b) return 0;
    if (Math.abs(a.length - b.length) > max) return max + 1;
    var m = a.length, n = b.length;
    if (!m) return n; if (!n) return m;
    var prev = new Array(n + 1), cur = new Array(n + 1);
    for (var j = 0; j <= n; j++) prev[j] = j;
    for (var i = 1; i <= m; i++) {
      cur[0] = i;
      var best = cur[0];
      for (var k = 1; k <= n; k++) {
        var c = a.charCodeAt(i - 1) === b.charCodeAt(k - 1) ? 0 : 1;
        cur[k] = Math.min(prev[k] + 1, cur[k - 1] + 1, prev[k - 1] + c);
        if (cur[k] < best) best = cur[k];
      }
      if (best > max) return max + 1;
      for (var t = 0; t <= n; t++) prev[t] = cur[t];
    }
    return prev[n];
  }

  /* Dice coefficient on character bigrams — cheap, robust typo tolerance
     for longer words ("schedulng" vs "scheduling"). */
  function dice(a, b) {
    if (a === b) return 1;
    if (a.length < 3 || b.length < 3) return 0;
    var map = {}, i, g;
    for (i = 0; i < a.length - 1; i++) { g = a.substr(i, 2); map[g] = (map[g] || 0) + 1; }
    var hit = 0;
    for (i = 0; i < b.length - 1; i++) {
      g = b.substr(i, 2);
      if (map[g]) { map[g]--; hit++; }
    }
    return (2 * hit) / (a.length + b.length - 2);
  }

  function near(w, target) {
    if (!w || !target) return 0;
    if (w === target) return 1;
    var min = Math.min(w.length, target.length);
    if (min >= 4 && (target.indexOf(w) === 0 || w.indexOf(target) === 0) &&
        Math.abs(w.length - target.length) <= 3) return 0.9;
    var maxD = target.length >= 8 ? 2 : 1;
    if (lev(w, target, maxD) <= maxD) return 0.75;
    if (min >= 5 && dice(w, target) >= 0.72) return 0.6;
    return 0;
  }

  /* ---------- query interpretation ---------- */
  function resolveWord(w) {
    var intents = [];
    var base = TYPOS[w] || w;
    for (var i = 0; i < INTENTS.length; i++) {
      var words = INTENTS[i].words;
      for (var j = 0; j < words.length; j++) {
        var t = words[j];
        if (base === t) { intents.push(INTENTS[i]); break; }
        if (t.indexOf(base) === 0 && base.length >= 4 && t.length - base.length <= 4) { intents.push(INTENTS[i]); break; }
        /* distance 1 for short words, 2 for long ones; the first letter must
           match, or "cancel" fuzzy-matches "channel" */
        var maxD = t.length >= 8 || base.length >= 8 ? 2 : 1;
        if (base.length >= 5 && base.charAt(0) === t.charAt(0) &&
            lev(base, t, maxD) <= maxD) { intents.push(INTENTS[i]); break; }
      }
    }
    return { word: base, intents: intents };
  }

  function interpret(q) {
    var low = normalize(q);
    var tokens = tokenize(q);
    var negatives = rawTokens(q).filter(function (w) { return NEGATIONS[w]; });
    var phraseLabel = null, forced = {};
    PHRASES.forEach(function (p) {
      if (p.intent && p.re.test(low)) {
        forced[p.intent] = true;
        if (!phraseLabel) phraseLabel = p.label;
      }
    });

    /* "post doesn't work" → error intent even though the phrase split into
       words the topic lexicons would otherwise read as scheduling. */
    if (negatives.length && /(post|send|schedul|publish|work|photo|video|channel)/.test(low)) {
      forced.error = true;
      if (!phraseLabel) phraseLabel = 'posts not going out';
    }

    var words = [], intents = {}, hits = {};
    tokens.forEach(function (w) {
      var r = resolveWord(w);
      if (!r || !r.word) return;
      if (words.indexOf(r.word) === -1) words.push(r.word);
      r.intents.forEach(function (it) {
        intents[it.id] = it;
        hits[it.id] = (hits[it.id] || 0) + 1;
      });
    });
    Object.keys(forced).forEach(function (id) {
      for (var i = 0; i < INTENTS.length; i++) if (INTENTS[i].id === id) { intents[id] = INTENTS[i]; break; }
      hits[id] = (hits[id] || 0) + 2;
    });
    var list = Object.keys(intents).map(function (k) { return intents[k]; });
    /* the label should name the topic the query talked about MOST, not just
       whichever intent happened to be first in the lexicon */
    var best = null, bestN = 0;
    Object.keys(hits).forEach(function (id) {
      if (hits[id] > bestN) { bestN = hits[id]; best = id; }
    });
    var label = phraseLabel || (best && intents[best] ? intents[best].label : null);
    /* "what's the limit" must read as limits, not as a billing question */
    if (/\blimit|how\s*many|quota|maximum/.test(low) && intents.limits) label = intents.limits.label;
    return { words: words, intents: list, label: label, negative: negatives.length > 0, raw: String(q || '').trim() };
  }

  /* ---------- document index ---------- */
  /* Prepared once per docs array (help list, blog list): stems, token set,
     lowercased text. Keeps every keystroke light even on 400 articles. */
  var prepared = typeof WeakMap === 'function' ? new WeakMap() : null;

  function prepDoc(d) {
    var t = normalize(d.t || d.title || '');
    var desc = normalize(d.d || d.description || '');
    var faq = normalize(d.f || '') + ' ' + normalize((d.faqQ || '') + ' ' + (d.faqA || ''));
    var body = normalize(d.b || d.body || '');
    var tTok = t.split(/\s+/).filter(Boolean).map(stem);
    var bTok = body.split(/\s+/).filter(Boolean).map(stem);
    var descTok = desc.split(/\s+/).filter(Boolean).map(stem);
    var faqTok = faq.split(/\s+/).filter(Boolean).map(stem);
    return {
      doc: d, t: t, d: desc, f: faq, b: body,
      tTok: tTok, bTok: bTok, descTok: descTok, faqTok: faqTok,
      tSet: toSet(tTok), descSet: toSet(descTok), faqSet: toSet(faqTok), bSet: toSet(bTok),
      intent: d.intent || d.i || d.c || ''
    };
  }
  function toSet(arr) {
    var o = Object.create(null);
    for (var i = 0; i < arr.length; i++) o[arr[i]] = 1;
    return o;
  }
  function prepare(docs) {
    if (prepared) {
      var hit = prepared.get(docs);
      if (hit && hit.length === docs.length) return hit;
    }
    var list = docs.map(prepDoc);
    if (prepared) prepared.set(docs, list);
    return list;
  }

  /* how strongly one query word matches a document */
  function wordScore(w, p) {
    var s = 0;
    if (p.tSet[w]) s = Math.max(s, 130);
    else {
      for (var i = 0; i < p.tTok.length; i++) {
        var r = near(w, p.tTok[i]);
        if (r) { s = Math.max(s, r >= 0.9 ? 90 : (r >= 0.75 ? 55 : 38)); break; }
      }
    }
    if (p.descSet[w]) s = Math.max(s, 42);
    if (p.faqSet[w]) s = Math.max(s, 34);
    if (p.bSet[w]) s = Math.max(s, 20);
    if (!s) {
      /* synonym coverage: the query word itself may be a synonym of what
         the article says ("pics" → photo) */
      var set = synth(w);
      for (var j = 0; j < set.length; j++) {
        var syn = stem(set[j]);
        if (p.tSet[syn]) { s = Math.max(s, 48); break; }
        if (p.descSet[syn] || p.faqSet[syn]) { s = Math.max(s, 22); break; }
        if (p.bSet[syn]) { s = Math.max(s, 14); break; }
      }
    }
    return s;
  }

  var CAT_INTENT = {
    scheduling: 'schedule', recurring: 'schedule', timezone: 'schedule', calendar: 'schedule',
    media: 'media', media_storage: 'media', storage: 'media',
    channels: 'channel', bots: 'bot',
    premium: 'payment', payment: 'payment', legal: 'payment', referral: 'payment',
    data: 'backup', backup: 'backup', export: 'backup', import: 'backup',
    statistics: 'stats', errors: 'error', faq: '', misc: '',
    start: 'account', getting_started: 'account', privacy: 'account', config: 'account',
    feedback: 'feedback', contact: 'feedback',
    formatting: 'formatting', language: 'formatting', tips: 'formatting',
    limits: 'limits', tools: 'schedule', commands: 'schedule', admins: 'channel'
  };

  /* scoreAll(q, docs) → ranked [{doc, score, ex}]. */
  function scoreAll(q, docs) {
    if (!docs || !docs.length) return [];
    var ex = interpret(q);
    var low = normalize(q);
    var words = ex.words.slice();
    var hadWords = words.length > 0;
    var phrase = low.replace(/\s+/g, ' ');
    var want = {};
    ex.intents.forEach(function (it) { want[it.id] = true; });
    var asksLimit = /how\s*many|how\s*much|\blimit|maximum|quota/.test(low);
    /* "how many posts can I schedule?" is a limits question, not a request
       for the scheduling guide: the topic words would otherwise outvote
       the limit article that actually answers it. */
    if (/how\s*many/.test(low)) {
      var keep = words.filter(function (w) { return !/^(post|schedule|schedul|message|recurr|send)/.test(w); });
      if (keep.length !== words.length) words = keep;
    }
    if (!words.length && !hadWords) {
      /* nothing but filler: fall back to a literal substring search so a
         one-word query like "premium" or "delete" still answers */
      words = tokenize(q);
    }

    var prep = prepare(docs);
    /* every doc counts toward IDF: a word that appears everywhere ("post")
       decides less than one that appears in 3 articles ("botfather") */
    var df = Object.create(null);
    prep.forEach(function (p) {
      words.forEach(function (w) { if (p.bSet[w] || p.tSet[w]) df[w] = (df[w] || 0) + 1; });
    });
    var N = prep.length;

    var scored = prep.map(function (p) {
      var s = 0;

      /* exact phrase — strongest single signal */
      if (phrase.length > 2) {
        if (p.t.indexOf(phrase) !== -1) s += 170;
        else if (p.d.indexOf(phrase) !== -1) s += 70;
        else if (p.f.indexOf(phrase) !== -1) s += 55;
        else if (p.b.indexOf(phrase) !== -1) s += 32;
      }

      /* intent fit — the article is filed under the topic the query pulls */
      var di = CAT_INTENT[p.intent] || CAT_INTENT[p.doc.c] || p.intent || '';
      if (want[di]) s += 60;
      if (asksLimit && di === 'limits') s += 70;
      if (asksLimit && /limit|plan|free/.test(p.t)) s += 50;
      /* A problem query should rank the troubleshooting article above the
         happy-path guide for the same feature: "my photos won't upload"
         wants Media Errors, not "Adding Photos & Videos". */
      if (ex.negative) s += (di === 'error') ? 100 : -40;

      var matched = 0;
      words.forEach(function (w) {
        var ws = wordScore(w, p);
        if (ws) {
          /* IDF weighting: 1.0 for a word in every doc, up to ~2.4 for rare */
          var idf = 1 + Math.log(1 + N / (1 + (df[w] || 1)));
          s += ws * (0.55 + Math.min(idf, 2.4) * 0.45);
          matched++;
        } else {
          s -= 26;
        }
      });

      /* every query word present somewhere in the article: strong bonus */
      if (words.length > 1 && matched === words.length) s += 40;
      if (words.length > 1 && matched === 0) s -= 60;

      /* bigrams ("sender bot", "time zone", "delete all") in title/body */
      var toks = phrase.split(/\s+/);
      for (var i = 0; i < toks.length - 1; i++) {
        var bg = toks[i] + ' ' + toks[i + 1];
        if (p.t.indexOf(bg) !== -1) s += 90;
        else if (p.b.indexOf(bg) !== -1) s += 26;
      }

      /* error queries should prefer troubleshooting articles, not the
         happy-path guide of the same feature */
      if (ex.negative && /error|problem|fix|not|fail|down|stuck|wrong|troubleshoot|didn.t|not sent/.test(p.t + ' ' + p.d)) s += 55;

      /* a short title that is mostly the query is more on-point than a
         long article that mentions it once in passing */
      if (words.length && p.tTok.length) {
        var titleHit = 0;
        words.forEach(function (w) { if (p.tSet[w]) titleHit++; });
        if (titleHit) s += (titleHit / Math.max(words.length, 1)) * 26;
      }

      return { doc: p.doc, score: Math.round(s), ex: ex };
    });

    return scored.filter(function (x) { return x.score > 0; })
      .sort(function (a, b) { return b.score - a.score; });
  }

  window.HelpAI = {
    interpret: interpret,
    scoreAll: scoreAll,
    tokenize: tokenize,
    normalize: normalize,
    stem: stem,
    lev: lev,
    dice: dice
  };
})();
