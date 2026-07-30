#!/usr/bin/env python3
"""fix_profile.py — repair the CXone Copilot profile the UI save-bug breaks.

A freshly created/saved profile silently drops: channels (-> []), the digitalChannel/
voiceChannel booleans, and includeAgentUtterances (-> false). Empty channels = the
profile does nothing and the workspace never mounts a copilot. This tool GETs the
profile, patches ONLY those fields, PUTs it back, and verifies.

Usage:
  set CC_TOKEN=<fresh bearer from any workspace API call, ~1h life>
  python tools/fix_profile.py [profile-name]        (default: Meridian_Agentic_Copilot_Profile)

NEVER re-save a working Agentic profile in the UI — use this instead.
"""
import json
import os
import sys
import urllib.error
import urllib.request

API = 'https://api-na1.niceincontact.com/profile-hub/v1/profile'
NAME = sys.argv[1] if len(sys.argv) > 1 else 'Meridian_Agentic_Copilot_Profile'


def req(url, method='GET', body=None):
    tok = os.environ['CC_TOKEN'].strip()
    r = urllib.request.Request(url, data=(json.dumps(body).encode() if body else None), method=method)
    r.add_header('authorization', 'Bearer ' + tok)
    r.add_header('content-type', 'application/json')
    r.add_header('accept', 'application/json, text/plain, */*')
    r.add_header('origin', 'https://na1.nice-incontact.com')
    r.add_header('referer', 'https://na1.nice-incontact.com/')
    try:
        with urllib.request.urlopen(r, timeout=30) as resp:
            return resp.status, json.loads(resp.read().decode('utf-8', 'ignore') or '{}')
    except urllib.error.HTTPError as e:
        return e.code, {'error': e.read().decode('utf-8', 'ignore')[:800]}


code, o = req(API + '/' + NAME)
assert code == 200, (code, o)
cfg = o['config']
cfg = json.loads(cfg) if isinstance(cfg, str) else cfg

print('BEFORE  channels=%s  digitalChannel=%s  voiceChannel=%s  includeAgentUtterances=%s' % (
    cfg.get('channels'), cfg.get('digitalChannel'), cfg.get('voiceChannel'), cfg.get('includeAgentUtterances')))
print('        endpoint=%s  flow=%s' % (
    (cfg.get('aiAgentConfig') or {}).get('endpointName'), (cfg.get('aiAgentConfig') or {}).get('flowName')))

cfg['channels'] = ['digital', 'voice']
cfg['digitalChannel'] = True
cfg['voiceChannel'] = True
cfg['includeAgentUtterances'] = True

code, o = req(API, 'PUT', {'agentAssistConfiguration': cfg, 'acdType': 'Internal', 'divisionId': 1})
print('PUT -> HTTP', code, json.dumps(o)[:200])
if code not in (200, 201, 204):
    sys.exit(1)

code, o = req(API + '/' + NAME)
cfg2 = o['config']
cfg2 = json.loads(cfg2) if isinstance(cfg2, str) else cfg2
print('AFTER   channels=%s  digitalChannel=%s  voiceChannel=%s  includeAgentUtterances=%s' % (
    cfg2.get('channels'), cfg2.get('digitalChannel'), cfg2.get('voiceChannel'), cfg2.get('includeAgentUtterances')))
ok = (cfg2.get('channels') and cfg2.get('digitalChannel') is True and cfg2.get('includeAgentUtterances') is True)
print('VERIFY:', 'OK — full agent logout/login, then take a FIRST contact.' if ok else 'STILL WRONG — paste this output back.')
sys.exit(0 if ok else 1)
