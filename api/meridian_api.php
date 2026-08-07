<?php
/**
 * meridian_api.php — Northlight Electronics mock systems (demo backend).
 *
 * Call:  GET or POST  meridian_api.php?action=<name>
 *        body (POST) = JSON; GET = query params. Both accepted.
 * Auth:  none (demo). CORS open so the sandboxed tile/iframe can call it.
 *
 * Design: a small generic ACTION REGISTRY (process_return_exception, apply_credit,
 * place_order, send_receipt, escalate_case) that the copilot parameterizes — plus
 * execute_batch, which runs an APPROVED action plan in one call so the flow's
 * deterministic Approve branch needs exactly one HTTP request.
 * Every executed action returns a REAL generated reference — the LLM never invents one.
 */

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization');
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { http_response_code(204); exit; }

require_once __DIR__ . '/meridian_customers.php';

/* ---- merge GET + JSON body into one params array ----
   json_decode rejects invalid UTF-8 outright (a Latin-1 byte from a Windows curl
   console would silently drop the whole body) — salvage once before giving up. */
$body = [];
$raw = file_get_contents('php://input');
if ($raw) {
  $j = json_decode($raw, true);
  if (!is_array($j)) $j = json_decode(mb_convert_encoding($raw, 'UTF-8', 'UTF-8, ISO-8859-1'), true);
  if (is_array($j)) $body = $j;
}
$P = array_merge($_GET, $_POST, $body);
$action = isset($P['action']) ? strtolower(trim($P['action'])) : '';

function val($P, $k, $d = null) { return isset($P[$k]) && $P[$k] !== '' ? $P[$k] : $d; }
function refnum($prefix) { return $prefix . '-' . strtoupper(substr(md5(uniqid('', true)), 0, 8)); }
function out($arr) { echo json_encode($arr, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT); exit; }
function fail($msg, $code = 400) { http_response_code($code); out(['ok' => false, 'error' => $msg]); }

/* ---- the product catalog (operational data — policy lives in the Knowledge Store) ---- */
function meridian_catalog() {
  return [
    'NL-AERO14' => [
      'sku' => 'NL-AERO14', 'name' => 'Aero 14', 'price' => 1299.00,
      'weightLb' => 2.7, 'batteryHrs' => 18, 'display' => '14" 2.8K · 500 nits',
      'performance' => 'Great for photo editing and light video',
      'ports' => '2× USB-C', 'sdSlot' => false,
      'sdSlotNote' => 'No SD slot — the $29 USB-C SD reader closes the gap',
      'inStock' => true, 'shipsToday' => true, 'img' => 'aero14.png',
    ],
    'NL-TITAN16' => [
      'sku' => 'NL-TITAN16', 'name' => 'Titan 16', 'price' => 1899.00,
      'weightLb' => 4.9, 'batteryHrs' => 9, 'display' => '16" 4K wide-gamut · 600 nits',
      'performance' => 'Workstation-class — heavy video and 3D',
      'ports' => '2× USB-C · HDMI · SD slot', 'sdSlot' => true,
      'sdSlotNote' => 'Built-in SD slot — a genuine pull for photographers',
      'inStock' => true, 'shipsToday' => true, 'img' => 'titan16.png',
    ],
  ];
}

/* ---- the generic action handlers (shared by direct calls AND execute_batch) ---- */
function run_action($name, $P) {
  switch (strtolower(trim((string)$name))) {

    case 'process_return_exception':
      return ['ok' => true, 'action' => 'process_return_exception',
        'rmaRef'       => refnum('RMA'),
        'orderRef'     => val($P, 'orderRef', val($P, 'order_ref', '')),
        'item'         => val($P, 'item', ''),
        'refundAmount' => (float)val($P, 'amount', val($P, 'refundAmount', 0)),
        'method'       => 'store credit — available immediately',
        'policyClause' => val($P, 'clause', val($P, 'policy_clause', '')),
        'reason'       => val($P, 'reason', ''),
        'status'       => 'ACCEPTED', 'ts' => date('c')];

    case 'apply_credit':
      return ['ok' => true, 'action' => 'apply_credit',
        'creditRef' => refnum('CR'),
        'amount'    => (float)val($P, 'amount', 0),
        'unit'      => val($P, 'unit', 'USD'),
        'reason'    => val($P, 'reason', ''),
        'appliesTo' => 'pre-tax order total', 'ts' => date('c')];

    case 'place_order':
      $cat = meridian_catalog();
      $sku = strtoupper((string)val($P, 'sku', ''));
      if (!isset($cat[$sku])) return ['ok' => false, 'action' => 'place_order', 'error' => "unknown sku '$sku'"];
      $p = $cat[$sku];
      $credit = (float)val($P, 'creditApplied', val($P, 'credits_applied', 0));
      $total = max(0, $p['price'] - $credit);
      $ship = val($P, 'shipMethod', val($P, 'ship_method', 'expedited'));
      $sameDay = (int)date('G') < 15;   // 3:00 PM warehouse cutoff (MER-POL-04 §2.1)
      return ['ok' => true, 'action' => 'place_order',
        'orderRef' => refnum('ORD'), 'sku' => $sku, 'product' => $p['name'],
        'itemPrice' => $p['price'], 'creditApplied' => $credit, 'total' => round($total, 2),
        'shipMethod' => $ship,
        'shipDate' => $sameDay ? date('Y-m-d') . ' (ships today)' : date('Y-m-d', strtotime('+1 day')),
        'ts' => date('c')];

    case 'send_receipt':
      // Builds the customer-facing receipt page + a short link the agent delivers IN CHAT
      // (this project has no SMS provider connection yet — honest delivery over the live
      // channel beats pretending an SMS went out; see api/README.md).
      $name  = val($P, 'name', 'there');
      $items = val($P, 'detail', val($P, 'items', ''));
      $total = val($P, 'total', '');
      $order = val($P, 'orderRef', '');
      $host = $_SERVER['HTTP_HOST'] ?? '';
      // str_replace: PHP's dirname() emits a backslash on Windows dev servers (php -S)
      $dir  = rtrim(str_replace('\\', '/', dirname($_SERVER['REQUEST_URI'] ?? '/')), '/');
      $long = 'https://' . $host . $dir . '/meridian_xapp.php?receipt=1&name=' . rawurlencode($name)
            . '&items=' . rawurlencode($items) . '&total=' . rawurlencode($total) . '&order=' . rawurlencode($order);
      // shorten via the xapp's flat-file shortener (same mechanism, called in-process)
      $sd = __DIR__ . '/_short'; if (!is_dir($sd)) @mkdir($sd, 0755, true);
      $id = substr(md5($long), 0, 8);
      @file_put_contents($sd . '/' . $id . '.txt', $long);
      $short = 'https://' . $host . $dir . '/meridian_xapp.php?s=' . $id;
      return ['ok' => true, 'action' => 'send_receipt',
        'docRef' => refnum('DOC'), 'receiptUrl' => $short, 'delivery' => 'link — paste into the chat',
        'ts' => date('c')];

    case 'escalate_case':
      return ['ok' => true, 'action' => 'escalate_case',
        'handoffId' => refnum('ESC'),
        'queue'     => val($P, 'queue', 'Care specialist'),
        'summary'   => val($P, 'summary', ''),
        'contextPublished' => true, 'ts' => date('c')];

    case 'log_case_summary':
      // The wrap-up card's "Push to CRM" button — writes the case note for real and hands
      // back a real reference, same as every other action here (no invented confirmation).
      $summary = (string)val($P, 'summary', '');
      if ($summary === '') return ['ok' => false, 'action' => 'log_case_summary', 'error' => 'summary is required'];
      return ['ok' => true, 'action' => 'log_case_summary',
        'noteRef'    => refnum('NOTE'),
        'customerId' => val($P, 'customer_id', val($P, 'customerId', '')),
        'summary'    => $summary,
        'ts' => date('c')];

    default:
      return ['ok' => false, 'action' => (string)$name, 'error' => "unknown action '$name'"];
  }
}

/* ---- dispatch ---- */
switch ($action) {

  case 'get_customer': {
    $rec = meridian_lookup(val($P, 'customer_id', ''), val($P, 'name', ''));
    // A miss answers HTTP 200 + ok:false, NOT 404: Cognigy's httpRequest node (abortOnError
    // false) stores an error wrapper on 4xx instead of the body, which hides the definitive
    // "customer not found" signal the flow's bad-id latch needs (verified 2026-08-06).
    if (!$rec) out(['ok' => false, 'action' => 'get_customer', 'error' => 'customer not found']);
    // ALIAS KEYS: Cognigy context storage masks PII-ish VALUES (phone etc.) on stored
    // OBJECTS — ship the same values under neutral names; the flow also keeps the record
    // as a JSON STRING, which survives masking intact.
    $rec['phoneDisplay'] = isset($rec['phone']) ? $rec['phone'] : '';
    out(['ok' => true, 'action' => 'get_customer', 'customer' => $rec, 'ts' => date('c')]);
  }

  case 'get_products': {
    // Per-scenario catalog: the customer's record names their duo (shopping.considering);
    // no customer (or unknown skus) falls back to the retail laptops.
    $full = array_merge(meridian_catalog(), meridian_catalog_extra());
    $cid = val($P, 'customerId', val($P, 'customer_id', ''));
    $items = [];
    if ($cid !== '') {
      $rec = meridian_lookup($cid, '');
      if ($rec && isset($rec['shopping']['considering']) && is_array($rec['shopping']['considering'])) {
        foreach ($rec['shopping']['considering'] as $sku) { if (isset($full[$sku])) $items[] = $full[$sku]; }
      }
    }
    if (count($items) < 2) $items = array_values(meridian_catalog());
    out(['ok' => true, 'action' => 'get_products', 'products' => $items, 'ts' => date('c')]);
  }

  case 'catalog_all': {
    // tooling endpoint: the full item map (used by tools/gen_catalog_images.py)
    out(['ok' => true, 'action' => 'catalog_all',
         'items' => array_merge(meridian_catalog(), meridian_catalog_extra()), 'ts' => date('c')]);
  }

  case 'execute_batch': {
    // The deterministic Approve path: POST {customerId, actions:[{action, params:{...}}, ...]}
    // Runs each action through the same handlers as direct calls; refs are real.
    $acts = val($P, 'actions', []);
    if (is_string($acts)) { $d = json_decode($acts, true); if (is_array($d)) $acts = $d; }
    if (!is_array($acts) || !count($acts)) fail('execute_batch needs a non-empty actions array');
    if (count($acts) > 6) fail('execute_batch caps at 6 actions per approval');
    $cid = val($P, 'customerId', val($P, 'customer_id', ''));
    $executed = []; $allOk = true;
    foreach ($acts as $a) {
      $nm = is_array($a) ? val($a, 'action', '') : '';
      $pp = (is_array($a) && isset($a['params']) && is_array($a['params'])) ? $a['params'] : [];
      $pp['customerId'] = $cid;
      $r = run_action($nm, $pp);
      $ref = '';
      foreach (['rmaRef','creditRef','orderRef','docRef','handoffId','noteRef'] as $k) { if (!empty($r[$k])) { $ref = $r[$k]; break; } }
      $executed[] = ['action' => $nm, 'ref' => $ref, 'ok' => ($r['ok'] === true),
                     'detail' => ($r['ok'] === true) ? $r : ['error' => val($r, 'error', 'failed')]];
      if ($r['ok'] !== true) $allOk = false;
    }
    out(['ok' => $allOk, 'action' => 'execute_batch', 'executed' => $executed,
         'customerId' => $cid, 'ts' => date('c')]);
  }

  /* single-action routes — the Command Agent's tools call these directly */
  case 'process_return_exception':
  case 'apply_credit':
  case 'place_order':
  case 'send_receipt':
  case 'escalate_case':
  case 'log_case_summary': {
    $r = run_action($action, $P);
    if ($r['ok'] !== true) fail($r['error'], 400);
    out($r);
  }

  case 'ping':
  case '': {
    out(['ok' => true, 'service' => 'Northlight Electronics Mock API (Meridian)', 'version' => '1.0',
         'actions' => ['get_customer', 'get_products', 'execute_batch', 'process_return_exception',
                       'apply_credit', 'place_order', 'send_receipt', 'escalate_case',
                       'log_case_summary', 'ping'],
         'usage' => 'GET|POST meridian_api.php?action=<name>  (JSON body or query params)',
         'ts' => date('c')]);
  }

  default:
    fail("unknown action '$action' — call ?action=ping for the list", 404);
}
