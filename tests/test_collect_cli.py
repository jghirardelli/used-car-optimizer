from src.used_car_optimizer.collect.cli import _build_collectors
from src.used_car_optimizer.collect.browser_capture import BrowserCaptureCollector
from src.used_car_optimizer.collect.browser_snapshot import BrowserSnapshotCollector


def test_browser_mode_prefers_capture_files_over_text_snapshots(tmp_path):
    capture_dir = tmp_path / "data" / "incoming" / "browser_captures"
    capture_dir.mkdir(parents=True)
    (capture_dir / "maita_subaru_page_1.json").write_text("[]", encoding="utf-8")

    collectors = _build_collectors(tmp_path, "Maita Subaru", mode="browser")

    assert any(isinstance(collector, BrowserCaptureCollector) for collector in collectors)
    assert not any(isinstance(collector, BrowserSnapshotCollector) for collector in collectors)

