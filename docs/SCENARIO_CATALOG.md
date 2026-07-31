# Meridian Scenario Catalog — nine more demos on the same chassis

Meridian's mechanics are deliberately generic. Every scenario below reuses the SAME proven parts —
nothing new to invent, only content to swap:

| Chassis part | What you swap per scenario |
|---|---|
| CRM seed (mock API) | two customers: the hero (top loyalty tier — the exception applies) and the contrast (base tier — honest "policy doesn't allow it" + escalate path) |
| The comparison showpiece | exactly TWO options ranked by the customer's STATED needs, with the honest tradeoff (MER-POL-05's "never oversell" rule travels to every domain) |
| Sore point → HEARD → exception | one past bad experience that dips sentiment; one Knowledge-Store clause (the §3.1 analog) the AI quotes VERBATIM to fix it |
| Action registry | the same 5 generic verbs: `process_return_exception` (any make-it-right reversal), `apply_credit`, `place_order` (any booking/enrollment/dispatch), `send_receipt` (any confirmation artifact, delivered in chat), `escalate_case` |
| Offer gate | the money moment holds Approve until the customer's yes |
| Hero image | the composer writes a scene brief from the customer's stated world — the personalization showcase |
| Knowledge docs | 5 policy .txt docs; ONE carries the exception clause with a numbered section |

To build one: copy `docs/SCENARIO.md`'s structure, fill the table below's row out into it, swap the
mock-API catalog + customers + knowledge docs, and adjust the composer's arc line. The flow, tile,
stage stream, and execute path don't change.

---

## 1 · "The Roamer" — telecom plan upgrade

- **Brand/cast:** Northwave Mobile (tiers: Blue → Wave → **Crest**). Customer **Dana Whitfield**
  (`cust_201`, Crest, 6 yr), consultant flying to Lisbon Monday. Contrast: **Sam Ortiz**, Blue tier.
- **The decision:** Unlimited Global plan vs. current plan + Europe roaming pass — ranked by HER
  words (two international trips a month, phone as hotspot for the laptop, hates surprise bills).
  Honest tradeoff: the pass is cheaper if travel drops off; Global only wins at her frequency.
- **Sore point → clause:** last trip ended in an $84 roaming overage after she'd asked in-store
  about coverage. **NWM-POL-02 §4.2: Crest members — one goodwill roaming adjustment per 12 months.**
- **Approve → execute:** overage reversal (`process_return_exception`) + $84 credit + plan change
  effective before the flight (`place_order`) → confirmation in chat.
- **Hero image:** her phone tethered to a laptop on a Lisbon café table, tiles and morning light.

## 2 · "The First Leak" — home insurance decision

- **Brand/cast:** Harborstone Insurance (Standard → Select → **Preferred**). Customer **Ruth Nakamura**
  (`cust_301`, Preferred, claim-free 9 yr), water heater leak in the hall closet.
- **The decision:** file the claim vs. pay out of pocket — ranked by HER numbers (repair estimate
  vs. deductible, the claim-free discount at stake). This is the "never oversell" scenario: the
  honest tradeoff may genuinely favor NOT filing — the AI must show that math plainly.
- **Sore point → clause:** her 2019 claim was denied for late filing; she almost didn't call.
  **HS-POL-03 §2.4: Preferred + 5 claim-free years = claim forgiveness — first claim does not
  affect renewal pricing.** That clause flips the decision math on the card.
- **Approve → execute:** open claim + waive inspection fee (`process_return_exception` as the
  forgiveness rider) + schedule adjuster (`place_order`) → claim packet link in chat.
- **Hero image:** a dry, warmly-lit hallway closet with a new water heater — calm after the fix.

## 3 · "The Down Payment" — banking wire under pressure

- **Brand/cast:** Meridian Trust Bank — reuse the name, it's on brand (Everyday → Plus → **Summit
  Private**). Customer **Andre Boyd** (`cust_401`, Summit Private), closing on a house at 3 PM.
- **The decision:** same-day wire vs. cashier's check courier — ranked by his constraint (title
  company deadline today, wire fee vs. courier risk). Deterministic math in the `why` lines.
- **Sore point → clause:** last month a transfer froze on a fraud flag and he stood at a counter
  for an hour. **MTB-POL-01 §5.1: Summit Private — expedited verification callback within 15
  minutes and same-day wire fee waived.**
- **Approve → execute:** fee waiver (`apply_credit`) + wire package prepared + verification
  callback booked (`place_order`) → wire confirmation reference in chat. (Demo executes the
  *preparation* artifacts — no real money moves, honest refs as always.)
- **Hero image:** house keys on a kitchen counter in evening light, moving boxes behind.

## 4 · "The New EV" — utility rate plan

- **Brand/cast:** Lumen Valley Power (Member → **EV+ Member**). Customer **Priya Raman**
  (`cust_501`), first EV delivered two weeks ago, charges overnight, rooftop solar.
- **The decision:** Time-of-Use rate vs. flat EV rate — ranked by her stated charging pattern
  (overnight, solar offset daytime). Honest tradeoff: flat wins if her schedule changes.
- **Sore point → clause:** first post-EV bill jumped $120 with no warning. **LVP-POL-04 §1.3:
  rate switches within 60 days of EV registration may be backdated one full billing cycle.**
- **Approve → execute:** backdated rate switch (`place_order`) + $120-difference credit
  (`apply_credit`) + charger rebate enrollment → confirmation in chat.
- **Hero image:** a garage at night, EV charging with a soft green ring of light, bikes on the wall.

## 5 · "The Anniversary" — hotel loyalty rebooking

- **Brand/cast:** Solstice Hotels (Traveler → Voyager → **Meridian Club** — wink). Guest
  **Elena + Marcus Webb** (`cust_601`, Meridian Club), 10th anniversary weekend.
- **The decision:** Terrace Suite package vs. two-night spa bundle — ranked by what Elena SAID
  (sunset dinner matters most, spa is Marcus's wish, budget cap stated out loud).
- **Sore point → clause:** last stay, the front desk refused the late checkout her tier
  "guarantees." **SOL-POL-02 §3.3: Meridian Club late checkout is guaranteed, not
  availability-based; refusal earns a 10k-point service recovery.**
- **Approve → execute:** book the package (`place_order`, offer-gated on her yes) + 10k goodwill
  points (`apply_credit`) + profile note for guaranteed 2 PM checkout → itinerary in chat.
- **Hero image:** a terrace table set for two at golden hour, city below, two glasses waiting.

## 6 · "The Growing Team" — SaaS seats and renewal

- **Brand/cast:** Fathom Analytics Cloud (Starter → Pro → **Scale**). Admin **Jordan Lee**
  (`cust_701`, Scale account owner), team growing 8 → 14 before Q4.
- **The decision:** stay Pro monthly per-seat vs. Business annual bundle — the comparison card's
  `why` lines carry REAL per-seat math from the catalog (code computes it, the LLM cites it).
- **Sore point → clause:** last renewal double-billed and support took three weeks to fix it.
  **FAC-POL-05 §2.2: billing errors credit at 2× the overcharge; upgrades inside the renewal
  window lock current pricing for 24 months.**
- **Approve → execute:** 2× billing credit (`apply_credit`) + co-termed upgrade with price lock
  (`place_order`) → updated invoice in chat. Contrast customer: a Starter admin gets the honest
  "price lock doesn't apply below Scale" + escalate offer.
- **Hero image:** a team standup around a wall screen of dashboards, six new empty chairs pulled in.

## 7 · "The Limping Golden" — pet insurance claim

- **Brand/cast:** Brightpaw Pet Care (Basic → **Whole-Life**). Customer **Maggie Sullivan**
  (`cust_801`, Whole-Life since puppyhood), golden retriever **Biscuit**, hind-leg sprain.
- **The decision:** urgent orthopedic consult now vs. regular vet Thursday — ranked by what she
  said (limp is improving, travel Friday, cost anxiety). Honest tradeoff both ways; the AI never
  plays doctor — it ranks logistics and coverage, and the knowledge answers quote policy only.
- **Sore point → clause:** last year a claim was denied as "pre-existing" — it was a coding
  error she never got fixed. **BPW-POL-03 §4.1: Whole-Life continuous-coverage pets — pre-existing
  designations are reviewable; miscoded claims resubmit within 24 months.**
- **Approve → execute:** resubmit the old claim (`process_return_exception`) + book the consult
  (`place_order`) + care summary (`send_receipt`) → link in chat.
- **Hero image:** a golden retriever mid-fetch on a beach at sunrise — the image generator's
  favorite subject on earth; this demo's hero moment is unfair.

## 8 · "The 1,200 Miles" — automotive goodwill repair

- **Brand/cast:** Aster Motors (Owner → **Aster One** certified-owner program). Customer
  **Victor Reyes** (`cust_901`, Aster One, bought new), transmission fault 1,200 miles past the
  powertrain warranty.
- **The decision:** dealer repair with goodwill assistance vs. certified trade-in credit — ranked
  by his stated intent (planned to keep it 5 more years; kid starts driving next fall).
- **Sore point → clause:** he reported "hesitation on shifts" AT a recall visit last year — inside
  warranty — and the notes prove it. **AST-POL-01 §6.2: documented in-warranty complaints extend
  goodwill coverage for related repairs up to 12 months / 12,000 miles.** The AI finding that
  clause against his service history is the best policy-archaeology beat in the catalog.
- **Approve → execute:** open goodwill case at 80% coverage (`process_return_exception` +
  `apply_credit`) + service appointment with loaner (`place_order`) → case summary in chat.
- **Hero image:** his sedan on a mountain overlook at dawn, a learner's-permit-aged kid leaning
  on the passenger door.

## 9 · "The Friday Move" — ISP install for a WFH move

- **Brand/cast:** Skylark Fiber (Connect → **Connect Max**). Customer **Amara Diallo**
  (`cust_1001`, Connect Max), moving Friday, client video calls Monday 9 AM.
- **The decision:** self-install kit shipped today vs. tech visit Saturday — ranked by her stated
  stakes (Monday deadline, old building wiring unknown, comfort with hardware).
- **Sore point → clause:** at her last address the tech missed a four-hour window entirely.
  **SKY-POL-02 §2.1: after a missed appointment, the customer holds priority-rebook status for
  6 months — first slot of the day, $50 service credit, live tech ETA.**
- **Approve → execute:** priority Saturday 8 AM slot (`place_order`) + $50 credit
  (`apply_credit`) + backup self-install kit shipped (`place_order` #2 — a two-action exec block)
  → confirmation + ETA link in chat.
- **Hero image:** a sunlit new apartment, desk by the window already set up, moving boxes behind,
  a video call ringing on screen.

---

## Picking your first re-skin

- **Fastest wow:** 7 (Biscuit) — the hero image sells itself; the resubmit-the-miscoded-claim
  beat is emotionally identical to Maya's return.
- **Most enterprise-credible:** 6 (SaaS) or 3 (banking) — numbers-heavy comparisons, C-suite
  familiar.
- **Best policy-archaeology story:** 8 (automotive goodwill) — the AI connects a year-old service
  note to a clause the customer never knew existed. That's the "AI read everything so the agent
  didn't have to" thesis in one beat.
- **Every one of them** keeps the same seven-beat run of show, the same test-block format, and the
  same wiring — SCENARIO.md is the only file that changes meaningfully.
