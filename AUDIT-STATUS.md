# Final publication audit — 2026-09-11

**Outcome: blocked for announcement by source-package contents and an unverified clean-host build prerequisite.**

The release binary and checksums pass the fresh packaging checks, but the current
split corresponding-source archive contains **22 APK containers** under
`external/adt-infra/`. All contain an Android manifest; 21 contain JAR signing
blocks. These are upstream test fixtures, not applications added by this project.
Upstream presence alone is not proof of redistribution permission.

One concrete example is `external/adt-infra/emu_test/utils/apks/BestFiends.apk`:

- size: 94,101,433 bytes
- SHA-256: `a690e8dfeffd625562cd0e62ce225378541cf3e530bd28d13742aaa221bcc7b3`
- real APK container: Android manifest, DEX bytecode, 5,886 ZIP entries, and
  `META-INF/CERT.RSA`; Java's verifier flags its legacy signature algorithm as
  disabled, rather than establishing a currently valid signature.

The affected source stream is 9,439,929,305 bytes, SHA-256
`d5a383db5b38ade07dcdc5aedaad7cf3456addb5d414ab13ae5e56e4de1de614`.
The fixtures are not needed for the recorded no-tests emulator build. Remove
unnecessary application fixtures from a corrected source offering, preserve the
required build inputs/licenses/notices, and recheck the source inventory and
checksums before clearing the announcement. This is an operational publication
finding, not a legal determination.

## Clean-host build prerequisite

The recorded emulator binaries are native AArch64, but the upstream build
entry point explicitly runs a bundled x86-64 Python executable and the driver
uses bundled x86-64 CMake. The validation host already had an x86-64 execution
compatibility layer. The earlier Ubuntu package recipe did not install or
explain that prerequisite, so it was not a complete untouched-ARM64 build guide.
No clean-host compatibility setup or native-tool alternative was validated in
this packaging-only audit; that remains a reproducibility blocker.

The old exported manifest also omitted nine Linux-only grouped projects,
including Python and CMake. The new `manifests/manifest-build-pinned.xml` combines
all 66 recorded revisions, preserving the historical manifest unchanged. The
build script and copyable commands now use that complete pinned manifest, and
the guide explicitly calls out the remaining host-tool prerequisite.

## Checks that passed

- Public repository and published, non-draft/non-prerelease
  `v0.1.0-unofficial`; 25 assets.
- All 25 GitHub SHA-256 digests and sizes verified against freshly downloaded
  small assets/binary or independently rehashed retained source parts.
- All 19 parts and the concatenated source checksum match `SHA256SUMS`.
- Binary archive integrity, packaged-file checksums, native AArch64 launcher/GUI/
  headless executables, package-aware shared-library resolution, and offline
  launcher `-version` reporting 35.6.3.0.
- Exact canonical KVM patch applies to the archived base; its static regression
  and the expected patched-source/test hashes pass.
- Compared with the retained validated build, ELF byte changes are exactly the
  documented equal-length diagnostic-path replacement; executable `.text`
  sections are unchanged. The FlatBuffers pkg-config metadata is relocatable.

No rebuild, emulator boot, Android device use, application test, or performance
benchmark was performed during this publication audit. Historical runtime
validation must not be described as a new runtime test of the repackaged bytes.

## Documentation corrections

Use the current [source-reassembly instructions](SOURCE-REASSEMBLY.md) and
[pinned build guide](DIY-COMPILATION.md). Earlier archived instructions used a
shortened aggregate filename that does not match `SHA256SUMS`, and their quick
build examples followed a moving manifest branch. The current instructions
verify only the required source inputs before checking the exact aggregate
filename and explicitly pin the recorded source revisions.

The existing release tag, source/binary assets, and historical validation have
not been rewritten. The compliance bundle and generated tag snapshot preserve
the older documentation; this current audit notice and corrected main-branch
guides supersede those instructions, not the recorded build identities.
