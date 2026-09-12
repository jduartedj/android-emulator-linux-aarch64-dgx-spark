# Reduced patched source: verify, extract and build

The source is already patched and includes the selected Linux ARM64 build inputs, corresponding library sources, licenses and frozen provenance. Historical releases remain unchanged. GitHub's automatic source ZIP is only the publication repository, not this source tree.

Download these exact files from [v0.2.0-unofficial](https://github.com/jduartedj/android-emulator-linux-aarch64-dgx-spark/releases/tag/v0.2.0-unofficial):

- [Source part 00](https://github.com/jduartedj/android-emulator-linux-aarch64-dgx-spark/releases/download/v0.2.0-unofficial/android-emulator-linux-aarch64-dgx-spark-unofficial-35.6.3-patched-source.tar.zst.part-00)
- [Source part 01](https://github.com/jduartedj/android-emulator-linux-aarch64-dgx-spark/releases/download/v0.2.0-unofficial/android-emulator-linux-aarch64-dgx-spark-unofficial-35.6.3-patched-source.tar.zst.part-01)
- [SHA256SUMS](https://github.com/jduartedj/android-emulator-linux-aarch64-dgx-spark/releases/download/v0.2.0-unofficial/SHA256SUMS)
- [ASSET-MANIFEST.json](https://github.com/jduartedj/android-emulator-linux-aarch64-dgx-spark/releases/download/v0.2.0-unofficial/ASSET-MANIFEST.json) (part lengths/digests)

Verify both parts before concatenation, then verify the aggregate. The commands fail on missing files, missing/duplicate checksum entries, malformed hashes or corruption. Run in a directory containing the downloaded files.

```bash
set -euo pipefail
verify_part() {
  local name="$1"
  test -f "$name"
  awk -v name="$name" '
    $2 == name {
      n++; line=$0
      if (NF != 2 || length($1) != 64 || $1 !~ /^[[:xdigit:]]+$/) bad=1
    }
    END { if (n != 1 || bad) exit 1; print line }
  ' SHA256SUMS > "$name.sha256"
  sha256sum -c "$name.sha256"
}

verify_part android-emulator-linux-aarch64-dgx-spark-unofficial-35.6.3-patched-source.tar.zst.part-00
verify_part android-emulator-linux-aarch64-dgx-spark-unofficial-35.6.3-patched-source.tar.zst.part-01
cat android-emulator-linux-aarch64-dgx-spark-unofficial-35.6.3-patched-source.tar.zst.part-00 \
    android-emulator-linux-aarch64-dgx-spark-unofficial-35.6.3-patched-source.tar.zst.part-01 > android-emulator-linux-aarch64-dgx-spark-unofficial-35.6.3-patched-source.tar.zst
printf '%s  %s\n' 441c99e8a140f4d388bc20629d651d22803de416c69da7150ff4b065e6bf8131 android-emulator-linux-aarch64-dgx-spark-unofficial-35.6.3-patched-source.tar.zst | sha256sum -c -
mkdir source
tar --zstd -xf android-emulator-linux-aarch64-dgx-spark-unofficial-35.6.3-patched-source.tar.zst -C source
```

Canonical archive: **2,647,263,684 bytes**. SHA-256: `441c99e8a140f4d388bc20629d651d22803de416c69da7150ff4b065e6bf8131`. Part digests and lengths are in [ASSET-MANIFEST.json](https://github.com/jduartedj/android-emulator-linux-aarch64-dgx-spark/releases/download/v0.2.0-unofficial/ASSET-MANIFEST.json) and [SHA256SUMS](https://github.com/jduartedj/android-emulator-linux-aarch64-dgx-spark/releases/download/v0.2.0-unofficial/SHA256SUMS). The aggregate is retained locally even when only its safe-size parts are uploaded; there is no full-fat source alternative.

After documented host prerequisites (`source/SOURCE-PROVENANCE/HOST-TOOLS.md`), build with the single offline entrypoint:

```bash
export QEMU_LD_PREFIX=/absolute/path/to/private/x86-library-root
JOBS=8 ./source/build-offline.sh /absolute/path/to/new-build-output
```

Use a new output directory outside source. Do not reapply patches, repo-sync or add excluded source as a fallback. The entrypoint does no source download; the verified build used network-disabled isolation, a fresh extraction, empty output and disabled object caches. It completed configure, compile, link, install and distribution. Test execution was disabled, not reported as passed. Native output still uses pinned x86 Python/CMake/Qt host tools during the build.

See SOURCE-CORRESPONDENCE.md, corrected notices/SBOM and full build evidence for scope and third-party source associations. No fresh Android benchmark, GPU feature or replacement runtime is implied.
