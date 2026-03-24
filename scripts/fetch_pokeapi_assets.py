#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "website" / "assets" / "official-artwork"
MANIFEST_PATH = ROOT / "website" / "assets" / "pokeapi-manifest.json"
COUNT_CACHE_PATH = ROOT / "data-cache" / "pokeapi" / "species-count.json"
SPRITE_BASE = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork"
COUNT_URL = "https://pokeapi.co/api/v2/pokemon-species?limit=1"
START_ID = 1
REQUEST_DELAY_SECONDS = 0.75
TIMEOUT_SECONDS = 20


def read_manifest() -> dict:
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text())
    return {"source": "pokeapi", "entries": {}}


def write_manifest(manifest: dict) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


def fetch_binary(url: str) -> bytes:
    result = subprocess.run(
        ["curl", "-L", "--silent", "--show-error", "--max-time", str(TIMEOUT_SECONDS), url],
        check=True,
        capture_output=True,
    )
    return result.stdout


def fetch_species_count() -> int:
    result = subprocess.run(
        ["curl", "-L", "--silent", "--show-error", "--max-time", str(TIMEOUT_SECONDS), COUNT_URL],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    COUNT_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    COUNT_CACHE_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return int(payload["count"])


def main() -> int:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    manifest = read_manifest()
    end_id = fetch_species_count()

    for pokemon_id in range(START_ID, end_id + 1):
        padded = f"{pokemon_id:03d}"
        out_path = ASSET_DIR / f"{padded}.png"

        if out_path.exists():
            manifest["entries"][padded] = {
                "pokemon_id": pokemon_id,
                "asset_path": str(out_path.relative_to(ROOT)),
                "status": "cached",
            }
            continue

        sprite_url = f"{SPRITE_BASE}/{pokemon_id}.png"
        print(f"Downloading artwork for #{padded} from {sprite_url}")

        try:
            out_path.write_bytes(fetch_binary(sprite_url))
            manifest["entries"][padded] = {
                "pokemon_id": pokemon_id,
                "asset_path": str(out_path.relative_to(ROOT)),
                "sprite_url": sprite_url,
                "status": "downloaded",
            }
            write_manifest(manifest)
            time.sleep(REQUEST_DELAY_SECONDS)
        except subprocess.CalledProcessError as exc:
            print(f"Stopped at #{padded} due to network error: {exc}")
            manifest["entries"][padded] = {
                "pokemon_id": pokemon_id,
                "sprite_url": sprite_url,
                "status": "error",
                "error": str(exc),
            }
            write_manifest(manifest)
            return 1

    print(f"Finished downloading official artwork through #{end_id:04d}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
