# Meridian — CXone wiring runbook

How to wire the Meridian copilot into live CXone Agent Workspace. **Follow the order exactly** —
every step exists because skipping it cost a debugging day somewhere.

> Two layers, both must be right: **Cognigy** (flow + webhook endpoint) and **CXone admin**
> (Copilot profile + routing chain: skill → studio script → chat channel → Guide entry point).

---

## Step 0 — MVP FIRST: prove the wiring with the hello flow (NON-NEGOTIABLE)

Never debug the real flow and the wiring at the same time. The repo ships a 6-node diagnostic flow
whose tile is fully inline (zero external dependencies):

1. `python tools/build_hello_copilot.py` → import `package/Package-Meridian-HelloCopilot.zip`.
2. Create (or reuse) the webhook endpoint → bind it to **`Meridian_HelloCopilot`**.
3. Wire the CXone chain (steps 1–3 below) and test.
4. **Only after** you see the green **"✓ TILE MOUNTED — Meridian Hello Copilot"** banner in Agent
   Workspace do you point the endpoint at the real `Meridian_Copilot` flow.

The hello tile also proves both directions: an echo row per customer message (flow → tile) and the
"Send test postback" button (tile → flow).

## Step 1 — Cognigy

1. Import `package/Package-Meridian-Copilot.zip` (fresh project) — flow + Command Agent +
   `Meridian_Knowledge` store land in one import. **Never open/save the Command Agent node in the
   UI** (save-validation gotcha; everything is pre-bound at import).
   Re-imports after a flow change: delete the old flow first, and use the `--no-ks` zip if the
   store already holds documents (same-project imports remap ids — re-shipping the store duplicates it).
2. Upload `knowledge/upload/*.txt` (all 5 MER-POL docs) into `Meridian_Knowledge` → wait for **ready**.
3. Endpoint: type **Webhook**, bound to the flow. Copy the endpoint URL.

## Step 2 — the Copilot profile (where everything breaks)

1. Create the profile — **type "Copilot" first → Save → configure → Save → switch to "Agentic" →
   Save** (the save-bug dance). Set AI Agent = your webhook endpoint.
2. **Assume the UI dropped config.** Run the repair (needs a fresh bearer token, ~1h life):
   ```
   set CC_TOKEN=<bearer>
   python tools/fix_profile.py <profile-name>
   ```
   It fixes the four known drops: `channels: []`, missing `digitalChannel`/`voiceChannel`,
   `includeAgentUtterances: false`, and `acdType: 'External'` (profiles born in the new AI Studio
   UI get External; working profiles are Internal).
3. **Never re-save a working profile in the UI.** If you must touch it, re-run `fix_profile.py` after.

## Step 3 — the routing chain

1. **Digital skill** for the demo.
2. **Studio script** — clone a KNOWN-WORKING agent-assist script if you have one (see the bisect
   rule below). Minimum shape: `Begin → ReqAgent(skill)`; `OnAssignment → Snippet
   (ASSIGN global:__AgentId = "{AGENTID}") → Agent Assist action (assistLaunchConfigName =
   the profile name)`.
3. **Chat channel** → default skill = the skill, script = the script.
4. **Guide entry point** → the chat channel.
5. **Full agent logout/login** after ANY profile or script change. Test on the **first contact
   after login** (the known socket bug breaks copilot mounting on later contacts in a session).

## Fast triage (distilled from the 2026-07-30 debugging day)

Work DOWN this list — each step assumes the ones above passed:

1. **Nothing reaches Cognigy at all** (no `[MER]` Live Logging on a customer message)
   → CXone never calls the endpoint. Profile checklist (step 2.2), script's Agent Assist action
   name, full logout/login. Prove the endpoint itself with a direct POST:
   `curl -X POST <endpoint-url> -H "Content-Type: application/json" -d '{"userId":"t","sessionId":"t1","text":"hi"}'` → expect 200 + `[MER]` logs.
2. **Flow runs but no Copilot tab** → check the flow's FIRST nodes: CXone pre-walks the flow at
   session start to find `setAgentAssistGrid`; the grid must be **first-chain-discoverable from
   Start** (before any router/switch). The builder validates this; don't reorder.
3. **Still no tab with a perfect profile + script** → bisect with proven objects. Swap ONE object
   at a time between the working and failing chains (profile → script → skill → channel), full
   logout/login between tests. The object whose swap flips the result is your culprit.
   ⚠️ Observed on tenant B32 (2026-07-30, platform 2026.14): routing objects **created after the
   tenant upgrade failed to mount copilot even with byte-identical scripts and proven profiles**,
   while pre-upgrade chains worked — if your bisect corners a freshly-created skill/channel, you
   are likely in this platform bug; wire onto older objects and file it.
4. **Tab mounts, tile errors** → `meridian_tile.js` not deployed / stale: `python tools/deploy_api.py`,
   then Ctrl+F5 in the workspace.
5. **Copilot never reacts to the agent's words** → `includeAgentUtterances` OFF → step 2.2.

## Known-benign noise (don't chase these)

Agent Workspace console always shows: Branding Profile fetch failures, Jabra partner-key warnings,
`Unexpected end of JSON input` HttpClient chatter, `<svg> viewBox` errors, `activateContact 404
InvalidContactId`. None of these are copilot-related.
