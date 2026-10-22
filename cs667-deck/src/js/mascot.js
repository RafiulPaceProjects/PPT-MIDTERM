/* Grady, the grade-seal mascot (Part 4). One instance, a fixed overlay
   outside the reveal root, pointer-events: none.

   State model: three layers, shown in priority order
     cue        content-cued: thinking, warning, celebrating, pointing
     transient  click-pop, dizzy (interrupt, then return)
     ambient    sleeping < idle < tracking < hover-delight
   MascotController.setState() is the only writer of #mascot[data-state].
   The placard letter is content: it changes even under reduced motion. */
(function () {
  "use strict";
  // grade colours come from the theme (INV-2: defined once, in theme.css)
  const GRADE = { A: "var(--grade-a)", B: "var(--grade-b)", C: "var(--grade-c)" };
  const MOUTHS = {
    smile: "M53 63 Q60 69 67 63",
    o: "M57.5 64 Q60 61 62.5 64 Q60 67.5 57.5 64",
    flat: "M54 65 Q60 65 66 65",
    wavy: "M52 65 Q55 62 58 65 Q61 68 64 65 Q66.5 62.5 68 64.5",
    grin: "M51.5 61.5 Q60 73 68.5 61.5 Q60 64.5 51.5 61.5",
    oval: "M58 65 Q60 62.5 62 65 Q60 67.5 58 65",
  };
  const FACE = {
    idle: "smile", tracking: "smile", "hover-delight": "o", "click-pop": "grin", thinking: "flat",
    warning: "wavy", celebrating: "grin", dizzy: "wavy", sleeping: "oval", pointing: "smile",
  };
  const AMBIENT = ["sleeping", "idle", "tracking", "hover-delight"];

  let svg, layer, pupils, head, mouth, letterText, placardRect;
  let exporting = false, reduced = false, paused = false;
  let ambient = "idle", transient = null, cue = null;
  let transientTimer = 0, cueTimer = 0, cueToken = 0;
  let slideLetter = "A", letter = "A", thinkingCycle = 0;
  let lastInput = performance.now(), lastMove = 0, stillTimer = 0, sleepTimer = 0, blinkTimer = 0;
  let pointer = null, pupilLock = null, rafPending = false;
  let entryFired = new Set(), forcedUsed = false, slideEnteredAt = 0;
  let hoverLeaveTimer = 0, hoverSince = 0, hoverTimer = 0, lastWiggle = 0;
  let dizzyCooldownUntil = 0, velSamples = [], crossings = [], lastEdge = null;
  let dragging = false, slideQuiet = false, tooltipOpenSince = 0;

  /* ---------------------------------------------------------------- render */
  function shown() { return cue || transient || ambient; }

  function setState(name) {   // the only writer of data-state
    if (!svg) return;
    svg.setAttribute("data-state", name);
    mouth.setAttribute("d", MOUTHS[svg.classList.contains("grin-hold") && name === "idle" ? "grin" : FACE[name]]);
  }
  function render() { setState(exporting ? "idle" : shown()); }

  function setLetter(l) {
    letter = l || "A";
    if (!letterText) return;
    letterText.textContent = letter;
    letterText.style.fill = GRADE[letter] || GRADE.A;
    placardRect.style.stroke = GRADE[letter] || GRADE.A;
  }
  function flash(cls, ms) {
    if (!svg) return;
    svg.classList.remove(cls);
    void svg.getBoundingClientRect();
    svg.classList.add(cls);
    setTimeout(() => svg.classList.remove(cls), ms);
  }

  /* big motions only outside the quiet windows (Part 4 restraint rules) */
  function quietWindow() {
    const entering = window.DeckAnimations && window.DeckAnimations.isEntering();
    const tooltipLong = tooltipOpenSince && performance.now() - tooltipOpenSince > 400;
    return entering || tooltipLong || dragging || slideQuiet;
  }
  function allowBig(force) {
    const ok = !reduced && !exporting && !paused && (force || !quietWindow());
    svg.classList.toggle("big", ok);
    return ok;
  }

  /* ---------------------------------------------------------------- layers */
  function setAmbient(name) {
    if (ambient === name) return;
    ambient = name;
    if (!cue && !transient) render();
  }
  function setTransient(name, ms) {
    if (cue) return false;                       // content cues outrank transients
    clearTimeout(transientTimer);
    transient = name;
    render();
    transientTimer = setTimeout(() => { transient = null; render(); }, ms);
    return true;
  }
  /** A content-cued state; ms = null holds it until releaseCue(). */
  function setCue(name, ms, opts = {}) {
    clearTimeout(cueTimer);
    const token = ++cueToken;
    cue = name;
    transient = null;
    svg.classList.remove("flag");
    if (name === "warning") setLetter(opts.letter || (slideLetter === "B" ? "B" : "C"));
    if (name === "celebrating") setLetter(opts.letter || "A");
    render();
    if (name === "warning" && opts.shake !== false && allowBig(opts.force)) flash("shake", 320);
    if (name === "celebrating") allowBig(opts.force);
    if (ms != null) cueTimer = setTimeout(() => { if (token === cueToken) releaseCue(opts.after); }, ms);
    return token;
  }
  function releaseCue(after) {
    clearTimeout(cueTimer);
    stopThinkingCycle();
    cue = null;
    svg.classList.remove("flag");
    pupilLock = null;
    setLetter(after || slideLetter);
    render();
    aimPupils();
  }

  /* thinking: placard cycles A -> B -> C at 300 ms per letter */
  function startThinkingCycle() {
    stopThinkingCycle();
    let i = 0;
    const seq = ["A", "B", "C"];
    setLetter(seq[i]);
    thinkingCycle = setInterval(() => { i = (i + 1) % 3; setLetter(seq[i]); }, 300);
  }
  function stopThinkingCycle() { clearInterval(thinkingCycle); thinkingCycle = 0; }

  function think(ms, landOn) {
    const t = setCue("thinking", ms, { after: landOn });
    startThinkingCycle();
    return t;
  }
  function hold(name) {           // held thinking (slider drag, toggle, [data-busy])
    if (name === "thinking") { setCue("thinking", null); startThinkingCycle(); }
  }

  /* ---------------------------------------------------------------- pointing */
  function center(elm) { const r = elm.getBoundingClientRect(); return { x: r.left + r.width / 2, y: r.top + r.height / 2 }; }
  function point(selector, opts = {}) {
    const slide = window.Reveal && Reveal.getCurrentSlide();
    const target = slide && (slide.querySelector(selector) || document.querySelector(selector));
    if (!target) return;
    const tok = setCue("pointing", 2500, { after: opts.after });
    const t = center(target), m = eyeCenter();
    pupilLock = t;
    svg.style.setProperty("--lean", (t.x < m.x ? -3 : 3) + "deg");
    if (allowBig(opts.force)) svg.classList.add("flag");
    aimPupils();
    return tok;
  }

  /* ---------------------------------------------------------------- pupils */
  function eyeCenter() {
    const r = svg.getBoundingClientRect();
    return { x: r.left + r.width * 0.5, y: r.top + r.height * (51 / 120) };
  }
  function aimPupils() {
    if (!pupils) return;
    const shownState = shown();
    if (reduced || exporting || shownState === "thinking" || shownState === "sleeping" || shownState === "dizzy") {
      pupils.style.transform = ""; head.style.transform = ""; return;
    }
    const aim = pupilLock || pointer;
    if (!aim) { pupils.style.transform = ""; head.style.transform = ""; return; }
    const c = eyeCenter();
    const dx = aim.x - c.x, dy = aim.y - c.y, dist = Math.hypot(dx, dy) || 1;
    const k = Math.min(dist / 300, 1) * 3.5;
    pupils.style.transform = `translate(${((dx / dist) * k).toFixed(2)}px, ${((dy / dist) * k).toFixed(2)}px)`;
    const tilt = Math.max(-4, Math.min(4, (dx / innerWidth) * 8));
    head.style.transform = pupilLock ? "" : `rotate(${tilt.toFixed(2)}deg)`;
  }
  function scheduleAim() {
    if (rafPending) return;
    rafPending = true;
    requestAnimationFrame(() => { rafPending = false; aimPupils(); });
  }

  /* ---------------------------------------------------------------- timers */
  function blinkLoop() {
    clearTimeout(blinkTimer);
    blinkTimer = setTimeout(() => {
      if (!paused && !exporting && shown() !== "sleeping") flash("blink", 140);
      blinkLoop();
    }, 3500 + Math.random() * 2000);
  }
  function noteInput() {
    const wasAsleep = ambient === "sleeping";
    lastInput = performance.now();
    clearTimeout(sleepTimer);
    sleepTimer = setTimeout(() => setAmbient("sleeping"), 20000);
    if (wasAsleep) {
      setAmbient("tracking");
      if (allowBig(false)) flash("startle", 220);
    }
  }
  function noteMove() {
    lastMove = performance.now();
    if (ambient !== "hover-delight") setAmbient("tracking");
    clearTimeout(stillTimer);
    stillTimer = setTimeout(() => { if (ambient === "tracking") setAmbient("idle"); }, 8000);
  }

  /* dizzy: velocity > 2,500 px/s sustained 300 ms, or 3 edge-to-edge crossings in 2 s */
  function checkDizzy(e, now) {
    velSamples.push({ x: e.clientX, y: e.clientY, t: now });
    velSamples = velSamples.filter((s) => now - s.t < 350);
    let fast = velSamples.length > 3;
    for (let i = 1; i < velSamples.length && fast; i++) {
      const a = velSamples[i - 1], b = velSamples[i];
      const v = Math.hypot(b.x - a.x, b.y - a.y) / Math.max(1, b.t - a.t) * 1000;
      if (v < 2500) fast = false;
    }
    fast = fast && velSamples[velSamples.length - 1].t - velSamples[0].t >= 300;
    const edge = e.clientX < innerWidth * 0.08 ? "L" : e.clientX > innerWidth * 0.92 ? "R" : null;
    if (edge && edge !== lastEdge) { if (lastEdge) crossings.push(now); lastEdge = edge; }
    crossings = crossings.filter((t) => now - t < 2000);
    if ((fast || crossings.length >= 3) && now > dizzyCooldownUntil && !cue) {
      dizzyCooldownUntil = now + 5000;              // 1 s dizzy + 4 s cooldown
      crossings = [];
      if (setTransient("dizzy", 1000)) allowBig(false);
    }
  }

  /* ---------------------------------------------------------------- events */
  function interactiveFrom(target) { return target && target.closest ? target.closest("[data-interactive]") : null; }

  function wire() {
    document.addEventListener("pointermove", (e) => {
      if (e.pointerType === "touch") return;
      const now = performance.now();
      pointer = { x: e.clientX, y: e.clientY };
      noteInput(); noteMove(); checkDizzy(e, now); scheduleAim();
    }, { passive: true });
    document.addEventListener("pointerover", (e) => {
      const it = interactiveFrom(e.target);
      if (!it) return;
      clearTimeout(hoverLeaveTimer);
      if (ambient !== "hover-delight") {
        hoverSince = performance.now();
        setAmbient("hover-delight");
        const now = performance.now();
        if (now - lastWiggle > 150 && !reduced) { lastWiggle = now; flash("wiggle", 220); }
        clearTimeout(hoverTimer);
        // reading a tooltip: settle to calm tracking after 400 ms, no repeated wiggling
        hoverTimer = setTimeout(() => { if (ambient === "hover-delight") setAmbient("tracking"); }, 400);
      }
    });
    document.addEventListener("pointerout", (e) => {
      const it = interactiveFrom(e.target);
      if (!it || (e.relatedTarget && it.contains(e.relatedTarget))) return;
      clearTimeout(hoverLeaveTimer);
      hoverLeaveTimer = setTimeout(() => { if (ambient === "hover-delight") setAmbient("tracking"); }, 150);
    });
    document.addEventListener("pointerdown", (e) => {
      const it = interactiveFrom(e.target);
      if (e.pointerType === "touch" && it) {
        pupilLock = center(it); aimPupils();
        setTimeout(() => { pupilLock = null; aimPupils(); }, 3000);
      }
      if (!it) return;                              // clicks elsewhere do nothing
      pop(it.getAttribute("data-mascot-letter"));
    });
    document.addEventListener("keydown", noteInput);
    document.documentElement.addEventListener("pointerleave", () => {
      pointer = null;
      pupils.style.transition = "transform 600ms ease-out";
      aimPupils();
      setTimeout(() => { pupils.style.transition = ""; }, 650);
      setAmbient("idle");
    });
  }

  /** click-pop: squash + hop; the element's letter lands at the pop's peak. */
  function pop(newLetter) {
    if (newLetter) setTimeout(() => setLetter(newLetter), 90);
    if (setTransient("click-pop", 180)) allowBig(false);
  }

  /* ---------------------------------------------------------------- slides */
  function slideChanged(slide, c) {
    if (!svg) return;
    layer.classList.toggle("hidden", c.hidden);
    entryFired = new Set();
    forcedUsed = false;
    slideQuiet = c.quiet;
    slideLetter = c.letter;
    slideEnteredAt = performance.now();
    svg.classList.remove("flag", "map-look", "wide", "grin-hold", "drop-in", "tip-cap", "wave");
    noteInput();
    clearTimeout(cueTimer);
    const token = ++cueToken;
    stopThinkingCycle();
    if (exporting) { cue = null; transient = null; ambient = "idle"; setLetter("A"); render(); return; }

    const after = (ms, fn) => setTimeout(() => { if (token === cueToken) fn(); }, ms);
    const entrance = reduced ? 0 : 1200;

    // the transition itself: thinking for <= 350 ms
    cue = "thinking"; render(); startThinkingCycle();
    after(350, () => {
      stopThinkingCycle();
      cue = null;
      setLetter(c.letter);
      render();
      applyEntry(slide, c, after, entrance);
    });
  }

  function cueOnce(name, fn) {
    if (entryFired.has(name)) return;                // at most once per slide entry
    entryFired.add(name);
    fn();
  }
  function forceAllowed(c) {
    if (!c.force || forcedUsed) return false;
    forcedUsed = true;
    return true;
  }

  function applyEntry(slide, c, after, entrance) {
    switch (c.type) {
      case "title":
        setLetter(" ");
        if (allowBig(true)) flash("drop-in", 440);
        after(reduced ? 0 : 200, () => setLetter("A"));
        after(reduced ? 0 : 600, () => { if (allowBig(true)) flash("tip-cap", 520); });
        return;
      case "map":
        svg.classList.add("map-look");
        break;
      case "model-results":
        think(reduced ? 1 : 600, c.letter);
        after(reduced ? 0 : 1100, () => setLetter(c.letter));
        break;
      case "discovery":
        cueOnce("warning", () => setCue("warning", null, { force: forceAllowed(c), letter: "C" }));
        return;
      case "closing":
        after(entrance + 200, () => { if (allowBig(true)) flash("wave", 920); });
        after(entrance + 1150, () => svg.classList.add("grin-hold") || render());
        return;
    }
    if (c.state === "warning") cueOnce("warning", () => setCue("warning", 2000, { force: forceAllowed(c) }));
    else if (c.state === "celebrating") cueOnce("celebrating", () => setCue("celebrating", 1200, { force: forceAllowed(c) }));
    if (c.target) after(entrance + 800, () => point(c.target));
  }

  /* ---------------------------------------------------------------- api */
  function place(rect) {
    if (!layer) return;
    const zone = 180 * rect.scale;
    const size = Math.min(104, zone * 0.9);
    layer.style.width = size + "px";
    layer.style.height = size + "px";
    layer.style.left = rect.left + rect.width - zone / 2 - size / 2 + "px";
    layer.style.top = rect.top + rect.height - zone / 2 - size / 2 + "px";
  }

  function init(opts) {
    exporting = !!opts.exporting;
    layer = document.getElementById("mascot-layer");
    svg = document.getElementById("mascot");
    if (!svg) return;
    pupils = svg.querySelector("#mascot-pupils");
    head = svg.querySelector("#mascot-head");
    mouth = svg.querySelector("#mascot-mouth");
    letterText = svg.querySelector("#mascot-letter");
    placardRect = svg.querySelector("#mascot-placard rect");
    setLetter("A");
    render();
    if (exporting) return;
    wire();
    blinkLoop();
    noteInput();
  }

  const api = {
    init, place, slideChanged,
    setState: (name) => {                       // external callers go through the layers
      if (AMBIENT.includes(name)) setAmbient(name);
      else if (name === "click-pop") pop();
      else if (name === "dizzy") setTransient("dizzy", 1000);
      else if (name === "thinking") hold("thinking");
      else setCue(name, name === "celebrating" ? 1200 : name === "pointing" ? 2500 : 2000);
    },
    setMood: (name) => api.setState(name),
    setVisible: (v) => layer && layer.classList.toggle("hidden", !v),
    setLetter, setCue, releaseCue, think, hold, pop, point,
    celebrate: (opts = {}) => setCue("celebrating", 1200, opts),
    warn: (opts = {}) => setCue("warning", "ms" in opts ? opts.ms : 2000, opts),
    dizzyLite: () => { if (!reduced) flash("orbit-once", 620); },
    shakePlacard: () => { if (!reduced) flash("placard-shake", 260); },
    setDragging: (d) => { dragging = d; },
    tooltipOpen: (open) => { tooltipOpenSince = open ? performance.now() : 0; },
    lockPupils: (p) => { pupilLock = p; aimPupils(); },
    wide: (on) => svg && svg.classList.toggle("wide", on),
    setReducedMotion: (r) => { reduced = r; aimPupils(); },
    setPaused: (p) => { paused = p; svg && svg.classList.toggle("paused", p); },
    get state() { return shown(); },
    get letter() { return letter; },
  };
  window.DeckMascot = api;
  window.MascotController = api;
})();
