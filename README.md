# Pokedex 151

Cyber-styled Kanto Pokedex focused on the first 151 Pokemon and their place in Pokemon Red, Blue, and Yellow.

## Project layout

- `website/` - static website build
- `ios/` - SwiftUI iOS wrapper scaffold plus bundled web content
- `macos/` - SwiftUI macOS wrapper scaffold plus bundled web content

## Run locally

From the project root:

```bash
cd /Users/kparker/Documents/Codex/Pokedex_151/website
python3 -m http.server 8000
```

Then open:

- `http://localhost:8000`

If `8000` is busy, use another port like:

```bash
python3 -m http.server 8001
```

## Pull artwork from PokeAPI

The site is set up to read local official artwork from `website/assets/official-artwork/`.

To download the first 151 safely:

```bash
cd /Users/kparker/Documents/Codex/Pokedex_151
python3 scripts/fetch_pokeapi_assets.py
```

Notes:

- The script fetches only `#001` through `#151`.
- It caches files locally and skips assets already downloaded.
- It pulls from PokeAPI's official artwork sprite repository one file at a time.
- It intentionally waits `0.75` seconds between downloads to stay polite.
- It stores progress in `website/assets/pokeapi-manifest.json`, so reruns can resume cleanly.

## Pull Pokedex text, locations, and move charts

The site can also cache Red/Blue/Yellow reference data locally from PokeAPI.

```bash
cd /Users/kparker/Documents/Codex/Pokedex_151
python3 scripts/fetch_kanto_reference_data.py
```

Notes:

- This builds `website/generated/kanto-reference.js`.
- It caches raw API responses in `data-cache/pokeapi/`.
- It stores English cartridge flavor text for Red, Blue, and Yellow.
- It stores encounter locations when PokeAPI exposes them for the original games.
- It stores the Gen 1 level-up learnset chart for each of the first 151 Pokemon.

## Sync content into the native app folders

When the website changes, re-copy it into the iOS and macOS resource folders:

```bash
cd /Users/kparker/Documents/Codex/Pokedex_151
./scripts/sync_web_bundle.sh
```

This copies the fully cached website into:

- `ios/KantoGridIOS/Resources/Web/`
- `macos/KantoGridMac/Resources/Web/`

## Notes

- The UI uses a techno/cyber visual direction with `Orbitron` and `Rajdhani` to approximate the requested EA-style futuristic tone.
- The base descriptive data is local in `website/pokemon-data.js`.
- Artwork is now cached locally in `website/assets/official-artwork/`.
- Pokedex text, encounter locations, and move charts are now cached locally in `website/generated/kanto-reference.js`.
- The iOS and macOS folders now include SwiftUI `WKWebView` wrappers that can ship the same offline content bundle in Xcode.
