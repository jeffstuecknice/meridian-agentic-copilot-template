# Meridian — instructions for Claude Code

Golden, distributable CXone + Cognigy agentic-copilot template (see `README.md` for the full demo
arc). Read `docs/SCENARIO.md` first — it's the single source of truth for this build. If the task
is adapting Meridian to a different customer/use case, also check `docs/SCENARIO_CATALOG.md` for
scenarios already scoped before writing one from scratch.

## Read before changing anything

- `docs/SCENARIO.md` — cast, product catalog, policy exception, transcript skeleton
- `docs/ARCHITECTURE.md` — the flow design (§2 flow top-to-bottom, §4 tile↔flow contract, §6 the
  agent-node rule below)
- `docs/CXONE_SETUP.md` — the CXone-side wiring runbook (skill/script/channel/profile) and its
  platform gotchas
- `docs/SCENARIO_CATALOG.md` — alternate scenarios already scoped, if the laptop use case isn't
  the target

## Hard rules

- **Never open/save an `aiAgent` or `aiAgentJob` node in the Cognigy UI after import.** The
  platform's save-validation fails on fields the import path accepts fine. Bind the LLM, knowledge
  reference, and instructions in `package/build_meridian.py` and rebuild instead of hand-editing.
- **`setAgentAssistGrid` must be first-chain from Start**, ahead of any router or switch — CXone's
  copilot socket pre-walks the flow at session start looking for it. Behind a branch means no
  Copilot tab appears at all, with an otherwise-correct profile and script.
- **No backend host is hardcoded anywhere in this repo.** `package/build_meridian.py` requires
  `MERIDIAN_API_BASE` (env var) and refuses to build without it; `tile/meridian_tile.js` derives its
  own base from wherever it was loaded. Don't reintroduce a hardcoded URL — that's what put a
  teammate's test clicks against someone else's live server in an earlier version of this repo.
- **Real data or a visible error — never a fallback or invented value.** If a data source isn't
  configured or a call fails, render the honest error state; don't have the tile or the flow make
  up a plausible-looking substitute.
- **Deterministic ids on re-import.** Changing a node's id breaks the "delete old flow, re-import"
  safety this package is built around — see the re-import gotcha in `docs/CXONE_SETUP.md`.

## Building

- Full package: `MERIDIAN_API_BASE=<your-deployed-api-url> python package/build_meridian.py`
  (add `--no-ks` once the Knowledge Store already has documents — re-shipping it duplicates the
  store)
- Zero-dependency wiring proof (no backend, no extra LLMs): `python tools/build_hello_copilot.py`
  — inline tile, `Start → grid → tile → echo → postback`. Build and import this FIRST when standing
  up a new CXone/Cognigy environment, before importing anything with real logic in it.
- Deploy the backend to your own host: `python tools/deploy_api.py` (FTP creds file outside the
  repo — see the script's docstring; it prints the URL to use as `MERIDIAN_API_BASE` once live)

## CXone-side setup

Not this repo's job to automate — `docs/CXONE_SETUP.md` has the Meridian-specific wiring steps
(exact skill/script/channel/profile names). For the general CXone + Cognigy agentic-copilot pattern
that applies beyond this one build: https://aicoe.3ddesignview.com/guides/agentic-copilot-setup/
