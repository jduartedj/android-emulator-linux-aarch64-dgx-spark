# Experimental NVIDIA OpenGL addon — GB10 / tested stack only

**Released as optional addon v0.1.0.** Start with the [download, checksum, installation and rollback guide](INSTALL.md), then read the ABI and argument restrictions below. Archive-internal candidate wording is retained as historical provenance; the linked installation guide is authoritative for release status.

This optional extra leaves the base Emulator35.6.3 and NVIDIA driver unchanged. Tested LinuxAArch64, GB10, existing NVIDIA580.173.02, authorized X11display, API36GoogleAPIsARM64rev7. No guestVulkan, Wayland/no-display, otherGPU/driver/API or arbitraryshader-conformance certification. No proprietary NVIDIA libraries are distributed.

**Before the first launch: use separate dedicated GPU and SwiftShader AVDs and preserve existing userdata. Same-userdata renderer migration is NOT validated.** A prior migration booted but failed to start the test app; dedicated-control rollback passed. Do not test this addon against production userdata.

## Install separately and enable

Extract the optional addon beside—not over—the base SDK. Supply an existing authorized X11DISPLAY and normal KVM membership. No driver installation, Xpermission change, chmod666, system linker config or host reboot is performed.

```bash
export ANDROID_SDK_ROOT="$HOME/android-sdk"
/path/to/nvidia-addon/nvidia-emulator --check
/path/to/nvidia-addon/nvidia-emulator @YourNewGpuAvd \
  -no-window -no-audio -no-snapshot -no-boot-anim \
  -memory 4096 -cores 4 -port 5582
```

If already assigned to kvm but the shell's groups are stale, invoke the wrapper inside the existing authorized `sg kvm -c '...'` context. The wrapper adds its library path only after the group-context transition; nothing persists globally.

Only exact approved matched launcher/headless pairs pass: published615f87…/42d523… or measureddevelopment2baee124…/a840768…. Full hashes are in PROVENANCE.json and the wrapper. Mixed/unknown pairs are rejected; displayed35.6.3 alone is insufficient.

## Argument contract

One `@AVD` or `-avd NAME`; numeric `-port`, `-memory`, `-cores`, `-dpi-device`; values for `-skin`, `-timezone`, `-sysdir`, `-datadir`, `-data`, `-cache`, `-sdcard`; flags `-no-window`, `-no-audio`, `-no-snapshot`, `-no-snapshot-load`, `-no-snapshot-save`, `-no-boot-anim`, `-wipe-data`, `-no-metrics`. Resource/path values cannot begin with an option token.

Renderer, acceleration and feature switches are wrapper-owned. Equals-style flags, `-qemu`, `--`, guestproperty injection and unknown options are rejected before execution. This deliberate grammar prevents user arguments from consuming/overriding the appended mandatory hostrenderer/KVM/minimal-feature flags; it is not an unrestricted emulator CLI proxy. `--check` is accepted only by itself.

## Verify actual GPU use

```bash
python3 /path/to/nvidia-addon/verify-nvidia.py --serial emulator-5582
```

Proof requires guest NVIDIA vendor/renderer without SwiftShader/llvmpipe, exact nativeheadless ELF/process and adjacent `-port` argument, mapped NVIDIA+addon libraries, KVM handles and the same graphicsPID in nvidia-smi. Preflight/GPUflag alone is not proof. The tested NVIDIA lane reports guestGLES3.1 while software reports3.0; record this capability difference in comparisons.

## Supported shader ABI semantics

The base was compiled with a384-byte legacy resource ABI, not the newer544-byte source representation. Resource conversion maps sharedfields explicitly and defaults newerfields. Legacydebugprecision/clamping resource extensions are not broadly supported.

**Compile options are NOT forwarded as a raw bitfield.** Only `ST_OBJECT_CODE`, `ST_VARIABLES` and `ST_INITIALIZE_UNINITIALIZED_LOCALS` are mapped by name to modernANGLE constants. In particular, legacybit31 becomes moderninitializationbit29. Allother61bitpositions return `compileStatus=false` with an unsupported-option infoLog. The actual frozenbasecaller uses onlyOBJECT_CODE|VARIABLES, but the boundary now enforces the contract rather than assuming callers never change.

Tests cover legacyinitialization red/green, everyunsupportedbit, actualcallermask,384-bytecanary, vertex/fragmenttranslation and nestedvariable/interfacecopy/destroy. This is not generalANGLEconformance. SeeSEMANTICS.md andtheexactsourcepatch.

## Public normalization and measurement binding

A new semanticfix means a new code/libraryhash; historicalc5dd…/68771… data are not relabelled as this library. SeePROVENANCE.json/currentvalidationandGPUbenchmarkdoc for newactualrunbinding.

Public normalization replaces exactly3knownNUL-terminated diagnostic sourcefilenames in nonexecutable `.rodata` atfixedwidth with `/angle-source/src/common/…` pluspadding. Allotherbytes, executable/relocationsections, offsets/sizes andoriginalbuild-id are unchanged relativetoitsownnewrawbuild. Full-fileSHA identifiespublicvariant. Theincludednormalizerfailsonunknownlayout/strings andwritesaseparatepublicfile; rawbuildretained. Nooperator/privateprojectpaths remain in publicpayloads.

## Disable/remove/rollback

Cleanly power off onlytheselectedguest: `adb -s emulator-5582 shell sync`, then `adb -s emulator-5582 shell reboot -p`; verifyitsownedprocessended. Launchtheunchangedbasewith explicit`-gpu swiftshader_indirect` and minimalfeatureoverrides on a **separate dedicated softwareAVD**, withoutwrapper/addonLD_LIBRARY_PATH. Verifymappedsoftware/noaddonandguestSwiftShader. Theaddonisprocess-scoped; onceunused, removingitsdirectoryrequiresnobaserestore,driveruninstall orhostconfigedit. Thisdoesnotguaranteesameuserdata migration.

## Build and licensing

`build-support.sh /path/to/corresponding-source/angle /path/to/NEW-output` compiles onlysupport, then applies checkedpublicnormalization. No fullbasebuild. Testnewoutputbefore substitution; buildpaths/buildIDs can differ, so functionalreproducibility is not bitidenticalrebuildattestation. ANGLE/Chromium/xxHash/SMHasher/Apache notices accompanysource/binary. NVIDIA drivers remain operatorsystemdependencies undertheirterms. NoGoogleimage/AVD/privatebenchmark/crashmemory/credentialsinthisaddon.

Published after independent review as an experimental, opt-in addon. No official Google/NVIDIA endorsement or automatic updates.
