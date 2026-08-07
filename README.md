# Meridian — the Golden Agentic Copilot Template

**Meridian is the canonical, distributable reference build of a CXone + Cognigy Agentic Copilot.**
It distills everything proven across the Voyager, Skyway, and Sparkathon builds (2026) into one clean,
version-free, fully documented example a teammate can clone, import, wire, and demo.

The demo arc: a live agent helps a customer decide between two laptops. The AI copilot **listens** to the
conversation, **reasons** over store policy in a Knowledge Store, **proposes** ranked recommendations and a
policy-exception resolution, the agent **approves** with one click, and the AI **executes** real actions with
confirmation references.

> **North star:** Listen → Reason → Propose → Approve → Execute — with the human agent in control at the
> approval gate, and the AI doing the reading, reasoning, and doing.

## Try it

Two ready-to-import packages ship in `package/` — no build step required:

- **`Package-Meridian-HelloCopilot.zip`** — a 6-node diagnostic flow (grid → inline tile → echo →
  postback), zero external dependencies. Import this first: it proves your CXone-to-Cognigy wiring
  end to end (see `docs/CXONE_SETUP.md`) before any real logic is involved.
- **`Package-Meridian-Copilot.zip`** (`-noKS.zip` for re-imports once the Knowledge Store already has
  documents) — the real flow, AI agents, and prompts. Import it to **study** the actual working
  build immediately. To **test** it end to end with live data, deploy `api/` to your own host
  (`python tools/deploy_api.py`, own Gemini key for hero images) and rebuild with
  `MERIDIAN_API_BASE=<your-url> python package/build_meridian.py` — the shipped zip points at a
  placeholder host on purpose, so nobody's clone silently calls somebody else's server.

## The seven demo beats

1. **Accept + pre-load** — agent accepts the contact; the tile boots with a skeleton, "AI Agent is reviewing
   the conversation…", and the customer profile populates from the CRM.
2. **Listen** — the customer describes what they need in plain conversation; the AI extracts *stated needs*,
   not keywords.
3. **Propose (the showpiece)** — comparison cards ranked by the customer's own words, each card explaining
   *why* it ranks where it does.
4. **Sentiment + HEARD moment** — the customer vents about a stuck refund; the live sentiment slider drops;
   when the agent acknowledges it, the "AI Agent heard this" banner fires and the slider recovers.
5. **Reason (policy exception)** — the return is outside the standard window; the AI finds the loyalty-tier
   exception clause in the Knowledge Store (verbatim quote on the card) and proposes bundling the return
   credit into the new purchase.
6. **Approve → Execute** — one click; a deterministic code + HTTP chain **inside the same flow**
   processes the return exception, applies the credit, and places the order — real confirmation
   refs in seconds, zero LLM calls on the execution path (`docs/ARCHITECTURE.md` §1 explains why
   Meridian doesn't need Skyway's separate execute flow).
7. **Receipt** — SMS receipt link via xApp; knowledge Q&A with "Add to steps" available throughout.
8. **Wrap-Up** — once every beat is done, a summary card appears on its own (or any time via the
   footer's Wrap Up button): a CRM-note recap of what actually happened, a "Push to CRM" button
   that logs it for real (`log_case_summary`, a real reference back), and a "Copy for customer"
   button with a warm, ready-to-paste message the agent relays in chat. Grounded only in real
   executed actions — an early wrap-up with nothing done yet says so honestly, never invents one.

Full script with characters, transcript, and what-to-look-for: [docs/SCENARIO.md](docs/SCENARIO.md).

## Repository map

| Path | What lives here |
|---|---|
| `docs/` | SCENARIO (demo script), SCENARIO_CATALOG (alternate industries), ARCHITECTURE, CXONE_SETUP (wiring runbook) |
| `package/` | Python builder → the importable Cognigy `.zip` (flows + AI agents + bundled Knowledge Store) |
| `tile/` | The custom HTML copilot tile (`meridian_tile.js`) + standalone preview harness (`harness.html`) |
| `api/` | PHP mock backend: CRM, product catalog, order/return/credit actions, xApp SMS |
| `knowledge/` | Policy documents — `.md` source, `.txt` upload copies (Knowledge Store rejects `.md`) |
| `tools/` | Deploy scripts, profile-hub API scripts, test utilities |
| `MeridianAgenticCopilot_StudioScript.json` | The bundled CXone Studio script — import and re-point it (Step 3 of CXONE_SETUP) instead of authoring from a blank canvas. Carries **no credentials by design**: it authenticates through an Integration Hub connection via Connect Auth (setup in CXONE_SETUP.md Step 3). |

## Architecture in one paragraph

**ONE Cognigy flow** (`Meridian_Copilot`) on one Agent-Assist endpoint. A router classifies every turn: tile
postbacks short-circuit straight to their branch; customer turns hit a lightweight gate model that routes the
turn and emits live sentiment; questions go to native Knowledge-Store search + a mini model; recommendation
turns run native Knowledge-Store search (policy) → one policy-analyst LLM (findings JSON with verbatim
quotes) → a composer that builds the full panel state, shipped to the tile as an escaped-JSON `sendData`
payload. The governing rule is **LLMs decide; code executes**: approved recommendation cards carry a
machine-readable action plan, so the Approve click runs a deterministic code + HTTP-request chain — real
confirmation refs in ~1–2 s with zero LLM calls — while a small Command Agent handles free-text agent
commands (the agentic-execution showcase). The tile is a pure data-driven display; it never reasons.
Why the previous build split execution into a second flow and why Meridian doesn't have to:
`docs/ARCHITECTURE.md` §1. 

## Status

✅ **Working end to end** — builder, tile, API, knowledge docs, and runbooks are all in place and
live-proven. The customer card carries an **identity provenance strip**: green when the record came
from a real signal (published customer id, name given in chat, id typed in chat), red when it is a
fallback, stale, or missing — the panel never lets substitute data masquerade as live CRM data.
