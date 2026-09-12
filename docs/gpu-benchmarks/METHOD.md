# Neutral benchmark method

Identical bytecode APK and guest settings across the two renderer lanes; all timing workload source is included beside this document. Guest `System.nanoTime()` measures CPU/SQLite/file/UI durations; Android `am start -W` TotalTime measures force-stop cold-process startup. Host orchestration timing is separate and not mixed into CPU results.

## Compilation and warmup

The APK is debuggable for local instrumentation/data collection. ART legitimately uses verify/JIT; a speed-compilation request was observed to downgrade to verify, so no full-AOT claim is made. Verify compilation state before tests.

After final no-snapshot boot and a fixed 20-second guest settle, run two to four full conditioning batches. Each contains five warmups plus 30 samples of each CPU/SQLite/file/UI workload. After at least two batches, require CPU1 median drift versus the preceding batch ≤10%, CPU1 last-15 CV ≤10%, and CPU4 median drift ≤20%. Failure stops before scoring, not an excuse to discard scored slow samples. Both measured lanes passed after two batches. Conditioning data remains separate from scored samples; CPU convergence does not prove every system component converged.

Then run three independent instrumentation processes, each five warmups plus 30 scored samples per workload, followed by three startup batches with the same 5+30 policy. Keep workload order and inputs fixed. Check integer result −80449474 for CPU1 and each CPU4 worker; CPU4 sum −321797896. SQLite rows512/id sum130816 with values checked. File bytes1048576/checksum133693440. UI verifies30draw events/29intervals. Every correctness check must pass.

## Statistics

Report n, median, nearest-rank p95, min/max, sample SD, CV and MAD per batch and pooled. Flag CV>0.15. Flag values beyond3×1.4826×MAD from median; ifMAD=0, unequal values flagged. Do not remove flagged samples. Warmups and conditioning excluded only by predefined phase/batch designation, not performance.

Optional ratio intervals: independently resample3batch clusters per lane, then30measured rows inside each selected batch; ratio of pooled medians;10000replicates, seed20260912, percentile95%. With only3clusters these intervals are exploratory and omit order/environment confounds. Five-boot results get median/range only, no bootp95 orCI.

Cold boots require sys.boot_completed1 and resumedlauncher, without snapshots, using initialized disposableuserdata and guest sync/clean poweroff between trials. Use separate AVDs for different renderers. Report failed attempts, post-run health and cleanup separately from measurement correctness; a shutdown crash is not converted to PASS.

Graphics verification requires actual vendor/renderer/library/process evidence. The30draw journey and interval samples are not presentationFPS. No supplementary FrameTimeline or GPUtime was measured in this comparison.
