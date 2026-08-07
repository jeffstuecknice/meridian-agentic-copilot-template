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

**Studio side:** import the companion script `MeridianHelloCopilot_StudioScript.json` (repo root)
rather than authoring one — same minimum shape as the real script minus the identity chain
(`Begin → Request Agent(skill)`, then on assignment `Set AgentID → Agent Assist`). Set the
Request Agent's Skill from the dropdown after import; confirm `assistLaunchConfigName` matches
your Copilot Profile's exact name.

### ✅ Verified live (2026-08-07) — Jeff's working reference config

The full chain below is confirmed live end to end (tile mounts, echoes both customer AND agent
utterances, test postback round-trips) on tenant B32 / brand `6050`:

| Object | Name |
|---|---|
| Cognigy flow | `Meridian_HelloCopilot` |
| Cognigy webhook endpoint | `MeridianHelloCopilot-CognigyWebhookEndpoint` |
| CXone Copilot Profile | `MeridianHelloCopilot-CopilotProfile` |
| Guide entry point | `MeridianHelloCopilot-GuideEntrypoint` |

**How to test it** (no CXone admin access needed beyond a login — this is the same playground
flow the public setup guide walks through):

1. Go to `aicoe.3ddesignview.com/demo/guide_playground`, enter Brand ID `6050`, **Apply & Reload**.
2. Expand **Entrypoint ID**, search, select **`MeridianHelloCopilot-GuideEntrypoint`**.
3. **Test Chat** as the customer.
4. In CXone Agent Workspace, assign the incoming contact to yourself, open the **Copilot** tab.
5. Expect the green **"✓ TILE MOUNTED — Meridian Hello Copilot"** banner immediately.
6. Type a message as the customer, then as the agent — both should produce an echo row in the
   tile (`helloStr` entries in the App Space log). If only the customer side echoes, the profile's
   `includeAgentUtterances` reverted — re-run `tools/fix_profile.py MeridianHelloCopilot-CopilotProfile`
   (this exact profile hit that bug once already; see Step 2 below for the general fix).
7. Click **Send test postback** in the tile and confirm a matching row appears from the flow side.

## Step 1 — Cognigy

1. Import `package/Package-Meridian-Copilot.zip` (fresh project) — flow + Command Agent +
   `Meridian_Knowledge` store land in one import. **Never open/save the Command Agent node in the
   UI** (save-validation gotcha; everything is pre-bound at import).
   Re-imports after a flow change: delete the old flow first, and use the `--no-ks` zip if the
   store already holds documents (same-project imports remap ids — re-shipping the store duplicates it).
2. Upload `knowledge/upload/*.txt` (all 5 MER-POL docs) into `Meridian_Knowledge` → wait for **ready**.
3. Endpoint: type **Webhook**, bound to the flow. Copy the endpoint URL.

## Step 2 — the Copilot profile (where everything breaks)

⚠️ **A profile created directly as "Agentic" is DEFECTIVE AT BIRTH and cannot be repaired** — it's
born `acdType: 'External'` with empty channels, and even after an API repair of every visible field
it will never mount the Copilot tab (proven 2026-07-30: identical config, only the profile swapped,
mounting followed the creation path). Delete such a profile; do not try to save it.

**The proven creation recipe (Jeff's best practice, 2026-07-30):**

1. Create a **regular "Copilot"** profile.
2. Select the channels — **Voice and Digital/Text** — and select the sub-profiles as required.
3. **Save.**
4. Re-open the profile → change type to **"Agentic Copilot"** → select the **Cognigy webhook
   endpoint** at that point.
5. **Save.**
6. **Always finish with the repair** (needs a fresh bearer token, ~1h life) — even a dance-born
   profile drops `includeAgentUtterances`:
   ```
   set CC_TOKEN=<bearer>
   python tools/fix_profile.py <profile-name>
   ```
   It verifies/fixes: `channels`, `digitalChannel`/`voiceChannel`, `includeAgentUtterances`
   (the copilot cannot hear the agent's side without it), and `acdType: 'Internal'`.
7. **Never re-save a working profile in the UI.** If you must touch it, re-run `fix_profile.py` after.

## Step 3 — the routing chain

1. **Digital skill** for the demo.
2. **Studio script** — import `MeridianAgenticCopilot_StudioScript.json` (bundled at the repo
   root) rather than authoring from a blank canvas — see the bisect rule below for why a proven
   script beats a fresh one. Its real shape (the identity chain must run **before** ReqAgent):
   `Begin → Get Custom Fields → Connect Auth → Map Context + Publish (Snippet) → ReqAgent(skill)`;
   `OnAssignment → Set AgentID (ASSIGN global:__AgentId = "{AGENTID}") → Agent Assist action
   (assistLaunchConfigName = the profile name)`.

   > **The script carries NO credentials — by design.** The publish Snippet reads its bearer
   > token from the **Connect Auth** action, which authenticates via a CXone **Integration Hub**
   > connection. Never paste an access key into a Studio script: a leaked script leaked the key
   > (that is this repo's origin story, 2026-08-06).
3. **Integration Hub connection** (Connections Hub → Integration Hub) — required for the script:
   1. Create a connection (any display name — e.g. `Meridian RTI Test Connection`), Integration
      Method **REST**, Authentication Type **OAuth 2.0**.
   2. **Authentication tab**: URL `https://<region>.nice-incontact.com/authentication/v1/token/access-key`,
      Method POST, Body `{"accessKeyId": "[[accessKeyId]]", "accessKeySecret": "[[accessKeySecret]]"}`.
   3. **Variables tab**: add `accessKeyId` / `accessKeySecret` as **secrets** (AES-encrypted,
      write-only) with a CXone API access key (Admin → Security → API Access). Click **Test
      Authentication** — expect HTTP 200 with tokens.
   4. In the imported script, set **Connect Auth → ConnectName** to your connection's **display
      name** (double-clicking the action opens a picker; note it can wipe neighboring fields —
      re-check them after).
   5. The token lives at **`{authBody.responseContent.access_token}`** (undocumented; confirmed
      against the one public production ConnectAuth script). The Snippet probes fallback paths
      and records the winner in the `dbg_tok_path` trace variable.
   6. **ConnectRequest is deliberately NOT used.** On this stack it reports success while
      delivering nothing (proven by reading the target API back: `404 Key not found`). The
      Snippet uses `GetRESTProxy()` so `dbg_ic_status` records a **real** HTTP status.
   7. **Region**: the publish URL in the Snippet is `api-na1.niceincontact.com` — edit both hosts
      to your tenant's region if you are not on NA1.
4. **Channel prerequisites for identity**: the chat channel needs a **contact custom field** with
   ident `customer_id` (the pre-contact survey fills it — e.g. `cust_101` for the bundled Maya
   Torres scenario), and the pre-chat form must capture the **customer name** (`__authorfullname`
   is the identity anchor — CXone locks it at chat start). The Snippet reads the custom field
   POSITIONALLY at `contactCustomFields[1]` — re-check the index in a trace if you add fields.
5. **Chat channel** → default skill = the skill, script = the script.
6. **Guide entry point** → the chat channel.
7. **Full agent logout/login** after ANY profile or script change. Test on the **first contact
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
6. **Customer card shows a red provenance strip on a live contact** → the strip's second line
   (`published=… chatName=… chatId=… turns=N (json|obj|none)`) says exactly which identify signal
   is missing. `published=-` → run a Studio **trace** and read `dbg_ic_status` (`SKIPPED` = the
   contact custom field is empty; `401` = token — check `dbg_tok_path`; `2xx` = publish fine,
   problem is Cognigy-side). `turns=0 (none)` → the flow package is stale, re-import.
   `chatName=-` after the customer gave a name → the name missed the CRM (check `ignored=` on
   the same line for blacklisted probes). ⚠️ Cognigy **Live Logging does not surface `api.log()`
   from code nodes** on this stack — the panel's own strip IS the diagnostic; don't hunt logs.

## Known-benign noise (don't chase these)

Agent Workspace console always shows: Branding Profile fetch failures, Jabra partner-key warnings,
`Unexpected end of JSON input` HttpClient chatter, `<svg> viewBox` errors, `activateContact 404
InvalidContactId`. None of these are copilot-related.
