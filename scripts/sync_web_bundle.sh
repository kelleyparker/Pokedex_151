#!/bin/zsh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WEB_SOURCE="$ROOT/website"
IOS_TARGET="$ROOT/ios/KantoGridIOS/Resources/Web"
MAC_TARGET="$ROOT/macos/KantoGridMac/Resources/Web"

python3 "$ROOT/scripts/build_national_pokedex.py"

mkdir -p "$IOS_TARGET"
mkdir -p "$MAC_TARGET"

rm -rf "$IOS_TARGET"
rm -rf "$MAC_TARGET"

mkdir -p "$IOS_TARGET"
mkdir -p "$MAC_TARGET"

cp -R "$WEB_SOURCE"/. "$IOS_TARGET"
cp -R "$WEB_SOURCE"/. "$MAC_TARGET"

python3 "$ROOT/scripts/generate_native_pokedex_json.py"

echo "Synced website bundle into:"
echo "  $IOS_TARGET"
echo "  $MAC_TARGET"
