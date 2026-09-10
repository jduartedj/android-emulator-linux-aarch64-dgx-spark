#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT=$(cd "$(dirname "$0")/.." && pwd)
ROOT=${1:-"$PWD/work"}
JOBS=${JOBS:-$(nproc)}
mkdir -p "$ROOT/src" "$ROOT/out" "$ROOT/dist"
cd "$ROOT/src"
repo init -u https://android.googlesource.com/platform/manifest -b emu-master-dev --depth=1 --partial-clone --clone-filter=blob:limit=10M --no-clone-bundle
cp "$PROJECT_ROOT/manifests/manifest-synced.xml" .repo/manifests/pinned.xml
repo init -m pinned.xml --depth=1 --partial-clone --clone-filter=blob:limit=10M --no-clone-bundle
repo sync -c -j"$JOBS" --no-clone-bundle --no-tags --optimized-fetch --prune
cd external/qemu
git apply "$PROJECT_ROOT/patches/linux-aarch64-build-fixes.patch"
git apply "$PROJECT_ROOT/patches/kvm-kick-arm64-shutdown-safe-sigipi.patch"
python3 tests/test-kvm-kick-guard.py
./android/rebuild.sh --target linux_aarch64 --config release --ccache /usr/bin/ccache \
  --feature minbuild --feature no-qtwebengine \
  --cmake_option CMAKE_MAKE_PROGRAM=/usr/bin/ninja \
  --out "$ROOT/out" --dist "$ROOT/dist" \
  --task-disable CTest --task-disable AccelerationCheck \
  --task-disable EmugenTest --task-disable GenEntriesTest \
  --task-disable CoverageReport --task-disable PackageSamples \
  --task-disable ZipIntegrationTests --task-disable IntegrationTest
