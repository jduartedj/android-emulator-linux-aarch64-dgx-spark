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
  '615f87a5c524acfe6209d462e71e4c9423b3c7375fe15196163c4dac5a049be3' "$EMU/emulator" \
  '3c90e0313ec5808a38b5d54cb50c6f0928af0080206adf1d711b33a2440855e5' "$GUI" \
  '42d52307362822cd1cfdf59b3f872660a4bc86b6a743cfc1000cf4ec69d3ff81' "$HEADLESS" | sha256sum -c -
