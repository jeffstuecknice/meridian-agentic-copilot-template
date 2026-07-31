<?php
/**
 * meridian_image.php — "LLMs decide; code executes," applied to imagery.
 *
 * The Cognigy composer WRITES a personalized image brief from the customer's
 * stated needs (comparison.heroPrompt); this endpoint executes it: one Gemini
 * image-generation call, cached by prompt hash so rehydrates, re-renders and
 * demo re-runs are instant and free.
 *
 * Call: POST JSON {prompt} (or GET ?prompt= for curl debugging)
 *       → {ok:true, url, cached, ms, model}  |  {ok:false, error, detail?}
 * Key:  gen_key.txt beside this file — uploaded by tools/deploy_api.py from the
 *       local secrets folder, NEVER in the repo.
 * Rule: a real generated image or a visible error — this endpoint never serves
 *       placeholder art (REAL DATA OR ERROR).
 */

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { http_response_code(204); exit; }

$MODEL = 'gemini-2.5-flash-image';

function out($arr, $code = 200) {
  http_response_code($code);
  echo json_encode($arr, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
  exit;
}

/* ---- merge GET + JSON body (same convention as meridian_api.php) ----
   json_decode rejects invalid UTF-8 outright, so a Latin-1 byte (curl from a
   Windows console) would silently read as "missing prompt" — salvage once,
   then fail HONESTLY if the body still isn't JSON. */
$body = [];
$raw = file_get_contents('php://input');
if ($raw) {
  $j = json_decode($raw, true);
  if (!is_array($j)) $j = json_decode(mb_convert_encoding($raw, 'UTF-8', 'UTF-8, ISO-8859-1'), true);
  if (is_array($j)) $body = $j;
  elseif (empty($_GET) && empty($_POST)) {
    out(['ok' => false, 'error' => 'request body was not valid JSON (check UTF-8 encoding)', 'detail' => substr($raw, 0, 200)], 400);
  }
}
$P = array_merge($_GET, $_POST, $body);
$prompt = isset($P['prompt']) ? trim((string)$P['prompt']) : '';

if ($prompt === '') out(['ok' => false, 'error' => 'missing prompt'], 400);
if (strlen($prompt) > 900) out(['ok' => false, 'error' => 'prompt too long (' . strlen($prompt) . ' chars, max 900)'], 400);

$genDir = __DIR__ . '/gen';
if (!is_dir($genDir) && !@mkdir($genDir, 0755, true)) out(['ok' => false, 'error' => 'cannot create gen/ directory on server'], 500);

/* cache key = model + prompt, so a model upgrade regenerates cleanly */
$hash = md5($MODEL . '|' . $prompt);
$file = $genDir . '/' . $hash . '.png';
$scheme = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off') ? 'https' : 'http';
$url = $scheme . '://' . $_SERVER['HTTP_HOST'] . rtrim(str_replace('\\', '/', dirname($_SERVER['SCRIPT_NAME'])), '/') . '/gen/' . $hash . '.png';

if (is_file($file) && filesize($file) > 0) {
  out(['ok' => true, 'url' => $url, 'cached' => true, 'ms' => 0, 'model' => $MODEL]);
}

$keyFile = __DIR__ . '/gen_key.txt';
if (!is_file($keyFile)) {
  out(['ok' => false, 'error' => 'gen_key.txt missing on server — run tools/deploy_api.py (it uploads the key from the local secrets folder)'], 500);
}
$key = trim(file_get_contents($keyFile));
if ($key === '') out(['ok' => false, 'error' => 'gen_key.txt is empty on server'], 500);

$req = json_encode([
  'contents' => [['parts' => [['text' => $prompt]]]],
  'generationConfig' => ['responseModalities' => ['IMAGE']],
]);

$t0 = microtime(true);
$ch = curl_init('https://generativelanguage.googleapis.com/v1beta/models/' . $MODEL . ':generateContent');
curl_setopt_array($ch, [
  CURLOPT_POST => true,
  CURLOPT_POSTFIELDS => $req,
  CURLOPT_HTTPHEADER => ['Content-Type: application/json', 'x-goog-api-key: ' . $key],
  CURLOPT_RETURNTRANSFER => true,
  CURLOPT_TIMEOUT => 55,
]);
$resp = curl_exec($ch);
$http = (int)curl_getinfo($ch, CURLINFO_RESPONSE_CODE);
$cerr = curl_error($ch);
curl_close($ch);
$ms = (int)round((microtime(true) - $t0) * 1000);

if ($resp === false) out(['ok' => false, 'error' => 'transport: ' . $cerr, 'ms' => $ms], 502);
$d = json_decode($resp, true);
if ($http !== 200 || !is_array($d)) {
  out(['ok' => false, 'error' => 'provider HTTP ' . $http, 'detail' => substr((string)$resp, 0, 400), 'ms' => $ms], 502);
}

/* the image arrives as an inline_data part; a blocked/refused prompt has none */
$png = null;
$parts = isset($d['candidates'][0]['content']['parts']) ? $d['candidates'][0]['content']['parts'] : [];
foreach ($parts as $part) {
  if (isset($part['inlineData']['data'])) { $png = base64_decode($part['inlineData']['data']); break; }
  if (isset($part['inline_data']['data'])) { $png = base64_decode($part['inline_data']['data']); break; }
}
if (!$png) {
  $why = isset($d['candidates'][0]['finishReason']) ? (' finishReason=' . $d['candidates'][0]['finishReason']) : '';
  out(['ok' => false, 'error' => 'provider returned no image part' . $why, 'detail' => substr((string)$resp, 0, 400), 'ms' => $ms], 502);
}
if (file_put_contents($file, $png) === false) out(['ok' => false, 'error' => 'could not write image file on server'], 500);

out(['ok' => true, 'url' => $url, 'cached' => false, 'ms' => $ms, 'model' => $MODEL, 'bytes' => strlen($png)]);
