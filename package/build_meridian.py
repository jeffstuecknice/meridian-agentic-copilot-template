# -*- coding: utf-8 -*-
"""
build_meridian.py — generates Package-Meridian-Copilot.zip (import via Cognigy "Upload Package").

ONE flow (Meridian_Copilot) on one Agent-Assist endpoint. The governing rule: LLMs decide; code
executes. The Approve postback carries a machine-readable action plan built by the composer, so
approved-action execution is a deterministic code + HTTP chain (~1-2s, zero LLM calls). One small
aiAgentJob (Meridian · Command Agent) handles free-text agent commands — the agentic-execution
showcase. Brain pipeline (gate mini -> native Knowledge Search -> policy analyst -> composer) is
inherited from the live-proven Skyway v4 build. See docs/ARCHITECTURE.md.

The zip BUNDLES the Meridian_Knowledge store record — import creates the store; upload the
knowledge/upload/*.txt docs into it afterwards (embeddings happen server-side).

Build:  python package/build_meridian.py     ->  package/Package-Meridian-Copilot.zip
"""
import hashlib
import json
import os
import shutil
import sys
import tempfile
import zipfile

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

# ── project constants (Meridian [Agentic Copilot] project, verified via Management API 2026-07-29) ──
PROJECT   = '6a6a822ebc1cab619429299e'
ORG       = '69c6a93834910b624e8f5fc2'
USER      = '69f8ea44d292925bcf7716c3'
# The TARGET PROJECT'S REAL locale — bundling a locale whose _id matches the project's is what makes
# node config attach on import (mgmt-api field notes; "empty imported nodes" root cause).
LOCALE    = '6a6a822ebc1cab61942929a0'
LOCALE_REF = '696d38ca-e3af-428b-a719-62a70fc418d9'
EPOCH     = 1785400000
DEBUG     = True

MOCK_API  = 'https://aicoe.3ddesignview.com/demo/cognigy_copilot/mock_api_meridian/meridian_api.php'
JS_URL    = 'https://aicoe.3ddesignview.com/demo/cognigy_copilot/mock_api_meridian'
TILE_ID   = 'meridian-copilot-tile'
DEMO_DEFAULT_CID = 'cust_101'

# Org-level Azure LLMs — referenceIds are stable across projects (assigned to Meridian 2026-07-29).
GPT54     = 'ae2167c7-9cec-4b7c-b10a-cb4c41e0e9e4'   # strong reasoner (policy analyst, command agent)
MINI      = 'dd516b18-1c07-48fe-b278-bad7bcfbac75'   # fast (gate, composer, knowledge answers)

PKG_NAME  = 'Package-Meridian-Copilot'
FLOW_NAME = 'Meridian_Copilot'
PFX       = 'eda1c0de0000000000aa'                    # 20-hex id namespace (+4-hex suffix = 24-hex _id)


def det_uuid(seed):
    h = hashlib.md5(('mer1:' + seed).encode()).hexdigest()
    return f'{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}'


def NID(s):
    x = PFX + s
    assert len(x) == 24, x
    return x


# ── resource ids ──
FLOW, CHART = NID('0010'), NID('0011')
FSET, FSTATE, ITG = NID('0012'), NID('0013'), NID('0014')
AGENT_ID  = NID('00b1')
AGENT_REF = det_uuid('meridian:agent:command')
KS_ID     = NID('00e1')
KS_REF    = det_uuid('meridian:knowledgestore')
FLOW_REF  = det_uuid(PFX + '_flow')

# ── node ids ──
START   = NID('0001'); ROUTER = NID('0002')
C_APPR  = NID('0003'); C_ASK  = NID('0004'); C_CMD = NID('0005'); DEF_R = NID('0006')
# approve (deterministic execute)
X_MAP = NID('0110'); X_SW = NID('0111'); X_GO = NID('0112'); X_BAD = NID('0113')
X_HTTP = NID('0114'); X_RES = NID('0115'); X_SEND = NID('0116')
# ask (knowledge answers — postback AND gate-question route converge here)
KA_PREP = NID('0120'); KA_KS = NID('0121'); KA_EXC = NID('0122'); KA_LLM = NID('0123')
KA_PARSE = NID('0124'); KA_SEND = NID('0125'); Q_PREP = NID('0126')
# command (the agentic-execution showcase)
CM_PREP = NID('0130'); CM_AG = NID('0131'); CM_FIN = NID('0132'); CM_DEF = NID('0133')
CT_HTTP = NID('0134'); CT_RES = NID('0135'); CT_ANS = NID('0136'); CM_SEND = NID('0137')
# default message turn
ONCE = NID('0150'); ONFIRST = NID('0151'); GRID = NID('0152'); TILE = NID('0153'); AFTERW = NID('0154')
GREET_P = NID('0155'); GREET_S = NID('0156')
CONVO_B = NID('0157'); CONVO_S = NID('0158'); REHYD = NID('0159')
CRM_P = NID('0160'); CRM_SW = NID('0161'); CRM_CSKIP = NID('0162'); CRM_CDEF = NID('0163')
CRM_H = NID('0164'); CRM_X = NID('0165')
PROD_P = NID('0166'); PROD_SW = NID('0167'); PROD_CSKIP = NID('0168'); PROD_CDEF = NID('0169')
PROD_H = NID('016a'); PROD_X = NID('016b')
PRE_P = NID('016c'); PRE_S = NID('016d')
RECOMP_SW = NID('0170'); RC_STOP = NID('0171'); RC_DEF = NID('0172')
GATE = NID('0173'); GATE_PN = NID('0174'); SENT_S = NID('0175')
ROUTE_SW = NID('0176'); RT_SKIP = NID('0177'); RT_Q = NID('0178'); RT_DEF = NID('0179')
POL_SW = NID('0180'); PL_RUN = NID('0181'); PL_DEF = NID('0182')
POLQ = NID('0183'); POL_KS = NID('0184'); POL_EXC = NID('0185'); POL_LLM = NID('0186'); POL_PARSE = NID('0187')
CMP_P = NID('0190'); CMP = NID('0191'); MERGE = NID('0192'); PUSH_SW = NID('0193')
PS_PUSH = NID('0194'); PS_DEF = NID('0195'); PUSH = NID('0196')
CMP2 = NID('0197'); MERGE2 = NID('0198'); PUSH_SW2 = NID('0199')
PS2_PUSH = NID('019a'); PS2_DEF = NID('019b'); PUSH2 = NID('019c')

# Command Agent tool node pairs (tool + map)
CMD_TOOLS_IDS = {
    'process_return_exception': (NID('01a1'), NID('01a2')),
    'apply_credit':             (NID('01a3'), NID('01a4')),
    'place_order':              (NID('01a5'), NID('01a6')),
    'send_receipt':             (NID('01a7'), NID('01a8')),
    'escalate_case':            (NID('01a9'), NID('01aa')),
}


# ═════════════════════════ JS code constants ═════════════════════════

# llmPromptV2 (context storage) wraps the completion in a RESULT OBJECT — dig the text out of
# any observed shape.
LLM_XTRACT = (
    "function xtract(raw){\n"
    "  if(raw==null)return null;\n"
    "  if(typeof raw==='string')return raw;\n"
    "  if(typeof raw==='object'){\n"
    "    if(typeof raw.text==='string')return raw.text;\n"
    "    if(typeof raw.result==='string')return raw.result;\n"
    "    try{var dr=raw.detailedResult;var ch=dr&&dr.choices&&dr.choices[0];\n"
    "      var mc=ch&&ch.message&&ch.message.content;if(typeof mc==='string')return mc;}catch(e){}\n"
    "    if(raw.result&&typeof raw.result==='object')return raw.result;\n"
    "  }\n"
    "  return raw;\n"
    "}\n")

# Deterministic profile builder — shared by the pre-panel and the merge (the LLM's profile is
# always overwritten from the CRM record; masking-proof via the merCrmStr JSON string).
PROFILE_JS = (
    "function buildProfile(rec,nick){\n"
    "  var sstr=function(v){return (typeof v==='string')?v:'';};\n"
    "  var tier=rec.tier||'';var badges=[];\n"
    "  if(tier)badges.push({t:tier+' Circle',cls:'plat'});\n"
    "  if(sstr(rec.valueNote).toLowerCase().indexOf('top')>=0)badges.push({t:'Top-10% Spend',cls:'good'});\n"
    "  return {initials:rec.initials||String(rec.name||'?').substr(0,2).toUpperCase(),name:rec.name||'',nickname:nick||'',tier:tier,\n"
    "    phone:sstr(rec.phoneDisplay)||sstr(rec.phone),occupation:sstr(rec.occupation),\n"
    "    meta:(tier?(tier+' Circle'):'')+(rec.memberSince?(' \\u00b7 member since '+rec.memberSince):''),\n"
    "    rightLabel:'Orders YTD',rightValue:String(rec.ordersYtd||''),\n"
    "    stats:[{k:'Lifetime spend',v:String(rec.lifetimeSpend||'')},{k:'Points',v:String(rec.pointsBalance||'')}],\n"
    "    badges:badges};\n"
    "}\n")

CONVO_BUILD = (
    "var aa=(input.data&&input.data._cognigy&&input.data._cognigy._agentAssist)||null;\n"
    "var isPayload=!!(aa&&aa.payload);\n"
    "var part=(input.data&&input.data.participant)||(aa&&aa.participant)||'';\n"
    "var pl=String(part).toLowerCase();\n"
    "var role=(pl.indexOf('agent')>=0)?'agent':'customer';\n"
    "var txt=(input.text||'').trim();\n"
    # CXone opens every chat with an automatic "Begin Conversation" customer message — keep the
    # turn (it triggers the pre-load) but keep the phrase out of the transcript.
    "if(/^begin conversation$/i.test(txt))txt='';\n"
    "var tx=context.merTx||[];\n"
    "var dup=false;\n"
    "if(!isPayload && txt && pl!=='system'){\n"
    "  var lastE=tx.length?tx[tx.length-1]:null;\n"
    "  if(lastE && lastE.role===role && lastE.text===txt){ dup=true; }\n"
    "  else { tx.push({role:role,text:txt}); if(tx.length>20) tx=tx.slice(-20); }\n"
    "}\n"
    "api.addToContext('merTx',tx,'simple');\n"
    "api.addToContext('merDupTurn',dup,'simple');\n"
    "api.addToContext('merLastPart',(role==='agent'&&txt)?'Agent':(part||''),'simple');\n"
    "var cc=(input.data&&input.data['copilot-customer-context'])||{};\n"
    "var cid=cc.customer_id||context.merCid||'';\n"
    "var nick=cc.customer_nickname||context.merNickFull||'';\n"
    "api.addToContext('merCid',cid,'simple');\n"
    "api.addToContext('merNickFull',nick,'simple');\n"
    "var conv={transcript:tx,customer:{customer_id:cid,nickname:nick}};\n"
    "var s=JSON.stringify(conv).replace(/\\\\/g,'\\\\\\\\').replace(/\"/g,'\\\\\"');\n"
    "api.addToContext('merConvoEsc',s,'simple');\n"
    # the tile pings {action:'boot'} on mount — it rides this default chain so rehydrate + the
    # briefing run; flag it so the recompute guard can stop a boot turn that has a cached panel.
    "var p0=aa&&aa.payload; if(typeof p0==='string'){try{p0=JSON.parse(p0);}catch(e){p0=null;}}\n"
    "api.addToContext('merBootTurn',!!(p0&&p0.action==='boot'),'simple');\n"
    + ("api.log('[MER][CONVO] part='+part+' payload='+isPayload+' role='+role+' turns='+tx.length+' cid='+cid+' txt='+txt.slice(0,40),'info');\n" if DEBUG else ""))

# Greeting fires ONLY before the first full panel exists, only on customer turns, and only
# extracts a name when the capture is actually capitalized in the ORIGINAL text ("I'm trying
# to pick a laptop" must NOT greet "Trying" — caught by the adversarial verify pass).
GREET_PREP = (
    "var t=String((input&&input.text)||''); var g='';\n"
    "var aa0=(input.data&&input.data._cognigy&&input.data._cognigy._agentAssist)||null;\n"
    "var part0=String((input.data&&input.data.participant)||(aa0&&aa0.participant)||'').toLowerCase();\n"
    "var isAgent0=part0.indexOf('agent')>=0;\n"
    "if((context.merPanelN||0)===0 && !isAgent0 && t.trim() && !/^begin conversation/i.test(t)){\n"
    "  var name='';\n"
    "  var pm=t.toLowerCase().match(/(?:this is|i am|i'm|my name is)\\s/);\n"
    "  if(pm){var rest=t.slice(pm.index+pm[0].length);\n"
    "    var nm=rest.match(/^\\s*([A-Z][a-zA-Z'\\u2019-]+)/);\n"
    "    if(nm)name=nm[1];}\n"
    "  g=name?('Thanks, '+name+' \\u2014 so glad you reached us. I can see your details and everything you told our assistant, so no need to repeat a thing.')"
    ":('Thanks for reaching out \\u2014 so glad you\\u2019re here. I can see your details and everything you told our assistant, so no need to repeat a thing.');\n"
    "}\n"
    "api.addToContext('merGreetEsc', g.replace(/\\\\/g,'\\\\\\\\').replace(/\"/g,'\\\\\"'), 'simple');\n"
    + ("api.log('[MER][GREET] '+(g||'(skip)'),'info');\n" if DEBUG else ""))

CRM_PREP = (
    "var tx=context.merTx||[];\n"
    "var chatName='';\n"
    # phrase match is case-insensitive (lowercased copy finds the trigger), the NAME must be
    # capitalized in the ORIGINAL casing — "This is Leo Martinez" re-targets, "i'm tired" doesn't.
    "for(var i=0;i<tx.length;i++){ var t0=String(tx[i].text||'');\n"
    "  var pm=t0.toLowerCase().match(/(?:this is|i am|i'm|my name is)\\s/);\n"
    "  if(pm){var rest=t0.slice(pm.index+pm[0].length);\n"
    "    var nm=rest.match(/^\\s*([A-Z][a-zA-Z'\\-]+(?:\\s+[A-Z][a-zA-Z'\\-]+)?)/);\n"
    "    if(nm){chatName=nm[1];break;}} }\n"
    "var cid=context.merCid||'';\n"
    # no identify signal yet (contact accept / tile boot) -> demo default so the briefing builds
    # on the very first turn; a name spoken in chat later still wins (name-first lookup).
    "if(!cid && !chatName){cid='" + DEMO_DEFAULT_CID + "';"
    + ("api.log('[MER][CRM>] no identify signal yet - using demo default '+cid,'info');" if DEBUG else "") + "}\n"
    "function q(v){return encodeURIComponent(v==null?'':String(v));}\n"
    "var url='" + MOCK_API + "?action=get_customer&customer_id='+q(cid)+'&name='+q(chatName);\n"
    "var crmSkip=(!!context.merCrm && url===context.merCrmUrl)?'skip':'go';\n"
    "api.addToContext('merCrmSkip',crmSkip,'simple');\n"
    "api.addToContext('merCrmUrl',url,'simple');\n"
    "var nick=String(context.merNickFull||'').split(/\\s+/)[0]||'';\n"
    "api.addToContext('merNick',nick,'simple');\n"
    "var msg='';\n"
    "for(var j=tx.length-1;j>=0;j--){ var r=String(tx[j].role||'').toLowerCase();\n"
    "  if(r==='customer'||r==='patron'||r==='contact'){ msg=String(tx[j].text||'').trim(); break; } }\n"
    "api.addToContext('merGateMsg',msg||'(no customer message yet)','simple');\n"
    "var tail=tx.slice(-6).map(function(e){return '['+(e.role||'?')+'] '+(e.text||'');}).join('\\n');\n"
    "api.addToContext('merTxTail',tail||'(none yet)','simple');\n"
    "var txs='';\n"
    "for(var i2=0;i2<tx.length;i2++){txs+='['+(tx[i2].role||'?')+'] '+(tx[i2].text||'')+'\\n';}\n"
    "api.addToContext('merTxStr',txs||'(no conversation captured yet)','simple');\n"
    "api.addToContext('merNickLine',(nick?('PREFERRED NAME (the customer gave this at chat start \\u2014 address them by it in ALL spoken lines): '+nick):''),'simple');\n"
    + ("api.log('[MER][CRM>] name='+chatName+' cid='+cid+' skip='+crmSkip,'info');\n" if DEBUG else ""))

CRM_POST = (
    "var raw=context.merCrmRaw||{};\n"
    "var r=(raw&&typeof raw.result==='object'&&raw.result)?raw.result:((raw&&typeof raw.body==='object'&&raw.body)?raw.body:raw);\n"
    "if(typeof r==='string'){try{r=JSON.parse(r);}catch(e){}}\n"
    "var rec=(r&&r.customer)||null;\n"
    "api.addToContext('merCrm',rec,'simple');\n"
    # masking-proof: context OBJECT values get PII-masked; the JSON STRING survives intact.
    "api.addToContext('merCrmStr',rec?JSON.stringify(rec,null,2):'(no customer identified yet)','simple');\n"
    + ("api.log('[MER][CRM<] '+(rec?(rec.name+' ('+rec.tier+')'):'NO RECORD'),'info');\n" if DEBUG else ""))

PROD_PREP = (
    "var url='" + MOCK_API + "?action=get_products';\n"
    "api.addToContext('merProdUrl',url,'simple');\n"
    "api.addToContext('merProdSkip',(!!context.merProdStr)?'skip':'go','simple');\n")

PROD_POST = (
    "var raw=context.merProdRaw||{};\n"
    "var r=(raw&&typeof raw.result==='object'&&raw.result)?raw.result:((raw&&typeof raw.body==='object'&&raw.body)?raw.body:raw);\n"
    "if(typeof r==='string'){try{r=JSON.parse(r);}catch(e){}}\n"
    "var prods=(r&&r.products)||[];\n"
    "api.addToContext('merProdStr',prods.length?JSON.stringify(prods,null,1):'(catalog unavailable)','simple');\n"
    + ("api.log('[MER][PROD<] '+prods.length+' products','info');\n" if DEBUG else ""))

# Keyed on merPanelN===0 (not just an empty merPanelEsc) so a composer double-failure
# mid-conversation can't overwrite the tile's last-good playbook with the skeleton.
PRE_PANEL_CODE = (
    PROFILE_JS +
    "if(!context.merPanelEsc && (context.merPanelN||0)===0 && context.merCrm){\n"
    "  var rec=null;try{var _rj=JSON.parse(context.merCrmStr||'');if(_rj&&typeof _rj==='object')rec=_rj;}catch(e){}\n"
    "  if(!rec)rec=context.merCrm||{};\n"
    "  var pre={profile:buildProfile(rec,context.merNick||''),\n"
    "    context:String(rec.escalation||''),\n"
    "    attempted:(rec.aiResolved||[]).map(function(t){return {t:t,k:'ok'};}),\n"
    "    needs:[],comparison:null,customerAsks:[],\n"
    "    nextStepsIntro:'The AI Agent is reasoning over Northlight policy and the catalog\\u2026',recommendations:[]};\n"
    "  var es=JSON.stringify(pre).replace(/\\\\/g,'\\\\\\\\').replace(/\"/g,'\\\\\"');\n"
    "  api.addToContext('merPanelEsc',es,'simple');\n"
    "  api.addToContext('merPreEsc',es,'simple');\n"
    + ("  api.log('[MER][PRE] instant pre-panel built','info');\n" if DEBUG else "")
    + "}else{api.addToContext('merPreEsc','','simple');}\n")

GATE_PROMPT = (
    "You are a routing classifier for a Northlight Electronics agent-assist copilot (consumer electronics retail). "
    "Read the CUSTOMER'S LATEST MESSAGE and choose EXACTLY one route:\n"
    "- \"request\": the customer wants the agent to DO something on their account/order — buy or order a product, decide/confirm which product to take, "
    "process or fix a return or refund, apply a credit or discount, price-match, change shipping, send a receipt (an action the agent performs).\n"
    "- \"question\": the customer asks for INFORMATION — product specs or comparisons (battery, weight, ports, displays), return/refund policy, "
    "loyalty-program benefits, shipping options and timing (answerable without performing an account action).\n"
    "- \"skip\": conversational filler with nothing to act on or look up — greetings, thanks, acknowledgments (hi, ok, thanks, yes, got it), small talk.\n"
    "If a message mixes filler with a real request/question, choose request or question. If genuinely unsure, prefer question. "
    "A message where the customer states their NEEDS or what matters to them (battery life, portability, budget, what they use it for) counts as \"request\" — it drives the recommendation.\n"
    "ALSO read the CUSTOMER'S emotional state from the RECENT CONVERSATION (weight the latest message most): "
    "pct 0-100 where 0-25 = upset/frustrated, 40-60 = neutral, 75-100 = pleased/delighted. "
    "label = a 2-3 word emotional label. note = one short clause naming the signal you read.\n"
    "Output STRICT JSON only: {\"route\":\"request|question|skip\", \"query\":\"<for question: a concise knowledge-search query; for request: a short phrase of what they want; otherwise empty>\", "
    "\"sentiment\":{\"pct\":<0-100 integer>, \"label\":\"<2-3 words>\", \"note\":\"<one short clause>\"}}\n\n"
    "RECENT CONVERSATION (latest last):\n{{context.merTxTail}}\n\n"
    "CUSTOMER'S LATEST MESSAGE:\n{{context.merGateMsg}}\n\nReturn the JSON now.")

GATE_PARSE = (
    LLM_XTRACT +
    "var raw=xtract(context.merGateRaw);\n"
    "var g=null;\n"
    "if(typeof raw==='string'){var s=raw.replace(/^```(?:json)?/m,'').replace(/```\\s*$/m,'').trim();\n"
    "  try{g=JSON.parse(s);}catch(e){var a1=s.indexOf('{'),b1=s.lastIndexOf('}');\n"
    "    if(a1>=0&&b1>a1){try{g=JSON.parse(s.slice(a1,b1+1));}catch(e2){}}}}\n"
    "else if(raw&&typeof raw==='object')g=raw;\n"
    "var route=(g&&['request','question','skip'].indexOf(g.route)>=0)?g.route:'skip';\n"
    "api.addToContext('merGate',{route:route,query:(g&&g.query)||''},'simple');\n"
    "var hasPanel=(context.merPanelN||0)>0;\n"
    "var decision=(route==='skip'&&hasPanel)?'skip':(route==='question'?'question':'go');\n"
    "if(context.merGateMsg==='(no customer message yet)'&&hasPanel)decision='skip';\n"
    "api.addToContext('merRoute',decision,'simple');\n"
    # live sentiment: push only when it actually shifted (>=5pts or a new label)
    "var sv=(g&&g.sentiment)||null;var sesc='';\n"
    "if(sv&&(+sv.pct>0||sv.label)){\n"
    "  var sp=Math.max(0,Math.min(100,Math.round(+sv.pct||0)));\n"
    "  var prev=context.merSent||null;\n"
    "  if(!prev||Math.abs((+prev.pct||0)-sp)>=5||String(sv.label||'')!==String(prev.label||'')){\n"
    "    var cur={pct:sp,label:String(sv.label||''),note:String(sv.note||'')};\n"
    "    api.addToContext('merSent',cur,'simple');\n"
    "    sesc=JSON.stringify(cur).replace(/\\\\/g,'\\\\\\\\').replace(/\"/g,'\\\\\"');\n"
    + ("    api.log('[MER][SENT] '+sp+'% '+String(sv.label||''),'info');\n" if DEBUG else "")
    + "  }\n"
    "}\n"
    "api.addToContext('merSentEsc',sesc,'simple');\n"
    + ("api.log('[MER][GATE] msg='+String(context.merGateMsg||'').slice(0,60)+' -> '+route+' -> '+decision,'info');\n" if DEBUG else ""))

POLICY_QUERY = (
    "var rec=null;try{var _rj=JSON.parse(context.merCrmStr||'');if(_rj&&typeof _rj==='object')rec=_rj;}catch(e){}\n"
    "if(!rec)rec=context.merCrm||{};\n"
    "var q=[rec.tier||'',(context.merGate&&context.merGate.query)||'',"
    "(rec.openReturn&&rec.openReturn.item)?('return window '+rec.openReturn.item):'',"
    "'return window loyalty tier benefits credit bundling recommendation guidance shipping'].join(' ').replace(/\\s+/g,' ').trim();\n"
    "api.addToContext('merPolQuery',q.slice(0,300),'simple');\n"
    + ("api.log('[MER][POLICY>] KS query='+q.slice(0,120),'info');\n" if DEBUG else ""))

# Defensive excerpt builder — tolerates every observed Knowledge-Search result shape.
def KS_EXCERPTS(hit_key, out_key, tag):
    return (
        "var h=input." + hit_key + "||context." + hit_key + "||{};\n"
        "var arr=(h&&h.result&&h.result.searches)||(h&&h.searches)||(h&&h.topK)||(h&&h.chunks)||(h&&h.results)||(Array.isArray(h)?h:[]);\n"
        "if(!Array.isArray(arr))arr=[];\n"
        "var out=[];\n"
        "for(var i=0;i<arr.length;i++){var s=arr[i]||{};\n"
        "  var name=s.name||s.title||s.sourceName||s.source||('excerpt '+(i+1));\n"
        "  var txt=s.summarized_answer||s.long_answer_sample||s.text||s.content||s.chunkText||'';\n"
        "  txt=String(txt).replace(/<[^>]+>/g,' ').replace(/\\s+/g,' ').trim();\n"
        "  if(txt)out.push('['+name+']\\n'+txt.slice(0,1800));\n"
        "}\n"
        "var blob=out.length?out.join('\\n\\n'):JSON.stringify(h).slice(0,6000);\n"
        "if(!blob||blob==='{}')blob='(no knowledge excerpts retrieved)';\n"
        "api.addToContext('" + out_key + "',blob,'simple');\n"
        + ("api.log('[MER][" + tag + "] KS hits='+arr.length+' blob='+blob.length,'info');\n" if DEBUG else ""))

POLICY_ANALYST_PROMPT = (
    "You are the Northlight Policy Analyst for a live agent-assist copilot. Determine WHAT NORTHLIGHT POLICY ALLOWS for this case, "
    "grounded ONLY in the POLICY EXCERPTS below (retrieved from the Meridian Knowledge Store) — never invent a rule, window, amount, or fee.\n"
    "Identify each distinct thing the customer wants or the situation requires (a product decision, a return outside the standard window, "
    "credits applied to a purchase, price match, shipping/receipt), PLUS findings the playbook needs even if not asked "
    "(e.g. the customer's loyalty-tier return window, whether a prior denial can be corrected, how credits combine at purchase, "
    "what the recommendation SOP requires).\n"
    "Output STRICT JSON only, with EXACTLY this shape and no prose:\n"
    "{\"findings\":[{\"topic\":\"<short>\", \"ruleId\":\"e.g. MER-POL-02 \\u00a73.1\", "
    "\"verdict\":\"allowed|capped|paid_addon|not_covered|escalate\", "
    "\"limit\":\"the CONCRETE figure/window for THIS customer's tier, e.g. '45-day accessory window' or '$189 store credit'\", "
    "\"quote\":\"ONE sentence copied VERBATIM from the excerpts that grants or caps this item — tier names, day counts and amounts exactly as "
    "written; never paraphrase or invent\", \"source\":\"that document's title/id, e.g. 'MER-POL-02 Northlight Circle Loyalty'\", "
    "\"action\":\"the exec registry call to use: one of process_return_exception/apply_credit/place_order/send_receipt/escalate_case with key params\"}], "
    "\"summary\":\"one line\"}\n"
    "verdicts: 'allowed' (within the agent's authority; recommend doing it), 'capped' (the ask exceeds policy; give the MAXIMUM in limit), "
    "'paid_addon' (the CUSTOMER pays; fee in limit), 'not_covered', 'escalate' (needs someone above the Care agent). "
    "Use the customer's TIER from the record for every window and cap. If the excerpts don't cover an item, verdict 'escalate' with quote ''.\n\n"
    "POLICY EXCERPTS (Meridian Knowledge Store):\n{{context.merPolExcerpts}}\n\n"
    "CUSTOMER RECORD (JSON):\n{{context.merCrmStr}}\n\n"
    "LIVE CONVERSATION:\n{{context.merTxStr}}\n\n"
    "Return the JSON now.")

POLICY_PARSE = (
    LLM_XTRACT +
    "var raw=xtract(context.merPolRaw);\n"
    "var a=null;\n"
    "if(typeof raw==='string'){var s=raw.replace(/^```(?:json)?/m,'').replace(/```\\s*$/m,'').trim();\n"
    "  try{a=JSON.parse(s);}catch(e){var a1=s.indexOf('{'),b1=s.lastIndexOf('}');\n"
    "    if(a1>=0&&b1>a1){try{a=JSON.parse(s.slice(a1,b1+1));}catch(e2){}}}}\n"
    "else if(raw&&typeof raw==='object')a=raw;\n"
    "if(!a||!a.findings)a={findings:[],summary:'(policy analysis unavailable \\u2014 be conservative; prefer escalate)'};\n"
    "api.addToContext('merPolicy',a,'simple');\n"
    "api.addToContext('merPolicyStr',JSON.stringify(a,null,2),'simple');\n"
    "api.addToContext('merPolicyForMsg',context.merGateMsg||'','simple');\n"
    + ("api.log('[MER][POLICY<] '+JSON.stringify(a).slice(0,400),'info');\n" if DEBUG else ""))

COMPOSER_PREP = (
    "var slim=context.merPanelSlim||[];\n"
    "api.addToContext('merPlaybookLine',(slim.length?('CURRENT PLAYBOOK \\u2014 these beats ALREADY EXIST on the panel. For any beat representing the same step, reuse the EXACT id and EXACT label verbatim; NEVER output a new beat that duplicates one of these under different wording: '+JSON.stringify(slim)):''),'simple');\n")

COMPOSER_PROMPT = (
    "You are the Northlight Agentic Copilot assisting a LIVE Care specialist named Riley (you never speak to the customer; you drive a side panel). "
    "The agent may apply any credit or exception whose authorizing policy clause is cited — recommend DOING what policy permits, never escalating what the agent can approve. "
    "Read the CUSTOMER RECORD, the PRODUCT CATALOG, the POLICY FINDINGS and the live conversation, then output the copilot panel as STRICT JSON with EXACTLY these keys:\n"
    "PREFERRED NAME: if a PREFERRED NAME is given below, ADDRESS THE CUSTOMER BY IT in EVERY conversational line you write (every say and sayDone, the greeting, the draftMessage) — first name only, warm and direct.\n"
    "profile: {initials, name, nickname, tier, meta, rightLabel, rightValue, stats:[{k,v}], badges:[{t,cls}]} — populate sensibly; a deterministic system overwrites it from the CRM record after you.\n"
    "context: one-paragraph situation summary (use the record's escalation + shopping fields so the customer never has to re-explain).\n"
    "needs: array of {id (stable slug e.g. 'battery'), label (2-4 words e.g. 'All-day battery'), quote (the customer's OWN words from the conversation or handoff that established this need — short verbatim fragment), weight ('high'|'med')}. ONLY needs the customer actually stated — never invent one. These render as chips above the comparison.\n"
    "comparison: null until the customer's needs are known; then {intro (one short line framing the ranking BY THEIR NEEDS), products:[EXACTLY the two catalog laptops, ranked: {sku, name, price (number), rank (1 or 2), tag (short e.g. 'Best fit for you'|'The power option'), headline (one sentence: why this rank FOR THIS CUSTOMER), fit:[{need (a needs id), verdict:'wins'|'close'|'trails', why (short, cite the spec: '18 hr vs 9 hr')}], honest (REQUIRED — the single strongest reason to pick the OTHER product, stated plainly; per MER-POL-05 a comparison with no tradeoffs is not permitted)}]}. Rank by the customer's STATED needs, not price or specs (MER-POL-05: fit beats basket size; never oversell — if the cheaper product fits better, it ranks first).\n"
    "attempted: array of {t, k:'ok'} — from the record's aiResolved plus anything the conversation shows already handled.\n"
    "customerAsks: array of {ask (SHORT phrase, one per distinct request), resolved (true ONLY if the transcript shows the AGENT addressed it), resolution (SHORT phrase of what was actually done; '' if not yet)}. RE-EVALUATE every turn.\n"
    "nextStepsIntro: one short sentence framing the guided playbook.\n"
    "recommendations: the ORDERED PLAYBOOK of conversational beats — a live, advancing checklist. The arc, in order:\n"
    "   1. (talk) GREET — the live agent's opening message (the customer was talking to the automated assistant and is now connected; the specialist speaks FIRST). Warm, by name, 'I can see your details and your conversation with our assistant' so they know they never repeat themselves.\n"
    "   2. (talk) EMPATHIZE — acknowledge the SPECIFIC situation. If the customer has voiced a frustration (e.g. a denied return), name it specifically and recognize their loyalty (tier/years). This is the beat whose say line the agent relays to trigger the heard moment.\n"
    "   3. (talk) WALK THE COMPARISON — present the ranked recommendation conversationally: which laptop fits their stated needs and the one honest reason they might still pick the other. The say line must cite THEIR words, never read like a spec sheet.\n"
    "   4. (action) FIX THE RETURN — when the POLICY FINDINGS show the customer's denied/open return is actually eligible (e.g. a loyalty-tier window), ONE beat that processes the return exception AND applies the refund as store credit: exec:{actions:[{action:'process_return_exception',params:{orderRef,item,amount,clause,reason}},{action:'apply_credit',params:{amount,unit:'USD',reason}}]}. Cite the clause in detail and policyQuote. Do NOT set offer — fixing their return needs no acceptance.\n"
    "   5. (action) PLACE THE ORDER — once the customer has chosen (or accepted the recommendation), ONE beat: exec:{actions:[{action:'place_order',params:{sku,creditApplied,shipMethod}}]} with offer:true (the customer's explicit yes authorizes the purchase; state the price AFTER credit in the say line). If the return credit exists, apply it here (creditApplied) and say so — MER-POL-02 \\u00a74.1 lets the credit apply in the same conversation.\n"
    "   6. (action) SEND THE RECEIPT — after the order: exec:{actions:[{action:'send_receipt',params:{name,detail,total,orderRef}}]} where detail is 'title \\u2014 REF|title \\u2014 REF' rows of what was done. Its sayDone tells the agent the receipt link is ready to paste into the chat.\n"
    "CUSTOMER REQUESTS — CRITICAL: whenever the CUSTOMER explicitly asks for something specific NOT already covered by a beat, ADD a dedicated (action) beat for THAT request at the END of the playbook, named after what they asked. Resolve it per the POLICY FINDINGS: allowed -> exec it; 'capped' -> do NOT auto-apply; OFFER the MAXIMUM policy permits (offer:true, say phrased as the offer, sayDone as the confirmation, exec at the cap). 'paid_addon' -> charge:true + chargeLabel + offer:true. 'escalate'/'not_covered'/no finding -> STILL add the beat with exec:{actions:[{action:'escalate_case',params:{summary,queue:'Care lead'}}]} and a say line that honestly says you're checking — never silently drop a request, never invent an outcome. Stable id derived from the request (e.g. 'req-price-match'). If a CURRENT PLAYBOOK list is provided, reuse those EXACT ids and labels for the same steps — never reword one into a near-duplicate.\n"
    "Each beat = {id (stable slug), label (short imperative), kind ('talk'|'action'), status ('done'|'active'|'pending'), offer (optional boolean — true ONLY when the customer must ACCEPT before it executes), confirmGated (optional boolean — true for a beat that must WAIT for the customer's explicit yes/no), charge (optional boolean), chargeLabel (paid add-ons only), "
    "say (ALWAYS populate — the EXACT customer-facing line the agent RELAYS for THIS beat, warm, 1-2 sentences, ready to paste. ACTION beats: the line said BEFORE doing it), "
    "sayDone (ACTION beats ONLY — the good-news line AFTER it succeeds, with the CONCRETE result: dollar amounts, the order total after credit, references; for send_receipt include that the link is ready to share), "
    "detail (one short internal why for the agent; cite the MER-POL rule id on action beats), "
    "running (action beats: present-tense policy-checking title, e.g. 'Checking policy & processing\\u2026'), "
    "substeps (action beats: MAX 3 short steps that LEAD with the policy check — cite the MER-POL rule id and what it permits, then the operational steps), "
    "exec (action beats ONLY: {actions:[{action:'process_return_exception'|'apply_credit'|'place_order'|'send_receipt'|'escalate_case', params:{...}}]} — an ARRAY, one entry per system call, in order; param shapes: process_return_exception={orderRef,item,amount,clause,reason}; apply_credit={amount,unit,reason}; place_order={sku,creditApplied,shipMethod}; send_receipt={name,detail,total,orderRef}; escalate_case={summary,queue}; ALL param values are strings), "
    "policyQuote (action beats that execute something ONLY — {ruleId, quote (the matching finding's quote VERBATIM — never reworded, never with changed numbers), source:'Northlight Policy Library \\u00b7 ' + the finding's source}. If the matching finding has no quote, omit policyQuote)}.\n"
    "COMPUTE STATUS BY READING THE TRANSCRIPT each turn: a TALK beat is 'done' if the AGENT's messages show they already expressed that beat's intent (match on meaning). A confirmGated beat is NEVER 'done' until the customer explicitly answered. ACTION beats are advanced by the tile — set status 'pending' unless the transcript clearly shows it handled. The FIRST not-done beat is 'active'; everything after is 'pending'. If the conversation just started, GREET is active.\n"
    "draftMessage: the single ready-to-send OUTBOUND message for AFTER the actions execute — warm, by preferred name, concrete results in one paragraph (what was returned, the credit, the order + total + ship date, the receipt link placeholder '<receipt link>').\n"
    "VOICE — every customer-facing line must be genuinely NICE, not merely polite: warm, human, personal. Open with their first name; take gracious ownership ('leave this with me', 'I've got you'); thank them for their loyalty where it fits; acknowledge the specific inconvenience with real empathy; deliver good news with genuine delight. No corporate stiffness, no exclamation-mark overload, never saccharine.\n"
    "BE TIGHT: say/sayDone max 2 sentences, detail one clause, substeps MAX 3, context max 3 sentences, needs max 5.\n"
    "Output ONLY the JSON object with EXACTLY these top-level keys and NO others: profile, context, needs, comparison, attempted, customerAsks, nextStepsIntro, recommendations, draftMessage. No prose, no code fences.\n\n"
    "POLICY FINDINGS (grounded in the Meridian Knowledge Store — your policy source of truth; cite its MER-POL rule ids; if a needed finding is missing, be conservative and escalate rather than inventing policy):\n{{context.merPolicyStr}}\n\n"
    "PRODUCT CATALOG (live from Northlight systems — SOURCE OF TRUTH for prices, specs, stock):\n{{context.merProdStr}}\n\n"
    "CUSTOMER RECORD (from the CRM — SOURCE OF TRUTH; the customer should NOT re-explain any of it):\n{{context.merCrmStr}}\n\n"
    "{{context.merNickLine}}\n"
    "{{context.merPlaybookLine}}\n"
    "Live conversation so far:\n{{context.merTxStr}}\n\n"
    "Produce the panel JSON now, grounded in the record, catalog, and policy findings above.")

MERGE_CODE = (
    LLM_XTRACT + PROFILE_JS +
    "var raw=xtract(context.merPanelRaw);\n"
    "var p=null;\n"
    "if(typeof raw==='string'){var s=raw.replace(/^```(?:json)?/m,'').replace(/```\\s*$/m,'').trim();\n"
    "  try{p=JSON.parse(s);}catch(e){var a1=s.indexOf('{'),b1=s.lastIndexOf('}');\n"
    "    if(a1>=0&&b1>a1){try{p=JSON.parse(s.slice(a1,b1+1));}catch(e2){}}}}\n"
    "else if(raw&&typeof raw==='object')p=raw;\n"
    "if(!p||!p.recommendations){api.log('[MER][MERGE] composer returned no usable panel \\u2014 skipping push','error');api.addToContext('merPanelEsc','','simple');}\n"
    "if(p&&p.recommendations){\n"
    "  var rec=null;try{var _rj=JSON.parse(context.merCrmStr||'');if(_rj&&typeof _rj==='object')rec=_rj;}catch(e){}\n"
    "  if(!rec)rec=context.merCrm||{};\n"
    "  p.profile=buildProfile(rec,context.merNick||'');\n"
    "  p.attempted=p.attempted||[];p.recommendations=p.recommendations||[];p.needs=p.needs||[];\n"
    "  // validate the LLM's 'done' claims on TALK beats against the REAL transcript\n"
    "  var vtx=context.merTx||[];var vab=[];\n"
    "  for(var vi=0;vi<vtx.length;vi++){var vr=String(vtx[vi].role||'').toLowerCase();\n"
    "    if(vr==='agent')vab.push(String(vtx[vi].text||'').toLowerCase().replace(/[^a-z0-9\\s]/g,' '));}\n"
    "  var vblob=vab.join(' | ');\n"
    "  for(var vj=0;vj<p.recommendations.length;vj++){var vb=p.recommendations[vj];\n"
    "    if(!vb||vb.status!=='done')continue;\n"
    "    if((vb.kind==='action')||vb.exec)continue;\n"
    "    if(vb.confirmGated===true){vb.status='active';continue;}\n"
    "    var vsay=String(vb.say||'').toLowerCase().replace(/[^a-z0-9\\s]/g,' ').replace(/\\s+/g,' ').trim();\n"
    "    var vtoks=vsay.split(' ').filter(function(w){return w.length>=4;});var vok=false;\n"
    "    if(vtoks.length>=3){var vh=0;for(var vk=0;vk<vtoks.length;vk++){if(vblob.indexOf(vtoks[vk])>=0)vh++;}vok=(vh/vtoks.length)>=0.5;}\n"
    "    else{vok=vsay.length>0&&vblob.indexOf(vsay)>=0;}\n"
    "    if(!vok)vb.status='pending';\n"
    "  }\n"
    "  var slim=[];for(var i=0;i<p.recommendations.length;i++){var r=p.recommendations[i];if(r&&r.id&&r.label)slim.push({id:r.id,label:r.label});}\n"
    "  api.addToContext('merPanelSlim',slim,'simple');\n"
    "  api.addToContext('merPanelN',p.recommendations.length,'simple');\n"
    "  var es=JSON.stringify(p).replace(/\\\\/g,'\\\\\\\\').replace(/\"/g,'\\\\\"');\n"
    "  api.addToContext('merPanelEsc',es,'simple');\n"
    + ("  api.log('[MER][PANEL] recs='+p.recommendations.length+' needs='+p.needs.length+' cmp='+(!!p.comparison),'info');\n"
       "  api.log('[MER][PANEL] '+JSON.stringify(p),'info');\n" if DEBUG else "")
    + "}\n")

PUSH_GUARD = "(context.merPanelEsc&&context.merPanelEsc.length)?'push':'skip'"

# ── deterministic execute (the Approve postback) ──
X_MAP_CODE = (
    "var aa=(input.data&&input.data._cognigy&&input.data._cognigy._agentAssist)||null;\n"
    "var p=aa&&aa.payload; if(typeof p==='string'){try{p=JSON.parse(p);}catch(e){p=null;}}\n"
    "p=p||{};\n"
    "var ex=p.exec||{}; var acts=ex.actions||ex||[];\n"
    "if(!Array.isArray(acts))acts=[];\n"
    "var rec=null;try{var _rj=JSON.parse(context.merCrmStr||'');if(_rj&&typeof _rj==='object')rec=_rj;}catch(e){}\n"
    "var cid=(rec&&rec.customer_id)||context.merCid||'';\n"
    "var clean=[];\n"
    "for(var i=0;i<acts.length&&i<6;i++){var a=acts[i]||{};\n"
    "  var nm=String(a.action||'');\n"
    "  if(['process_return_exception','apply_credit','place_order','send_receipt','escalate_case'].indexOf(nm)<0)continue;\n"
    "  clean.push({action:nm,params:(a.params&&typeof a.params==='object')?a.params:{}});\n"
    "}\n"
    "function q(v){return encodeURIComponent(v==null?'':String(v));}\n"
    "var url='';\n"
    "if(clean.length){url='" + MOCK_API + "?action=execute_batch&customerId='+q(cid)+'&actions='+q(JSON.stringify(clean));}\n"
    "api.addToContext('merExecRaw',null,'simple');\n"
    "api.addToContext('merExecUrl',url,'simple');\n"
    "api.addToContext('merExecRecId',String(p.recId||''),'simple');\n"
    + ("api.log('[MER][EXEC>] recId='+String(p.recId||'')+' actions='+clean.length+(url?'':' (INVALID \\u2014 no runnable actions)'),'info');\n" if DEBUG else ""))

X_RES_CODE = (
    "var recId=context.merExecRecId||'';\n"
    "var out={recId:recId,ok:false,narration:'',executed:[]};\n"
    "if(!context.merExecUrl){\n"
    "  out.narration='ERROR: the approval carried no runnable action plan \\u2014 nothing was executed.';\n"
    "  api.log('[MER][EXEC<] invalid approval payload','error');\n"
    "}else{\n"
    "  var raw=context.merExecRaw||{};\n"
    "  var r=(raw&&typeof raw.result==='object'&&raw.result)?raw.result:((raw&&typeof raw.body==='object'&&raw.body)?raw.body:raw);\n"
    "  if(typeof r==='string'){try{r=JSON.parse(r);}catch(e){}}\n"
    "  var exd=(r&&r.executed)||[];\n"
    "  if(!exd.length){out.narration='ERROR: the Northlight systems returned no execution result.';api.log('[MER][EXEC<] empty result','error');}\n"
    "  else{\n"
    "    out.ok=(r.ok===true);\n"
    "    for(var i=0;i<exd.length;i++){var e1=exd[i]||{};var d=e1.detail||{};var sum='';\n"
    "      if(e1.action==='process_return_exception'){sum='Return accepted \\u2014 '+(d.item||'item')+' \\u00b7 $'+(d.refundAmount||'')+' to store credit';}\n"
    "      else if(e1.action==='apply_credit'){sum='$'+(d.amount||'')+' credit applied to the order';}\n"
    "      else if(e1.action==='place_order'){sum=(d.product||d.sku||'Order')+' ordered \\u2014 total $'+(d.total!=null?d.total:'')+(d.shipDate?(' \\u00b7 '+d.shipDate):'');}\n"
    "      else if(e1.action==='send_receipt'){sum='Receipt ready \\u2014 '+(d.receiptUrl||'link');}\n"
    "      else if(e1.action==='escalate_case'){sum='Escalated to '+(d.queue||'a lead');}\n"
    "      else{sum=e1.ok?'Done':'Failed';}\n"
    "      out.executed.push({action:e1.action,ref:e1.ref||'',ok:(e1.ok===true),summary:sum,receiptUrl:(d.receiptUrl||undefined),total:(d.total!=null?d.total:undefined)});\n"
    "    }\n"
    "    out.narration='Executed '+out.executed.length+' action'+(out.executed.length>1?'s':'')+' with Northlight systems.';\n"
    "  }\n"
    "}\n"
    "var es=JSON.stringify(out).replace(/\\\\/g,'\\\\\\\\').replace(/\"/g,'\\\\\"');\n"
    "api.addToContext('merExecEsc',es,'simple');\n"
    + ("api.log('[MER][EXEC<] '+out.narration+' :: '+out.executed.map(function(e){return e.action+':'+e.ref;}).join(', '),'info');\n" if DEBUG else ""))

# ── knowledge answers (ask postback + gate question route) ──
KA_PREP_CODE = (
    "var aa=(input.data&&input.data._cognigy&&input.data._cognigy._agentAssist)||null;\n"
    "var p=aa&&aa.payload; if(typeof p==='string'){try{p=JSON.parse(p);}catch(e){p=null;}}\n"
    "p=p||{};\n"
    "api.addToContext('merAskQuery',String(p.query||p.q||'').slice(0,300)||'(empty question)','simple');\n"
    "api.addToContext('merAskId',String(p.askId||('ask-'+((context.merAskN||0)+1))),'simple');\n"
    "api.addToContext('merAskN',(context.merAskN||0)+1,'simple');\n"
    + ("api.log('[MER][ASK>] '+String(context.merAskQuery||''),'info');\n" if DEBUG else ""))

Q_PREP_CODE = (
    "api.addToContext('merAskQuery',String((context.merGate&&context.merGate.query)||context.merGateMsg||'').slice(0,300),'simple');\n"
    "api.addToContext('merAskId','auto-'+((context.merAskN||0)+1),'simple');\n"
    "api.addToContext('merAskN',(context.merAskN||0)+1,'simple');\n"
    + ("api.log('[MER][ASK>] (auto) '+String(context.merAskQuery||''),'info');\n" if DEBUG else ""))

KB_ANSWER_PROMPT = (
    "You are the Northlight knowledge assistant for a live Care agent. Answer the QUESTION for the agent, grounded ONLY in the "
    "POLICY EXCERPTS and the PRODUCT CATALOG below — never invent a spec, price, window, or rule. If neither source covers it, "
    "say so honestly and set escalate true.\n"
    "Output STRICT JSON only: {\"askId\":\"{{context.merAskId}}\", \"title\":\"<3-6 word topic>\", "
    "\"answer\":\"<2-3 sentences for the AGENT, concrete figures included>\", "
    "\"tell\":\"<ONE warm customer-facing line the agent can relay verbatim>\", "
    "\"sources\":[{\"id\":\"<MER-POL id or SKU>\",\"title\":\"<doc/product name>\"}], "
    "\"escalate\":<boolean>, \"escalateNote\":\"<short, only when escalate is true>\"}\n\n"
    "QUESTION:\n{{context.merAskQuery}}\n\n"
    "POLICY EXCERPTS (Meridian Knowledge Store):\n{{context.merAskExcerpts}}\n\n"
    "PRODUCT CATALOG (JSON):\n{{context.merProdStr}}\n\n"
    "CUSTOMER RECORD (JSON):\n{{context.merCrmStr}}\n\nReturn the JSON now.")

KA_PARSE_CODE = (
    LLM_XTRACT +
    "var raw=xtract(context.merAskRaw);\n"
    "var a=null;\n"
    "if(typeof raw==='string'){var s=raw.replace(/^```(?:json)?/m,'').replace(/```\\s*$/m,'').trim();\n"
    "  try{a=JSON.parse(s);}catch(e){var a1=s.indexOf('{'),b1=s.lastIndexOf('}');\n"
    "    if(a1>=0&&b1>a1){try{a=JSON.parse(s.slice(a1,b1+1));}catch(e2){}}}}\n"
    "else if(raw&&typeof raw==='object')a=raw;\n"
    "if(!a||!a.answer)a={askId:context.merAskId||'',title:'Knowledge lookup',answer:'ERROR: no grounded answer was produced for this question.',tell:'',sources:[],escalate:true,escalateNote:'knowledge answer unavailable'};\n"
    "a.askId=a.askId||context.merAskId||'';\n"
    "var s2=JSON.stringify(a).replace(/\\\\/g,'\\\\\\\\').replace(/\"/g,'\\\\\"');\n"
    "api.addToContext('merAskEsc',s2,'simple');\n"
    + ("api.log('[MER][ASK<] '+String(a.title||'')+' escalate='+(!!a.escalate),'info');\n" if DEBUG else ""))

# ── the Command Agent (free-text agent commands — the agentic-execution showcase) ──
CM_PREP_CODE = (
    "var aa=(input.data&&input.data._cognigy&&input.data._cognigy._agentAssist)||null;\n"
    "var p=aa&&aa.payload; if(typeof p==='string'){try{p=JSON.parse(p);}catch(e){p=null;}}\n"
    "p=p||{};\n"
    "var cmd=String(p.command||p.text||'').trim();\n"
    "var rec=null;try{var _rj=JSON.parse(context.merCrmStr||'');if(_rj&&typeof _rj==='object')rec=_rj;}catch(e){}\n"
    "api.addToContext('merCmdCid',(rec&&rec.customer_id)||context.merCid||'','simple');\n"
    "api.addToContext('merExecLog',[],'simple');\n"
    "var t='CUSTOMER RECORD (JSON):\\n'+(context.merCrmStr||'{}')+'\\n\\nPRODUCT CATALOG (JSON):\\n'+(context.merProdStr||'[]')+'\\n\\nThe live agent COMMANDS you to do this now:\\n'+(cmd||'(empty command)');\n"
    "api.addToContext('merCmdTask',t,'simple');\n"
    + ("api.log('[MER][CMD>] '+cmd.slice(0,80),'info');\n" if DEBUG else ""))

CMD_AGENT_RESOURCE = (
    "You are the Northlight Execution Agent supporting a LIVE Care specialist. You NEVER speak to the customer. "
    "When the specialist commands an action you carry it out by calling the matching Northlight system tools. "
    "Ground policy questions in the attached Meridian Knowledge Store (MER-POL documents).")

CMD_AGENT_INSTR = (
    "The live agent has COMMANDED the action in the user message and delegated EXECUTION to you. The action is NOT yet done — "
    "carrying it out is YOUR job, and the ONLY way to perform it is to CALL its matching tool. You MUST call a tool. Do NOT answer "
    "in plain text, do NOT claim an action is already handled, and do NOT reply 'DONE' until every commanded action has been "
    "performed by a tool call.\n"
    "Pick the matching tool, reading concrete values (amounts, order refs, SKUs, reasons) from the CUSTOMER RECORD, the PRODUCT "
    "CATALOG, and the command:\n"
    "- process_return_exception: accept a return under a policy exception (pass orderRef, item, amount, clause, reason).\n"
    "- apply_credit: apply a store credit to the order (pass amount as a string, unit 'USD', reason).\n"
    "- place_order: place a product order (pass sku, creditApplied as a string, shipMethod).\n"
    "- send_receipt: build the customer's receipt page + short link (pass name, detail as 'title \\u2014 REF|title \\u2014 REF' rows, total, orderRef).\n"
    "- escalate_case: anything beyond policy or beyond these tools (pass summary, queue).\n"
    "If the command is ambiguous or exceeds what MER-POL policy permits, use escalate_case honestly instead of guessing. "
    "Call ONE tool per commanded action, one after another for multi-part commands. Use the tools' REAL returned reference "
    "numbers — never invent one. ONLY after every commanded action has been executed via a tool call, reply with ONLY the word DONE.")

def CMD_MAP_CODE(kind, urlexpr):
    # merToolRaw is cleared before each call so an HTTP failure can never be narrated
    # as the PREVIOUS call's successful result.
    return ("var a=(input.aiAgent&&input.aiAgent.toolArgs)?input.aiAgent.toolArgs:{};\n"
            "function q(v){return encodeURIComponent(v==null?'':String(v));}\n"
            "var cid=context.merCmdCid||'';\n"
            "var url=" + urlexpr + ";\n"
            "api.addToContext('merToolRaw',null,'simple');\n"
            "api.addToContext('merToolExec',{kind:'" + kind + "',url:url,args:a},'simple');\n"
            "api.log('[MER][EXEC>] " + kind + " '+url,'info');\n")

CMD_TOOLS = [
    ('process_return_exception',
     'Accept a customer return under a policy exception. Pass orderRef, item, amount (number as string), clause (the MER-POL clause authorizing it), reason.',
     {'orderRef': {'type': 'string'}, 'item': {'type': 'string'},
      'amount': {'type': 'string', 'description': 'refund amount as a string, e.g. "189"'},
      'clause': {'type': 'string'}, 'reason': {'type': 'string'}},
     ['orderRef', 'item', 'amount', 'reason'], 'return',
     "'" + MOCK_API + "?action=process_return_exception&orderRef='+q(a.orderRef)+'&item='+q(a.item)+'&amount='+q(a.amount)+'&clause='+q(a.clause)+'&reason='+q(a.reason)+'&customerId='+q(cid)"),
    ('apply_credit',
     'Apply a store credit to the current order. Pass amount (number as string), unit "USD", reason.',
     {'amount': {'type': 'string', 'description': 'numeric amount as a string, e.g. "189"'},
      'unit': {'type': 'string'}, 'reason': {'type': 'string'}},
     ['amount', 'reason'], 'credit',
     "'" + MOCK_API + "?action=apply_credit&amount='+q(a.amount)+'&unit='+q(a.unit||'USD')+'&reason='+q(a.reason)+'&customerId='+q(cid)"),
    ('place_order',
     'Place a product order. Pass sku (from the catalog), creditApplied (number as string, 0 if none), shipMethod.',
     {'sku': {'type': 'string'}, 'creditApplied': {'type': 'string', 'description': 'credit amount as a string, e.g. "189" or "0"'},
      'shipMethod': {'type': 'string'}},
     ['sku'], 'order',
     "'" + MOCK_API + "?action=place_order&sku='+q(a.sku)+'&creditApplied='+q(a.creditApplied||'0')+'&shipMethod='+q(a.shipMethod||'expedited')+'&customerId='+q(cid)"),
    ('send_receipt',
     "Build the customer's receipt page and short link. Pass name, detail ('title \\u2014 REF|title \\u2014 REF' rows), total (e.g. '$1,110.00'), orderRef.",
     {'name': {'type': 'string'}, 'detail': {'type': 'string'}, 'total': {'type': 'string'}, 'orderRef': {'type': 'string'}},
     ['name', 'detail'], 'receipt',
     "'" + MOCK_API + "?action=send_receipt&name='+q(a.name)+'&detail='+q(a.detail)+'&total='+q(a.total)+'&orderRef='+q(a.orderRef)+'&customerId='+q(cid)"),
    ('escalate_case',
     'Escalate anything beyond policy or beyond the other tools. Pass summary and queue.',
     {'summary': {'type': 'string'}, 'queue': {'type': 'string'}},
     ['summary'], 'escalate',
     "'" + MOCK_API + "?action=escalate_case&summary='+q(a.summary)+'&queue='+q(a.queue||'Care lead')+'&customerId='+q(cid)"),
]

CT_RES_CODE = (
    "var raw=context.merToolRaw||{};\n"
    "var r=(raw&&typeof raw.result==='object'&&raw.result)?raw.result:((raw&&typeof raw.body==='object'&&raw.body)?raw.body:raw);\n"
    "if(typeof r==='string'){try{r=JSON.parse(r);}catch(e){}}\n"
    "function dec(s){try{return decodeURIComponent(String(s==null?'':s));}catch(e){return String(s==null?'':s);}}\n"
    "var k=(context.merToolExec&&context.merToolExec.kind)||'';var ref='';var c='';\n"
    "if(k==='return'){ref=r.rmaRef||'';c='Return accepted \\u2014 '+dec(r.item||'')+' \\u00b7 $'+(r.refundAmount||'')+' to store credit'+(ref?(' \\u00b7 '+ref):'');}\n"
    "else if(k==='credit'){ref=r.creditRef||'';c='$'+(r.amount||'')+' credit applied'+(r.reason?(' \\u2014 '+dec(r.reason)):'')+(ref?(' \\u00b7 '+ref):'');}\n"
    "else if(k==='order'){ref=r.orderRef||'';c=(r.product||r.sku||'Order')+' ordered \\u2014 total $'+(r.total!=null?r.total:'')+(r.shipDate?(' \\u00b7 '+r.shipDate):'')+(ref?(' \\u00b7 '+ref):'');}\n"
    "else if(k==='receipt'){ref=r.docRef||'';c='Receipt ready \\u2014 '+(r.receiptUrl||'link')+(ref?(' \\u00b7 '+ref):'');}\n"
    "else if(k==='escalate'){ref=r.handoffId||'';c='Escalated to '+dec(r.queue||'a lead')+(ref?(' \\u00b7 '+ref):'');}\n"
    "else{c=(r.ok?'Done':'Could not complete');}\n"
    # confirm/ref land inside the toolAnswer's double-quoted JSON template — keep them quote-safe
    "c=String(c).replace(/[\\\\\"]/g,\"'\");ref=String(ref).replace(/[\\\\\"]/g,\"'\");\n"
    "var log=context.merExecLog||[];log.push({action:k,ref:ref,summary:c,ok:(r.ok===true),receiptUrl:(r.receiptUrl||undefined)});api.addToContext('merExecLog',log,'simple');\n"
    "api.addToContext('merToolOut',{confirm:c,ref:ref,ok:(r.ok===true)},'simple');\n"
    "api.log('[MER][EXEC<] '+k+' :: '+c,'info');\n")

CM_FIN_CODE = (
    "var ex=context.merExecLog||[];\n"
    "var out={recId:'command',ok:ex.length>0&&ex.every(function(e){return e.ok;}),\n"
    "  narration:(ex.length?('Executed '+ex.length+' action'+(ex.length>1?'s':'')+' with Northlight systems.'):'ERROR: the command produced no executed actions.'),\n"
    "  executed:ex.map(function(e){return {action:e.action,ref:e.ref,ok:e.ok,summary:e.summary,receiptUrl:e.receiptUrl};})};\n"
    "var es=JSON.stringify(out).replace(/\\\\/g,'\\\\\\\\').replace(/\"/g,'\\\\\"');\n"
    "api.addToContext('merExecEsc',es,'simple');\n"
    + ("api.log('[MER][CMD<] '+out.narration,'info');\n" if DEBUG else ""))


# ═════════════════════════ config factories ═════════════════════════

def http_cfg(url_tpl, context_key):
    return {'type': 'GET', 'url': url_tpl, 'headers': '{}', 'payloadType': 'none', 'payloadText': '',
            'payloadJSON': '', 'payloadFormData': [], 'storeLocation': 'context', 'inputKey': 'input',
            'contextKey': context_key, 'authType': 'noAuth', 'basicConnection': '', 'apiKeyAuthKeyConnection': '',
            'apiKeyXKeyConnection': '', 'oAuth2Connection': '', 'async': False, 'cache': False, 'cacheExpiry': '0',
            'timeout': 8000, 'retryAttempts': 0, 'storeResponseHeaders': False, 'allowSelfSigned': True,
            'errorLogging': True, 'debugLogging': True, 'abortOnError': False, 'logWarning': True}


def llm_cfg(provider, prompt, context_key, *, temp=0.0, max_tokens=1000, timeout=30000):
    # usePromptMode=True: with prompt mode OFF, llmPromptV2 injects the SESSION CHAT TRANSCRIPT
    # (full of tool-loop "DONE" replies) — everything the model needs is in the prompt itself.
    return {'llmProviderReferenceId': provider, 'prompt': prompt, 'chatTranscriptSteps': 0,
            'usePromptMode': True, 'samplingMethod': 'temperature', 'temperature': temp, 'topP': 1,
            'maxTokens': max_tokens, 'frequencyPenalty': 0, 'presencePenalty': 0, 'useStop': False, 'stop': '',
            'timeout': timeout, 'storeLocation': 'context', 'immediateOutput': False,
            'inputKey': context_key, 'contextKey': context_key,
            'streamStopTokens': ['.', '!', '?', '\n'], 'streamStopTokenOverrides': [], 'streamDescription': '',
            'streamStoreCopyInInput': False, 'debugLogTokenCount': DEBUG, 'debugLogRequestAndCompletion': DEBUG,
            'debugDescription': '', 'responseFormat': 'default', 'seed': '', 'jsonStreamWarning': '',
            'customModelOptions': {}, 'customRequestOptions': {}, 'logErrorToSystem': False,
            'errorHandling': 'continue', 'errorMessage': '', 'errorHandlingGotoTarget': '',
            'toolChoice': 'auto', 'useStrict': False, 'processImages': False,
            'transcriptImageHandling': 'minify', 'debugLogToolDefinitions': False, 'debugLogLLMLatency': DEBUG,
            'useTextAlternativeForLLM': False, 'advancedLogging': False, 'conditionForLogging': '',
            'loggingCustomData': '', 'loggingHeaders': '', 'loggingWebhookUrl': ''}


def ks_cfg(search_expr, store_key, *, topk=5):
    # Native Knowledge-Search node ('searchExtractOutput', mode 's'). FULL config — truncated
    # clones crash at runtime ("Cannot read properties of undefined (reading 'replace')").
    return {'mode': 's', 'knowledgeStoreId': KS_REF, 'followUpDetection': 'none',
            'followUpDetectionSteps': 2, 'topK': topk, 'searchString': search_expr,
            'searchStoreLocation': 'input', 'searchStoreLocationInputKey': store_key,
            'searchStoreLocationContextKey': store_key,
            'searchSourceTags': '', 'searchSourceTagsFilterOp': 'and',
            'prompt': 'Answer the question according to the sources found in the knowledgebase.\n'
                      'Sources: @foundDocuments\nQuestion: @userInput\nAnswer:',
            'temperature': 0.7, 'maxTokens': 1000, 'frequencyPenalty': 0, 'presencePenalty': 0,
            'useStop': False, 'stop': [], 'timeout': 5000,
            'storeLocation': 'input', 'inputKey': 'promptResult', 'contextKey': 'promptResult',
            'outputMode': 'text', 'outputFallback': 'Sorry, I could not find an answer to your question.',
            'errorHandling': 'continue',
            'timeoutMessage': "I'm very sorry, but I am having some technical difficulties right now. Please try again.",
            'errorHandlingGotoTarget': '', 'streamStopTokens': ['.', '!', '?'], 'streamDescription': '',
            'debugLogTokenCount': False, 'debugLogRequestAndCompletion': False, 'debugDescription': '',
            'searchStringDescription': '', 'customModelOptions': {}, 'customRequestOptions': {}}


def aiagent_cfg(name, instructions, context_key, *, max_tokens=2000, context_injection=''):
    # The task + record reach the agent via memoryContextInjection — mutating input.text in a
    # code node does NOT change what aiAgentJob sees.
    return {'aiAgent': AGENT_REF, 'llmProviderReferenceId': GPT54, 'name': name,
            'description': name, 'instructions': instructions, 'toolChoice': 'auto', 'useStrict': False,
            'memoryType': 'inherit', 'selectedProfileFields': '', 'memoryContextInjection': context_injection,
            'knowledgeSearchBehavior': 'onDemand', 'knowledgeSearchAlwaysWarning': '', 'knowledgeSearchTags': '',
            'knowledgeSearchTagsFilterOp': 'and', 'knowledgeSearchAiAgentKnowledge': True,
            'knowledgeSearchJobKnowledge': False, 'knowledgeSearchGenerateSearchPrompt': False,
            'knowledgeSearchTopK': 3, 'knowledgeSearchJobStore': '', 'apiVersion': '1.0', 'timeoutInMs': 20000,
            'maxTokens': max_tokens, 'temperature': 0, 'useTextAlternativeForLLM': True, 'advancedLogging': False,
            'loggingWebhookUrl': '', 'loggingCustomData': '', 'loggingHeaders': '{}', 'conditionForLogging': '',
            'logErrorToSystem': False, 'storeErrorInInput': True, 'errorHandling': 'continue', 'errorMessage': '',
            'errorHandlingGotoTarget': {'flow': '', 'node': ''}, 'debugLogTokenCount': DEBUG,
            'debugLogSystemPrompt': DEBUG, 'debugLogToolDefinitions': DEBUG, 'debugConfig': True,
            'debugLogLLMLatency': DEBUG, 'debugResult': DEBUG, 'outputImmediately': False,
            'storeLocation': 'context', 'contextKey': context_key, 'inputKey': context_key,
            'streamStopTokens': ['.', '!', '?', '\n'], 'streamStoreCopyInInput': True,
            'customModelOptions': {}, 'customRequestOptions': {}, 'processImages': False,
            'transcriptImageHandling': 'minify', 'voiceSetting': 'inheritFromAiAgent', 'ttsVoice': '',
            'ttsLanguage': '', 'ttsVendor': '', 'ttsModel': '', 'ttsLabel': '', 'ttsDisableCache': False}


def _p(props, required):
    return json.dumps({'type': 'object', 'properties': props, 'required': required})


# ═════════════════════════ build ═════════════════════════

def build():
    # --no-ks: omit the bundled knowledgeStore record. Use for RE-imports into a project whose
    # Meridian_Knowledge store already exists (same-project imports remap _ids, so re-shipping the
    # store would DUPLICATE it; the KS-search nodes bind by referenceId, which survives).
    include_ks = '--no-ks' not in sys.argv
    build_root = tempfile.mkdtemp(prefix='merbuild_')
    pkg = os.path.join(build_root, PKG_NAME)
    folders = ['flow', 'chart', 'nodeData', 'locale', 'flowSettings', 'flowState',
               'intentTrainGroup', 'aiAgent'] + (['knowledgeStore'] if include_ks else [])
    for d in folders:
        os.makedirs(os.path.join(pkg, d))

    def dump(sub, _id, obj):
        with open(os.path.join(pkg, sub, _id), 'w', encoding='utf-8') as f:
            json.dump(obj, f, separators=(',', ':'), ensure_ascii=False)

    with open(os.path.join(pkg, 'index.json'), 'w', encoding='utf-8') as f:
        json.dump({'cognigyVersion': '2026.13.1', 'type': 'package', 'createdAt': '2026-07-29T00:00:00.000Z',
                   'name': PKG_NAME, 'description': 'Meridian — the golden agentic-copilot template. ONE flow: '
                   'router + gate + native Knowledge Search + policy analyst + composer, deterministic Approve '
                   'execution (LLMs decide; code executes), and one Command Agent for free-text agent commands. '
                   'Bundles the Meridian_Knowledge store (upload the MER-POL .txt docs after import).',
                   'resourcesHash': '0' * 40}, f, separators=(',', ':'), ensure_ascii=False)

    # locale — the TARGET PROJECT'S REAL locale ids, so localized node config attaches on import
    dump('locale', LOCALE, {'_id': LOCALE, 'referenceId': LOCALE_REF, 'name': 'en-US', 'primary': True,
                            'nluLanguage': 'en-US', 'projectReference': PROJECT, 'organisationReference': ORG,
                            'createdAt': EPOCH, 'lastChanged': EPOCH, 'createdBy': USER, 'lastChangedBy': USER})

    # knowledge store — bundled so ONE import creates it; upload knowledge/upload/*.txt afterwards
    if include_ks:
        dump('knowledgeStore', KS_ID, {'_id': KS_ID, 'referenceId': KS_REF, 'name': 'Meridian_Knowledge',
                                       'language': 'en-US', 'status': 'ready', 'documents': [],
                                       'projectReference': PROJECT, 'organisationReference': ORG,
                                       'createdBy': USER, 'createdAt': EPOCH,
                                       'lastChangedBy': USER, 'lastChanged': EPOCH})

    # flow + chart scaffolding
    dump('flow', FLOW, {'_id': FLOW, 'referenceId': FLOW_REF, 'name': FLOW_NAME,
                        'context': {}, 'attachedFlows': [],
                        'localizedData': [{'attachedLexiconReferences': [], 'localeReference': LOCALE}],
                        'img': '', 'projectReference': PROJECT, 'organisationReference': ORG,
                        'createdAt': EPOCH, 'lastChanged': EPOCH, 'createdBy': USER, 'lastChangedBy': USER,
                        'chartReference': CHART})
    dump('flowSettings', FSET, {'_id': FSET, 'continueExecutionAfterAttachedFlow': False,
         'continueExecutionAfterDefaultReply': False, 'continueExecutionAfterNegativeConfirmation': False,
         'passDefaultRepliesIntoFlow': False, 'flowIntentMappingOrder': 'joint',
         'useAttachedFlowThresholds': True, 'useAttachedFlowContinueAfterDefaultReply': True,
         'useAttachedFlowPassDefaultRepliesIntoFlow': True, 'implicitSlotParsing': 'disabled',
         'useAttachedFlowImplicitSlotParsing': False, 'useIntentDefaultRepliesAsExamples': True,
         'flowReference': FLOW, 'projectReference': PROJECT, 'organisationReference': ORG,
         'lexiconSlotsWithSubMatches': False, 'localeSettings': []})
    dump('flowState', FSTATE, {'_id': FSTATE, 'name': 'default', 'type': 'blacklist', 'isDefault': True,
         'referenceId': det_uuid(FSTATE), 'intentReferences': [], 'flowReference': FLOW,
         'projectReference': PROJECT, 'organisationReference': ORG, 'createdAt': EPOCH,
         'lastChanged': EPOCH, 'createdBy': USER, 'lastChangedBy': USER})
    dump('intentTrainGroup', ITG, {'_id': ITG, 'nluOptions': {}, 'referenceId': det_uuid(ITG),
         'lastChanged': EPOCH, 'localeReference': LOCALE, 'lastChangedBy': USER, 'lastTrainedAt': 0,
         'lastTrainedBy': None, 'flowReference': FLOW, 'projectReference': PROJECT,
         'organisationReference': ORG, 'lexiconsInServiceMatcher': True,
         'lastRelevantChangeAt': EPOCH, 'lastRelevantChangeBy': None})

    # the Command Agent resource (knowledge store attached)
    dump('aiAgent', AGENT_ID, {'_id': AGENT_ID, 'referenceId': AGENT_REF, 'name': 'Meridian · Command Agent',
         'description': 'Meridian · Command Agent', 'image': 'default-avatar:3', 'imageOptimizedFormat': True,
         'knowledgeReferenceId': KS_REF,
         'speakingStyle': {'formality': 'balanced', 'completeness': 'balanced'},
         'voiceConfigs': {'ttsVoice': '', 'ttsLanguage': '', 'ttsVendor': 'none', 'ttsModel': '',
                          'ttsLabel': '', 'ttsDisableCache': False}, 'enableVoiceConfigs': False,
         'safetySettings': {'avoidHarmfulContent': True, 'avoidUngroundedContent': True,
                            'avoidCopyrightInfringements': True, 'preventJailbreakAndManipulation': True},
         'instructions': CMD_AGENT_RESOURCE, 'enableAutoLanguageDetection': True,
         'contactProfilesOption': 'completeProfile', 'contactProfilesSelected': [],
         'projectReference': PROJECT, 'organisationReference': ORG,
         'createdBy': USER, 'createdAt': EPOCH, 'lastChangedBy': USER, 'lastChanged': EPOCH})

    # ── nodes ──
    def node(_id, ntype, label, config, *, entry=False, disabled=False, ext='@cognigy/basic-nodes'):
        return {'_id': _id, 'referenceId': det_uuid(_id), 'type': ntype, 'extension': ext,
                'label': label, 'comment': '', 'commentColor': '', 'analyticsLabel': None,
                'isEntryPoint': entry, 'isDisabled': disabled, 'mock': {'isEnabled': False, 'code': ''},
                'localizedData': [{'config': config, 'preview': '', 'localeReference': LOCALE}],
                'chartReference': CHART, 'resourceReference': FLOW,
                'projectReference': PROJECT, 'organisationReference': ORG}

    def code_node(_id, label, code):
        return node(_id, 'code', label, {'code': code, 'hasError': False, 'transpiled': code})

    tile_html = (
        '<!doctype html><html><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1"><title>AI Agent</title>'
        "<style>html,body{margin:0;height:100%;background:#fff;font-family:'Segoe UI',system-ui,-apple-system,sans-serif}"
        ".mrb{display:flex;align-items:center;justify-content:center;height:100%;color:#64748B;font-size:12.5px;font-weight:600;text-align:center;padding:0 22px}"
        ".mrb .sp{width:20px;height:20px;border:3px solid #CBD5E1;border-top-color:#0F2A4A;border-radius:50%;animation:mrbsp .7s linear infinite;margin-right:9px;flex:0 0 auto}"
        "@keyframes mrbsp{to{transform:rotate(360deg)}}</style></head>"
        '<body><div class="mrb"><span class="sp"></span>Loading the AI Agent…</div>'
        "<script>(function(){window.__merBuf=window.__merBuf||[];"
        'window.addEventListener("message",function(e){if(!window.MER)window.__merBuf.push(e.data);});'
        'var s=document.createElement("script");s.src="' + JS_URL + '/meridian_tile.js?v="+Date.now();'
        's.onerror=function(){document.body.innerHTML=\'<div class="mrb">Couldn\\\'t load the AI Agent panel. Refresh to retry.</div>\';};'
        "document.body.appendChild(s);})();</script></body></html>")

    N = []  # (id, nodeObj)
    N.append((START, node(START, 'start', 'Start', {}, entry=True)))
    N.append((ROUTER, node(ROUTER, 'switch', 'Route tile action',
        {'switch': {'type': 'cognigyScript',
                    'operator': '(input.data&&input.data._cognigy&&input.data._cognigy._agentAssist&&'
                                'input.data._cognigy._agentAssist.payload&&'
                                'input.data._cognigy._agentAssist.payload.action)||""'},
         'intentLevel': 'input.intent', 'useStrict': ''})))
    N.append((C_APPR, node(C_APPR, 'case', 'approve', {'case': {'value': 'approve'}})))
    N.append((C_ASK, node(C_ASK, 'case', 'ask', {'case': {'value': 'ask'}})))
    N.append((C_CMD, node(C_CMD, 'case', 'command', {'case': {'value': 'command'}})))
    N.append((DEF_R, node(DEF_R, 'default', 'Default (message turn)', {})))

    # approve — LLMs decide; code executes
    N.append((X_MAP, code_node(X_MAP, 'Approve - map action plan', X_MAP_CODE)))
    N.append((X_SW, node(X_SW, 'switch', 'Plan valid?',
        {'switch': {'type': 'cognigyScript',
                    'operator': "(context.merExecUrl&&context.merExecUrl.length)?'go':'bad'"},
         'intentLevel': 'input.intent', 'useStrict': ''})))
    N.append((X_GO, node(X_GO, 'case', 'go', {'case': {'value': 'go'}})))
    N.append((X_BAD, node(X_BAD, 'default', 'invalid plan', {})))
    N.append((X_HTTP, node(X_HTTP, 'httpRequest', 'Execute - Northlight systems (batch)',
                           http_cfg('{{context.merExecUrl}}', 'merExecRaw'))))
    N.append((X_RES, code_node(X_RES, 'Execute - collect refs', X_RES_CODE)))
    N.append((X_SEND, node(X_SEND, 'sendData', 'Push exec result to tile',
                           {'tileId': TILE_ID, 'json': '{"merExecStr":"{{context.merExecEsc}}"}'})))

    # ask — knowledge answers
    N.append((KA_PREP, code_node(KA_PREP, 'Ask - read question', KA_PREP_CODE)))
    N.append((KA_KS, node(KA_KS, 'searchExtractOutput', 'Knowledge Search (ask)',
                          ks_cfg('{{context.merAskQuery}}', 'merAskHits'))))
    N.append((KA_EXC, code_node(KA_EXC, 'Ask - build excerpts', KS_EXCERPTS('merAskHits', 'merAskExcerpts', 'ASK'))))
    N.append((KA_LLM, node(KA_LLM, 'llmPromptV2', 'KB answer (mini)',
                           llm_cfg(MINI, KB_ANSWER_PROMPT, 'merAskRaw', temp=0.0, max_tokens=600, timeout=20000))))
    N.append((KA_PARSE, code_node(KA_PARSE, 'Ask - parse answer', KA_PARSE_CODE)))
    N.append((KA_SEND, node(KA_SEND, 'sendData', 'Push KB answer to tile',
                            {'tileId': TILE_ID, 'json': '{"merAskStr":"{{context.merAskEsc}}"}'})))
    N.append((Q_PREP, code_node(Q_PREP, 'Question - stage query', Q_PREP_CODE)))

    # command — the agentic-execution showcase
    N.append((CM_PREP, code_node(CM_PREP, 'Command - build task', CM_PREP_CODE)))
    N.append((CM_AG, node(CM_AG, 'aiAgentJob', 'Command Agent',
        aiagent_cfg('Meridian · Command Agent', CMD_AGENT_INSTR, 'merCmdAgent', max_tokens=2000,
                    context_injection='CURRENT TASK (do this now):\n{{context.merCmdTask}}'))))
    N.append((CM_DEF, node(CM_DEF, 'aiAgentJobDefault', 'Default', {}, disabled=True)))
    for tid, desc, props, req, kind, urlexpr in CMD_TOOLS:
        t_node, c_node = CMD_TOOLS_IDS[tid]
        N.append((t_node, node(t_node, 'aiAgentJobTool', tid + ' Tool',
             {'toolId': tid, 'description': desc, 'useParameters': True, 'parameters': _p(props, req),
              'debugMessage': True, 'condition': ''})))
        N.append((c_node, code_node(c_node, 'Map - ' + tid, CMD_MAP_CODE(kind, urlexpr))))
    N.append((CT_HTTP, node(CT_HTTP, 'httpRequest', 'Execute - call Northlight system',
                            http_cfg('{{context.merToolExec.url}}', 'merToolRaw'))))
    N.append((CT_RES, code_node(CT_RES, 'Execute - read result', CT_RES_CODE)))
    N.append((CT_ANS, node(CT_ANS, 'aiAgentToolAnswer', 'Answer - executed',
         {'answer': 'Executed: {{context.merToolOut.confirm}}. If more commanded actions remain, call the next tool now; '
          'otherwise reply with ONLY the word DONE.', 'debugToolAnswer': True, 'maxLoops': 10,
          'toolAnswer': '{"ok":true,"confirm":"{{context.merToolOut.confirm}}","ref":"{{context.merToolOut.ref}}"}'})))
    N.append((CM_FIN, code_node(CM_FIN, 'Command - finalize', CM_FIN_CODE)))
    N.append((CM_SEND, node(CM_SEND, 'sendData', 'Push command result to tile',
                            {'tileId': TILE_ID, 'json': '{"merExecStr":"{{context.merExecEsc}}"}'})))

    # default message turn
    N.append((ONCE, node(ONCE, 'once', 'Once (tile mount)', {})))
    N.append((ONFIRST, node(ONFIRST, 'onFirstExecution', 'On first execution', {})))
    N.append((GRID, node(GRID, 'setAgentAssistGrid', 'Set Layout',
         {'agentAssistConfig': {'grid': {'columns': 1, 'rows': 8, 'gap': 8},
                                'tiles': {TILE_ID: {'x': 1, 'y': 1, 'columns': 1, 'rows': 8}}},
          'backgroundSelector': 'default'})))
    N.append((TILE, node(TILE, 'setHTMLTile', 'Copilot Tile', {'tileId': TILE_ID, 'htmlContent': tile_html})))
    N.append((AFTERW, node(AFTERW, 'afterwards', 'Afterwards', {})))
    N.append((GREET_P, code_node(GREET_P, 'Greeting - instant ack', GREET_PREP)))
    N.append((GREET_S, node(GREET_S, 'sendData', 'Push greeting',
                            {'tileId': TILE_ID, 'json': '{"merGreet":"{{context.merGreetEsc}}"}'})))
    N.append((CONVO_B, code_node(CONVO_B, 'Build conversation', CONVO_BUILD)))
    N.append((CONVO_S, node(CONVO_S, 'sendData', 'Push conversation',
                            {'tileId': TILE_ID, 'json': '{"merConvoStr":"{{context.merConvoEsc}}"}'})))
    N.append((REHYD, node(REHYD, 'sendData', 'Rehydrate panel (cached)',
                          {'tileId': TILE_ID, 'json': '{"merStateStr":"{{context.merPanelEsc}}"}'})))
    N.append((CRM_P, code_node(CRM_P, 'CRM - prep lookup', CRM_PREP)))
    N.append((CRM_SW, node(CRM_SW, 'switch', 'CRM cached?',
        {'switch': {'type': 'cognigyScript', 'operator': "context.merCrmSkip||'go'"},
         'intentLevel': 'input.intent', 'useStrict': ''})))
    N.append((CRM_CSKIP, node(CRM_CSKIP, 'case', 'skip', {'case': {'value': 'skip'}})))
    N.append((CRM_CDEF, node(CRM_CDEF, 'default', 'go', {})))
    N.append((CRM_H, node(CRM_H, 'httpRequest', 'CRM - get_customer', http_cfg('{{context.merCrmUrl}}', 'merCrmRaw'))))
    N.append((CRM_X, code_node(CRM_X, 'CRM - extract record', CRM_POST)))
    N.append((PROD_P, code_node(PROD_P, 'Catalog - prep', PROD_PREP)))
    N.append((PROD_SW, node(PROD_SW, 'switch', 'Catalog cached?',
        {'switch': {'type': 'cognigyScript', 'operator': "context.merProdSkip||'go'"},
         'intentLevel': 'input.intent', 'useStrict': ''})))
    N.append((PROD_CSKIP, node(PROD_CSKIP, 'case', 'skip', {'case': {'value': 'skip'}})))
    N.append((PROD_CDEF, node(PROD_CDEF, 'default', 'go', {})))
    N.append((PROD_H, node(PROD_H, 'httpRequest', 'Catalog - get_products', http_cfg('{{context.merProdUrl}}', 'merProdRaw'))))
    N.append((PROD_X, code_node(PROD_X, 'Catalog - extract', PROD_POST)))
    N.append((PRE_P, code_node(PRE_P, 'Instant pre-panel', PRE_PANEL_CODE)))
    N.append((PRE_S, node(PRE_S, 'sendData', 'Push pre-panel to tile',
                          {'tileId': TILE_ID, 'json': '{"merStateStr":"{{context.merPreEsc}}"}'})))
    N.append((RECOMP_SW, node(RECOMP_SW, 'switch', 'Recompute this turn?',
        {'switch': {'type': 'cognigyScript',
                    'operator': "(!context.merCrm)?'stop':(((context.merLastPart==='Agent'||context.merDupTurn===true||context.merBootTurn===true)&&(context.merPanelN||0)>0)?'stop':'go')"},
         'intentLevel': 'input.intent', 'useStrict': ''})))
    N.append((RC_STOP, node(RC_STOP, 'case', 'stop', {'case': {'value': 'stop'}})))
    N.append((RC_DEF, node(RC_DEF, 'default', 'go', {})))
    N.append((GATE, node(GATE, 'llmPromptV2', 'GATE (mini)',
                         llm_cfg(MINI, GATE_PROMPT, 'merGateRaw', temp=0.0, max_tokens=320, timeout=15000))))
    N.append((GATE_PN, code_node(GATE_PN, 'GATE - parse + sentiment', GATE_PARSE)))
    N.append((SENT_S, node(SENT_S, 'sendData', 'Push live sentiment',
                           {'tileId': TILE_ID, 'json': '{"merSentStr":"{{context.merSentEsc}}"}'})))
    N.append((ROUTE_SW, node(ROUTE_SW, 'switch', 'Route decision',
        {'switch': {'type': 'cognigyScript', 'operator': "context.merRoute||'go'"},
         'intentLevel': 'input.intent', 'useStrict': ''})))
    N.append((RT_SKIP, node(RT_SKIP, 'case', 'skip', {'case': {'value': 'skip'}})))
    N.append((RT_Q, node(RT_Q, 'case', 'question', {'case': {'value': 'question'}})))
    N.append((RT_DEF, node(RT_DEF, 'default', 'go (request)', {})))
    N.append((POL_SW, node(POL_SW, 'switch', 'Policy findings fresh?',
        {'switch': {'type': 'cognigyScript',
                    # the RAW gate route lives in merGate.route — merRoute holds the mapped
                    # decision and can never equal 'request' (the v4 stale-findings bug).
                    'operator': "(!context.merPolicy||((context.merGate&&context.merGate.route)==='request'&&context.merGateMsg!==context.merPolicyForMsg))?'run':'skip'"},
         'intentLevel': 'input.intent', 'useStrict': ''})))
    N.append((PL_RUN, node(PL_RUN, 'case', 'run', {'case': {'value': 'run'}})))
    N.append((PL_DEF, node(PL_DEF, 'default', 'cached', {})))
    N.append((POLQ, code_node(POLQ, 'Policy - build query', POLICY_QUERY)))
    N.append((POL_KS, node(POL_KS, 'searchExtractOutput', 'Knowledge Search (policy)',
                           ks_cfg('{{context.merPolQuery}}', 'merPolHits', topk=6))))
    N.append((POL_EXC, code_node(POL_EXC, 'Policy - build excerpts', KS_EXCERPTS('merPolHits', 'merPolExcerpts', 'POLICY'))))
    N.append((POL_LLM, node(POL_LLM, 'llmPromptV2', 'POLICY ANALYST (GPT-5.4)',
                            llm_cfg(GPT54, POLICY_ANALYST_PROMPT, 'merPolRaw', temp=0.0, max_tokens=1600, timeout=30000))))
    N.append((POL_PARSE, code_node(POL_PARSE, 'Policy - parse findings', POLICY_PARSE)))
    N.append((CMP_P, code_node(CMP_P, 'Composer - prep', COMPOSER_PREP)))
    N.append((CMP, node(CMP, 'llmPromptV2', 'COMPOSER (mini)',
                        llm_cfg(MINI, COMPOSER_PROMPT, 'merPanelRaw', temp=0.3, max_tokens=4096, timeout=45000))))
    N.append((MERGE, code_node(MERGE, 'Merge + escape panel', MERGE_CODE)))
    N.append((PUSH_SW, node(PUSH_SW, 'switch', 'Panel usable?',
        {'switch': {'type': 'cognigyScript', 'operator': PUSH_GUARD},
         'intentLevel': 'input.intent', 'useStrict': ''})))
    N.append((PS_PUSH, node(PS_PUSH, 'case', 'push', {'case': {'value': 'push'}})))
    N.append((PS_DEF, node(PS_DEF, 'default', 'retry', {})))
    N.append((PUSH, node(PUSH, 'sendData', 'Push panel to tile',
                         {'tileId': TILE_ID, 'json': '{"merStateStr":"{{context.merPanelEsc}}"}'})))
    N.append((CMP2, node(CMP2, 'llmPromptV2', 'COMPOSER retry (mini)',
                         llm_cfg(MINI, COMPOSER_PROMPT, 'merPanelRaw', temp=0.2, max_tokens=4096, timeout=45000))))
    N.append((MERGE2, code_node(MERGE2, 'Merge + escape panel (retry)', MERGE_CODE)))
    N.append((PUSH_SW2, node(PUSH_SW2, 'switch', 'Panel usable? (retry)',
        {'switch': {'type': 'cognigyScript', 'operator': PUSH_GUARD},
         'intentLevel': 'input.intent', 'useStrict': ''})))
    N.append((PS2_PUSH, node(PS2_PUSH, 'case', 'push', {'case': {'value': 'push'}})))
    N.append((PS2_DEF, node(PS2_DEF, 'default', 'give up', {})))
    N.append((PUSH2, node(PUSH2, 'sendData', 'Push panel to tile (retry)',
                          {'tileId': TILE_ID, 'json': '{"merStateStr":"{{context.merPanelEsc}}"}'})))

    for _id, obj in N:
        dump('nodeData', _id, obj)

    # ── relations (topological: switch.next=None; continuation chained inside the default case) ──
    def rel(nid, nxt, children=None):
        return {'_id': det_uuid('rel:' + nid).replace('-', '')[:24], 'node': nid, 'next': nxt,
                'children': children or []}

    # ⚠ GRID DISCOVERABILITY (live-debugged 2026-07-30): CXone's copilot socket does a session-start
    # PRE-WALK of the flow to find setAgentAssistGrid. With the grid buried in the router's LAST child
    # branch the pre-walk finds nothing -> config:null -> NO Copilot tab at all (profile/script/endpoint
    # all correct). The working password-reset flow has grid+tile FIRST on the main chain — so: the
    # once/grid/tile mount sits BEFORE the router, and the default branch is the router's FIRST child.
    rels = [
        rel(START, ONCE),
        rel(ONCE, ROUTER, children=[ONFIRST, AFTERW]),
        rel(ONFIRST, GRID), rel(GRID, TILE), rel(TILE, None), rel(AFTERW, None),
        rel(ROUTER, None, children=[DEF_R, C_APPR, C_ASK, C_CMD]),
        # approve
        rel(C_APPR, X_MAP), rel(X_MAP, X_SW),
        rel(X_SW, None, children=[X_GO, X_BAD]),
        rel(X_GO, X_HTTP), rel(X_HTTP, X_RES), rel(X_BAD, X_RES),
        rel(X_RES, X_SEND), rel(X_SEND, None),
        # ask (postback) + gate-question join
        rel(C_ASK, KA_PREP), rel(KA_PREP, KA_KS),
        rel(KA_KS, KA_EXC), rel(KA_EXC, KA_LLM), rel(KA_LLM, KA_PARSE),
        rel(KA_PARSE, KA_SEND), rel(KA_SEND, None),
        rel(Q_PREP, KA_KS),
        # command
        rel(C_CMD, CM_PREP), rel(CM_PREP, CM_AG),
        rel(CM_AG, CM_FIN, children=[CM_DEF] + [CMD_TOOLS_IDS[t[0]][0] for t in CMD_TOOLS]),
        rel(CM_DEF, None),
        rel(CT_HTTP, CT_RES), rel(CT_RES, CT_ANS), rel(CT_ANS, None),
        rel(CM_FIN, CM_SEND), rel(CM_SEND, None),
        # default message turn (once/grid/tile now mounts on the main chain, before the router)
        rel(DEF_R, GREET_P),
        rel(GREET_P, GREET_S), rel(GREET_S, CONVO_B),
        rel(CONVO_B, CONVO_S), rel(CONVO_S, REHYD), rel(REHYD, CRM_P),
        rel(CRM_P, CRM_SW),
        rel(CRM_SW, None, children=[CRM_CSKIP, CRM_CDEF]),
        rel(CRM_CSKIP, PROD_P),
        rel(CRM_CDEF, CRM_H), rel(CRM_H, CRM_X), rel(CRM_X, PROD_P),
        rel(PROD_P, PROD_SW),
        rel(PROD_SW, None, children=[PROD_CSKIP, PROD_CDEF]),
        rel(PROD_CSKIP, PRE_P),
        rel(PROD_CDEF, PROD_H), rel(PROD_H, PROD_X), rel(PROD_X, PRE_P),
        rel(PRE_P, PRE_S), rel(PRE_S, RECOMP_SW),
        rel(RECOMP_SW, None, children=[RC_STOP, RC_DEF]),
        rel(RC_STOP, None),
        rel(RC_DEF, GATE), rel(GATE, GATE_PN), rel(GATE_PN, SENT_S), rel(SENT_S, ROUTE_SW),
        rel(ROUTE_SW, None, children=[RT_SKIP, RT_Q, RT_DEF]),
        rel(RT_SKIP, None),
        rel(RT_Q, Q_PREP),
        rel(RT_DEF, POL_SW),
        rel(POL_SW, None, children=[PL_RUN, PL_DEF]),
        rel(PL_RUN, POLQ), rel(POLQ, POL_KS), rel(POL_KS, POL_EXC), rel(POL_EXC, POL_LLM),
        rel(POL_LLM, POL_PARSE), rel(POL_PARSE, CMP_P),
        rel(PL_DEF, CMP_P),
        rel(CMP_P, CMP), rel(CMP, MERGE), rel(MERGE, PUSH_SW),
        rel(PUSH_SW, None, children=[PS_PUSH, PS_DEF]),
        rel(PS_PUSH, PUSH), rel(PUSH, None),
        rel(PS_DEF, CMP2), rel(CMP2, MERGE2), rel(MERGE2, PUSH_SW2),
        rel(PUSH_SW2, None, children=[PS2_PUSH, PS2_DEF]),
        rel(PS2_PUSH, PUSH2), rel(PUSH2, None), rel(PS2_DEF, None),
    ]
    # per-tool: tool -> map -> shared worker
    for tid, *_rest in CMD_TOOLS:
        t_node, c_node = CMD_TOOLS_IDS[tid]
        rels.append(rel(t_node, c_node))
        rels.append(rel(c_node, CT_HTTP))

    dump('chart', CHART, {'_id': CHART, 'resourceReference': FLOW,
                          'projectReference': PROJECT, 'organisationReference': ORG, 'relations': rels})

    # ── validation ──
    def hexok(x):
        return isinstance(x, str) and len(x) == 24 and all(c in '0123456789abcdef' for c in x)
    problems = []
    nodes = set(os.listdir(os.path.join(pkg, 'nodeData')))
    for sub in folders:
        for fn in os.listdir(os.path.join(pkg, sub)):
            if not hexok(fn):
                problems.append(f'{sub}/{fn} not 24-hex')
            o = json.load(open(os.path.join(pkg, sub, fn), encoding='utf-8'))
            if o.get('_id') != fn:
                problems.append(f'{sub}/{fn} _id mismatch')
            for ld in o.get('localizedData', []) or []:
                if isinstance(ld, dict) and 'locale' in ld:
                    problems.append(f'{sub}/{fn} forbidden locale field')
    node_flow = {fn: json.load(open(os.path.join(pkg, 'nodeData', fn), encoding='utf-8'))['resourceReference']
                 for fn in nodes}
    seen_rel_ids = set()
    c = json.load(open(os.path.join(pkg, 'chart', CHART), encoding='utf-8'))
    referenced = set()
    for r in c['relations']:
        if r['_id'] in seen_rel_ids:
            problems.append(f"duplicate relation _id {r['_id']}")
        seen_rel_ids.add(r['_id'])
        for ref in [r['node'], r['next']] + r.get('children', []):
            if ref is not None and ref not in nodes:
                problems.append(f'chart: rel ref {ref} missing')
            elif ref is not None and node_flow.get(ref) != c['resourceReference']:
                problems.append(f'chart: rel ref {ref} cross-flow leak')
            if ref is not None:
                referenced.add(ref)
    for fn in nodes:
        o = json.load(open(os.path.join(pkg, 'nodeData', fn), encoding='utf-8'))
        if fn not in referenced and o.get('type') != 'start':
            # every non-start node must appear in some relation (as node/next/child)
            src_ok = any(r['node'] == fn for r in c['relations'])
            if not src_ok:
                problems.append(f'node {fn} ({o.get("label")}) not wired into the chart')
        if o.get('type') == 'aiAgentToolAnswer':
            for r in c['relations']:
                if r['node'] == fn and r['next'] is not None:
                    problems.append(f'aiAgentToolAnswer {fn} next must be null')
        if o.get('type') == 'searchExtractOutput':
            cfg = o['localizedData'][0]['config']
            if len(cfg.keys()) < 30:
                problems.append(f'searchExtractOutput {fn} config truncated ({len(cfg.keys())} keys)')
            if cfg.get('knowledgeStoreId') != KS_REF:
                problems.append(f'searchExtractOutput {fn} not bound to the bundled store')
    # grid discoverability — the session-start pre-walk must hit setAgentAssistGrid on the
    # first-child chain right after Start, or the Copilot tab never mounts (2026-07-30).
    rmap = {r['node']: r for r in c['relations']}
    if not (rmap[START]['next'] == ONCE and (rmap[ONCE].get('children') or [None])[0] == ONFIRST
            and rmap[ONFIRST]['next'] == GRID and rmap[GRID]['next'] == TILE):
        problems.append('grid/tile mount is not first-chain-discoverable from Start (pre-walk would miss it)')
    if problems:
        print('VALIDATION FAILED:')
        for p in problems:
            print('  -', p)
        sys.exit(1)
    print('VALIDATION: OK  (%d nodes, 1 flow, 1 aiAgent%s)' % (
        len(nodes), ', 1 knowledgeStore' if include_ks else ', KS OMITTED (--no-ks re-import build)'))

    # ── zip (POSIX paths; temp dir keeps OneDrive from locking the exploded tree) ──
    out_zip = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           PKG_NAME + ('' if include_ks else '-noKS') + '.zip')
    n = 0
    with zipfile.ZipFile(out_zip, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(pkg):
            for fn in files:
                full = os.path.join(root, fn)
                zf.write(full, os.path.relpath(full, pkg).replace(os.sep, '/'))
                n += 1
    shutil.rmtree(build_root, ignore_errors=True)
    print('WROTE %s  (%d files)' % (out_zip, n))
    print()
    print('IMPORT: Cognigy project "Meridian [Agentic Copilot]" -> Upload Package -> this zip.')
    print('  Do NOT open/save the Command Agent node in the UI (save-validation gotcha).')
    print('  After import: upload knowledge/upload/*.txt into the Meridian_Knowledge store; wait for "ready".')
    print('  Then: create an Agent-Assist endpoint bound to flow Meridian_Copilot.')
    print('Live Logging tags: [MER][CONVO] [MER][GREET] [MER][CRM>/<] [MER][PROD<] [MER][PRE] [MER][GATE] '
          '[MER][SENT] [MER][POLICY>/<] [MER][PANEL] [MER][MERGE] [MER][ASK>/<] [MER][EXEC>/<] [MER][CMD>/<]')


if __name__ == '__main__':
    build()
