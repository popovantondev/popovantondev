/* Mini piano for the "About me" pages (about.html, about-de.html, about-ru.html).
   Two octaves C4..B5 in the look of Virtual Piano Arranger (graphite and gold), played with the mouse,
   a finger or the computer keyboard. Sound: nine recordings of the Salamander Grand Piano V3
   (Alexander Holm, CC BY 3.0), the same files the program uses, pitch-shifted between the recorded notes.
   Nothing is requested and no audio context exists before the first key press; own files only.
   Before the recordings have loaded (or if they cannot load) a plain synthesised tone is played. */
(() => {
  'use strict';
  const root = document.getElementById('mini-piano');
  const section = document.getElementById('piano');
  const stringsEl = document.getElementById('piano-strings');
  if (!root || !section || !stringsEl) return;
  const T = JSON.parse(stringsEl.textContent);
  const BASE = 'assets/about-piano/samples/';
  const LOW = 60; // MIDI C4
  const COUNT = 24; // two octaves
  const WHITE_PC = [0, 2, 4, 5, 7, 9, 11];
  const SAMPLES = [['C4', 60], ['Ds4', 63], ['Fs4', 66], ['A4', 69], ['C5', 72], ['Ds5', 75], ['Fs5', 78], ['A5', 81], ['C6', 84]];
  // Tracker-style layout: lower row Z..M with S D G H J for the black keys, upper row Q..U with 2 3 5 6 7.
  const CODES = ['KeyZ', 'KeyS', 'KeyX', 'KeyD', 'KeyC', 'KeyV', 'KeyG', 'KeyB', 'KeyH', 'KeyN', 'KeyJ', 'KeyM',
    'KeyQ', 'Digit2', 'KeyW', 'Digit3', 'KeyE', 'KeyR', 'Digit5', 'KeyT', 'Digit6', 'KeyY', 'Digit7', 'KeyU'];
  const OFFSET_OF = new Map(CODES.map((c, i) => [c, i]));
  const reduced = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ---------- keys ----------
  const whiteCount = 14;
  const wPct = 100 / whiteCount;
  const bPct = wPct * 0.6;
  const board = document.createElement('div');
  board.className = 'pk-board';
  board.setAttribute('role', 'group');
  board.setAttribute('aria-label', T.aria);
  const keys = [];
  let wi = 0;
  for (let off = 0; off < COUNT; off++) {
    const pc = off % 12;
    const white = WHITE_PC.includes(pc);
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'pk ' + (white ? 'pk-white' : 'pk-black');
    b.dataset.off = String(off);
    b.tabIndex = off === 0 ? 0 : -1;
    const name = T.notes[pc] + (4 + Math.floor(off / 12));
    b.setAttribute('aria-label', name);
    if (white) { b.style.left = (wi * wPct) + '%'; b.style.width = wPct + '%'; wi++; }
    else { b.style.left = (wi * wPct - bPct / 2) + '%'; b.style.width = bPct + '%'; }
    const label = document.createElement('span');
    label.className = 'pk-label';
    const code = CODES[off];
    label.textContent = code.replace('Key', '').replace('Digit', '');
    b.append(label);
    if (pc === 0) {
      const mark = document.createElement('span');
      mark.className = 'pk-mark';
      mark.textContent = name;
      b.append(mark);
    }
    board.append(b);
    keys.push({ el: b, label });
  }
  const felt = document.createElement('div');
  felt.className = 'pk-felt';
  felt.setAttribute('aria-hidden', 'true');
  root.replaceChildren(board, felt);
  root.classList.add('is-live');
  if (navigator.keyboard && navigator.keyboard.getLayoutMap) {
    navigator.keyboard.getLayoutMap().then((map) => {
      CODES.forEach((c, i) => { const v = map.get(c); if (v) keys[i].label.textContent = v.toUpperCase(); });
    }).catch(() => {});
  }

  // ---------- status, mute, armed ----------
  const status = section.querySelector('.pk-status');
  const muteBtn = section.querySelector('.pk-mute');
  let muted = reduced; // reduced motion: sound stays off until the visitor switches it on
  const setStatus = (s) => { if (status) status.textContent = s; };
  function paintMute() {
    if (!muteBtn) return;
    muteBtn.setAttribute('aria-pressed', String(!muted));
    muteBtn.textContent = muted ? T.unmute : T.mute;
    if (muted) setStatus(T.silent); else if (!ctx) setStatus(T.idle);
  }
  let armed = false;
  function arm(on) { armed = on; section.classList.toggle('is-armed', on); }

  // ---------- audio ----------
  let ctx = null, master = null, loadState = 'none';
  const buffers = new Map();
  const voices = new Map(); // note offset -> voice
  function ensureAudio() {
    if (ctx) { if (ctx.state === 'suspended') ctx.resume().catch(() => {}); return ctx; }
    const AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) return null;
    try { ctx = new AC(); } catch (e) { return null; }
    master = ctx.createGain();
    master.gain.value = muted ? 0 : 0.8;
    const limiter = ctx.createDynamicsCompressor();
    limiter.threshold.value = -14; limiter.ratio.value = 8; limiter.attack.value = 0.003; limiter.release.value = 0.15;
    master.connect(limiter); limiter.connect(ctx.destination);
    if (ctx.state === 'suspended') ctx.resume().catch(() => {});
    loadSamples();
    return ctx;
  }
  const decode = (data) => new Promise((resolve, reject) => { ctx.decodeAudioData(data, resolve, reject); });
  async function loadSamples() {
    if (loadState !== 'none') return;
    loadState = 'loading';
    if (!muted) setStatus(T.loading);
    try {
      await Promise.all(SAMPLES.map(async ([n]) => {
        const r = await fetch(BASE + n + '.mp3');
        if (!r.ok) throw new Error('sample ' + n);
        buffers.set(n, await decode(await r.arrayBuffer()));
      }));
      loadState = 'ready';
      if (!muted) setStatus(T.ready);
    } catch (e) {
      loadState = 'failed';
      if (!muted) setStatus(T.error);
    }
  }
  function nearest(m) {
    let best = null;
    for (const s of SAMPLES) if (!best || Math.abs(s[1] - m) < Math.abs(best[1] - m)) best = s;
    return best;
  }
  function startVoice(off) {
    const c = ensureAudio();
    if (!c || muted) return null;
    const m = LOW + off, now = c.currentTime;
    const g = c.createGain();
    g.gain.setValueAtTime(0, now);
    g.gain.linearRampToValueAtTime(0.9, now + 0.004);
    g.connect(master);
    const nodes = [];
    const smp = nearest(m);
    const buf = loadState === 'ready' && buffers.get(smp[0]);
    if (buf) {
      const src = c.createBufferSource();
      src.buffer = buf;
      src.playbackRate.value = Math.pow(2, (m - smp[1]) / 12);
      src.connect(g); src.start(now);
      nodes.push(src);
    } else { // simple fallback tone: triangle plus a soft octave, decaying like a struck string
      const f = 440 * Math.pow(2, (m - 69) / 12);
      const a = c.createOscillator(), b = c.createOscillator(), gb = c.createGain();
      a.type = 'triangle'; a.frequency.value = f;
      b.type = 'sine'; b.frequency.value = f * 2; gb.gain.value = 0.25;
      a.connect(g); b.connect(gb); gb.connect(g);
      g.gain.setTargetAtTime(0.0001, now + 0.02, 0.55);
      a.start(now); b.start(now);
      nodes.push(a, b);
    }
    const voice = { g, nodes, at: now };
    nodes[0].onended = () => { try { g.disconnect(); } catch (e) { /* already gone */ } };
    return voice;
  }
  function stopVoice(v, fade) {
    if (!v || !ctx) return;
    const t = ctx.currentTime;
    try {
      v.g.gain.cancelScheduledValues(t);
      v.g.gain.setValueAtTime(Math.max(v.g.gain.value, 0.0001), t);
      v.g.gain.linearRampToValueAtTime(0, t + fade);
      v.nodes.forEach((n) => n.stop(t + fade + 0.02));
    } catch (e) { /* node already stopped */ }
  }

  // ---------- pressing and releasing ----------
  const holders = new Map(); // offset -> Set of sources (pointer id or key code)
  function press(off, source) {
    let set = holders.get(off);
    if (!set) { set = new Set(); holders.set(off, set); }
    const first = set.size === 0;
    set.add(source);
    if (!first) return;
    keys[off].el.classList.add('is-active');
    const old = voices.get(off);
    if (old) stopVoice(old, 0.03);
    if (voices.size >= 18) { // keep the number of voices small
      const oldest = [...voices.entries()].sort((x, y) => x[1].at - y[1].at)[0];
      stopVoice(oldest[1], 0.04); voices.delete(oldest[0]);
    }
    const v = startVoice(off);
    if (v) voices.set(off, v);
  }
  function release(off, source) {
    const set = holders.get(off);
    if (!set || !set.delete(source) || set.size) return;
    holders.delete(off);
    keys[off].el.classList.remove('is-active');
    const v = voices.get(off);
    if (v) { stopVoice(v, 0.28); voices.delete(off); }
  }
  function releaseAll() {
    for (const [off, set] of [...holders]) for (const s of [...set]) release(off, s);
  }

  // ---------- pointer (mouse, touch, pen) ----------
  const active = new Map(); // pointerId -> offset
  const keyAt = (x, y) => {
    const el = document.elementFromPoint(x, y);
    const k = el && el.closest ? el.closest('.pk') : null;
    return k && board.contains(k) ? Number(k.dataset.off) : -1;
  };
  board.addEventListener('pointerdown', (e) => {
    if (e.button > 0) return;
    const off = keyAt(e.clientX, e.clientY);
    if (off < 0) return;
    e.preventDefault();
    arm(true);
    try { board.setPointerCapture(e.pointerId); } catch (err) { /* not capturable */ }
    active.set(e.pointerId, off);
    press(off, 'p' + e.pointerId);
  });
  board.addEventListener('pointermove', (e) => {
    if (!active.has(e.pointerId)) return;
    const off = keyAt(e.clientX, e.clientY);
    const cur = active.get(e.pointerId);
    if (off === cur || off < 0) return;
    release(cur, 'p' + e.pointerId);
    active.set(e.pointerId, off);
    press(off, 'p' + e.pointerId);
  });
  const lift = (e) => {
    if (!active.has(e.pointerId)) return;
    release(active.get(e.pointerId), 'p' + e.pointerId);
    active.delete(e.pointerId);
  };
  board.addEventListener('pointerup', lift);
  board.addEventListener('pointercancel', lift);
  board.addEventListener('lostpointercapture', lift);
  board.addEventListener('contextmenu', (e) => e.preventDefault());

  // ---------- keyboard ----------
  // Keys of the piano itself: Tab to the keys, arrows move, Enter or Space plays.
  board.addEventListener('keydown', (e) => {
    const k = e.target.closest ? e.target.closest('.pk') : null;
    if (!k) return;
    const off = Number(k.dataset.off);
    if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') {
      const next = Math.max(0, Math.min(COUNT - 1, off + (e.key === 'ArrowRight' ? 1 : -1)));
      keys.forEach((x) => { x.el.tabIndex = -1; });
      keys[next].el.tabIndex = 0; keys[next].el.focus();
      e.preventDefault();
    } else if ((e.key === 'Enter' || e.key === ' ') && !e.repeat) {
      e.preventDefault(); arm(true); press(off, 'e' + off);
    }
  });
  board.addEventListener('keyup', (e) => {
    const k = e.target.closest ? e.target.closest('.pk') : null;
    if (k && (e.key === 'Enter' || e.key === ' ')) release(Number(k.dataset.off), 'e' + k.dataset.off);
  });
  board.addEventListener('focusin', () => arm(true));
  // Letters of the computer keyboard play only while the piano is "armed" (clicked or focused),
  // so the page's own shortcuts and the search field keep working.
  document.addEventListener('keydown', (e) => {
    if (!armed || e.ctrlKey || e.metaKey || e.altKey || e.repeat) return;
    const t = e.target;
    if (t && (t.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName))) return;
    const off = OFFSET_OF.get(e.code);
    if (off === undefined) return;
    e.preventDefault();
    press(off, 'k' + e.code);
  });
  document.addEventListener('keyup', (e) => {
    const off = OFFSET_OF.get(e.code);
    if (off !== undefined) release(off, 'k' + e.code);
  });
  document.addEventListener('pointerdown', (e) => { if (!section.contains(e.target)) arm(false); });
  window.addEventListener('blur', () => { releaseAll(); arm(false); });
  document.addEventListener('visibilitychange', () => { if (document.hidden) releaseAll(); });

  if (muteBtn) {
    muteBtn.addEventListener('click', () => {
      muted = !muted;
      if (master) master.gain.setTargetAtTime(muted ? 0 : 0.8, ctx.currentTime, 0.02);
      if (!muted) { ensureAudio(); setStatus(loadState === 'ready' ? T.ready : loadState === 'failed' ? T.error : loadState === 'loading' ? T.loading : T.idle); }
      paintMute();
    });
  }
  paintMute();
  if (!muted) setStatus(T.idle);
})();
