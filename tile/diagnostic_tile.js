/* meridian_tile.js — DIAGNOSTIC build.
 *
 * Purpose: prove the CXone ↔ Cognigy wiring end-to-end before the real panel lands.
 * Renders every sendData push the flow emits (merStateStr / merGreet / merConvoStr /
 * merSentStr / merAskStr / merExecStr) with counts, parsed summaries, and raw payloads.
 * Sends the {action:'boot'} postback on mount (retries until a panel arrives) and offers
 * a one-click test question postback to prove tile → flow.
 *
 * The real panel build will replace this file at the same URL — the flow's tile shell
 * loads it with a cache-buster, so a deploy + Ctrl+F5 is all it takes to swap.
 */
(function () {
  'use strict';

  var KEYS = ['merStateStr', 'merGreet', 'merConvoStr', 'merSentStr', 'merAskStr', 'merExecStr'];
  var counts = {}, last = {}, bootTimer = null, gotPanel = false;

  /* ---------- ui scaffold ---------- */
  document.body.innerHTML = '';
  var css = document.createElement('style');
  css.textContent =
    "html,body{margin:0;background:#F8FAFC;font-family:'Segoe UI',system-ui,sans-serif;color:#0F172A;font-size:12.5px}" +
    '.hd{background:linear-gradient(135deg,#0F2A4A,#173D6B);color:#fff;padding:10px 14px;font-weight:600}' +
    '.hd small{display:block;font-weight:400;opacity:.8;margin-top:2px}' +
    '.bd{padding:10px 12px}' +
    '.row{background:#fff;border:1px solid #E2E8F0;border-radius:8px;padding:8px 10px;margin-bottom:8px}' +
    '.row b{font-size:12px}.cnt{float:right;color:#64748B;font-family:Consolas,monospace;font-size:11px}' +
    '.sum{margin-top:4px;color:#334155;line-height:1.45;word-break:break-word}' +
    'details{margin-top:5px}summary{cursor:pointer;color:#64748B;font-size:11px}' +
    'pre{background:#0F172A;color:#B8F5C4;font-size:10.5px;padding:8px;border-radius:6px;overflow:auto;max-height:180px;white-space:pre-wrap;word-break:break-all}' +
    '.btn{display:inline-block;background:#0F2A4A;color:#fff;border:none;border-radius:6px;padding:7px 11px;font-size:12px;font-weight:600;cursor:pointer;margin:2px 6px 2px 0}' +
    '.ok{color:#208337;font-weight:700}.wait{color:#B45309;font-weight:700}';
  document.head.appendChild(css);

  var hd = document.createElement('div');
  hd.className = 'hd';
  hd.innerHTML = 'AI Agent — diagnostic panel<small id="mer-status">Waiting for the first push from the flow…</small>';
  document.body.appendChild(hd);

  var bd = document.createElement('div');
  bd.className = 'bd';
  document.body.appendChild(bd);

  var ctl = document.createElement('div');
  ctl.className = 'row';
  ctl.innerHTML = '<b>Tile → flow tests</b><div class="sum" id="mer-post-note">SDK ' +
    (window.SDK && window.SDK.postback ? '<span class="ok">available</span>' : '<span class="wait">not available (standalone preview?)</span>') + '</div>';
  var b1 = document.createElement('button');
  b1.className = 'btn'; b1.textContent = 'Send test question (KS round-trip)';
  b1.addEventListener('click', function () {
    post({ action: 'ask', query: 'What is the return window for Summit members?', askId: 'diag-1' });
  });
  var b2 = document.createElement('button');
  b2.className = 'btn'; b2.textContent = 'Re-send boot ping';
  b2.addEventListener('click', function () { post({ action: 'boot' }); });
  ctl.appendChild(b1); ctl.appendChild(b2);
  bd.appendChild(ctl);

  var rows = {};
  KEYS.forEach(function (k) {
    var r = document.createElement('div');
    r.className = 'row';
    r.innerHTML = '<b>' + k + '</b><span class="cnt" id="mer-cnt-' + k + '">0 received</span>' +
      '<div class="sum" id="mer-sum-' + k + '">—</div>' +
      '<details><summary>raw payload</summary><pre id="mer-raw-' + k + '">(none yet)</pre></details>';
    bd.appendChild(r);
    rows[k] = r;
  });

  function status(t) { var el = document.getElementById('mer-status'); if (el) el.textContent = t; }

  function post(payload) {
    try {
      if (window.SDK && window.SDK.postback) { window.SDK.postback(payload); return true; }
    } catch (e) { /* standalone preview */ }
    return false;
  }

  /* Payloads can arrive with ONE extra escape level depending on channel version
   * (observed live 2026-07-30) — parse, and on failure unescape once and retry. */
  function jparse(val) {
    if (typeof val !== 'string') return val;
    try { return JSON.parse(val); } catch (e) { /* retry unescaped */ }
    return JSON.parse(val.replace(/\\"/g, '"').replace(/\\\\/g, '\\'));
  }

  /* ---------- summaries per key ---------- */
  function summarize(key, val) {
    try {
      if (key === 'merStateStr') {
        var p = jparse(val);
        gotPanel = true;
        var recs = (p.recommendations || []).map(function (r) { return (r.status === 'done' ? '✓ ' : r.status === 'active' ? '▶ ' : '· ') + r.label; });
        return '<b>' + ((p.profile && p.profile.name) || '?') + '</b> (' + ((p.profile && p.profile.tier) || '—') + ') · needs: ' +
          ((p.needs || []).map(function (n) { return n.label; }).join(', ') || 'none yet') +
          ' · comparison: ' + (p.comparison && p.comparison.products ? p.comparison.products.map(function (x) { return '#' + x.rank + ' ' + x.name; }).join(' / ') : 'none yet') +
          '<br>beats: ' + (recs.join(' | ') || 'none yet');
      }
      if (key === 'merSentStr') { var s = jparse(val); return s.pct + '% — ' + s.label + ' (' + (s.note || '') + ')'; }
      if (key === 'merAskStr') { var a = jparse(val); return '<b>' + a.title + '</b>: ' + a.answer + (a.sources && a.sources.length ? ' [' + a.sources.map(function (x) { return x.id; }).join(', ') + ']' : ''); }
      if (key === 'merExecStr') {
        var x = jparse(val);
        return x.narration + '<br>' + (x.executed || []).map(function (e) { return (e.ok ? '✓ ' : '✗ ') + e.summary + (e.ref ? ' · ' + e.ref : ''); }).join('<br>');
      }
      if (key === 'merConvoStr') { var c = jparse(val); return (c.transcript || []).length + ' turns · customer: ' + ((c.customer && (c.customer.nickname || c.customer.customer_id)) || '—'); }
      if (key === 'merGreet') { return String(val); }
    } catch (e) { return '<span class="wait">received but failed to parse: ' + String(e) + '</span>'; }
    return String(val).slice(0, 200);
  }

  function ingest(key, val) {
    if (val == null || val === '') return;
    counts[key] = (counts[key] || 0) + 1;
    last[key] = val;
    var c = document.getElementById('mer-cnt-' + key);
    var s = document.getElementById('mer-sum-' + key);
    var r = document.getElementById('mer-raw-' + key);
    if (c) c.textContent = counts[key] + ' received · ' + new Date().toLocaleTimeString();
    if (s) s.innerHTML = summarize(key, val);
    if (r) r.textContent = typeof val === 'string' ? val.slice(0, 4000) : JSON.stringify(val).slice(0, 4000);
    status('Wiring LIVE — flow pushes are arriving. (' + Object.keys(counts).map(function (k) { return k + ':' + counts[k]; }).join('  ') + ')');
  }

  function handle(data) {
    if (!data || typeof data !== 'object') return;
    var src = (data.metadata && typeof data.metadata === 'object') ? data.metadata : data;
    KEYS.forEach(function (k) { if (src[k] != null && src[k] !== '') ingest(k, src[k]); });
  }

  window.MER = { handle: handle, setState: function (p) { ingest('merStateStr', typeof p === 'string' ? p : JSON.stringify(p)); } };

  window.addEventListener('message', function (e) { handle(e.data); });
  (window.__merBuf || []).forEach(handle);
  window.__merBuf = [];

  /* boot ping — retries until the first panel push arrives (max 6 tries) */
  var tries = 0;
  bootTimer = setInterval(function () {
    if (gotPanel || tries >= 6) { clearInterval(bootTimer); return; }
    tries++;
    if (post({ action: 'boot' })) status('Boot ping ' + tries + ' sent — waiting for the flow…');
  }, 2500);
  post({ action: 'boot' });
})();
