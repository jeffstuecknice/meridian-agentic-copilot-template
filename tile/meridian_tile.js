/* meridian_tile.js — the Meridian copilot panel (Northlight Electronics demo).
 *
 * One self-contained IIFE: injects its own CSS, builds its own DOM, no external
 * resources of any kind. Loaded by the flow's tile shell (which buffers early
 * messages in window.__merBuf); also runs standalone under tile/harness.html.
 *
 * Contract (docs/ARCHITECTURE.md §4/§4a + package/build_meridian.py):
 *   inbound  — merStateStr / merExecStr / merAskStr / merSentStr / merConvoStr / merGreet
 *              (payload at e.data.metadata.<key> OR e.data.<key>; values are JSON
 *              strings that may carry ONE extra escape level — see jparse)
 *   outbound — SDK.postback({action:'boot'|'approve'|'ask'|'command', …})
 *
 * SECTION MAP
 *   §1  design tokens + stylesheet
 *   §2  icons (inline SVG)
 *   §3  utilities (esc, jparse, copy, postback)
 *   §4  state (panel + local overlays)
 *   §5  dom scaffold (shell, scroll body, footer, greet toast)
 *   §6  render — profile / sentiment / context / needs / comparison
 *   §7  render — playbook beats
 *   §8  render — knowledge cards, draft message, skeleton + thinking card
 *   §9  render orchestrator (idempotent, no-flicker)
 *   §10 interactions (one delegated click handler)
 *   §11 heard-gating + confirm gates (transcript matching)
 *   §12 execution (approve → in-flight → real refs / visible error)
 *   §13 inbound messages
 *   §14 boot (window.MER, buffer drain, boot ping)
 */
(function () {
  'use strict';

  /* ======================================================================
     §1  DESIGN TOKENS + STYLESHEET
     Northlight navy is the brand; AI purple marks everything the AI Agent
     suggested or executed; live-agent blue marks the human's own moves;
     green is reserved for real, confirmed completion.
     ====================================================================== */
  var css = document.createElement('style');
  css.textContent = `
:root{
  --navy:#0F2A4A; --navy2:#173D6B; --navy-grad:linear-gradient(135deg,#0F2A4A 0%,#173D6B 100%);
  --ai:#8630E8; --ai-deep:#6B21C8; --ai-bg:#F7F1FE; --ai-bg2:#FBF8FF; --ai-bd:#DCC5F6;
  --blue:#126BCE; --blue-bg:#EDF4FC; --blue-bd:#BFDAF5;
  --ok:#208337; --ok-bg:#EDF8F0; --ok-bd:#BBE2C6;
  --warn:#B45309; --warn-bg:#FFF6E6; --warn-bd:#F0D492;
  --err:#C2312B; --err-bg:#FDEDEC; --err-bd:#F0B9B5;
  --ink:#16233B; --ink-2:#42526B; --ink-3:#71809A;
  --bd:#E3E9F1; --bd-2:#EDF1F6; --page:#F4F7FA; --card:#FFFFFF;
  --mono:Consolas,'Cascadia Mono',ui-monospace,monospace;
  --shadow:0 4px 18px rgba(15,42,74,.08);
}
*{box-sizing:border-box}
html,body{margin:0;height:100%}
body{font-family:'Geist','Inter Tight','Segoe UI',system-ui,sans-serif;font-size:13px;
  color:var(--ink);background:var(--page);-webkit-font-smoothing:antialiased}
.mer-app{display:flex;flex-direction:column;height:100%;background:var(--page);overflow:hidden;position:relative}
.mer-scroll{flex:1 1 auto;overflow-y:auto;padding:10px 12px 14px;display:flex;flex-direction:column;gap:10px}
.mer-scroll::-webkit-scrollbar{width:8px}
.mer-scroll::-webkit-scrollbar-thumb{background:#CBD6E2;border-radius:99px}

/* cards animate only on FIRST appearance (seen ledger adds .seen on re-renders) */
.mcard{background:var(--card);border:1px solid var(--bd);border-radius:12px;padding:13px 14px;
  box-shadow:var(--shadow);flex-shrink:0;animation:cardIn .4s ease-out both}
.mcard.seen{animation:none}
@keyframes cardIn{0%{opacity:0;transform:translateY(12px)}100%{opacity:1;transform:none}}
.sec{font-size:10px;font-weight:700;letter-spacing:.07em;text-transform:uppercase;color:var(--navy)}
.sec.ai{color:var(--ai-deep)}
.sec-hd{display:flex;align-items:center;gap:6px;margin-bottom:9px}
.sec-hd svg{width:13px;height:13px;flex:0 0 auto}

/* ---------- profile header (navy brand panel) ---------- */
.mcard.hd{padding:0;overflow:hidden;background:var(--navy-grad);border-color:#123055;color:#fff}
.hd-top{display:flex;align-items:flex-start;gap:11px;padding:14px 14px 4px}
.hd-avatar{flex:0 0 40px;height:40px;border-radius:50%;background:rgba(255,255,255,.14);
  border:1px solid rgba(255,255,255,.25);display:flex;align-items:center;justify-content:center;
  font-weight:700;font-size:14px;letter-spacing:.5px}
.hd-id{flex:1;min-width:0}
.hd-name{font-size:15px;font-weight:700;line-height:1.2}
.hd-name .nick{font-weight:400;font-size:11.5px;opacity:.75;margin-left:5px}
.hd-meta{font-size:11px;opacity:.78;margin-top:2px}
.hd-sub{font-size:10.5px;opacity:.62;margin-top:1px}
.hd-right{text-align:right;flex:0 0 auto}
.hd-right .lbl{font-size:9px;letter-spacing:.06em;text-transform:uppercase;opacity:.65}
.hd-right .val{font-size:15px;font-weight:700;margin-top:1px}
.hd-stats{display:flex;gap:8px;padding:10px 14px 0}
.hd-stat{flex:1;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.13);
  border-radius:8px;padding:7px 9px}
.hd-stat .k{font-size:9px;letter-spacing:.05em;text-transform:uppercase;opacity:.65}
.hd-stat .v{font-size:14px;font-weight:700;margin-top:1px}
.hd-badges{display:flex;flex-wrap:wrap;gap:6px;padding:10px 14px 12px}
.pill{display:inline-flex;align-items:center;gap:4px;border:1px solid;border-radius:999px;
  padding:2.5px 9px;font-size:10.5px;font-weight:600}
.pill.plat{background:#FFF3D6;color:#8A6100;border-color:#F0D492}
.pill.blue{background:var(--blue-bg);color:#0B4E9B;border-color:var(--blue-bd)}
.pill.warn{background:var(--err-bg);color:var(--err);border-color:var(--err-bd)}
.pill.good{background:var(--ok-bg);color:var(--ok);border-color:var(--ok-bd)}

/* ---------- live sentiment (bottom strip of the header card) ---------- */
.hd-sent{padding:10px 14px 13px;border-top:1px solid rgba(255,255,255,.12)}
.hd-sent .row1{display:flex;align-items:center;gap:6px;font-size:10px;letter-spacing:.06em;
  text-transform:uppercase;opacity:.8}
.sent-live{display:inline-flex;align-items:center;gap:4px;margin-left:auto;font-size:8.5px;
  letter-spacing:.6px;text-transform:uppercase;color:rgba(255,255,255,.55)}
.sent-live i{width:6px;height:6px;border-radius:50%;background:#4ADE80;animation:livePulse 1.6s ease-in-out infinite}
@keyframes livePulse{0%,100%{opacity:.35;transform:scale(.85)}50%{opacity:1;transform:scale(1)}}
.sent-bar{margin-top:7px;height:7px;border-radius:99px;background:rgba(255,255,255,.12);overflow:hidden}
.sent-bar i{display:block;height:100%;width:0;border-radius:99px;
  transition:width .8s ease,background-color .8s ease}
.sent-bar i.pulse{animation:sentPulse .9s ease}
@keyframes sentPulse{0%{filter:brightness(1.7)}100%{filter:brightness(1)}}
.sent-sub{display:flex;justify-content:space-between;margin-top:5px;font-size:10.5px}
.sent-sub .lb{font-weight:700;transition:color .8s ease}
.sent-sub .pc{opacity:.55}
.sent-note{font-size:10px;opacity:.55;margin-top:4px;line-height:1.4}

/* ---------- context card ---------- */
.ctx-tx{font-size:12.5px;line-height:1.55;color:var(--ink-2)}
.ctx-att{margin-top:9px;display:flex;flex-direction:column;gap:5px}
.att-row{display:flex;align-items:flex-start;gap:7px;font-size:11.5px;color:var(--ink-2)}
.att-row svg{width:13px;height:13px;flex:0 0 auto;color:var(--ok);margin-top:1px}
.ask-chips{margin-top:9px;display:flex;flex-wrap:wrap;gap:6px}
.ask-chip{display:inline-flex;align-items:center;gap:5px;border-radius:999px;border:1px solid var(--bd);
  background:var(--page);padding:3px 10px;font-size:10.5px;font-weight:600;color:var(--ink-2)}
.ask-chip.res{border-color:var(--ok-bd);background:var(--ok-bg);color:var(--ok)}
.ask-chip.res .a{text-decoration:line-through;opacity:.72}
.ask-chip .r{font-weight:500}

/* ---------- needs chips (captured intelligence → AI purple) ---------- */
.needs{display:flex;flex-wrap:wrap;gap:7px}
.need{border:1px solid var(--ai-bd);background:var(--ai-bg2);border-radius:10px;padding:7px 10px;
  max-width:100%;min-width:0}
.need .lb{display:flex;align-items:center;gap:5px;font-size:11.5px;font-weight:700;color:var(--ai-deep)}
.need .lb svg{width:11px;height:11px}
.need .qt{font-size:10px;font-style:italic;color:var(--ink-3);margin-top:2px;line-height:1.35}
.need.hi{background:var(--ai-bg);border-color:#C9A6F0;box-shadow:0 1px 6px rgba(134,48,232,.10)}
.need.hi .lb{color:var(--ai)}

/* ---------- comparison showpiece ---------- */
.cmp-intro{font-size:12px;color:var(--ink-2);margin-bottom:10px;line-height:1.45}
.cmp-grid{display:grid;grid-template-columns:1fr 1fr;gap:9px}
@media (max-width:480px){.cmp-grid{grid-template-columns:1fr}}
.prod{border:1px solid var(--bd);border-radius:11px;background:#fff;overflow:hidden;
  display:flex;flex-direction:column;min-width:0}
.prod.lead{border-color:#C9A6F0;box-shadow:0 5px 20px rgba(134,48,232,.13)}
.prod-tag{font-size:9.5px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;
  text-align:center;padding:5px 8px;background:var(--page);color:var(--ink-3)}
.prod.lead .prod-tag{background:linear-gradient(90deg,var(--ai),var(--blue));color:#fff}
.prod-bd{padding:10px 11px 11px;display:flex;flex-direction:column;flex:1}
.prod-nm{display:flex;align-items:baseline;gap:6px;flex-wrap:wrap}
.prod-nm .n{font-size:14px;font-weight:700;color:var(--ink)}
.prod-nm .p{margin-left:auto;font-size:13.5px;font-weight:700;color:var(--navy)}
.prod-hl{font-size:11px;color:var(--ink-2);line-height:1.45;margin-top:5px}
.fits{margin-top:9px;display:flex;flex-direction:column;gap:6px}
.fit{display:flex;align-items:flex-start;gap:6px;font-size:11px;line-height:1.35}
.fit .g{flex:0 0 15px;height:15px;border-radius:50%;display:flex;align-items:center;justify-content:center;
  font-size:9.5px;font-weight:800;margin-top:1px}
.fit.wins .g{background:var(--ok-bg);color:var(--ok);border:1px solid var(--ok-bd)}
.fit.close .g{background:var(--warn-bg);color:var(--warn);border:1px solid var(--warn-bd)}
.fit.trails .g{background:var(--err-bg);color:var(--err);border:1px solid var(--err-bd)}
.fit .nd{font-weight:700;color:var(--ink)}
.fit .why{color:var(--ink-3)}
.honest{margin-top:auto;padding-top:9px}
.honest-in{border-top:1px dashed var(--bd);padding-top:8px}
.honest .hl{font-size:9px;font-weight:700;letter-spacing:.07em;text-transform:uppercase;color:var(--warn)}
.honest .ht{font-size:10.5px;font-style:italic;color:var(--ink-2);line-height:1.45;margin-top:3px}
.prod-img{margin:0 0 8px;border-radius:8px;overflow:hidden;background:var(--page)}
.prod-img img{display:block;width:100%;height:84px;object-fit:cover}
.prod.prov{border-style:dashed}
.prod.prov .prod-tag{background:var(--ai-bg);color:var(--ai-deep)}

/* ---------- live brain-run stage strip (real pipeline boundaries, no fake spinners) ---------- */
.stgcard{padding:9px 11px 8px}
.stg-eyebrow{font-size:9px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;
  color:var(--ai-deep);display:flex;align-items:center;gap:5px;margin-bottom:6px}
.stg-eyebrow svg{width:10px;height:10px}
.stg{display:flex;align-items:center;gap:7px;font-size:11px;line-height:1.4;padding:2.5px 0}
.stg.done{color:var(--ink-3)}
.stg.cur{color:var(--ink);font-weight:600}
.stg .sdot{flex:0 0 14px;width:14px;height:14px;border-radius:50%;display:flex;align-items:center;justify-content:center}
.stg.done .sdot{background:var(--ok-bg);border:1px solid var(--ok-bd);color:var(--ok)}
.stg.done .sdot svg{width:8px;height:8px}
.stg.cur .sdot{border:2px solid var(--ai);border-top-color:transparent;animation:mer-spin .8s linear infinite}
@keyframes mer-spin{to{transform:rotate(360deg)}}

/* ---------- generative hero — the AI-drawn "your day with this laptop" scene ---------- */
.hero{margin-top:10px;border:1px solid var(--ai-bd);border-radius:12px;overflow:hidden;background:var(--ai-bg2)}
.hero-shimmer{display:flex;gap:8px;align-items:center;padding:20px 14px;font-size:11.5px;color:var(--ai-deep);
  background:linear-gradient(100deg,var(--ai-bg) 40%,#EFE3FC 50%,var(--ai-bg) 60%);
  background-size:200% 100%;animation:mer-shim 1.5s linear infinite}
.hero-shimmer svg{width:13px;height:13px;flex:0 0 13px}
@keyframes mer-shim{to{background-position:-200% 0}}
.hero-imgwrap{max-height:200px;overflow:hidden;background:var(--ai-bg)}
.hero-img{display:block;width:100%;object-fit:cover;opacity:0;transform:scale(1.02);
  transition:opacity .9s ease,transform 1.4s ease}
.hero-img.in{opacity:1;transform:none}
.hero-cap{display:flex;justify-content:space-between;align-items:center;gap:8px;padding:7px 11px;
  font-size:10.5px;color:var(--ai-deep)}
.hero-cap .hc-l{display:flex;align-items:center;gap:5px;min-width:0}
.hero-cap svg{width:11px;height:11px;flex:0 0 11px}
.hero-why{border:none;background:none;color:var(--ai);font-size:10.5px;cursor:pointer;
  text-decoration:underline;padding:0;white-space:nowrap}
.hero-brief{padding:0 12px 10px;font-size:11px;font-style:italic;color:var(--ink-2);line-height:1.5}
.hero-err{padding:12px 14px}
.hero-err .he-t{font-size:11px;font-weight:700;letter-spacing:.04em;color:var(--err)}
.hero-err .he-d{font-size:11px;color:var(--ink-2);margin:4px 0 9px;line-height:1.45;word-break:break-word;
  font-family:var(--mono)}
.hero-retry{border:1px solid var(--err-bd);background:#fff;color:var(--err);border-radius:8px;
  padding:5px 12px;font-size:11px;font-weight:600;cursor:pointer}

/* ---------- playbook beats ---------- */
.pb-intro{font-size:12px;color:var(--ink-2);margin-bottom:9px;line-height:1.45}
.beat{border:1px solid var(--bd);border-radius:10px;background:#fff;padding:10px 11px;margin-bottom:8px;
  transition:border-color .2s,background .2s}
.beat:last-child{margin-bottom:0}
.beat.active{border-color:var(--blue);background:var(--blue-bg);box-shadow:0 0 0 2px rgba(18,107,206,.12)}
.beat.pending{opacity:.55}
.beat.done{border-color:var(--ai-bd);background:var(--ai-bg2)}
.beat.declined{border-color:var(--warn-bd);background:var(--warn-bg)}
.beat.failed{border-color:var(--err-bd)}
.beat-hd{display:flex;align-items:center;gap:8px}
.dot{flex:0 0 16px;height:16px;border-radius:50%;border:1.5px solid #C3CEDC;background:#fff;
  display:flex;align-items:center;justify-content:center}
.dot svg{width:9px;height:9px;color:#fff}
.beat.active .dot{border-color:var(--blue);animation:dotPulse 1.6s ease-in-out infinite}
@keyframes dotPulse{0%,100%{box-shadow:0 0 0 0 rgba(18,107,206,.3)}50%{box-shadow:0 0 0 5px rgba(18,107,206,0)}}
.dot.ck{background:var(--ai);border-color:var(--ai)}
.beat.declined .dot.ck{background:var(--warn);border-color:var(--warn)}
.beat-lab{font-size:12.5px;font-weight:700;color:var(--ink);min-width:0}
.beat.done .beat-lab{text-decoration:line-through;color:var(--ink-3);font-weight:600}
.beat-kind{margin-left:auto;flex:0 0 auto;font-size:8.5px;font-weight:700;letter-spacing:.6px;
  text-transform:uppercase;border-radius:999px;padding:2px 7px}
.beat-kind.talk{background:var(--blue-bg);color:#0B4E9B;border:1px solid var(--blue-bd)}
.beat-kind.action{background:var(--ai-bg);color:var(--ai-deep);border:1px solid var(--ai-bd)}
.beat-kind.done-chip{background:var(--ai-bg);color:var(--ai-deep);border:1px solid var(--ai-bd)}
.beat-detail{font-size:10.5px;color:var(--ink-3);margin:6px 0 0 24px;line-height:1.4}

/* say card — the line the agent relays (AI suggestion → purple) */
.say{margin:8px 0 0 24px;border:1px solid var(--ai-bd);border-radius:9px;background:var(--ai-bg2);padding:8px 10px}
.say .lab{display:flex;align-items:center;gap:5px;font-size:9.5px;font-weight:700;letter-spacing:.05em;
  text-transform:uppercase;color:var(--ai-deep);margin-bottom:4px}
.say .lab svg{width:11px;height:11px}
.say .tx{font-size:12.5px;line-height:1.5;color:var(--ink)}
.say.good{border-color:var(--ok-bd);background:var(--ok-bg)}
.say.good .lab{color:var(--ok)}
.say-foot{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-top:7px}
.copy-btn{display:inline-flex;align-items:center;gap:5px;height:26px;padding:0 11px;border:none;
  border-radius:7px;background:var(--ai);color:#fff;font-size:11px;font-weight:600;font-family:inherit;
  cursor:pointer;transition:transform .12s cubic-bezier(.34,1.56,.64,1),background .15s}
.copy-btn svg{width:11px;height:11px}
.copy-btn:active{transform:scale(.95)}
.copy-btn.did{background:linear-gradient(120deg,var(--ai),var(--blue))}
.copy-btn.ghost{background:#fff;color:var(--ai-deep);border:1px solid var(--ai-bd)}
.listen-hint{display:inline-flex;align-items:center;gap:5px;font-size:10px;color:var(--ink-3)}
.listen-hint svg{width:11px;height:11px;color:var(--blue)}
.ldots i{display:inline-block;width:3px;height:3px;border-radius:50%;background:var(--ink-3);
  margin-left:2px;animation:blink 1.2s infinite}
.ldots i:nth-child(2){animation-delay:.2s}.ldots i:nth-child(3){animation-delay:.4s}
@keyframes blink{0%,100%{opacity:.25}50%{opacity:1}}

/* HEARD moment — green banner where the listening hint sat, then a slow fold */
.heard{display:flex;align-items:center;gap:7px;margin-top:8px;font-size:11.5px;font-weight:800;
  color:var(--ok);background:var(--ok-bg);border:1.5px solid var(--ok-bd);border-radius:9px;
  padding:7px 11px;animation:heardPop .38s cubic-bezier(.2,1.4,.4,1) both}
.heard svg{width:13px;height:13px}
@keyframes heardPop{0%{transform:scale(.86);opacity:0}100%{transform:scale(1);opacity:1}}
.beat.folding{overflow:hidden;animation:foldClose 1.15s cubic-bezier(.4,0,.2,1) both}
@keyframes foldClose{from{max-height:420px}to{max-height:44px}}

/* awaiting the customer (confirm-gated) */
.await{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin:8px 0 0 24px}
.await-chip{display:inline-flex;align-items:center;gap:5px;border:1px solid var(--warn-bd);
  background:var(--warn-bg);color:var(--warn);border-radius:999px;padding:3px 10px;
  font-size:10px;font-weight:700}
.await-chip i{width:5px;height:5px;border-radius:50%;background:var(--warn);animation:livePulse 1.4s infinite}
.mini-btn{height:24px;padding:0 10px;border-radius:6px;font-size:10.5px;font-weight:700;font-family:inherit;
  cursor:pointer;border:1px solid var(--ok-bd);background:#fff;color:var(--ok)}
.mini-btn.no{border-color:var(--bd);color:var(--ink-3)}
.declined-note{margin:8px 0 0 24px;font-size:11px;color:var(--warn);background:var(--warn-bg);
  border:1px solid var(--warn-bd);border-radius:8px;padding:6px 9px}
.noexec{margin:8px 0 0 24px;font-size:11px;color:var(--ink-3);border:1px dashed var(--bd);
  border-radius:8px;padding:6px 9px;line-height:1.4}

/* policy basis — the verbatim citation card (grounded, serious) */
.pbasis{display:flex;gap:9px;margin:9px 0 0 24px;border:1px solid #D4DEEA;border-left:3px solid var(--navy);
  border-radius:8px;background:#F8FAFD;padding:9px 11px}
.pbasis svg{width:14px;height:14px;flex:0 0 auto;color:var(--navy);margin-top:1px}
.pb-hd{display:flex;align-items:center;gap:7px}
.pb-lab{font-size:9px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:var(--navy)}
.pb-rule{font-family:var(--mono);font-size:9.5px;font-weight:700;color:var(--navy);
  background:#E8EFF7;border-radius:5px;padding:1px 6px}
.pb-q{font-size:11.5px;font-style:italic;line-height:1.5;color:var(--ink-2);margin-top:4px}
.pb-src{font-size:9.5px;color:var(--ink-3);margin-top:4px}

/* approve CTA (the AI executes → purple) + in-flight ribbon */
.approve{width:calc(100% - 24px);margin:9px 0 0 24px;border:none;border-radius:9px;padding:9px 12px;
  font-size:12px;font-weight:700;font-family:inherit;cursor:pointer;background:var(--ai);color:#fff;
  display:flex;align-items:center;justify-content:center;gap:7px;
  box-shadow:0 4px 14px rgba(134,48,232,.28);
  transition:transform .12s cubic-bezier(.34,1.56,.64,1),background .15s}
.approve svg{width:13px;height:13px}
.approve:active{transform:scale(.97)}
.approve:hover{background:var(--ai-deep)}
.run-strip{position:relative;overflow:hidden;width:calc(100% - 24px);margin:9px 0 0 24px;border-radius:9px;
  padding:9px 12px;background:var(--navy);color:#fff;display:flex;align-items:center;gap:8px;
  font-size:11.5px;font-weight:700}
.run-strip::after{content:"";position:absolute;top:0;bottom:0;width:45%;left:-45%;
  background:linear-gradient(100deg,transparent,rgba(91,196,232,.32),transparent);animation:sweep 1.6s ease-in-out infinite}
@keyframes sweep{to{left:130%}}
.run-strip .sp{flex:0 0 13px;width:13px;height:13px;border:2px solid rgba(255,255,255,.28);
  border-top-color:#5BC4E8;border-radius:50%;animation:spin .7s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.run-tx{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;
  opacity:1;transition:opacity .3s ease}
.run-tx.out{opacity:0}

/* executed refs — real confirmations only (green + monospace) */
.execd{margin:9px 0 0 24px;display:flex;flex-direction:column;gap:6px}
.exec-row{display:flex;align-items:center;gap:8px;font-size:11.5px;color:var(--ink-2);
  opacity:0;transform:translateY(6px);animation:refIn .38s ease-out forwards}
.execd.settled .exec-row{animation:none;opacity:1;transform:none}
@keyframes refIn{to{opacity:1;transform:none}}
.exec-row svg{width:13px;height:13px;flex:0 0 auto;color:var(--ok)}
.exec-row.bad svg{color:var(--err)}
.ref{font-family:var(--mono);font-size:10.5px;font-weight:700;color:var(--ok);
  background:var(--ok-bg);border:1px solid var(--ok-bd);border-radius:6px;padding:1px 7px;flex:0 0 auto}
.rcpt{display:flex;align-items:center;gap:7px;margin:8px 0 0 24px;border:1px solid var(--ok-bd);
  background:var(--ok-bg);border-radius:8px;padding:7px 10px;min-width:0}
.rcpt svg{width:13px;height:13px;flex:0 0 auto;color:var(--ok)}
.rcpt a{font-family:var(--mono);font-size:10.5px;font-weight:700;color:var(--ok);
  text-decoration:underline;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;min-width:0}
.rcpt .plain{font-family:var(--mono);font-size:10.5px;font-weight:700;color:var(--ok);
  overflow:hidden;text-overflow:ellipsis;white-space:nowrap;min-width:0}
.rcpt .copy-btn{margin-left:auto;flex:0 0 auto;height:22px;padding:0 8px;font-size:10px;
  background:#fff;color:var(--ok);border:1px solid var(--ok-bd)}

/* execution error — REAL DATA OR ERROR: the narration verbatim, never a fake success */
.exec-err{margin:9px 0 0 24px;border:1.5px solid var(--err-bd);background:var(--err-bg);
  border-radius:9px;padding:9px 11px}
.exec-err .t{display:flex;align-items:center;gap:6px;font-size:10px;font-weight:800;
  letter-spacing:.06em;text-transform:uppercase;color:var(--err)}
.exec-err .t svg{width:12px;height:12px}
.exec-err .m{font-size:11.5px;color:#8C2320;line-height:1.45;margin-top:4px;word-break:break-word}
.retry-btn{margin-top:7px;height:24px;padding:0 11px;border-radius:6px;border:1px solid var(--err-bd);
  background:#fff;color:var(--err);font-size:10.5px;font-weight:700;font-family:inherit;cursor:pointer}

/* ---------- draft message ---------- */
.draft-tx{font-size:12.5px;line-height:1.55;color:var(--ink-2);border:1px dashed var(--bd);
  border-radius:9px;background:var(--page);padding:9px 11px}
.draft-foot{margin-top:8px}

/* ---------- knowledge cards ---------- */
.kb-card{border-top:3px solid var(--ai)}
.kb-q{font-size:11px;color:var(--ink-3);font-style:italic;margin-bottom:6px}
.kb-a{font-size:12.5px;line-height:1.55;color:var(--ink-2)}
.kb-load{display:flex;align-items:center;gap:8px;font-size:11.5px;color:var(--ink-3)}
.kb-load .sp{width:13px;height:13px;border:2px solid var(--ai-bd);border-top-color:var(--ai);
  border-radius:50%;animation:spin .7s linear infinite;flex:0 0 auto}
.kb-esc{display:flex;align-items:flex-start;gap:7px;margin-top:8px;font-size:11px;color:var(--warn);
  background:var(--warn-bg);border:1px solid var(--warn-bd);border-radius:8px;padding:7px 10px;line-height:1.4}
.kb-esc svg{width:13px;height:13px;flex:0 0 auto;margin-top:1px}
.kb-srcs{display:flex;align-items:center;flex-wrap:wrap;gap:5px;margin-top:8px}
.kb-srcl{font-size:9px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--ink-3)}
.kb-src{font-family:var(--mono);font-size:9.5px;font-weight:700;color:var(--ai-deep);
  background:var(--ai-bg);border:1px solid var(--ai-bd);border-radius:5px;padding:1px 6px}
.kb-addrow{margin-top:8px;display:flex;justify-content:flex-end}
.kb-add{display:inline-flex;align-items:center;gap:5px;height:25px;padding:0 10px;border-radius:7px;
  border:1px solid var(--ai-bd);background:#fff;color:var(--ai-deep);font-size:10.5px;font-weight:700;
  font-family:inherit;cursor:pointer}
.kb-add svg{width:11px;height:11px}
.kb-add[disabled]{opacity:.55;cursor:default}
.cmd-card{border-top:3px solid var(--navy)}
.cmd-q{font-size:11.5px;color:var(--ink-2);font-style:italic}

/* ---------- skeleton + thinking choreography ---------- */
.boot{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px;
  padding:44px 24px 20px;color:var(--ink-3);text-align:center}
.boot svg{width:32px;height:32px;color:var(--ai);animation:earPulse 1.6s ease-in-out infinite}
@keyframes earPulse{0%,100%{opacity:.45;transform:scale(.95)}50%{opacity:1;transform:scale(1)}}
.boot .t{font-size:12.5px;font-weight:700;color:var(--ink-2)}
.skel{height:9px;border-radius:5px;background:linear-gradient(90deg,#E4EAF1 25%,#F2F5F9 50%,#E4EAF1 75%);
  background-size:200% 100%;animation:shimmer 1.5s ease-in-out infinite}
@keyframes shimmer{0%{background-position:200% 0}100%{background-position:-200% 0}}
.skel-card{display:flex;flex-direction:column;gap:8px}
.think{display:flex;align-items:flex-start;gap:10px}
.think .sp{flex:0 0 14px;width:14px;height:14px;border:2px solid var(--ai-bd);border-top-color:var(--ai);
  border-radius:50%;animation:spin .7s linear infinite;margin-top:2px}
.think-t{display:flex;align-items:center;gap:5px;font-size:12.5px;font-weight:700;color:var(--ai-deep)}
.think-t svg{width:12px;height:12px}
.think-s{font-size:11.5px;color:var(--ink-3);line-height:1.45;margin-top:3px;transition:opacity .32s ease}

/* ---------- footer (ask / command) ---------- */
.mer-foot{flex:0 0 auto;display:flex;gap:7px;padding:9px 12px;background:#fff;border-top:1px solid var(--bd)}
.mer-foot input{flex:1;min-width:0;height:32px;border:1px solid var(--bd);border-radius:8px;
  padding:0 11px;font-size:12px;font-family:inherit;color:var(--ink);outline:none;background:var(--page)}
.mer-foot input:focus{border-color:var(--ai-bd);background:#fff}
.foot-btn{height:32px;padding:0 12px;border-radius:8px;border:none;font-size:11.5px;font-weight:700;
  font-family:inherit;cursor:pointer;display:inline-flex;align-items:center;gap:5px;flex:0 0 auto;
  transition:transform .12s cubic-bezier(.34,1.56,.64,1)}
.foot-btn:active{transform:scale(.95)}
.foot-btn svg{width:12px;height:12px}
.foot-btn.ask{background:var(--ai);color:#fff}
.foot-btn.cmd{background:var(--navy);color:#fff}

/* ---------- greet toast ---------- */
.greet{position:absolute;left:10px;right:10px;top:10px;z-index:30;display:flex;gap:9px;
  background:linear-gradient(120deg,#2A0F55,#4A1A8F);color:#fff;border-radius:11px;
  padding:11px 12px;box-shadow:0 10px 30px rgba(42,15,85,.35);
  animation:greetIn .45s cubic-bezier(.2,1.2,.4,1) both}
@keyframes greetIn{0%{opacity:0;transform:translateY(-14px)}100%{opacity:1;transform:none}}
.greet.bye{transition:opacity .3s ease,transform .3s ease;opacity:0;transform:translateY(-10px)}
.greet svg.spark{width:15px;height:15px;flex:0 0 auto;color:#D8BCFF;margin-top:1px}
.greet .gx{flex:1;min-width:0}
.greet .gl{font-size:9px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:#D8BCFF}
.greet .gt{font-size:12px;line-height:1.5;margin-top:3px}
.greet .gb{display:flex;gap:6px;margin-top:8px}
.greet .copy-btn{background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.25)}
.greet .dismiss{height:26px;padding:0 10px;border-radius:7px;border:1px solid rgba(255,255,255,.25);
  background:transparent;color:#E7DBFF;font-size:11px;font-weight:600;font-family:inherit;cursor:pointer}
`;
  document.head.appendChild(css);

  /* ======================================================================
     §2  ICONS — inline SVG constants (stroke = currentColor, no assets)
     ====================================================================== */
  function svg(d, vb) {
    return '<svg viewBox="' + (vb || '0 0 24 24') + '" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + d + '</svg>';
  }
  var IC_CHK = svg('<path d="M4 12.5l5 5L20 6.5"/>');
  var IC_SPARK = svg('<path d="M12 3l1.9 5.6L19.5 10l-5.6 1.9L12 17.5l-1.9-5.6L4.5 10l5.6-1.4z"/>');
  var IC_EAR = svg('<path d="M17 8.5a5 5 0 10-9.6 2c.8 1.6 2.1 2.4 2.1 4a3 3 0 003 3"/><path d="M9.5 8.5a2.5 2.5 0 015 0c0 1.7-2 2.2-2 4"/>');
  var IC_DOC = svg('<path d="M7 3h7l4 4v14H7z"/><path d="M14 3v4h4"/><path d="M10 12h5M10 16h5"/>');
  var IC_COPY = svg('<rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15V6a2 2 0 012-2h9"/>');
  var IC_WARN = svg('<path d="M12 3L2.5 20h19z"/><path d="M12 9.5v5"/><circle cx="12" cy="17.3" r=".5"/>');
  var IC_SEND = svg('<path d="M4 12h15"/><path d="M13 6l6 6-6 6"/>');
  var IC_LINK = svg('<path d="M10 14a4 4 0 005.7 0l3-3a4 4 0 00-5.7-5.7l-1.2 1.2"/><path d="M14 10a4 4 0 00-5.7 0l-3 3a4 4 0 005.7 5.7l1.2-1.2"/>');
  var IC_BOLT = svg('<path d="M13 2L4.5 13.5H11L10 22l8.5-11.5H12z"/>');
  var IC_PLUS = svg('<path d="M12 5v14M5 12h14"/>');

  /* ======================================================================
     §3  UTILITIES
     ====================================================================== */
  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }
  function has(s) { return typeof s === 'string' && s.trim().length > 0; }
  function fmt$(n) {
    var v = +n; if (isNaN(v)) return esc(String(n));   // payload-derived → always escaped
    return '$' + v.toLocaleString('en-US');
  }
  /* Values arrive as JSON strings that MAY carry ONE extra escape level
     (observed live 2026-07-30) — parse, and on failure unescape once and retry. */
  function jparse(val) {
    if (typeof val !== 'string') return val;
    try { return JSON.parse(val); } catch (e) { /* retry unescaped */ }
    return JSON.parse(val.replace(/\\"/g, '"').replace(/\\\\/g, '\\'));
  }
  /* Copy to clipboard — execCommand within the click gesture is the reliable
     path inside the sandboxed tile iframe; navigator.clipboard is the fallback. */
  function copyText(t) {
    try {
      var ta = document.createElement('textarea');
      ta.value = t; ta.setAttribute('readonly', '');
      ta.style.position = 'fixed'; ta.style.top = '-1000px';
      document.body.appendChild(ta); ta.select();
      var ok = document.execCommand('copy');
      document.body.removeChild(ta);
      if (ok) return true;
    } catch (e) { /* fall through */ }
    try { if (navigator.clipboard) { navigator.clipboard.writeText(t); return true; } } catch (e2) { /* no-op */ }
    return false;
  }
  function postback(payload) {
    try {
      if (window.SDK && typeof window.SDK.postback === 'function') {
        window.SDK.postback(payload);
        return true;
      }
    } catch (e) { /* standalone preview */ }
    return false;
  }
  function norm(s) {
    return String(s == null ? '' : s).toLowerCase()
      .replace(/[^a-z0-9\s]/g, ' ').replace(/\s+/g, ' ').trim();
  }
  /* Cognigy context storage can mask PII-ish string values into {} —
     scrub every string-expected profile field so "[object Object]" never renders. */
  function saneProfile(p) {
    if (!p || typeof p !== 'object') return p;
    ['initials', 'name', 'nickname', 'tier', 'phone', 'occupation', 'meta', 'rightLabel', 'rightValue']
      .forEach(function (k) {
        if (p[k] != null && typeof p[k] !== 'string') {
          p[k] = (typeof p[k] === 'number') ? String(p[k]) : '';
        }
      });
    return p;
  }

  /* ======================================================================
     §4  STATE
     The panel is what the flow sent; everything the agent did locally lives
     in overlays keyed by beat id, so every merStateStr re-push (rehydrate)
     merges cleanly and renders stay idempotent.
     ====================================================================== */
  var S = {
    panel: null,      // last merStateStr object
    sent: null,       // {pct,label,note}
    convo: [],        // transcript from merConvoStr
    fname: '',        // customer's first name for say-labels
    greet: '',        // suggested instant greeting (merGreet)
    asks: [],         // [{askId,q,status,a,added,err}]
    cmds: [],         // [{id,cmd,status,exec,err}] — command-bar jobs
    added: [],        // locally added talk beats (Add to steps)
    stages: []        // live brain-run stages from merStageStr [{n,total,label}]
  };
  var OV = {};        // per-beat overlay: {done,declined,heardHold,foldNow,confirmed,running,runIdx,exec,error,execSettled,copied,toldDone}
  var CP = {};        // copy-text registry, rebuilt every render (key → exact text)
  var SEEN = {};      // first-appearance animation ledger (card key → 1)
  var _askSeq = 0, _cmdSeq = 0;
  var _gotPanel = false;
  var _runTimers = {};   // beat id → substep interval
  var _watchdogs = {};   // beat id → exec watchdog timeout
  var _lastSig = '';     // no-op re-push guard
  var _sentAnimated = false;

  /* ---- generative hero image (the AI-drawn "your day with this laptop" scene) ----
     The composer authors comparison.heroPrompt from the customer's stated needs
     (LLMs decide); the tile hands it to the image endpoint and displays the result
     (code executes). Sig-guarded on the prompt string so rehydrates never regenerate;
     the endpoint caches by prompt hash so even a tile reload costs nothing. */
  var GEN_URL = 'https://aicoe.3ddesignview.com/demo/cognigy_copilot/mock_api_meridian/meridian_image.php';
  var IMG_BASE = 'https://aicoe.3ddesignview.com/demo/cognigy_copilot/mock_api_meridian/img/';
  /* keys are normalized (uppercase, alphanumeric only) so 'NL-AERO14', 'NL-AERO-14'
     and 'nl aero 14' all resolve — composer SKU spelling must never hide a photo */
  var SKU_IMG = { 'NLAERO14': 'aero14.png', 'NLTITAN16': 'titan16.png' };
  function skuImg(sku) {
    return SKU_IMG[String(sku == null ? '' : sku).toUpperCase().replace(/[^A-Z0-9]/g, '')] || '';
  }
  var HERO = { sig: '', state: '', url: '', err: '', showPrompt: false };

  function heroPrompt() {
    var c = S.panel && S.panel.comparison;
    return (c && typeof c.heroPrompt === 'string' && c.heroPrompt.trim()) ? c.heroPrompt.trim() : '';
  }
  function tendHero() {
    var p = heroPrompt();
    if (!p || p === HERO.sig) return;
    HERO.sig = p; HERO.state = 'gen'; HERO.url = ''; HERO.err = ''; HERO.showPrompt = false;
    startHero(p);
  }
  function startHero(mine) {
    var ctl = (typeof AbortController !== 'undefined') ? new AbortController() : null;
    var killed = false;
    var timer = setTimeout(function () { killed = true; if (ctl) ctl.abort(); }, 65000);
    fetch(GEN_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt: mine }),
      signal: ctl ? ctl.signal : undefined
    }).then(function (r) { return r.json(); }).then(function (j) {
      if (HERO.sig !== mine) return;                       // superseded by a newer prompt
      clearTimeout(timer);
      if (j && j.ok && j.url && /^https:/.test(j.url)) { HERO.state = 'ok'; HERO.url = j.url; }
      else {
        HERO.state = 'err';
        HERO.err = 'ERROR: image generation failed — ' + (j && j.error ? j.error : 'no result from the endpoint') +
          (j && j.detail ? ' :: ' + String(j.detail).slice(0, 200) : '');
      }
      render();
    }).catch(function (e) {
      if (HERO.sig !== mine) return;
      clearTimeout(timer);
      HERO.state = 'err';
      HERO.err = killed ? 'ERROR: image generation timed out after 65 s'
        : 'ERROR: image endpoint unreachable — ' + String(e).slice(0, 200);
      render();
    });
  }

  function ov(id) { return OV[id] || (OV[id] = {}); }

  /* Merged view: the flow's playbook + locally added beats, in order. */
  function beats() {
    var out = ((S.panel && S.panel.recommendations) || []).slice();
    S.added.forEach(function (b) {
      if (!out.some(function (r) { return r.id === b.id; })) out.push(b);
    });
    return out;
  }
  function isAction(b) { return b.kind === 'action' || !!b.exec; }
  /* offer:true means the customer must ACCEPT before it executes — it gates
     exactly like confirmGated (the customer's explicit yes authorizes). */
  function needsYes(b) { return !!(b.confirmGated || b.offer); }
  function hasPlan(b) { return !!(b.exec && b.exec.actions && b.exec.actions.length); }
  /* Effective terminal state: the local overlay wins, then the flow's status.
     Contract note: the composer only marks TALK beats done from the transcript;
     action beats complete exclusively through a real merExecStr result here. */
  function done(b) {
    var o = OV[b.id] || {};
    if (o.done || (o.exec && o.exec.ok) || o.declined) return true;
    return b.status === 'done' && !(isAction(b) && !o.exec);
  }
  function firstActive(list) {
    for (var i = 0; i < list.length; i++) { if (!done(list[i])) return i; }
    return -1;
  }
  function findBeat(id) {
    var list = beats();
    for (var i = 0; i < list.length; i++) { if (list[i].id === id) return list[i]; }
    return null;
  }
  function firstName() {
    if (S.fname) return S.fname;
    var p = S.panel && S.panel.profile;
    if (p) {
      if (has(p.nickname)) return p.nickname.split(/\s+/)[0];
      if (has(p.name)) return p.name.split(/\s+/)[0];
    }
    return 'the customer';
  }
  function firstNameLabel() { var n = firstName(); return n === 'the customer' ? 'Customer' : esc(n); }

  /* ======================================================================
     §5  DOM SCAFFOLD
     Mounts into #mer-root when the page provides one (harness); otherwise
     takes over the shell's body. The footer lives outside the scroll area
     so it survives every innerHTML rebuild.
     ====================================================================== */
  var host = document.getElementById('mer-root');
  if (!host) { document.body.innerHTML = ''; host = document.body; }
  else { host.innerHTML = ''; }

  var app = document.createElement('div'); app.className = 'mer-app';
  var scroll = document.createElement('div'); scroll.className = 'mer-scroll';
  var foot = document.createElement('div'); foot.className = 'mer-foot';
  foot.innerHTML =
    '<input id="mer-in" type="text" placeholder="Ask the AI Agent a question… or tell it what to do" autocomplete="off">' +
    '<button type="button" class="foot-btn ask" data-act="ask-send">' + IC_SPARK + 'Ask</button>' +
    '<button type="button" class="foot-btn cmd" data-act="cmd-send">' + IC_BOLT + 'Command</button>';
  app.appendChild(scroll); app.appendChild(foot);
  host.appendChild(app);

  var greetEl = null;   // toast node, managed outside render()

  /* ======================================================================
     §6  RENDER — PROFILE / SENTIMENT / CONTEXT / NEEDS / COMPARISON
     Every renderer returns an HTML string; newCard() gates entry animations
     to the FIRST appearance only, so re-renders never re-animate.
     ====================================================================== */
  function newCard(k) { if (SEEN[k]) return ' seen'; SEEN[k] = 1; return ''; }

  function sentColor(p) { return p >= 70 ? '#4ADE80' : (p >= 40 ? '#FBBF24' : '#F87171'); }

  function htmlProfile() {
    var p = saneProfile(S.panel && S.panel.profile);
    if (!p) return '';
    var h = '<div class="mcard hd' + newCard('profile') + '">';
    h += '<div class="hd-top">' +
      '<div class="hd-avatar">' + esc(p.initials || (p.name || '?').slice(0, 2).toUpperCase()) + '</div>' +
      '<div class="hd-id"><div class="hd-name">' + esc(p.name || '') +
      (has(p.nickname) && p.nickname !== (p.name || '').split(/\s+/)[0]
        ? '<span class="nick">goes by ' + esc(p.nickname) + '</span>' : '') + '</div>' +
      (has(p.meta) ? '<div class="hd-meta">' + esc(p.meta) + '</div>' : '') +
      ((has(p.occupation) || has(p.phone))
        ? '<div class="hd-sub">' + esc([p.occupation, p.phone].filter(has).join(' · ')) + '</div>' : '') +
      '</div>' +
      (has(p.rightValue)
        ? '<div class="hd-right"><div class="lbl">' + esc(p.rightLabel || '') + '</div><div class="val">' + esc(p.rightValue) + '</div></div>' : '') +
      '</div>';
    if (p.stats && p.stats.length) {
      h += '<div class="hd-stats">';
      p.stats.forEach(function (st) {
        h += '<div class="hd-stat"><div class="k">' + esc(st.k) + '</div><div class="v">' + esc(st.v) + '</div></div>';
      });
      h += '</div>';
    }
    if (p.badges && p.badges.length) {
      h += '<div class="hd-badges">';
      p.badges.forEach(function (b) { h += '<span class="pill ' + esc(b.cls || 'blue') + '">' + esc(b.t) + '</span>'; });
      h += '</div>';
    }
    h += htmlSentiment();
    return h + '</div>';
  }

  function htmlSentiment() {
    var sv = S.sent;
    if (!sv) return '';
    var pct = Math.max(0, Math.min(100, +sv.pct || 0));
    return '<div class="hd-sent">' +
      '<div class="row1">' + firstNameLabel() + '’s sentiment' +
      '<span class="sent-live"><i></i>live</span></div>' +
      '<div class="sent-bar"><i id="mer-sent-fill" data-w="' + pct + '" style="background:' + sentColor(pct) + '"></i></div>' +
      '<div class="sent-sub"><span class="lb" id="mer-sent-lb" style="color:' + sentColor(pct) + '">' + esc(sv.label || '') + '</span>' +
      '<span class="pc" id="mer-sent-pc">' + pct + '%</span></div>' +
      (has(sv.note) ? '<div class="sent-note" id="mer-sent-note">' + esc(sv.note) + '</div>' : '') +
      '</div>';
  }

  function htmlContext() {
    var p = S.panel; if (!p || !has(p.context)) return '';
    var h = '<div class="mcard' + newCard('ctx') + '"><div class="sec-hd"><span class="sec">The situation</span></div>';
    h += '<div class="ctx-tx">' + esc(p.context) + '</div>';
    if (p.attempted && p.attempted.length) {
      h += '<div class="ctx-att">';
      p.attempted.forEach(function (a) { h += '<div class="att-row">' + IC_CHK + '<span>' + esc(a.t) + '</span></div>'; });
      h += '</div>';
    }
    if (p.customerAsks && p.customerAsks.length) {
      h += '<div class="ask-chips">';
      p.customerAsks.forEach(function (a) {
        h += '<span class="ask-chip' + (a.resolved ? ' res' : '') + '"><span class="a">' + esc(a.ask) + '</span>' +
          (a.resolved && has(a.resolution) ? '<span class="r">· ' + esc(a.resolution) + '</span>' : '') + '</span>';
      });
      h += '</div>';
    }
    return h + '</div>';
  }

  function htmlNeeds() {
    var needs = (S.panel && S.panel.needs) || [];
    if (!needs.length) return '';
    var h = '<div class="mcard' + newCard('needs') + '"><div class="sec-hd">' +
      IC_EAR.replace('<svg', '<svg style="color:#6B21C8"') +
      '<span class="sec ai">What ' + firstNameLabel() + ' told us</span></div><div class="needs">';
    needs.forEach(function (n) {
      h += '<div class="need' + (n.weight === 'high' ? ' hi' : '') + '" title="' + esc(n.quote || '') + '">' +
        '<div class="lb">' + (n.weight === 'high' ? IC_SPARK : '') + esc(n.label) + '</div>' +
        (has(n.quote) ? '<div class="qt">“' + esc(n.quote) + '”</div>' : '') +
        '</div>';
    });
    return h + '</div></div>';
  }

  function htmlComparison() {
    var c = S.panel && S.panel.comparison;
    if (!c || !c.products || c.products.length < 2) return '';
    /* provisional = the zero-LLM pre-panel duo (photos + prices, no ranking yet);
       the composer's real ranked cards replace it in place */
    var isProv = !!c.provisional;
    var needById = {};
    ((S.panel && S.panel.needs) || []).forEach(function (n) { needById[n.id] = n.label; });
    var prods = c.products.slice().sort(function (a, b) { return (a.rank || 9) - (b.rank || 9); });
    var h = '<div class="mcard' + newCard('cmp') + '"><div class="sec-hd">' +
      IC_SPARK.replace('<svg', '<svg style="color:#6B21C8"') +
      '<span class="sec ai">' + (isProv ? 'Sizing up the options' : 'The recommendation') + '</span></div>';
    if (has(c.intro)) h += '<div class="cmp-intro">' + esc(c.intro) + '</div>';
    h += '<div class="cmp-grid">';
    prods.forEach(function (pr) {
      var lead = pr.rank === 1 && !isProv;
      var imgFile = skuImg(pr.sku);
      h += '<div class="prod' + (lead ? ' lead' : '') + (isProv ? ' prov' : '') + '">' +
        '<div class="prod-tag">' + esc(pr.tag || (isProv ? 'On the table' : (lead ? 'Best fit for you' : 'The alternative'))) + '</div>' +
        '<div class="prod-bd">' +
        (imgFile ? '<div class="prod-img"><img alt="' + esc(pr.name) + '" data-imgfall src="' + IMG_BASE + imgFile + '"></div>' : '') +
        '<div class="prod-nm"><span class="n">' + esc(pr.name) + '</span><span class="p">' + fmt$(pr.price) + '</span></div>' +
        (has(pr.headline) ? '<div class="prod-hl">' + esc(pr.headline) + '</div>' : '');
      if (pr.fit && pr.fit.length) {
        h += '<div class="fits">';
        pr.fit.forEach(function (f) {
          var g = f.verdict === 'wins' ? '✓' : (f.verdict === 'close' ? '~' : '▾');
          h += '<div class="fit ' + esc(f.verdict) + '"><span class="g">' + g + '</span>' +
            '<span><span class="nd">' + esc(needById[f.need] || f.need) + '</span> ' +
            '<span class="why">— ' + esc(f.why || '') + '</span></span></div>';
        });
        h += '</div>';
      }
      /* MER-POL-05: the comparison is never one-sided — the honest tradeoff always renders. */
      if (has(pr.honest)) {
        h += '<div class="honest"><div class="honest-in"><div class="hl">The honest tradeoff</div>' +
          '<div class="ht">' + esc(pr.honest) + '</div></div></div>';
      }
      h += '</div></div>';
    });
    return h + '</div>' + htmlHero(prods[0]) + '</div>';
  }

  /* The hero renders inside the comparison card, full width under the grid:
     shimmer while the scene generates, then the image with an honest
     "AI-generated visualization" caption + the LLM's own brief on demand,
     or a visible error with the raw payload (never silent, never stock art). */
  function htmlHero(lead) {
    if (!heroPrompt() || !HERO.state) return '';
    var name = lead && has(lead.name) ? lead.name : 'this pick';
    var h = '<div class="hero">';
    if (HERO.state === 'gen') {
      h += '<div class="hero-shimmer">' + IC_SPARK +
        '<span>AI Agent is sketching how the ' + esc(name) + ' fits ' + firstNameLabel() + '’s day…</span></div>';
    } else if (HERO.state === 'ok') {
      h += '<div class="hero-imgwrap"><img class="hero-img" alt="AI-generated visualization" src="' + esc(HERO.url) + '"></div>' +
        '<div class="hero-cap"><span class="hc-l">' + IC_SPARK +
        '<span>AI-generated visualization — drawn from what ' + firstNameLabel() + ' told us</span></span>' +
        '<button type="button" class="hero-why" data-act="hero-prompt">' +
        (HERO.showPrompt ? 'Hide the brief' : 'What the AI asked for') + '</button></div>' +
        (HERO.showPrompt ? '<div class="hero-brief">“' + esc(heroPrompt()) + '”</div>' : '');
    } else {
      h += '<div class="hero-err"><div class="he-t">⚠ IMAGE GENERATION FAILED</div>' +
        '<div class="he-d">' + esc(HERO.err) + '</div>' +
        '<button type="button" class="hero-retry" data-act="hero-retry">Try again</button></div>';
    }
    return h + '</div>';
  }

  /* Live brain-run stages (merStageStr) — REAL pipeline boundaries pushed by the
     flow (gate done → policy read → composing), never a fake spinner. Earlier
     stages collapse to checkmarks; the latest one spins. Cleared the moment a
     composed panel lands. */
  function htmlStages() {
    if (!S.stages.length) return '';
    var h = '<div class="mcard stgcard' + newCard('stg') + '">' +
      '<div class="stg-eyebrow">' + IC_SPARK + '<span>AI Agent is working</span></div>';
    S.stages.forEach(function (st, i) {
      var cur = i === S.stages.length - 1;
      h += '<div class="stg' + (cur ? ' cur' : ' done') + '">' +
        '<span class="sdot">' + (cur ? '' : IC_CHK) + '</span>' +
        '<span class="slb">' + esc(st.label) + '</span></div>';
    });
    return h + '</div>';
  }

  /* ======================================================================
     §7  RENDER — PLAYBOOK BEATS
     Talk beats: say line + copy + heard-gating. Action beats: policy basis,
     Approve → in-flight → real refs (or a visible error, never fake success).
     ====================================================================== */
  function htmlPlaybook() {
    var list = beats();
    if (!list.length) return '';
    var act = firstActive(list);
    var h = '<div class="mcard' + newCard('pb') + '"><div class="sec-hd"><span class="sec">Guided steps</span></div>';
    if (has(S.panel && S.panel.nextStepsIntro)) h += '<div class="pb-intro">' + esc(S.panel.nextStepsIntro) + '</div>';
    list.forEach(function (b, i) { h += htmlBeat(b, i, act); });
    return h + '</div>';
  }

  function htmlBeat(b, i, act) {
    var o = OV[b.id] || {};
    var isAct = isAction(b);
    var isDecl = !!o.declined;
    var isDone = done(b) && !o.heardHold;
    var state = o.heardHold ? 'active'
      : isDecl ? 'declined'
        : isDone ? 'done'
          : (i === act ? 'active' : 'pending');
    var cls = 'beat ' + state + (o.error ? ' failed' : '') + (o.foldNow ? ' folding' : '');
    var fn = firstName();
    var h = '<div class="' + cls + '" data-beat="' + esc(b.id) + '">';

    /* header row */
    h += '<div class="beat-hd">' +
      '<span class="dot' + ((isDone || isDecl) ? ' ck' : '') + '">' + ((isDone || isDecl) ? IC_CHK : '') + '</span>' +
      '<span class="beat-lab">' + esc(b.label) + '</span>' +
      (isDone && !isDecl
        ? '<span class="beat-kind done-chip">Done</span>'
        : '<span class="beat-kind ' + (isAct ? 'action' : 'talk') + '">' + (isAct ? 'AI runs it' : 'You say it') + '</span>') +
      '</div>';

    /* queued talk beats stay slim; done beats collapse unless mid-fold or carrying results */
    if (state === 'pending' && !isAct) return h + '</div>';
    var keepOpen = o.heardHold || o.foldNow ||
      (isAct && o.exec && o.exec.executed && o.exec.executed.length);
    if (state === 'done' && !keepOpen) return h + '</div>';
    if (isDecl) {
      h += '<div class="declined-note">' + esc(fn) + ' declined — no action taken.</div>';
      return h + '</div>';
    }

    if (has(b.detail) && state !== 'done') {
      h += '<div class="beat-detail">' + esc(b.detail) + '</div>';
    }

    /* say card — the exact line the agent relays */
    if (has(b.say) && state !== 'done') {
      var sayKey = 'say-' + b.id; CP[sayKey] = b.say;
      var footHtml;
      if (o.heardHold) {
        footHtml = '<div class="heard">' + IC_CHK + '✓ AI Agent heard this</div>';
      } else if (!isAct) {
        footHtml = '<div class="say-foot">' +
          '<button type="button" class="copy-btn' + (o.copied ? ' did' : '') + '" data-act="copy" data-key="' + sayKey + '">' +
          IC_COPY + (o.copied ? 'Copied' : 'Copy') + '</button>' +
          '<span class="listen-hint">' + IC_EAR + 'Auto-checks when the AI Agent hears you say it<span class="ldots"><i></i><i></i><i></i></span></span>' +
          '</div>';
      } else {
        footHtml = '<div class="say-foot">' +
          '<button type="button" class="copy-btn ghost" data-act="copy" data-key="' + sayKey + '">' + IC_COPY + 'Copy</button></div>';
      }
      h += '<div class="say"><div class="lab">' + IC_SPARK + (isAct ? 'Relay to ' : 'Say to ') + esc(fn) + '</div>' +
        '<div class="tx">' + esc(b.say) + '</div>' + footHtml + '</div>';
    }

    /* confirm-gated OR offered: awaiting the customer's yes/no */
    if (needsYes(b) && state === 'active' && !o.heardHold && o.confirmed !== 'yes') {
      h += '<div class="await"><span class="await-chip"><i></i>awaiting ' + esc(fn) + '’s answer</span>' +
        '<button type="button" class="mini-btn" data-act="confirm-yes" data-id="' + esc(b.id) + '">' + esc(fn) + ' said yes</button>' +
        '<button type="button" class="mini-btn no" data-act="confirm-no" data-id="' + esc(b.id) + '">No</button></div>';
    }

    /* action beats: policy basis + approve / in-flight / executed / error */
    if (isAct) {
      if (b.policyQuote && has(b.policyQuote.quote) && state !== 'done') {
        var PQ = b.policyQuote;
        h += '<div class="pbasis">' + IC_DOC + '<div style="min-width:0"><div class="pb-hd">' +
          '<span class="pb-lab">Policy basis</span>' +
          (has(PQ.ruleId) ? '<span class="pb-rule">' + esc(PQ.ruleId) + '</span>' : '') + '</div>' +
          '<div class="pb-q">“' + esc(PQ.quote) + '”</div>' +
          (has(PQ.source) ? '<div class="pb-src">' + esc(PQ.source) + '</div>' : '') +
          '</div></div>';
      }
      if (o.error) {
        h += '<div class="exec-err"><div class="t">' + IC_WARN + 'Execution failed</div>' +
          '<div class="m">' + esc(o.error) + '</div>' +
          '<button type="button" class="retry-btn" data-act="approve" data-id="' + esc(b.id) + '">Try again</button></div>';
      } else if (o.running) {
        h += '<div class="run-strip"><span class="sp"></span>' +
          '<span class="run-tx" id="mer-run-' + esc(b.id) + '">' +
          esc((b.substeps && b.substeps[o.runIdx % b.substeps.length]) || b.running || 'AI Agent working…') +
          '</span></div>';
      } else if (o.exec && o.exec.executed && o.exec.executed.length) {
        h += htmlExecuted(b, o);
      } else if (state === 'active' && (!needsYes(b) || o.confirmed === 'yes')) {
        if (hasPlan(b)) {
          var label = b.offer ? 'Offer & approve' : 'Approve';
          if (b.charge && has(b.chargeLabel)) label += ' · ' + b.chargeLabel;
          h += '<button type="button" class="approve" data-act="approve" data-id="' + esc(b.id) + '">' + IC_CHK + esc(label) + '</button>';
        } else {
          /* honest empty state — an action beat with no executable plan gets no Approve */
          h += '<div class="noexec">No executable plan attached — nothing for the AI Agent to run.</div>';
        }
      }
    }
    return h + '</div>';
  }

  /* Executed refs + sayDone reveal + receipt link. Refs animate in once, then settle. */
  function htmlExecuted(b, o) {
    var x = o.exec;
    var h = '<div class="execd' + (o.execSettled ? ' settled' : '') + '">';
    x.executed.forEach(function (e, i) {
      h += '<div class="exec-row' + (e.ok ? '' : ' bad') + '" style="animation-delay:' + (i * 0.18) + 's">' +
        (e.ok ? IC_CHK : IC_WARN) + '<span>' + esc(e.summary || e.action) + '</span>' +
        (has(e.ref) ? '<span class="ref">' + esc(e.ref) + '</span>' : '') + '</div>';
    });
    h += '</div>';
    var rc = null;
    x.executed.forEach(function (e) { if (has(e.receiptUrl)) rc = e.receiptUrl; });
    if (rc) {
      CP['rcpt-' + b.id] = rc;
      /* payload URL becomes an href ONLY when it is a real https URL */
      h += '<div class="rcpt">' + IC_LINK +
        (/^https:\/\//i.test(rc)
          ? '<a href="' + esc(rc) + '" target="_blank" rel="noopener">' + esc(rc) + '</a>'
          : '<span class="plain">' + esc(rc) + '</span>') +
        '<button type="button" class="copy-btn" data-act="copy" data-key="rcpt-' + esc(b.id) + '">' + IC_COPY + 'Copy link</button></div>';
    }
    if (has(b.sayDone) && !o.toldDone) {
      var k = 'sayDone-' + b.id; CP[k] = b.sayDone;
      h += '<div class="say good" style="margin-left:24px"><div class="lab">' + IC_SPARK + 'Tell ' + esc(firstName()) + ' the good news</div>' +
        '<div class="tx">' + esc(b.sayDone) + '</div>' +
        '<div class="say-foot"><button type="button" class="copy-btn" data-act="copy-saydone" data-key="' + k + '" data-id="' + esc(b.id) + '">' +
        IC_COPY + 'Copy</button></div></div>';
    }
    if (!o.execSettled) {
      /* let the ref stagger play once, then settle so re-renders are static */
      setTimeout(function () { o.execSettled = true; }, 900 + x.executed.length * 180);
    }
    return h;
  }

  /* ======================================================================
     §8  RENDER — DRAFT MESSAGE, KNOWLEDGE CARDS, SKELETON + THINKING
     ====================================================================== */
  function htmlDraft() {
    var d = S.panel && S.panel.draftMessage;
    if (!has(d)) return '';
    CP['draft'] = d;
    return '<div class="mcard' + newCard('draft') + '"><div class="sec-hd">' +
      IC_SEND.replace('<svg', '<svg style="color:#126BCE"') +
      '<span class="sec" style="color:#126BCE">Suggested message</span></div>' +
      '<div class="draft-tx">' + esc(d) + '</div>' +
      '<div class="draft-foot"><button type="button" class="copy-btn" data-act="copy" data-key="draft">' + IC_COPY + 'Copy message</button></div></div>';
  }

  function htmlAsks() {
    var h = '';
    S.asks.forEach(function (a) {
      var key = 'ask-' + a.askId;
      h += '<div class="mcard kb-card' + newCard(key) + '">';
      h += '<div class="sec-hd">' + IC_DOC.replace('<svg', '<svg style="color:#6B21C8"') +
        '<span class="sec ai">' + esc((a.a && a.a.title) || 'Knowledge lookup') + '</span></div>';
      if (has(a.q)) h += '<div class="kb-q">“' + esc(a.q) + '”</div>';
      if (a.status === 'loading') {
        h += '<div class="kb-load"><span class="sp"></span>Searching the Northlight policy library…</div>';
      } else if (a.status === 'error') {
        h += '<div class="kb-esc">' + IC_WARN + '<span>' + esc(a.err || 'No answer arrived from the flow.') + '</span></div>';
      } else if (a.a) {
        var ans = a.a;
        h += '<div class="kb-a">' + esc(ans.answer || '') + '</div>';
        if (ans.escalate && has(ans.escalateNote)) {
          h += '<div class="kb-esc">' + IC_WARN + '<span>' + esc(ans.escalateNote) + '</span></div>';
        }
        if (ans.sources && ans.sources.length) {
          h += '<div class="kb-srcs"><span class="kb-srcl">Policy library</span>';
          ans.sources.forEach(function (s2) { h += '<span class="kb-src" title="' + esc(s2.title || '') + '">' + esc(s2.id) + '</span>'; });
          h += '</div>';
        }
        if (has(ans.tell)) {
          var tk = 'tell-' + a.askId; CP[tk] = ans.tell;
          h += '<div class="say good" style="margin:8px 0 0"><div class="lab">' + IC_SPARK + 'Tell ' + esc(firstName()) + '</div>' +
            '<div class="tx">' + esc(ans.tell) + '</div>' +
            '<div class="say-foot"><button type="button" class="copy-btn" data-act="copy" data-key="' + tk + '">' + IC_COPY + 'Copy</button></div></div>';
        }
        if (has(ans.tell) || has(ans.answer)) {
          h += '<div class="kb-addrow"><button type="button" class="kb-add" data-act="ask-add" data-id="' + esc(a.askId) + '"' +
            (a.added ? ' disabled' : '') + '>' + (a.added ? IC_CHK + 'Added to steps' : IC_PLUS + 'Add to steps') + '</button></div>';
        }
      }
      h += '</div>';
    });
    /* command-bar jobs (free-text agent commands → merExecStr results) */
    S.cmds.forEach(function (c) {
      var key = 'cmd-' + c.id;
      h += '<div class="mcard cmd-card' + newCard(key) + '">';
      h += '<div class="sec-hd">' + IC_BOLT.replace('<svg', '<svg style="color:#0F2A4A"') +
        '<span class="sec">Agent command</span></div>';
      h += '<div class="cmd-q">“' + esc(c.cmd) + '”</div>';
      if (c.status === 'run') {
        h += '<div class="kb-load" style="margin-top:8px"><span class="sp"></span>AI Agent is carrying it out…</div>';
      } else if (c.status === 'error') {
        h += '<div class="exec-err" style="margin:8px 0 0"><div class="t">' + IC_WARN + 'Execution failed</div>' +
          '<div class="m">' + esc(c.err || '') + '</div></div>';
      } else if (c.exec) {
        h += '<div class="execd settled" style="margin:8px 0 0">';
        (c.exec.executed || []).forEach(function (e) {
          h += '<div class="exec-row" style="opacity:1;transform:none;animation:none">' +
            (e.ok ? IC_CHK : IC_WARN) + '<span>' + esc(e.summary || e.action) + '</span>' +
            (has(e.ref) ? '<span class="ref">' + esc(e.ref) + '</span>' : '') + '</div>';
        });
        h += '</div>';
      }
      h += '</div>';
    });
    return h;
  }

  /* Before the first merStateStr: skeleton + "reviewing the conversation". */
  function htmlBootSkeleton() {
    return '<div class="mcard' + newCard('boot') + '"><div class="boot">' + IC_EAR +
      '<div class="t">AI Agent is reviewing the conversation…</div></div>' +
      '<div class="skel-card"><div class="skel" style="width:62%"></div>' +
      '<div class="skel" style="width:88%"></div><div class="skel" style="width:74%"></div></div></div>' +
      '<div class="mcard' + newCard('boot2') + '"><div class="skel-card"><div class="skel" style="width:40%"></div>' +
      '<div class="skel" style="width:92%"></div><div class="skel" style="width:80%"></div>' +
      '<div class="skel" style="width:56%"></div></div></div>';
  }

  /* Pre-panel (profile in, playbook not yet): cycling thinking card holds the slot. */
  var THINK_MSGS = [
    'Reviewing Northlight policies and the product catalog…',
    'Matching the catalog to what the customer said matters…',
    'Grounding each step in the Northlight policy library…',
    'Drafting the guided steps…'
  ];
  var _thinkIdx = 0, _thinkIv = null;
  function htmlThinking() {
    return '<div class="mcard' + newCard('think') + '"><div class="think"><span class="sp"></span>' +
      '<div style="min-width:0"><div class="think-t">' + IC_SPARK + 'AI Agent is building the guided steps…</div>' +
      '<div class="think-s" id="mer-think-msg">' + esc(THINK_MSGS[_thinkIdx % THINK_MSGS.length]) + '</div></div></div></div>';
  }
  function tendThinkTimer() {
    /* self-cleaning: runs while the element exists, stops the moment it's gone */
    var el = document.getElementById('mer-think-msg');
    if (el && !_thinkIv) {
      _thinkIv = setInterval(function () {
        var e2 = document.getElementById('mer-think-msg');
        if (!e2) { clearInterval(_thinkIv); _thinkIv = null; return; }
        _thinkIdx = (_thinkIdx + 1) % THINK_MSGS.length;
        e2.style.opacity = 0;
        setTimeout(function () {
          var e3 = document.getElementById('mer-think-msg');
          if (e3) { e3.textContent = THINK_MSGS[_thinkIdx]; e3.style.opacity = 1; }
        }, 320);
      }, 2600);
    } else if (!el && _thinkIv) { clearInterval(_thinkIv); _thinkIv = null; }
  }

  /* ======================================================================
     §9  RENDER ORCHESTRATOR
     Full innerHTML rebuild of the scroll area, guarded by a state signature
     so rehydrate re-pushes never blink, with scroll preservation.
     ====================================================================== */
  function sig() {
    return JSON.stringify([
      S.panel, S.sent, S.greet,
      S.asks.map(function (a) { return [a.askId, a.status, a.added, a.a && a.a.answer, a.a && a.a.tell]; }),
      S.cmds.map(function (c) { return [c.id, c.status]; }),
      S.added.map(function (b) { return b.id; }),
      OV,
      [HERO.sig, HERO.state, HERO.url, HERO.err, HERO.showPrompt],
      S.stages
    ]);
  }

  function render(force) {
    var s = sig();
    if (!force && s === _lastSig) return;   // no-op push → no flicker, no scroll loss
    _lastSig = s;
    CP = {};
    var h = '';
    if (!S.panel) {
      h = htmlBootSkeleton();
    } else {
      h += htmlProfile();
      h += htmlContext();
      h += htmlNeeds();
      h += htmlComparison();
      h += htmlStages();
      /* the live stage strip replaces the generic thinking card while a run streams */
      h += beats().length ? htmlPlaybook() : (S.stages.length ? '' : htmlThinking());
      h += htmlDraft();
      h += htmlAsks();
    }
    var keep = scroll.scrollTop;
    scroll.innerHTML = h;
    scroll.scrollTop = keep;
    wireImgs();
    animateSentIn();
    tendThinkTimer();
    tendGreet();
  }

  /* Image listeners re-attach after every rebuild (no inline handlers in the
     sandbox): missing static shots hide their strip; the hero fades in on load
     and a dead generated URL surfaces as a visible error. */
  function wireImgs() {
    var imgs = scroll.querySelectorAll('img[data-imgfall]');
    for (var i = 0; i < imgs.length; i++) {
      (function (im) {
        im.addEventListener('error', function () {
          var w = im.closest ? im.closest('.prod-img') : null;
          if (w) w.style.display = 'none';
        });
      })(imgs[i]);
    }
    var hi = scroll.querySelector('img.hero-img');
    if (hi) {
      hi.addEventListener('load', function () { hi.classList.add('in'); });
      hi.addEventListener('error', function () {
        if (HERO.state !== 'ok') return;
        HERO.state = 'err';
        HERO.err = 'ERROR: the generated image URL failed to load — ' + HERO.url;
        render();
      });
      if (hi.complete && hi.naturalWidth > 0) hi.classList.add('in');
    }
  }

  /* ======================================================================
     §10 INTERACTIONS — one delegated click handler (survives every rebuild;
     no inline onclick anywhere, per the tile sandbox rules)
     ====================================================================== */
  app.addEventListener('click', function (e) {
    var t = e.target && e.target.closest ? e.target.closest('[data-act]') : null;
    if (!t) return;
    var act = t.getAttribute('data-act');
    var id = t.getAttribute('data-id') || '';

    if (act === 'copy' || act === 'copy-saydone') {
      var key = t.getAttribute('data-key');
      if (key && CP[key] != null && copyText(CP[key])) {
        t.classList.add('did');
        t.innerHTML = IC_CHK + 'Copied';
        if (key.indexOf('say-') === 0) ov(key.slice(4)).copied = true;
        if (act === 'copy-saydone' && id) {
          /* good news relayed → let the card breathe, then tuck it away */
          var o = ov(id);
          setTimeout(function () { o.toldDone = true; render(); }, 1900);
        }
      }
      return;
    }
    if (act === 'approve') { approve(id); return; }
    if (act === 'confirm-yes') { confirmBeat(id, true); return; }
    if (act === 'confirm-no') { confirmBeat(id, false); return; }
    if (act === 'hero-prompt') { HERO.showPrompt = !HERO.showPrompt; render(); return; }
    if (act === 'hero-retry') { HERO.sig = ''; tendHero(); return; }
    if (act === 'ask-send') { submitInput('ask'); return; }
    if (act === 'cmd-send') { submitInput('command'); return; }
    if (act === 'ask-add') { addAskAsStep(id); return; }
    if (act === 'greet-copy') {
      if (S.greet && copyText(S.greet)) t.innerHTML = IC_CHK + 'Copied';
      return;
    }
    if (act === 'greet-dismiss') { dismissGreet(); return; }
  });

  document.getElementById('mer-in').addEventListener('keydown', function (e) {
    if (e.key !== 'Enter') return;
    /* Enter always takes the safe, read-only ASK path; execution only via the explicit Command button */
    submitInput('ask');
  });

  function submitInput(kind) {
    var input = document.getElementById('mer-in');
    var v = (input.value || '').trim();
    if (!v) return;
    input.value = '';
    if (kind === 'ask') {
      var askId = 'tile-' + (++_askSeq);
      S.asks.push({ askId: askId, q: v, status: 'loading' });
      render();
      if (!postback({ action: 'ask', query: v, askId: askId })) {
        markAskError(askId, 'ERROR: no connection to the flow — the question was not sent.');
        return;
      }
      setTimeout(function () {   // watchdog: an infinite spinner tells the agent nothing
        var a = findAsk(askId);
        if (a && a.status === 'loading') markAskError(askId, 'ERROR: no answer arrived from the flow (30s). Try again.');
      }, 30000);
    } else {
      var cid = 'cmd-' + (++_cmdSeq);
      S.cmds.push({ id: cid, cmd: v, status: 'run' });
      render();
      if (!postback({ action: 'command', command: v })) {
        markCmd(cid, 'error', 'ERROR: no connection to the flow — the command was not sent.');
        return;
      }
      setTimeout(function () {   // multi-tool passes run long — a generous 60s before declaring failure
        var c = findCmd(cid);
        if (c && c.status === 'run') markCmd(cid, 'error', 'ERROR: no result arrived from the flow (60s).');
      }, 60000);
    }
    scrollToBottom();
  }
  function findAsk(id) { for (var i = 0; i < S.asks.length; i++) { if (S.asks[i].askId === id) return S.asks[i]; } return null; }
  function findCmd(id) { for (var i = 0; i < S.cmds.length; i++) { if (S.cmds[i].id === id) return S.cmds[i]; } return null; }
  function markAskError(id, msg) { var a = findAsk(id); if (a) { a.status = 'error'; a.err = msg; render(); } }
  function markCmd(id, st, msg) { var c = findCmd(id); if (c) { c.status = st; if (msg) c.err = msg; render(); } }
  function scrollToBottom() { setTimeout(function () { scroll.scrollTop = scroll.scrollHeight; }, 60); }

  /* "Add to steps" — promote a knowledge answer into a heard-gated talk beat,
     kept in a local overlay list so every re-render (and rehydrate) keeps it. */
  function addAskAsStep(askId) {
    var a = findAsk(askId);
    if (!a || a.status !== 'done' || !a.a || a.added) return;
    var say = has(a.a.tell) ? a.a.tell
      : String(a.a.answer || '').replace(/\n+/g, ' ').split('. ').slice(0, 2).join('. ');
    if (!has(say)) return;
    var slug = String(a.a.title || a.q || askId).toLowerCase()
      .replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 40) || askId;
    var beat = {
      id: 'kb-' + slug,
      label: 'Cover: ' + (a.a.title || 'knowledge answer'),
      kind: 'talk', status: 'pending', say: say,
      detail: 'From the knowledge lookup — ' +
        (((a.a.sources || []).map(function (s2) { return s2.id; }).join(', ')) || 'Northlight policy library')
    };
    if (/\?\s*$/.test(say.trim())) beat.confirmGated = true;
    if (!S.added.some(function (b2) { return b2.id === beat.id; })) S.added.push(beat);
    a.added = true;
    render();
  }

  function confirmBeat(id, yes) {
    var b = findBeat(id); if (!b) return;
    var o = ov(id);
    if (o.confirmed || o.declined) return;   // re-entry guard: double-clicks / duplicate auto-detects are no-ops
    if (yes) {
      o.confirmed = 'yes';
      if (!isAction(b)) {
        /* talk beat confirmed → heard-style completion with the slow fold */
        o.done = true; o.heardHold = true;
        scheduleFold(id);
      }
    } else {
      o.declined = true;
    }
    render();
  }

  /* ======================================================================
     §11 HEARD-GATING + CONFIRM GATES (transcript matching)
     The active talk beat's say line is matched against the agent's own
     utterances: >= 50% of its >= 4-char words within the last 8 agent turns.
     Confirm-gated beats instead listen for the CUSTOMER's yes/no.
     ====================================================================== */
  function scheduleFold(id) {
    /* HEARD MOMENT: banner holds ~2.1s, then the slow (1.15s) visible fold. */
    setTimeout(function () {
      var o = ov(id);
      o.heardHold = false; o.foldNow = true;
      render(true);
      setTimeout(function () { delete o.foldNow; render(true); }, 1250);
    }, 2100);
  }

  /* Customer yes/no detection — whole-token matching only, with a negation
     guard: an affirmation preceded within 3 tokens by not/n't/no/never/don't/
     won't/wouldn't NEVER counts as yes ("not sure", "no thanks, sounds good
     though" must not auto-confirm). Declines are checked first. */
  var ACCEPT_TOK = { yes: 1, yeah: 1, yep: 1, sure: 1, okay: 1, ok: 1, fine: 1, deal: 1, accept: 1, perfect: 1 };
  var ACCEPT_PHRASES = ['that works', 'works for me', 'sounds good', 'go ahead', 'please do', 'lets do it', 'ill take it'];
  var DECLINE_PHRASES = ['no thanks', 'no thank you', 'nope', 'not now', 'wont work', 'not interested', 'rather not', 'hold off', 'too much', 'forget it'];
  var NEG_TOK = { not: 1, no: 1, never: 1, dont: 1, wont: 1, wouldnt: 1, cant: 1, nt: 1 };
  function yesNoToks(s) {
    return String(s == null ? '' : s).toLowerCase()
      .replace(/[’']/g, '')                    // don't → dont, won't → wont
      .replace(/[^a-z0-9\s]/g, ' ')
      .split(/\s+/).filter(Boolean);
  }
  function phraseAt(toks, ph) {
    for (var i = 0; i + ph.length <= toks.length; i++) {
      var hit = true;
      for (var j = 0; j < ph.length; j++) { if (toks[i + j] !== ph[j]) { hit = false; break; } }
      if (hit) return i;
    }
    return -1;
  }
  function negatedAt(toks, i) {
    for (var j = Math.max(0, i - 3); j < i; j++) { if (NEG_TOK[toks[j]] === 1) return true; }
    return false;
  }
  function saysYes(text) {
    var toks = yesNoToks(text);
    for (var i = 0; i < toks.length; i++) {
      if (ACCEPT_TOK[toks[i]] === 1 && !negatedAt(toks, i)) return true;
    }
    for (var p = 0; p < ACCEPT_PHRASES.length; p++) {
      var at = phraseAt(toks, ACCEPT_PHRASES[p].split(' '));
      if (at >= 0 && !negatedAt(toks, at)) return true;
    }
    return false;
  }
  function saysNo(text) {
    var toks = yesNoToks(text);
    for (var p = 0; p < DECLINE_PHRASES.length; p++) {
      if (phraseAt(toks, DECLINE_PHRASES[p].split(' ')) >= 0) return true;
    }
    return false;
  }

  function checkHeard() {
    var list = beats();
    var act = firstActive(list);
    if (act < 0) return;
    var b = list[act];
    var o = ov(b.id);

    /* confirm-gated / offered: the CUSTOMER's latest words decide */
    if (needsYes(b) && o.confirmed !== 'yes' && !o.declined) {
      var lastCust = '';
      for (var i = S.convo.length - 1; i >= 0; i--) {
        var r = String(S.convo[i].role || '').toLowerCase();
        if (r === 'customer' || r === 'patron' || r === 'contact') { lastCust = String(S.convo[i].text || ''); break; }
      }
      if (lastCust) {
        if (saysNo(lastCust)) { confirmBeat(b.id, false); return; }
        if (saysYes(lastCust)) { confirmBeat(b.id, true); return; }
      }
      return;   // never auto-completes on the agent's own words
    }

    /* talk beats: heard-gate on the agent actually saying the line */
    if (isAction(b) || !has(b.say) || o.done || o.heardHold) return;
    var agent = S.convo.filter(function (t) {
      var role = String(t.role || '').toLowerCase();
      return role === 'agent' || role === 'bot' || role === 'specialist';
    }).slice(-8).map(function (t) { return norm(t.text); });
    if (!agent.length) return;
    var toks = norm(b.say).split(' ').filter(function (w) { return w.length >= 4; });
    if (toks.length < 2) return;   // too little signal — a short/empty say line is never auto-heard
    /* whole-token membership only: build a Set of the agent's words so 'rate'
       can never match inside 'operate' */
    var bset = Object.create(null);
    agent.join(' ').split(' ').forEach(function (w) { if (w) bset[w] = 1; });
    var hit = toks.filter(function (w) { return bset[w] === 1; }).length;
    var said = (hit / toks.length) >= 0.5;
    if (said) {
      o.done = true; o.heardHold = true;
      scheduleFold(b.id);
      render(true);
    }
  }

  /* ======================================================================
     §12 EXECUTION — approve → in-flight → real refs / visible error
     The Approve postback echoes the beat's exec object VERBATIM; the card
     only completes when merExecStr returns real confirmations. No LLM in
     this path, and no fake success: a bad result renders red, narration
     verbatim (standing rule: real data or a visible error).
     ====================================================================== */
  function approve(id) {
    var b = findBeat(id); if (!b || !isAction(b)) return;
    var o = ov(id);
    if (o.running || (o.exec && o.exec.ok)) return;
    if (!hasPlan(b)) return;                            // no executable plan → nothing to postback
    if (needsYes(b) && o.confirmed !== 'yes') return;   // the customer's explicit yes authorizes
    o.error = '';
    if (!postback({ action: 'approve', recId: b.id, exec: b.exec })) {
      o.error = 'ERROR: no connection to the flow — nothing was executed.';
      render();
      return;
    }
    o.running = true; o.runIdx = 0;
    render(true);
    /* cycle the substeps in place while the deterministic exec runs (~1-2s live) */
    var steps = (b.substeps && b.substeps.length) ? b.substeps : [b.running || 'AI Agent working…'];
    clearRun(id);
    _runTimers[id] = setInterval(function () {
      var o2 = OV[id];
      var el = document.getElementById('mer-run-' + id);
      if (!o2 || !o2.running || !el) { clearRun(id); return; }
      o2.runIdx = (o2.runIdx + 1) % steps.length;
      el.classList.add('out');
      setTimeout(function () {
        var el2 = document.getElementById('mer-run-' + id);
        if (el2) { el2.textContent = steps[o2.runIdx % steps.length]; el2.classList.remove('out'); }
      }, 300);
    }, 1100);
    /* watchdog — an infinite spinner tells the agent nothing */
    clearTimeout(_watchdogs[id]);
    _watchdogs[id] = setTimeout(function () {
      var o3 = OV[id];
      if (o3 && o3.running) {
        o3.running = false;
        o3.error = 'ERROR: no confirmation arrived from Northlight systems (25s) — nothing is confirmed yet.';
        clearRun(id);
        render(true);
      }
    }, 25000);
  }
  function clearRun(id) {
    if (_runTimers[id]) { clearInterval(_runTimers[id]); delete _runTimers[id]; }
  }

  function onExec(x) {
    if (!x || typeof x !== 'object') return;
    var id = String(x.recId || '');
    var ok = x.ok === true && !/^ERROR/i.test(String(x.narration || ''));
    var b = id ? findBeat(id) : null;
    if (b) {
      var o = ov(id);
      /* idempotency: replaying the IDENTICAL result is a total no-op (no
         re-animation, no state churn); a different result updates in place */
      var xsig = JSON.stringify(x);
      if (o.execSig === xsig) return;
      var hadOk = !!(o.exec && o.exec.ok);
      o.execSig = xsig;
      clearRun(id);
      clearTimeout(_watchdogs[id]);
      o.running = false;
      if (ok) {
        o.exec = x; o.done = true; o.error = '';
        if (!hadOk) o.execSettled = false;   // stagger animation only on the FIRST success
      } else { o.exec = null; o.error = String(x.narration || 'Execution failed with no narration.'); }
      render(true);
      return;
    }
    /* recId 'command' (or none) → fill the oldest running command-bar job */
    if (!id || id === 'command') {
      for (var i = 0; i < S.cmds.length; i++) {
        if (S.cmds[i].status === 'run') {
          if (ok) { S.cmds[i].status = 'done'; S.cmds[i].exec = x; }
          else { S.cmds[i].status = 'error'; S.cmds[i].err = String(x.narration || 'Execution failed.'); }
          render();
          return;
        }
      }
    }
    /* unknown recId (or no home) — an honest standalone card; it NEVER steals
       a beat or a command card, so a flow echo bug stays visible */
    S.cmds.push({
      id: 'cmd-x' + (++_cmdSeq),
      cmd: (id && id !== 'command') ? '(flow-initiated · ' + id + ')' : '(flow-initiated)',
      status: ok ? 'done' : 'error', exec: ok ? x : null,
      err: ok ? '' : String(x.narration || '')
    });
    render();
  }

  /* ======================================================================
     §13 INBOUND MESSAGES
     ====================================================================== */
  function onState(p) {
    if (!p || typeof p !== 'object') return;
    _gotPanel = true;
    if (S.panel) {
      /* merge — a re-push must never blank sections we already show */
      var cur = S.panel;
      if ((!p.recommendations || !p.recommendations.length) && cur.recommendations && cur.recommendations.length) {
        p.recommendations = cur.recommendations;
      }
      if (!p.profile && cur.profile) p.profile = cur.profile;
      /* the zero-LLM provisional duo must never overwrite real ranked cards */
      if (p.comparison && p.comparison.provisional && cur.comparison && !cur.comparison.provisional) {
        p.comparison = cur.comparison;
      }
      if (!p.comparison && cur.comparison) p.comparison = cur.comparison;
      if ((!p.needs || !p.needs.length) && cur.needs && cur.needs.length) p.needs = cur.needs;
      if (!has(p.context) && has(cur.context)) p.context = cur.context;
      if ((!p.attempted || !p.attempted.length) && cur.attempted) p.attempted = cur.attempted;
      if ((!p.customerAsks || !p.customerAsks.length) && cur.customerAsks) p.customerAsks = cur.customerAsks;
      if (!has(p.draftMessage) && has(cur.draftMessage)) p.draftMessage = cur.draftMessage;
      if (!has(p.nextStepsIntro) && has(cur.nextStepsIntro)) p.nextStepsIntro = cur.nextStepsIntro;
    }
    saneProfile(p.profile);
    S.panel = p;
    if (p.profile && has(p.profile.nickname)) S.fname = p.profile.nickname.split(/\s+/)[0];
    else if (p.profile && has(p.profile.name)) S.fname = p.profile.name.split(/\s+/)[0];
    if (S.greet && p.recommendations && p.recommendations.length) dismissGreet();  // the panel is up → the greeting served its purpose
    if (p.recommendations && p.recommendations.length) {
      S.stages = [];                                   // the run landed — the stage strip is done
      if (_stageTimer) { clearTimeout(_stageTimer); _stageTimer = null; }
    }
    tendHero();   // composer sent (or re-sent) a heroPrompt → generate once per unique brief
    render();
  }

  function onSent(v) {
    if (!v) return;
    var pct = Math.max(0, Math.min(100, +v.pct || 0));
    if (!pct && !has(v.label)) return;
    var changed = !S.sent || +S.sent.pct !== pct || S.sent.label !== v.label;
    S.sent = {
      pct: pct,
      label: has(v.label) ? v.label : (S.sent && S.sent.label) || '',
      note: has(v.note) ? v.note : (S.sent && S.sent.note) || ''
    };
    var f = document.getElementById('mer-sent-fill');
    if (!f) { render(); return; }
    /* in-place patch — width + color animate together, label follows, pulse on change */
    f.style.width = pct + '%';
    f.style.background = sentColor(pct);
    f.setAttribute('data-w', pct);
    var lb = document.getElementById('mer-sent-lb'),
      pc = document.getElementById('mer-sent-pc'),
      nt = document.getElementById('mer-sent-note');
    if (lb) { lb.textContent = S.sent.label; lb.style.color = sentColor(pct); }
    if (pc) pc.textContent = pct + '%';
    if (nt && has(S.sent.note)) nt.textContent = S.sent.note;
    if (changed) { f.classList.remove('pulse'); void f.offsetWidth; f.classList.add('pulse'); }
    _lastSig = '';   // the DOM moved ahead of the signature — the next render must not be skipped
  }
  function animateSentIn() {
    /* first paint grows from 0 (CSS width transition); later renders land instantly */
    var f = document.getElementById('mer-sent-fill');
    if (!f) return;
    var w = f.getAttribute('data-w') + '%';
    if (_sentAnimated) { f.style.transition = 'none'; f.style.width = w; }
    else { _sentAnimated = true; setTimeout(function () { f.style.width = w; }, 60); }
  }

  function onConvo(c) {
    if (!c || typeof c !== 'object') return;
    S.convo = c.transcript || [];
    if (c.customer && has(c.customer.nickname)) S.fname = String(c.customer.nickname).split(/\s+/)[0];
    checkHeard();
  }

  var _stageTimer = null;
  function onStage(st) {
    if (!st || typeof st !== 'object' || !has(st.label)) return;
    var n = +st.n || (S.stages.length + 1);
    /* stage 1 of a fresh run resets a stale strip from an abandoned run */
    S.stages = S.stages.filter(function (s) { return +s.n < n; });
    S.stages.push({ n: n, total: +st.total || 0, label: String(st.label) });
    if (_stageTimer) clearTimeout(_stageTimer);
    /* a run that never lands its panel must not imply progress forever */
    _stageTimer = setTimeout(function () { S.stages = []; render(); }, 90000);
    render();
  }

  function onAsk(a) {
    if (!a || typeof a !== 'object') return;
    var pend = findAsk(String(a.askId || ''));
    if (pend) { pend.status = 'done'; pend.a = a; }
    else {
      /* flow-initiated (auto-gate) answer — dedupe by title */
      var dup = S.asks.some(function (x) { return x.a && x.a.title === a.title; });
      if (!dup) S.asks.push({ askId: String(a.askId || ('auto-' + (++_askSeq))), q: '', status: 'done', a: a });
    }
    render();
    scrollToBottom();
  }

  function onGreet(g) {
    g = String(g == null ? '' : g);
    /* strip ONE stray escape level if the live channel delivered it escaped */
    if (/\\["\\]/.test(g)) g = g.replace(/\\"/g, '"').replace(/\\\\/g, '\\');
    if (!has(g)) return;
    if (S.panel && S.panel.recommendations && S.panel.recommendations.length) return;  // panel already up
    S.greet = g;
    tendGreet();
  }
  function tendGreet() {
    if (!S.greet) { if (greetEl) { greetEl.remove(); greetEl = null; } return; }
    if (greetEl) return;
    greetEl = document.createElement('div');
    greetEl.className = 'greet';
    greetEl.innerHTML = '<span class="spark">' + IC_SPARK + '</span><div class="gx">' +
      '<div class="gl">Suggested greeting</div>' +
      '<div class="gt">' + esc(S.greet) + '</div>' +
      '<div class="gb"><button type="button" class="copy-btn" data-act="greet-copy">' + IC_COPY + 'Copy</button>' +
      '<button type="button" class="dismiss" data-act="greet-dismiss">Dismiss</button></div></div>';
    app.appendChild(greetEl);
  }
  function dismissGreet() {
    S.greet = '';
    if (greetEl) {
      var g = greetEl; greetEl = null;
      g.classList.add('bye');
      setTimeout(function () { g.remove(); }, 320);
    }
  }

  /* Router — payloads sit at data.metadata.<key> OR data.<key>. */
  function handle(data) {
    if (!data || typeof data !== 'object') return;
    var srcs = [];
    if (data.metadata && typeof data.metadata === 'object') srcs.push(data.metadata);
    srcs.push(data);
    srcs.forEach(function (src) {
      ing(src, 'merStateStr', function (v) { onState(jparse(v)); });
      ing(src, 'merExecStr', function (v) { onExec(jparse(v)); });
      ing(src, 'merAskStr', function (v) { onAsk(jparse(v)); });
      ing(src, 'merSentStr', function (v) { onSent(jparse(v)); });
      ing(src, 'merConvoStr', function (v) { onConvo(jparse(v)); });
      ing(src, 'merStageStr', function (v) { onStage(jparse(v)); });
      ing(src, 'merGreet', function (v) { onGreet(typeof v === 'string' ? v : String(v)); });
    });
  }
  function ing(src, key, fn) {
    var v = src[key];
    if (v == null || v === '') return;
    try { fn(v); }
    catch (e) {
      /* a malformed payload must be visible, not silent (real data or error) */
      S.cmds.push({ id: 'err-' + (++_cmdSeq), cmd: key, status: 'error', err: 'ERROR: could not parse ' + key + ' — ' + String(e) });
      render();
    }
  }

  /* ======================================================================
     §14 BOOT — window.MER, buffered-message drain, boot ping
     ====================================================================== */
  window.MER = {
    handle: handle,
    setState: function (p) { onState(typeof p === 'string' ? jparse(p) : p); }
  };

  window.addEventListener('message', function (e) { handle(e.data); });
  if (window.__merBuf && window.__merBuf.length) {
    var drained = window.__merBuf.splice(0);
    drained.forEach(function (d) { handle(d); });
  }
  window.__merBuf = [];

  render(true);   // paint the skeleton immediately (or whatever the buffer already delivered)

  /* Boot ping — asks the flow to rehydrate or build the briefing the moment the
     tile mounts; retries cover slow SDK injection, stops on the first panel. */
  (function bootPing(n) {
    if (_gotPanel || n > 6) return;
    postback({ action: 'boot' });
    setTimeout(function () { bootPing(n + 1); }, 2500);
  })(0);
})();
