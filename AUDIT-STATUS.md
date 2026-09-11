# Publication repair and verification — 2026-09-11

**Use source r2 + supplement 2 and `SHA256SUMS-r2`.** The initial publication
findings are resolved for this corrected offering, with the explicit scope and
limits below. The emulator binary and historical runtime evidence are unchanged.

## Resolved: unnecessary application/system-image test fixtures

The first audit identified 22 APK payloads under upstream `external/adt-infra`.
Recursive inspection then found an APK inside a test Python wheel, an APK in
each of two Qt source bundles, and Android system-image fixtures inside an
upstream test ZIP. These were real containers/payloads, not just filenames in
documentation. Source r2:

- removes all **22 direct APK payloads**;
- removes the unused test wheel containing one additional APK;
- removes the unused test ZIP containing Android system-image fixtures;
- removes the one APK member from each Qt bundle, retaining all other member
  contents, source licenses and notices;
- records exact excluded paths/digests, upstream revisions and transformed
  archive hashes in `manifests/source-r2-*.json` and source provenance.

This totals **25 direct/nested APK payloads**, plus the separate system-image
fixture container. The removed test payloads are absent from the retained
no-tests Ninja build graph; the build driver explicitly disables its eight
recorded test/sample tasks. Required host-tool prebuilts, emulator source,
portability changes, canonical KVM patch and notices remain available.

Omission is conservative because these test payloads are unnecessary and this
publication did not establish redistribution permission for each fixture. It is
not an allegation that upstream hosting was unlawful, and this audit is not a
legal compliance certification. The source offering is deliberately **no-tests**,
not an identical upstream tree or a guarantee that the entire upstream test suite
can run from the pruned archive.

See [COMPLIANCE.md](COMPLIANCE.md) and [source reassembly](SOURCE-REASSEMBLY.md).
The prior source stream SHA-256 was
`d5a383db5b38ade07dcdc5aedaad7cf3456addb5d414ab13ae5e56e4de1de614`;
current source r2 is `a23b34f58d401434c387e15ddab2081043b0b4cd75bd56751225d3deae5c69fc` (**10,186,159,362 bytes**).

## Resolved: explicit, verified host-tool prerequisite

The emulator/QEMU output is **native Linux AArch64**, while the pinned upstream
Python 3.10.3 and CMake 3.23.1 build tools are **x86-64**. The existing host handler
is Ubuntu QEMU user-mode. [HOST-TOOLS.md](HOST-TOOLS.md) now gives the exact
verified handler, Ubuntu package versions/checksums, private library-root setup
and smoke commands; it does not instruct readers to copy libraries into system
locations or overwrite binfmt configuration.

An isolated, network-disabled Ubuntu 24.04 ARM64 container successfully ran:

- the pinned Python and CMake through an explicitly supplied QEMU interpreter
  and Ubuntu package-derived x86-64 runtime root;
- selected build-related Python standard-library imports;
- a minimal CMake configure and its nested pinned-Python subprocess;
- the real emulator build driver's help, feature-list and task-list paths;
- instrumented construction of the recorded ARM64/minbuild/no-Qt-WebEngine
  configuration and eight disabled test/sample tasks, with task execution
  intercepted and `QEMU_LD_PREFIX` preserved by the real subprocess wrapper.

Evidence: `validation/host-tools-r2-validation.txt`,
`validation/host-tools-r2-smoke.txt`, and
`validation/host-tools-r2-driver-probe.txt`.

The complete pinned build manifest includes all **66** exact project revisions.
The older exported 57-project manifest omitted nine Linux host-tool projects;
it is preserved for historical provenance, while current build commands use
`manifests/manifest-build-pinned.xml`.

**Remaining limit, not an unfulfilled clean-room claim:** this repair did not
repeat a full emulator configure/compile/link on an untouched machine. It
verifies the compatibility prerequisite and argument/import paths, supplementing
the retained successful full-build evidence. No bit-identical clean-room rebuild,
universal ARM64-host support or all-native build-tool stack is claimed.

## Integrity and source correspondence

The current checksum file covers every current release payload and the complete
source aggregate. Public API digests/sizes are matched to fresh small-asset
downloads and independently hashed exact source parts; source streams and nested
Qt transformations are parsed and compared to their retained content manifests.
The source base plus canonical supplement patch passes the exact static KVM
regression and expected patched-source/test hashes.

The binary remains SHA-256
`aaa426635e9b760567931e98f2de260f6323d46855f54067eb1401061f80c265`
(94,213,418 bytes). Prior checks verified 207 packaged checksums, native
AArch64 launcher/GUI/headless binaries, bundled dependency resolution, and
offline version 35.6.3.0. The prior path-normalization comparison proved changed
ELF bytes are only the documented fixed-width diagnostic prefix replacement,
with unchanged executable `.text` sections. Historical runtime validation is
not relabeled as a fresh test of the repackaged bytes.

Source/member inventories and bounded recursive archive inspection identified no
remaining APK or Android-system-image payloads in the corrected offering. Known encrypted,
corrupt and decompression-stress fixtures in upstream compression-library tests
are documented scan limits, not executable build inputs or a claim that every
upstream byte was recursively decrypted. Required source notices remain intact.

## Publication history and claim boundaries

The stable release URL and `v0.1.0-unofficial` tag are unchanged. Corrected r2
assets supersede the old source/supplement/compliance/checksum assets only after
replacement verification. The binary, redacted runtime/build logs and component
SBOM are unchanged. Old private archives/reports and Git history are preserved;
current documentation supersedes older tagged/generated snapshots.

Appropriate claims: unofficial native AArch64 emulator output built on DGX Spark,
recorded API 36/KVM and clean-shutdown validation, published source/patches,
verified artifact checksums, and explicit host-tool compatibility. Do not claim
Google/NVIDIA endorsement, legal certification, new application benchmarks,
NVIDIA GPU rendering (validation used SwiftShader), or a new full clean-room
build. No Android device, emulator boot, application-project change or public
announcement was performed as part of this publication repair.
