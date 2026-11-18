"""Check the Classic port's authored Pallet Town voxel buildings."""

import json
import sys
import tempfile
from pathlib import Path


PORT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PORT / "scripts"))

import gen_voxel_buildings as generator
import voxel_building as buildings


def main():
    layout = "LAYOUT_PALLET_TOWN"
    expected = {"pallet_house": {(5, 3), (14, 3)}, "oaks_lab": {(13, 9)}}
    models = [model for model in generator.build_models() if model.name in expected]
    assert {model.name for model in models} == expected.keys()
    layouts = buildings._layouts_json()
    occupied = set()
    with tempfile.TemporaryDirectory() as directory:
        for model in models:
            preview = Path(directory) / (model.name + ".png")
            assert buildings.ortho_check(model, preview, exact=model.spec["exact"]) == (0, 0, 0), model.name
            assert model.triangle_count() > 12, model.name
            placements = [entry for entry in generator.find_placements(model, layouts) if entry[4] == layout]
            assert {(entry[1], entry[2]) for entry in placements} == expected[model.name]
            width, height = model.cells
            for _, x, y, _, _, _ in placements:
                cells = {(x + column, y + row) for column in range(width) for row in range(height)}
                assert not occupied.intersection(cells), model.name
                occupied.update(cells)
        binary = Path(directory) / "buildings.bin"
        generator.export(models, str(binary))
        assert binary.read_bytes().startswith(b"VXB9")
    town = json.loads((PORT.parent / "data/maps/PalletTown/map.json").read_text())
    warps = {(warp["x"], warp["y"]) for warp in town["warp_events"]}
    assert len(warps) == 3 and warps <= occupied
    print("PASS Classic Pallet buildings: original projection, two houses, Oak's lab, all three doors")


if __name__ == "__main__":
    main()
