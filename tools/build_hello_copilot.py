# -*- coding: utf-8 -*-
"""
build_hello_copilot.py — MINIMAL diagnostic copilot flow for wiring bisection.

Clones the working password-reset topology exactly: Start -> setAgentAssistGrid ->
setHTMLTile (INLINE html, zero external dependencies) -> echo code -> sendData -> End.
If THIS flow's tile mounts in Agent Workspace, the whole CXone chain (profile/script/
channel/endpoint) is proven good and any remaining problem is in the main flow.

Build:  python tools/build_hello_copilot.py  ->  package/Package-Meridian-HelloCopilot.zip
Test:   import zip -> point MeridianWebhookEndpoint's Flow at Meridian_HelloCopilot ->
        full logout/login -> first contact. Flip the endpoint back afterwards.
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

PROJECT = '6a6a822ebc1cab619429299e'
ORG     = '69c6a93834910b624e8f5fc2'
USER    = '69f8ea44d292925bcf7716c3'
LOCALE  = '6a6a822ebc1cab61942929a0'
LOCALE_REF = '696d38ca-e3af-428b-a719-62a70fc418d9'
EPOCH   = 1785400000
PKG_NAME = 'Package-Meridian-HelloCopilot'
FLOW_NAME = 'Meridian_HelloCopilot'
PFX = 'e11000000000000000aa'
TILE_ID = 'mer-hello-tile'


def det_uuid(seed):
    h = hashlib.md5(('hello1:' + seed).encode()).hexdigest()
    return f'{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}'


def NID(s):
    x = PFX + s
    assert len(x) == 24, x
    return x


FLOW, CHART = NID('0010'), NID('0011')
FSET, FSTATE, ITG = NID('0012'), NID('0013'), NID('0014')
START, GRID, TILE, ECHO, SEND, END = NID('0001'), NID('0002'), NID('0003'), NID('0004'), NID('0005'), NID('0006')

TILE_HTML = (
    '<!doctype html><html><head><meta charset="utf-8">'
    '<meta name="viewport" content="width=device-width,initial-scale=1"><title>AI Agent</title>'
    "<style>html,body{margin:0;background:#F8FAFC;font-family:'Segoe UI',system-ui,sans-serif;color:#0F172A;font-size:13px}"
    '.ok{background:#DCFCE7;color:#166534;font-weight:700;font-size:15px;padding:14px;text-align:center}'
    '.st{padding:8px 12px;color:#475569;border-bottom:1px solid #E2E8F0}'
    '.log{padding:8px 12px}.row{background:#fff;border:1px solid #E2E8F0;border-radius:6px;padding:6px 9px;margin-bottom:6px;word-break:break-word}'
    '.btn{margin:8px 12px;background:#0F2A4A;color:#fff;border:none;border-radius:6px;padding:8px 12px;font-weight:600;cursor:pointer}'
    '</style></head><body>'
    '<div class="ok">✓ TILE MOUNTED — Meridian Hello Copilot</div>'
    '<div class="st" id="sdk">checking SDK…</div>'
    '<button class="btn" id="pb">Send test postback</button>'
    '<div class="log" id="log"></div>'
    '<script>(function(){\n'
    'function row(t){var d=document.createElement("div");d.className="row";d.textContent=t;'
    'var l=document.getElementById("log");l.insertBefore(d,l.firstChild);}\n'
    'document.getElementById("sdk").textContent=(window.SDK&&window.SDK.postback)?"SDK available — postbacks will reach the flow":"SDK NOT available (standalone preview)";\n'
    'document.getElementById("pb").addEventListener("click",function(){'
    'try{if(window.SDK&&window.SDK.postback){window.SDK.postback({action:"ping",from:"hello-tile"});row("postback sent → expect an echo row back");}'
    'else{row("no SDK — cannot postback");}}catch(e){row("postback error: "+e);}});\n'
    'function handle(d){if(!d||typeof d!=="object")return;var src=(d.metadata&&typeof d.metadata==="object")?d.metadata:d;\n'
    'if(src.helloStr){var o=null;try{o=JSON.parse(src.helloStr);}catch(e){}\n'
    'row(o?("turn "+o.n+" · "+(o.participant||"?")+" · “"+(o.text||"(no text)")+"”"+(o.payload?(" · payload:"+JSON.stringify(o.payload)):"")):("helloStr (unparsed): "+String(src.helloStr).slice(0,160)));}}\n'
    'window.addEventListener("message",function(e){handle(e.data);});\n'
    '(window.__merBuf||[]).forEach(handle);\n'
    'row("tile script running · "+new Date().toLocaleTimeString());\n'
    '})();</script></body></html>')

ECHO_CODE = (
    "var aa=(input.data&&input.data._cognigy&&input.data._cognigy._agentAssist)||null;\n"
    "var pay=aa&&aa.payload; if(typeof pay==='string'){try{pay=JSON.parse(pay);}catch(e){}}\n"
    "var n=(context.helloN||0)+1; api.addToContext('helloN',n,'simple');\n"
    "var o={n:n,text:String(input.text||'').slice(0,120),participant:String((input.data&&input.data.participant)||(aa&&aa.participant)||''),payload:pay||null,ts:new Date().toISOString()};\n"
    "api.log('[HELLO] turn '+n+' :: '+JSON.stringify(o),'info');\n"
    "var es=JSON.stringify(o).replace(/\\\\/g,'\\\\\\\\').replace(/\"/g,'\\\\\"');\n"
    "api.addToContext('helloEsc',es,'simple');\n")


def build():
    build_root = tempfile.mkdtemp(prefix='hellobuild_')
    pkg = os.path.join(build_root, PKG_NAME)
    for d in ('flow', 'chart', 'nodeData', 'locale', 'flowSettings', 'flowState', 'intentTrainGroup'):
        os.makedirs(os.path.join(pkg, d))

    def dump(sub, _id, obj):
        with open(os.path.join(pkg, sub, _id), 'w', encoding='utf-8') as f:
            json.dump(obj, f, separators=(',', ':'), ensure_ascii=False)

    with open(os.path.join(pkg, 'index.json'), 'w', encoding='utf-8') as f:
        json.dump({'cognigyVersion': '2026.13.1', 'type': 'package', 'createdAt': '2026-07-30T00:00:00.000Z',
                   'name': PKG_NAME, 'description': 'Minimal diagnostic copilot: Start -> grid -> inline tile -> '
                   'echo push. If this mounts, the CXone chain is good.',
                   'resourcesHash': '0' * 40}, f, separators=(',', ':'), ensure_ascii=False)

    dump('locale', LOCALE, {'_id': LOCALE, 'referenceId': LOCALE_REF, 'name': 'en-US', 'primary': True,
                            'nluLanguage': 'en-US', 'projectReference': PROJECT, 'organisationReference': ORG,
                            'createdAt': EPOCH, 'lastChanged': EPOCH, 'createdBy': USER, 'lastChangedBy': USER})
    dump('flow', FLOW, {'_id': FLOW, 'referenceId': det_uuid(PFX + '_flow'), 'name': FLOW_NAME,
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

    def node(_id, ntype, label, config, *, entry=False):
        return {'_id': _id, 'referenceId': det_uuid(_id), 'type': ntype, 'extension': '@cognigy/basic-nodes',
                'label': label, 'comment': '', 'commentColor': '', 'analyticsLabel': None,
                'isEntryPoint': entry, 'isDisabled': False, 'mock': {'isEnabled': False, 'code': ''},
                'localizedData': [{'config': config, 'preview': '', 'localeReference': LOCALE}],
                'chartReference': CHART, 'resourceReference': FLOW,
                'projectReference': PROJECT, 'organisationReference': ORG}

    dump('nodeData', START, node(START, 'start', 'Start', {}, entry=True))
    dump('nodeData', GRID, node(GRID, 'setAgentAssistGrid', 'Set Layout',
         {'agentAssistConfig': {'grid': {'columns': 1, 'rows': 6, 'gap': 8},
                                'tiles': {TILE_ID: {'x': 1, 'y': 1, 'columns': 1, 'rows': 6}}},
          'backgroundSelector': 'default'}))
    dump('nodeData', TILE, node(TILE, 'setHTMLTile', 'Hello Tile', {'tileId': TILE_ID, 'htmlContent': TILE_HTML}))
    dump('nodeData', ECHO, node(ECHO, 'code', 'Echo turn', {'code': ECHO_CODE, 'hasError': False, 'transpiled': ECHO_CODE}))
    dump('nodeData', SEND, node(SEND, 'sendData', 'Push echo to tile',
         {'tileId': TILE_ID, 'json': '{"helloStr":"{{context.helloEsc}}"}'}))
    dump('nodeData', END, node(END, 'end', 'End', {}))

    def rel(nid, nxt, children=None):
        return {'_id': det_uuid('rel:' + nid).replace('-', '')[:24], 'node': nid, 'next': nxt,
                'children': children or []}

    rels = [rel(START, GRID), rel(GRID, TILE), rel(TILE, ECHO), rel(ECHO, SEND), rel(SEND, END), rel(END, None)]
    dump('chart', CHART, {'_id': CHART, 'resourceReference': FLOW,
                          'projectReference': PROJECT, 'organisationReference': ORG, 'relations': rels})

    # validation
    problems = []
    for sub in ('flow', 'chart', 'nodeData', 'locale', 'flowSettings', 'flowState', 'intentTrainGroup'):
        for fn in os.listdir(os.path.join(pkg, sub)):
            o = json.load(open(os.path.join(pkg, sub, fn), encoding='utf-8'))
            if o.get('_id') != fn:
                problems.append(f'{sub}/{fn} _id mismatch')
            if not (len(fn) == 24 and all(c in '0123456789abcdef' for c in fn)):
                problems.append(f'{sub}/{fn} not 24-hex')
    nodes = set(os.listdir(os.path.join(pkg, 'nodeData')))
    for r in rels:
        for ref in [r['node'], r['next']] + r['children']:
            if ref is not None and ref not in nodes:
                problems.append(f'rel ref {ref} missing')
    if problems:
        print('VALIDATION FAILED:', problems)
        sys.exit(1)
    print('VALIDATION: OK  (%d nodes; tile html %d bytes inline)' % (len(nodes), len(TILE_HTML)))

    out_zip = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           'package', PKG_NAME + '.zip')
    with zipfile.ZipFile(out_zip, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(pkg):
            for fn in files:
                full = os.path.join(root, fn)
                zf.write(full, os.path.relpath(full, pkg).replace(os.sep, '/'))
    shutil.rmtree(build_root, ignore_errors=True)
    print('WROTE', out_zip)
    print('TEST: import -> point MeridianWebhookEndpoint Flow at', FLOW_NAME,
          '-> logout/login -> first contact. Flip the endpoint back to Meridian_Copilot afterwards.')


if __name__ == '__main__':
    build()
