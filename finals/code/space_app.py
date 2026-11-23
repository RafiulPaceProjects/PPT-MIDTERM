"""LAYA — Multimodal Misinformation Detection: the pack-switching demo.

Hugging Face Space (Gradio, CPU) for Rafiul Haider's Pace University
Analytics Capstone (Fall 2026, CRN 72369), CS 668 Team 3.

DESIGN (Rafiul's spec, 2026-11-22): the app runs on CHANGING THE WEIGHTS
ACCORDING TO THE DATASET. A per-dataset pack registry (below) mirrors the
experiment notebook's pack registry (runs/packs.json): each pack carries
its own native labels, its own two questions (verbatim), its own fake
threshold, and its own AFTER checkpoint repo. Selecting a dataset switches
the questions, the labels and the loaded weights together, and the UI says
what it is serving.

The layout is a visible three-stage pipeline so a visitor can SEE the
input, the processing and the output, with the image on screen throughout:
  1 · INPUT       — image + caption together, one-click examples.
  2 · PROCESSING  — the active pack: which weights, which two questions
                    are being asked, and the arbitration rule.
  3 · OUTPUT      — BEFORE and AFTER columns: class-probability bars, the
                    fake-probability readout, the verdict, an "uncertain"
                    badge when the two questions disagree, and a flip
                    callout when training changed the verdict.

Inference binding (verified live in the 2026-11-22 pipeline rehearsal):
laya.load_vlm(repo, revision=...) + agent.predict(state={"context",
"image"}, questions={native, fake}); choice probabilities at
result["answers"]["native"]["probabilities"], P(Fake) at
result["answers"]["fake"]["noul"].

Numbers come from results.json when the publish stage writes it (out of
final_results_bundle.json); until then the verified BEFORE table below is
shown and AFTER panels say they are pending. Nothing is ever invented.
"""

import json
import os

import gradio as gr

HERE = os.path.dirname(os.path.abspath(__file__))

BASE_MODEL = "thaitea/laya-vision"
BASE_REVISION = "f2fe3c12cb6d04c59d8a190250bf3fb40fc828dc"

_FAKE_Q = {
    "type": "noul",
    "instructions": "Would the dataset assign the item a falsified, distorted, miscaptioned, or out-of-context label rather than its original, pristine, or true label? This is a benchmark-label estimate, not an independent fact-check.",
    "criteria": {
        "false": "The native benchmark label is original, pristine, or true.",
        "true": "The native benchmark label denotes a distortion or incorrect pairing.",
    },
}

PACKS = {
    "mmfakebench": {
        "name": "MMFakeBench",
        "metric": "4-class macro-F1",
        "labels": ["original", "textual_veracity_distortion", "visual_veracity_distortion", "mismatch"],
        "display": {
            "original": "Original",
            "textual_veracity_distortion": "Textual",
            "visual_veracity_distortion": "Visual",
            "mismatch": "Mismatch",
        },
        "fake_labels": ["textual_veracity_distortion", "visual_veracity_distortion", "mismatch"],
        "after_repo": "RafiulHaiderbro/laya-vision-fullft-mmfakebench",
        "noul_threshold": 0.5,
        "questions": {
            "native": {
                "type": "choice",
                "instructions": "Using only the supplied content, which dataset label best describes this item? Predict the benchmark label; do not claim independent factual verification.",
                "criteria": {
                    "original": "Original, undistorted benchmark item.",
                    "textual_veracity_distortion": "The text factual content is fabricated or altered.",
                    "visual_veracity_distortion": "The image is visually distorted or manipulated.",
                    "mismatch": "The image and text do not match.",
                },
            },
            "fake": _FAKE_Q,
        },
    },
    "newsclippings": {
        "name": "NewsCLIPpings",
        "metric": "pairing accuracy",
        "labels": ["pristine", "falsified"],
        "display": {
            "pristine": "Pristine",
            "falsified": "Falsified (out-of-context)",
        },
        "fake_labels": ["falsified"],
        "after_repo": "RafiulHaiderbro/laya-vision-fullft-newsclippings",
        "noul_threshold": 0.5,
        "questions": {
            "native": {
                "type": "choice",
                "instructions": "Using only the supplied content, which dataset label best describes this item? Predict the benchmark label; do not claim independent factual verification.",
                "criteria": {
                    "pristine": "The image and caption are an unaltered, correctly paired news item.",
                    "falsified": "The image and caption were repurposed into an incorrect pairing.",
                },
            },
            "fake": _FAKE_Q,
        },
    },
}
PACK_BY_NAME = {p["name"]: k for k, p in PACKS.items()}

# ---------------------------------------------------------------- results
def _load_results():
    try:
        with open(os.path.join(HERE, "results.json")) as f:
            return json.load(f)
    except Exception:
        return {}

RESULTS = _load_results()

def _temperature(pack_key):
    try:
        return float(RESULTS["temperatures"][pack_key]["choice"])
    except Exception:
        return None

# ---------------------------------------------------------------- models
_models = {}

def _load(pack_key, slot):
    key = (pack_key, slot)
    if key in _models:
        return _models[key]
    import laya

    if slot == "before":
        agent = laya.load_vlm(BASE_MODEL, revision=BASE_REVISION)
    else:
        agent = laya.load_vlm(PACKS[pack_key]["after_repo"], revision="main")
    _models[key] = agent
    return agent

def after_available(pack_key):
    from huggingface_hub import repo_exists

    try:
        return bool(repo_exists(PACKS[pack_key]["after_repo"]))
    except Exception:
        return False

def score(pack_key, slot, image, text):
    """One pack + one checkpoint + one pair -> (display probs, P(Fake))."""
    pack = PACKS[pack_key]
    agent = _load(pack_key, slot)
    result = agent.predict({"context": text, "image": image}, pack["questions"])
    native = result["answers"]["native"]["probabilities"]
    probs = {pack["display"][name]: float(p) for name, p in native.items()}
    if slot == "after":
        t = _temperature(pack_key)
        if t and t > 0:
            import math

            adj = {k: math.exp(math.log(max(v, 1e-9)) / t) for k, v in probs.items()}
            s = sum(adj.values())
            probs = {k: v / s for k, v in adj.items()}
    fake_p = float(result["answers"]["fake"]["noul"])
    return probs, fake_p

def _verdict_note(pack_key, probs, fake_p, slot_label):
    pack = PACKS[pack_key]
    verdict_disp = max(probs, key=probs.get)
    verdict_native = next(n for n, d in pack["display"].items() if d == verdict_disp)
    choice_fake = verdict_native in pack["fake_labels"]
    noul_fake = fake_p >= pack["noul_threshold"]
    badge = ""
    if choice_fake != noul_fake:
        badge = " · ⚠ **uncertain** — the two questions disagree, so the study reports this as uncertain rather than confident"
    return (
        f"**Verdict: {verdict_disp}** ({slot_label}) · fake probability {fake_p:.2f}{badge}",
        verdict_disp,
    )

MODES = ["Compare — before vs after", "Before training (zero-shot)", "After training (fine-tuned)"]

def predict(dataset_name, image, caption, mode):
    pack_key = PACK_BY_NAME[dataset_name]
    pack = PACKS[pack_key]
    empty = (None, None, "", None, None, "", "")
    if image is None or not caption or not caption.strip():
        return (None, None, "Please provide BOTH an image and its caption — the model judges the pair together, and the image stays on screen with the result.", None, None, "", "")
    run_before = mode in (MODES[0], MODES[1])
    run_after = mode in (MODES[0], MODES[2])
    b_probs = b_fake = a_probs = a_fake = None
    b_note = a_note = ""
    b_verdict = a_verdict = None
    if run_before:
        try:
            b_probs, fp = score(pack_key, "before", image, caption.strip())
            b_fake = {"Fake": round(fp, 4), "Not fake": round(1 - fp, 4)}
            b_note, b_verdict = _verdict_note(pack_key, b_probs, fp, "BEFORE — pretrained, zero-shot")
        except Exception as exc:
            b_note = f"BEFORE model call failed: {exc}"
    if run_after:
        if not after_available(pack_key):
            a_note = ("The AFTER checkpoint for this dataset has not been published yet — "
                      "this panel activates automatically once its fine-tuned weights are pushed to the Hub.")
        else:
            try:
                a_probs, fp = score(pack_key, "after", image, caption.strip())
                a_fake = {"Fake": round(fp, 4), "Not fake": round(1 - fp, 4)}
                a_note, a_verdict = _verdict_note(pack_key, a_probs, fp, "AFTER — fine-tuned, this dataset's own weights")
            except Exception as exc:
                a_note = f"AFTER model call failed: {exc}"
    delta = ""
    if b_verdict and a_verdict:
        if b_verdict != a_verdict:
            delta = f"### 🔀 Training changed the verdict: **{b_verdict} → {a_verdict}** on this pair."
        else:
            delta = f"### Same verdict before and after: **{b_verdict}** — compare the confidence bars; calibration is part of the story."
    return b_probs, b_fake, b_note, a_probs, a_fake, a_note, delta

# ---------------------------------------------------------------- text
INTRO = """
# LAYA — Multimodal Misinformation Detection, Before & After Training

**Rafiul Haider · Pace University Analytics Capstone (Fall 2026, CRN 72369) · CS 668 Team 3**
*(Ananya Saravani Ganni, Harika Etikela, Rafiul Haider)*

News posts pair an image with a caption, and either half can be the lie. This study evaluates — and then adapts — **LAYA-Vision**, a small typed-decision vision–language model, on three public benchmarks, each in its native metric: **MMFakeBench** (4-class macro-F1), **NewsCLIPpings** (pairing accuracy), **VERITE** (accuracy, eval-only).

The diagnosis came first: zero-shot, the model sits near chance and **collapses onto one answer** — on 1,000 validation rows it called 289 of 300 mismatch cases correctly but only **1 of 300** originals. A plain TF-IDF baseline beat it. But a logistic probe on the model's *frozen* features beat zero-shot by **+6.24 points** on NewsCLIPpings test — the features know things the decisions don't. So the study fine-tunes (full fine-tuning vs LoRA, on carefully split records, winner selected on a tune split only, test scored once, calibration on a reserved split), **with each dataset getting its own training, its own questions, and its own weights**.

**How to read this page — follow the three panels:** ➊ give the model an image + caption and pick a dataset (the app switches weights to that dataset's own checkpoint); ➋ watch what is being asked and which weights are serving; ➌ read the verdicts, before and after, side by side.
"""

def scoreboard_md():
    if RESULTS.get("scoreboard_md"):
        return RESULTS["scoreboard_md"]
    return ("**Verified BEFORE baselines** — MMFakeBench test macro-F1 **0.2037** · NewsCLIPpings val accuracy **0.5141** · "
            "VERITE accuracy **0.3467**. *AFTER results publish with the experiment run.*")

def serving_md(pack_key):
    pack = PACKS[pack_key]
    return (
        f"**Now serving: {pack['name']}** · native metric: {pack['metric']} · "
        f"BEFORE weights: `{BASE_MODEL}` (pinned) · AFTER weights: `{pack['after_repo']}` · "
        f"fake threshold: {pack['noul_threshold']}"
    )

def processing_md(pack_key):
    pack = PACKS[pack_key]
    q = pack["questions"]
    crit = " · ".join(f"**{pack['display'][k]}** — {v}" for k, v in q["native"]["criteria"].items())
    return f"""
**The pipeline, live:** your image + caption → **LAYA-Vision** (weights switch with the dataset — see the serving line) → **two questions** → one verdict.

**Question 1 — the native choice.** *"{q['native']['instructions']}"*
Options: {crit}

**Question 2 — the fake screen (noul form).** *"{q['fake']['instructions']}"*
Its answer is a probability: P(Fake).

**Arbitration (the study's rule):** the choice question's verdict headlines. If the fake screen disagrees with it (one says fake, the other doesn't, at threshold {pack['noul_threshold']}), the result is flagged **uncertain** instead of confident — watch for the badge in the output panel.
"""

RESULTS_MD = """
## Results — measured, not promised

### BEFORE training (pretrained LAYA-Vision, zero-shot) — verified baselines
| Dataset | Metric | Before |
|---|---|---|
| MMFakeBench (paired, val 1,000 rows) | macro-F1 | **0.2079** |
| MMFakeBench (paired, test ablation) | macro-F1 | **0.2037** |
| NewsCLIPpings (val, 7,024 rows, 0 skipped) | accuracy | **0.5141** |
| VERITE (paired) | accuracy | **0.3467** |
| Per-class recall, 1,000 rows | original / textual / visual / mismatch | 1/300 · 8/300 · 22/100 · 289/300 |
| Calibration (raw) | ECE | ≈ 0.466 |

*Baselines re-measured in the experiment run under the frozen pack protocol (NewsCLIPpings PASS 1, streamed and verified row by row). The October audit measured 0.5083 (NewsCLIPpings) and 0.3566 (VERITE) under the earlier question wording — the small deltas are the wording, not the model.*

Reference points: a TF-IDF baseline reaches 0.4986 accuracy / 0.4156 macro-F1 (grouped OOF) on the development population, and a frozen-feature logistic probe transfers at **57.4%** on NewsCLIPpings test (+6.24 pp over zero-shot). A source-metadata-only rule reaches 0.9150 on MMFakeBench — that is label leakage, and it is excluded everywhere in this study by design.

### AFTER training — per-dataset fine-tuned weights
Published by the experiment run into `results.json` and rendered here: the MMFakeBench winner's test-once macro-F1 with its paired bootstrap, the NewsCLIPpings winner's streamed val accuracy (PASS 2), VERITE transfer, calibration before/after, and the H1–H5 pre-registered verdicts — each as it falls.
"""

def _examples(pack_key):
    """Staged example rows for one pack, or None (fail-soft)."""
    d = os.path.join(HERE, "examples", pack_key)
    try:
        with open(os.path.join(d, "examples.json")) as f:
            ex = json.load(f)
        rows = [[os.path.join(d, e["image"]), e["caption"]] for e in ex]
        return rows or None
    except Exception:
        return None

# ---------------------------------------------------------------- app
with gr.Blocks(title="LAYA — Before / After Training") as demo:
    gr.Markdown(INTRO)
    gr.Markdown(scoreboard_md())
    with gr.Row():
        with gr.Column():
            gr.Markdown("## 1 · Input — the pair, judged together")
            dataset = gr.Dropdown(
                choices=[p["name"] for p in PACKS.values()],
                value="MMFakeBench",
                label="Dataset — switching it switches the weights, questions and labels",
            )
            serving = gr.Markdown(serving_md("mmfakebench"))
            img = gr.Image(type="pil", label="Image — it stays on screen next to your result")
            cap = gr.Textbox(label="Caption / text", lines=4,
                             placeholder="Paste the caption or post text that goes with the image…")
            mode = gr.Radio(MODES, value=MODES[0], label="Which weights run?")
            btn = gr.Button("Run the pair through LAYA", variant="primary")
            _ex_mmf = _examples("mmfakebench")
            ex_mmf = gr.Examples(
                examples=_ex_mmf or [["", ""]], inputs=[img, cap],
                label="Validation examples — one per class (click one, then Run)",
                visible=_ex_mmf is not None,
            )
            _ex_ncp = _examples("newsclippings")
            ex_ncp = gr.Examples(
                examples=_ex_ncp or [["", ""]], inputs=[img, cap],
                label="NewsCLIPpings examples (click one, then Run)",
                visible=False,
            )
        with gr.Column():
            gr.Markdown("## 2 · Processing — what the model is asked")
            proc = gr.Markdown(processing_md("mmfakebench"))
        with gr.Column():
            gr.Markdown("## 3 · Output — the verdicts")
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### BEFORE — zero-shot")
                    b_label = gr.Label(num_top_classes=4, label="Class probabilities")
                    b_fake = gr.Label(num_top_classes=2, label="Fake screen")
                    b_note = gr.Markdown()
                with gr.Column():
                    gr.Markdown("### AFTER — fine-tuned")
                    a_label = gr.Label(num_top_classes=4, label="Class probabilities")
                    a_fake = gr.Label(num_top_classes=2, label="Fake screen")
                    a_note = gr.Markdown()
            delta = gr.Markdown()

    def _on_dataset(name):
        key = PACK_BY_NAME[name]
        return (
            serving_md(key),
            processing_md(key),
            gr.update(visible=(key == "mmfakebench" and _examples("mmfakebench") is not None)),
            gr.update(visible=(key == "newsclippings" and _examples("newsclippings") is not None)),
        )

    dataset.change(_on_dataset, inputs=[dataset], outputs=[serving, proc, ex_mmf, ex_ncp])
    btn.click(
        predict,
        inputs=[dataset, img, cap, mode],
        outputs=[b_label, b_fake, b_note, a_label, a_fake, a_note, delta],
    )
    with gr.Tab("Results"):
        gr.Markdown(RESULTS_MD)
        if RESULTS.get("after_md"):
            gr.Markdown(RESULTS["after_md"])
    gr.Markdown(
        "*Checkpoints: BEFORE = thaitea/laya-vision @ f2fe3c12 (pinned). AFTER = each dataset's own fine-tuned "
        "winner, published by the experiment run. Demo runs on CPU; a first click on a new dataset loads its "
        "weights and can take a few seconds — the image and caption stay on screen while it works.*"
    )

if __name__ == "__main__":
    demo.launch()
