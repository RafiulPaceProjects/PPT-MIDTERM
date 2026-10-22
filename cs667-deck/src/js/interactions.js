/* The six interactions (Part 6). Every control carries [data-interactive],
   which is all the mascot needs to react. Every one has a static final
   state for the export, and none keeps the keyboard: focus always comes
   back to slide navigation. */
(function () {
  "use strict";
  const { get, fmt } = window.DeckFormat;
  const M = () => window.DeckMascot;
  const A = () => window.DeckAnimations;
  let exporting = false;

  /** Hand the keyboard back to reveal. */
  function returnFocus() {
    if (document.activeElement && document.activeElement !== document.body) document.activeElement.blur();
    window.focus();
  }

  /* ---------------------------------------------------- 1. tooltips */
  const tip = document.getElementById("tooltip");
  let tipOwner = null;
  function showTip(owner, e) {
    tipOwner = owner;
    tip.innerHTML = owner.getAttribute("data-tip");
    tip.classList.add("on");
    moveTip(e);
    const dim = owner.closest(".hover-dim");
    if (dim) {
      dim.classList.add("dimming");
      const hl = owner.closest(".hl");
      dim.querySelectorAll(".hl.hot").forEach((n) => n.classList.remove("hot"));
      if (hl) hl.classList.add("hot");
    }
    M().tooltipOpen(true);
  }
  function moveTip(e) {
    if (!tipOwner || !e) return;
    const pad = 18, w = tip.offsetWidth, h = tip.offsetHeight;
    let x = e.clientX + pad, y = e.clientY + pad;
    if (x + w > innerWidth - 8) x = e.clientX - w - pad;
    if (y + h > innerHeight - 8) y = e.clientY - h - pad;
    tip.style.left = x + "px";
    tip.style.top = y + "px";
  }
  function hideTip() {
    if (!tipOwner) return;
    const dim = tipOwner.closest(".hover-dim");
    if (dim) { dim.classList.remove("dimming"); dim.querySelectorAll(".hl.hot").forEach((n) => n.classList.remove("hot")); }
    tipOwner = null;
    tip.classList.remove("on");
    M().tooltipOpen(false);
  }
  function wireTooltips() {
    document.addEventListener("pointerover", (e) => {
      const owner = e.target.closest && e.target.closest("[data-tip]");
      if (owner && owner !== tipOwner) showTip(owner, e);
    });
    document.addEventListener("pointermove", moveTip, { passive: true });
    document.addEventListener("pointerout", (e) => {
      const owner = e.target.closest && e.target.closest("[data-tip]");
      if (owner && owner === tipOwner && !(e.relatedTarget && owner.contains(e.relatedTarget))) hideTip();
    });
    document.addEventListener("focusin", (e) => {
      const owner = e.target.closest && e.target.closest("[data-tip]");
      if (owner) {
        const r = owner.getBoundingClientRect();
        showTip(owner, { clientX: r.right, clientY: r.top });
      }
    });
    document.addEventListener("focusout", hideTip);
  }

  /* ---------------------------------------------------- 2. visit-type toggle */
  function wireToggle() {
    document.querySelectorAll('[data-toggle="visit-type"]').forEach((btn) => {
      btn.addEventListener("click", () => {
        const measure = btn.dataset.measure;
        if (btn.getAttribute("aria-pressed") === "true") return;
        document.querySelectorAll('[data-toggle="visit-type"]').forEach((b) => b.setAttribute("aria-pressed", String(b === btn)));
        const minis = document.querySelectorAll('[data-chart-mini="after"]');
        M().hold("thinking");
        minis.forEach((m) => m.classList.add("swapping"));
        setTimeout(() => {
          window.DeckCharts.charts.visitMinis(measure);
          minis.forEach((m) => m.classList.remove("swapping"));
          M().releaseCue();
          M().point('[data-chart-mini="after"]');
          returnFocus();
        }, A().motionAllowed() ? 300 : 0);
      });
    });
  }

  /* ---------------------------------------------------- 3. live 3D map */
  const LIVE_TIMEOUT_MS = 4000;
  let liveTimer = 0;
  function wireLiveMap() {
    const wrap = document.querySelector("[data-live-map]");
    if (!wrap) return;
    const btn = wrap.querySelector("[data-go-live]");
    const status = wrap.querySelector(".live-status");
    const video = wrap.querySelector("video");
    const say = (s) => { status.textContent = s; };

    function playRecording(reason) {
      say(reason + " Playing the recorded rotation.");
      wrap.classList.add("playing");
      video.currentTime = 0;
      video.play().catch(() => { wrap.classList.remove("playing"); say(reason + " Showing the poster."); });
      btn.textContent = "Back to poster";
      btn.setAttribute("aria-label", "Back to the poster");
    }
    function reset() {
      clearTimeout(liveTimer);
      const frame = wrap.querySelector("iframe");
      if (frame) frame.remove();
      wrap.querySelector(".live-cover")?.remove();
      wrap.classList.remove("live", "playing");
      video.pause();
      btn.textContent = "Go live";
      btn.setAttribute("aria-label", "Go live: open the interactive 3D map");
      say("");
      M().wide(false);
      M().lockPupils(null);
      returnFocus();
    }
    function goLive() {
      if (wrap.classList.contains("live") || wrap.classList.contains("playing")) { reset(); return; }
      if (!navigator.onLine) { playRecording("Offline: the live map needs the network."); return; }
      say("Loading the live map…");
      M().hold("thinking");
      const frame = document.createElement("iframe");
      frame.title = "Interactive 3D map of inspections per ZIP code";
      frame.src = "assets/embeds/nyc_zip_3d_hero.html";
      frame.setAttribute("tabindex", "-1");
      wrap.appendChild(frame);
      const started = performance.now();
      const check = () => {
        let ok = false;
        try { ok = !!frame.contentDocument.querySelector("#deck-container canvas"); } catch (e) { ok = false; }
        if (ok) {
          clearTimeout(liveTimer);
          wrap.classList.add("live");
          addCover(frame);
          say("Live. Drag to tilt and rotate; Esc returns the keys to the slides.");
          btn.textContent = "Back to flat view";
          btn.setAttribute("aria-label", "Back to the flat view");
          M().releaseCue();
          M().celebrate({ letter: "C" });
          return;
        }
        if (performance.now() - started > LIVE_TIMEOUT_MS) {
          frame.remove();                          // silent fallback: the poster stays
          M().releaseCue();
          playRecording("The live map did not load.");
          return;
        }
        liveTimer = setTimeout(check, 250);
      };
      liveTimer = setTimeout(check, 250);
    }
    /* click-to-activate: the iframe only takes the keyboard after a click,
       and Esc or leaving the map hands it back */
    function addCover(frame) {
      const cover = document.createElement("button");
      cover.className = "live-cover";
      cover.type = "button";
      cover.setAttribute("data-interactive", "");
      cover.setAttribute("aria-label", "Click to interact with the 3D map");
      cover.textContent = "Click to interact";
      wrap.appendChild(cover);
      cover.addEventListener("click", () => {
        cover.hidden = true;
        frame.setAttribute("tabindex", "0");
        frame.focus();
        try {
          frame.contentWindow.addEventListener("keydown", (e) => {
            if (e.key === "Escape") { cover.hidden = false; frame.setAttribute("tabindex", "-1"); returnFocus(); }
          });
        } catch (e) { /* cross-origin: leaving the map still returns focus */ }
      });
      wrap.addEventListener("pointerleave", () => {
        if (!cover.isConnected) return;
        cover.hidden = false;
        frame.setAttribute("tabindex", "-1");
        returnFocus();
      });
    }
    btn.addEventListener("click", () => { goLive(); btn.blur(); });
    // pointer events stop at the iframe edge: Grady holds his aim there, eyes wide
    wrap.addEventListener("pointerenter", () => { if (wrap.classList.contains("live")) M().wide(true); });
    wrap.addEventListener("pointermove", (e) => { if (wrap.classList.contains("live")) M().lockPupils({ x: e.clientX, y: e.clientY }); });
    wrap.addEventListener("pointerleave", () => { M().wide(false); M().lockPupils(null); });
    wrap._reset = reset;
  }

  /* ---------------------------------------------------- 4. threshold slider */
  let stops = [];
  let stopIndex = 0;
  function wireSlider() {
    const box = document.querySelector("[data-threshold]");
    if (!box) return;
    const input = box.querySelector("input[type=range]");
    stops = get("thresholds.stops");
    const def = get("thresholds.default");
    input.max = String(stops.length - 1);
    stopIndex = stops.findIndex((s) => s.threshold === def);
    input.value = String(stopIndex);
    const ticks = box.querySelector(".thr-ticks");
    ticks.innerHTML = "";
    stops.forEach((s, i) => {
      const t = document.createElement("span");
      // range thumbs are inset by half their width; nudge labels to match
      t.style.left = `calc(${(100 * i) / (stops.length - 1)}% + ${12 - (24 * i) / (stops.length - 1)}px)`;
      t.textContent = fmt(s.threshold, "thr") + (s.threshold === def ? " ★" : "");
      if (s.threshold === def) { t.className = "default"; t.title = "the chosen threshold"; }
      ticks.appendChild(t);
    });
    let dragging = false;
    input.addEventListener("pointerdown", () => {
      dragging = true;
      M().setDragging(true);
      M().hold("thinking");
      M().setLetter("C");
    });
    input.addEventListener("input", () => {
      setStop(Number(input.value), true);
      if (dragging) {
        const r = input.getBoundingClientRect();
        M().lockPupils({ x: r.left + (r.width * Number(input.value)) / (stops.length - 1), y: r.top + r.height / 2 });
      }
    });
    const release = () => {
      if (!dragging) return;
      dragging = false;
      M().setDragging(false);
      M().lockPupils(null);
      M().releaseCue();
      judge();
      input.blur();                              // the arrow keys go back to the slides
    };
    input.addEventListener("pointerup", release);
    input.addEventListener("pointercancel", release);
    input.addEventListener("keyup", (e) => { if (e.key.startsWith("Arrow") || e.key === "Home" || e.key === "End") judge(); });
    input.addEventListener("keydown", (e) => { if (e.key === "Escape") { e.stopPropagation(); input.blur(); } });
    setStop(stopIndex, false);
  }
  function judge() {
    const s = stops[stopIndex];
    if (s.recall >= 0.8) M().celebrate({ letter: "C" });
    else if (s.precision < 0.3) M().warn({});
    else M().pop();
  }
  function setStop(i, animate) {
    const prev = stops[stopIndex], s = stops[i];
    stopIndex = i;
    const box = document.querySelector("[data-threshold]");
    const input = box.querySelector("input[type=range]");
    input.value = String(i);
    const recall = fmt(s.recall, "frac_pct1"), precision = fmt(s.precision, "frac_pct1");
    input.setAttribute("aria-valuetext",
      `threshold ${fmt(s.threshold, "thr")}: recall ${recall}, precision ${precision}, F1 ${fmt(s.f1, "dec3")}`);
    const out = (k) => box.querySelector(`[data-out="${k}"]`);
    const tw = (el, from, to, kind) => (animate ? A().tweenText(el, from, to, kind, 300) : (el.textContent = fmt(to, kind)));
    tw(out("recall"), prev.recall, s.recall, "frac_pct1");
    tw(out("precision"), prev.precision, s.precision, "frac_pct1");
    tw(out("f1"), prev.f1, s.f1, "dec3");
    out("plain").textContent =
      `Catches ~${fmt(s.recall, "per100")} of every 100 B or C inspections; about ${fmt(s.precision, "inv_tenths")} in 10 flags still end A.`;
    document.querySelectorAll("[data-confusion] [data-cm]").forEach((el) => {
      const k = el.dataset.cm;
      tw(el, prev[k], s[k], "int");
    });
    window.DeckCharts.charts.curveMarker(s.threshold);
  }

  /* ---------------------------------------------------- 5. dummy trap card */
  function wireTrap() {
    const card = document.querySelector("[data-trap-card]");
    if (!card) return;
    card.querySelector("[data-reveal]").addEventListener("click", (e) => {
      card.classList.add("flipped");
      M().warn({ ms: 2600, letter: "C" });
      M().dizzyLite();
      returnFocus();
    });
  }

  /* ---------------------------------------------------- 6. cuisine explorer */
  function wireCuisine() {
    const fig = document.querySelector('[data-chart="cuisine"]');
    if (!fig) return;
    const readout = fig.querySelector(".cuisine-readout");
    const rows = get("tables.cuisine");
    let pinned = null;
    const show = (name, animate) => {
      const c = rows.find((r) => r.cuisine === name);
      if (!c) { readout.textContent = ""; return; }
      readout.innerHTML = `<b>${c.cuisine}</b>: median <b class="cx-med">${fmt(c.median_score, "num0")}</b> points (${c.typical_grade}) · ` +
        `<b class="cx-n">${fmt(c.inspections, "int")}</b> inspections · ` +
        (c.modeled_bc_pct == null ? "" : `<b class="cx-bc">${fmt(c.modeled_bc_pct, "pct1")}</b> of modeled inspections ended B or C`);
      if (animate && A().motionAllowed()) {
        A().tweenText(readout.querySelector(".cx-med"), 0, c.median_score, "num0", 400);
        if (c.modeled_bc_pct != null) A().tweenText(readout.querySelector(".cx-bc"), 0, c.modeled_bc_pct, "pct1", 400);
      }
    };
    const plot = fig.querySelector(".plot");
    const mark = (name) => {
      plot.classList.toggle("dimming", !!name);
      plot.querySelectorAll(".crow").forEach((r) => r.classList.toggle("hot", r.dataset.cuisineRow === name));
    };
    plot.addEventListener("pointerover", (e) => {
      const chip = e.target.closest("[data-cuisine]");
      if (chip && !pinned) { show(chip.dataset.cuisine, false); mark(chip.dataset.cuisine); }
    });
    plot.addEventListener("pointerleave", () => { if (!pinned) { readout.textContent = ""; mark(null); } });
    plot.addEventListener("click", (e) => {
      const chip = e.target.closest("[data-cuisine]");
      if (!chip) return;
      const name = chip.dataset.cuisine;
      pinned = pinned === name ? null : name;
      plot.querySelectorAll("[data-cuisine]").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.cuisine === pinned)));
      mark(pinned);
      if (pinned) show(pinned, true); else readout.textContent = "";
      if (e.detail === 0) M().pop(chip.getAttribute("data-mascot-letter"));   // keyboard activation
    });
    fig._reset = () => {
      pinned = null;
      readout.textContent = "";
      mark(null);
      plot.querySelectorAll("[data-cuisine]").forEach((b) => b.setAttribute("aria-pressed", "false"));
    };
  }

  /* ---------------------------------------------------- reveal hooks */
  function discoveryState(slide) {
    const wrap = slide.querySelector("[data-discovery]");
    if (!wrap) return;
    const step = slide.querySelector(".fragment.reveal-step");
    wrap.classList.toggle("revealed", exporting || (step && step.classList.contains("visible")));
  }
  function trapRings(slide) {
    slide.querySelectorAll(".trap-note").forEach((note) => {
      const on = exporting || note.classList.contains("visible");
      slide.querySelectorAll(`.trap-ring[data-trap="${note.dataset.trap}"]`).forEach((r) => r.classList.toggle("on", on));
    });
  }

  function fragment(frag, shown) {
    const slide = frag.closest("section");
    if (frag.classList.contains("reveal-step")) {
      const wrap = slide.querySelector("[data-discovery]");
      if (shown) {
        // the deck's only anticipation cue: one placard shake 250 ms before the reveal
        M().shakePlacard();
        setTimeout(() => {
          wrap.classList.add("revealed");
          M().releaseCue("A");
          setTimeout(() => M().point(".keynum", { after: "A" }), A().motionAllowed() ? 700 : 0);
        }, A().motionAllowed() ? 250 : 0);
      } else {
        wrap.classList.remove("revealed");
        M().warn({ ms: null, letter: "C" });
      }
    }
    if (frag.classList.contains("trap-note")) trapRings(slide);
  }

  function enter(slide, previous) {
    hideTip();
    returnFocus();
    if (previous) {
      const wrap = previous.querySelector("[data-live-map]");
      if (wrap && wrap._reset) wrap._reset();
      const card = previous.querySelector("[data-trap-card]");
      if (card && !exporting) card.classList.remove("flipped");
      const cu = previous.querySelector('[data-chart="cuisine"]');
      if (cu && cu._reset) cu._reset();
    }
    if (slide.querySelector("[data-threshold]") && stops.length) {
      const def = stops.findIndex((s) => s.threshold === get("thresholds.default"));
      setStop(def, false);
    }
    discoveryState(slide);
    trapRings(slide);
  }

  /** Export mode: every interactive slide in its post-interaction state. */
  function finalStates() {
    document.querySelectorAll("[data-trap-card]").forEach((c) => c.classList.add("flipped"));
    document.querySelectorAll("[data-discovery]").forEach((w) => w.classList.add("revealed"));
    document.querySelectorAll(".trap-ring").forEach((r) => r.classList.add("on"));
  }

  function init(opts) {
    exporting = !!opts.exporting;
    wireTooltips();
    wireToggle();
    wireLiveMap();
    wireSlider();
    wireTrap();
    wireCuisine();
    const chip = document.querySelector(".cover-chip");
    if (chip) chip.addEventListener("click", () => Reveal.next());
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && document.activeElement && document.activeElement.matches("input, button, iframe")) {
        e.stopPropagation();                     // Esc hands the keys back; it does not also open the overview
        returnFocus();
      }
    }, true);
  }

  window.DeckInteractions = { init, enter, fragment, finalStates, returnFocus };
})();
