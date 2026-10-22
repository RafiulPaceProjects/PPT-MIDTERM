/* Reveal init, slide-state hooks, keyboard extras, export mode.
   The presenter timer is reveal's own speaker view (S key), paced by each
   slide's data-timing; it is never shown on the audience screen. */
(function () {
  "use strict";
  const params = new URLSearchParams(location.search);
  const exporting = params.has("export");
  const root = document.documentElement;

  if (exporting) root.classList.add("exporting");

  /* reduced motion (INV-12): the OS setting, or the manual toggle (R / footer) */
  const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
  let manual = null;
  try { manual = localStorage.getItem("deck-reduced-motion"); } catch (e) { /* storage blocked */ }
  function applyMotion() {
    const reduced = exporting || manual === "1" || (manual === null && mq.matches);
    root.classList.toggle("reduced-motion", reduced);
    const btn = document.getElementById("motion-toggle");
    if (btn) btn.setAttribute("aria-pressed", String(reduced));
    window.DeckMascot && window.DeckMascot.setReducedMotion(reduced);
  }
  function toggleMotion() {
    manual = root.classList.contains("reduced-motion") ? "0" : "1";
    try { localStorage.setItem("deck-reduced-motion", manual); } catch (e) { /* fine */ }
    applyMotion();
  }
  mq.addEventListener("change", applyMotion);

  /* where the 1920x1080 slide sits in the viewport, for the overlays */
  function slideRect() {
    const scale = Reveal.getScale();
    const w = 1920 * scale, h = 1080 * scale;
    return { left: (innerWidth - w) / 2, top: (innerHeight - h) / 2, width: w, height: h, scale };
  }
  function placeChrome() {
    const r = slideRect();
    const btn = document.getElementById("motion-toggle");
    if (btn) {
      btn.style.left = r.left + 1200 * r.scale + "px";
      btn.style.top = r.top + 1080 * r.scale - 70 * r.scale + "px";
    }
    window.DeckMascot && window.DeckMascot.place(r);
  }

  Reveal.initialize({
    width: 1920,
    height: 1080,
    margin: 0,
    minScale: 0.05,
    maxScale: 4,
    center: false,
    controls: false,
    progress: true,
    slideNumber: "c/t",
    hash: true,
    keyboard: true,
    transition: exporting ? "none" : "fade",
    transitionSpeed: "fast",
    backgroundTransition: "none",
    // export shows every fragment in its final state (the post-reveal slide)
    fragments: !exporting,
    plugins: [RevealNotes],
  });

  Reveal.addKeyBinding({ keyCode: 82, key: "R", description: "Toggle reduced motion" }, toggleMotion);

  function cueFor(slide) {
    return {
      state: slide.dataset.mascotState || "idle",
      letter: slide.dataset.mascotLetter || "A",
      target: slide.dataset.mascotTarget || null,
      force: slide.dataset.mascotForce === "true",
      quiet: slide.dataset.quiet === "true",
      hidden: slide.dataset.mascot === "hidden",
      type: slide.dataset.slideType,
    };
  }

  function onSlide(slide, previous) {
    window.DeckCharts.renderSlide(slide);
    window.DeckAnimations.enter(slide);
    window.DeckInteractions.enter(slide, previous);
    window.DeckMascot.slideChanged(slide, cueFor(slide));
  }

  Reveal.on("ready", async (event) => {
    document.getElementById("motion-toggle").addEventListener("click", toggleMotion);
    window.DeckMascot.init({ exporting });
    applyMotion();
    try { await document.fonts.ready; } catch (e) { /* fonts are vendored; carry on */ }
    window.DeckAnimations.init({ exporting });
    window.DeckInteractions.init({ exporting });
    placeChrome();
    onSlide(event.currentSlide, null);
    if (exporting) window.DeckInteractions.finalStates();
    // the capture tool waits for this flag
    requestAnimationFrame(() => requestAnimationFrame(() => { window.__deckReady = true; }));
  });
  Reveal.on("slidechanged", (event) => onSlide(event.currentSlide, event.previousSlide));
  Reveal.on("fragmentshown", (event) => window.DeckInteractions.fragment(event.fragment, true));
  Reveal.on("fragmenthidden", (event) => window.DeckInteractions.fragment(event.fragment, false));
  Reveal.on("resize", () => {
    const slide = Reveal.isReady() && Reveal.getCurrentSlide();
    if (!slide) return;
    placeChrome();
    window.DeckCharts.renderSlide(slide);
  });
  window.addEventListener("resize", placeChrome);

  document.addEventListener("visibilitychange", () => window.DeckMascot.setPaused(document.hidden));

  window.Deck = { slideRect, exporting };
})();
