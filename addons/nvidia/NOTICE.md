# Candidate notices and dependencies

- Shader translator/common/preprocessor source: ANGLE Project, BSD-style license in LICENSES/ANGLE.txt; source commit901e32aa9923b05c3a2af846f8a28fc79c93d0be from Android platform/external/angle.
- Legacy exported ShaderTranslator.h copied from the base's ANGLE prebuilt include source, under the accompanying ANGLE terms; used to preserve frozen host ABI. The base checkout's prebuilt patches identify ChromiumANGLE origin commit7d712e7d05418533fd90652ad089b3cacfcfca72, not the newer source resource layout.
- Chromium base helpers: source README.angle identifies Chromium revision28b5bbb227d331c01e6ff9b2f8729732135aadc7, Chromium BSD terms reproduced in LICENSES/Chromium.txt (retrieved from that exact revision). Individual source notices preserved.
- xxHash: BSD2-Clause, LICENSES/xxhash.txt; SMHasher/PMurHash: public-domain notices and applicable MIT terms in LICENSES/smhasher.txt. Original notices remain in corresponding source.
- New standalone helper scripts/build integration/test and documentation are offered under Apache License2.0, included as LICENSES/Apache-2.0.txt; modifications to existing ANGLE files retain their original applicable license. This is a proposed distribution, pending parent review.
- Existing base Emulator/QEMU is separate and remains under its own existing licensing/source obligations. No replacement of that binary or claim to relicense it.
- **No NVIDIA proprietary code/driver/runtime files, Google system image, guest disk, test APK/data, crash memory, credentials or signing key included.** NVIDIA OpenGL kernel/userspace libraries must already be legally installed by the operator and remain system dependencies. No endorsement by NVIDIA, Google or the ANGLE authors.
- Tested scope does not imply security hardening, all-app graphics correctness, Vulkan support or universal driver compatibility. Inspect exact patch/resource-field limitations and validation report before distribution.
