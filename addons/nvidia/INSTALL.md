# Install the experimental NVIDIA OpenGL extra

**GB10 / Linux AArch64 / existing X11 / tested stack only.** The base v0.2.0 emulator remains unchanged. This extra does not install or upgrade NVIDIA drivers; validation used the existing 580.173.02 driver. Vulkan is not enabled.

**Use separate dedicated GPU and SwiftShader AVDs. Preserve existing userdata.** In-place renderer migration on the same AVD is not validated; a previous migration could boot but could not launch the test app. Dedicated-control rollback passed.

## 1. Download and verify the optional addon

Run in a new download directory. These are separate addon assets, not replacements for the base archive:

```bash
set -euo pipefail
DOWNLOAD_DIR=$(mktemp -d "$HOME/nvidia-addon-download.XXXXXX")
cd "$DOWNLOAD_DIR"
RELEASE=https://github.com/jduartedj/android-emulator-linux-aarch64-dgx-spark/releases/download/nvidia-opengl-addon-v0.1.0
ARCHIVE=nvidia-opengl-addon-linux-aarch64-v0.1.0.tar.gz
curl -fL --proto '=https' --proto-redir '=https' -o "$ARCHIVE" "$RELEASE/$ARCHIVE"
curl -fL --proto '=https' --proto-redir '=https' -o SHA256SUMS "$RELEASE/SHA256SUMS"
awk -v name="$ARCHIVE" '$2 == name { n++; line=$0 } END { if (n != 1) exit 1; print line }' SHA256SUMS > addon.sha256
sha256sum -c addon.sha256
```

Expected archive SHA256: `0c4906acb5d0c99f0b749a799bafd9ec29a538e91030cbb08c89f55b8778ab9d` (883,285 bytes). Checksums detect corruption; they are not an independent publisher signature.

[Corresponding source](https://github.com/jduartedj/android-emulator-linux-aarch64-dgx-spark/releases/download/nvidia-opengl-addon-v0.1.0/nvidia-opengl-addon-source-v0.1.0.tar.gz) is optional for rebuilding/auditing: 962,553 bytes, SHA256 `fa466614bc889c22bb2b5bfa53537c0dae268db7404a7de0ef7d2072655f1f7e`. [Asset manifest](https://github.com/jduartedj/android-emulator-linux-aarch64-dgx-spark/releases/download/nvidia-opengl-addon-v0.1.0/ASSET-MANIFEST.json) binds the accepted support library and source archives.

## 2. Extract beside the base—not over it

```bash
ADDON_ROOT=$(mktemp -d "$HOME/nvidia-addon.XXXXXX")
tar -xzf "$DOWNLOAD_DIR/$ARCHIVE" -C "$ADDON_ROOT"
export ANDROID_SDK_ROOT="$HOME/android-sdk" # your existing base SDK
"$ADDON_ROOT/nvidia-addon/nvidia-emulator" --check
```

The wrapper requires an existing authorized X11 `DISPLAY`, native AArch64, normal KVM read/write access, an approved exact base launcher/headless pair and the correct addon hash. Do not weaken permissions or edit global loader configuration. If your already-assigned KVM membership needs a fresh group context, run the wrapper inside that existing `sg kvm` context.

## 3. Launch a new dedicated GPU AVD and verify

Create a **new** ARM64 API36 Google APIs AVD through your existing SDK tooling; do not reuse production userdata. Then:

```bash
"$ADDON_ROOT/nvidia-addon/nvidia-emulator" @YourNewGpuAvd \
  -no-window -no-audio -no-snapshot -no-boot-anim \
  -memory 4096 -cores 4 -port 5582
```

In another authorized shell:

```bash
python3 "$ADDON_ROOT/nvidia-addon/verify-nvidia.py" --serial emulator-5582
```

Actual NVIDIA guest vendor/renderer, mapped driver/addon libraries, native process/KVM and matching graphics PID must all verify. A flag or `nvidia-smi` availability alone is not proof. See [argument and shader-ABI limits](README.md).

## 4. Stop and return to SwiftShader

```bash
adb -s emulator-5582 shell sync
adb -s emulator-5582 shell reboot -p
```

Verify that the owned process has ended. Launch the unchanged base directly with explicit `-gpu swiftshader_indirect` and its existing minimal feature overrides on a **separate dedicated software AVD**, without the addon wrapper/loader path. Removing the unused standalone addon directory requires no base restore, driver uninstall or host configuration change. This does not certify migration of the same userdata between renderers.

## Status and provenance

This is the independently reviewed semantic-corrected support library `5d798f97574236634e9059430beb4352c65a8c3b4a75a581eb0c8d9d6bc3d995`, published as a separate **experimental prerelease**, not the latest base. Archive bytes are exactly the accepted candidate bytes; internal “candidate” wording is retained as historical provenance. These release instructions and the [current benchmark document](../../docs/GPU-BENCHMARKS.md) are authoritative for publication status.

No proprietary NVIDIA driver, Google system image, AVD, account, credential or private crash memory is distributed. Source licenses and bounded compatibility limitations remain applicable. No Google/NVIDIA endorsement or universal shader-conformance claim.
