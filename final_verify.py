#!/usr/bin/env python

import json
import os
import glob

print('=' * 60)
print('Final Verification of MSRA Plugin Fixes')
print('=' * 60)

print('\n1. manifest.json:')
with open('manifest.json', 'r', encoding='utf-8') as f:
    manifest = json.load(f)
print(f'   Version: {manifest["version"]}')
print(f'   Icon: {manifest.get("icon")}')
print(f'   Commands: {len(manifest["commands"])}')
print(f'   msra-modules: {"msra-modules" in [k[1:] for k in manifest["commands"].keys()]}')

print('\n2. SKILL.md files:')
skill_files = glob.glob('skills/**/SKILL.md', recursive=True)
all_ok = True
for sf in skill_files:
    with open(sf, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    v_ok = 'version: "0.9.0"' not in content
    mc_ok = 'min_claude_version: "3.5"' not in content
    if not v_ok or not mc_ok:
        all_ok = False
    print(f'   {os.path.basename(os.path.dirname(sf))}: version={v_ok}, min_claude={mc_ok}')

print('\n3. Command files:')
cmd_files = glob.glob('commands/*.md')
print(f'   Total: {len(cmd_files)}')
for cf in cmd_files:
    with open(cf, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    mr_ok = 'MODE_REGISTRY.md' not in content
    if not mr_ok:
        all_ok = False
    print(f'   {os.path.basename(cf)}: MODE_REGISTRY={mr_ok}')

print('\n4. Icon:')
icon_ok = os.path.exists('icon.png')
if not icon_ok:
    all_ok = False
print(f'   icon.png exists: {icon_ok}')

print('\n5. msra_modules:')
try:
    import msra_modules
    print(f'   Import OK')
    print(f'   Modules: {list(msra_modules.list_modules().keys())}')
except Exception as e:
    print(f'   Import FAILED: {e}')
    all_ok = False

print('\n' + '=' * 60)
if all_ok:
    print('✅ All verifications PASSED!')
else:
    print('❌ Some verifications FAILED!')
    exit(1)
print('=' * 60)
