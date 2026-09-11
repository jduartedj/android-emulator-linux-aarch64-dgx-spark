# Corresponding-source reassembly

Release source is split into 19 parts (00 through 18), each smaller than GitHub's per-file limit. Download all 19 parts, the supplement, and `SHA256SUMS` into one directory. The other binary/log/SBOM assets are not needed for source-only verification.

```bash
set -euo pipefail
SOURCE=android-emulator-linux-aarch64-dgx-spark-unofficial-35.6.3-source.tar.zst
SUPPLEMENT=android-emulator-linux-aarch64-dgx-spark-unofficial-35.6.3-corresponding-source-supplement-1.tar.zst
# Verify every required part and the supplement before concatenating.
awk -v source="$SOURCE" -v supplement="$SUPPLEMENT" '
  index($2, source ".part-") == 1 || $2 == supplement { print }
' SHA256SUMS > source-inputs.sha256
test "$(wc -l < source-inputs.sha256)" -eq 20
sha256sum -c source-inputs.sha256
cat "$SOURCE".part-{00..18} > "$SOURCE"
# Preserve the exact aggregate filename recorded in SHA256SUMS.
awk -v source="$SOURCE" '$2 == source { print }' SHA256SUMS > source-aggregate.sha256
test "$(wc -l < source-aggregate.sha256)" -eq 1
sha256sum -c source-aggregate.sha256
zstd -t "$SOURCE"
mkdir source && tar --zstd -xf "$SOURCE" -C source
```

The split archive records the exact checked-out base source and the portability/build patch. To reconstruct the source corresponding to the final SIGIPI-safe binary, also download `android-emulator-linux-aarch64-dgx-spark-unofficial-35.6.3-corresponding-source-supplement-1.tar.zst`, verify it with `SHA256SUMS`, and apply its canonical patch:

```bash
mkdir source-supplement
tar --zstd -xf android-emulator-linux-aarch64-dgx-spark-unofficial-35.6.3-corresponding-source-supplement-1.tar.zst   -C source-supplement
cd source/external/qemu
GIT_CEILING_DIRECTORIES="$(pwd)" git apply \
  ../../../source-supplement/patches/kvm-kick-arm64-shutdown-safe-sigipi.patch
python3 tests/test-kvm-kick-guard.py
```

The source archive excludes Git object caches and build outputs but contains all checked-out source/build inputs used by the recorded manifest. The supplement adds the final canonical local patch, its regression test, patch provenance, and the rejected predecessor clearly labeled as historical troubleshooting only. Together they are the complete corresponding source for the binary. The release checksum file records the complete source stream, every split part, and the supplement.

Run these Bash commands from the download directory. The base already includes the portability/build patch: do not apply it twice. The aggregate is 9,439,929,305 bytes with SHA-256 `d5a383db5b38ade07dcdc5aedaad7cf3456addb5d414ab13ae5e56e4de1de614`. Earlier archived instructions used the shortened filename `source.tar.zst`, which does not match the checksum manifest; use the commands above.

The archived `SOURCE-PROVENANCE/reproduce-build.sh` is a historical helper with publication-repository-relative paths, not a standalone entry point inside the extracted source tree. Use the current [DIY guide](DIY-COMPILATION.md) for the direct build command and prerequisites, or the current publication repository's `scripts/build.sh` for a new pinned checkout.

The Git ceiling keeps `git apply` from discovering an unrelated enclosing checkout if the download directory is inside another repository; otherwise Git may silently skip these paths.
