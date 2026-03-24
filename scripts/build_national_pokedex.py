#!/usr/bin/env python3
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data-cache" / "pokeapi"
WEBSITE_DATA_PATH = ROOT / "website" / "pokemon-data.js"
WEBSITE_REFERENCE_PATH = ROOT / "website" / "generated" / "pokedex-reference.js"
COUNT_CACHE_PATH = RAW_DIR / "species-count.json"

POKEAPI_BASE = "https://pokeapi.co/api/v2"
COUNT_URL = f"{POKEAPI_BASE}/pokemon-species?limit=1"
REQUEST_TIMEOUT_SECONDS = 30
MAX_RETRIES = 4
RETRY_DELAY_SECONDS = 1.5

POKEMON_DIR = RAW_DIR / "pokemon"
SPECIES_DIR = RAW_DIR / "pokemon-species"
ENCOUNTERS_DIR = RAW_DIR / "encounters"
EVOLUTION_DIR = RAW_DIR / "evolution-chain"


def clean_text(value: str) -> str:
    return " ".join(value.replace("\f", " ").replace("\n", " ").split())


def slug_to_label(value: str) -> str:
    pieces = value.replace("'", "").split("-")
    return " ".join(piece.capitalize() if piece else piece for piece in pieces)


def version_label(value: str) -> str:
    special_cases = {
        "lets-go-pikachu": "Let's Go Pikachu",
        "lets-go-eevee": "Let's Go Eevee",
        "omega-ruby": "Omega Ruby",
        "alpha-sapphire": "Alpha Sapphire",
        "ultra-sun": "Ultra Sun",
        "ultra-moon": "Ultra Moon",
        "brilliant-diamond": "Brilliant Diamond",
        "shining-pearl": "Shining Pearl",
        "legends-arceus": "Legends Arceus",
    }
    if value in special_cases:
        return special_cases[value]
    return " ".join(word.upper() if len(word) <= 2 else word.capitalize() for word in value.split("-"))


def read_json(path: Path) -> dict | list:
    return json.loads(path.read_text())


def fetch_json(url: str) -> dict | list:
    last_error: Exception | None = None
    headers = {
        "User-Agent": "Codex-Pokedex-Builder/1.0",
        "Accept": "application/json",
    }

    for attempt in range(MAX_RETRIES):
        try:
            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
                return json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt == MAX_RETRIES - 1:
                break
            time.sleep(RETRY_DELAY_SECONDS * (attempt + 1))

    raise RuntimeError(f"Failed to fetch {url}: {last_error}")


def read_or_fetch(url: str, path: Path) -> dict | list:
    if path.exists():
        return read_json(path)

    payload = fetch_json(url)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return payload


def get_species_count() -> int:
    payload = read_or_fetch(COUNT_URL, COUNT_CACHE_PATH)
    if not isinstance(payload, dict) or "count" not in payload:
        raise RuntimeError("Pokemon species count payload is missing a count field.")
    return int(payload["count"])


def english_name(species_payload: dict) -> str:
    for entry in species_payload.get("names", []):
        if entry["language"]["name"] == "en":
            return entry["name"]
    return slug_to_label(species_payload["name"])


def english_genus(species_payload: dict) -> str:
    for entry in species_payload.get("genera", []):
        if entry["language"]["name"] == "en":
            return clean_text(entry["genus"])
    return "Pokemon"


def english_flavor_text(species_payload: dict) -> str:
    preferred_versions = [
        "scarlet",
        "violet",
        "sword",
        "shield",
        "sun",
        "moon",
        "x",
        "y",
        "black",
        "white",
        "diamond",
        "pearl",
        "ruby",
        "sapphire",
        "gold",
        "silver",
        "yellow",
        "blue",
        "red",
    ]
    english_entries = [
        entry
        for entry in species_payload.get("flavor_text_entries", [])
        if entry["language"]["name"] == "en"
    ]
    for version in preferred_versions:
        for entry in english_entries:
            if entry["version"]["name"] == version:
                return clean_text(entry["flavor_text"])
    if english_entries:
        return clean_text(english_entries[0]["flavor_text"])
    return ""


def primary_habitat(species_payload: dict) -> str:
    habitat = species_payload.get("habitat")
    if not habitat:
        return "Unknown"
    return slug_to_label(habitat["name"])


def generation_label(species_payload: dict) -> str:
    generation_name = species_payload["generation"]["name"].removeprefix("generation-")
    roman = generation_name.upper()
    return f"Generation {roman}"


def availability_label(species_payload: dict, encounter_locations: list[dict]) -> str:
    if encounter_locations:
        return "Wild Encounter"
    if species_payload.get("is_mythical"):
        return "Mythical / Event"
    if species_payload.get("is_legendary"):
        return "Legendary / Special"
    if species_payload.get("is_baby"):
        return "Baby / Breeding"
    return "Special / Evolved"


def summarize_locations(encounter_locations: list[dict]) -> str:
    if not encounter_locations:
        return "No wild encounter locations are listed in PokeAPI for this species."

    summaries = []
    for group in encounter_locations[:3]:
        locations = ", ".join(group["locations"][:2])
        if len(group["locations"]) > 2:
            locations += ", ..."
        summaries.append(f"{group['versionLabel']}: {locations}")
    return " | ".join(summaries)


def unique_versions(encounter_locations: list[dict]) -> list[str]:
    return [group["versionLabel"] for group in encounter_locations]


def encounter_groups(encounters_payload: list) -> list[dict]:
    version_locations: dict[str, set[str]] = {}

    for encounter in encounters_payload:
        location_name = slug_to_label(encounter["location_area"]["name"])
        for detail in encounter.get("version_details", []):
            label = version_label(detail["version"]["name"])
            version_locations.setdefault(label, set()).add(location_name)

    return [
        {
            "versionLabel": label,
            "locations": sorted(locations),
        }
        for label, locations in sorted(version_locations.items(), key=lambda item: item[0])
    ]


def evolution_detail_label(details: list[dict]) -> str:
    if not details:
        return ""

    detail = details[0]
    if detail.get("min_level"):
        return f"Lv. {detail['min_level']}"
    if detail.get("item"):
        return f"Use {slug_to_label(detail['item']['name'])}"
    if detail.get("trigger", {}).get("name") == "trade":
        if detail.get("held_item"):
            return f"Trade holding {slug_to_label(detail['held_item']['name'])}"
        return "Trade"
    if detail.get("min_happiness"):
        return "High friendship"
    if detail.get("known_move"):
        return f"Learn {slug_to_label(detail['known_move']['name'])}"
    if detail.get("known_move_type"):
        return f"Know a {slug_to_label(detail['known_move_type']['name'])} move"
    if detail.get("location"):
        return f"At {slug_to_label(detail['location']['name'])}"
    if detail.get("min_affection"):
        return "High affection"
    if detail.get("needs_overworld_rain"):
        return "While raining"
    if detail.get("party_species"):
        return f"With {slug_to_label(detail['party_species']['name'])} in party"
    if detail.get("party_type"):
        return f"With a {slug_to_label(detail['party_type']['name'])} type in party"
    if detail.get("relative_physical_stats") == 1:
        return "Attack > Defense"
    if detail.get("relative_physical_stats") == -1:
        return "Attack < Defense"
    if detail.get("relative_physical_stats") == 0:
        return "Attack = Defense"
    if detail.get("time_of_day"):
        return f"At {detail['time_of_day']}"
    if detail.get("turn_upside_down"):
        return "Turn device upside down"
    if detail.get("min_beauty"):
        return "High beauty"
    if detail.get("gender") == 1:
        return "Female only"
    if detail.get("gender") == 2:
        return "Male only"
    if detail.get("trigger"):
        return slug_to_label(detail["trigger"]["name"])
    return ""


def build_chain_paths(node: dict) -> list[dict]:
    species_slug = node["species"]["name"]
    species_name = slug_to_label(species_slug)
    evolves_to = node.get("evolves_to", [])
    if not evolves_to:
        return [{"slugs": [species_slug], "text": species_name}]

    paths: list[dict] = []
    for child in evolves_to:
        detail_label = evolution_detail_label(child.get("evolution_details", []))
        connector = f" -> ({detail_label}) -> " if detail_label else " -> "
        for child_path in build_chain_paths(child):
            paths.append(
                {
                    "slugs": [species_slug, *child_path["slugs"]],
                    "text": f"{species_name}{connector}{child_path['text']}",
                }
            )
    return paths


def evolution_summary(species_payload: dict) -> str:
    chain_url = species_payload["evolution_chain"]["url"]
    chain_id = chain_url.rstrip("/").rsplit("/", 1)[-1]
    chain_payload = read_or_fetch(chain_url, EVOLUTION_DIR / f"{chain_id}.json")
    species_slug = species_payload["name"]
    matching_paths = [
        path["text"]
        for path in build_chain_paths(chain_payload["chain"])
        if species_slug in path["slugs"]
    ]
    if matching_paths:
        return " / ".join(dict.fromkeys(matching_paths))
    return english_name(species_payload)


def default_variety_url(species_payload: dict) -> str:
    for variety in species_payload.get("varieties", []):
        if variety.get("is_default"):
            return variety["pokemon"]["url"]
    return f"{POKEAPI_BASE}/pokemon/{species_payload['id']}"


def build_entry(species_payload: dict, pokemon_payload: dict, encounter_locations: list[dict]) -> dict:
    flavor_text = english_flavor_text(species_payload)
    summary = (
        flavor_text
        if flavor_text
        else f"{english_name(species_payload)} is a {english_genus(species_payload).lower()} from {generation_label(species_payload)}."
    )
    return {
        "id": int(species_payload["id"]),
        "name": english_name(species_payload),
        "types": [slot["type"]["name"].title() for slot in sorted(pokemon_payload["types"], key=lambda item: item["slot"])],
        "habitat": primary_habitat(species_payload),
        "generation": generation_label(species_payload),
        "availability": availability_label(species_payload, encounter_locations),
        "location": summarize_locations(encounter_locations),
        "summary": summary,
        "evolution": evolution_summary(species_payload),
        "versions": unique_versions(encounter_locations),
    }


def build_reference(species_payload: dict, encounter_locations: list[dict]) -> dict:
    return {
        "flavorText": english_flavor_text(species_payload),
        "genus": english_genus(species_payload),
        "generation": generation_label(species_payload),
        "encounterLocations": encounter_locations,
        "locationFallback": "No wild encounter locations are listed in PokeAPI for this species.",
    }


def write_website_data(entries: list[dict]) -> None:
    payload = "window.pokedexEntries = " + json.dumps(entries, indent=2, ensure_ascii=False) + ";\n"
    WEBSITE_DATA_PATH.write_text(payload)


def write_reference_data(reference: dict[str, dict]) -> None:
    WEBSITE_REFERENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = "window.pokedexReferenceData = " + json.dumps(reference, indent=2, ensure_ascii=False) + ";\n"
    WEBSITE_REFERENCE_PATH.write_text(payload)


def main() -> int:
    total_species = get_species_count()
    entries: list[dict] = []
    reference: dict[str, dict] = {}

    for species_id in range(1, total_species + 1):
        padded = f"{species_id:04d}"
        print(f"Building #{padded}")

        species_payload = read_or_fetch(
            f"{POKEAPI_BASE}/pokemon-species/{species_id}",
            SPECIES_DIR / f"{species_id:04d}.json",
        )
        pokemon_payload = read_or_fetch(
            default_variety_url(species_payload),
            POKEMON_DIR / f"{species_id:04d}.json",
        )
        encounters_payload = read_or_fetch(
            pokemon_payload["location_area_encounters"],
            ENCOUNTERS_DIR / f"{species_id:04d}.json",
        )

        encounter_locations = encounter_groups(encounters_payload)
        entries.append(build_entry(species_payload, pokemon_payload, encounter_locations))
        reference[str(species_id)] = build_reference(species_payload, encounter_locations)

    write_website_data(entries)
    write_reference_data(reference)
    print(f"Wrote {WEBSITE_DATA_PATH}")
    print(f"Wrote {WEBSITE_REFERENCE_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
