// CS 668 midterm deck: three equal tracks (text, image, combined).
// Build: NODE_PATH=/tmp/deck_tools/node_modules node build_deck.js
// Numbers: combined track from dashboard/results.json and full_probe.json (verified);
// text and image tracks from the teammates' midterm decks as captured in the vault notes.

const path = require("path");
const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa");
const { applyTheme } = require(
  "/Users/rafiulhaider/.claude/skills/synced/7eb42c12-a19a-4b61-8ea1-3c8125ec4ec2_76aeac15-2c46-4749-96f0-05c0b8451a1a/pptx/scripts/apply_theme.js"
);

const OUT = path.join(__dirname, "CS668_three_track_midterm.pptx");
const FIG = path.join(__dirname, "..", "figures");

// Palette: ink navy dominates; one accent per track; grey for floors and references.
const HEX = {
  ink: "1B2333", navy: "16233A", tint: "EEF1F6", white: "FFFFFF",
  text: "0F8B8D", image: "D98E2B", comb: "6A55C9",
  grey: "9AA5B1", greyDark: "5B6676", red: "C8553D", green: "3F8F5B",
  textLight: "9FD4D5", imageLight: "F0C78A", combLight: "BDB2EC",
};
const THEME = {
  name: "CS668 Three Track",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: HEX.ink, lt1: HEX.white, dk2: HEX.navy, lt2: HEX.tint,
    accent1: HEX.text, accent2: HEX.image, accent3: HEX.comb,
    accent4: HEX.grey, accent5: HEX.red, accent6: HEX.green,
    hlink: HEX.text, folHlink: HEX.comb,
  },
};

const TRACK = {
  text: { name: "Text track", owner: "Harika Etikela", hex: HEX.text, light: HEX.textLight, icon: fa.FaNewspaper },
  image: { name: "Image track", owner: "Ananya", hex: HEX.image, light: HEX.imageLight, icon: fa.FaImage },
  comb: { name: "Combined track", owner: "Rafiul Haider", hex: HEX.comb, light: HEX.combLight, icon: fa.FaLayerGroup },
};

async function icon(Comp, hex, px = 256) {
  const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(Comp, { color: "#" + hex, size: px }));
  const buf = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + buf.toString("base64");
}

const shadow = () => ({ type: "outer", color: "000000", opacity: 0.12, blur: 6, offset: 2, angle: 90 });

async function main() {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5 in
  pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
  pres.title = "CS 668 Multimodal Misinformation Detector: midterm";
  pres.author = "Harika Etikela, Ananya, Rafiul Haider";
  const C = pres.SchemeColor;
  const W = 13.333;

  // ---------- layouts ----------
  pres.defineSlideMaster({
    title: "DARK",
    background: { color: C.text2 },
    objects: [
      { placeholder: { options: { name: "title", type: "title", x: 0.8, y: 2.0, w: 11.7, h: 1.4, fontSize: 44, bold: true, color: C.background1, fontFace: THEME.headFontFace, valign: "middle", align: "left", margin: 0 }, text: "" } },
      { placeholder: { options: { name: "body", type: "body", x: 0.8, y: 3.4, w: 11.7, h: 0.8, fontSize: 20, color: C.background2, valign: "top", align: "left", margin: 0 }, text: "" } },
    ],
  });
  pres.defineSlideMaster({
    title: "CONTENT",
    background: { color: C.background1 },
    objects: [
      { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.35, w: 9.4, h: 0.85, fontSize: 32, bold: true, color: C.text1, fontFace: THEME.headFontFace, valign: "middle", align: "left", margin: 0 }, text: "" } },
      { text: { text: "CS 668 · Multimodal Misinformation Detector", options: { x: 0.6, y: 7.0, w: 6, h: 0.3, fontSize: 10, color: C.accent4, margin: 0 } } },
    ],
    slideNumber: { x: 12.3, y: 7.0, w: 0.5, h: 0.3, fontSize: 10, color: C.accent4, align: "right" },
  });

  // ---------- shared pieces ----------
  const icons = {};
  for (const [k, t] of Object.entries(TRACK)) {
    icons[k + "White"] = await icon(t.icon, HEX.white);
    icons[k] = await icon(t.icon, t.hex);
  }
  const extra = {
    info: await icon(fa.FaInfoCircle, HEX.greyDark),
    broom: await icon(fa.FaBroom, HEX.navy), floor: await icon(fa.FaRulerHorizontal, HEX.navy),
    chart: await icon(fa.FaChartBar, HEX.navy), scale: await icon(fa.FaBalanceScale, HEX.navy),
    arrow: await icon(fa.FaArrowRight, HEX.grey), snow: await icon(fa.FaSnowflake, HEX.white),
    lock: await icon(fa.FaLock, HEX.comb), search: await icon(fa.FaSearch, HEX.white),
    merge: await icon(fa.FaCodeBranch, HEX.white), users: await icon(fa.FaUsers, HEX.white),
    bulb: await icon(fa.FaLightbulb, HEX.white),
  };

  const badge = (slide, key) => {
    const t = TRACK[key];
    slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 10.15, y: 0.5, w: 2.6, h: 0.5, rectRadius: 0.25, fill: { color: C[{ text: "accent1", image: "accent2", comb: "accent3" }[key]] }, line: { type: "none" }, objectName: "track badge" });
    slide.addImage({ data: icons[key + "White"], x: 10.3, y: 0.6, w: 0.3, h: 0.3 });
    slide.addText(`${t.name} · ${t.owner}`, { x: 10.65, y: 0.5, w: 2.05, h: 0.5, fontSize: 11, bold: true, color: C.background1, valign: "middle", margin: 0, isTextBox: true, fit: "shrink" });
  };

  const sideNote = (slide, text, y = 1.6, h = 1.5) => {
    slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 10.15, y, w: 2.6, h, rectRadius: 0.12, fill: { color: C.background2 }, line: { type: "none" }, objectName: "good to know card" });
    slide.addImage({ data: extra.info, x: 10.35, y: y + 0.2, w: 0.26, h: 0.26 });
    slide.addText("Good to know", { x: 10.7, y: y + 0.15, w: 1.9, h: 0.36, fontSize: 12, bold: true, color: C.text1, margin: 0, valign: "middle", isTextBox: true });
    slide.addText(text, { x: 10.35, y: y + 0.55, w: 2.25, h: h - 0.7, fontSize: 12, color: C.text1, margin: 0, valign: "top", isTextBox: true });
  };

  const credit = (slide, text) =>
    slide.addText(text, { x: 0.6, y: 6.6, w: 9.4, h: 0.3, fontSize: 10, italic: true, color: C.accent4, margin: 0, isTextBox: true });

  const stat = (slide, { x, y, w, value, label, colorKey, valueSize = 40 }) => {
    slide.addText(value, { x, y, w, h: 0.8, fontSize: valueSize, bold: true, color: C[colorKey], fontFace: THEME.headFontFace, margin: 0, isTextBox: true });
    slide.addText(label, { x, y: y + 0.8, w, h: 0.55, fontSize: 14, color: C.text1, margin: 0, valign: "top", isTextBox: true });
  };

  const axisText = { catAxisLabelColor: HEX.greyDark, valAxisLabelColor: HEX.greyDark, catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt", catAxisLabelFontSize: 12, valAxisLabelFontSize: 11, dataLabelFontFace: "+mn-lt", dataLabelFontSize: 12, dataLabelColor: HEX.ink, valGridLine: { color: "E3E7ED", size: 0.75 }, catGridLine: { style: "none" }, legendFontFace: "+mn-lt", legendFontSize: 12, legendColor: HEX.ink, titleFontFace: "+mn-lt", titleColor: HEX.ink, titleFontSize: 14 };

  // =====================================================================
  // 1. Title
  pres.addSection({ title: "Opening" });
  let s = pres.addSlide({ masterName: "DARK", sectionTitle: "Opening" });
  s.addText("Multimodal Misinformation Detector", { placeholder: "title" });
  s.addText("Three tracks, one question: what does each kind of evidence really tell us?", { placeholder: "body" });
  ["text", "image", "comb"].forEach((k, i) => {
    const t = TRACK[k], x = 0.8 + i * 3.9;
    s.addShape(pres.shapes.OVAL, { x, y: 5.0, w: 0.9, h: 0.9, fill: { color: C[{ text: "accent1", image: "accent2", comb: "accent3" }[k]] }, line: { type: "none" } });
    s.addImage({ data: icons[k + "White"], x: x + 0.22, y: 5.22, w: 0.46, h: 0.46 });
    s.addText([{ text: t.owner, options: { bold: true, breakLine: true } }, { text: t.name }], { x: x + 1.05, y: 4.98, w: 2.7, h: 0.95, fontSize: 16, color: C.background1, valign: "middle", margin: 0, isTextBox: true });
  });
  s.addText("CS 668 Analytics Capstone · Pace University · Midterm", { x: 0.8, y: 6.6, w: 11.7, h: 0.4, fontSize: 14, color: C.accent4, margin: 0, isTextBox: true });
  s.addNotes("All: introduce the team. Our project builds three detectors, one for each way misinformation spreads: false text, fake images, and real images paired with the wrong caption. Harika presents the text track, Ananya the image track, and Rafiul the combined track with the LAYA-Vision model.");

  // 2. One problem, three ways
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Opening" });
  s.addText("One problem, three ways it spreads", { placeholder: "title" });
  const cards = [
    { k: "text", head: "False text", sub: "The claim in the article is wrong", data: "WELFake" },
    { k: "image", head: "Edited or generated image", sub: "The picture itself is fake", data: "CIFAKE" },
    { k: "comb", head: "Real image, wrong caption", sub: "Both are real; the pairing misleads", data: "MMFakeBench · VERITE · NewsCLIPpings" },
  ];
  cards.forEach((c, i) => {
    const x = 0.6 + i * 4.15, t = TRACK[c.k], acc = C[{ text: "accent1", image: "accent2", comb: "accent3" }[c.k]];
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.55, w: 3.85, h: 4.6, rectRadius: 0.15, fill: { color: C.background1 }, line: { color: "E3E7ED", width: 1 }, shadow: shadow(), objectName: c.k + " card" });
    s.addShape(pres.shapes.OVAL, { x: x + 0.35, y: 1.9, w: 1.0, h: 1.0, fill: { color: acc }, line: { type: "none" } });
    s.addImage({ data: icons[c.k + "White"], x: x + 0.6, y: 2.15, w: 0.5, h: 0.5 });
    s.addText(c.head, { x: x + 0.35, y: 3.1, w: 3.2, h: 0.85, fontSize: 22, bold: true, color: C.text1, fontFace: THEME.headFontFace, margin: 0, valign: "top", isTextBox: true });
    s.addText(c.sub, { x: x + 0.35, y: 3.95, w: 3.2, h: 0.7, fontSize: 15, color: C.text1, margin: 0, valign: "top", isTextBox: true });
    s.addText([{ text: t.name, options: { bold: true, color: acc, breakLine: true } }, { text: t.owner }], { x: x + 0.35, y: 4.75, w: 3.2, h: 0.65, fontSize: 14, color: C.text1, margin: 0, isTextBox: true });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.35, y: 5.5, w: 3.15, h: 0.42, rectRadius: 0.21, fill: { color: C.background2 }, line: { type: "none" } });
    s.addText(c.data, { x: x + 0.45, y: 5.5, w: 2.95, h: 0.42, fontSize: 12, color: C.text1, align: "center", valign: "middle", margin: 0, isTextBox: true, fit: "shrink" });
  });
  s.addText("Each track has its own dataset and task, so scores are read within a track, never across tracks.", { x: 0.6, y: 6.35, w: 12.1, h: 0.4, fontSize: 13, italic: true, color: C.accent4, margin: 0, isTextBox: true });
  s.addNotes("Misinformation travels three ways. Sometimes the text is false. Sometimes the image is edited or generated. And often both are real, but a photo from one event is shown with a caption about another. Each of us took one of these and built a detector for it, each on a dataset designed for that problem.");

  // 3. How we work
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Opening" });
  s.addText("How we work, in every track", { placeholder: "title" });
  const tiles = [
    { ic: extra.broom, head: "Clean the data first", sub: "Remove duplicates and leaks before any test" },
    { ic: extra.floor, head: "Start from a floor", sub: "Know what simple guessing scores" },
    { ic: extra.chart, head: "Measure uncertainty", sub: "95% ranges, not single numbers" },
    { ic: extra.scale, head: "Say what it can't do", sub: "Limits travel with every result" },
  ];
  tiles.forEach((t, i) => {
    const x = 0.6 + (i % 2) * 6.15, y = 1.6 + Math.floor(i / 2) * 2.45;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: 5.9, h: 2.1, rectRadius: 0.15, fill: { color: C.background2 }, line: { type: "none" } });
    s.addShape(pres.shapes.OVAL, { x: x + 0.35, y: y + 0.55, w: 1.0, h: 1.0, fill: { color: C.background1 }, line: { type: "none" } });
    s.addImage({ data: t.ic, x: x + 0.6, y: y + 0.8, w: 0.5, h: 0.5 });
    s.addText(t.head, { x: x + 1.65, y: y + 0.45, w: 4.0, h: 0.6, fontSize: 22, bold: true, color: C.text1, fontFace: THEME.headFontFace, margin: 0, isTextBox: true });
    s.addText(t.sub, { x: x + 1.65, y: y + 1.05, w: 4.0, h: 0.6, fontSize: 16, color: C.text1, margin: 0, valign: "top", isTextBox: true });
  });
  s.addNotes("All three tracks follow the same habits. We clean duplicates and leaks before testing. We always compare against what guessing would score. We report uncertainty ranges. And every result comes with its limits.");

  // =====================================================================
  // TEXT TRACK
  pres.addSection({ title: "Text track (Harika)" });
  // 4. WELFake data
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Text track (Harika)" });
  s.addText("Real and fake articles leave different clues", { placeholder: "title" });
  badge(s, "text");
  stat(s, { x: 0.6, y: 1.55, w: 3.0, value: "63,678", label: "articles after removing 8,456 duplicates", colorKey: "accent1" });
  stat(s, { x: 0.6, y: 3.15, w: 3.0, value: "70 · 15 · 15", label: "train · validation · test split", colorKey: "accent1", valueSize: 32 });
  stat(s, { x: 0.6, y: 4.75, w: 3.0, value: "54.6%", label: "accuracy from always guessing \"Real\"", colorKey: "accent4" });
  s.addChart(pres.charts.BAR, [
    { name: "Real", labels: ['Mentions "reuters"', 'Has an "!"', 'Mentions "video"'], values: [61.8, 8, 7.6] },
    { name: "Fake", labels: ['Mentions "reuters"', 'Has an "!"', 'Mentions "video"'], values: [1.6, 35, 34.4] },
  ], { x: 3.9, y: 1.45, w: 5.9, h: 4.9, barDir: "bar", barGrouping: "clustered", chartColors: [HEX.grey, HEX.text], showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: '0.0"%"', valAxisMaxVal: 75, valAxisMinVal: 0, valAxisHidden: true, showLegend: true, legendPos: "t", showTitle: true, title: "Share of training articles (%)", ...axisText, catAxisOrientation: "maxMin" });
  sideNote(s, "Strong source and style cues mean a model can learn the outlet's style, not only the facts.", 1.6, 1.9);
  credit(s, "Text track midterm results, Harika Etikela (WELFake training split).");
  s.addNotes("Harika: WELFake has 72,134 news articles; after removing 8,456 exact duplicates we keep 63,678 and freeze a 70/15/15 split. Real and fake articles look different: most real articles mention Reuters, while fake ones use far more exclamation marks and the word video. Always guessing Real gives 54.6%, which is our floor.");

  // 5. Models
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Text track (Harika)" });
  s.addText("From simple to deep models", { placeholder: "title" });
  badge(s, "text");
  const tLabels = ["Naive Bayes", "Random Forest", "Logistic Regression", "Linear SVM (cleaned text)", "Linear SVM (raw text)", "DistilBERT (early run)"];
  s.addChart(pres.charts.BAR, [
    { name: "TF-IDF models", labels: tLabels, values: [87.6, 93.84, 95.24, 96.49, 97.44, 0] },
    { name: "Transformer", labels: tLabels, values: [0, 0, 0, 0, 0, 98.28] },
  ], { x: 0.6, y: 1.45, w: 9.2, h: 5.0, barDir: "bar", barGrouping: "stacked", chartColors: [HEX.text, HEX.textLight], showValue: true, dataLabelPosition: "inEnd", dataLabelFormatCode: '0.00"%";;;', dataLabelColor: HEX.white, valAxisMinVal: 50, valAxisMaxVal: 100, valAxisLabelFormatCode: '0"%"', showLegend: true, legendPos: "t", showTitle: true, title: "Test accuracy (9,552 articles)", ...axisText, dataLabelColor: HEX.white, catAxisOrientation: "maxMin" });
  sideNote(s, "DistilBERT is an early run: 5,000 training articles, one epoch. It does not yet show transformers are better.", 1.6, 2.1);
  credit(s, "Text track midterm results, Harika Etikela. Axis starts at 50%.");
  s.addNotes("Harika: we compared four classical models on TF-IDF features. Accuracy rises from 87.6% for Naive Bayes to 97.4% for a linear SVM on raw text. A first DistilBERT run reached 98.3%, but it used only 5,000 articles for one epoch, so we treat it as exploratory.");

  // 6. What text learned
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Text track (Harika)" });
  s.addText("Words carry the signal, partly through style", { placeholder: "title" });
  badge(s, "text");
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.6, y: 1.6, w: 4.6, h: 3.9, rectRadius: 0.15, fill: { color: C.background2 }, line: { type: "none" } });
  s.addText("97.4%", { x: 0.9, y: 1.9, w: 2.0, h: 0.9, fontSize: 40, bold: true, color: C.accent1, fontFace: THEME.headFontFace, margin: 0, isTextBox: true });
  s.addImage({ data: extra.arrow, x: 2.85, y: 2.15, w: 0.45, h: 0.45 });
  s.addText("96.2%", { x: 3.35, y: 1.9, w: 1.8, h: 0.9, fontSize: 40, bold: true, color: C.accent4, fontFace: THEME.headFontFace, margin: 0, isTextBox: true });
  s.addText('Linear SVM test accuracy with the word "reuters" removed', { x: 0.9, y: 2.9, w: 4.0, h: 0.7, fontSize: 15, color: C.text1, margin: 0, isTextBox: true });
  s.addText("About 1.3 points come from a single source word.", { x: 0.9, y: 3.8, w: 4.0, h: 0.9, fontSize: 16, bold: true, color: C.text1, margin: 0, isTextBox: true });
  s.addText("Next for the text track", { x: 5.6, y: 1.6, w: 4.2, h: 0.5, fontSize: 18, bold: true, color: C.text1, fontFace: THEME.headFontFace, margin: 0, isTextBox: true });
  const tNext = [["Ensemble", "SVM + DistilBERT, soft voting"], ["Explanations", "LIME and SHAP feature comparison"], ["New datasets", "ISOT and LIAR, no retraining"]];
  tNext.forEach(([h, d], i) => {
    const y = 2.25 + i * 1.1;
    s.addShape(pres.shapes.OVAL, { x: 5.6, y, w: 0.75, h: 0.75, fill: { color: C.accent1 }, line: { type: "none" } });
    s.addText(String(i + 1), { x: 5.6, y, w: 0.75, h: 0.75, fontSize: 18, bold: true, color: C.background1, align: "center", valign: "middle", margin: 0, isTextBox: true });
    s.addText([{ text: h, options: { bold: true, breakLine: true } }, { text: d }], { x: 6.55, y: y - 0.05, w: 3.3, h: 0.85, fontSize: 14, color: C.text1, margin: 0, valign: "middle", isTextBox: true });
  });
  sideNote(s, "Results so far report accuracy; precision, recall and F1 come with the next phase.", 1.6, 1.7);
  credit(s, "Text track midterm results, Harika Etikela.");
  s.addNotes("Harika: removing just the word Reuters drops the SVM from 97.4% to 96.2%, so part of the score is outlet style. Next we build the SVM plus DistilBERT ensemble, compare features with LIME and SHAP, and test on ISOT and LIAR without retraining.");

  // =====================================================================
  // IMAGE TRACK
  pres.addSection({ title: "Image track (Ananya)" });
  // 7. CIFAKE clean first
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Image track (Ananya)" });
  s.addText("Clean first, then test", { placeholder: "title" });
  badge(s, "image");
  const steps = [
    { head: "120,000", sub: "CIFAKE images, 32×32\nhalf real, half generated" },
    { head: "Duplicate audit", sub: "2,218 train · 454 test\n378 shared across splits" },
    { head: "Clean split", sub: "10,000 · 1,996 · 3,986\n0 images shared with train" },
  ];
  steps.forEach((st, i) => {
    const x = 0.6 + i * 3.2;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 2.0, w: 2.75, h: 2.6, rectRadius: 0.15, fill: { color: i === 2 ? C.accent2 : C.background2 }, line: { type: "none" }, shadow: shadow() });
    s.addText(st.head, { x: x + 0.2, y: 2.3, w: 2.35, h: 0.8, fontSize: i === 0 ? 34 : 22, bold: true, color: i === 2 ? C.background1 : C.text1, fontFace: THEME.headFontFace, margin: 0, align: "center", valign: "middle", isTextBox: true });
    s.addText(st.sub, { x: x + 0.2, y: 3.2, w: 2.35, h: 1.1, fontSize: 14, color: i === 2 ? C.background1 : C.text1, margin: 0, align: "center", valign: "top", isTextBox: true });
    if (i < 2) s.addImage({ data: extra.arrow, x: x + 2.83, y: 3.1, w: 0.32, h: 0.32 });
  });
  s.addText("Train · validation · test images in the clean working subset", { x: 6.9, y: 4.75, w: 2.9, h: 0.6, fontSize: 12, italic: true, color: C.accent4, margin: 0, isTextBox: true });
  sideNote(s, "Pixel-identical copies were found across splits and removed before the final run, so test scores are not inflated.", 1.6, 2.1);
  credit(s, "Image track midterm results, Ananya (CIFAKE: Bird and Lotfi, 2024).");
  s.addNotes("Ananya: CIFAKE has 120,000 tiny images, half real from CIFAR-10 and half generated by Stable Diffusion. Before training, an audit found thousands of duplicates, including 378 files shared between train and test. We removed them and built a clean working split of 10,000, 1,996 and 3,986 images with zero overlap.");

  // 8. Image ladder
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Image track (Ananya)" });
  s.addText("Climbing the model ladder", { placeholder: "title" });
  badge(s, "image");
  const iLabels = ["Always guess", "21 features + LogReg", "21 features + Random Forest", "ResNet18 frozen", "Small CNN", "ResNet18 fine-tuned"];
  s.addChart(pres.charts.BAR, [
    { name: "Baselines", labels: iLabels, values: [49.8, 86.8, 87.9, 88.1, 94.2, 0] },
    { name: "Best", labels: iLabels, values: [0, 0, 0, 0, 0, 96.3] },
  ], { x: 0.6, y: 1.45, w: 6.4, h: 5.0, barDir: "bar", barGrouping: "stacked", chartColors: [HEX.imageLight, HEX.image], showValue: true, dataLabelPosition: "inEnd", dataLabelFormatCode: '0.0"%";;;', valAxisMinVal: 0, valAxisMaxVal: 100, valAxisLabelFormatCode: '0"%"', showLegend: false, showTitle: true, title: "Test accuracy (3,986 images)", ...axisText, catAxisOrientation: "maxMin" });
  stat(s, { x: 7.3, y: 1.8, w: 2.6, value: "96.3%", label: "fine-tuned ResNet18 accuracy", colorKey: "accent2" });
  stat(s, { x: 7.3, y: 3.45, w: 2.6, value: "0.995", label: "AUC for the same model", colorKey: "accent2" });
  stat(s, { x: 7.3, y: 5.1, w: 2.6, value: "39×", label: "smaller small CNN, only 2.1 points behind", colorKey: "accent4", valueSize: 32 });
  sideNote(s, "One run so far; three seeds and the full training set are planned.", 1.6, 1.6);
  credit(s, "Image track midterm results, Ananya. 95% range for ResNet18: 95.7% to 96.8%.");
  s.addNotes("Ananya: we climbed a ladder of models. Guessing gets about 50%. Twenty-one handcrafted features reach about 87%. A small CNN reaches 94.2%, and fine-tuned ResNet18 reaches 96.3% with an AUC of 0.995. The small CNN is 39 times smaller for only 2.1 points less.");

  // 9. What the model looks at
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Image track (Ananya)" });
  s.addText("Fine detail, not color, carries the signal", { placeholder: "title" });
  badge(s, "image");
  s.addChart(pres.charts.BAR, [{ name: "ResNet18", labels: ["Clean test", "Mild blur (σ = 0.5)"], values: [96.3, 85.6] }],
    { x: 0.6, y: 1.45, w: 4.6, h: 4.9, barDir: "col", chartColors: [HEX.image], showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: '0.0"%"', valAxisMinVal: 0, valAxisMaxVal: 100, valAxisLabelFormatCode: '0"%"', showLegend: false, showTitle: true, title: "Fine-tuned ResNet18 accuracy", ...axisText });
  const chips = [["Strong blur (σ = 1)", "AUC 0.995 → 0.77"], ["Grayscale", "AUC stays 0.98"], ["JPEG quality 75", "No change"]];
  chips.forEach(([h, d], i) => {
    const y = 1.7 + i * 1.25;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 5.6, y, w: 4.2, h: 1.0, rectRadius: 0.12, fill: { color: C.background2 }, line: { type: "none" } });
    s.addText([{ text: h, options: { bold: true, breakLine: true } }, { text: d, options: { color: C.accent2, bold: true } }], { x: 5.85, y, w: 3.8, h: 1.0, fontSize: 16, color: C.text1, margin: 0, valign: "middle", isTextBox: true });
  });
  s.addText("Next: test on images from other generators and real-photo sources.", { x: 5.6, y: 5.55, w: 4.2, h: 0.75, fontSize: 15, bold: true, color: C.text1, margin: 0, isTextBox: true });
  sideNote(s, "Grad-CAM shows where the model looks; it is not proof of a true generator fingerprint.", 1.6, 1.9);
  credit(s, "Image track midterm results, Ananya.");
  s.addNotes("Ananya: stress tests show what the model relies on. A mild blur drops accuracy from 96.3% to 85.6%, and a strong blur drops AUC to 0.77, while grayscale and JPEG compression barely matter. So the model uses fine detail, not color. Next we test it on generators it has never seen.");

  // =====================================================================
  // COMBINED TRACK
  pres.addSection({ title: "Combined track (Rafiul)" });
  // 10. Setup
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Combined track (Rafiul)" });
  s.addText("What does a pretrained model already know?", { placeholder: "title" });
  badge(s, "comb");
  const flow = [["Image + caption", C.background2, C.text1], ["LAYA-Vision", C.accent3, C.background1], ["Answer", C.background2, C.text1]];
  flow.forEach(([t, fill, col], i) => {
    const x = 0.6 + i * 3.15;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.6, w: 2.7, h: 1.2, rectRadius: 0.15, fill: { color: fill }, line: { type: "none" }, shadow: shadow() });
    s.addText(t, { x, y: 1.6, w: 2.7, h: 1.2, fontSize: 20, bold: true, color: col, align: "center", valign: "middle", margin: 0, isTextBox: true });
    if (i < 2) s.addImage({ data: extra.arrow, x: x + 2.78, y: 2.03, w: 0.32, h: 0.32 });
  });
  s.addImage({ data: extra.snow, x: 3.9, y: 1.72, w: 0.28, h: 0.28 });
  s.addText("Frozen: no training, no prompt tuning", { x: 3.15, y: 2.9, w: 3.3, h: 0.4, fontSize: 12, italic: true, color: C.accent3, align: "center", margin: 0, isTextBox: true });
  const dsets = [["MMFakeBench", "10,000 test rows", "4 labels"], ["VERITE", "1,001 rows", "3 labels"], ["NewsCLIPpings", "7,024 pairs", "2 labels"]];
  dsets.forEach(([n, r, l], i) => {
    const x = 0.6 + i * 3.15;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 3.6, w: 2.7, h: 1.45, rectRadius: 0.12, fill: { color: C.background1 }, line: { color: HEX.combLight, width: 1.5 } });
    s.addText([{ text: n, options: { bold: true, fontSize: 18, breakLine: true } }, { text: r, options: { breakLine: true } }, { text: l }], { x: x + 0.15, y: 3.6, w: 2.4, h: 1.45, fontSize: 14, color: C.text1, align: "center", valign: "middle", margin: 0, isTextBox: true });
  });
  s.addText("Same rows, three ways: image + text · text only · image only", { x: 0.6, y: 5.35, w: 9.2, h: 0.5, fontSize: 16, bold: true, color: C.accent3, margin: 0, isTextBox: true });
  sideNote(s, "This is the reference point a fine-tuned model must beat later.", 1.6, 1.5);
  credit(s, "Combined track, Rafiul Haider. LAYA-Vision checkpoint f2fe3c12, one fixed question set.");
  s.addNotes("Rafiul: before fine-tuning, we asked what the pretrained LAYA-Vision model already knows. We froze it and asked each dataset's own question on three benchmarks, using the same rows with the image and text, the text only, and the image only. That gives the reference a fine-tuned model has to beat.");

  // 11. Asked cold
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Combined track (Rafiul)" });
  s.addText("Asked cold, it mostly guesses", { placeholder: "title" });
  badge(s, "comb");
  s.addChart(pres.charts.BAR, [
    { name: "LAYA-Vision (image + text)", labels: ["MMFakeBench", "VERITE", "NewsCLIPpings"], values: [26.4, 35.7, 50.8] },
    { name: "Guessing floor", labels: ["MMFakeBench", "VERITE", "NewsCLIPpings"], values: [30.0, 33.3, 50.0] },
  ], { x: 0.6, y: 1.45, w: 5.6, h: 5.0, barDir: "col", barGrouping: "clustered", chartColors: [HEX.comb, HEX.grey], showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: '0.0"%"', valAxisMinVal: 0, valAxisMaxVal: 70, valAxisLabelFormatCode: '0"%"', showLegend: true, legendPos: "t", showTitle: true, title: "Accuracy", ...axisText });
  [["91.5%", "of MMFakeBench labels guessed from source names alone, without seeing the image or text"], ["−1.5 pts", "average change when the model also sees the image (from −18 to +18 by source)"]].forEach(([v, l], i) => {
    const y = 1.6 + i * 2.45;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.5, y, w: 3.3, h: 2.15, rectRadius: 0.15, fill: { color: C.background2 }, line: { type: "none" } });
    s.addText(v, { x: 6.75, y: y + 0.15, w: 2.9, h: 0.8, fontSize: 36, bold: true, color: C.accent3, fontFace: THEME.headFontFace, margin: 0, isTextBox: true });
    s.addText(l, { x: 6.75, y: y + 0.95, w: 2.9, h: 1.1, fontSize: 13, color: C.text1, margin: 0, valign: "top", isTextBox: true });
  });
  sideNote(s, "The MMFakeBench test split had been looked at before, so its numbers are a check-up, not a final exam.", 1.6, 2.1);
  credit(s, "Combined track, Rafiul Haider. n = 9,999 · 1,001 · 7,024. Floors: always-majority, 1 in 3, coin flip.");
  s.addNotes("Rafiul: asked cold, the model is close to guessing on all three: 26.4% on MMFakeBench where always picking the most common answer gets 30%, 35.7% on VERITE against one in three, and 50.8% on NewsCLIPpings against a coin flip. Two surprises: on MMFakeBench, the source names alone predict 91.5% of the labels. And adding the image lowered accuracy by 1.5 points on average, with large swings by source.");

  // 12. Signal is there
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Combined track (Rafiul)" });
  s.addText("The signal is there, just unused", { placeholder: "title" });
  badge(s, "comb");
  s.addChart(pres.charts.BAR, [
    { name: "Asked cold", labels: ["NewsCLIPpings test (sealed)", "VERITE true vs out-of-context"], values: [51.1, 50.5] },
    { name: "With a small trained helper", labels: ["NewsCLIPpings test (sealed)", "VERITE true vs out-of-context"], values: [57.4, 54.9] },
  ], { x: 0.6, y: 1.45, w: 5.6, h: 5.0, barDir: "col", barGrouping: "clustered", chartColors: [HEX.combLight, HEX.comb], showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: '0.0"%"', valAxisMinVal: 0, valAxisMaxVal: 80, valAxisLabelFormatCode: '0"%"', showLegend: true, legendPos: "t", showTitle: true, title: "Accuracy", ...axisText });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.5, y: 1.6, w: 3.3, h: 2.6, rectRadius: 0.15, fill: { color: C.accent3 }, line: { type: "none" }, shadow: shadow() });
  s.addText("+6.2 pts", { x: 6.75, y: 1.8, w: 2.9, h: 0.85, fontSize: 40, bold: true, color: C.background1, fontFace: THEME.headFontFace, margin: 0, isTextBox: true });
  s.addText("on 7,264 sealed test pairs, read once (95% range +4.8 to +7.7)", { x: 6.75, y: 2.7, w: 2.9, h: 1.3, fontSize: 14, color: C.background1, margin: 0, valign: "top", isTextBox: true });
  s.addImage({ data: extra.lock, x: 6.6, y: 4.55, w: 0.4, h: 0.4 });
  s.addText("The helper learns from 71,072 NewsCLIPpings examples on top of the frozen model; the model itself never changes.", { x: 7.1, y: 4.45, w: 2.75, h: 1.6, fontSize: 13, color: C.text1, margin: 0, valign: "top", isTextBox: true });
  sideNote(s, "On VERITE the gain (+4.4 pts) sits inside its 95% range of zero, so it may be luck.", 1.6, 1.9);
  credit(s, "Combined track, Rafiul Haider. Helper = linear probe on frozen 576-d LAYA-Vision features.");
  s.addNotes("Rafiul: published systems train on NewsCLIPpings and test on the target, so we did the same without changing the model. A small linear helper trained on the model's frozen features raised accuracy from 51.1% to 57.4% on a test set we kept sealed until the end. So the information is inside the model; its direct answer just does not use it. On VERITE the gain is smaller and could be chance.");

  // =====================================================================
  // TOGETHER
  pres.addSection({ title: "Together" });
  // 13. What the tracks teach
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Together" });
  s.addText("What the three tracks teach together", { placeholder: "title" });
  const lessons = [
    { k: "text", good: "Strong signal from words", catch: 'Part of it is outlet style ("reuters")' },
    { k: "image", good: "Strong on its own benchmark", catch: "Mild blur costs about 11 points" },
    { k: "comb", good: "The signal sits inside the model", catch: "Source names give MMFakeBench labels away" },
  ];
  lessons.forEach((l, i) => {
    const x = 0.6 + i * 4.15, t = TRACK[l.k], acc = C[{ text: "accent1", image: "accent2", comb: "accent3" }[l.k]];
    s.addShape(pres.shapes.OVAL, { x: x + 1.45, y: 1.5, w: 1.0, h: 1.0, fill: { color: acc }, line: { type: "none" } });
    s.addImage({ data: icons[l.k + "White"], x: x + 1.7, y: 1.75, w: 0.5, h: 0.5 });
    s.addText(t.name, { x, y: 2.6, w: 3.9, h: 0.45, fontSize: 18, bold: true, color: acc, align: "center", margin: 0, isTextBox: true });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 3.15, w: 3.85, h: 1.2, rectRadius: 0.12, fill: { color: C.background2 }, line: { type: "none" } });
    s.addText(l.good, { x: x + 0.2, y: 3.15, w: 3.45, h: 1.2, fontSize: 16, bold: true, color: C.text1, align: "center", valign: "middle", margin: 0, isTextBox: true });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 4.5, w: 3.85, h: 1.2, rectRadius: 0.12, fill: { color: C.background1 }, line: { color: "E3E7ED", width: 1 } });
    s.addText(l.catch, { x: x + 0.2, y: 4.5, w: 3.45, h: 1.2, fontSize: 15, color: C.text1, align: "center", valign: "middle", margin: 0, isTextBox: true });
  });
  s.addText("Every benchmark hides a shortcut. Finding it is part of the result.", { x: 0.6, y: 5.95, w: 12.1, h: 0.55, fontSize: 20, bold: true, italic: true, color: C.text2, fontFace: THEME.headFontFace, align: "center", margin: 0, isTextBox: true });
  s.addNotes("All: put together, each track found real signal and a weak spot. Text models read outlet style. The image model depends on fine detail that blur removes. And on MMFakeBench, source names give the labels away. We are not ranking the tracks; the tasks differ. The shared lesson is that every benchmark hides a shortcut.");

  // 14. Road to final
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Together" });
  s.addText("Road to the final", { placeholder: "title" });
  const lanes = [
    { k: "text", items: ["Ensemble", "LIME / SHAP", "ISOT and LIAR"] },
    { k: "image", items: ["Unseen generators", "Three seeds", "Full training set"] },
    { k: "comb", items: ["Attention and Gate heads", "CLIP classifier", "Three seeds"] },
  ];
  lanes.forEach((ln, i) => {
    const y = 1.55 + i * 1.45, t = TRACK[ln.k], acc = C[{ text: "accent1", image: "accent2", comb: "accent3" }[ln.k]];
    s.addShape(pres.shapes.OVAL, { x: 0.6, y: y + 0.1, w: 0.8, h: 0.8, fill: { color: acc }, line: { type: "none" } });
    s.addImage({ data: icons[ln.k + "White"], x: 0.8, y: y + 0.3, w: 0.4, h: 0.4 });
    s.addText(t.name, { x: 1.55, y: y + 0.1, w: 1.7, h: 0.8, fontSize: 15, bold: true, color: acc, valign: "middle", margin: 0, isTextBox: true });
    ln.items.forEach((it, j) => {
      const x = 3.3 + j * 2.25;
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: y + 0.12, w: 2.05, h: 0.76, rectRadius: 0.12, fill: { color: C.background2 }, line: { type: "none" } });
      s.addText(it, { x: x + 0.1, y: y + 0.12, w: 1.85, h: 0.76, fontSize: 14, color: C.text1, align: "center", valign: "middle", margin: 0, isTextBox: true, fit: "shrink" });
    });
  });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 3.3, y: 5.95, w: 6.55, h: 0.75, rectRadius: 0.15, fill: { color: C.text2 }, line: { type: "none" } });
  s.addImage({ data: extra.merge, x: 3.5, y: 6.12, w: 0.4, h: 0.4 });
  s.addText("One shared output format → one app that gives a verdict for text, image or both", { x: 4.0, y: 5.95, w: 5.75, h: 0.75, fontSize: 14, bold: true, color: C.background1, valign: "middle", margin: 0, isTextBox: true });
  sideNote(s, "The combined track's stretch targets (84.8% and 76.3%) come from fully trained systems and are not met yet.", 1.6, 2.1);
  s.addNotes("All: for the final, Harika adds the ensemble, explanations and two new datasets. Ananya tests on unseen generators with three seeds. Rafiul trains Attention and Gate heads on the frozen model and adds a CLIP classifier. Then we agree on one output format and build a single app that gives a verdict for text, an image, or both.");

  // 15. Thank you
  s = pres.addSlide({ masterName: "DARK", sectionTitle: "Together" });
  s.addText("Thank you", { placeholder: "title" });
  s.addText("Questions welcome", { placeholder: "body" });
  ["text", "image", "comb"].forEach((k, i) => {
    const t = TRACK[k], x = 0.8 + i * 3.9;
    s.addShape(pres.shapes.OVAL, { x, y: 5.0, w: 0.9, h: 0.9, fill: { color: C[{ text: "accent1", image: "accent2", comb: "accent3" }[k]] }, line: { type: "none" } });
    s.addImage({ data: icons[k + "White"], x: x + 0.22, y: 5.22, w: 0.46, h: 0.46 });
    s.addText([{ text: t.owner, options: { bold: true, breakLine: true } }, { text: t.name }], { x: x + 1.05, y: 4.98, w: 2.7, h: 0.95, fontSize: 16, color: C.background1, valign: "middle", margin: 0, isTextBox: true });
  });
  s.addNotes("All: thank you. We are happy to take questions on any of the three tracks.");

  // =====================================================================
  // BACKUP
  pres.addSection({ title: "Backup" });
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Backup" });
  s.addText("Backup: published systems on NewsCLIPpings", { placeholder: "title" });
  badge(s, "comb");
  const pLabels = ["This study, asked cold", "This study, with helper", "CLIP, fine-tuned", "LAMAR Attention", "CCN", "SNIFFER"];
  s.addChart(pres.charts.BAR, [
    { name: "This study", labels: pLabels, values: [51.1, 57.4, 0, 0, 0, 0] },
    { name: "Published", labels: pLabels, values: [0, 0, 60.2, 84.8, 84.7, 88.4] },
  ], { x: 0.6, y: 1.45, w: 9.2, h: 5.0, barDir: "bar", barGrouping: "stacked", chartColors: [HEX.comb, HEX.grey], showValue: true, dataLabelPosition: "inEnd", dataLabelFormatCode: '0.0"%";;;', dataLabelColor: HEX.white, valAxisMinVal: 0, valAxisMaxVal: 100, valAxisLabelFormatCode: '0"%"', showLegend: true, legendPos: "t", showTitle: true, title: "NewsCLIPpings test accuracy", ...axisText, dataLabelColor: HEX.white, catAxisOrientation: "maxMin" });
  sideNote(s, "Published systems retrain the whole model; CCN and SNIFFER also search the web. These are reference points, not a ranking.", 1.6, 2.3);
  credit(s, "Values checked against each paper's results table on 25 Oct 2026.");
  s.addNotes("Backup: published systems reach 60% to 88% on the same test split, but they retrain their whole model, and two of them look up evidence online.");

  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Backup" });
  s.addText("Backup: the image effect by source", { placeholder: "title" });
  badge(s, "comb");
  s.addImage({ path: path.join(FIG, "03_image_effect_by_pair.png"), x: 0.6, y: 1.4, w: 6.9, h: 4.8, sizing: { type: "contain", w: 6.9, h: 4.8 } });
  sideNote(s, "On 13 of 14 sources every row has the same label, so the image mainly changes which answer the model picks.", 1.6, 2.1);
  credit(s, "MMFakeBench test, 9,999 rows, paired minus text-only accuracy with 95% ranges.");
  s.addNotes("Backup: split by source, the image effect ranges from minus 18 to plus 18 points; the average of minus 1.5 hides that spread.");

  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Backup" });
  s.addText("Backup: where the model's answers go", { placeholder: "title" });
  badge(s, "comb");
  s.addImage({ path: path.join(FIG, "02_confusion_matrices.png"), x: 0.6, y: 1.6, w: 12.1, h: 4.0, sizing: { type: "contain", w: 12.1, h: 4.0 } });
  credit(s, "Zero-shot, image + text. MMFakeBench test (9,999), VERITE (1,001), NewsCLIPpings validation (7,024).");
  s.addNotes("Backup: confusion matrices for the three zero-shot runs.");

  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Backup" });
  s.addText("Backup: where to find everything", { placeholder: "title" });
  const finds = [["Showcase folder", "MIDTERM_PRETRAINED_BASELINE/README.md"], ["Executed notebooks", "notebooks/01 to 04, each with self-checks"], ["Detailed dashboard", "http://localhost:8501"], ["Plain-language dashboard", "http://localhost:8502"]];
  finds.forEach(([h, d], i) => {
    const x = 0.6 + (i % 2) * 6.15, y = 1.6 + Math.floor(i / 2) * 2.0;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: 5.9, h: 1.6, rectRadius: 0.15, fill: { color: C.background2 }, line: { type: "none" } });
    s.addText([{ text: h, options: { bold: true, fontSize: 18, breakLine: true } }, { text: d, options: { fontSize: 14 } }], { x: x + 0.3, y, w: 5.3, h: 1.6, color: C.text1, valign: "middle", margin: 0, isTextBox: true });
  });
  s.addNotes("Backup: the showcase folder holds the synthesis, notebooks, figures and reports for the combined track.");

  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("wrote " + OUT);
}

main().catch((e) => { console.error(e); process.exit(1); });
