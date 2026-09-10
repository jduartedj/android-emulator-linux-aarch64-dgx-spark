# DIY compilation on Ubuntu 24.04 ARM64

This is the canonical, end-to-end build guide for the unofficial Linux AArch64 Android Emulator in this repository. Every command below reflects the retained build/provenance from the NVIDIA DGX Spark validation host. Read [COMPLIANCE.md](COMPLIANCE.md) before redistributing anything.

## 1. Capacity and prerequisites

Validated host:

- NVIDIA DGX Spark / GB10
- 20 ARM64 CPU cores (10 Cortex-X925 + 10 Cortex-A725)
- 121 GiB RAM
- Ubuntu 24.04.4 LTS, Linux `6.17.0-1032-nvidia`, `aarch64`

Measured storage after the work:

- checked-out source plus Repo metadata: about **43 GiB**
- build tree after retries and retained objects: about **24 GiB**
- installed emulator distribution: about **258 MiB**
- API 36 Google APIs ARM64 system image: about **4.3 GiB** installed; official download metadata is 1,872,691,175 bytes
- ccache: 2.0 GiB used of a 5 GiB limit after 7,507 calls; 4.53% hit rate because this was mostly a clean build

Reserve at least **80 GiB free** for source, one build, ccache, image, logs, and transient archive space. Reserve substantially more if creating complete corresponding-source archives. Check first:

```bash
uname -m                       # must print aarch64
free -h
df -h "$HOME"
nvidia-smi                     # informational on DGX Spark
```

Twenty parallel compiler jobs worked with 121 GiB RAM. On smaller hosts use `JOBS=8` or lower. Avoid filling the filesystem: Repo's emulator test-image prebuilt alone transiently consumed about 16 GiB during our first sync.

## 2. Check Google Android CI first

Google's public emulator branch is:

- branch: `aosp-emu-master-dev`
- target: `linux_aarch64` (the actual exposed target seen in the build metadata was `emulator-linux_aarch64_gfxstream`)
- expected artifact: `sdk-repo-linux_aarch64-emulator-<buildid>.zip`

Open:

```text
https://ci.android.com/builds/branches/aosp-emu-master-dev/grid
```

For a candidate build, inspect only `ci.android.com` and the Google Storage redirect returned by the official download. Record:

```bash
URL='https://ci.android.com/builds/submitted/<buildid>/<target>/latest/...'
curl -fL --proto '=https' --proto-redir '=https' -D headers.txt -o artifact.zip "$URL"
stat -c '%s' artifact.zip
sha256sum artifact.zip
unzip -l artifact.zip | sed -n '1,40p'
```

Verify the initial host is `ci.android.com`, every redirect is HTTPS and remains on official Google infrastructure, the filename contains the selected build ID, and the downloaded size/hash are recorded. Artifacts can expire. At the time of this build, the latest visible build was `13288691`; its ARM64 target inventory had logs and e2e tests but no emulator ZIP. We therefore built from official source.

Android SDK Manager did **not** offer a native Linux ARM64 emulator package. It offered the ARM64 system image, but not an ARM64 host emulator binary. Do not substitute community binaries.

## 3. Install build dependencies

```bash
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update
sudo apt-get install -y --no-install-recommends \
  git curl ca-certificates build-essential python3 python3-pip \
  repo ccache ninja-build cmake qemu-kvm \
  libasound2-dev libgl1-mesa-dev libpulse-dev \
  libx11-dev libx11-xcb-dev libxcb-shm0-dev libxcb-xfixes0-dev \
  libxkbcommon-dev libxkbfile-dev
```

Why they are present:

- `git`, `curl`, `ca-certificates`, `repo`: official multi-repository source retrieval
- `build-essential`, `cmake`, `ninja-build`, `python3`: configure, code generation, and native C/C++ compilation
- `ccache`: bounded compiler cache for rebuilds
- `qemu-kvm`: host KVM tooling and `/dev/kvm` integration checks
- ALSA/Pulse development packages: emulator audio build interfaces, even though validation used `-no-audio`
- Mesa/X11/XCB/XKB development packages: Linux UI/graphics link interfaces and bundled Qt platform support
- `python3-pip`: listed by the official Linux development guide; the retained build did not install project packages from PyPI

Validated versions included GCC 13.3.0, Ninja 1.11.1, ccache 4.9.1, Ubuntu CMake 3.28.3, and Repo launcher 2.36. The source manifest also supplies its own CMake/Python build tools.

If Ubuntu's `repo` package is unavailable, install Google's signed/hashed Repo launcher from its official HTTPS storage and verify it before execution:

```bash
mkdir -p "$HOME/bin"
curl -fL --proto '=https' \
  https://storage.googleapis.com/git-repo-downloads/repo \
  -o "$HOME/bin/repo"
curl -fL --proto '=https' \
  https://storage.googleapis.com/git-repo-downloads/repo.asc \
  -o "$HOME/bin/repo.asc"
gpg --verify "$HOME/bin/repo.asc" "$HOME/bin/repo"
chmod 0755 "$HOME/bin/repo"
export PATH="$HOME/bin:$PATH"
repo version
```

Do not pipe a network download directly into a shell.

## 4. KVM without weakening device permissions

Inspect first:

```bash
ls -l /dev/kvm
getent group kvm
id
```

The validated device remained `root:kvm` and mode `0660`. Add only the intended user and start a fresh group context:

```bash
sudo usermod -aG kvm "$USER"
getent group kvm
sg kvm -c 'id; test -r /dev/kvm -a -w /dev/kvm && echo KVM_ACCESS_OK'
```

Group changes do not alter an already-running shell. Use `sg kvm -c ...`, log out/in, or start a new process. Never solve this with `chmod 666 /dev/kvm`.

## 5. Initialize and sync official source

```bash
export WORK="$HOME/android-emulator-arm64"
mkdir -p "$WORK/src" "$WORK/provenance" "$WORK/logs"
cd "$WORK/src"

repo init \
  -u https://android.googlesource.com/platform/manifest \
  -b emu-master-dev \
  --depth=1 \
  --partial-clone \
  --clone-filter=blob:limit=10M \
  --no-clone-bundle

repo sync -c -j8 \
  --no-clone-bundle --no-tags --optimized-fetch --prune

repo manifest -r -o "$WORK/provenance/manifest-synced.xml"
repo forall -c 'printf "%s %s\n" "$REPO_PATH" "$(git rev-parse HEAD)"' \
  > "$WORK/provenance/project-revisions.txt"
sha256sum "$WORK/provenance/manifest-synced.xml"
du -sh "$WORK/src"
```

These shallow/partial flags completed successfully. The exact retained manifest is [manifests/manifest-synced.xml](manifests/manifest-synced.xml), SHA-256 `15003ebd2a045a255ca31f83a43c6743693c5219a210faa91cac5a68046dbb5a`. Its manifest repository revision is `1a75ee5c54d3b3161516ae27b6769a70e0ffcfca`; `external/qemu` is `ae9d18d2b6261179fbd57fffec720a04f7bfb053`.

The first sync spent about 16 GiB on `platform/prebuilts/android-emulator-build/system-images`, which is test data rather than a host-emulator build input. If capacity is constrained, this exact local manifest exclusion was proven for the no-tests build:

```bash
mkdir -p .repo/local_manifests
cat > .repo/local_manifests/exclude-build-tests.xml <<'XML'
<?xml version="1.0" encoding="UTF-8"?>
<manifest>
  <remove-project name="platform/prebuilts/android-emulator-build/system-images" />
</manifest>
XML
repo sync -c -j8 --no-clone-bundle --no-tags --optimized-fetch --prune
```

Record this deviation. Do not exclude arbitrary projects.

## 6. Apply the exact verified patch

```bash
cd "$WORK/src/external/qemu"
git apply /path/to/this/repository/patches/linux-aarch64-build-fixes.patch
git apply /path/to/this/repository/patches/kvm-kick-arm64-shutdown-safe-sigipi.patch
python3 tests/test-kvm-kick-guard.py
git diff --check
git diff > "$WORK/provenance/source-patch.diff"
sha256sum \
  /path/to/this/repository/patches/linux-aarch64-build-fixes.patch \
  /path/to/this/repository/patches/kvm-kick-arm64-shutdown-safe-sigipi.patch
```

Expected individual patch SHA-256 values:

```text
6439982c72030dd28247b60bd3ce7b0d85f04242d1b511ebc46ce58ed9c47cfc  linux-aarch64-build-fixes.patch
809f1a88c275382fdbdecfd980efc03826641615531e4b2f79e4e36c60be4bee  kvm-kick-arm64-shutdown-safe-sigipi.patch
```

The build changes are documented in §9 and the KVM shutdown fix near the end of this guide. Re-check the upstream branch before carrying either patch into a newer revision.

## 7. Configure and build

First inspect the current official script rather than assuming historical flags:

```bash
./android/rebuild.sh --help
./android/rebuild.sh --feature-list
./android/rebuild.sh --task-list
```

The exact successful clean configure/build command was:

```bash
mkdir -p "$WORK/build/objs" "$WORK/build/dist"

./android/rebuild.sh \
  --target linux_aarch64 \
  --config release \
  --ccache /usr/bin/ccache \
  --feature minbuild \
  --feature no-qtwebengine \
  --cmake_option CMAKE_MAKE_PROGRAM=/usr/bin/ninja \
  --out "$WORK/build/objs" \
  --dist "$WORK/build/dist" \
  --task-disable CTest \
  --task-disable AccelerationCheck \
  --task-disable EmugenTest \
  --task-disable GenEntriesTest \
  --task-disable CoverageReport \
  --task-disable PackageSamples \
  --task-disable ZipIntegrationTests \
  --task-disable IntegrationTest \
  2>&1 | tee "$WORK/logs/build.log"
```

This is a production artifact build with build-script tests disabled, followed by independent boot/API/Perfetto/stability validation. It is not a claim that upstream's entire test suite passed.

For an incremental rebuild after a source-only fix:

```bash
/usr/bin/ninja -C "$WORK/build/objs" install/strip \
  2>&1 | tee -a "$WORK/logs/build-resume.log"
```

For a clean rebuild, remove or rename only the dedicated output directory, then rerun `android/rebuild.sh`; do not delete unrelated SDK/source trees:

```bash
mv "$WORK/build/objs" "$WORK/build/objs.previous.$(date +%s)"
mkdir -p "$WORK/build/objs"
# rerun the full command above
```

## 8. Verify and package the build

The install tree is:

```bash
export DIST="$WORK/build/objs/distribution/emulator"
file "$DIST/emulator" \
  "$DIST/qemu/linux-aarch64/qemu-system-aarch64-headless"
"$DIST/emulator" -version
```

Expected architecture/version:

```text
ELF 64-bit ... ARM aarch64
Android emulator version 35.6.3.0 (build_id standalone-0)
```

Validated hashes after the shutdown-safe ARM64 KVM fix:

```text
emulator: 2baee124da343882d48c24024c03ce32e04f338e91a4f1564b9fb1b34046d83e
qemu-system-aarch64: e97cf42b32aa834264d7e5bc42ab5299b6ba89f586b97e245ecd656d6cc9f7b0
qemu-system-aarch64-headless: a840768428b0a7d28fa306146baacbfd7a50ec5543320a57cc6bd6b2cfc0792a
```

The QEMU binary relies on sibling `lib64` libraries. A bare `ldd qemu/.../qemu-system-aarch64-headless` reports them as not found because it bypasses the launcher environment. Verify with the package library path:

```bash
LD_LIBRARY_PATH="$DIST/lib64${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" \
  ldd "$DIST/qemu/linux-aarch64/qemu-system-aarch64-headless"
ldd "$DIST/emulator"
```

Package deterministically with the clearly unofficial name:

```bash
mkdir -p "$WORK/artifacts"
cd "$WORK/build/objs/distribution"
tar --sort=name --format=gnu --mtime='@1788951600' \
  --owner=0 --group=0 --numeric-owner -cf - emulator |
  zstd -T1 -19 -o "$WORK/artifacts/android-emulator-linux-aarch64-dgx-spark-unofficial-35.6.3.tar.zst"
sha256sum "$WORK/artifacts/"*.tar.zst
```

Binary archive SHA-256:

```text
0307a48c58a2a48bb1e8bbf16b01df097582f40302190540e8e211ed8b26f128
```

## 9. Compilation issues we encountered

### 9.1 SDK Manager had no Linux ARM64 emulator package

**Symptom:** `sdkmanager --list` exposed ARM64 system images but no native ARM64 host emulator. Installing the system image initially warned `Dependant package with key emulator not found!`.

**Cause:** Google's Linux emulator package metadata targets the normally distributed host architecture; it did not provide the locally needed AArch64 host executable.

**Fix:** build `external/qemu` from official source. When installing into an SDK, register the local emulator directory with `source.properties` and a local `package.xml` before asking SDK Manager for the system image. This repository's release archive includes `source.properties`; create minimal local metadata if your SDK manager requires it:

```bash
cat > "$ANDROID_SDK_ROOT/emulator/package.xml" <<'XML'
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<ns2:repository xmlns:ns2="http://schemas.android.com/repository/android/common/02" xmlns:ns5="http://schemas.android.com/repository/android/generic/02">
  <localPackage path="emulator" obsolete="false">
    <type-details xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="ns5:genericDetailsType"/>
    <revision><major>35</major><minor>6</minor><micro>3</micro></revision>
    <display-name>Android Emulator (local source build, Linux aarch64)</display-name>
  </localPackage>
</ns2:repository>
XML
```

**Verify:** `sdkmanager --list_installed` recognizes `emulator`, and `file "$ANDROID_SDK_ROOT/emulator/emulator"` says ARM AArch64.

### 9.2 Bundled depot-tools Ninja rejected AArch64

**Symptom:** configure failed with:

```text
Unknown architecture (aarch64) -- unable to run ninja.
No prebuilt ninja binary was found for this system.
```

A nested FlatBuffers host-tool configure later hit the same launcher.

**Cause:** `android/third_party/chromium/depot_tools/ninja` only dispatched its bundled binaries for x86.

**Fix:** pass `--cmake_option CMAKE_MAKE_PROGRAM=/usr/bin/ninja`, use `--ccache /usr/bin/ccache` instead of the bundled x86-64 sccache, and add the exact AArch64 `/usr/bin/ninja` dispatch in the recorded patch for nested builds.

**Verify:** configure prints `CMAKE_MAKE_PROGRAM=/usr/bin/ninja`; nested FlatBuffers configuration reaches `Build files have been written`.

### 9.3 Ubuntu's ARM64 `libstdc++` multiarch path differed

**Symptom:** configure failed:

```text
RUNTIME_OS_DEPENDENCIES depends on ...
/usr/aarch64-linux-gnu/lib/libstdc++.so.6 that does not exist
```

**Cause:** the official ARM64 helper expected `/usr/aarch64-linux-gnu/lib/libstdc++.so.6`; Ubuntu 24.04 ARM64 installs it at `/usr/lib/aarch64-linux-gnu/libstdc++.so.6`.

**Fix:** the exact one-line patch is:

```diff
- printf "%s\n" "/usr/aarch64-linux-gnu/lib/libstdc++.so.6"
+ printf "%s\n" "/usr/lib/aarch64-linux-gnu/libstdc++.so.6"
```

Patch bundle SHA-256 is recorded above. This is Ubuntu 24.04/DGX Spark context, not a universal upstream path rule; verify your host with `readlink -f` before applying it.

**Verify:** configure prints `/usr/lib/aarch64-linux-gnu/libstdc++.so.6` and generates the copied `lib64/libstdc++.so.6`.

### 9.4 Shallow checkout produced Git version warnings

**Symptom:** configure printed:

```text
fatal: No names found, cannot describe anything.
Unable to retrieve git version ... not setting version.
```

**Cause:** `--depth=1 --no-tags` does not provide descriptive tags.

**Fix:** no source change was required. Record immutable commit IDs, manifest SHA-256, `source.properties`, and the emitted emulator version. Do not fabricate a Git-derived version.

**Verify:** final `-version` reports 35.6.3.0 and the recorded commits match `repo manifest -r`.

### 9.5 Rust was disabled by minbuild

**Symptom:** CMake warned:

```text
Disabling RUST, you might have reduced functionality.
```

**Cause:** the `minbuild` feature omits the Rust toolchain/features for this target.

**Fix:** accepted for this bounded headless/API/Perfetto use case; we do not claim feature equivalence with Google's full SDK emulator. If Rust-dependent functionality matters, inspect current `--feature-list` and supply a supported toolchain rather than suppressing the warning.

**Observed impact:** API 36 boot, KVM, ADB, SwiftShader OpenGL ES, package inventory, Perfetto/FrameTimeline, and 10-minute stability passed. Vulkan, local Netsim Bluetooth/UWB, and untested UI features remain limitations.

### 9.6 Missing `<thread>` stopped the native GCC build

**Symptom:** GCC failed in `Snapshotter.cpp`:

```text
error: ‘sleep_for’ is not a member of ‘std::this_thread’
```

**Cause:** the source used `std::this_thread::sleep_for` without directly including `<thread>`; the previous toolchain evidently supplied a transitive include.

**Fix:** add `#include <thread>` beside the standard headers.

**Verify:** both `android-emu` and `android-emu-shared` compile `Snapshotter.cpp` successfully.

### 9.7 ARM64 startup crashed during virtio reset

**Symptom:** the first built binary reached display setup and then segfaulted before boot. GDB showed:

```text
object_get_class
virtio_current_cpu_endian
virtio_reset
virtio_bus_reset
qemu_devices_reset
```

`current_cpu` was non-null but invalid on the non-vCPU reset thread.

**Cause:** the old QEMU-derived reset path treated a stale thread-local `current_cpu` as a guest-initiated reset.

**Fix:** for this `linux_aarch64` minbuild, set `VIRTIO_DEVICE_ENDIAN_LITTLE` directly under `__aarch64__`; this build supports little-endian ARM64 guests only. The exact guarded patch is included.

**Verify:** API 36 reaches `sys.boot_completed=1`; the QEMU process holds `/dev/kvm`; all 60 stability probes pass.

### 9.8 `strip ... lib.so` warnings occurred despite success

**Symptom:** install repeatedly printed:

```text
/usr/bin/aarch64-linux-gnu-strip: .../distribution/emulator/lib64/lib.so: No such file
```

The overall build still ended `BUILD_EXIT=0`.

**Cause:** the install/strip rule derived a generic `lib.so` name for several versioned/shared library installs. We did not hide or patch this warning.

**How we judged it nonfatal for this artifact:** the expected distribution was installed; `file` showed native AArch64; `-version` ran; packaged launcher dependencies resolved; Android booted with KVM; ADB/API/ABI/display/storage checks passed; Perfetto/FrameTimeline and 611 seconds of stability passed. This remains a caveat, not proof that every optional feature is complete.

### 9.9 Headless graphics and missing stub Xlib

**Symptom:** `-no-window` logs:

```text
libStubXlib.so ... cannot be preloaded ... ignored
```

Enabling Vulkan also failed because the minbuild distribution lacked a usable Vulkan loader; the initial unpatched build additionally crashed during reset.

**Fix:** validate with bundled SwiftShader OpenGL ES and explicit feature disables:

```text
-gpu swiftshader_indirect -feature -Vulkan -feature -BluetoothEmulation -feature -Uwb
```

Bluetooth/UWB were disabled because this minbuild had no local Netsim service. Xvfb plus `-qt-hide-window` was a diagnostic experiment, not the final tested command.

**Verify:** logs identify `Google SwiftShader`, OpenGL ES 3.0, boot completion, and stable ADB. The stub-Xlib warning remains visible and harmless for the tested path.

### 9.10 ADB transport naming differed

**Symptom:** the available x86-64 Google platform-tools binary did not initially list `emulator-5554`, while `127.0.0.1:5555` worked after `adb connect`. Later boots could appear as `emulator-5554`, and a stale offline TCP transport could remain after shutdown.

**Cause:** the locally installed Google platform-tools executable was x86-64 and ran through the host compatibility layer; explicit TCP connection and emulator serial discovery differed between attempts.

**Fix:** enumerate devices, select one serial, and disconnect stale TCP transports during cleanup:

```bash
adb connect 127.0.0.1:5555 || true
adb devices -l
SERIAL=${SERIAL:-127.0.0.1:5555}
adb -s "$SERIAL" get-state
# shutdown
adb -s "$SERIAL" emu kill || true
adb disconnect 127.0.0.1:5555 || true
```

**Verify:** no emulator/QEMU process, listener on 5554/5555/8554, or emulator ADB transport remains.

### 9.11 ARM64 KVM shutdown crash in `kvm_cpu_kick()`

**Symptom:** an 8-vCPU ARM64 KVM session could complete its workload and then
crash during clean shutdown. Breakpad minidump symbolization resolved thread 0
to `kvm_cpu_kick()` in `accel/kvm/kvm-all.c`, writing
`cpu->kvm_run->immediate_exit` after teardown had begun.

**Rejected attempts:** checking `cpu` and `cpu->kvm_run` for null passed 20
lifecycle cycles and a 30-minute hold, but `adb emu kill` still produced a
SIGSEGV because the mapping was stale and non-null. Forcing
`kvm_immediate_exit=false` selected the legacy signal path and passed 20 cycles
plus 10 one-minute probes, but shutdown still crashed. In this release build the
`assert(kvm_immediate_exit)` check was compiled out, so `kvm_ipi_signal()` still
called `kvm_cpu_kick(current_cpu)`. The file
[`patches/FAILED-kvm-kick-arm64-legacy-sigipi.patch`](patches/FAILED-kvm-kick-arm64-legacy-sigipi.patch)
is retained only as historical negative evidence. **Do not apply it.**

**Accepted fix:** apply
[`patches/kvm-kick-arm64-shutdown-safe-sigipi.patch`](patches/kvm-kick-arm64-shutdown-safe-sigipi.patch),
SHA-256 `809f1a88c275382fdbdecfd980efc03826641615531e4b2f79e4e36c60be4bee`.
It keeps KVM enabled, forces AArch64 onto QEMU's existing
`KVM_SET_SIGNAL_MASK`/SIGIPI path, retains `qemu_cpu_kick_self()`, and makes
`kvm_ipi_signal()` call `kvm_cpu_kick()` only when
`current_cpu && kvm_immediate_exit`. In legacy mode SIGIPI itself interrupts
`KVM_RUN`, so the handler must not access `kvm_run`.

The change matches the semantics documented by upstream QEMU commit
[`cf0f7cf903073f9dd9979dd33d52618b384ac2cb`](https://github.com/qemu/qemu/commit/cf0f7cf903073f9dd9979dd33d52618b384ac2cb)
and its [mailing-list rationale](https://lists.gnu.org/archive/html/qemu-devel/2017-02/msg02201.html).
The exact source base was
`ae9d18d2b6261179fbd57fffec720a04f7bfb053`.

**Build and validation:** the incremental release build exited 0; the patch's
static regression passed. The stripped GUI and headless QEMU SHA-256 values are
`e97cf42b32aa834264d7e5bc42ab5299b6ba89f586b97e245ecd656d6cc9f7b0`
and `a840768428b0a7d28fa306146baacbfd7a50ec5543320a57cc6bd6b2cfc0792a`.
API 36/ARM64 with 8 vCPUs, 8192 MiB, and KVM active passed 20/20 lifecycle
cycles, 10/10 one-minute ADB/QEMU probes, four accepted FrameTimeline captures
with zero nonzero error/data-loss stats, clean `adb emu kill`, and guest
`reboot -p`; no new minidump or crash signature appeared. See
[`validation/kvm-kick-shutdown-safe-sigipi-validation.txt`](validation/kvm-kick-shutdown-safe-sigipi-validation.txt).

**Rollback:** install through a same-filesystem staging directory and retain the
previous emulator directory. If post-shutdown dump inspection fails, rename the
candidate aside and atomically rename the retained pre-fix directory back to
`$ANDROID_SDK_ROOT/emulator`. Runtime-only stability is not sufficient for this
race: always inspect dumps after shutdown, and never disable KVM as a substitute
for the fix.

## 10. Install API 36 and create the AVD

Copy the built distribution to a dedicated SDK root without overwriting an existing emulator:

```bash
export ANDROID_SDK_ROOT=${ANDROID_SDK_ROOT:-"$HOME/android-sdk"}
test ! -e "$ANDROID_SDK_ROOT/emulator"
cp -a "$DIST" "$ANDROID_SDK_ROOT/emulator"
```

Create `package.xml` as shown in §9.1 if SDK Manager requires local package registration, then install the official **non-Play-Store** image:

```bash
yes | "$ANDROID_SDK_ROOT/cmdline-tools/latest/bin/sdkmanager" \
  --sdk_root="$ANDROID_SDK_ROOT" \
  'system-images;android-36;google_apis;arm64-v8a'
```

Validated image metadata:

```text
revision 7
archive arm64-v8a-36_r07.zip
official archive SHA-1 5a99183b6d924da606260e45fd41a3eb8eca6eb7
API 36; extension level 17; arm64-v8a; google_apis; PlayStore.enabled=false
```

Do **not** commit, release, or redistribute this Google system image.

Create the AVD:

```bash
printf 'no\n' | "$ANDROID_SDK_ROOT/cmdline-tools/latest/bin/avdmanager" create avd \
  --force \
  --name DgxSparkApi36Arm64 \
  --package 'system-images;android-36;google_apis;arm64-v8a' \
  --device pixel_5
```

Set one value per key in `$HOME/.android/avd/DgxSparkApi36Arm64.avd/config.ini`:

```ini
hw.keyboard=yes
hw.gpu.enabled=yes
hw.gpu.mode=auto
snapshot.present=false
fastboot.forceColdBoot=yes
fastboot.forceFastBoot=no
showDeviceFrame=no
disk.dataPartition.size=8G
```

The current `avdmanager` also logged a missing optional image `devices.xml` while successfully creating the Pixel 5 AVD. Verify the generated config rather than treating stderr alone as failure.

## 11. Boot and validate

```bash
export EMULATOR="$ANDROID_SDK_ROOT/emulator/emulator"
export AVD=DgxSparkApi36Arm64

sg kvm -c 'env ANDROID_SDK_ROOT="$ANDROID_SDK_ROOT" \
  "$EMULATOR" @"$AVD" \
  -no-window -no-audio -no-snapshot -no-boot-anim \
  -gpu swiftshader_indirect \
  -feature -Vulkan -feature -BluetoothEmulation -feature -Uwb \
  -accel on -no-metrics'
```

In another shell:

```bash
ADB="$ANDROID_SDK_ROOT/platform-tools/adb"
"$ADB" connect 127.0.0.1:5555 || true
"$ADB" devices -l
export SERIAL=127.0.0.1:5555   # or emulator-5554 if that is the listed device

"$ADB" -s "$SERIAL" wait-for-device
until [ "$("$ADB" -s "$SERIAL" shell getprop sys.boot_completed | tr -d '\r')" = 1 ]; do sleep 5; done

"$ADB" -s "$SERIAL" shell getprop ro.build.version.sdk
"$ADB" -s "$SERIAL" shell getprop ro.product.cpu.abilist
"$ADB" -s "$SERIAL" shell getprop ro.build.fingerprint
"$ADB" -s "$SERIAL" shell wm size
"$ADB" -s "$SERIAL" shell wm density
"$ADB" -s "$SERIAL" shell getenforce
"$ADB" -s "$SERIAL" shell 'echo ok > /data/local/tmp/isolation-test && cat /data/local/tmp/isolation-test && rm /data/local/tmp/isolation-test'
"$ADB" -s "$SERIAL" shell pm list packages -3
```

Expected core results: API 36, `arm64-v8a`, 1080×2340/440 dpi, SELinux enforcing, writable isolated data, and no third-party packages.

Verify KVM without changing permissions:

```bash
PID=$(pgrep -f "$ANDROID_SDK_ROOT/emulator/qemu/linux-aarch64/qemu-system-aarch64-headless" | head -1)
sudo readlink -f "/proc/$PID/exe"
sudo ls -l "/proc/$PID/fd" | grep /dev/kvm
```

Verify graphics from the emulator log: `Google SwiftShader` and OpenGL ES 3.0 were observed. Do not report NVIDIA GPU rendering; the validated configuration used CPU SwiftShader.

## 12. Perfetto and FrameTimeline check

Guest availability:

```bash
"$ADB" -s "$SERIAL" shell 'command -v perfetto; perfetto --version; perfetto --query' |
  grep -E 'track_event|android.surfaceflinger.frame|android.surfaceflinger.frametimeline'
```

Use [validation/perfetto-config.pbtxt](validation/perfetto-config.pbtxt), pipe it on stdin to avoid Android shell file-label restrictions, interact with the UI during the 10-second capture, then pull it:

```bash
cat validation/perfetto-config.pbtxt |
  "$ADB" -s "$SERIAL" shell \
  'perfetto --txt -c - -o /data/misc/perfetto-traces/validation.perfetto-trace'
"$ADB" -s "$SERIAL" pull \
  /data/misc/perfetto-traces/validation.perfetto-trace .
```

Use the official native Linux ARM64 Trace Processor from `get.perfetto.dev/trace_processor`; the validated v58.2 binary had SHA-256 `0e6e0c5452c505c8d46fe472fd196a0d17d963460727e2ce2013b02aa1309555`.

```bash
trace_processor_shell query validation.perfetto-trace \
  "SELECT 'actual_frame_timeline_slice', COUNT(*) FROM actual_frame_timeline_slice UNION ALL SELECT 'expected_frame_timeline_slice', COUNT(*) FROM expected_frame_timeline_slice"
trace_processor_shell query validation.perfetto-trace \
  "SELECT severity,name,value FROM stats WHERE severity IN ('error','data_loss') AND value != 0 ORDER BY severity,name"
```

Retained result: 268 actual rows, 244 expected rows, and zero nonzero error/data-loss stats.

Ten-minute ADB stability probe:

```bash
failures=0
for i in $(seq 1 60); do
  state=$("$ADB" -s "$SERIAL" get-state 2>/dev/null || true)
  boot=$("$ADB" -s "$SERIAL" shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')
  [ "$state" = device ] && [ "$boot" = 1 ] || failures=$((failures + 1))
  "$ADB" -s "$SERIAL" shell 'echo noop; cmd package list packages --user 0 | wc -l' >/dev/null || failures=$((failures + 1))
  sleep 10
done
printf 'failures=%d\n' "$failures"
test "$failures" -eq 0
```

Retained result: 60/60 probes passed over 611 seconds.

## 13. Troubleshooting table

| Error or observation | Cause | Fix | Verification |
|---|---|---|---|
| `Dependant package with key emulator not found` | local source build lacks SDK package metadata | install the source build and create local `emulator/package.xml` | `sdkmanager --list_installed`; `file emulator` |
| `Unknown architecture (aarch64)` from depot-tools Ninja | x86-only launcher dispatch | system Ninja plus recorded AArch64 launcher patch | nested FlatBuffers configure succeeds |
| `/usr/aarch64-linux-gnu/lib/libstdc++.so.6 ... does not exist` | Ubuntu multiarch path mismatch | recorded one-line `/usr/lib/aarch64-linux-gnu` patch | configure and copied `libstdc++` succeed |
| `fatal: No names found` | shallow, tagless checkout | record commits/manifest and emitted version; no fake tag | `repo manifest -r`, `-version` |
| `Disabling RUST` | minbuild feature choice | accept bounded reduced feature set or provide supported Rust toolchain | independently validate required features |
| `sleep_for is not a member of std::this_thread` | missing direct `<thread>` include | recorded include patch | Snapshotter compiles |
| SIGSEGV in `virtio_current_cpu_endian` | stale `current_cpu` on ARM64 reset thread | recorded little-endian AArch64 guard | API 36 boots; 60/60 stability |
| `strip ... lib.so: No such file` with exit 0 | generic install/strip target name | retain warning; verify package/ELFs/deps/boot | all bounded validation passes |
| missing `libStubXlib.so` preload | headless AArch64 launcher expects absent optional stub | retain warning; use tested SwiftShader path | OpenGL ES and boot succeed |
| Vulkan loader errors | minbuild package lacks validated loader | `-feature -Vulkan`; use SwiftShader OpenGL ES | graphics log and FrameTimeline |
| Bluetooth/UWB or Netsim errors | no local Netsim in minbuild | disable BluetoothEmulation and Uwb | clean boot/stability |
| ADB only at `127.0.0.1:5555` | transport discovery/compatibility difference | `adb connect`, then select listed serial | `get-state=device` |
| AVD `devices.xml` warning | optional image-side profile file absent | verify Pixel 5 config and generated AVD | config has 1080×2340/ARM64 |
| no KVM access after `usermod` | old shell lacks new group | `sg kvm` or new login | readable/writable `/dev/kvm`, open QEMU FD |
| disk exhausted during sync/archive | large prebuilts and source archives | reserve space; exclude only proven test-image project; monitor `df` | sync/build complete with headroom |

## 14. Clean-room reproduction checklist

1. Start on Ubuntu 24.04 AArch64 with at least 80 GiB free.
2. Install only the listed packages.
3. Verify scoped KVM access in a fresh group process.
4. Initialize Google's official `emu-master-dev` manifest with the proven shallow/partial flags.
5. Pin to this repository's manifest or record a new immutable manifest before changing anything.
6. Apply the exact patch; verify its SHA-256.
7. Run the full release command; retain complete logs and exit status.
8. Verify `file`, package-aware `ldd`, `-version`, and binary hashes.
9. Install the Google API 36 ARM64 image separately; never put it in an emulator archive.
10. Create a fresh AVD and cold boot with KVM and tested feature flags.
11. Verify ADB, API, ABI, fingerprint, display, SELinux, isolated storage, clean packages, graphics, Perfetto/FrameTimeline, and 10-minute stability.
12. Stop the emulator and prove no QEMU/emulator child/listener/ADB transport remains.
13. Before redistribution, scan binary and source archives for system images, AVD data, credentials, private keys, personal paths, and caches.

## 15. GPL/source and Google image boundaries

The emulator/QEMU aggregate is GPLv2 and contains components under additional licenses. Preserve the exact `NOTICE.txt`, `NOTICE.csv`, GPL text, copyrights, warranty disclaimers, modification record, build scripts, and complete corresponding source. Do not rely only on an upstream link. If source exceeds GitHub's per-file limit, split deterministically, publish part and reassembled-stream SHA-256 values, and include reassembly instructions.

Google API/Play system images, Play services, SDK credentials, firmware, AVD userdata, and proprietary SDK tools are separate from the emulator corresponding source and are excluded from this project's repository/release. Users download the selected system image themselves under Google's terms.

This section records source-backed license facts and the packaging performed for this release; it is not legal advice.

## Known limitations

- Source revision 35.6.3 is older because no current official ARM64 CI emulator ZIP was downloadable.
- The validated minbuild disables Rust-dependent functionality, Vulkan, local Netsim Bluetooth/UWB, snapshots, audio, and the visible UI path.
- Graphics validation used SwiftShader OpenGL ES 3.0, not the NVIDIA GPU.
- The headless stub-Xlib and install/strip warnings remain documented.
- Google platform-tools on the validation SDK was x86-64 under the host compatibility layer; emulator/QEMU were native AArch64.
- No application benchmark APK was installed; the result is emulator suitability validation, not app performance data.
