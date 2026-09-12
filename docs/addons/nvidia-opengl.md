# Optional NVIDIA OpenGL support (candidate)

Base v0.2.0 remains unchanged. This optional LinuxARM64 extra uses an already-installed NVIDIA driver; it is not a driver installer or base emulator replacement. Validated GB10/driver580.173.02/OpenGL path only, no guest Vulkan certification.

See [addon instructions](../../addons/nvidia/README.md), [validation and limitations](../../addons/nvidia/VALIDATION-SUMMARY.md), and [source/license notice](../../addons/nvidia/NOTICE.md). Binary and corresponding-source artifacts must be reviewed/published separately; the git proposal does not embed proprietary drivers or private benchmark/crash data.

Use separate GPU and SwiftShader disposable AVDs: in-place same-userdata renderer migration was not validated. Explicitly verify NVIDIA vendor/renderer/process usage rather than trusting a flag. Rollback launches the unchanged base in SwiftShader mode without the addon environment. No host configuration or permission changes are required on the tested setup.
