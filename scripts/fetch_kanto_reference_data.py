#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import time
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data-cache" / "pokeapi"
GENERATED_JS_PATH = ROOT / "website" / "generated" / "kanto-reference.js"
START_ID = 1
END_ID = 151
REQUEST_DELAY_SECONDS = 0.55

VERSION_ORDER = ["red", "blue", "yellow"]
LOCATION_VERSION_ORDER = {"red": 0, "blue": 1, "yellow": 2}
MOVE_DIR = RAW_DIR / "move"


def curl_json(url: str) -> dict:
    result = subprocess.run(
        ["curl", "-L", "--silent", "--show-error", url],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def read_or_fetch(url: str, path: Path, *, delay_after_fetch: bool = True) -> dict:
    if path.exists():
        return json.loads(path.read_text())

    payload = curl_json(url)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    if delay_after_fetch:
        time.sleep(REQUEST_DELAY_SECONDS)
    return payload


def clean_text(value: str) -> str:
    return " ".join(value.replace("\f", " ").replace("\n", " ").split())


def english_flavor_text(species_payload: dict) -> dict:
    texts = {}
    for version in VERSION_ORDER:
        for entry in species_payload.get("flavor_text_entries", []):
            if entry["language"]["name"] == "en" and entry["version"]["name"] == version:
                texts[version] = clean_text(entry["flavor_text"])
                break
    return texts


def encounter_groups(encounters_payload: list) -> list:
    version_locations = defaultdict(list)

    for encounter in encounters_payload:
        location_name = encounter["location_area"]["name"].replace("-", " ").title()
        for detail in encounter.get("version_details", []):
            version = detail["version"]["name"]
            if version in LOCATION_VERSION_ORDER:
                version_locations[version].append(location_name)

    groups = []
    for version in VERSION_ORDER:
      if version_locations[version]:
          unique_locations = sorted(set(version_locations[version]))
          groups.append(
              {
                  "version": version,
                  "versionLabel": "Red/Blue" if version in {"red", "blue"} else "Yellow",
                  "locations": unique_locations,
              }
          )

    merged = {}
    for group in groups:
        key = group["versionLabel"]
        merged.setdefault(key, [])
        merged[key].extend(group["locations"])

    return [
        {"versionLabel": label, "locations": sorted(set(locations))}
        for label, locations in merged.items()
    ]


def level_up_learnset(pokemon_payload: dict) -> list:
    move_rows = []
    for move in pokemon_payload.get("moves", []):
        move_name = move["move"]["name"]
        move_payload = read_or_fetch(
            move["move"]["url"],
            MOVE_DIR / f"{move_name}.json",
            delay_after_fetch=False,
        )
        row = {
            "move": move_name.replace("-", " ").title(),
            "type": move_payload["type"]["name"].title(),
            "redBlueLevel": "-",
            "yellowLevel": "-",
        }
        for detail in move.get("version_group_details", []):
            if detail["move_learn_method"]["name"] != "level-up":
                continue

            version_group = detail["version_group"]["name"]
            level = detail["level_learned_at"]
            if version_group == "red-blue":
                row["redBlueLevel"] = "Start" if level == 0 else str(level)
            elif version_group == "yellow":
                row["yellowLevel"] = "Start" if level == 0 else str(level)

        if row["redBlueLevel"] != "-" or row["yellowLevel"] != "-":
            move_rows.append(row)

    move_rows.sort(
        key=lambda row: (
            10**6 if row["redBlueLevel"] == "-" else 0 if row["redBlueLevel"] == "Start" else int(row["redBlueLevel"]),
            10**6 if row["yellowLevel"] == "-" else 0 if row["yellowLevel"] == "Start" else int(row["yellowLevel"]),
            row["move"],
        )
    )
    return move_rows


def build_reference_entry(pokemon_payload: dict, species_payload: dict, encounters_payload: list) -> dict:
    return {
        "pokedexText": english_flavor_text(species_payload),
        "encounterLocations": encounter_groups(encounters_payload),
        "locationFallback": "Gift, trade, evolution, fossil revival, or special event only.",
        "learnset": level_up_learnset(pokemon_payload),
    }


def main() -> int:
    reference = {}

    for pokemon_id in range(START_ID, END_ID + 1):
        padded = f"{pokemon_id:03d}"
        print(f"Syncing #{padded}")

        pokemon_payload = read_or_fetch(
            f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}",
            RAW_DIR / "pokemon" / f"{padded}.json",
        )
        species_payload = read_or_fetch(
            f"https://pokeapi.co/api/v2/pokemon-species/{pokemon_id}",
            RAW_DIR / "pokemon-species" / f"{padded}.json",
        )
        encounters_payload = read_or_fetch(
            pokemon_payload["location_area_encounters"],
            RAW_DIR / "encounters" / f"{padded}.json",
        )

        reference[str(pokemon_id)] = build_reference_entry(
            pokemon_payload,
            species_payload,
            encounters_payload,
        )

    GENERATED_JS_PATH.parent.mkdir(parents=True, exist_ok=True)
    GENERATED_JS_PATH.write_text(
        "window.kantoReferenceData = " + json.dumps(reference, indent=2, sort_keys=True) + ";\n"
    )
    print(f"Wrote {GENERATED_JS_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
