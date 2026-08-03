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
6. **Approve → Execute** — one click; a separate REST execute flow processes the return exception, applies
   the credit, and places the order — real confirmation refs in seconds.
7. **Wrap** — SMS receipt link via xApp; knowledge Q&A with "Add to steps" available throughout.

Full script with characters, transcript, and what-to-look-for: [docs/SCENARIO.md](docs/SCENARIO.md).

## Repository map

| Path | What lives here |
|---|---|
| `docs/` | SCENARIO (demo script), ARCHITECTURE, CXONE_SETUP (wiring runbook), DEMO_RUNOFSHOW, TROUBLESHOOTING |
| `package/` | Python builder → the importable Cognigy `.zip` (flows + AI agents + bundled Knowledge Store) |
| `tile/src/` | The custom HTML copilot tile (HTML/CSS/JS) + standalone preview harness |
| `api/` | PHP mock backend: CRM, product catalog, order/return/credit actions, xApp SMS |
| `knowledge/` | Policy documents — `.md` source, `.txt` upload copies (Knowledge Store rejects `.md`) |
| `tools/` | Deploy scripts, profile-hub API scripts, test utilities |
| `MeridianAgenticCopilot_StudioScript_1.json` | Known-working CXone Studio script — clone and re-point it (Phase 5 of CXONE_SETUP) instead of authoring from a blank canvas. API key stripped to a placeholder; see the credentials note in CXONE_SETUP.md. |

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

🚧 **Foundation phase** — scenario locked, workspace scaffolded. Builder, tile, API, knowledge docs, and
runbooks land next.
