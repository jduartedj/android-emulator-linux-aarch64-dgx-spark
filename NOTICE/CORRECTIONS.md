# Attribution corrections accompanying unchanged Emulator 35.6.3

The binary's historical generated notice is preserved in HISTORICAL-EMULATOR-NOTICE.txt. These corrections accompany it without modifying runtime bytes.

- GNU libstdc++ is GPL-3.0-or-later WITH GCC-exception-3.1, not LLVM/Apache. The top-level file exactly matches Ubuntu GCC-14 14.2.0-4ubuntu2~24.04.1; source and packaging are included.
- ARM64 FFmpeg is 4.4.2, not the stale historical 3.4.5 URL. Its actual static library embeds --enable-gpl and --enable-libx264; GPL-2.0-or-later applies to this configured library. The recorded source/patches, full license texts and original attribution material are supplied.
- The old-distribution compatibility archive is named glibc-2.29.tgz but contains Ubuntu GNU libc 2.31 and GNU GCC9/10 cross-runtime objects. 52 of its 53 regular members match exact official cross-package bytes; the remaining tcmalloc object is BSD-3-Clause. Complete glibc/GCC source and native/cross packaging source are included. See the source correspondence matrix.
- patchelf identifies 0.12; its GPL source is supplied. No additional source modification is evidenced. Source version association does not assert identical compiler output.
- SwiftShader legacy GLES source revision is d0851364a1c7ca750b1fb6c0558d9d6126424d1c, from exact prebuilt-origin blobs. Preserve Apache and applicable third-party notices; do not substitute newer Vulkan origins.
- Qt sources/modules, full LGPL/GPL texts and replacement context accompany this package. No restriction on library modification or reverse engineering for debugging such changes is introduced. The published source/header association is documented; a bit-identical Qt rebuild is not claimed.

The component inventory is source-backed engineering evidence, not legal certification. Preserve all applicable component notices and file-specific license choices.
