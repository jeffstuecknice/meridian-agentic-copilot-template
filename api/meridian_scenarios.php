<?php
/**
 * meridian_scenarios.php — the nine catalog scenarios (SCENARIO_CATALOG.md), data-complete.
 *
 * Each scenario = one hero customer (top tier — the policy exception applies) + a two-option
 * catalog duo. Records are free-form JSON the composer grounds in; policyKeywords steers the
 * Knowledge-Store query; every catalog item carries img (static product shot) and imgPrompt
 * (the brief tools/gen_catalog_images.py used to create it — regeneration is reproducible).
 * Test any scenario live: say "This is <name>" or just paste the cust_ id into the chat.
 */

function meridian_scenario_customers() {
  return [

    // 1 · THE ROAMER — telecom plan upgrade
    'cust_201' => [
      'name' => 'Dana Whitfield', 'initials' => 'DW', 'brand' => 'Northwave Mobile',
      'program' => 'Northwave Tiers (Blue › Wave › Crest)', 'tier' => 'Crest',
      'policyKeywords' => 'roaming overage goodwill adjustment international travel pass credit bundling',
      'memberSince' => 2020, 'occupation' => 'management consultant',
      'valueNote' => '6-year Crest member; two international trips a month; autopay since day one',
      'sentimentLabel' => 'Focused, slightly burned', 'sentimentPct' => 58,
      'sentimentNote' => 'Wants this settled before Monday\'s flight · June overage still stings',
      'roamingIncident' => ['amount' => 84.00, 'tripMonth' => 'June', 'billRef' => 'NW-INV-30417',
        'note' => 'She asked in-store about Lisbon coverage BEFORE the trip and was told she was set; the overage landed anyway'],
      'shopping' => ['considering' => ['NW-GLOBAL-UNL', 'NW-EU-PASS'],
        'useCase' => 'flies internationally about twice a month; phone is the hotspot for her laptop; hates surprise bills'],
      'history' => ['June: $84 roaming overage in Lisbon (disputed verbally, never credited)', '4 device upgrades, never late'],
      'aiResolved' => ['Pulled her June bill and the disputed roaming line', 'Confirmed her travel dates: flying Monday'],
      'escalation' => 'Dana flies to Lisbon Monday and wants the right international plan — and she brought up the June roaming overage she was assured would not happen.',
      'handoff' => [
        ['role'=>'ai','text'=>'Hi Dana — I can see you\'re comparing our international options before Monday\'s trip.'],
        ['role'=>'customer','text'=>'Yes. And before we talk plans — last trip I got hit with an $84 roaming charge AFTER your store told me I was covered. That can\'t happen again.'],
        ['role'=>'ai','text'=>'Understood — a specialist will look at that June charge and set up the right plan before you fly. Connecting you now.'],
      ],
    ],

    // 2 · THE FIRST LEAK — home insurance decision
    'cust_301' => [
      'name' => 'Ruth Nakamura', 'initials' => 'RN', 'brand' => 'Harborstone Insurance',
      'program' => 'Harborstone (Standard › Select › Preferred)', 'tier' => 'Preferred',
      'policyKeywords' => 'claim forgiveness claim-free discount deductible water damage inspection fee renewal pricing',
      'memberSince' => 2017, 'occupation' => 'retired teacher',
      'valueNote' => 'Preferred tier; 9 claim-free years; home + auto bundled',
      'sentimentLabel' => 'Anxious, careful', 'sentimentPct' => 48,
      'sentimentNote' => 'Worried filing will raise her premium · 2019 denial made her almost not call',
      'priorClaim' => ['year' => 2019, 'outcome' => 'denied — filed 4 days past the notification window',
        'note' => 'She has been afraid of the claims process since'],
      'incident' => ['type' => 'water heater leak — hall closet, subfloor damage', 'repairEstimate' => 4800.00, 'deductible' => 1000.00],
      'shopping' => ['considering' => ['HS-CLAIM-FILE', 'HS-SELF-PAY'],
        'useCase' => 'wants the math straight: deductible vs. her claim-free discount vs. paying the contractor herself'],
      'history' => ['2019 storm claim denied (late filing)', '9 consecutive claim-free years since'],
      'aiResolved' => ['Logged the leak with photos from her phone', 'Pulled her policy, deductible and claim history'],
      'escalation' => 'Ruth has water damage from a failed water heater and cannot decide whether to file — the 2019 denial and her claim-free discount are both weighing on her.',
      'handoff' => [
        ['role'=>'ai','text'=>'Hi Ruth — I have the photos of the closet damage and your policy in front of me.'],
        ['role'=>'customer','text'=>'I just don\'t know if I should even file. Last time I tried, in 2019, it was denied and it was awful. And I don\'t want my rate going up after nine good years.'],
        ['role'=>'ai','text'=>'That\'s exactly the right question — a specialist will lay out both paths with real numbers. One moment.'],
      ],
    ],

    // 3 · THE DOWN PAYMENT — banking wire under deadline
    'cust_401' => [
      'name' => 'Andre Boyd', 'initials' => 'AB', 'brand' => 'Meridian Trust Bank',
      'program' => 'Meridian Trust (Everyday › Plus › Summit Private)', 'tier' => 'Summit Private',
      'policyKeywords' => 'wire fee waiver expedited verification fraud hold same-day cutoff Summit Private',
      'memberSince' => 2014, 'occupation' => 'physical therapist, first-time home buyer',
      'valueNote' => 'Summit Private; 11-year relationship; mortgage pre-approval with us',
      'sentimentLabel' => 'Time-pressed, tense', 'sentimentPct' => 44,
      'sentimentNote' => 'Closing at 3 PM today · last month\'s frozen transfer is fresh',
      'fraudHoldIncident' => ['month' => 'last month', 'note' => 'A legitimate $9,200 transfer froze on a fraud flag; he stood at a branch counter for an hour to release it'],
      'wireNeed' => ['amount' => 62500.00, 'deadline' => '3:00 PM today — title company closing', 'payee' => 'Lakeside Title & Escrow'],
      'shopping' => ['considering' => ['MTB-WIRE-SAME', 'MTB-CHECK-COURIER'],
        'useCase' => 'closing funds must arrive before 3 PM today; cannot risk a repeat of last month\'s freeze'],
      'history' => ['Legitimate transfer frozen by fraud flag last month (released after branch visit)'],
      'aiResolved' => ['Verified his identity and the title company\'s wire instructions on file', 'Confirmed the 3 PM closing deadline'],
      'escalation' => 'Andre needs his down payment at the title company before a 3 PM closing and is choosing between a same-day wire and a couriered cashier\'s check — after last month\'s fraud-hold experience.',
      'handoff' => [
        ['role'=>'ai','text'=>'Hi Andre — congratulations on the closing. I can see the wire instructions from Lakeside Title on file.'],
        ['role'=>'customer','text'=>'Thanks — but I\'m nervous. Last month you froze my transfer and I lost an hour at a branch. If that happens today at 2 PM, I lose the house.'],
        ['role'=>'ai','text'=>'Understood — a specialist will make sure this one is verified up front and moves on time. Connecting you.'],
      ],
    ],

    // 4 · THE NEW EV — utility rate plan
    'cust_501' => [
      'name' => 'Priya Raman', 'initials' => 'PR', 'brand' => 'Lumen Valley Power',
      'program' => 'Lumen Valley (Member › EV+ Member)', 'tier' => 'EV+ Member',
      'policyKeywords' => 'EV rate switch backdating billing cycle registration charger rebate time-of-use',
      'memberSince' => 2019, 'occupation' => 'software engineer',
      'valueNote' => 'EV+ registered two weeks ago; rooftop solar since 2022; paperless + autopay',
      'sentimentLabel' => 'Annoyed, data-driven', 'sentimentPct' => 52,
      'sentimentNote' => 'Bill spiked $120 the month the EV arrived · wants the numbers to make sense',
      'billIncident' => ['amount' => 120.00, 'note' => 'First post-EV bill jumped $120 with no rate guidance; she charged nightly on the standard rate'],
      'evProfile' => ['vehicle' => 'registered 2 weeks ago', 'charging' => 'overnight, weeknights', 'solar' => 'rooftop, exports midday'],
      'shopping' => ['considering' => ['LVP-RATE-TOU', 'LVP-RATE-FLAT'],
        'useCase' => 'charges overnight on weeknights; rooftop solar exports midday; wants a predictable, fair bill'],
      'history' => ['Solar interconnection 2022 — smooth', 'Last bill +$120 after the EV arrived'],
      'aiResolved' => ['Pulled her last three bills and hourly usage curve', 'Confirmed EV registration date (14 days ago)'],
      'escalation' => 'Priya\'s first post-EV bill spiked $120 and she wants the right EV rate — and the spike addressed — now that the car is registered.',
      'handoff' => [
        ['role'=>'ai','text'=>'Hi Priya — I can see the new EV registration and your usage curve since the car arrived.'],
        ['role'=>'customer','text'=>'That last bill was $120 higher and nobody told me the standard rate would do that with overnight charging. I charge at night and my solar covers the day.'],
        ['role'=>'ai','text'=>'That pattern matters a lot for which rate wins — a specialist will run both against your actual usage. One moment.'],
      ],
    ],

    // 5 · THE ANNIVERSARY — hotel loyalty rebooking
    'cust_601' => [
      'name' => 'Elena Webb', 'initials' => 'EW', 'brand' => 'Solstice Hotels',
      'program' => 'Solstice (Traveler › Voyager › Meridian Club)', 'tier' => 'Meridian Club',
      'policyKeywords' => 'late checkout guarantee service recovery points package upgrade anniversary',
      'memberSince' => 2016, 'occupation' => 'architect',
      'valueNote' => 'Meridian Club; 40+ nights/year; celebrating a 10th anniversary',
      'sentimentLabel' => 'Excited, one bruise', 'sentimentPct' => 66,
      'sentimentNote' => 'Thrilled about the weekend · last stay\'s refused late checkout still bugs her',
      'checkoutIncident' => ['stay' => 'March, Solstice Harbor', 'note' => 'Front desk refused the late checkout her tier guarantees, citing availability — she had a 1 PM flight and sat in the lobby'],
      'occasion' => ['event' => '10th wedding anniversary with Marcus', 'dates' => 'weekend after next', 'priorities' => 'sunset dinner matters most to Elena; the spa is Marcus\'s wish; stated budget cap ~$750'],
      'shopping' => ['considering' => ['SOL-TERRACE', 'SOL-SPA'],
        'useCase' => 'anniversary weekend; sunset dinner is her top priority, spa is his; budget cap around $750'],
      'history' => ['March: late checkout refused at Solstice Harbor despite tier guarantee', '43 nights last year'],
      'aiResolved' => ['Confirmed weekend availability for both packages', 'Noted the anniversary occasion on the reservation shell'],
      'escalation' => 'Elena is choosing between the Terrace Suite anniversary package and the Spa Escape for her 10th anniversary — and mentioned the late checkout her tier guarantees was refused in March.',
      'handoff' => [
        ['role'=>'ai','text'=>'Hi Elena — happy almost-anniversary! Both weekend packages have availability.'],
        ['role'=>'customer','text'=>'We\'re torn. The sunset dinner is what I really want, Marcus wants the spa day, and we\'d like to stay under about $750. Also — last stay your desk refused the late checkout I\'m supposed to be guaranteed.'],
        ['role'=>'ai','text'=>'A specialist will sort the package AND that checkout guarantee properly. Connecting you now.'],
      ],
    ],

    // 6 · THE GROWING TEAM — SaaS seats and renewal
    'cust_701' => [
      'name' => 'Jordan Lee', 'initials' => 'JL', 'brand' => 'Fathom Analytics Cloud',
      'program' => 'Fathom plans (Starter › Pro › Scale)', 'tier' => 'Scale',
      'policyKeywords' => 'billing error double credit renewal window price lock seat upgrade co-term',
      'memberSince' => 2022, 'occupation' => 'head of operations, 14-person consultancy',
      'valueNote' => 'Scale account owner; renewal window opens this month; team growing 8 → 14',
      'sentimentLabel' => 'Pragmatic, wary', 'sentimentPct' => 55,
      'sentimentNote' => 'Ready to upgrade · last renewal\'s double-billing took 3 weeks to fix',
      'billingIncident' => ['amount' => 880.00, 'note' => 'Last renewal charged twice; support took three weeks to reverse it and never credited the inconvenience', 'invoiceRef' => 'FAC-INV-99120'],
      'teamProfile' => ['seatsNow' => 8, 'seatsNeeded' => 14, 'deadline' => 'before Q4 planning'],
      'shopping' => ['considering' => ['FAC-BIZ-ANNUAL', 'FAC-PRO-MONTHLY'],
        'useCase' => 'growing 8 to 14 seats before Q4; wants cost certainty but fears annual lock-in after last renewal\'s billing mess'],
      'history' => ['Double-billed at last renewal (FAC-INV-99120) — reversed after 3 weeks', '2 years on Scale'],
      'aiResolved' => ['Pulled both renewal invoices and the double-charge record', 'Confirmed current seat count and renewal window'],
      'escalation' => 'Jordan is upgrading from 8 to 14 seats and choosing between the Business annual bundle and staying monthly — and expects the double-billing from last renewal to be made right first.',
      'handoff' => [
        ['role'=>'ai','text'=>'Hi Jordan — I can see the renewal window just opened and the seat request for 14.'],
        ['role'=>'customer','text'=>'Before we talk upgrade: last renewal you billed us twice and it took three weeks to fix. I need the math on annual vs monthly for 14 seats, and I need to trust the billing this time.'],
        ['role'=>'ai','text'=>'Fair on both counts — a specialist will bring the invoice history and both quotes. One moment.'],
      ],
    ],

    // 7 · THE LIMPING GOLDEN — pet insurance claim
    'cust_801' => [
      'name' => 'Maggie Sullivan', 'initials' => 'MS', 'brand' => 'Brightpaw Pet Care',
      'program' => 'Brightpaw (Basic › Whole-Life)', 'tier' => 'Whole-Life',
      'policyKeywords' => 'pre-existing review miscoded claim resubmission continuous coverage orthopedic',
      'memberSince' => 2019, 'occupation' => 'nurse',
      'valueNote' => 'Whole-Life since Biscuit was a puppy — continuous coverage, zero lapses',
      'sentimentLabel' => 'Worried about her dog', 'sentimentPct' => 40,
      'sentimentNote' => 'Biscuit is limping · last year\'s "pre-existing" denial has her braced for a fight',
      'pet' => ['name' => 'Biscuit', 'breed' => 'Golden Retriever', 'age' => 6, 'issue' => 'hind-leg limp after fetch, improving slowly'],
      'deniedClaim' => ['year' => 2025, 'amount' => 410.00, 'claimRef' => 'BPW-CLM-70233',
        'note' => 'Denied as "pre-existing" — the vet\'s office miscoded a routine checkup as an orthopedic visit; never corrected'],
      'shopping' => ['considering' => ['BPW-ORTHO-NOW', 'BPW-VET-THU'],
        'useCase' => 'limp is improving; she travels Friday; anxious about cost after last year\'s denial'],
      'history' => ['2025 claim BPW-CLM-70233 denied as pre-existing (miscoded)', '6 years continuous Whole-Life coverage'],
      'aiResolved' => ['Pulled Biscuit\'s coverage and the 2025 denied claim with its coding', 'Found tomorrow 9:40 AM and Thursday appointment options'],
      'escalation' => 'Maggie needs to choose between an orthopedic consult tomorrow and the regular vet Thursday for Biscuit\'s limp — and the 2025 "pre-existing" denial (a coding error) is coloring everything.',
      'handoff' => [
        ['role'=>'ai','text'=>'Hi Maggie — poor Biscuit! I can see his coverage and both appointment options.'],
        ['role'=>'customer','text'=>'He\'s limping after fetch but it IS getting better, and I fly Friday. Honestly, after you called his checkup "pre-existing" last year and denied my claim, I\'m scared to even use this insurance.'],
        ['role'=>'ai','text'=>'That denial deserves a real look — a specialist will review the coding and get the right appointment booked. Connecting you.'],
      ],
    ],

    // 8 · THE 1,200 MILES — automotive goodwill repair
    'cust_901' => [
      'name' => 'Victor Reyes', 'initials' => 'VR', 'brand' => 'Aster Motors',
      'program' => 'Aster One certified-owner program', 'tier' => 'Aster One',
      'policyKeywords' => 'goodwill assistance documented complaint warranty extension powertrain transmission',
      'memberSince' => 2021, 'occupation' => 'restaurant owner',
      'valueNote' => 'Bought new; every service at the dealer; Aster One since purchase',
      'sentimentLabel' => 'Frustrated, braced for a fight', 'sentimentPct' => 35,
      'sentimentNote' => 'Transmission fault 1,200 miles out of warranty · he reported the symptom IN warranty',
      'vehicle' => ['model' => 'Aster Meridian GT sedan', 'purchased' => 'new, 2021', 'mileage' => 61200, 'warrantyEnd' => '60,000 mi powertrain'],
      'serviceHistory' => ['recallVisit' => ['date' => 'last year, at 52,300 mi', 'note' => 'During the recall visit he reported "hesitation on shifts" — it is WRITTEN IN THE SERVICE NOTES; the shop found no fault code and released the car']],
      'repairNeed' => ['issue' => 'transmission fault, confirmed by dealer diagnostics', 'estimate' => 3200.00],
      'shopping' => ['considering' => ['AST-REPAIR-GW', 'AST-TRADE-CERT'],
        'useCase' => 'planned to keep the car 5 more years; his kid starts driving next fall; feels burned that the symptom he reported in-warranty became this'],
      'history' => ['Recall visit last year: reported shift hesitation at 52,300 mi (documented, no action)', 'All scheduled maintenance on time'],
      'aiResolved' => ['Pulled the full service history including the recall-visit notes', 'Confirmed dealer diagnostic estimate: $3,200'],
      'escalation' => 'Victor\'s transmission failed 1,200 miles past the powertrain warranty — but he reported the symptom during an in-warranty recall visit, and it\'s in the notes. He\'s weighing a goodwill repair vs. a certified trade-in.',
      'handoff' => [
        ['role'=>'ai','text'=>'Hi Victor — I have the dealer\'s diagnosis and your complete service history here.'],
        ['role'=>'customer','text'=>'I told your own shop about the shifting LAST YEAR, during the recall, while it was still under warranty. Now it fails at 61,200 miles and suddenly it\'s my problem? I planned to keep this car for my son.'],
        ['role'=>'ai','text'=>'The fact that it\'s documented in-warranty matters — a specialist will review exactly what that entitles you to. One moment.'],
      ],
    ],

    // 9 · THE FRIDAY MOVE — ISP install for a WFH move
    'cust_1001' => [
      'name' => 'Amara Diallo', 'initials' => 'AD', 'brand' => 'Skylark Fiber',
      'program' => 'Skylark (Connect › Connect Max)', 'tier' => 'Connect Max',
      'policyKeywords' => 'missed appointment priority rebook service credit install window transfer',
      'memberSince' => 2021, 'occupation' => 'UX consultant, fully remote',
      'valueNote' => 'Connect Max; 4 years; moving across town Friday',
      'sentimentLabel' => 'Deadline stress', 'sentimentPct' => 46,
      'sentimentNote' => 'Client video calls Monday 9 AM · last install\'s missed window not forgotten',
      'missedApptIncident' => ['when' => 'current address, 2021 install', 'note' => 'Tech missed the entire four-hour window; she waited with no ETA and lost a workday'],
      'move' => ['newAddress' => 'across town', 'moveDay' => 'Friday', 'hardDeadline' => 'client video calls Monday 9:00 AM', 'buildingNote' => 'older building, wiring condition unknown'],
      'shopping' => ['considering' => ['SKY-TECH-SAT', 'SKY-SELF-KIT'],
        'useCase' => 'moving Friday; must be solid for Monday 9 AM video calls; old building with unknown wiring; comfortable with hardware but wants certainty'],
      'history' => ['2021 install: four-hour window missed entirely', '4 years, zero late payments'],
      'aiResolved' => ['Confirmed serviceability at the new address', 'Found Saturday tech slots and same-day kit shipping'],
      'escalation' => 'Amara moves Friday and must be online for client calls Monday 9 AM — choosing between a Saturday tech visit and a self-install kit, with 2021\'s missed install window on her mind.',
      'handoff' => [
        ['role'=>'ai','text'=>'Hi Amara — good news: the new address is serviceable and I can see Saturday options.'],
        ['role'=>'customer','text'=>'I move Friday and I\'m on client video calls Monday at 9. Last time your tech missed the whole window and I lost a day — I can\'t gamble like that with this move. The building\'s old, too; no idea what the wiring\'s like.'],
        ['role'=>'ai','text'=>'A specialist will lock in the safest path for Monday — connecting you with everything you\'ve told me.'],
      ],
    ],

  ];
}

/* ---- the 18 scenario catalog items (get_products serves each customer their duo) ---- */
function meridian_catalog_extra() {
  return [
    'NW-GLOBAL-UNL' => ['sku'=>'NW-GLOBAL-UNL','name'=>'Global Unlimited Plan','price'=>95.00,'unit'=>'per month',
      'coverage'=>'Unlimited high-speed data in 90+ countries','hotspot'=>'25 GB international hotspot','overage'=>'None possible — truly unlimited',
      'bestFor'=>'2+ international trips a month','img'=>'nw_global.png',
      'imgPrompt'=>'A smartphone on an airplane tray table beside a passport, world-map route lines glowing softly on its screen as abstract shapes, warm cabin light. Clean lifestyle product photography, no readable text, no logos, no people.'],
    'NW-EU-PASS' => ['sku'=>'NW-EU-PASS','name'=>'Europe Travel Pass (on current plan)','price'=>60.00,'unit'=>'per trip (est., $10/day)',
      'coverage'=>'5 GB/day across the EU on top of the current plan','hotspot'=>'Capped at 5 GB/day shared','overage'=>'Possible after the daily cap',
      'bestFor'=>'Occasional European trips','img'=>'nw_eupass.png',
      'imgPrompt'=>'A smartphone resting on a Lisbon café table with azulejo tiles, espresso cup beside it, soft morning light. Clean lifestyle product photography, no readable text, no logos, no people.'],

    'HS-CLAIM-FILE' => ['sku'=>'HS-CLAIM-FILE','name'=>'File the Claim (adjuster + covered repair)','price'=>1000.00,'unit'=>'deductible',
      'covers'=>'$4,800 repair estimate covered after deductible','timeline'=>'Adjuster within 48 hours','risk'=>'Normally affects claim-free pricing — check forgiveness eligibility',
      'bestFor'=>'Larger repairs where coverage math wins','img'=>'hs_claim.png',
      'imgPrompt'=>'A bright, freshly repaired hallway closet with a new water heater, clean dry hardwood floor, warm afternoon light through a window. Calm interior photography, no readable text, no logos, no people.'],
    'HS-SELF-PAY' => ['sku'=>'HS-SELF-PAY','name'=>'Self-Pay Repair (no claim)','price'=>1450.00,'unit'=>'out of pocket (contractor quote)',
      'covers'=>'Limited scope — visible damage only','timeline'=>'Contractor availability next week','risk'=>'Hidden subfloor damage stays yours',
      'bestFor'=>'Small repairs when claim history is at risk','img'=>'hs_selfpay.png',
      'imgPrompt'=>'A toolbox and level resting on clean hardwood in a sunlit hallway mid-renovation, dust motes in the light. Calm interior photography, no readable text, no logos, no people.'],

    'MTB-WIRE-SAME' => ['sku'=>'MTB-WIRE-SAME','name'=>'Same-Day Domestic Wire','price'=>35.00,'unit'=>'fee (waived for Summit Private)',
      'arrival'=>'~2 hours after release; 5:00 PM ET cutoff','certainty'=>'Direct to escrow, confirmed reference number','risk'=>'Verification hold if not pre-cleared',
      'bestFor'=>'Same-day deadlines','img'=>'mtb_wire.png',
      'imgPrompt'=>'House keys with a ribbon resting on a polished kitchen counter in golden evening light, moving boxes softly blurred in the background. Warm lifestyle photography, no readable text, no logos, no people.'],
    'MTB-CHECK-COURIER' => ['sku'=>'MTB-CHECK-COURIER','name'=>'Cashier\'s Check + Courier','price'=>48.00,'unit'=>'check + overnight courier',
      'arrival'=>'Tomorrow ~10 AM — after a 3 PM closing today','certainty'=>'Physical instrument, signature on delivery','risk'=>'Misses any same-day deadline',
      'bestFor'=>'Next-day settlements','img'=>'mtb_check.png',
      'imgPrompt'=>'A sealed cream envelope on a leather portfolio beside a fountain pen on a mahogany desk, soft window light. Elegant still-life photography, no readable text, no logos, no people.'],

    'LVP-RATE-TOU' => ['sku'=>'LVP-RATE-TOU','name'=>'Time-of-Use EV Rate','price'=>61.00,'unit'=>'est./month at her overnight pattern',
      'nightRate'=>'$0.09/kWh overnight (11 PM–6 AM)','solarFit'=>'Peak-hour exports credit at the high rate — pairs with rooftop solar','risk'=>'Costs more if charging shifts to daytime',
      'bestFor'=>'Disciplined overnight chargers with solar','img'=>'lvp_tou.png',
      'imgPrompt'=>'An electric car charging in a tidy garage at night, soft green charge-ring glow, moonlight through the window, bicycles on the wall. Quiet nighttime photography, no readable text, no logos, no people.'],
    'LVP-RATE-FLAT' => ['sku'=>'LVP-RATE-FLAT','name'=>'Flat EV Rate','price'=>74.00,'unit'=>'flat/month',
      'nightRate'=>'Same price all hours','solarFit'=>'Standard export credit only','risk'=>'None — schedule-proof',
      'bestFor'=>'Unpredictable charging schedules','img'=>'lvp_flat.png',
      'imgPrompt'=>'An electric car charging in a bright driveway on a sunny afternoon, rooftop solar panels visible on the house behind. Clean residential photography, no readable text, no logos, no people.'],

    'SOL-TERRACE' => ['sku'=>'SOL-TERRACE','name'=>'Terrace Suite Anniversary Package','price'=>689.00,'unit'=>'2 nights',
      'includes'=>'Terrace suite, private sunset dinner for two, sparkling wine turn-down','spa'=>'Spa access not included (à la carte)','fit'=>'Built around the sunset dinner',
      'bestFor'=>'The dinner-first anniversary','img'=>'sol_terrace.png',
      'imgPrompt'=>'A hotel terrace table elegantly set for two at golden hour, city skyline below, candles and two glasses catching the sunset. Romantic hospitality photography, no readable text, no logos, no people.'],
    'SOL-SPA' => ['sku'=>'SOL-SPA','name'=>'Signature Spa Escape','price'=>739.00,'unit'=>'2 nights',
      'includes'=>'Deluxe room, full couples spa day, late breakfast','spa'=>'The centerpiece — 4-hour couples ritual','fit'=>'Dinner reservation possible but not the private sunset setup',
      'bestFor'=>'The spa-first anniversary','img'=>'sol_spa.png',
      'imgPrompt'=>'A serene spa relaxation room with two loungers, eucalyptus steam, soft robes folded, warm stone and candlelight. Tranquil hospitality photography, no readable text, no logos, no people.'],

    'FAC-BIZ-ANNUAL' => ['sku'=>'FAC-BIZ-ANNUAL','name'=>'Business Annual Bundle (15 seats)','price'=>13500.00,'unit'=>'per year (≈$75/seat/mo)',
      'terms'=>'24-month price lock inside the renewal window; 15th seat included free','flex'=>'Annual commitment','support'=>'Priority support + dedicated CSM',
      'bestFor'=>'Teams settling at 12+ seats','img'=>'fac_annual.png',
      'imgPrompt'=>'A modern team workspace with a large wall display showing colorful abstract analytics shapes, six chairs pulled up, morning light. Clean office photography, no readable text, no logos, no people.'],
    'FAC-PRO-MONTHLY' => ['sku'=>'FAC-PRO-MONTHLY','name'=>'Pro Monthly (14 seats)','price'=>1540.00,'unit'=>'per month (≈$110/seat)',
      'terms'=>'Month to month, cancel anytime','flex'=>'Seats flex up/down monthly','support'=>'Standard support',
      'bestFor'=>'Headcount still in flux','img'=>'fac_monthly.png',
      'imgPrompt'=>'A laptop on a standing desk showing abstract colorful dashboard shapes, sticky notes on the wall behind, bright afternoon office light. Clean office photography, no readable text, no logos, no people.'],

    'BPW-ORTHO-NOW' => ['sku'=>'BPW-ORTHO-NOW','name'=>'Orthopedic Consult — tomorrow 9:40 AM','price'=>95.00,'unit'=>'copay after coverage',
      'timing'=>'Tomorrow morning — answers before Friday travel','depth'=>'Specialist exam + imaging if needed','risk'=>'Higher copay; may be more than a sprain needs',
      'bestFor'=>'Peace of mind before travel','img'=>'bpw_ortho.png',
      'imgPrompt'=>'A calm modern veterinary exam room with a padded table and gentle morning light, a leash hanging by the door. Warm clinical photography, no readable text, no logos, no people, no animals in distress.'],
    'BPW-VET-THU' => ['sku'=>'BPW-VET-THU','name'=>'Regular Vet Visit — Thursday','price'=>35.00,'unit'=>'copay',
      'timing'=>'Thursday — one day before travel','depth'=>'General exam; refers out if serious','risk'=>'A referral after Thursday collides with the Friday flight',
      'bestFor'=>'A limp that keeps improving','img'=>'bpw_thu.png',
      'imgPrompt'=>'A happy golden retriever mid-stride fetching a ball on a beach at sunrise, ears flying, soft golden light. Joyful pet photography, no readable text, no logos, no people.'],

    'AST-REPAIR-GW' => ['sku'=>'AST-REPAIR-GW','name'=>'Dealer Repair with Goodwill Assistance','price'=>640.00,'unit'=>'customer share (80% goodwill on $3,200)',
      'includes'=>'Factory parts, 24-month repair warranty, loaner car','timeline'=>'3 service days','keeps'=>'The car he planned to hand to his son',
      'bestFor'=>'Keeping a car you love','img'=>'ast_repair.png',
      'imgPrompt'=>'A well-kept sedan parked at a mountain overlook at dawn, mist in the valley below, soft warm light on the paint. Cinematic automotive photography, no readable text, no logos, no people.'],
    'AST-TRADE-CERT' => ['sku'=>'AST-TRADE-CERT','name'=>'Certified Trade-In Credit Path','price'=>2900.00,'unit'=>'trade credit toward a newer model',
      'includes'=>'As-is trade accepted despite the fault','timeline'=>'Same week','keeps'=>'Nothing — the car goes',
      'bestFor'=>'Walking away clean','img'=>'ast_trade.png',
      'imgPrompt'=>'A bright dealership forecourt at dusk with a row of clean sedans under warm lot lighting, one car with a subtle spotlight. Automotive photography, no readable text, no logos, no people.'],

    'SKY-TECH-SAT' => ['sku'=>'SKY-TECH-SAT','name'=>'Priority Tech Install — Saturday 8 AM','price'=>0.00,'unit'=>'fee waived (priority rebook)',
      'certainty'=>'First slot of the day, live tech ETA, wiring handled whatever its condition','timing'=>'Done by Saturday noon — two full days of margin','risk'=>'None material',
      'bestFor'=>'Hard Monday deadlines + unknown wiring','img'=>'sky_tech.png',
      'imgPrompt'=>'A sunlit new apartment with a tidy desk by the window, a glowing router with soft light dots, moving boxes neatly stacked behind. Bright interior photography, no readable text, no logos, no people.'],
    'SKY-SELF-KIT' => ['sku'=>'SKY-SELF-KIT','name'=>'Self-Install Kit — overnight shipped','price'=>0.00,'unit'=>'free shipping today',
      'certainty'=>'Arrives Saturday; success depends on the building\'s existing wiring','timing'=>'Online Saturday IF the jack is live','risk'=>'Old-building wiring unknown — no tech on site',
      'bestFor'=>'Modern buildings + confident DIY','img'=>'sky_kit.png',
      'imgPrompt'=>'An unboxed router kit laid out neatly on a wooden floor beside a window, cables coiled, afternoon light. Clean flat-lay product photography, no readable text, no logos, no people.'],
  ];
}
