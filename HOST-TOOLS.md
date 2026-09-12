# Linux ARM64 host-tool compatibility

The released emulator/QEMU executables are **native AArch64**. The recorded
upstream build, however, invokes **x86-64 Python 3.10.3 and CMake 3.23.1** from
its source prebuilts. Do not describe every build tool as native ARM64.

## Verified setup and scope

The validation host has Ubuntu `qemu-user-static`
`1:8.2.2+ds-0ubuntu1.18` and `binfmt-support` `2.2.2-7`. Its enabled
`/proc/sys/fs/binfmt_misc/qemu-x86_64` handler uses
`/usr/libexec/qemu-binfmt/x86_64-binfmt-P`, resolving to
`/usr/bin/qemu-x86_64-static`, with flags `POF`.

A publication repair tested the exact source-pinned Python/CMake in an isolated
Ubuntu 24.04 ARM64 container, with no network, an empty inherited environment,
read-only source, and an explicit library root extracted from the official
Ubuntu packages below. Native QEMU user-mode and Ninja executables were mounted
read-only; no host package or binfmt configuration was changed. The tests passed:

- Python version and `zlib`, `ctypes`, `subprocess`, `json`, `pathlib`, `argparse` imports;
- CMake version and a minimal `project(... NONE)` configure using native Ninja;
- CMake launching the pinned Python as a subprocess through binfmt;
- the real `android/rebuild.sh --help`, `--feature-list`, and `--task-list` paths;
- instrumented build-driver task construction with all eight no-tests exclusions,
  the AArch64/minbuild/no-Qt-WebEngine configuration, and preserved
  `QEMU_LD_PREFIX` through its real subprocess environment merger.

The task-construction probe intercepted task execution; it did not run emulator
configure, compile, clean, distribution, or integration tasks.

This verifies the **host-tool prerequisite and build-driver import/argument
paths**, not a full clean-room emulator build, its full configure/link graph, or
all optional Python modules. The pinned Python does not supply `_ssl`; TLS/PyPI
work is not part of this offline smoke or the recorded no-tests recipe. Source
retrieval uses system Git/Repo/curl, not this prebuilt Python's TLS stack.

## 1. Install standard Ubuntu host packages

On an Ubuntu 24.04 ARM64 machine you control, first inspect existing setup:

```bash
uname -m
command -v qemu-x86_64-static || true
cat /proc/sys/fs/binfmt_misc/qemu-x86_64 2>/dev/null || true
```

If absent, obtain QEMU user-mode support from Ubuntu's normal signed package
repositories, with `universe` available. Installation is a host-administrator
operation; this project's publication repair did not perform it:

```bash
sudo apt-get update
sudo apt-get install qemu-user-static binfmt-support ninja-build curl ca-certificates
```

Verify an enabled x86-64 handler before using the upstream build script:

```bash
command -v qemu-x86_64-static
grep -q '^enabled$' /proc/sys/fs/binfmt_misc/qemu-x86_64
cat /proc/sys/fs/binfmt_misc/qemu-x86_64
```

If registration is absent, stop and resolve the Ubuntu package/service setup
with your administrator. Do not overwrite binfmt rules or weaken permissions.
Explicit QEMU execution alone does not guarantee that nested subprocesses work;
the upstream build requires the enabled handler too.

## 2. Create a private x86-64 library root without changing system libraries

Use a new directory. `apt-get download` only downloads packages; `dpkg-deb -x`
extracts them here rather than installing them. These exact cross-package
versions were available and tested during the repair:

```bash
export COMPAT="$HOME/emulator-host-tools"
mkdir -p "$COMPAT/packages" "$COMPAT/root" "$COMPAT/zlib"
cd "$COMPAT/packages"
apt-get download \
  libc6-amd64-cross=2.39-0ubuntu8cross1 \
  libgcc-s1-amd64-cross=14.2.0-4ubuntu2~24.04.1cross1 \
  libstdc++6-amd64-cross=14.2.0-4ubuntu2~24.04.1cross1

for package in libc6-amd64-cross_*.deb libgcc-s1-amd64-cross_*.deb libstdc++6-amd64-cross_*.deb; do
  dpkg-deb -x "$package" "$COMPAT/root"
done

curl -fL --proto '=https' --proto-redir '=https' \
  https://archive.ubuntu.com/ubuntu/pool/main/z/zlib/zlib1g_1.3.dfsg-3.1ubuntu2.2_amd64.deb \
  -o zlib1g_1.3.dfsg-3.1ubuntu2.2_amd64.deb
printf '%s  %s\n' \
  84b9cf5752b29c9f92c27cd4c4ba9bbcc70b5ccf9b1b515421a28ae23212e273 \
  zlib1g_1.3.dfsg-3.1ubuntu2.2_amd64.deb | sha256sum -c -
dpkg-deb -x zlib1g_1.3.dfsg-3.1ubuntu2.2_amd64.deb "$COMPAT/zlib"
cp -a "$COMPAT/zlib/usr/lib/x86_64-linux-gnu/"libz* \
  "$COMPAT/root/usr/x86_64-linux-gnu/lib/"
export QEMU_LD_PREFIX="$COMPAT/root/usr/x86_64-linux-gnu"
```

The zlib SHA-256 above was checked against Ubuntu's `noble-updates/main`
`binary-amd64/Packages.xz` index. If a pinned package expires, deliberately select
and verify its official replacement, then repeat the smoke checks; do not bypass
checksum failures. The cross-package hashes used in the repair were:

```text
db98738caedbc18b257f59c0d5485023ff6eee7232a7682f8ece02f277bb521a  libc6-amd64-cross_2.39-0ubuntu8cross1_all.deb
c30bf5f527592529c165b4bc1a9c3ca77e462b1171c993900e6abbc4dff4830a  libgcc-s1-amd64-cross_14.2.0-4ubuntu2~24.04.1cross1_all.deb
d73e0b4182537c197878416b462921ceed326c3dc32d552056ed7e240705dae5  libstdc++6-amd64-cross_14.2.0-4ubuntu2~24.04.1cross1_all.deb
```

QEMU, Ubuntu runtime packages and their licenses are obtained separately from
Ubuntu; they are not republished in this project's binary/source assets. Their
package copyright files remain in the extracted package directories.

## 3. Smoke-check the pinned source tools before compiling

After obtaining the [complete pinned source](DIY-COMPILATION.md#5-initialize-and-sync-official-source):

```bash
export WORK="$HOME/emulator-build"
SRC="$WORK/src"
qemu-x86_64-static -L "$QEMU_LD_PREFIX" \
  "$SRC/prebuilts/python/linux-x86/bin/python3" -I -c \
  'import sys,zlib,ctypes,subprocess,json,pathlib,argparse; print(sys.version)'
qemu-x86_64-static -L "$QEMU_LD_PREFIX" \
  "$SRC/prebuilts/cmake/linux-x86/bin/cmake" --version

# These direct invocations also exercise the registered binfmt path.
"$SRC/prebuilts/python/linux-x86/bin/python3" --version
"$SRC/prebuilts/cmake/linux-x86/bin/cmake" --version
cd "$SRC/external/qemu"
./android/rebuild.sh --help
./android/rebuild.sh --target linux_aarch64 --feature minbuild \
  --feature no-qtwebengine --feature-list
./android/rebuild.sh --target linux_aarch64 --out "$WORK/build/objs" \
  --dist "$WORK/build/dist" --task-list
```

Keep `QEMU_LD_PREFIX` exported for the build shell and use the native system
Ninja/ccache settings in the DIY guide. The current supported statement is a
DGX Spark/Ubuntu ARM64 host-build recipe with verified compatibility tooling and
historical full-build evidence—not a newly repeated, bit-identical clean-room
build on every Ubuntu ARM64 installation.


## v0.2.0 reduced-source validation record

The historical smoke-test descriptions above remain accurate for the September 11 repair. The reduced-source packaging candidate adds a separate complete build validation: the final source archive is freshly extracted and its offline entrypoint runs configure, compile, link, install and distribution with networking disabled, empty outputs and no original-source or compiler-object-cache fallback. The final result and exact image/prerequisite mounts are recorded in `BUILD-AND-REVIEW-RESULT.json` and the accompanying build-compliance evidence; archive creation or configure alone must not be treated as that result.

This uses the existing native GCC/G++ and Ninja prerequisites plus pinned x86 Python/CMake/Qt generators with the private compatibility root. No global package installation, binfmt adjustment or security-policy change was performed. The runtime archive remains unchanged, and no new Android or GPU benchmark is claimed. For the already-patched reduced source, use [SOURCE-REASSEMBLY.md](SOURCE-REASSEMBLY.md), not the fresh-checkout script that retrieves a complete upstream workspace.
