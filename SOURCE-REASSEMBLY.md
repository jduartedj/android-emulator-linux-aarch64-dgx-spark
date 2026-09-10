# Corresponding-source reassembly

Release source is split into parts smaller than GitHub's per-file limit.

```bash
cat android-emulator-linux-aarch64-dgx-spark-unofficial-35.6.3-source.tar.zst.part-* > source.tar.zst
sha256sum -c SHA256SUMS
mkdir source && tar --zstd -xf source.tar.zst -C source
```

The split archive records the exact checked-out base source and the portability/build patch. To reconstruct the source corresponding to the final SIGIPI-safe binary, also download `android-emulator-linux-aarch64-dgx-spark-unofficial-35.6.3-corresponding-source-supplement-1.tar.zst`, verify it with `SHA256SUMS`, and apply its canonical patch:

```bash
mkdir source-supplement
tar --zstd -xf android-emulator-linux-aarch64-dgx-spark-unofficial-35.6.3-corresponding-source-supplement-1.tar.zst   -C source-supplement
cd source/external/qemu
git apply ../../../source-supplement/patches/kvm-kick-arm64-shutdown-safe-sigipi.patch
python3 tests/test-kvm-kick-guard.py
```

The source archive excludes Git object caches and build outputs but contains all checked-out source/build inputs used by the recorded manifest. The supplement adds the final canonical local patch, its regression test, patch provenance, and the rejected predecessor clearly labeled as historical troubleshooting only. Together they are the complete corresponding source for the binary. The release checksum file records the complete source stream, every split part, and the supplement.
