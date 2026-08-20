#!/usr/bin/env python3
"""Focused keyboard/state and visual checks for the V6 Report/Explore boundary."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

from verify_support import (
    BASELINE_ROOT,
    CHROMIUM,
    CURRENT_ROOT,
    DIFF_ROOT,
    ROOT,
    Variant,
    VerificationFailure,
    assert_no_page_errors,
    compare_images,
    expect,
    image_sha,
    load_variant,
    state_count,
)

REPORT = ROOT / "tests" / "hybrid-switch-report.json"
VARIANT = Variant("v6", "v6-hybrid.html", "Hybrid Report + Workbench Mode")
VIEWPORT = {"width": 1440, "height": 1000}


def capture(page, mode: str, name: str, records: list[dict[str, object]]) -> None:
    target_root = BASELINE_ROOT if mode == "update" else CURRENT_ROOT
    target = target_root / name
    target.parent.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(target), full_page=True, animations="disabled")
    image = Image.open(target)
    record: dict[str, object] = {
        "artifact": str(target.relative_to(ROOT)),
        "sha256": image_sha(target),
        "dimensions": list(image.size),
        "status": "baseline-updated" if mode == "update" else "pending",
    }
    if mode == "compare":
        baseline = BASELINE_ROOT / name
        diff = DIFF_ROOT / name
        expect(baseline.exists(), f"Missing hybrid switch baseline: {baseline}")
        record.update(compare_images(baseline, target, diff))
        record["baseline_sha256"] = image_sha(baseline)
        record["diff_artifact"] = str(diff.relative_to(ROOT)) if diff.exists() else None
        expect(record["status"] == "passed", f"Hybrid switch visual mismatch: {record}")
    records.append(record)


def run(mode: str) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, executable_path=str(CHROMIUM), args=["--no-sandbox"])
        page = browser.new_page(viewport=VIEWPORT, device_scale_factor=1)
        errors = load_variant(page, VARIANT, "authored")
        report = page.locator("[data-hybrid-mode-control='report']")
        explore = page.locator("[data-hybrid-mode-control='explore']")
        expect(page.locator("body").get_attribute("data-hybrid-mode") == "report", "V6 must open in Report mode.")
        expect(report.get_attribute("aria-pressed") == "true", "Report must expose a persistent selected-state signal.")
        initial_count = state_count(page)
        capture(page, mode, "v6-switch-report-desktop.png", records)
        explore.focus()
        expect(explore.evaluate("el => document.activeElement === el"), "Explore mode control must accept keyboard focus.")
        explore.press("Enter")
        expect(page.locator("body").get_attribute("data-hybrid-mode") == "explore", "Enter on Explore must reveal the workbench.")
        expect(explore.get_attribute("aria-pressed") == "true", "Explore must expose aria-pressed=true.")
        expect(page.locator(".v6-fields").is_visible(), "Explore must reveal field controls.")
        expect(page.locator(".v6-filters").is_visible(), "Explore must reveal condition controls.")
        expect(page.locator(".v6-distribution").is_visible(), "Explore must retain distribution context.")
        expect(state_count(page) == initial_count, "Changing mode must not reset the table state.")
        capture(page, mode, "v6-switch-explore-desktop.png", records)
        report.focus()
        report.press("Enter")
        expect(page.locator("body").get_attribute("data-hybrid-mode") == "report", "Report must be recoverable by keyboard.")
        expect(state_count(page) == initial_count, "Returning to Report must preserve table state.")
        assert_no_page_errors(errors, "v6 hybrid switch")
        page.close()
        browser.close()
    return records


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["update", "compare"])
    args = parser.parse_args()
    try:
        records = run(args.mode)
    except VerificationFailure as error:
        print(f"HYBRID VERIFICATION FAILED: {error}", file=sys.stderr)
        return 1
    REPORT.write_text(json.dumps({
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": args.mode,
        "browser": "Chromium",
        "assertions": "passed",
        "cases": records,
    }, indent=2) + "\n", encoding="utf-8")
    print(f"Verified V6 Report/Explore mode boundary in {args.mode} mode.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
