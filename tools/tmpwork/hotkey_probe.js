/* Behavioral probe for the main-page hotkey stack (scratch, not shipped).
 * Loads the REAL website/scripts/*.js with a minimal DOM stub and asserts
 * the documented dispatch matrix. ASCII stdout only (Win cp1252 console).
 * Run: node tools/tmpwork/hotkey_probe.js  (exit 0 = all pass)
 */
'use strict';
const fs = require('fs');
const vm = require('vm');
const path = require('path');

const ROOT = path.resolve(__dirname, '..', '..');
const SCRIPTS = path.join(ROOT, 'website', 'scripts');
const load = (f) => fs.readFileSync(path.join(SCRIPTS, f), 'utf8');

let pass = 0, fail = 0;
function ok(cond, name) {
  if (cond) { pass++; console.log('PASS  ' + name); }
  else { fail++; console.log('FAIL  ' + name); }
}

/* ---------- tiny DOM stub ---------- */
function makeEnv() {
  const listeners = { document: {}, window: {} };
  const store = {};
  const localStorage = {
    getItem: (k) => (k in store ? store[k] : null),
    setItem: (k, v) => { store[k] = String(v); },
    removeItem: (k) => { delete store[k]; },
  };
  function fakeEl() {
    return {
      nodeType: 1, tagName: 'DIV', isContentEditable: false,
      parentElement: null, children: [],
      _attrs: {}, _clicked: 0,
      classList: { add() {}, remove() {}, toggle() {}, contains() { return false; } },
      style: {},
      click() { this._clicked++; },
      getAttribute(k) { return k in this._attrs ? this._attrs[k] : null; },
      setAttribute(k, v) { this._attrs[k] = String(v); },
      removeAttribute(k) { delete this._attrs[k]; },
      getBoundingClientRect() { return { width: 100, height: 20, top: 0, left: 0 }; },
      matches() { return false; },
      querySelector() { return null; },
      querySelectorAll() { return []; },
      appendChild(c) { this.children.push(c); return c; },
      addEventListener() {},
    };
  }
  const root = fakeEl();
  root.tagName = 'HTML';
  root.getAttribute = (k) => (k in root._attrs ? root._attrs[k] : null);
  const bySel = {};   // selector -> [fakeEl] for querySelectorAll
  const oneSel = {};  // selector -> fakeEl for querySelector
  const doc = {
    readyState: 'complete',
    documentElement: root,
    activeElement: { tagName: 'BODY', isContentEditable: false },
    _listeners: listeners.document,
    addEventListener(t, fn) { (listeners.document[t] = listeners.document[t] || []).push(fn); },
    removeEventListener() {},
    querySelector(sel) {
      if (oneSel[sel]) return oneSel[sel];
      const a = bySel[sel];
      return a && a.length ? a[0] : null;
    },
    querySelectorAll(sel) { return bySel[sel] ? bySel[sel].slice() : []; },
    getElementById() { return null; },
    createElement() { return fakeEl(); },
    body: null,
  };
  doc.body = fakeEl();
  const win = {
    _listeners: listeners.window,
    addEventListener(t, fn) { (listeners.window[t] = listeners.window[t] || []).push(fn); },
    removeEventListener() {},
    matchMedia() { return { matches: false }; },
    getComputedStyle() { return { display: 'block', visibility: 'hidden' === 'x' ? 'hidden' : 'visible' }; },
    innerWidth: 1200, innerHeight: 800, scrollY: 0,
    scrollTo() { win._scrolls.push(Array.from(arguments)); },
    _scrolls: [],
    location: { pathname: '/index.html' },
  };
  const sandbox = {
    window: win, document: doc, localStorage,
    console, CustomEvent: function (t, d) { this.type = t; this.detail = d && d.detail; },
    matchMedia: win.matchMedia, getComputedStyle: win.getComputedStyle,
    location: win.location,
  };
  sandbox.globalThis = sandbox;
  return { listeners, store, localStorage, doc, win, root, bySel, oneSel, sandbox, fakeEl };
}

function fireKey(listeners, over, props) {
  const e = Object.assign(
    { key: '', code: '', shiftKey: false, ctrlKey: false, metaKey: false, altKey: false,
      repeat: false, defaultPrevented: false,
      preventDefault() { this._pd = true; },
      stopPropagation() {}, stopImmediatePropagation() {} },
    props || {});
  (listeners.document.keydown || []).forEach((fn) => fn(e));
  return e;
}

/* ================= hotkeys.js ================= */
(function testHotkeys() {
  console.log('--- hotkeys.js ---');
  const env = makeEnv();
  vm.createContext(env.sandbox);
  // settings.js first (owns FS_KEYS), then hotkeys.js
  vm.runInContext(load('settings.js'), env.sandbox, { filename: 'settings.js' });
  vm.runInContext(load('hotkeys.js'), env.sandbox, { filename: 'hotkeys.js' });

  // register fake controls
  const mk = () => env.fakeEl();
  const cta = mk(), burger = mk(), gear = mk(), blog = mk(), help = mk();
  const billY = mk(), billM = mk();
  const rows = { d: mk(), a: mk(), x: mk(), k: mk() };
  const secs = { 1: mk(), 2: mk(), 3: mk(), 4: mk(), 5: mk() };
  env.bySel['.nav-cta-sm, .nav-cta-m, .nav-cta, .cta-big'] = [cta];
  env.bySel['#navBurger'] = [burger];
  env.bySel['#settingsBtn'] = [gear];
  env.bySel['a.nav-link[href*="blog"], .help-row a[href*="blog"], a[href$="blog/index.html"], a[href$="/blog/"], #navMobile a[href*="blog"], footer a[href$="blog/index.html"]'] = [blog];
  env.bySel['a.nav-link[href*="help"], .site-menu-row, a.gp-row[href*="help"], .help-row a[href*="help"], #navMobile a[href*="help"], footer a[href$="help.html"]'] = [help];
  env.bySel['#billYearly'] = [billY];
  env.bySel['#billMonthly'] = [billM];
  env.oneSel['a[href="#time"]'] = secs[1];
  env.oneSel['a[href="#features"]'] = secs[2];
  env.oneSel['a[href="#how"]'] = secs[3];
  env.oneSel['a[href="#pricing"]'] = secs[4];
  env.oneSel['a[href="#faq"]'] = secs[5];
  env.oneSel['#rowDark'] = rows.d;
  env.oneSel['#rowAnim'] = rows.a;
  env.oneSel['#rowFx'] = rows.x;
  env.oneSel['#rowKeys'] = rows.k;
  const K = (props) => fireKey(env.listeners, env.win, props);
  const clicks = () => cta._clicked + burger._clicked + gear._clicked + blog._clicked +
    help._clicked + billY._clicked + billM._clicked +
    rows.d._clicked + rows.a._clicked + rows.x._clicked + rows.k._clicked +
    secs[1]._clicked + secs[2]._clicked + secs[3]._clicked + secs[4]._clicked + secs[5]._clicked;

  K({ key: 'b', code: 'KeyB' });
  ok(cta._clicked === 1, 'B opens Bot');
  K({ key: 'B', code: 'KeyB', shiftKey: true });
  ok(clicks() === 1, 'Shift+B fires nothing');
  K({ key: 'm', code: 'KeyM' });
  ok(burger._clicked === 1, 'M opens menu');
  K({ key: ',', code: 'Comma' });
  ok(gear._clicked === 1, 'comma opens Settings');
  K({ key: '<', code: 'Comma', shiftKey: true });
  ok(clicks() === 3, 'Shift+, fires nothing');
  K({ key: '1', code: 'Digit1' });
  ok(secs[1]._clicked === 1, '1 goes to section 1');
  K({ key: '!', code: 'Digit1', shiftKey: true });
  ok(clicks() === 4, 'Shift+1 (!) fires nothing (no code fallback)');
  K({ key: 'g', code: 'KeyG' });
  ok(blog._clicked === 1, 'G goes to Blog');
  K({ key: 'h', code: 'KeyH' });
  ok(help._clicked === 1, 'H goes to Help');
  K({ key: 'd', code: 'KeyD' });
  ok(rows.d._clicked === 1, 'D toggles dark');
  K({ key: 'a', code: 'KeyA' });
  ok(rows.a._clicked === 1, 'A toggles animations');
  K({ key: 'x', code: 'KeyX' });
  ok(rows.x._clicked === 1, 'X toggles effects');
  K({ key: 'k', code: 'KeyK' });
  ok(rows.k._clicked === 1, 'K toggles hotkeys switch');
  K({ key: 'K', code: 'KeyK', shiftKey: true });
  ok(rows.k._clicked === 1, 'Shift+K fires nothing');
  K({ key: 'y', code: 'KeyY' });
  ok(billY._clicked === 1, 'Y selects yearly billing');
  K({ key: 'n', code: 'KeyN' });
  ok(billM._clicked === 1, 'N selects monthly billing');
  // RU layout fallback: Cyrillic char + physical code
  K({ key: 'и', code: 'KeyB' });
  ok(cta._clicked === 2, 'RU layout: Cyrillic key + KeyB still opens Bot');
  K({ key: 's', code: 'KeyS' });
  ok(clicks() === 13, 'S on home (no blog search) is a silent no-op');
  // typing guard
  env.doc.activeElement = { tagName: 'INPUT', isContentEditable: false };
  K({ key: 'b', code: 'KeyB' });
  ok(clicks() === 13, 'no fire while typing in INPUT');
  env.doc.activeElement = { tagName: 'BODY', isContentEditable: false };
  // stolen keys (remapped in editor)
  env.sandbox.window.FS_HOTKEYS_STOLEN = ['b'];
  K({ key: 'b', code: 'KeyB' });
  ok(clicks() === 13, 'remapped B stands down in hotkeys.js');
  delete env.sandbox.window.FS_HOTKEYS_STOLEN;
  // modal open / recording guards
  env.oneSel['.hk-overlay.open'] = mk();
  K({ key: 'b', code: 'KeyB' });
  ok(clicks() === 13, 'no fire while editor modal open');
  delete env.oneSel['.hk-overlay.open'];
  env.sandbox.window.FS_HK_RECORDING = true;
  K({ key: 'b', code: 'KeyB' });
  ok(clicks() === 13, 'no fire while recording a binding');
  env.sandbox.window.FS_HK_RECORDING = false;
  // hotkeys switched off: everything dead except K hatch
  env.root._attrs['data-keys'] = 'off';
  K({ key: 'b', code: 'KeyB' });
  ok(clicks() === 13, 'no fire while switched off');
  K({ key: 'k', code: 'KeyK' });
  ok(rows.k._clicked === 2, 'K hatch still toggles switch while off');
  K({ key: 'K', code: 'KeyK', shiftKey: true });
  ok(rows.k._clicked === 2, 'Shift+K hatch stays dead while off');
  delete env.root._attrs['data-keys'];
})();

/* ================= hotkeys-modal registry ================= */
(function testRegistry() {
  console.log('--- hotkeys-modal registry ---');
  const env = makeEnv();
  vm.createContext(env.sandbox);
  vm.runInContext(load('hotkeys-modal.js'), env.sandbox, { filename: 'hotkeys-modal.js' });
  const O = env.sandbox.window.FS_HOTKEYS_OVERRIDE;
  ok(!!O && !!O.registry, 'override API exposed');
  const reg = O.registry;
  ok(O.get('jumpFab') === 'F', 'jumpFab default is F (G freed for Blog)');
  ok(O.get('blog') === 'G', 'blog default stays G');
  const menu = reg.filter((e) => e.id === 'menu')[0];
  ok(menu && menu.mobileOnly === true, 'menu entry is mobileOnly (burger hidden on desktop)');
  // no two entries on overlapping pages share one default key
  const normPage = (p) => (p === 'all' ? ['home', 'help', 'legal', 'blog', 'other'] :
    (p === 'home+legal' ? ['home', 'legal'] : [p]));
  let clash = null;
  for (let i = 0; i < reg.length; i++) {
    for (let j = i + 1; j < reg.length; j++) {
      const a = reg[i], b = reg[j];
      if (String(a.key).toLowerCase() !== String(b.key).toLowerCase()) continue;
      const overlap = normPage(a.page).some((p) => normPage(b.page).indexOf(p) !== -1);
      const bothCapped = a.desktopOnly && b.desktopOnly;
      if (overlap && !(a.mobileOnly || b.mobileOnly) && !bothCapped) { clash = a.id + '/' + b.id; break; }
    }
  }
  ok(!clash, 'no duplicate default keys on overlapping pages' + (clash ? ' (' + clash + ')' : ''));
  // stolen-key derivation: combo/sequence customs free the plain default
  const remapHandlers = env.listeners.window['fs-hotkeys-remap'] || [];
  function setCustom(map) {
    env.localStorage.setItem('fs-hotkey-custom', JSON.stringify(map));
    remapHandlers.forEach((fn) => fn({}));
    return env.sandbox.window.FS_HOTKEYS_STOLEN;
  }
  let s = setCustom({ bot: 'Shift+B' });
  ok(s.indexOf('B') !== -1, 'combo custom steals plain default (bot Shift+B -> B stolen)');
  s = setCustom({ bot: 'O>B' });
  ok(s.indexOf('B') !== -1, 'sequence custom steals plain default (bot O>B -> B stolen)');
  s = setCustom({ bot: 'B' });
  ok(s.indexOf('B') === -1, 'identical re-record keeps default live');
  s = setCustom({});
  ok(s.length === 0, 'no customs -> nothing stolen');
})();

/* ================= scroll-jump.js ================= */
(function testJump() {
  console.log('--- scroll-jump.js ---');
  const env = makeEnv();
  const creations = [];
  function cls() {
    const s = new Set();
    return {
      add(c) { s.add(c); }, remove(c) { s.delete(c); },
      toggle(c, f) { if (f === undefined) { if (s.has(c)) s.delete(c); else s.add(c); } else if (f) s.add(c); else s.delete(c); },
      contains(c) { return s.has(c); },
    };
  }
  function jel() {
    const el = env.fakeEl();
    el.classList = cls();
    el.offsetHeight = 200; el.offsetWidth = 200;
    el._rows = null;
    el.querySelectorAll = function (sel) { return sel === '.gp-row' && this._rows ? this._rows.slice() : []; };
    creations.push(el);
    return el;
  }
  env.doc.createElement = jel;
  env.doc.scrollingElement = { scrollHeight: 2000, clientHeight: 800, addEventListener() {}, removeEventListener() {} };
  env.win.scrollY = 1000;
  env.win.FS_HOTKEYS = { map: [{ key: 'g' }] };
  env.win.FS_HOTKEYS_OVERRIDE = { get(id) { return id === 'jumpFab' ? 'F' : null; } };
  vm.createContext(env.sandbox);
  vm.runInContext(load('scroll-jump.js'), env.sandbox, { filename: 'scroll-jump.js' });
  const menu = creations[1];
  menu._rows = ['top', 'pageup', 'pagedown', 'bottom'].map((kind) => ({
    getAttribute() { return kind; },
    setAttribute() {}, removeAttribute() {},
    querySelector() { return { textContent: '' }; },
  }));
  const J = (props) => fireKey(env.listeners, env.win, props);
  const isOpen = () => menu.classList.contains('open');
  const scrolls = env.win._scrolls;

  J({ key: 'f', code: 'KeyF' });
  ok(isOpen() === true, 'F toggles jump menu open');
  J({ key: 'f', code: 'KeyF' });
  ok(isOpen() === false, 'F toggles jump menu closed');
  J({ key: 'F', code: 'KeyF', shiftKey: true });
  ok(isOpen() === false, 'Shift+F toggles nothing');
  const n0 = scrolls.length;
  J({ key: 'u', code: 'KeyU' });
  ok(scrolls.length === n0 + 1 && scrolls[scrolls.length - 1][0].top === 280, 'U pages up');
  J({ key: 'U', code: 'KeyU', shiftKey: true });
  ok(scrolls.length === n0 + 1, 'Shift+U pages nothing');
  J({ key: 'j', code: 'KeyJ' });
  ok(scrolls[scrolls.length - 1][0].top === 1200, 'J pages down');
  J({ key: 'J', code: 'KeyJ', shiftKey: true });
  ok(scrolls[scrolls.length - 1][0].top === 1200, 'Shift+J pages nothing');
  J({ key: ' ', code: 'Space', shiftKey: true });
  ok(scrolls[scrolls.length - 1][0].top === 0, 'Shift+Space goes to top');
  J({ key: 'Enter', code: 'Enter', shiftKey: true });
  ok(scrolls[scrolls.length - 1][0].top === 1200, 'Shift+Enter goes to end');
  J({ key: 'g', code: 'KeyG' });
  ok(isOpen() === false, 'G stands down while Blog owns it');
  delete env.sandbox.window.FS_HOTKEYS;
  J({ key: 'g', code: 'KeyG' });
  ok(isOpen() === true, 'legacy G toggles menu where Blog is absent');
  J({ key: 'g', code: 'KeyG' });
  ok(isOpen() === false, 'legacy G toggles menu closed');
  env.oneSel['.hk-overlay.open'] = env.fakeEl();
  J({ key: 'f', code: 'KeyF' });
  ok(isOpen() === false, 'no toggle while editor modal open');
  delete env.oneSel['.hk-overlay.open'];
  env.doc.activeElement = { tagName: 'SELECT', isContentEditable: false };
  const n1 = scrolls.length;
  J({ key: 'u', code: 'KeyU' });
  ok(scrolls.length === n1, 'no paging while focused in SELECT');
  env.doc.activeElement = { tagName: 'BODY', isContentEditable: false };
  // remapped single-char jump key is honoured
  env.win.FS_HOTKEYS_OVERRIDE = { get(id) { return id === 'jumpFab' ? 'O' : null; } };
  J({ key: 'o', code: 'KeyO' });
  ok(isOpen() === true, 'remapped single-char jump key (O) toggles menu');
})();

console.log('------------------------------');
console.log('passed ' + pass + ', failed ' + fail);
process.exit(fail ? 1 : 0);
