# Publish-Path Verification — LAYA Main Run (READ-ONLY)

Verified 2026-11-22 ~16:25 ET by the publish-verification swarm agent.
No pushes, no repo creation, no token use. All checks were public API reads
and local file reads.

## 1. Do the target repos exist on Hugging Face?

**No — neither exists yet (public evidence). The publish step must create both.**

| Repo | `GET /api/models|spaces/<repo>` | Author listing |
|---|---|---|
| `RafiulHaiderbro/laya-vision-fullft-mmfakebench` | 401 `Invalid username or password.` | `/api/models?author=RafiulHaiderbro` → 200 `[]` |
| `RafiulHaiderbro/laya-misinfo-demo` | 401 `Invalid username or password.` | `/api/spaces?author=RafiulHaiderbro` → 200 `[]` |

Notes on interpretation:
- HF's unauthenticated API returns that exact 401 body for nonexistent repos —
  verified against a control name (`RafiulHaiderbro/zzz-no-such-repo-12345` →
  identical 401). So 401 here means "not found / not public," not an auth failure
  of the check itself.
- The account itself exists: `https://huggingface.co/RafiulHaiderbro` → 200.
- Caveat: a *private* repo under the account would be invisible to these
  unauthenticated checks. This does not block publish: the notebook cell calls
  `create_repo(..., exist_ok=True)` for both repos, which succeeds whether it
  creates them fresh or finds them already present.
- Base model sanity: `thaitea/laya-vision` → 200, public, library_name `laya` ✓.

## 2. Space code (`~/workspace/misinfo_run/hf_space/`)

`app.py` — all bindings correct:
- **BEFORE**: `BEFORE_MODEL` defaults to `thaitea/laya-vision`, `BEFORE_REVISION`
  defaults to the pinned `f2fe3c12cb6d04c59d8a190250bf3fb40fc828dc` ✓
  (both overridable by env, defaults are the pinned values).
- **AFTER**: `AFTER_MODEL` defaults to
  `RafiulHaiderbro/laya-vision-fullft-mmfakebench` ✓, and `after_available()`
  gates the After panel on `huggingface_hub.repo_exists(AFTER_MODEL)`,
  returning a plain "not published yet" message instead of crashing ✓.
- **Real API**: `_load()` uses `laya.load_vlm(repo, revision=rev)`; `score_pair()`
  calls `agent.predict({"context": text, "image": image}, QUESTIONS)` and reads
  `result["answers"]["native"]["probabilities"]` (native class names mapped to
  display classes) and `result["answers"]["fake"]["noul"]` — the
  rehearsal-verified binding (Stage 7), documented in the module docstring ✓.
- Questions are the study's frozen pair (native 4-way choice + fake noul),
  copied verbatim from the workspace validation script ✓.

`requirements.txt` — correct:
- `laya @ git+https://github.com/r33drichards/laya-vision@9e1e2419d855ad3e1a2af4d4bd1ef6be5418842c`
  — the dev VLM build at the rehearsal-pinned commit, **not** PyPI `laya` ✓
  (with an explicit comment saying why). CPU torch index, gradio, transformers,
  peft, pillow, huggingface_hub all present ✓.

`README.md` — present with valid Space frontmatter (`sdk: gradio`,
`sdk_version: 5.0.0`, `app_file: app.py`, license apache-2.0) ✓ — all three
files the publish cell uploads (`app.py`, `requirements.txt`, `README.md`)
exist in `hf_space/` ✓.

Residual risk (known, publish-time): the first Space boot must be smoke-checked
for `laya.load_vlm` importing from the git pin — if the Space's build silently
resolved PyPI laya, the app would fail loudly on first load, not silently
mis-score. Watch the Space build log after push.

## 3. Notebook PUBLISH cell (cell 51 of `LAYA_Colab_Staged_For_Review.ipynb`)

CONFIG (cell 5) confirmed first: `PUBLISH = True`,
`HF_MODEL_REPO = "RafiulHaiderbro/laya-vision-fullft-mmfakebench"`,
`HF_SPACE_REPO = "RafiulHaiderbro/laya-misinfo-demo"`,
`BASE_MODEL = "thaitea/laya-vision"`,
`VISION_REVISION = "f2fe3c12cb6d04c59d8a190250bf3fb40fc828dc"` — all exact ✓.

What cell 51 does, in order:
1. **Guards**: no-ops if `PUBLISH` is False; no-ops if `runs/.published.json`
   marker already exists (idempotent — cannot double-publish).
2. **Token resolution** (see §4) — asserts a token was found, else stops with a
   clear message.
3. **Model push**: builds a model card (license, base model + revision, winner
   arm/loss/steps, tune F1, test bootstrap delta + CI, H1–H5 verdicts, the
   frozen-vision-tower amendment, limitations) → writes it as `README.md` into
   the calibrated winner dir (`runs/<winner>_calibrated`, from §12; asserts the
   dir exists) → `create_repo(HF_MODEL_REPO, repo_type="model", exist_ok=True)`
   → `upload_folder(cal_dir → HF_MODEL_REPO)`.
4. **Space push**: locates `hf_space/` at `WS/hf_space` or `/root/hf_space`
   (asserts it exists — **the run agent must ensure `hf_space/` is synced to the
   pod before this cell runs**) → `create_repo(HF_SPACE_REPO, repo_type="space",
   space_sdk="gradio", exist_ok=True)` → uploads `app.py`, `requirements.txt`,
   `README.md` → sets Space variable `AFTER_MODEL = HF_MODEL_REPO` if the
   installed `huggingface_hub` supports `add_space_variable` (graceful fallback
   message otherwise; the app default already equals the repo, so this is
   belt-and-braces).
5. Writes the `runs/.published.json` marker with both repo ids.

**Token printing audit: CLEAN.** The token is only ever passed to
`HfApi(token=...)`. Nothing in the cell prints it, logs it, or writes it to a
file. The only identity output is `api.whoami()["name"]` (the account name).

## 4. Token route at publish time — PRECISE instructions

The token lives only in Rafiul's Mac workspace, in the "hf token.rtfd" folder
(`/Users/rafiulhaider/Documents/Misinformation/...`). It has never been read by
any agent. The publish cell accepts the token from, in priority order:

1. Env `HF_TOKEN` or `HUGGING_FACE_HUB_TOKEN` in the kernel process, else
2. The HF cache file `~/.cache/huggingface/token` on the pod, else
3. A workspace scan: any file under the pod workspace whose name contains
   `token` with suffix `.rtfd` / `.txt` / `.md`, regex-extracting `hf_[A-Za-z0-9]{20,}`.

**Recommended route for the run agent (route 2 — HF cache):**
1. Read the token file from the Mac via the device files route
   (`files.read` on the "hf token.rtfd" item) and extract the `hf_…` string
   in memory. Never echo it into a shell command line, a log, or a chat report.
2. Deliver it to the pod over the existing SSH route by **stdin**, e.g.
   `ssh … 'install -d -m 700 ~/.cache/huggingface && install -m 600 /dev/stdin ~/.cache/huggingface/token'`
   with the token as the process's stdin payload — so the value never appears
   in argv, shell history, or any file on this VM.
3. Verify presence without revealing it: `test -s ~/.cache/huggingface/token && echo present` on the pod.
4. Run the PUBLISH cell. Afterwards, optionally delete the pod cache token
   (the pod is terminated at run end regardless).

**⚠ FLAG — the route-3 fallback has a real defect risk:** on macOS, `.rtfd` is
normally a *package* (a directory containing `TXT.rtf`), not a flat file. The
cell's scan requires `cand.is_file()` and `read_text()` — a directory-form
`.rtfd` copied to the pod would be silently skipped and the cell would assert
"No HF token found." Do not rely on route 3 unless the copied item is confirmed
to be a single flat file. Routes 1–2 have no such dependency — use route 2.

**⚠ FLAG — never stage the token through this VM's git clone:** the clone's
`.gitignore` does cover `*token*` (line 15, "Secrets — never commit"), which is
protection, but the rule stands: the token transits memory/stdin only, and is
never written into `~/workspace/misinfo_run/` or `~/workspace/laya-github-copy/`.

**Workable route exists** (route 2 above) — no blocker, provided the Mac
files-read at publish time returns the token text. If the .rtfd read returns a
package listing instead of text, the fallback is: Rafiul pastes the token into
the Secure Vault / a flat `hf_token.txt` in the Mac workspace, and the same
stdin route is used from there.

## Blockers / pre-publish checklist

- [ ] **Not a blocker:** both HF repos must be created at publish — the cell
      does this itself (`create_repo`, `exist_ok=True`).
- [ ] Ensure `hf_space/` (all 3 files) is synced to the pod workspace before
      cell 51 runs — the cell asserts on it.
- [ ] Deliver the token via the HF-cache stdin route (§4); do not rely on the
      `.rtfd` workspace-scan fallback.
- [ ] After the Space push, smoke-check the Space build log for a clean
      `laya.load_vlm` import from the git pin (known residual risk, §2).
- [ ] `PUBLISH = True` is already set in CONFIG; the `.published.json` marker
      prevents accidental re-publish.
