# Android Emulator for Linux ARM64

A **native AArch64 Android Emulator with KVM**, validated on NVIDIA DGX Spark / Ubuntu 24.04. Unofficial **35.6.3** build—not the latest emulator or an endorsed Google/NVIDIA product.

**[Download][binary] · [Install](#install) · [Build](#build-from-source) · [Limitations](#compatibility-and-limitations) · [Troubleshooting](DIY-COMPILATION.md#13-troubleshooting-table)**

The ready-to-run emulator is a **single download**; source archives are optional for rebuilding or auditing. Android system images and SDK tools are obtained separately.

| I want to… | Start here |
| --- | --- |
| Run Android | [Download the emulator][binary] and [checksums][checksums], then follow the installation steps below |
| Build it myself | [DIY compilation](DIY-COMPILATION.md) and [host-tool prerequisites](HOST-TOOLS.md) |
| Inspect the source | [Reduced patched source and reassembly](SOURCE-REASSEMBLY.md), [provenance](COMPLIANCE.md), and [release assets][release] |

## Install

### 1. Check the host

Requires Linux `aarch64`, KVM, Bash, curl, CA certificates, GNU tar, zstd, coreutils, awk, `file` and `ldd`. Android boot additionally requires compatible **Java, SDK command-line tools and host-compatible ADB**, supplied separately; see [runtime prerequisites](DIY-COMPILATION.md#10-install-api-36-and-create-the-avd).

Run blocks in order in the **same Bash shell**. Stop if a check fails:

```bash
set -euo pipefail
test "$(uname -m)" = aarch64
for tool in curl tar zstd sha256sum awk file ldd; do command -v "$tool"; done
test -r /dev/kvm && test -w /dev/kvm
```

KVM denied? Inspect the device/group, arrange membership in the existing `kvm` group, then log out/in. Preserve normal permissions: [KVM setup](DIY-COMPILATION.md#4-kvm-without-weakening-device-permissions).

### 2. Download and verify before extracting

Download into a fresh directory; verify **only the binary**, not absent source parts:

```bash
DOWNLOAD_DIR=$(mktemp -d "$HOME/emulator-download.XXXXXX")
cd "$DOWNLOAD_DIR"
RELEASE=https://github.com/jduartedj/android-emulator-linux-aarch64-dgx-spark/releases/download/v0.2.0-unofficial
ARCHIVE=android-emulator-linux-aarch64-dgx-spark-unofficial-35.6.3.tar.zst
curl -fL --proto '=https' --proto-redir '=https' -o "$ARCHIVE" "$RELEASE/$ARCHIVE"
curl -fL --proto '=https' --proto-redir '=https' -o SHA256SUMS "$RELEASE/SHA256SUMS"
awk -v name="$ARCHIVE" '
  $2 == name {
    n++; line=$0
    if (NF != 2 || length($1) != 64 || $1 !~ /^[[:xdigit:]]+$/) bad=1
  }
  END { if (n != 1 || bad) exit 1; print line }
' SHA256SUMS > binary.sha256
sha256sum -c binary.sha256
```

Expected binary SHA-256: `aaa426635e9b760567931e98f2de260f6323d46855f54067eb1401061f80c265`. Checksums detect corruption; they are not an independent signature of the publisher.

### 3. Extract into a new SDK root and check the package

This creates a fresh SDK root. Keep it for image/tool setup below. **Back up your emulator first** if using an existing SDK instead.

```bash
ANDROID_SDK_ROOT=$(mktemp -d "$HOME/android-sdk-arm64.XXXXXX")
export ANDROID_SDK_ROOT
tar --zstd -xf "$ARCHIVE" -C "$ANDROID_SDK_ROOT"
printf 'SDK root: %s\n' "$ANDROID_SDK_ROOT"
export PATH="$ANDROID_SDK_ROOT/emulator:$PATH"
curl -fL --proto '=https' --proto-redir '=https' -o verify-release.sh \
  https://raw.githubusercontent.com/jduartedj/android-emulator-linux-aarch64-dgx-spark/6d3b62404b0b8e9c67e1dcded9f709cb3eca7753/scripts/verify-release.sh
```

Inspect the downloaded [script](scripts/verify-release.sh), then run it. **No Git clone needed.** It checks executable hashes, architecture/version and headless libraries—not boot:

```bash
bash "$DOWNLOAD_DIR/verify-release.sh" "$ANDROID_SDK_ROOT/emulator"
```

### 4. Create an Android ARM64 AVD and boot

Follow [SDK/image/AVD setup](DIY-COMPILATION.md#10-install-api-36-and-create-the-avd) in the **same SDK root**: install command-line tools under `cmdline-tools/latest`, supply Java/ADB, accept Google’s terms, and create `DgxSparkApi36Arm64` using `system-images;android-36;google_apis;arm64-v8a`. Use a new AVD name if it exists. See [package registration](DIY-COMPILATION.md#91-sdk-manager-had-no-linux-arm64-emulator-package) if required. Validation used image revision 7; current downloads may differ.

With that AVD ready and KVM accessible:

```bash
"$ANDROID_SDK_ROOT/emulator/emulator" @DgxSparkApi36Arm64 \
  -no-window -no-audio -no-snapshot -no-boot-anim \
  -gpu swiftshader_indirect -feature -Vulkan \
  -feature -BluetoothEmulation -feature -Uwb -accel on -no-metrics
```

Use host-compatible ADB in another shell for [boot checks and shutdown](DIY-COMPILATION.md#11-boot-and-validate). The validated Google platform-tools were **x86-64 under a pre-existing compatibility layer**, not native ARM64 tools bundled here.

## Optional NVIDIA GPU extra

The base download and default SwiftShader path above are unchanged. A separate, [experimental addon v0.1.0](https://github.com/jduartedj/android-emulator-linux-aarch64-dgx-spark/releases/tag/nvidia-opengl-addon-v0.1.0) provides opt-in NVIDIA OpenGL support, tested on DGX Spark with the existing NVIDIA 580.173.02 driver—**no driver upgrade was required**. See the [GPU benchmark results and limitations](docs/GPU-BENCHMARKS.md) and [addon installation, verification and rollback guide](addons/nvidia/INSTALL.md). Use separate GPU and software-rendered AVDs; the addon is not an in-place AVD migration guarantee.

## Compatibility and limitations

| Area | Validated scope / limitation |
| --- | --- |
| Host and guest | DGX Spark, Ubuntu 24.04.4, Linux `6.17.0-1032-nvidia`; native AArch64 emulator/QEMU, Android 16 / API 36 `arm64-v8a`, KVM. Other hosts unvalidated. |
| Version | 35.6.3.0; no current upstream feature/security parity claimed. |
| Graphics and UI | Headless, **CPU SwiftShader OpenGL ES 3.0**, not NVIDIA GPU rendering. GUI QEMU included; full GUI unvalidated. |
| Reduced features | `minbuild`, no Qt WebEngine, Rust-dependent functionality omitted; Vulkan, Bluetooth and UWB disabled for the validated path. Audio and snapshots were not exercised. |
| Build tools | Pinned **x86-64 Python/CMake** need QEMU user-mode, binfmt and compatible libraries despite native output: [HOST-TOOLS.md](HOST-TOOLS.md). |
| Known warning | Optional `libStubXlib.so` warning harmless in tested headless mode: [troubleshooting](DIY-COMPILATION.md#13-troubleshooting-table). |

## Build from source

[DIY-COMPILATION.md](DIY-COMPILATION.md) is the canonical fresh-checkout recipe: dependencies, capacity planning, patches and validation. [scripts/build.sh](scripts/build.sh) automates checkout/build **after prerequisites**, not host-tool provisioning. No clean-room or bit-identical rebuild is claimed.

For archived source, follow [SOURCE-REASSEMBLY.md](SOURCE-REASSEMBLY.md) → [HOST-TOOLS.md](HOST-TOOLS.md) → the linked build command. The reduced source is already patched, including the final shutdown-safe KVM fix. Use its offline build entrypoint; do not double-apply patches or use the historical failed patch.

## Engineering and historical validation

The [engineering notes](DIY-COMPILATION.md#9-compilation-issues-we-encountered) explain native Ninja dispatch, library-path/C++ fixes, ARM64 virtio reset and shutdown-safe KVM signaling, including rejected fixes.

- API 36 booted with KVM; ADB and guest boot completion were verified.
- The final KVM fix passed **20/20 lifecycle cycles and 10/10 one-minute probes**, with clean emulator/guest shutdown and no new minidumps.
- FrameTimeline captures had no nonzero error/data-loss statistics. See [retained validation](validation/kvm-kick-shutdown-safe-sigipi-validation.txt).

These are historical checks, not fresh benchmarks, application performance results, or proof that the full upstream test suite passed.

## Help and contributions

Start with the [troubleshooting guide](DIY-COMPILATION.md#13-troubleshooting-table). For fixes or additional host validation, see [CONTRIBUTING.md](CONTRIBUTING.md); include your host, emulator version, exact flags and redacted logs. Report security concerns as described in [SECURITY.md](SECURITY.md).

## Source archive FAQ

The reduced patched source is split only as needed to fit [GitHub’s under-2-GiB per-file limit][github-limits]. Follow [source reassembly](SOURCE-REASSEMBLY.md). GitHub’s automatic source ZIP contains only this publication repository, not the build tree. Historical releases remain available.

## Licensing and provenance

Emulator/QEMU is GPLv2; bundled components retain their licenses. See [LICENSE](LICENSE), [LICENSES/](LICENSES/), [NOTICE/](NOTICE/), [COMPLIANCE.md](COMPLIANCE.md), the [pinned manifest](manifests/manifest-build-pinned.xml) and [publication history](AUDIT-STATUS.md). Preserve notices/source obligations. These materials are not legal advice or compliance certification.

No Google system images, proprietary Google SDK payloads, AVD userdata, credentials or private applications are included. Obtain images/tools separately under their terms. Open QEMU firmware sources/notices remain included. Android/Google and NVIDIA/DGX Spark trademarks belong to their respective owners.

[binary]: https://github.com/jduartedj/android-emulator-linux-aarch64-dgx-spark/releases/download/v0.2.0-unofficial/android-emulator-linux-aarch64-dgx-spark-unofficial-35.6.3.tar.zst
[checksums]: https://github.com/jduartedj/android-emulator-linux-aarch64-dgx-spark/releases/download/v0.2.0-unofficial/SHA256SUMS
[release]: https://github.com/jduartedj/android-emulator-linux-aarch64-dgx-spark/releases/tag/v0.2.0-unofficial
[github-limits]: https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases
