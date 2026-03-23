#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEBSITE_DATA = ROOT / "website" / "pokemon-data.js"
REFERENCE_DATA = ROOT / "website" / "generated" / "kanto-reference.js"
IOS_OUTPUT = ROOT / "ios" / "KantoGridIOS" / "Resources" / "Web" / "native-kanto-pokedex.json"
MAC_OUTPUT = ROOT / "macos" / "KantoGridMac" / "Resources" / "Web" / "native-kanto-pokedex.json"


def split_top_level(source: str, separator: str = ",") -> list[str]:
    items: list[str] = []
    current: list[str] = []
    depth_paren = 0
    depth_bracket = 0
    in_string = False
    escape = False

    for char in source:
        current.append(char)

        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == "(":
            depth_paren += 1
        elif char == ")":
            depth_paren -= 1
        elif char == "[":
            depth_bracket += 1
        elif char == "]":
            depth_bracket -= 1
        elif char == separator and depth_paren == 0 and depth_bracket == 0:
            items.append("".join(current[:-1]).strip())
            current = []

    if current:
        items.append("".join(current).strip())

    return [item for item in items if item]


def extract_create_calls(source: str) -> list[str]:
    anchor = "const pokemon151 = ["
    start = source.index(anchor) + len(anchor)
    end = source.rindex("];")
    body = source[start:end]

    calls: list[str] = []
    current: list[str] = []
    depth = 0
    in_string = False
    escape = False

    for char in body:
        if in_string:
            current.append(char)
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
            current.append(char)
        elif char == "(":
            depth += 1
            current.append(char)
        elif char == ")":
            depth -= 1
            current.append(char)
            if depth == 0 and "".join(current).strip():
                calls.append("".join(current).strip())
                current = []
        elif depth > 0:
            current.append(char)

    return calls


def parse_pokemon_data() -> list[dict]:
    text = WEBSITE_DATA.read_text()
    pokemon_entries: list[dict] = []

    for call in extract_create_calls(text):
        args = split_top_level(call[1:-1])
        pokemon_entries.append(
            {
                "id": int(args[0]),
                "name": json.loads(args[1]),
                "types": json.loads(args[2]),
                "habitat": json.loads(args[3]),
                "location": json.loads(args[4]),
                "availability": json.loads(args[5]),
                "summary": json.loads(args[6]),
                "role": json.loads(args[7]),
                "evolution": json.loads(args[8]),
                "versions": json.loads(args[9]),
                "fieldNote": json.loads(args[10]),
            }
        )

    return pokemon_entries


def parse_reference_data() -> dict:
    text = REFERENCE_DATA.read_text()
    payload = text.removeprefix("window.kantoReferenceData = ").rstrip(" ;\n")
    return json.loads(payload)


def main() -> int:
    pokemon_entries = parse_pokemon_data()
    reference_entries = parse_reference_data()

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
