# Redistribution source and notices — packaging release v0.2.0

This is source-backed engineering documentation, not legal advice or compliance certification.

## Unchanged runtime, corrected source offering

The runtime archive remains the byte-identical unofficial Android Emulator 35.6.3 package. Its historical validation is unchanged; newly compiled validation outputs are not substituted. Historical releases, source assets and tags remain available and are not rewritten or removed by this packaging release.

The new release supplies only the reduced, already-patched source offering, with its frozen manifest, canonical fixes, offline entrypoint, corresponding library-source additions and required notices. [SOURCE-REASSEMBLY.md](SOURCE-REASSEMBLY.md) describes exact verification/extraction. GitHub's automatically generated source ZIP is only the publication repository, not the selected build tree.

## Corresponding source and modifications

Emulator/QEMU is GPLv2. The source package includes its exact pinned source, accepted portability fixes, canonical shutdown-safe SIGIPI fix and an explicitly separate minbuild BoringSSL test-target guard. That guard corrects historical r2 omitted test-fixture references; runtime ssl/crypto definitions are unchanged. Do not apply the rejected historical shutdown patch or double-apply any patch to the already-patched tree.

[Source correspondence](SOURCE-CORRESPONDENCE.md) and the machine-readable source/keep-drop manifests distinguish source revisions, prebuilt-object origins, final file hashes, package-byte matches and disclosed provenance limitations. Qt source modules, GNU libc/GCC runtime sources and packaging modifications, and patchelf source are included where required; permissive components retain their own applicable notice obligations. They are not all treated as having identical license terms.

The Qt shared-library mechanism and source/build/replacement instructions preserve the ability to modify and replace interface-compatible library code. The original environment for each third-party prebuilt is not independently attested, and bit-identical third-party reconstruction is not claimed as a condition of this source offering.

## Notice corrections

The unchanged binary retains its historical generated notices. [NOTICE/CORRECTIONS.md](NOTICE/CORRECTIONS.md), full license texts and the corrected component inventory accompany and clarify them:

- GNU libstdc++ uses GPLv3 with the GCC Runtime Library Exception, not the old LLVM/Apache label.
- The selected FFmpeg library is 4.4.2 and embeds GPL/x264-enabled configuration; its old 3.4.5 URL and LGPL-only summary are superseded.
- The nested archive named `glibc-2.29.tgz` contains glibc 2.31 and exact GCC9/10 cross-runtime packages, whose source and packaging are now supplied.
- SwiftShader legacy ARM64 GLES has its own exact prebuilt/source association, distinct from newer Vulkan components.

Retain upstream copyright, attribution and warranty notices as well as these corrections. Do not remove source obligations when redistributing the unchanged runtime or derived binaries.

## Validation scope

The release review evidence records the final archive's fresh-extraction checks and complete isolated configure/compile/link/install/distribution result. It is the authority for final build success; archive creation or configure alone is not proof. Test execution was disabled. No new Android benchmark, device-state change, NVIDIA driver/GPU integration or replacement runtime is part of this base packaging task.

Public upstream test fixtures and literal key-format markers are distinguished from user credentials by frozen-source identity checks; matched values are not emitted in reports. Prior proprietary fixture exclusions are preserved. No Google system images, Play services, AVD userdata, SDK credentials or private applications are included. Users obtain Android images and tools separately under their respective terms.
