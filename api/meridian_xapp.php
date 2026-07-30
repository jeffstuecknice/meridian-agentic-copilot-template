<?php
/**
 * meridian_xapp.php — Northlight customer-facing receipt page + link shortener + QR proxy.
 *
 * Modes:
 *   POST ?shorten=1  {url:"https://…"}   → {id, short:"…meridian_xapp.php?s=<id>"}
 *   GET  ?s=<id>                          → 302 to the stored URL
 *   GET  ?qr=<absolute url>               → same-origin QR PNG (CSP/attachment-validator safe)
 *   GET  ?receipt=1&name=..&items=a — REF|b — REF&total=..&order=..  → the receipt page
 */

// ---------- Mode 0: tiny link shortener (long receipt URLs break SMS/QR paths) ----------
if (isset($_REQUEST['shorten'])) {
  header('Content-Type: application/json'); header('Access-Control-Allow-Origin: *');
  $in  = json_decode(file_get_contents('php://input'), true) ?: [];
  $url = (string)($in['url'] ?? ($_REQUEST['url'] ?? ''));
  if ($url === '' || strpos($url, 'https://') !== 0) { http_response_code(400); echo json_encode(['error' => 'bad_url']); exit; }
  $dir = __DIR__ . '/_short'; if (!is_dir($dir)) @mkdir($dir, 0755, true);
  $id = substr(md5($url), 0, 8);
  @file_put_contents($dir . '/' . $id . '.txt', $url);
  $base = 'https://' . ($_SERVER['HTTP_HOST'] ?? '') . strtok((string)($_SERVER['REQUEST_URI'] ?? ''), '?');
  echo json_encode(['id' => $id, 'short' => $base . '?s=' . $id]); exit;
}
if (isset($_GET['s'])) {
  $id  = preg_replace('/[^a-f0-9]/', '', (string)$_GET['s']);
  $f   = __DIR__ . '/_short/' . $id . '.txt';
  $url = ($id !== '' && is_file($f)) ? (string)file_get_contents($f) : '';
  if ($url === '' || strpos($url, 'https://') !== 0) { http_response_code(404); header('Content-Type: text/plain'); echo 'link_expired'; exit; }
  header('Location: ' . $url, true, 302); exit;
}

// ---------- Mode 1: same-origin QR proxy (2 attempts × 4s — a slow QR service must not break the send) ----------
if (isset($_GET['qr'])) {
  $target = (string)$_GET['qr'];
  $svc = 'https://api.qrserver.com/v1/create-qr-code/?size=260x260&margin=1&qzone=1&data=' . rawurlencode($target);
  $img = false; $code = 0;
  for ($try = 0; $try < 2 && !($img !== false && $code >= 200 && $code < 300 && strlen((string)$img) > 100); $try++) {
    $ch = curl_init($svc);
    curl_setopt_array($ch, [CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 4, CURLOPT_CONNECTTIMEOUT => 3, CURLOPT_FOLLOWLOCATION => true]);
    $img = curl_exec($ch); $code = curl_getinfo($ch, CURLINFO_HTTP_CODE); curl_close($ch);
  }
  if ($img !== false && $code >= 200 && $code < 300 && strlen((string)$img) > 100) {
    header('Content-Type: image/png'); header('Cache-Control: public, max-age=3600'); header('Access-Control-Allow-Origin: *');
    echo $img; exit;
  }
  http_response_code(502); header('Content-Type: text/plain'); echo 'qr_unavailable'; exit;
}

// ---------- Mode 2: the receipt page ----------
function q($k, $d = '') { return isset($_GET[$k]) ? trim((string)$_GET[$k]) : $d; }
function e($s) { return htmlspecialchars($s, ENT_QUOTES, 'UTF-8'); }

$name  = q('name', 'there');
$order = q('order');
$total = q('total');
$items = q('items');   // "title — REF|title — REF"
$rows  = array_filter(array_map('trim', explode('|', $items)));
?><!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Northlight — Order Receipt</title>
<style>
  html,body{margin:0;background:#F1F5F9;font-family:'Segoe UI',system-ui,-apple-system,sans-serif;color:#0F172A}
  .card{max-width:430px;margin:24px auto;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 8px 28px rgba(15,23,42,.12)}
  .hd{background:linear-gradient(135deg,#0F2A4A,#173D6B);color:#fff;padding:22px 24px}
  .hd .brand{font-size:12px;letter-spacing:.14em;text-transform:uppercase;opacity:.85}
  .hd h1{margin:6px 0 2px;font-size:20px}
  .hd .ord{font-family:Consolas,monospace;font-size:12.5px;opacity:.9}
  .bd{padding:18px 24px 22px}
  .row{display:flex;align-items:flex-start;gap:10px;padding:9px 0;border-bottom:1px solid #E2E8F0}
  .row:last-child{border-bottom:none}
  .ck{flex:0 0 auto;width:20px;height:20px;border-radius:50%;background:#DCFCE7;color:#208337;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700}
  .t{font-size:14px;line-height:1.35}
  .t .ref{display:block;font-family:Consolas,monospace;font-size:11.5px;color:#64748B;margin-top:2px}
  .tot{display:flex;justify-content:space-between;margin-top:14px;padding-top:12px;border-top:2px solid #0F172A;font-weight:700;font-size:15px}
  .ft{padding:0 24px 20px;color:#94A3B8;font-size:11.5px}
</style></head>
<body>
  <div class="card">
    <div class="hd">
      <div class="brand">Northlight Electronics</div>
      <h1>Thanks, <?= e($name) ?> — you're all set.</h1>
      <?php if ($order !== ''): ?><div class="ord">Order <?= e($order) ?></div><?php endif; ?>
    </div>
    <div class="bd">
      <?php foreach ($rows as $r): $p = array_map('trim', explode(' — ', $r, 2)); ?>
      <div class="row"><div class="ck">✓</div>
        <div class="t"><?= e($p[0]) ?><?php if (isset($p[1])): ?><span class="ref"><?= e($p[1]) ?></span><?php endif; ?></div>
      </div>
      <?php endforeach; ?>
      <?php if ($total !== ''): ?><div class="tot"><span>Total charged</span><span><?= e($total) ?></span></div><?php endif; ?>
    </div>
    <div class="ft">Sent <?= date('M j · g:i A') ?> · Northlight Electronics · Northlight Circle member receipt</div>
  </div>
</body></html>
