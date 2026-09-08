# Android Emulator for Linux ARM64 on NVIDIA DGX Spark (unofficial)

> **Built natively and validated on NVIDIA DGX Spark.** This is an unofficial, source-built Android Emulator distribution for Linux `aarch64`. It is not an official Google, Android, or NVIDIA product and no endorsement is implied.

The first release builds Android Emulator 35.6.3 from Google's official `emu-master-dev` manifest and runs an Android 16 / API 36 ARM64 Google APIs image with KVM on the NVIDIA DGX Spark host named Judith.

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

The isolated AVD `DrinkingModeApi36Arm64Judith` booted with the native AArch64 headless QEMU executable and KVM (`/dev/kvm` open by the QEMU process), with:

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

No Drinking Mode APK or benchmark APK is included or installed.

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

Google system images, Google APIs, Play services, SDK tools, firmware, AVD userdata, and credentials are deliberately excluded. Obtain them separately from Google under Google's terms:

```bash
"$ANDROID_SDK_ROOT/cmdline-tools/latest/bin/sdkmanager" \
  'system-images;android-36;google_apis;arm64-v8a'
```

This project validated revision 7 of the non-Play-Store Google APIs image. Do not redistribute that system image as part of this project.

Create an isolated phone AVD:

```bash
printf 'no\n' | "$ANDROID_SDK_ROOT/cmdline-tools/latest/bin/avdmanager" create avd \
  --name DrinkingModeApi36Arm64Judith \
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
sg kvm -c '"$ANDROID_SDK_ROOT/emulator/emulator" @DrinkingModeApi36Arm64Judith \
  -no-window -no-audio -no-snapshot -no-boot-anim \
  -gpu swiftshader_indirect -feature -Vulkan \
  -feature -BluetoothEmulation -feature -Uwb -accel on -no-metrics'
```

The Vulkan, BluetoothEmulation, and Uwb feature overrides reflect the validated minimal/headless configuration. OpenGL ES uses bundled SwiftShader. The current build may log a harmless missing `libStubXlib.so` preload warning in headless mode.

## Reproduce the build

Run `scripts/build.sh`. It initializes Google's official manifest, checks out the recorded revisions, applies `patches/linux-aarch64-build-fixes.patch`, and invokes the release `linux_aarch64` build. The same-release complete corresponding-source archive is supplied as split release assets; see `SOURCE-REASSEMBLY.md`.

## Limitations

- This is a source build of an older emulator revision (35.6.3) because Google's public `aosp-emu-master-dev` CI grid exposed no downloadable ARM64 emulator ZIP at validation time.
- Vulkan was disabled for the validated run because the minbuild distribution does not bundle the Vulkan loader; SwiftShader OpenGL ES 3.0 was used.
- Bluetooth and UWB emulation were disabled because the minbuild configuration has no local Netsim service.
- The official Google Linux platform-tools package in the test SDK was x86-64 and ran through the host compatibility layer; the emulator and QEMU themselves were verified native AArch64.
- P3-2 app benchmarking is not represented here because no authorized benchmark APK was supplied during emulator validation.

## Licensing and compliance

Android Emulator/QEMU is distributed under GPLv2, with bundled components under their respective licenses. The binary archive includes upstream `NOTICE.txt`, `NOTICE.csv`, and license material. This repository includes the exact patch, revision manifest, component/notice inventory, and complete corresponding source release assets. See `LICENSES/`, `NOTICE/`, and `COMPLIANCE.md`.

These are source-backed license facts and operational compliance materials, not legal advice.

## Trademarks and affiliation

NVIDIA and DGX Spark are trademarks of NVIDIA Corporation. Android and Google are trademarks of Google LLC. All other marks belong to their owners. No logos are used. This project is unaffiliated with and not endorsed by Google or NVIDIA.
