/* Entrances, count-ups and the skip rule. CSS does the motion (see
   animations.css); this file only flips classes at the right moments and
   runs the one shared count-up loop. */
(function () {
  "use strict";
  const { fmt } = window.DeckFormat;
  const ENTRANCE_MS = 1200;
  const NAV_KEYS = new Set(["ArrowRight", "ArrowLeft", "ArrowDown", "ArrowUp", "PageDown", "PageUp", " ", "Enter", "n", "p"]);
  const root = document.documentElement;
  let exporting = false;
  let current = null;
  let entering = false;
  let enterTimer = 0;
  let counters = [];
  let rafId = 0;

  const motionAllowed = () => !exporting && !root.classList.contains("reduced-motion");

  function splitWords() {
    document.querySelectorAll(".words").forEach((h) => {
      if (h.dataset.split) return;
      const words = h.textContent.trim().split(/\s+/);
      h.textContent = "";
      words.forEach((w, i) => {
        const s = document.createElement("span");
        s.textContent = w;
        s.style.setProperty("--w", i);
        h.appendChild(s);
        if (i < words.length - 1) h.appendChild(document.createTextNode(" "));
      });
      h.dataset.split = "1";
    });
  }

  /* confusion cells pop in diagonal order: (row + col) x 60 ms */
  function diagonal() {
    document.querySelectorAll(".cm").forEach((cm) => {
      const order = { tn: 0, fp: 1, fn: 1, tp: 2 };
      cm.querySelectorAll(".cell").forEach((c) => {
        const k = ["tn", "fp", "fn", "tp"].find((n) => c.classList.contains(n));
        c.style.setProperty("--cd", order[k]);
      });
    });
  }

  /* ---- count-ups and tweens: one shared rAF loop ----------------------- */
  const ease = (t) => 1 - Math.pow(1 - t, 3);
  function tick(now) {
    counters = counters.filter((c) => {
      const t = Math.min(1, (now - c.start) / c.ms);
      c.el.textContent = fmt(c.from + (c.to - c.from) * ease(t), c.kind);
      if (t >= 1) { c.el.textContent = c.final; return false; }
      return true;
    });
    rafId = counters.length ? requestAnimationFrame(tick) : 0;
  }
  function run(el, from, to, kind, ms) {
    const final = fmt(to, kind);
    counters = counters.filter((c) => c.el !== el);
    if (!motionAllowed() || !Number.isFinite(from)) { el.textContent = final; return; }
    counters.push({ el, from, to, kind, final, start: performance.now(), ms });
    el.textContent = fmt(from, kind);
    if (!rafId) rafId = requestAnimationFrame(tick);
  }
  /** Count an element up from 0 to its stamped data-value (800 ms ease-out). */
  function countUp(el, ms = 800) {
    const to = Number(el.dataset.value);
    if (!Number.isFinite(to) || el.hasAttribute("data-pending")) return;
    run(el, 0, to, el.dataset.fmt, ms);
  }
  /** Tween a number element between two values (slider readouts, toggles). */
  function tweenText(el, from, to, kind, ms = 300) {
    run(el, from == null ? NaN : from, to, kind, ms);
  }
  function snapCounters(slide) {
    counters = counters.filter((c) => {
      if (!slide || slide.contains(c.el)) { c.el.textContent = c.final; return false; }
      return true;
    });
  }

  /* ---- entering a slide ------------------------------------------------- */
  function enter(slide) {
    snapCounters(null);
    document.querySelectorAll(".reveal section.entered, .reveal section.skip").forEach((s) => {
      if (s !== slide) s.classList.remove("entered", "skip");
    });
    current = slide;
    slide.classList.remove("entered", "skip");
    root.classList.toggle("anim", motionAllowed());
    void slide.offsetWidth;                 // restart: start state, then entered
    slide.classList.add("entered");
    slide.querySelectorAll("[data-count]").forEach((el) => countUp(el));
    entering = motionAllowed();
    clearTimeout(enterTimer);
    enterTimer = setTimeout(() => { entering = false; }, ENTRANCE_MS);
  }

  function skip() {
    if (!entering || !current) return false;
    current.classList.add("skip");
    snapCounters(current);
    entering = false;
    return true;
  }

  function init(opts) {
    exporting = !!opts.exporting;
    splitWords();
    diagonal();
    root.classList.toggle("anim", motionAllowed());
    // a key during an entrance finishes it at once; the key still navigates
    window.addEventListener("keydown", (e) => { if (NAV_KEYS.has(e.key)) skip(); }, true);
    document.querySelector(".reveal").addEventListener("pointerdown", () => skip(), true);
  }

  window.DeckAnimations = { init, enter, countUp, tweenText, motionAllowed, isEntering: () => entering };
})();
