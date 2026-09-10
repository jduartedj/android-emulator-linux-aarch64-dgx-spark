#!/usr/bin/env bash
set -euo pipefail
EMU=${1:-./emulator}
GUI="$EMU/qemu/linux-aarch64/qemu-system-aarch64"
HEADLESS="$EMU/qemu/linux-aarch64/qemu-system-aarch64-headless"
file "$EMU/emulator" "$GUI" "$HEADLESS"
file "$EMU/emulator" "$GUI" "$HEADLESS" | grep -q 'ARM aarch64'
"$EMU/emulator" -version
LDD_OUTPUT=$(LD_LIBRARY_PATH="$EMU/lib64:$EMU/lib64/qt/lib" ldd "$HEADLESS")
printf '%s\n' "$LDD_OUTPUT"
if grep -q 'not found' <<<"$LDD_OUTPUT"; then
  exit 1
fi
printf '%s  %s\n' \
  '2baee124da343882d48c24024c03ce32e04f338e91a4f1564b9fb1b34046d83e' "$EMU/emulator" \
  'e97cf42b32aa834264d7e5bc42ab5299b6ba89f586b97e245ecd656d6cc9f7b0' "$GUI" \
  'a840768428b0a7d28fa306146baacbfd7a50ec5543320a57cc6bd6b2cfc0792a' "$HEADLESS" | sha256sum -c -
