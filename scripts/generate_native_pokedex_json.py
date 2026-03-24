#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEBSITE_DATA = ROOT / "website" / "pokemon-data.js"
REFERENCE_DATA = ROOT / "website" / "generated" / "pokedex-reference.js"
IOS_OUTPUT = ROOT / "ios" / "KantoGridIOS" / "Resources" / "Web" / "native-kanto-pokedex.json"
MAC_OUTPUT = ROOT / "macos" / "KantoGridMac" / "Resources" / "Web" / "native-kanto-pokedex.json"

def parse_global_assignment(path: Path, prefix: str):
    text = path.read_text()
    payload = text.removeprefix(prefix).rstrip(" ;\n")
    return json.loads(payload)


def main() -> int:
    pokemon_entries = parse_global_assignment(WEBSITE_DATA, "window.pokedexEntries = ")
    reference_entries = parse_global_assignment(REFERENCE_DATA, "window.pokedexReferenceData = ")

    merged = []
    for entry in pokemon_entries:
        reference = reference_entries.get(str(entry["id"]), {})
        merged.append(
            {
                **entry,
                "reference": reference,
            }
        )

    for output in [IOS_OUTPUT, MAC_OUTPUT]:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(merged, indent=2, ensure_ascii=False) + "\n")
        print(f"Wrote {output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
