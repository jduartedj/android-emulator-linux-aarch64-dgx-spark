# Corresponding-source reassembly

Release source is split into parts smaller than GitHub's per-file limit.

```bash
cat android-emulator-linux-aarch64-dgx-spark-unofficial-35.6.3-source.tar.zst.part-* > source.tar.zst
sha256sum -c SHA256SUMS
mkdir source && tar --zstd -xf source.tar.zst -C source
```

The source archive excludes Git object caches and build outputs but contains all checked-out source/build inputs used by the recorded manifest, plus the exact patch and build metadata. The release checksum file records both the complete stream and every split part.
