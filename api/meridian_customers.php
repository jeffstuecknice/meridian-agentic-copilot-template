<?php
/**
 * meridian_customers.php — Northlight Electronics systems of record (demo CRM).
 *
 * Record shape is the template for ALL customers — richer record = richer briefing.
 * The panel grounds itself in whatever is here; the copilot never invents CRM facts.
 * Included by meridian_api.php (get_customer).
 */

function meridian_customers() {
  return [

    'cust_101' => [
      'name'         => 'Maya Torres',
      'initials'     => 'MT',
      'tier'         => 'Summit',
      'memberSince'  => 2023,
      'ordersYtd'    => 11,
      'lifetimeSpend'=> '$6,840',
      'pointsBalance'=> '2,310 Circle Points',
      'email'        => 'maya.torres@example.com',
      'phone'        => '+1 ••• ••• 8842',
      'commsPref'    => 'SMS + email',
      'occupation'   => 'freelance photographer / designer',
      'valueNote'    => 'Top-10% spend; 3 consecutive Circle years; zero service complaints on file',
      // Handoff panel display fields (deterministic, per-scenario scripted):
      'sentimentLabel' => 'Engaged, mildly wary',
      'sentimentPct'   => 62,
      'sentimentNote'  => 'Positive about the purchase · unresolved return still stings',
      // The sore point — the storyline's policy-exception fuel:
      'openReturn'   => [
        'item'          => 'ProDock USB-C Docking Station',
        'sku'           => 'PDX-500',
        'price'         => 189.00,
        'orderRef'      => 'NL-88214',
        'purchasedDaysAgo' => 34,
        'deniedAtStore' => true,
        'deniedReason'  => 'Store associate applied the standard 30-day window; her Summit 45-day accessory window was not checked',
      ],
      // What she's shopping for (the automated agent captured this before handoff):
      'shopping'     => [
        'considering' => ['NL-AERO14', 'NL-TITAN16'],
        'useCase'     => 'photo editing, some short video; works from cafés; flies about twice a month',
        'oldMachine'  => 'battery no longer holds a charge',
      ],
      'history'      => [
        'Bought a mirrorless camera body in March — smooth delivery',
        'ProDock return attempted in-store last week — denied at the counter',
      ],
      // What the automated AI agent already handled before the human handoff:
      'aiResolved'   => [
        'Verified live stock on both laptops — each ships today from the regional warehouse',
        'Pulled her order history and Circle status into the case',
        'Captured her needs so she never has to repeat them',
      ],
      // The one thing it escalated to the human Care specialist:
      'escalation'   => 'Maya is deciding between the Aero 14 and the Titan 16, and asked about her denied ProDock return. The purchase decision plus the return-window review were escalated to a Care specialist.',
      // Condensed automated-agent conversation (the handoff transcript the panel can show):
      'handoff'      => [
        ['role'=>'ai',       'text'=>'Hi Maya — thanks for reaching Northlight. I can see you\'ve been comparing the Aero 14 and the Titan 16. Want me to line those up for you?'],
        ['role'=>'customer', 'text'=>'Yes — I edit photos, work out of cafés most days, and my old laptop\'s battery is shot. That\'s honestly why I\'m here.'],
        ['role'=>'ai',       'text'=>'Got it — battery life and portability matter most, with photo editing as the main workload. One more thing: I see an open return attempt on a ProDock docking station.'],
        ['role'=>'customer', 'text'=>'Ugh, yes. The store said I was past the window. I\'ve been a member three years — that felt bad.'],
        ['role'=>'ai',       'text'=>'I hear you. A Care specialist can review that return and walk you through the laptop decision — connecting you now with everything from our conversation.'],
      ],
    ],

    // Contrast customer — Member tier (NO extended return window) so the policy
    // reasoning visibly changes with the record. Say "this is Leo Martinez" in chat to re-target.
    'cust_102' => [
      'name'         => 'Leo Martinez',
      'initials'     => 'LM',
      'tier'         => 'Member',
      'memberSince'  => 2026,
      'ordersYtd'    => 1,
      'lifetimeSpend'=> '$248',
      'pointsBalance'=> '40 Circle Points',
      'email'        => 'leo.martinez@example.com',
      'phone'        => '+1 ••• ••• 3317',
      'commsPref'    => 'email',
      'occupation'   => 'student',
      'valueNote'    => 'New member — first Circle year',
      'sentimentLabel' => 'Curious',
      'sentimentPct'   => 70,
      'sentimentNote'  => 'First live-agent contact',
      'shopping'     => [
        'considering' => ['NL-AERO14', 'NL-TITAN16'],
        'useCase'     => 'note-taking and streaming, tight budget',
        'oldMachine'  => 'hand-me-down desktop',
      ],
      'history'      => ['Bought a mechanical keyboard in June'],
      'aiResolved'   => ['Verified live stock on both laptops'],
      'escalation'   => 'Leo wants help choosing between the Aero 14 and the Titan 16 on a student budget.',
      'handoff'      => [
        ['role'=>'ai',       'text'=>'Hi Leo — happy to help you compare the Aero 14 and Titan 16.'],
        ['role'=>'customer', 'text'=>'Mostly notes and streaming. Budget matters.'],
        ['role'=>'ai',       'text'=>'Understood — connecting you with a Care specialist to finish the decision.'],
      ],
    ],

  ];
}

// Look up a record by name first (a name spoken in chat is the strongest live signal and
// must beat a stale/published customer_id), falling back to exact customer_id key.
function meridian_lookup($customer_id, $name) {
  $all = meridian_customers();
  $name = strtolower(trim((string)$name));
  $customer_id = trim((string)$customer_id);
  if ($name !== '') {
    foreach ($all as $id => $r) {
      $rn = strtolower($r['name']);
      if ($rn === $name || strpos($rn, $name) !== false || strpos($name, $rn) !== false)
        return array_merge($r, ['customer_id' => $id]);
    }
  }
  if ($customer_id !== '' && isset($all[$customer_id])) return array_merge($all[$customer_id], ['customer_id' => $customer_id]);
  return null;
}
