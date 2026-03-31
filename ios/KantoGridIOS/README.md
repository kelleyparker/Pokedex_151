# KantoGridIOS

SwiftUI iOS wrapper for the shared Kanto Pokédex web bundle.

## What is here

- `Sources/` contains the SwiftUI app entry point and `WKWebView` wrapper.
- `Resources/Web/` is where the synced website bundle should live.

## Xcode setup

1. Create a new **App** project in Xcode named `KantoGridIOS`.
2. Or open the included [KantoGridIOS.xcodeproj](KantoGridIOS.xcodeproj).
3. Replace or keep the included Swift files in this folder's `Sources/`.
4. Run:
   ```bash
   cd /path/to/Pokedex_151
   ./scripts/sync_web_bundle.sh
   ```
5. Build and run on iPhone or iPad.

## Notes

- The app loads the already-cached site locally, including artwork and generated Pokédex reference data.
- Because the content is bundled, the app does not need live PokeAPI access at runtime.
