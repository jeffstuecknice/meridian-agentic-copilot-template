# Meridian Architecture — ONE flow, fast

Meridian runs the entire copilot in a **single Cognigy flow** (`Meridian_Copilot`) bound to one
Agent-Assist endpoint. This is a deliberate reversal of the Skyway v4 two-flow split, and this document
explains both the history (so you understand *why*) and the design (so you can build on it).

---

## 1. History: why Skyway split execution out — and why Meridian doesn't need to

| Generation | Shape | Why |
|---|---|---|
| Skyway v3 | ONE flow, Execution Agent **inline** | `executeFlow` child flows proved unsafe for long LLM pipelines (session-stick, dropped context) — so everything lived in one flow. It worked, but the inline 8-tool execution agent was slow and blocked the conversation session while it ran. |
| Skyway v4 | TWO flows — brain + a **REST-endpoint Execute flow** | Speed. Moving the execution aiAgentJob behind a REST endpoint (called by the tile through a PHP proxy) meant: it ran parallel to the conversation, each call got a **unique session** (stable sessions leaked stale context into the agent), and results returned in the HTTP response (~4–8 s). |
| **Meridian** | **ONE flow again** | Every reason for the split traces back to one fact: *execution ran through an LLM agent*. Meridian makes approved-action execution **deterministic** — no LLM in the hot path — so there is nothing slow to isolate, no context to leak, and nothing blocking the session. One flow, one endpoint, one import binding: simpler to distribute AND faster. |

**The design rule that falls out:** *LLMs decide; code executes.* By the time the agent clicks Approve,
the AI has already done all the thinking — the recommendation card carries every parameter (SKU, amount,
policy clause, order ref). Executing it is a mapping problem, not a reasoning problem.

## 2. The flow, top to bottom

```
start
 └─ ONCE (first turn only: setAgentAssistGrid → Copilot tile shell) — MUST be first on the main
 │   chain: CXone's copilot socket pre-walks the flow at session start to find the grid config;
 │   a grid buried in a later router branch = config:null = NO Copilot tab at all (live-debugged)
 └─ ROUTER (code) — classifies the turn, sets context.route
     ├─ postback: boot        → REHYDRATE (cached panel? push it) → CRM httpRequest → instant PRE-PANEL push → end-turn
     ├─ postback: approve     → EXEC MAP (code: recId+params → action plan)
     │                          → httpRequest chain (mock API: return / credit / order / sms)
     │                          → EXEC RESULT (code: collect real refs)
     │                          → sendData {merExecStr} → end-turn                  ★ ~1–2 s, zero LLM calls
     ├─ postback: ask         → native KNOWLEDGE SEARCH → ONE mini LLM → sendData {merAskStr} → end-turn
     ├─ postback: command     → COMMAND AGENT (small aiAgentJob, the action-tool registry)
     │                          → sendData {merExecStr} → end-turn                  ★ the agentic-execution showcase
     └─ customer/agent turn   → CONVO BUILD (code; filters "Begin Conversation"; agent utterances tagged)
                                → GATE (mini LLM: route + live sentiment from a 6-turn tail)
                                → sentiment push (only on ≥5-pt/label change)
                                ├─ route: skip     → end-turn                       ★ one mini call
                                ├─ route: question → same as `ask` branch
                                └─ route: go       → POLICY CACHE GATE (code — re-run only on a NEW request)
                                                     → native KNOWLEDGE SEARCH (policy)
                                                     → POLICY ANALYST (one GPT call → findings JSON, verbatim quotes)
                                                     → COMPOSER (mini LLM → full panel state; retry-guarded)
                                                     → MERGE (code, masking-safe) → sendData {merStateStr} → end-turn
```

Control flow is **topological** — Cognigy `end` nodes do not halt a turn, and switch branches fall
through to the switch's next sibling, so the branch order above is load-bearing.

### 2a. Identity resolution & provenance (probe-then-commit)

Every turn, the flow decides WHO the panel is about, and the customer card **states where that
answer came from** — a fallback record must never masquerade as a live CRM hit (the REAL-DATA-OR-
ERROR rule in CLAUDE.md; the labeled `cust_101` demo default is that rule's one sanctioned
exception, allowed precisely *because* the strip brands it red).

Signals, strongest first: **id typed in chat** (`cust_NNN`, tester hook, any participant) →
**name given in chat** (customer turns only, `this is / i am / i'm / my name is` anchored to the
message start, lowercase accepted) → **published customer id** (`copilot-customer-context`, fed by
the Studio script via the Interaction Context API) → **demo default** (red). The name/id captures
are **latched** into masking-safe context strings so they survive the 20-turn transcript window.

The regex is deliberately loose because **the CRM is the verifier, not the regex**:
- a captured name is a **probe** — provenance only commits (`merCrmOk/UrlOk/SrcOk/LastId`) when
  the lookup returns a record; a definitive miss (`ok:false`) blacklists the candidate
  (capped at 8; a capitalized two-word miss retries its first word — "Maya I'll" → "Maya") and
  the prior identity stands untouched; a transient failure changes NOTHING and retries next turn
  (only success-committed URLs are skip-cached);
- a **definitive** unknown published id latches `merCrmBad` and falls to the labeled default
  (`unknown`, red, naming the bad id and which signal carried it); the latch clears if the id
  later succeeds;
- an **identity flip** (record's customer_id changed) wipes every per-customer artifact (beat
  ledger, policy findings, published nickname — the superseded published id is dead to the
  session via `merCidOverridden`), pushes the new profile instantly (PRE0 re-fires), and forces
  the gate/recompute/policy path to re-run even on a "filler" turn;
- a cold-start CRM failure renders an explicit red **NO RECORD** card — never an eternal spinner.

Cognigy PII-masks **object/array values** in context (live-proven: `merTx` came back empty), so
every cross-node object read has a JSON-string mirror that survives intact: `merTxJson`,
`merCrmStr`, `merPanelSlimJson`, `merProdStr`, `merGateRoute`/`merGateQuery`, `merSentJson`.

### The two execution paths, on purpose

- **Approve (deterministic):** the panel's recommendation cards are built by the composer with a
  machine-readable `exec` block: `exec: {actions: [{action, params}, …]}` (up to 6 system calls per
  beat, in order). The Approve postback echoes it back as `{action:'approve', recId, exec}`; a code
  node validates the plan against the action whitelist and makes ONE `execute_batch` HTTP call; the
  mock API returns **real confirmation refs** (`RMA-…`, `CR-…`, `ORD-…`); `sendData` animates them
  onto the card. No LLM, no stale context, ~1–2 s.
- **Command bar (agentic):** free-text agent commands ("also text her the receipt") go to a small
  execution aiAgentJob with the parameterized tool registry. This preserves the *AI-executes* teaching
  showcase where it earns its keep — unplanned actions — without ever putting an LLM between an
  approved card and its execution.

## 3. Latency budget (the point of the exercise)

| Turn type | LLM calls | Target |
|---|---|---|
| Boot / rehydrate | 0 | instant pre-panel < 1 s |
| Skip-worthy chit-chat | 1 (gate mini) | < 2 s |
| First full panel (needs + comparison cards) | 3 (gate mini → analyst → composer mini) + 1 KS search | 10–15 s, with pre-panel + thinking-card choreography covering the wait |
| Follow-up request (policy cached) | 2 (gate, composer) | 5–8 s |
| Knowledge question | 2 (gate mini routes it, 1 mini answer) + KS search | 4–6 s |
| **Approve → refs on card** | **0** | **1–2 s** |
| Command-bar action | 1 aiAgentJob pass | 4–8 s |

Levers already applied: postbacks bypass the gate entirely; CRM lookup skipped when cached; policy
analysis cached per request (re-runs only when the gate detects a *new* request); sentiment computed by
the gate call (zero extra calls); native Knowledge-Store search (no lookup nodes, no CXone Knowledge Hub).

Tuning experiment (after the baseline is live): fuse ANALYST + COMPOSER into one call that emits
`{findings, panel}` in a single JSON — saves one round-trip on the showcase turn. Two-step ships first
because the retry-guarded composer and verbatim-quote fidelity are proven; fuse only with a live timing
comparison in hand.

## 4. Tile ↔ flow contract

- **Flow → tile** (all on `tileId: meridian-copilot-tile`; sendData arrives wrapped as
  `e.data.metadata.<key>` — the tile unwraps; every value is an escaped JSON string the tile
  `JSON.parse`s; an empty string = no-op):

  | key | payload | when |
  |---|---|---|
  | `merStateStr` | the full panel object (see §4a) | pre-panel, every composed panel, rehydrate each turn |
  | `merExecStr` | `{recId, ok, narration, executed:[{action, ref, ok, summary, receiptUrl?, total?}]}` | after Approve or a command finishes |
  | `merAskStr` | `{askId, title, answer, tell, sources:[{id,title}], escalate, escalateNote}` | knowledge answers (ask postback + auto-question) |
  | `merSentStr` | `{pct, label, note}` | live sentiment, only on ≥5-pt/label change |
  | `merStageStr` | `{n, total, label}` | REAL brain-run boundaries (gate done → policy read w/ actual section count → composing) — the tile's "AI Agent is working" strip; cleared when the composed panel lands |
  | `merConvoStr` | `{transcript:[{role,text}], customer:{customer_id,nickname}}` | every message turn |
  | `merGreet` | a suggested instant-greeting string | pre-panel turns only (before the first panel) |

- **Tile → flow:** official `SDK.postback(payload)` — arrives as
  `input.data._cognigy._agentAssist = {type:'submit', payload}`; the ROUTER switches on
  `payload.action`. The three routed payloads: `{action:'approve', recId, exec:{actions:[{action,
  params}]}}` (echo the beat's exec block verbatim), `{action:'ask', query, askId?}`,
  `{action:'command', command}`. `{action:'boot'}` deliberately has no router case — it rides the
  default chain so rehydrate + the briefing run on tile mount. Inline `onclick` handlers fail in the
  tile sandbox — wire with `addEventListener` only.

### 4a. Panel object (what `merStateStr` carries)

`{profile, context, needs:[{id,label,quote,weight}], comparison:{intro, products:[2 ranked cards with
fit[] verdicts + an honest tradeoff], heroPrompt}, attempted, customerAsks, nextStepsIntro,
recommendations:[beats with say/sayDone/detail/running/substeps/exec/policyQuote], draftMessage}` — the
composer prompt in `package/build_meridian.py` is the authoritative field-by-field contract.
- **`profile.src` / `srcNote` / `srcDbg` — the provenance strip** (§2a). The tile renders a strip
  ABOVE the customer's name: green (`.ok`) for the live sources `id`/`name`/`chatid`, red pulsing
  (`.bad`) for `default`/`unknown`/`stale`/`error`. `srcNote` is the human sentence; `srcDbg` is
  the raw identify-input line (`published=… chatName=… chatId=… turns=N (json) ignored=…`) — the
  panel's own diagnostic, because Cognigy Live Logging does not surface `api.log()` from code
  nodes on this stack. The deterministic `buildProfile` overwrites the LLM's profile with these
  fields on every push; a panel push that omits `profile` keeps the previous card (tile merge).
- **`comparison.provisional` — the instant product duo.** The pre-panel (zero LLM, ~1 s after boot)
  now carries both catalog laptops as unranked cards (`provisional:true`, "Option A/B" tags, dashed
  borders, photos from the tile's static map) so the agent sees real product information the moment
  the contact lands. The composer's ranked comparison replaces it in place; a provisional push can
  never overwrite real ranked cards (tile merge guard).
- **`comparison.heroPrompt` — the generative hero image.** "LLMs decide; code executes," applied to
  imagery: the composer AUTHORS a personalized image brief from the customer's stated needs (their
  café, their boarding pass, their editing app — no readable text, no logos, no faces); the tile hands
  it to `api/meridian_image.php` (one POST; Gemini image model server-side, key never in the package;
  cached by prompt hash so rehydrates and re-runs are instant) and renders the result full-width under
  the comparison grid with an honest "AI-generated visualization" caption + the LLM's own brief on
  demand. **The generation is a demo beat the agent triggers**: a new brief arms a "Have the AI draw
  the <option> in <name>'s world" button; the click generates (~6 s shimmer), and the agent can then
  art-direct revisions or restore the original. Generation failure renders a visible error card with
  the raw payload — never stock art. Loading choreography: the flow pushes `merStateStr` in stages
  (profile-only the instant the CRM lands → situation + provisional duo after the catalog → the
  composed panel), and the tile staggers each card's FIRST appearance (~420 ms apart, beats cascading
  within the playbook) — rehydrates never replay the entrance.
  Static product shots (`img/aero14.png`, `img/titan16.png`) render at the top of each product card
  independently of this.
- The tile is a **pure data-driven display**. It never reasons and never calls LLMs; its one outbound
  call executes the composer's image brief verbatim (display work — the thinking already happened in
  the flow), and it renders whatever the flow sends. It renders only in real CXone Agent Workspace (not Cognigy's Interaction Panel — the
  flow still runs there, which is how you test the brain).

## 5. Session semantics (the single-flow caveats, handled)

- **One session per contact** on the Agent-Assist channel. The deterministic exec branch keeps the
  session's LLM history clean — code nodes can't poison agent context (the exact failure that pushed v4
  to unique-session REST calls).
- **Blocking window:** a turn occupies the session while it runs. Deterministic exec holds it ~1–2 s
  (fine). The command-bar aiAgentJob can hold it 4–8 s — acceptable for an explicit agent command; the
  tile shows its thinking state meanwhile.
- **Who triggers turns:** customer messages always; the agent's typed words only when the profile has
  `includeAgentUtterances` ON (required — the HEARD moment and approvals-by-speech depend on it); tile
  clicks always (postback).

## 6. Resources in the package (all pre-bound at import — never UI-edit agent nodes)

| Resource | Purpose |
|---|---|
| Flow `Meridian_Copilot` | everything above |
| aiAgent `Meridian · Command Agent` | command-bar execution registry (the only aiAgentJob) |
| LLM bindings | analyst (strong model) + gate/composer/ask (mini) — `referenceId`s baked by the builder |
| Knowledge Store `Meridian_Knowledge` | MER-POL-01…05, **bundled in the zip** (chunks + embeddings ship with exports) |
| Endpoint | ONE Agent-Assist endpoint → `Meridian_Copilot` |

## 7. Debug tags (Cognigy Live Logging)

`[MER][CONVO]` turn build · `[MER][CRM<]` record · `[MER][GATE]` route+sentiment · `[MER][POLICY<]`
findings · `[MER][PANEL]` full panel JSON (paste into the standalone tile: `MER.setState(<json>)`) ·
`[MER][EXEC>]`/`[MER][EXEC<]` action plan / refs · `[MER][ASK]` knowledge answers.
