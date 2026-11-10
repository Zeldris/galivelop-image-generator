/* «Sistema de logo» (taller de marca, D25/D40) dentro de la pestaña Marca: el camino que hace `gimg brand` desde la
   interfaz, sobre la API local `…/brand` (docs/api.md). Cada paso deja su copia en el taller de la marca
   (`<datos>/projects/<p>/brand/<slug>/`) y nunca toca el intento de origen; cada paso se repite con otros parámetros.
   0 nombre y talleres · 1 origen (perfil → pedido → intento) · 2 quitar fondo · 3 pasar a SVG · 4 wordmark · 5 lockups ·
   6 guardar. Un paso que depende de otro queda deshabilitado con su motivo escrito al lado hasta que exista la pieza.
   Las llamadas tardan segundos: el botón dice «trabajando…» y todos se deshabilitan mientras (la API sirve una
   tarea pesada a la vez: `api.heavy_busy` se explica aparte). El resultado de cada paso va en una región `aria-live`. */

import { h, replace, when } from '../dom.js';
import { t } from '../i18n.js';
import { api, paths, describeError, ApiError } from '../api.js';
import { parse } from '../router.js';
import { toastError, toastOk } from './toast.js';
import { confirmAction } from './confirm.js';
import { imageVersion } from './attempt-util.js';

const PIECES = ['emblema-alpha.png', 'emblema.svg', 'emblema-mono.svg', 'wordmark.svg', 'lockup-h.svg', 'lockup-v.svg'];
const SIZES = [16, 32, 64, 128];
const RANK = { candidate: 1, new: 2, discarded: 3 };

/** El slug que la API saca del nombre (acentos fuera, ASCII y guiones). La lista de talleres corrige lo que difiera. */
export const slugOf = (name) => String(name || '').normalize('NFKD').replace(/[̀-ͯ]/g, '').toLowerCase()
  .replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');

const k = (key, params) => t(`ui.brand.shop.${key}`, params);

export function brandWorkshop(project, cfg) {
  const brand = cfg.brand || {};
  const profiles = Object.keys(cfg.profiles || {});
  const fonts = [...new Set(Object.values(cfg.profiles || {}).flatMap((p) => (p.compose && p.compose.fonts) || []))];
  const state = { slug: '', files: new Set(), shops: [], source: null, busy: null, v: String(Date.now()), transparent: null, last: {} };
  const actions = [];
  let nameInput; let sourceNote; let shopsHost;

  /* ---- piezas de interfaz ---- */
  const field = (id, label, input, hint) => h('div.field', {}, h('label', { for: id }, label), input, hint ? h('span.hint', { id: `${id}-hint` }, hint) : null);
  const num = (id, value, attrs = {}) => h('input', { id, type: 'number', value, inputmode: 'decimal', ...attrs });
  const numOf = (input, fallback) => (input.value.trim() === '' || !Number.isFinite(Number(input.value)) ? fallback : Number(input.value));
  const live = () => h('div.shop-result', { aria: { live: 'polite', atomic: 'true' } });
  const has = (key) => state.files.has(key);
  const url = (key) => paths.brandFile(project, state.slug, key, state.v);
  const validName = () => state.slug !== '';

  /** Un botón de paso: `need()` devuelve el motivo por el que no puede ir (o null); `run()` hace la llamada. */
  function action(label, need, run, host, { primary = false } = {}) {
    const hint = h('span.hint.shop-why');
    const btn = h(primary ? 'button.btn.btn-primary' : 'button.btn', { type: 'button' });
    const a = { label, need, run, host, btn, hint };
    btn.addEventListener('click', () => exec(a));
    actions.push(a);
    return h('span.shop-action', {}, btn, hint);
  }

  function refresh() {
    for (const a of actions) {
      const why = a.need();
      const mine = state.busy === a;
      a.btn.disabled = Boolean(state.busy) || Boolean(why);
      a.btn.setAttribute('aria-busy', mine ? 'true' : 'false');
      replace(a.btn, mine ? [h('span.spin', { aria: { hidden: 'true' } }), ' ', k('working')] : a.label);
      a.hint.textContent = state.busy ? '' : (why || '');
    }
  }

  const explain = (e) => (e instanceof ApiError && e.code === 'api.heavy_busy' ? k('busy') : describeError(e, t));

  async function exec(a) {
    if (state.busy || a.need()) return;
    state.busy = a;
    replace(a.host, h('p.hint', {}, k('working')));
    refresh();
    try { await a.run(); } catch (e) {
      replace(a.host, h('p.notice.notice-bad', { role: 'alert' }, t('ui.brand.shop.failed'), ' ', explain(e)));
      toastError(explain(e));
    } finally {
      state.busy = null;
      refresh();
    }
  }

  const done = (host, text, ...more) => replace(host, h('p.notice.notice-ok', {}, h('span.chip.chip-ok', {}, t('ui.brand.shop.done')), ' ', text), ...more);

  /** Tras un paso: el taller manda (qué piezas hay, con qué slug), y se repintan las vistas con otra marca de caché. */
  async function reload() {
    state.v = String(Date.now());
    let list = [];
    try { list = await api.brandList(project); } catch { list = state.shops; }
    state.shops = Array.isArray(list) ? list : [];
    if (state.slug && !state.shops.some((s) => s.slug === state.slug) && state.shops.length) {
      const newest = state.shops.slice().sort((a, b) => b.modified - a.modified)[0]; // el nombre dio otro slug que el de aquí
      state.slug = newest.slug;
    }
    const shop = state.shops.find((s) => s.slug === state.slug);
    state.files = new Set(shop ? shop.files : []);
    paintShops();
    paintAll();
    refresh();
  }

  /* ---- 0 · nombre y talleres ---- */
  nameInput = h('input', { id: 'shop-name', type: 'text', maxlength: 60, value: (cfg.name || project), autocomplete: 'off', aria: { describedby: 'shop-name-hint' } });
  state.slug = slugOf(nameInput.value);
  shopsHost = h('div.row', { aria: { live: 'polite' } });
  nameInput.addEventListener('input', () => { state.slug = slugOf(nameInput.value); syncText(); refresh(); });
  nameInput.addEventListener('change', () => {
    state.slug = slugOf(nameInput.value);
    const shop = state.shops.find((s) => s.slug === state.slug);
    state.files = new Set(shop ? shop.files : []);
    state.transparent = null;
    paintAll();
    refresh();
  });
  const step0 = h('div.stack', {},
    h('div.field', {}, h('label', { for: 'shop-name' }, k('name')), nameInput,
      h('span.hint', { id: 'shop-name-hint' }, k('nameHint'))),
    h('div.field', {}, h('span.label', {}, k('shops')), shopsHost));

  function paintShops() {
    replace(shopsHost, state.shops.length ? state.shops.map((s) => h('button.btn.btn-toggle', {
      type: 'button', aria: { pressed: s.slug === state.slug ? 'true' : 'false' },
      title: s.modified ? when(new Date(s.modified * 1000).toISOString()) : null,
      onclick: () => { nameInput.value = s.slug; nameInput.dispatchEvent(new Event('change')); },
    }, `${s.slug} · ${k('pieces', { n: PIECES.filter((x) => s.files.includes(x)).length, total: PIECES.length })}`)) : h('span.hint', {}, k('noShops')));
  }

  /* ---- 1 · origen: perfil → pedido → intento ---- */
  const profileSel = h('select', { id: 'shop-profile' }, profiles.map((p) => h('option', { value: p }, p)));
  const orderSel = h('select', { id: 'shop-order', disabled: true });
  const attemptsHost = h('div.shop-attempts', { role: 'radiogroup', aria: { label: k('attempt') } });
  sourceNote = h('p.hint', { aria: { live: 'polite' } });

  function setSource(src) {
    state.source = src;
    sourceNote.textContent = src ? k('sourceIs', { profile: src.profile, key: src.key, attempt: `q${src.attempt}` }) : k('sourceNone');
    refresh();
  }

  async function loadOrders(profile, wantKey) {
    replace(orderSel, h('option', { value: '' }, t('ui.loading')));
    orderSel.disabled = true;
    replace(attemptsHost);
    let list = [];
    try { list = await api.orders(project, { profile }); } catch (e) { replace(attemptsHost, h('p.notice.notice-bad', { role: 'alert' }, describeError(e, t))); return; }
    list = (Array.isArray(list) ? list : (list && list.orders) || []).filter((o) => (o.attempts || []).some((a) => a.image))
      .sort((a, b) => (b.chosen !== null) - (a.chosen !== null) || String(b.updatedAt || '').localeCompare(String(a.updatedAt || '')));
    replace(orderSel, h('option', { value: '' }, list.length ? k('pickOrder') : k('noOrders')),
      list.map((o) => h('option', { value: o.key, selected: o.key === wantKey }, o.chosen !== null ? k('orderChosen', { key: o.key, attempt: `q${o.chosen}` }) : o.key)));
    orderSel.disabled = !list.length;
    if (wantKey && list.some((o) => o.key === wantKey)) await loadAttempts(profile, wantKey);
  }

  async function loadAttempts(profile, key, wantId) {
    replace(attemptsHost, h('p.hint', {}, t('ui.loading')));
    let order;
    try { order = await api.order(project, profile, key); } catch (e) { replace(attemptsHost, h('p.notice.notice-bad', { role: 'alert' }, describeError(e, t))); return; }
    const list = ((order && order.attempts) || []).filter((a) => a.image || a.raw)
      .sort((a, b) => (order.chosen === b.id) - (order.chosen === a.id) || (RANK[a.state] || 2) - (RANK[b.state] || 2) || a.id - b.id);
    replace(attemptsHost, list.length ? list.map((a) => {
      const label = order.chosen === a.id ? t('ui.state.chosen') : t(`ui.state.${a.state || 'new'}`);
      const input = h('input', { type: 'radio', name: 'shop-attempt', value: String(a.id), checked: a.id === wantId, aria: { label: `q${a.id}, ${label}` },
        onchange: () => setSource({ profile, key, attempt: a.id }) });
      return h('label.attempt-pick', {}, input,
        h('img', { src: paths.image(project, profile, key, a.id, { v: imageVersion(a) }), alt: '', loading: 'lazy' }),
        h('span', {}, `q${a.id} · ${label}`));
    }) : h('p.hint', {}, k('noAttempts')));
    if (wantId !== undefined && list.some((a) => a.id === wantId)) setSource({ profile, key, attempt: wantId });
  }

  profileSel.addEventListener('change', () => { setSource(null); loadOrders(profileSel.value); });
  orderSel.addEventListener('change', () => { setSource(null); if (orderSel.value) loadAttempts(profileSel.value, orderSel.value); else replace(attemptsHost); });

  const step1 = h('div.stack', {},
    profiles.length ? h('div.cols-2', {}, field('shop-profile', k('profile'), profileSel), field('shop-order', k('order'), orderSel)) : h('p.hint', {}, k('noProfiles')),
    attemptsHost, sourceNote);

  /* ---- 2 · quitar fondo ---- */
  const matteOut = live();
  const tol = num('shop-tol', 30, { min: 0, max: 255, step: 1 });
  const soft = num('shop-soft', 80, { min: 0, max: 255, step: 1 });
  const border = num('shop-border', 6, { min: 0, max: 64, step: 1 });
  const grow = num('shop-grow', 3, { min: 0, max: 32, step: 1 });
  const matteView = h('div.stack');
  const step2 = h('div.stack', {},
    h('div.cols-4', {}, field('shop-tol', k('tol'), tol, k('tolHint')), field('shop-soft', k('soft'), soft, k('softHint')),
      field('shop-border', k('border'), border, k('borderHint')), field('shop-grow', k('grow'), grow, k('growHint'))),
    action(k('matteGo'), () => (!validName() ? k('needName') : !state.source ? k('needSource') : null), async () => {
      const r = await api.brandMatte(project, { name: nameInput.value, source: state.source, tol: numOf(tol, 30), soft: numOf(soft, 80), border: numOf(border, 6), grow: numOf(grow, 3) });
      state.transparent = r && Number.isFinite(r.transparent) ? r.transparent : null;
      await reload();
      done(matteOut, state.transparent === null ? k('matteDone') : k('matteDoneAt', { pct: (state.transparent * 100).toFixed(1) }));
    }, matteOut, { primary: true }),
    matteOut, matteView);

  const tile = (src, kind, size) => h('figure.shop-tile', {}, h('div.shop-bg', { class: `shop-bg-${kind}` }, h('img.shop-img', { src, alt: '', ...(size ? { width: size, height: size } : {}) })),
    h('figcaption.hint', {}, kind === 'light' ? k('onLight') : k('onDark')));

  function paintMatte() {
    replace(matteView, has('emblema-alpha.png')
      ? [h('div.shop-tiles', {}, tile(url('emblema-alpha.png'), 'light'), tile(url('emblema-alpha.png'), 'dark')),
        state.transparent === null ? null : h('p', {}, k('transparentPct', { pct: (state.transparent * 100).toFixed(1) }))]
      : h('p.hint', {}, k('noPiece')));
  }

  /* ---- 3 · pasar a SVG ---- */
  const traceOut = live();
  const colorSrc = h('select', { id: 'shop-colorsrc', aria: { describedby: 'shop-colorsrc-hint' } },
    h('option', { value: 'n' }, k('colorsN')),
    h('option', { value: 'palette', disabled: !(brand.palette || []).length }, (brand.palette || []).length ? k('colorsPalette', { n: brand.palette.length }) : k('colorsNoPalette')));
  const colorsN = num('shop-colors', '', { min: 1, max: 16, step: 1, placeholder: k('auto') });
  const dpTol = num('shop-dptol', 1.2, { min: 0, max: 10, step: 0.1 });
  const island = num('shop-island', 12, { min: 0, max: 10000, step: 1 });
  const traceView = h('div.stack');
  const needAlpha = () => (!validName() ? k('needName') : !has('emblema-alpha.png') ? k('needMatte') : null);
  const trace = (mode) => async () => {
    const body = { name: nameInput.value, mode, dp_tol: numOf(dpTol, 1.2), min_island: numOf(island, 12) };
    if (mode === 'color') {
      if (colorSrc.value === 'palette') body.usePalette = true;
      else if (colorsN.value.trim() !== '') body.colors = numOf(colorsN, undefined);
    }
    const r = await api.brandTrace(project, body);
    await reload();
    done(traceOut, k('traceDone', { mode: k(`mode.${mode}`), paths: r && r.paths !== undefined ? r.paths : '?' }));
  };
  const step3 = h('div.stack', {},
    h('div.cols-4', {}, field('shop-colorsrc', k('colorsFrom'), colorSrc), field('shop-colors', k('colors'), colorsN, k('colorsHint')),
      field('shop-dptol', k('dpTol'), dpTol, k('dpTolHint')), field('shop-island', k('island'), island, k('islandHint'))),
    h('div.row', {}, action(k('traceColor'), needAlpha, trace('color'), traceOut, { primary: true }), action(k('traceMono'), needAlpha, trace('mono'), traceOut)),
    traceOut, traceView);
  colorSrc.addEventListener('change', () => { colorsN.disabled = colorSrc.value === 'palette'; });

  function paintTrace() {
    const rows = [['emblema.svg', 'color'], ['emblema-mono.svg', 'mono']].filter(([f]) => has(f));
    replace(traceView, rows.length ? rows.map(([f, mode]) => h('div.stack', {}, h('h4', {}, k(`mode.${mode}`)),
      h('div.shop-tiles', {}, SIZES.map((s) => h('figure.shop-tile', {}, h('div.shop-bg.shop-bg-light', {}, h('img.shop-img', { src: url(f), alt: '', width: s, height: s })),
        h('figcaption.hint', {}, `${s} px`)))))) : h('p.hint', {}, k('noPiece')));
  }

  /* ---- 4 · wordmark ---- */
  const wordOut = live();
  let textEdited = false;
  const wText = h('input', { id: 'shop-wtext', type: 'text', maxlength: 100, autocomplete: 'off', value: nameInput.value.toUpperCase() });
  wText.addEventListener('input', () => { textEdited = true; });
  const syncText = () => { if (!textEdited) wText.value = nameInput.value.toUpperCase(); };
  const wFont = h('input', { id: 'shop-wfont', type: 'text', list: 'shop-fonts', value: fonts[0] || '', autocomplete: 'off', aria: { describedby: 'shop-wfont-hint' } });
  wFont.addEventListener('input', refresh);
  const wWeight = num('shop-wweight', 800, { min: 100, max: 900, step: 100 });
  const wSpacing = num('shop-wspacing', 0.12, { min: -0.2, max: 1, step: 0.02 });
  const wordView = h('div.stack');
  const step4 = h('div.stack', {},
    h('div.cols-4', {}, field('shop-wtext', k('wtext'), wText, k('wtextHint')),
      h('div.field', {}, h('label', { for: 'shop-wfont' }, k('wfont')), wFont, h('datalist', { id: 'shop-fonts' }, fonts.map((f) => h('option', { value: f }))),
        h('span.hint', { id: 'shop-wfont-hint' }, fonts.length ? k('wfontHint') : k('wfontNone'))),
      field('shop-wweight', k('wweight'), wWeight), field('shop-wspacing', k('wspacing'), wSpacing, k('wspacingHint'))),
    action(k('wordGo'), () => (!validName() ? k('needName') : !wFont.value.trim() ? k('needFont') : null), async () => {
      const body = { name: nameInput.value, font: wFont.value.trim(), weight: numOf(wWeight, 800), spacing: numOf(wSpacing, 0.12) };
      if (wText.value.trim()) body.text = wText.value.trim();
      const r = await api.brandWordmark(project, body);
      await reload();
      done(wordOut, k('wordDone', { family: (r && r.family) || body.font, paths: r && r.paths !== undefined ? r.paths : '?' }));
    }, wordOut, { primary: true }),
    wordOut, wordView);

  const single = (key, width) => h('figure.shop-tile', {}, h('div.shop-bg.shop-bg-light', {}, h('img.shop-img.shop-wide', { src: url(key), alt: '', ...(width ? { width } : {}) })));
  const paintWord = () => replace(wordView, has('wordmark.svg') ? single('wordmark.svg') : h('p.hint', {}, k('noPiece')));

  /* ---- 5 · lockups ---- */
  const lockOut = live();
  const cap = num('shop-cap', 0.45, { min: 0.05, max: 2, step: 0.05 });
  const gap = num('shop-gap', 0.25, { min: 0, max: 2, step: 0.05 });
  const width = num('shop-width', 1.6, { min: 0.2, max: 10, step: 0.1 });
  const lockView = h('div.stack');
  const needPieces = () => (!validName() ? k('needName') : !has('emblema.svg') ? k('needTrace') : !has('wordmark.svg') ? k('needWord') : null);
  const lockup = (layout) => async () => {
    const r = await api.brandLockup(project, { name: nameInput.value, layout, cap: numOf(cap, 0.45), gap: numOf(gap, 0.25), width: numOf(width, 1.6) });
    await reload();
    done(lockOut, k('lockDone', { layout: k(`layout.${layout}`), paths: r && r.paths !== undefined ? r.paths : '?' }));
  };
  const step5 = h('div.stack', {},
    h('div.cols-3', {}, field('shop-cap', k('cap'), cap, k('capHint')), field('shop-gap', k('gap'), gap, k('gapHint')), field('shop-width', k('width'), width, k('widthHint'))),
    h('div.row', {}, action(k('lockH'), needPieces, lockup('h'), lockOut, { primary: true }), action(k('lockV'), needPieces, lockup('v'), lockOut)),
    lockOut, lockView);

  function paintLock() {
    const shown = [['lockup-h.svg', 'h'], ['lockup-v.svg', 'v']].filter(([f]) => has(f));
    replace(lockView, shown.length ? h('div.shop-tiles', {}, shown.map(([f, l]) => h('div.stack', {}, h('h4', {}, k(`layout.${l}`)), single(f)))) : h('p.hint', {}, k('noPiece')));
  }

  /* ---- 6 · guardar el sistema ---- */
  const saveOut = live();
  const projectDir = Boolean(brand.dir);
  const dest = h('select', { id: 'shop-dest', aria: { describedby: 'shop-dest-hint' } },
    h('option', { value: 'data' }, k('destData')), h('option', { value: 'project', disabled: !projectDir }, projectDir ? k('destProject', { dir: brand.dir }) : k('destProjectOff')));
  const missing = () => PIECES.filter((f) => !has(f));
  const saveCall = (force) => api.brandSave(project, { name: nameInput.value, dest: dest.value, force });
  const step6 = h('div.stack', {},
    field('shop-dest', k('dest'), dest, projectDir ? k('destHint') : k('noBrandDir')),
    action(k('saveGo'), () => (!validName() ? k('needName') : missing().length ? k('needAll', { files: missing().join(', ') }) : null), async () => {
      let r;
      try { r = await saveCall(false); } catch (e) {
        if (!(e instanceof ApiError && e.code === 'brand.exists')) throw e;
        const ok = await confirmAction({ title: k('overwriteTitle'), message: `${e.message} ${k('overwriteAsk')}`, confirmLabel: k('overwriteYes'), opener: () => actions.find((a) => a.host === saveOut).btn });
        if (!ok) { replace(saveOut, h('p.hint', {}, k('saveCancelled'))); return; }
        r = await saveCall(true);
      }
      await reload();
      toastOk(k('saveToast', { dir: r.out_dir }));
      const folder = h('code.mono', {}, r.out_dir);
      done(saveOut, k('saveDone', { n: Object.keys(r.files || {}).length }),
        h('div.row', {}, h('span', {}, k('folder')), folder,
          h('button.btn', { type: 'button', onclick: () => copy(r.out_dir) }, '⎘ ', k('copyPath'))),
        (r.overwritten || []).length ? h('p.hint', {}, k('overwritten', { files: r.overwritten.join(', ') })) : null,
        h('figure.shop-tile', {}, h('div.shop-bg.shop-bg-light', {}, h('img.shop-img.shop-wide', { src: url('contactos.png'), alt: k('contactAlt') })), h('figcaption.hint', {}, k('contact', { w: r.contact_size && r.contact_size[0], h: r.contact_size && r.contact_size[1] }))));
    }, saveOut, { primary: true }),
    saveOut);

  async function copy(text) {
    try { await navigator.clipboard.writeText(text); toastOk(k('copied')); } catch { toastError(k('copyFailed')); }
  }

  /* ---- montaje ---- */
  const paintAll = () => { paintMatte(); paintTrace(); paintWord(); paintLock(); };
  const section = (n, id, title, intro, body) => h('section.shop-step', { aria: { labelledby: `shop-${id}-h` } },
    h('h3', { id: `shop-${id}-h` }, h('span.shop-n', { aria: { hidden: 'true' } }, n), ' ', title), intro ? h('p.hint', {}, intro) : null, body);

  const root = h('section.card.shop', { id: 'brand-shop', aria: { labelledby: 'shop-h' } },
    h('h2', { id: 'shop-h' }, k('title')), h('p.hint', {}, k('intro')),
    section(0, 'name', k('s0'), null, step0), section(1, 'source', k('s1'), k('s1Intro'), step1), section(2, 'matte', k('s2'), k('s2Intro'), step2),
    section(3, 'trace', k('s3'), k('s3Intro'), step3), section(4, 'word', k('s4'), k('s4Intro'), step4), section(5, 'lock', k('s5'), k('s5Intro'), step5),
    section(6, 'save', k('s6'), k('s6Intro'), step6));

  setSource(null);
  paintShops();
  paintAll();
  refresh();
  init();

  async function init() {
    const asked = String(parse().query.src || '').split('|');
    const want = asked.length === 3 && profiles.includes(asked[0]) && /^\d+$/.test(asked[2]) ? { profile: asked[0], key: asked[1], attempt: Number(asked[2]) } : null;
    const first = want ? want.profile : profiles[0];
    if (first) profileSel.value = first;
    await Promise.all([reload(), first ? loadOrders(first, want ? want.key : undefined).then(() => (want ? loadAttemptsFor(want) : null)) : null]);
    if (want) root.scrollIntoView({ block: 'start' });
  }

  async function loadAttemptsFor(want) {
    if (orderSel.value === want.key) await loadAttempts(want.profile, want.key, want.attempt);
  }

  return root;
}
