"""Resolve private, exact-revision inputs without replacing historical ROMs."""
import hashlib,json
from pathlib import Path

def resolve_input(workspace,game,expected_sha256=None):
    workspace=Path(workspace).resolve()
    manifest=workspace/'scenery-completion/rom-inputs.json'
    overrides=json.loads(manifest.read_text(encoding='utf-8')) if manifest.exists() else {}
    row=overrides.get(game)
    if row:
        rom=(workspace/row['rom']).resolve()
        inventory_path=(workspace/row['inventory']).resolve()
        assert rom.is_relative_to(workspace) and inventory_path.is_relative_to(workspace)
    else:
        rom=workspace/'solid-rollout'/('' if game in ('letsgo','radical','unbound') else 'expansion')/(game+'.gba')
        inventory_path=workspace/'scenery-completion/all-game-inventory'/game/'inventory.json'
    inventory=json.loads(inventory_path.read_text(encoding='utf-8'))
    with rom.open('rb') as stream: digest=hashlib.file_digest(stream,'sha256').hexdigest()
    assert digest==inventory['rom_sha256'], 'ROM and inventory revision differ'
    if row:assert digest==row['sha256'], 'Private input identity changed'
    if expected_sha256:assert digest==expected_sha256, 'Profile targets another ROM revision'
    return rom,inventory
