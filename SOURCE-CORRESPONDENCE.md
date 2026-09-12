# Corresponding-source and license coverage for the unchanged runtime

**Final-archive build and source-offering review passed for v0.2.0-unofficial.** This coverage record supersedes earlier source-offering limitations; historical records are preserved. It is not a claim of bit-identical rebuilding of every prebuilt or legal certification.

## Runtime identity

The runtime remains Android Emulator 35.6.3, archive 94,213,418 bytes, SHA-256 `aaa426635e9b760567931e98f2de260f6323d46855f54067eb1401061f80c265`. It was freshly hashed; no new build output is substituted. The final source archive's exact digest/build result is recorded separately after completion.

## Selected emulator source and modifications

QEMU source `ae9d18d2b6261179fbd57fffec720a04f7bfb053`, the frozen complete project manifest and canonical portability/shutdown patches are supplied. The final source tree is already patched. A new, separately supplied minbuild guard omits only BoringSSL test targets referencing public test-key fixtures already excluded by historical source r2; it does not alter the runtime ssl/crypto target definitions.

Retained source/prebuilt paths are mapped to upstream Git object IDs, historical r2 hashes, final content hashes, types/modes and explicit keep/drop reasons. Added source archives carry official revision/URL/digest provenance. The previous all-in source archive is not republished as an alternative in the new release, and no historical release is deleted.

## Qt 6.5.3

- Supplied AOSP emulator-prebuilts source superproject `c4ae34cce9a2e8031eecd7c7d58440ea0f91d1c7`; tree equals upstream `f4a01d798aad2a5779e4bb19b6299eefc7d18181`.
- Exact selected module gitlinks: qtbase `372eaedc5b8c771c46acc4c96e91bbade4ca3624`, qtsvg `220cd8c6261552f0fcf47061c64f862adae29b55`, qtimageformats `4f89d7ef7d4f30c1907915435b432d957b62b7ff`. These module source trees are included, not just gitlink placeholders.
- Exact prebuilt commit `7d360214a0308888671cd5b672fe5d2747d8a228` identifies ARM64 build recipe change 3080856. The included builder specifies the AndroidEmu infix, platform options and post-install steps. **1,224 installed headers match the offered source bytes**; remaining headers are generated configuration/export/version/compatibility headers, not evidenced handwritten modifications.
- The source import is later than the prebuilt build. That timing is disclosed; no original clean-tree attestation or bit-for-bit Qt reconstruction is claimed. No additional handwritten Qt source patch is evidenced by the inspected source/header/build records.
- Full LGPLv3/GPLv3 and module/third-party license material is included. The emulator uses dynamic shared Qt libraries; `source/SOURCE-PROVENANCE/QT-REPLACEMENT.md` in the [extracted source](SOURCE-REASSEMBLY.md) explains compatible replacement/relinking and introduces no restriction on library modification or reverse engineering for debugging those changes. LGPL obligations are not being confused with a demand for identical compiler output.
- Qt's separately copied system libraries retain their file-specific licenses/notices; do not treat all of them as LGPL Qt code merely because they share the directory.

## GNU runtime source: exact nested cross-package binding

The runtime's misleadingly named `glibc-2.29.tgz` contains libc 2.31 and a mix of GNU runtime versions. Package comparisons resolved the previously unknown origins:

| Distributed material | Exact matched package/source association | Included source |
|---|---|---|
| Top-level libstdc++.so.6.0.33 | Ubuntu GCC-14 `14.2.0-4ubuntu2~24.04.1`; SHA equals runtime manifest | Full GCC-14 original + Ubuntu packaging |
| Nested libstdc++.so.6.0.28, libgcc, atomic/gomp/itm/lsan/tsan/ubsan | Runtime packages `10.2.0-5ubuntu1~20.04cross1`; source `gcc-10-cross (6ubuntu3)` with GCC-10 `10.2.0-5ubuntu1~20.04` | Full GCC-10 original + Ubuntu patches + cross packaging |
| Nested libasan.so.5.0.0 | `9.3.0-17ubuntu1~20.04cross2`; source `gcc-9-cross (21ubuntu4)` | Full GCC-9 original + Ubuntu patches + cross packaging |
| Nested GNU libc libraries, static libraries and startup objects | `libc6[-dev]-arm64-cross 2.31-0ubuntu7cross1`; source `cross-toolchain-base (43ubuntu3)` with glibc `2.31-0ubuntu7` | Full glibc original + Ubuntu patches + cross packaging |

**52 of 53 regular nested members match exact official package bytes.** The sole remaining member is tcmalloc, covered by the retained BSD-3-Clause notice; BSD redistribution does not impose the same corresponding-source requirements. No claim of its exact build version is invented.

GNU runtime copyright, GPLv3 and GCC Runtime Library Exception are included. glibc retains LGPL2.1 and other file-specific terms. Official source package digests were checked against HTTPS .dsc SHA-256 records; source-signing-key authentication is not claimed beyond that stated verification. The full sources are supplied rather than relying solely on moving URLs or an unfulfilled source offer.

## Other components

- **FFmpeg:** actual ARM64 static-library configuration embeds `--enable-gpl` and `--enable-libx264`; version headers identify 4.4.2. The supplied existing 4.4.2/x264 source/patch material and GPL notices replace the historical stale 3.4.5 attribution and misleading LGPL-only summary. Official update association has 92 overlapping file blob/mode matches.
- **patchelf:** packaged tool identifies 0.12. Standard upstream tag 0.12 source and GPLv3-or-later text are supplied. No separate local source modification is evidenced; identical historical tool output bytes are not claimed.
- **SwiftShader legacy ARM64 GLES:** exact prebuilt blobs map to origin commit `9326422a5dbb98b87acdc486e0afd3ed7a27071d`, naming source `d0851364a1c7ca750b1fb6c0558d9d6126424d1c`. Apache-2.0 notices and applicable third-party attributions are retained. An unrelated Vulkan update is not used as its origin.
- Other shipped components retain their source/archives/notices from the frozen selected tree and generated inventory, with the corrections here and in `NOTICE/CORRECTIONS.md`. No proprietary system images or SDK runtime images are added.

## Verification boundaries

The complete selected emulator build passed validation from the final freshly extracted source archive with disabled network, an empty output, explicit prerequisite mounts and no original/excluded source fallback. That result is not a fresh Android boot/GPU/benchmark test. Historical runtime evidence remains tied to the unchanged binary. Source/header/package associations and documented modifications support the source offering; they do not imply original build-system attestation for every third-party binary.
