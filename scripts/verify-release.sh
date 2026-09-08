#!/usr/bin/env bash
set -euo pipefail
EMU=${1:-./emulator}
file "$EMU/emulator" "$EMU/qemu/linux-aarch64/qemu-system-aarch64-headless"
file "$EMU/emulator" | grep -q 'ARM aarch64'
file "$EMU/qemu/linux-aarch64/qemu-system-aarch64-headless" | grep -q 'ARM aarch64'
"$EMU/emulator" -version
sha256sum "$EMU/emulator" "$EMU/qemu/linux-aarch64/qemu-system-aarch64-headless" "$EMU/NOTICE.txt" "$EMU/NOTICE.csv"
