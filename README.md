# Android Emulator for Linux ARM64 on NVIDIA DGX Spark (unofficial)

> **Built natively and validated on NVIDIA DGX Spark.** This is an unofficial, source-built Android Emulator distribution for Linux `aarch64`. It is not an official Google, Android, or NVIDIA product and no endorsement is implied.

**Publication audit (2026-09-11): source-package blocker open.** The binary archive contains no APKs, but the split source archive includes 22 upstream APK fixtures, including a third-party game APK. Source redistribution review/cleanup and clean-host toolchain setup remain open; this release has not passed the final publication audit. See [AUDIT-STATUS.md](AUDIT-STATUS.md).

The first release builds Android Emulator 35.6.3 from Google's official `emu-master-dev` manifest and runs an Android 16 / API 36 ARM64 Google APIs image with KVM on NVIDIA DGX Spark.

**Build it yourself:** [DIY-COMPILATION.md](DIY-COMPILATION.md) is the canonical Ubuntu 24.04 ARM64 host-build guide, including exact dependencies, commands, patches, every verified failure, packaging, compliance, and validation.

## Pinned build recipe (host prerequisites required)

```bash
export WORK="$HOME/emulator-build"
export PUBLICATION=/path/to/android-emulator-linux-aarch64-dgx-spark
test -f "$PUBLICATION/manifests/manifest-build-pinned.xml"
mkdir -p "$WORK/src" && cd "$WORK/src"
repo init -u https://android.googlesource.com/platform/manifest \
  -b 1a75ee5c54d3b3161516ae27b6769a70e0ffcfca --depth=1 --partial-clone \
  --clone-filter=blob:limit=10M --no-clone-bundle
cp "$PUBLICATION/manifests/manifest-build-pinned.xml" .repo/manifests/pinned.xml
repo init -m pinned.xml --depth=1 --partial-clone \
  --clone-filter=blob:limit=10M --no-clone-bundle
repo sync -c -j8 --no-clone-bundle --no-tags --optimized-fetch --prune
cd external/qemu
git apply "$PUBLICATION/patches/linux-aarch64-build-fixes.patch"
git apply "$PUBLICATION/patches/kvm-kick-arm64-shutdown-safe-sigipi.patch"
python3 tests/test-kvm-kick-guard.py
./android/rebuild.sh --target linux_aarch64 --config release \
  --ccache /usr/bin/ccache --feature minbuild --feature no-qtwebengine \
  --cmake_option CMAKE_MAKE_PROGRAM=/usr/bin/ninja \
  --out "$WORK/build/objs" --dist "$WORK/build/dist" \
  --task-disable CTest --task-disable AccelerationCheck \
  --task-disable EmugenTest --task-disable GenEntriesTest \
  --task-disable CoverageReport --task-disable PackageSamples \
  --task-disable ZipIntegrationTests --task-disable IntegrationTest
```

Install the prerequisites and review capacity, KVM, manifest pinning, SDK registration, image installation, and verification steps in the [full DIY guide](DIY-COMPILATION.md) before running this excerpt.

## DIY compilation

You can build this emulator yourself on Ubuntu Linux ARM64, including NVIDIA DGX Spark. **Follow [`DIY-COMPILATION.md`](DIY-COMPILATION.md)** for the complete verified steps, capacity planning, KVM setup, encountered errors and fixes, caveats, validation, and reproducible release packaging.

## Why this matters

Official Linux SDK emulator packages are ordinarily distributed for x86-64 hosts. On an ARM64 DGX Spark, an ARM64 emulator host executable plus an ARM64 system image allows ARM64-on-ARM64 virtualization through KVM rather than host CPU translation. The validated process holds `/dev/kvm` through membership in the existing `kvm` group; this project does not recommend weakening `/dev/kvm` permissions.

## Validated DGX Spark environment

- NVIDIA DGX Spark with NVIDIA GB10 GPU; driver 580.173.02; CUDA 13.0 reported by `nvidia-smi`
- 20 ARM64 CPU cores: 10 Cortex-X925 and 10 Cortex-A725
- 121 GiB RAM
- Ubuntu 24.04.4 LTS, Linux `6.17.0-1032-nvidia`, `aarch64`
- Emulator 35.6.3.0, source revision `ae9d18d2b6261179fbd57fffec720a04f7bfb053`
- Manifest revision `1a75ee5c54d3b3161516ae27b6769a70e0ffcfca`

## Validation evidence

An isolated API 36 AVD booted with the native AArch64 headless QEMU executable and KVM (`/dev/kvm` open by the QEMU process), with:

- ADB online and `sys.boot_completed=1`
- Android 16, API 36, ABI `arm64-v8a`
- fingerprint `google/sdk_gphone64_arm64/emu64a:16/BE2A.250530.026.F3/13894323:userdebug/dev-keys`
- 1080×2340 at 440 dpi
- SELinux enforcing; writable isolated 8 GiB userdata
- no third-party packages in the clean inventory
- Perfetto v49.0 available in the guest
- a 10-second trace containing `track_event`, `android.surfaceflinger.frame`, and `android.surfaceflinger.frametimeline`
- native official Perfetto Trace Processor v58.2: 268 actual and 244 expected FrameTimeline rows, with no nonzero error or data-loss stats
- a 10-minute ADB stability probe (see `validation/`)

No application or benchmark APK is included in the **binary archive**. The clean-AVD validation did not install third-party packages; the source-archive fixture exception is documented in [AUDIT-STATUS.md](AUDIT-STATUS.md).

## Install the emulator

Extract the release archive into an Android SDK root so the resulting directory is `$ANDROID_SDK_ROOT/emulator`:

```bash
mkdir -p "$HOME/android-sdk"
tar --zstd -xf android-emulator-linux-aarch64-dgx-spark-unofficial-35.6.3.tar.zst -C "$HOME/android-sdk"
export ANDROID_SDK_ROOT="$HOME/android-sdk"
```

Verify it:

```bash
./scripts/verify-release.sh "$ANDROID_SDK_ROOT/emulator"
```

## Install Android 16 separately

Google system images, Google APIs, Play services, SDK tools, firmware, AVD userdata, and credentials are deliberately excluded. Obtain them separately from Google under Google's terms. Before these runtime
steps, supply command-line tools, Java, and host-compatible ADB as described in
[DIY guide §10](DIY-COMPILATION.md#10-install-api-36-and-create-the-avd):

```bash
"$ANDROID_SDK_ROOT/cmdline-tools/latest/bin/sdkmanager" \
  'system-images;android-36;google_apis;arm64-v8a'
```

This project validated revision 7 of the non-Play-Store Google APIs image. Do not redistribute that system image as part of this project.

Create an isolated phone AVD:

```bash
printf 'no\n' | "$ANDROID_SDK_ROOT/cmdline-tools/latest/bin/avdmanager" create avd \
  --name DgxSparkApi36Arm64 \
  --package 'system-images;android-36;google_apis;arm64-v8a' \
  --device pixel_5
```

## KVM and boot

Preserve normal device permissions and add only the intended user to the existing group:

```bash
sudo usermod -aG kvm "$USER"
sg kvm -c 'test -r /dev/kvm -a -w /dev/kvm'
```

Boot in a fresh group context:

```bash
sg kvm -c '"$ANDROID_SDK_ROOT/emulator/emulator" @DgxSparkApi36Arm64 \
  -no-window -no-audio -no-snapshot -no-boot-anim \
  -gpu swiftshader_indirect -feature -Vulkan \
  -feature -BluetoothEmulation -feature -Uwb -accel on -no-metrics'
```

The Vulkan, BluetoothEmulation, and Uwb feature overrides reflect the validated minimal/headless configuration. OpenGL ES uses bundled SwiftShader. The current build may log a harmless missing `libStubXlib.so` preload warning in headless mode.

## Reproduce the build

Follow [DIY-COMPILATION.md](DIY-COMPILATION.md), or run `scripts/build.sh` for its automated equivalent. It initializes Google's official manifest, checks out the recorded revisions, applies the portability/build patch and canonical shutdown-safe KVM patch, runs the static KVM regression, and invokes the release `linux_aarch64` build. The same-release corresponding source is the split base archive plus the small final-patch supplement; see `SOURCE-REASSEMBLY.md`.

## Compilation issues we encountered

This was not a warning-free upstream build. The full symptoms, log excerpts, diagnosis, exact patches, verification, and troubleshooting table are in [DIY-COMPILATION.md §9](DIY-COMPILATION.md#9-compilation-issues-we-encountered). In order, the verified issues were:

1. SDK Manager exposed ARM64 system images but no native Linux ARM64 host emulator package.
2. The bundled Chromium/depot-tools Ninja launcher rejected `aarch64`; system Ninja and `CMAKE_MAKE_PROGRAM=/usr/bin/ninja` were required, plus a nested-build launcher dispatch.
3. The official helper expected `/usr/aarch64-linux-gnu/lib/libstdc++.so.6`, while Ubuntu 24.04 used `/usr/lib/aarch64-linux-gnu/libstdc++.so.6`.
4. The shallow/tagless checkout produced nonfatal `git describe` warnings; immutable commits and emitted version metadata were recorded instead.
5. `minbuild` disabled Rust with a reduced-functionality warning; only the independently validated bounded feature set is claimed.
6. Native GCC found a missing direct `<thread>` include in `Snapshotter.cpp`.
7. The first ARM64 runtime segfaulted during virtio reset; GDB isolated a stale `current_cpu` path and the patch explicitly selects little-endian virtio for this ARM64-only minbuild.
8. Install emitted `aarch64-linux-gnu-strip ... lib.so: No such file` warnings despite exit 0; package, dependency, boot, KVM, ADB, Perfetto, and stability checks bounded the nonfatal conclusion.
9. Headless mode logs a missing optional `libStubXlib.so`; Vulkan and local Netsim Bluetooth/UWB were disabled, and SwiftShader OpenGL ES 3.0 was validated.
10. ADB transport naming differed between `127.0.0.1:5555` and `emulator-5554`; cleanup explicitly removes stale TCP transports.
11. Source, build, system image, ccache, and corresponding-source packaging required careful disk budgeting.
12. KVM group changes required `sg kvm` or a new login; `/dev/kvm` was never opened globally.
13. Clean shutdown could crash in `kvm_cpu_kick()` after a successful run. Minidump symbolization showed a stale `cpu->kvm_run` access: a null guard failed after a 30-minute hold, and forcing legacy SIGIPI alone failed because the release build removed the assertion while `kvm_ipi_signal()` still called `kvm_cpu_kick()`. The canonical patch forces AArch64 to the existing `KVM_SET_SIGNAL_MASK`/SIGIPI path and guards the handler with `current_cpu && kvm_immediate_exit`. It rebuilt successfully, passed the static regression, 20/20 lifecycle cycles, 10/10 one-minute probes, clean FrameTimeline/error statistics, `adb emu kill`, guest `reboot -p`, and zero new minidumps. The rejected patch is explicitly historical and must not be applied; rollback is an atomic directory swap to the retained pre-fix package.

The retained result was a native AArch64 emulator that booted API 36 with KVM, produced real FrameTimeline tables, passed the shutdown-safe KVM regression, completed 20/20 lifecycle cycles and a 10-minute ADB/KVM hold, then exited cleanly under both `adb emu kill` and guest `reboot -p` with no new minidump. Failed experimental commands are not presented as the tested recipe.

## Limitations

- This is a source build of an older emulator revision (35.6.3) because Google's public `aosp-emu-master-dev` CI grid exposed no downloadable ARM64 emulator ZIP at validation time.
- Vulkan was disabled for the validated run because the minbuild distribution does not bundle the Vulkan loader; SwiftShader OpenGL ES 3.0 was used.
- Bluetooth and UWB emulation were disabled because the minbuild configuration has no local Netsim service.
- The official Google Linux platform-tools package in the test SDK was x86-64 and ran through the host compatibility layer; the emulator and QEMU themselves were verified native AArch64.
- Application benchmarking is not represented here because no benchmark APK was supplied during emulator validation.

## Licensing and compliance

Android Emulator/QEMU is distributed under GPLv2, with bundled components under their respective licenses. The binary archive includes upstream `NOTICE.txt`, `NOTICE.csv`, and license material. This repository includes the exact patch, revision manifest, component/notice inventory, complete corresponding source release assets, and a redacted build/GDB log archive. See `LICENSES/`, `NOTICE/`, and `COMPLIANCE.md`.

These are source-backed license facts and operational compliance materials, not legal advice.

## Trademarks and affiliation

NVIDIA and DGX Spark are trademarks of NVIDIA Corporation. Android and Google are trademarks of Google LLC. All other marks belong to their owners. No logos are used. This project is unaffiliated with and not endorsed by Google or NVIDIA.
