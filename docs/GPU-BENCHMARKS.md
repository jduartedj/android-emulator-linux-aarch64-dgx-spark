# NVIDIA OpenGL addon: measured results and limitations

The optional addon enables genuine NVIDIA GB10 OpenGL rendering without replacing the base emulator. **The existing NVIDIA 580.173.02 driver was unchanged; no driver upgrade was required.** This measures renderer enablement, not the effect of a driver upgrade.

See the [installation, verification and rollback guide](../addons/nvidia/INSTALL.md) and [compatibility/validation notes](../addons/nvidia/VALIDATION-SUMMARY.md). The base v0.2.0 download and default SwiftShader behavior remain unchanged. Addon binary/source distribution is separate; no proprietary NVIDIA driver is included.

## Current released addon: semantic-corrected, separately benchmarked

[Experimental addon v0.1.0](https://github.com/jduartedj/android-emulator-linux-aarch64-dgx-spark/releases/tag/nvidia-opengl-addon-v0.1.0) uses support library **5d798f97574236634e9059430beb4352c65a8c3b4a75a581eb0c8d9d6bc3d995**. Its legacy compile-option mapping was corrected and independently reviewed; unsupported options reject rather than being silently reinterpreted. This is new code with its **own actual full GPU benchmark**, not a relabelling of the previous adapter's timings.

The new GPU run was recorded on **2026-09-12, 19:24–19:29 Europe/Lisbon**, using the actual published base, unchanged NVIDIA 580.173.02 driver and the same neutral APK/settings/method. Five new lifecycle/smoke cycles passed before timing. All correctness checks and six measured-run shutdowns passed; no fatal guest event was captured during scored samples. CPU4/SQLite variability and provisioning Bluetooth failures remain documented.

**Comparison control is earlier, not contemporaneous:** SwiftShader was measured at 18:41–18:49, about 35 minutes before the new GPU run. Configuration was matched, but sequential time, cache, background and thermal confounds remain. Each row contains 90 measured samples across three batches, plus retained warmups/conditioning. This is exploratory same-host latency evidence, not a universal speedup, GPU timestamp or driver-upgrade effect.

| Workload | Earlier SwiftShader median / p95 ms | Current NVIDIA median / p95 ms |
| --- | ---: | ---: |
| CPU, one thread | 2.871 / 2.901 | 2.873 / 2.939 |
| CPU, four threads (4× work) | 3.193 / 5.906 | 3.186 / 5.400 |
| SQLite transaction/read | 6.351 / 9.417 | 6.694 / 9.265 |
| 1 MiB write/sync/read | 6.675 / 7.830 | 6.380 / 7.829 |
| 30 onDraw events (not FPS) | 685.222 / 706.108 | 483.430 / 483.735 |
| Force-stop app startup | 758.500 / 1015.000 | 305.500 / 333.000 |

Observed current-versus-earlier-control median reductions: **startup 59.7231%**, **UI callbacks 29.4491%**, and **boot 59.9677%**. CPU medians remain effectively unchanged. SQLite was **5.40% slower**, noisy; it is not omitted. File latency was 4.42% lower, also subject to variability.

Five-boot medians: **20.668 s → 8.274 s**; ranges **20.325–20.851 s → 8.249–8.310 s**. No boot p95 or confidence interval is claimed. No presented-FPS claim is made from onDraw callbacks.

[Current raw samples](gpu-benchmarks/nvidia-semantic-fixed-raw.csv), [current summary](gpu-benchmarks/nvidia-semantic-fixed-summary.json), [current boot samples](gpu-benchmarks/nvidia-semantic-fixed-boots.json). Historical results below remain labelled and belong to the previous adapter.

## Test setup

Tested on DGX Spark/GB10, Ubuntu 24.04, native AArch64 Emulator 35.6.3 with KVM. Both lanes used **4 vCPU, 4 GiB guest RAM, Android 16/API 36 Google APIs ARM64 revision 7**, image build `BE2A.250530.026.F3/13894323`, security patch 2025-07-05, 1080×1920, density 420, nominal 60 Hz, English, font scale 1 and disabled system animations. Guest Bluetooth/BLE and Wi-Fi were disabled after provisioning. Vulkan was disabled.

The **same neutral Java-bytecode APK** was used in both lanes, SHA-256 `7fcaef88592aeedf34d45c951b46cc1fbd281eabd11d831aca94a35c410dab27`. It has no native libraries or network permissions. The workload source is linked below. No production application, account or private application data is involved.

The historical measurements used the pre-normalization development binary; the published v0.2.0 binaries have different file hashes but **identical executable `.text` sections**, verified separately. The earlier diagnostic-only publication candidate `68771…` was subsequently superseded by a real compile-option semantic correction. The current support `5d798f…` is NEW code, not attributed to the original c5dd… full timings below. The current released-addon section above records its separate actual testing; the historical table is retained rather than relabelled. A focused normalized-support + published-base GPU boot/proof/smoke/shutdown compatibility check and ABI/shader test are recorded with the addon candidate; it is not misrepresented as another full benchmark. The wrapper accepts only explicitly approved, matched launcher/headless pairs.

The control ran first, NVIDIA second, in fresh dedicated AVDs. Each lane passed its bounded verify/JIT warmup gate after two retained conditioning batches, followed by **three batches of five warmups plus 30 measured samples per workload**: 90 measured samples per table row. Five independent no-snapshot boots were measured separately. Fixed order is not randomized and leaves time/cache/background confounds.

## Historical measured results (previous shader adapter)

Median and nearest-rank p95 in milliseconds. Lower latency is better for these particular workloads; there is no overall platform or ISA ranking.

| Workload | SwiftShader median | SwiftShader p95 | NVIDIA median | NVIDIA p95 |
| --- | ---: | ---: | ---: | ---: |
| CPU, one thread: 2M integer rounds | 2.871 | 2.901 | 2.870 | 2.909 |
| CPU, four threads: 4 × 2M rounds | 3.193 | 5.906 | 3.200 | 5.271 |
| SQLite: 512-row transaction and checked read | 6.351 | 9.417 | 6.828 | 9.522 |
| File: 1 MiB write, sync and checked warm read | 6.675 | 7.830 | 6.549 | 7.803 |
| UI: first-to-last of 30 `onDraw` events | 685.222 | 706.108 | 483.362 | 483.709 |
| Force-stop cold-process app startup | 758.5 | 1015.0 | 306.0 | 329.0 |

Observed median latency changes:

- **Startup: 59.66% lower.**
- **UI draw journey: 29.46% lower.**
- CPU medians effectively unchanged: −0.03% single-thread, +0.22% four-thread.
- **SQLite: 7.52% slower median**, with enough variance that the exploratory interval includes no change. This regression is not omitted.
- File journey: 1.88% lower median, a small/noisy difference.

| Five cold boots | Median seconds | Range seconds |
| --- | ---: | ---: |
| SwiftShader | 20.668 | 20.325–20.851 |
| NVIDIA | 8.803 | 8.252–8.845 |

Boot median was **57.4% lower**. No boot p95 or confidence interval is claimed from five trials. Timing starts before emulator process launch and ends after `sys.boot_completed=1` plus resumed launcher; it includes host/ADB readiness overhead. The 0.5-second readiness retry interval limits meaningful precision. Initial provisioning boots are excluded. This is not a true cold-page-cache test.

## What these numbers do—and do not—mean

- CPU4 performs **four times CPU1's work**, not the same work in parallel.
- `onDraw` events are application callbacks, **not presented frames, FPS, FrameTimeline or GPU timestamps**. Across 2,610 intervals per lane, medians were 23.246 ms versus 16.668 ms; p95 was 35.861 ms versus 17.097 ms. No unmeasured “60 FPS” claim is made.
- SQLite uses checked DELETE journal / synchronous FULL semantics; file IO requests `FileDescriptor.sync()`. Both use warm caches. These are application journeys, not physical storage throughput or proof of hardware persistence.
- Startup is a new app process after force-stop, not a cold filesystem cache.
- Only three independent batch clusters per lane were collected. P95 and hierarchical-bootstrap intervals are exploratory, not a guarantee of tail behavior. CPU4 and SQLite variability remained flagged. All measured slow samples and outliers were retained.
- Guest GLES capability differed: SwiftShader reported GLES 3.0, NVIDIA GLES 3.1. Host driver/base executable code was unchanged, but renderer capability and fixed-order/background effects remain confounds.
- No support compilation or packaging ran during scored measurements. Host power policies, global drivers and permissions were not changed. Existing background services were not killed. Scored-window host swap was small but nonzero; no zero-interference claim.

## Correctness and reliability

NVIDIA use was verified by guest vendor/renderer, mapped NVIDIA libraries and addon, native QEMU/KVM handles and the exact QEMU graphics PID in `nvidia-smi`—not by the command-line flag alone. Screenshots showed the expected neutral scene.

Before measurement, five repeated GPU boot/render/input/smoke/shutdown cycles passed with no new minidump during those cycles. Both complete measured lanes passed all correctness checks and six clean shutdowns each. No fatal guest events were captured in scored windows. Initial provisioning Bluetooth-service failures were retained separately; bounded logs are not exhaustive proof of zero system failures. Earlier failed pre-boot addon probes were also retained during development.

**Use separate dedicated GPU and SwiftShader AVDs.** A same-userdata renderer-switch probe booted the software-rendered base but failed to launch the neutral app. Its cause is unresolved; in-place migration is not certified. A separate dedicated control AVD passed rollback verification with no addon loaded, correct SwiftShader rendering, neutral smoke checks and clean shutdown. Do not describe rollback as general userdata migration support.

## Small normalized evidence and method

These files omit host/user paths, process identifiers, credentials, screenshots, crash dumps and private application data. Durations, warmup/measurement phase, batch/sample labels, checksums and outlier flags are retained.

- [SwiftShader raw samples](gpu-benchmarks/recent-swiftshader-raw.csv), [summary](gpu-benchmarks/recent-swiftshader-summary.json), [five boots](gpu-benchmarks/recent-swiftshader-boots.json).
- [NVIDIA raw samples](gpu-benchmarks/nvidia-host-raw.csv), [summary](gpu-benchmarks/nvidia-host-summary.json), [five boots](gpu-benchmarks/nvidia-host-boots.json).
- Neutral [instrumentation workload](gpu-benchmarks/BenchInstrumentation.java), [Canvas activity](gpu-benchmarks/MainActivity.java), [manifest](gpu-benchmarks/AndroidManifest.xml).
- [Method and conditioning policy](gpu-benchmarks/METHOD.md); retained [software conditioning rows](gpu-benchmarks/recent-swiftshader-conditioning.csv) and [GPU conditioning rows](gpu-benchmarks/nvidia-host-conditioning.csv), plus each lane’s conditioning-decision JSON in the same directory.
- [Evidence file checksums](gpu-benchmarks/SHA256SUMS).

If a future host-driver upgrade is performed, rerun the same benchmark and retain a post-upgrade SwiftShader control plus the verified NVIDIA lane. The present results must not be relabelled as that future driver-upgrade experiment.
