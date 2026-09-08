SELECT name FROM sqlite_master WHERE type IN ('table','view') AND lower(name) LIKE '%frame%timeline%' ORDER BY name;
SELECT 'actual_frame_timeline_slice' AS table_name, COUNT(*) AS rows FROM actual_frame_timeline_slice;
SELECT 'expected_frame_timeline_slice' AS table_name, COUNT(*) AS rows FROM expected_frame_timeline_slice;
SELECT severity, COUNT(*) AS rows FROM stats WHERE severity IN ('error','data_loss') GROUP BY severity ORDER BY severity;
