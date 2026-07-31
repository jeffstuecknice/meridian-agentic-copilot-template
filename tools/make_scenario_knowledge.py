#!/usr/bin/env python3
"""make_scenario_knowledge.py — emit the nine scenario policy docs as knowledge/upload/*.txt.

One doc per scenario brand. Each carries THE exception clause (the SCENARIO_CATALOG.md
section number, verbatim-quotable), a credit/bundling clause the BOOK-IT beat can cite,
and a recommendation-guidance section so every brand retrieves its own "rank by stated
needs, never oversell" grounding. Upload all nine into the Meridian_Knowledge store.
"""
import os

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'knowledge', 'upload')

DOCS = {

'NWM-POL-02_Northwave_Tiers_and_Roaming.txt': """NWM-POL-02 — Northwave Mobile: Tier Benefits, Roaming & Goodwill
Applies to: Northwave Tiers (Blue, Wave, Crest). Effective 2026.

Section 1 — Tier structure. Blue is the entry tier. Wave unlocks priority support. Crest is earned at 5+ years or top-decile spend and carries every benefit in this document.

Section 2 — International options. The Europe Travel Pass provides 5 GB per day on top of the customer's current plan at $10 per day, hotspot shared within the daily cap; overage billing resumes beyond the cap. The Global Unlimited Plan includes unlimited high-speed data in 90+ countries with 25 GB of international hotspot and no overage mechanism of any kind.

Section 3 — Plan changes before travel. A plan change requested before a departure date takes effect immediately upon confirmation; no waiting period applies for Wave and Crest members.

Section 4 — Roaming charges and goodwill.
4.1 Roaming overage is billed as incurred and appears on the next invoice.
4.2 Crest members are entitled to one goodwill roaming adjustment per rolling 12 months: a disputed roaming overage is credited in full when the member states they sought coverage guidance before travel. No receipt or proof of the store conversation is required for Crest.
4.3 Goodwill roaming credits under 4.2 may be applied to the current balance or to the first invoice of a newly selected plan, in the same interaction.

Section 5 — Recommendation guidance. Recommend from the customer's stated travel pattern and usage, not from plan price. Disclose the tradeoff of the non-recommended option honestly. Never oversell: if the cheaper option fits the stated pattern better, it is the recommendation.
""",

'HS-POL-03_Harborstone_Claims_and_Forgiveness.txt': """HS-POL-03 — Harborstone Insurance: Claims, Deductibles & Claim Forgiveness
Applies to: Standard, Select and Preferred homeowner policies. Effective 2026.

Section 1 — Filing windows. Water damage must be reported within 30 days of discovery. Reports through any channel (phone, chat, app) satisfy the window on the day they are logged.

Section 2 — Claim-free pricing and forgiveness.
2.1 Claim-free discounts accrue per consecutive claim-free year and ordinarily reset when a claim is paid.
2.2 (reserved)
2.3 Select members with 7+ claim-free years may request forgiveness review.
2.4 Preferred members with 5 or more consecutive claim-free years receive claim forgiveness automatically: the first paid claim does not affect renewal pricing and does not reset the claim-free discount.
2.5 Forgiveness under 2.4 applies once per policy period and is noted on the claim record at filing time.

Section 3 — Fees. The adjuster inspection fee is waived for Select and Preferred tiers.

Section 4 — Deductible mathematics. Agents must present the covered-repair estimate, the deductible, and the out-of-pocket alternative side by side. Where forgiveness (2.4) applies, renewal-pricing risk must not be cited as a reason to avoid filing.

Section 5 — Recommendation guidance. Recommend from the customer's actual numbers and history, never from claim-volume targets. If self-pay genuinely wins on the customer's numbers, recommend self-pay and say why. Disclose hidden-damage risk honestly on self-pay paths.
""",

'MTB-POL-01_MeridianTrust_Wires_and_Verification.txt': """MTB-POL-01 — Meridian Trust Bank: Wires, Cutoffs & Expedited Verification
Applies to: Everyday, Plus and Summit Private relationships. Effective 2026.

Section 1 — Same-day wires. Domestic wires released before 5:00 PM ET settle same day, typically within two hours of release. The standard wire fee is $35.

Section 2 — Cashier's checks. Cashier's checks with overnight courier arrive the next business day by 10:30 AM; total cost $48.

Section 3 — Fraud review holds. Transfers may be held for verification when flagged. Standard verification requires a branch visit or a callback within 4 business hours.

Section 5 — Summit Private servicing.
5.1 Summit Private wires receive expedited verification: a verification callback is initiated within 15 minutes of the request, and the same-day wire fee is waived. Wires pre-verified in an active service interaction release without further holds.
5.2 A prior false-positive fraud hold on the relationship entitles the client to pre-verification at request time — the review happens before release, never after.
5.3 Fee waivers under 5.1 may be applied in the same interaction as the wire request.

Section 6 — Recommendation guidance. Recommend from the client's stated deadline. Where a deadline makes one instrument unfit (for example a next-day check against a same-day closing), state that plainly. Never let a fee difference outweigh a stated hard deadline.
""",

'LVP-POL-04_LumenValley_EV_Rates.txt': """LVP-POL-04 — Lumen Valley Power: EV Rates, Backdating & Rebates
Applies to: Member and EV+ Member accounts. Effective 2026.

Section 1 — Rate switching and backdating.
1.1 Members may switch rate plans once per billing cycle.
1.2 (reserved)
1.3 When an electric vehicle is registered on the account, a rate switch requested within 60 days of registration may be backdated to the start of the current full billing cycle, and the difference between rates for that cycle is credited to the account.
1.4 Backdating credits under 1.3 apply automatically in the same interaction as the switch.

Section 2 — The rates. The Time-of-Use EV rate bills overnight usage (11 PM to 6 AM) at $0.09/kWh with on-peak pricing daytime; solar exports credit at the on-peak rate. The Flat EV rate bills all hours at a single price and is schedule-proof.

Section 3 — Charger rebate. EV+ Members qualify for a Level-2 charger rebate; enrollment may be completed by an agent during any service interaction.

Section 4 — Recommendation guidance. Recommend from the customer's actual charging pattern and solar profile, not from average-customer assumptions. Disclose honestly when a schedule change would flip the recommendation.
""",

'SOL-POL-02_Solstice_Club_Guarantees.txt': """SOL-POL-02 — Solstice Hotels: Meridian Club Guarantees & Service Recovery
Applies to: Traveler, Voyager and Meridian Club members. Effective 2026.

Section 1 — Packages. Anniversary and Escape packages may be customized by an agent at booking; package components (dining, spa) may be noted as occasion-critical on the reservation.

Section 2 — Points. Points post at checkout; goodwill points post immediately.

Section 3 — Meridian Club guarantees.
3.1 Room-type guarantee at booking.
3.2 (reserved)
3.3 Late checkout until 2:00 PM is GUARANTEED for Meridian Club members. It is not subject to availability. A refusal at the desk is a service failure that entitles the member to a 10,000-point service recovery credit, applicable in any later interaction where the failure is identified.
3.4 Guarantee failures are honored retroactively without a formal complaint on file — the member stating the event is sufficient when the stay is on record.

Section 4 — Credits at booking. Service-recovery points and certificates may be applied toward a package in the same interaction they are granted.

Section 5 — Recommendation guidance. Recommend the package that serves the customer's STATED priority for the occasion; disclose plainly what the other package does better. Respect stated budget caps — never upsell past one.
""",

'FAC-POL-05_Fathom_Billing_and_Renewals.txt': """FAC-POL-05 — Fathom Analytics Cloud: Billing Errors, Renewals & Price Locks
Applies to: Starter, Pro and Scale plans. Effective 2026.

Section 1 — Plans. Pro bills monthly per seat and flexes freely. The Business annual bundle bills yearly, includes priority support and a dedicated CSM, and prices at the equivalent of $75 per seat per month at 15 seats.

Section 2 — Billing errors and renewal protections.
2.1 Confirmed billing errors are reversed to the original payment method.
2.2 A confirmed double-billing entitles Scale accounts to a service credit equal to 2× the overcharged amount, applicable to any invoice, in the same interaction the error is confirmed.
2.3 Upgrades executed inside the renewal window lock current per-seat pricing for 24 months (Scale and above). The lock is written to the order.
2.4 Upgrades co-term to the existing renewal date; unused monthly balances convert to credit.

Section 3 — Seats. Seat increases take effect immediately; the Business bundle includes the 15th seat at no charge.

Section 4 — Recommendation guidance. Recommend from the customer's actual seat math and stated flexibility needs. Show the per-seat arithmetic plainly. If month-to-month genuinely fits their uncertainty better, say so — never let the annual bundle's size outweigh a stated need to stay flexible.
""",

'BPW-POL-03_Brightpaw_Coverage_and_Review.txt': """BPW-POL-03 — Brightpaw Pet Care: Coverage, Pre-existing Review & Resubmission
Applies to: Basic and Whole-Life plans. Effective 2026.

Section 1 — Appointments. Specialist consults and general visits may be booked by an agent; copays are $95 (specialist) and $35 (general) after coverage.

Section 2 — Coverage. Whole-Life covers orthopedic exams, imaging and treatment at 90% after copay.

Section 3 — Travel. Boarding-related visits within 72 hours of documented owner travel are covered as standard visits.

Section 4 — Pre-existing designations.
4.1 For pets with CONTINUOUS Whole-Life coverage since first enrollment, pre-existing designations are reviewable at any time: where the designation rests on a miscoded visit record, the claim is recoded and RESUBMITTED, and resubmission is available for 24 months from the original denial.
4.2 Resubmission under 4.1 is initiated by the servicing agent in the same interaction; no new veterinary documentation is required when the original record shows the coding error.
4.3 Approved resubmissions pay at the coverage level in force on the original service date.

Section 5 — Recommendation guidance. Agents recommend appointment LOGISTICS (timing, copay, travel fit) only — never clinical judgments. Both options are presented with their honest scheduling risk; urgency claims must come from the customer or their vet, not from the agent.
""",

'AST-POL-01_Aster_Warranty_and_Goodwill.txt': """AST-POL-01 — Aster Motors: Warranty, Documented Complaints & Goodwill Assistance
Applies to: all Aster owners; enhanced terms for Aster One certified owners. Effective 2026.

Section 1 — Powertrain warranty. 60,000 miles or 60 months, whichever first.

Section 2 — Trade paths. Certified trade-in accepts vehicles with known faults at adjusted credit; Aster One owners receive the certified adjustment without a diagnostic fee.

Section 6 — Goodwill assistance.
6.1 Goodwill assistance may be offered on out-of-warranty repairs at dealer discretion.
6.2 Where a customer REPORTED a symptom related to the failed component during an in-warranty service or recall visit, and that report is documented in the service record, goodwill coverage of the related repair is extended for 12 months or 12,000 miles beyond warranty end at a minimum of 80% parts and labor. Dealer discretion does not apply — the documented report makes the assistance an entitlement.
6.3 Goodwill cases under 6.2 include a loaner vehicle for the repair duration and a 24-month warranty on the repair itself.
6.4 The customer share under 6.2 may be settled in the same interaction the case is opened.

Section 7 — Recommendation guidance. Recommend from the owner's stated intent for the vehicle (keep vs. move on), never from inventory goals. Where a goodwill entitlement exists, it is presented BEFORE any trade-in option. Disclose each path's honest downside.
""",

'SKY-POL-02_Skylark_Appointments_and_Priority.txt': """SKY-POL-02 — Skylark Fiber: Installs, Missed Appointments & Priority Rebook
Applies to: Connect and Connect Max accounts. Effective 2026.

Section 1 — Install options. Tech installs handle inside wiring regardless of condition. Self-install kits ship free overnight and depend on a live existing jack; older buildings carry unknown-wiring risk that a kit cannot resolve.

Section 2 — Missed appointments and priority status.
2.1 When Skylark misses a scheduled appointment window, the customer holds PRIORITY REBOOK status for 6 months at any address on the account, including a new address after a move: first slot of the requested day, live technician ETA tracking, a $50 service credit, and the tech-visit fee waived.
2.2 Priority status under 2.1 is invoked by the customer stating the missed appointment; where the account record shows the miss, no further validation is required.
2.3 Priority rebook and the credit may be applied in the same interaction.

Section 3 — Moves. Service transfers keep plan, pricing and tenure. A backup self-install kit may ship alongside a booked tech visit at no charge when a hard deadline is stated.

Section 4 — Recommendation guidance. Recommend from the customer's stated deadline and building conditions. Where wiring is unknown and the deadline is hard, the honest recommendation is the path that removes the unknown; state plainly what the kit cannot guarantee.
""",
}

os.makedirs(OUT, exist_ok=True)
for fn, body in DOCS.items():
    with open(os.path.join(OUT, fn), 'w', encoding='utf-8') as f:
        f.write(body)
    print('wrote', fn, '(%d chars)' % len(body))
print('\n%d docs -> %s' % (len(DOCS), OUT))
print('Upload ALL of them into the Meridian_Knowledge store (alongside the 5 MER-POL docs); wait for ready.')
