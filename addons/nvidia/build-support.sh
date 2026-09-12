#!/usr/bin/env bash
# Build only the optional open-source support library; no base/driver mutation.
set -euo pipefail
SOURCE=${1:?Usage: build-support.sh /path/to/corresponding-source/angle /path/to/NEW-build-directory}
OUT=${2:?Specify a new build directory outside the source/base SDK}
[[ $(uname -m) == aarch64 ]] || { echo 'Native Linux aarch64 build required' >&2; exit 1; }
[[ ! -e "$OUT" ]] || { echo 'Refusing existing output directory' >&2; exit 1; }
cmake -S "$SOURCE" -B "$OUT" -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build "$OUT" --target shadertranslator -j4
file "$OUT/libshadertranslator.so"
HERE=$(cd -- "$(dirname -- "$0")" && pwd)
python3 "$HERE/normalize-diagnostics.py" "$OUT/libshadertranslator.so" "$OUT/libshadertranslator-public.so" "$OUT/public-normalization.json"
sha256sum "$OUT/libshadertranslator-public.so"
printf 'Built support library plus fixed-width public diagnostic normalization. Raw build retained; validate public output before separate addon/lib placement. No base files changed.\n'
