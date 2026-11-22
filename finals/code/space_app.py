"""LAYA — Multimodal Misinformation Detection: Before / After Training.

Hugging Face Space (Gradio, CPU) for Rafiul Haider's Pace University
Analytics Capstone (Fall 2026, CRN 72369), CS 668 Team 3.

The app shows the SAME image+text test through two checkpoints:
  BEFORE — the pretrained LAYA-Vision checkpoint, zero-shot (pinned revision).
  AFTER  — the fine-tuned winner checkpoint, published to the Hub by the
           experiment notebook after training. Until that repo exists, the
           AFTER panel says so plainly instead of failing.

Inference binding note: score_pair() is the single model-specific call. It
uses the REAL laya API, verified live in the 2026-11-22 pipeline rehearsal
(rehearsal Stage 7): laya.load_vlm(repo, revision=...) + agent.predict(
state={"context": caption, "image": PIL image}, questions={native, fake}),
probabilities at result["answers"]["native"]["probabilities"] and the fake
probability at result["answers"]["fake"]["noul"]. (An earlier draft bound
AutoModelForCausalLM + an invented prompt against the text-model repo; the
rehearsal proved that binding wrong and it has been replaced.)
"""

import os

import gradio as gr

BEFORE_MODEL = os.environ.get("BEFORE_MODEL", "thaitea/laya-vision")
BEFORE_REVISION = os.environ.get(
    "BEFORE_REVISION", "f2fe3c12cb6d04c59d8a190250bf3fb40fc828dc"
)
AFTER_MODEL = os.environ.get("AFTER_MODEL", "RafiulHaiderbro/laya-vision-fullft-mmfakebench")
AFTER_REVISION = os.environ.get("AFTER_REVISION", "main")

CLASSES = ["original", "textual", "visual", "mismatch"]

# The model's native class names (the criteria keys of the study's frozen
# four-way question) mapped to the short display classes used above.
NATIVE_TO_DISPLAY = {
    "original": "original",
    "textual_veracity_distortion": "textual",
    "visual_veracity_distortion": "visual",
    "mismatch": "mismatch",
}

# The study's frozen questions, verbatim (data/workflows/
# run_laya_vision_validation.py in the team workspace): the native four-way
# choice question, and the binary Fake/True question in 'noul' form, whose
# answer carries P(Fake) directly.
QUESTIONS = {
    "native": {
        "type": "choice",
        "instructions": "Which MMFakeBench four-way class best describes this item, using both the image and the supplied text?",
        "criteria": {
            "original": "Original, undistorted benchmark item.",
            "textual_veracity_distortion": "The text factual content is fabricated or altered.",
            "visual_veracity_distortion": "The image is visually distorted or manipulated.",
            "mismatch": "The image and text do not match.",
        },
    },
    "fake": {
        "type": "noul",
        "instructions": "Would MMFakeBench assign this item the binary label Fake rather than True?",
        "criteria": {"false": "The benchmark label is True.", "true": "The benchmark label is Fake."},
    },
}

_models = {}


def _load(slot):
    """Load (once) and cache the laya agent for a slot (BEFORE / AFTER)."""
    if slot in _models:
        return _models[slot]
    import laya

    repo, rev = (
        (BEFORE_MODEL, BEFORE_REVISION) if slot == "before" else (AFTER_MODEL, AFTER_REVISION)
    )
    agent = laya.load_vlm(repo, revision=rev)
    _models[slot] = agent
    return agent


def after_available():
    """True only if the AFTER checkpoint repo actually exists on the Hub."""
    from huggingface_hub import repo_exists

    try:
        return bool(repo_exists(AFTER_MODEL))
    except Exception:
        return False


def score_pair(slot, image, text):
    """Run the paired (image+text) route for one example, via the real API.

    Returns ({display class: probability}, fake_probability): the four-way
    probabilities come from result["answers"]["native"]["probabilities"]
    (keyed by the model's native class names, mapped to display classes),
    and the fake probability from result["answers"]["fake"]["noul"] — the
    study's own binary readout. Binding verified live in the 2026-11-22
    rehearsal (Stage 7).
    """
    agent = _load(slot)
    result = agent.predict({"context": text, "image": image}, QUESTIONS)
    native = result["answers"]["native"]["probabilities"]
    probs = {NATIVE_TO_DISPLAY[name]: round(float(p), 4) for name, p in native.items()}
    fake_p = float(result["answers"]["fake"]["noul"])
    return probs, fake_p


def predict(image, caption, which):
    if image is None or not caption or not caption.strip():
        return None, "Please provide BOTH an image and its caption text — the model judges the pair together."
    slots = ["before"] if which == "Before training (zero-shot)" else ["after"]
    if slots == ["after"] and not after_available():
        return None, (
            "The AFTER checkpoint has not been published yet — training is still pending. "
            "The BEFORE (zero-shot) test is live above; this panel activates automatically "
            "once the fine-tuned checkpoint is pushed to the Hub."
        )
    try:
        probs, fake_p = score_pair(slots[0], image, caption.strip())
    except Exception as exc:  # surface, never fake a result
        return None, f"Model call failed: {exc}"
    verdict = max(probs, key=probs.get)
    note = (
        f"**Verdict: {verdict}** · fake probability {fake_p:.2f} "
        f"({'BEFORE — pretrained, zero-shot' if slots[0] == 'before' else 'AFTER — fine-tuned winner'})"
    )
    return probs, note


INTRO = """
# LAYA — Multimodal Misinformation Detection, Before & After Training

**Rafiul Haider · Pace University Analytics Capstone (Fall 2026, CRN 72369) · CS 668 Team 3**
*(Ananya Saravani Ganni, Harika Etikela, Rafiul Haider)*

## What this research is
News posts pair an image with a caption, and either half can be the lie. This study evaluates — and then adapts — **LAYA-Vision**, a small typed-decision vision–language model, on the four-way judgement that defines the task: a pair is **original** (both halves truthful and matched), **textual** (the text is distorted), **visual** (the image is distorted), or **mismatch** (real image, real text, wrong pairing). It is measured on three public benchmarks, each in its native metric: **MMFakeBench** (4-class macro-F1), **NewsCLIPpings** (pairing accuracy), and **VERITE** (3-class accuracy, eval-only).

## How we came about it
The project began as a diagnostic study, and the diagnosis was blunt: zero-shot, the model sits near chance and **collapses onto one answer** — on 1,000 validation rows it called 289 of 300 mismatch cases correctly but only **1 of 300** originals. A plain TF-IDF baseline beat it. But a second probe changed the conclusion: a logistic regression on the model's *frozen* features beat zero-shot by **+6.24 points** on NewsCLIPpings test. The features know things the decisions don't — so the research question became: **can proper adaptation (full fine-tuning vs LoRA, on 490 carefully split training records, selected on a tune split, calibrated on a reserved split) turn that latent signal into defensible performance?** This Space is where the answer is shown — the same tests, before and after.

## How to read this page
- **Try it** — give the model an image and its caption *together* and test it, before training or after.
- **Results** — the measured scoreboard for both checkpoints, per dataset, with the pre-registered predictions the experiment is judged against.
"""

RESULTS_MD = """
## Results — measured, not promised

### BEFORE training (pretrained LAYA-Vision, zero-shot) — verified baselines
| Dataset | Metric | Before |
|---|---|---|
| MMFakeBench (paired, test ablation) | macro-F1 | **0.2037** |
| NewsCLIPpings (val, 7,024 rows) | accuracy | **0.5083** |
| VERITE (paired) | accuracy | **0.3566** |
| Per-class recall, 1,000 rows | original / textual / visual / mismatch | 1/300 · 8/300 · 22/100 · 289/300 |
| Calibration (raw) | ECE | ≈ 0.466 |

Reference points: a TF-IDF baseline reaches 0.4986 accuracy / 0.4156 macro-F1 (grouped OOF) on the development population, and a frozen-feature logistic probe transfers at **57.4%** on NewsCLIPpings test (+6.24 pp over zero-shot). A source-metadata-only rule reaches 0.9150 on MMFakeBench — that is label leakage, and it is excluded everywhere in this study by design.

### AFTER training (fine-tuned winner) — pending
The AFTER column is published by the experiment notebook when training completes: both arms (full fine-tune and LoRA) are run, the winner is selected on the tune split only, the test split is scored once, and calibration is fitted on the reserved split. Pre-registered predictions (recorded before training): MMFakeBench tune macro-F1 0.30–0.42 · NewsCLIPpings val accuracy 0.55–0.65 · VERITE 0.38–0.48 · minimum per-class recall ≥ 0.25 · calibrated ECE < 0.15. The final table reports each prediction as met, missed, or rejected — as it falls.
"""

with gr.Blocks(title="LAYA — Before / After Training") as demo:
    gr.Markdown(INTRO)
    with gr.Tab("Try it — image + text together"):
        with gr.Row():
            img = gr.Image(type="pil", label="Image")
            cap = gr.Textbox(label="Caption / text", lines=4,
                             placeholder="Paste the caption or post text that goes with the image…")
        which = gr.Radio(
            ["Before training (zero-shot)", "After training (fine-tuned)"],
            value="Before training (zero-shot)", label="Which LAYA?",
        )
        btn = gr.Button("Test the pair")
        label_out = gr.Label(num_top_classes=4, label="Class probabilities")
        note_out = gr.Markdown()
        btn.click(predict, inputs=[img, cap, which], outputs=[label_out, note_out])
    with gr.Tab("Results"):
        gr.Markdown(RESULTS_MD)
    gr.Markdown(
        "*Checkpoints: BEFORE = thaitea/laya-vision @ f2fe3c12 (pinned). "
        "AFTER = the fine-tuned winner, published by the experiment run. "
        "Demo runs on CPU; long inputs are handled per the study protocol.*"
    )

if __name__ == "__main__":
    demo.launch()
