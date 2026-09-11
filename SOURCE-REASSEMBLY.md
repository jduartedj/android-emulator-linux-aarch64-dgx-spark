# Corresponding-source r2 reassembly

Use the current **source r2 + supplement 2** assets from the same
[v0.1.0-unofficial release](https://github.com/jduartedj/android-emulator-linux-aarch64-dgx-spark/releases/tag/v0.1.0-unofficial).
Download all **20 parts**, supplement 2, and `SHA256SUMS-r2` into a
new directory. Older source parts/supplement/checksum files are superseded.

Run these commands in **Bash** from that download directory:

```bash
set -euo pipefail
SOURCE=android-emulator-linux-aarch64-dgx-spark-unofficial-35.6.3-source-r2.tar.zst
SUPPLEMENT=android-emulator-linux-aarch64-dgx-spark-unofficial-35.6.3-corresponding-source-supplement-2.tar.zst
PART_COUNT=20
awk -v source="$SOURCE" -v supplement="$SUPPLEMENT" '
  index($2, source ".part-") == 1 || $2 == supplement { print }
' SHA256SUMS-r2 > source-inputs.sha256
test "$(wc -l < source-inputs.sha256)" -eq "$((PART_COUNT + 1))"
sha256sum -c source-inputs.sha256
for index in $(seq 0 "$((PART_COUNT - 1))"); do
  printf -v part '%s.part-%02d' "$SOURCE" "$index"
  cat "$part"
done > "$SOURCE"
awk -v source="$SOURCE" '$2 == source { print }' SHA256SUMS-r2 > source-aggregate.sha256
test "$(wc -l < source-aggregate.sha256)" -eq 1
sha256sum -c source-aggregate.sha256
zstd -t "$SOURCE"
mkdir source source-supplement
tar --zstd -xf "$SOURCE" -C source
tar --zstd -xf "$SUPPLEMENT" -C source-supplement
cd source/external/qemu
GIT_CEILING_DIRECTORIES="$(cd .. && pwd)" git apply \
  ../../../source-supplement/patches/kvm-kick-arm64-shutdown-safe-sigipi.patch
python3 tests/test-kvm-kick-guard.py
```

Expected source aggregate: **10,186,159,362 bytes**, SHA-256
`a23b34f58d401434c387e15ddab2081043b0b4cd75bd56751225d3deae5c69fc`.

The base already contains the portability/build patch; **do not apply it twice**.
Supplement 2 adds the canonical final KVM patch (which also creates its static
regression), the complete 66-project pinned manifest, corrected build/reassembly
instructions, exact fixture-exclusion/normalization records and host-tool setup.
The failed legacy patch is historical negative evidence only: do not apply it.
The Git ceiling prevents accidentally discovering an unrelated enclosing Git
checkout and silently skipping patch paths.

## Build the extracted source

Follow the native dependencies and [host-tool setup](HOST-TOOLS.md), keeping
`QEMU_LD_PREFIX` exported. From the patched `source/external/qemu` directory, use
the exact `android/rebuild.sh` command in [DIY guide §7](DIY-COMPILATION.md#7-configure-and-build),
with dedicated absolute output/dist directories. For this already extracted tree,
set `SRC="$(cd ../.. && pwd)"` while in `source/external/qemu`, rather than
using the fresh-checkout example `SRC="$WORK/src"` in the host-tool guide. Set
`WORK` to a separate absolute build-output directory. No Git object cache is needed
for this source build; shallow/Git-description warnings are documented.

The archived `SOURCE-PROVENANCE/reproduce-build.sh` is preserved historical
provenance, not a standalone entry point for the extracted tree. For a new
upstream checkout instead, use the current publication repository's
`scripts/build.sh` and `manifests/manifest-build-pinned.xml`.

## What changed in r2

The prior source aggregate was 9,439,929,305 bytes, SHA-256
`d5a383db5b38ade07dcdc5aedaad7cf3456addb5d414ab13ae5e56e4de1de614`.
Source r2 is explicitly a **no-tests corresponding-source offering**, not an
identical upstream tree:

- 22 direct upstream APK fixtures removed;
- an unused Python test wheel containing one APK removed;
- an unused test ZIP containing Android system-image fixtures removed;
- one unused Android APK member removed from each of two Qt source bundles;
  every other member's contents are preserved, while archive compression changes;
- precise exclusion/normalization provenance added under `SOURCE-PROVENANCE/`.

The required source/build inputs, host-tool prebuilts, source licenses/notices,
portability changes and canonical KVM patch remain available. Exact path,
upstream-revision and SHA-256 records are in `manifests/` and supplement 2.
Upstream test-fixture omission is conservative; it is not a claim that upstream
hosting was unlawful. The binary archive, its SBOM and runtime evidence are
unchanged. See [COMPLIANCE.md](COMPLIANCE.md) and [AUDIT-STATUS.md](AUDIT-STATUS.md).
