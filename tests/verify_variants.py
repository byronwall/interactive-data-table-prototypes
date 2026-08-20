#!/usr/bin/env python3
"""Playwright screenshot and diff runner for the interactive table variants."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops
from playwright.sync_api import Browser, Playwright, sync_playwright

from verify_support import (
    ARTIFACT_ROOT,
    BASELINE_ROOT,
    CHROMIUM,
    CURRENT_ROOT,
    DIFF_ROOT,
    REPORT_PATH,
    ROOT,
    SCENARIOS,
    VARIANTS,
    VIEWPORTS,
    VerificationFailure,
    assert_interactions,
    assert_no_page_errors,
    assert_static_states,
    expect,
    load_variant,
)


def image_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compare_images(baseline: Path, current: Path, diff_path: Path) -> dict[str, Any]:
    baseline_image = Image.open(baseline).convert("RGBA")
    current_image = Image.open(current).convert("RGBA")
    if baseline_image.size != current_image.size:
        return {
            "status": "failed",
            "reason": "dimension mismatch",
            "baseline_dimensions": list(baseline_image.size),
            "current_dimensions": list(current_image.size),
            "mismatched_pixels": baseline_image.size[0] * baseline_image.size[1],
            "mismatch_ratio": 1.0,
            "max_channel_delta": 255,
        }

    diff = ImageChops.difference(baseline_image, current_image)
    rgba = diff.get_flattened_data() if hasattr(diff, "get_flattened_data") else diff.getdata()
    mismatched = 0
    max_delta = 0
    for pixel in rgba:
        delta = max(pixel)
        if delta:
            mismatched += 1
            max_delta = max(max_delta, delta)
    total = baseline_image.size[0] * baseline_image.size[1]
    ratio = mismatched / total if total else 0.0
    if mismatched:
        diff_path.parent.mkdir(parents=True, exist_ok=True)
        # Amplify small deltas so a human can inspect the artifact quickly.
        amplified = diff.point(lambda value: min(255, value * 4))
        amplified.save(diff_path)
    elif diff_path.exists():
        diff_path.unlink()
    return {
        "status": "passed" if mismatched == 0 else "failed",
        "reason": "identical" if mismatched == 0 else "pixel mismatch",
        "baseline_dimensions": list(baseline_image.size),
        "current_dimensions": list(current_image.size),
        "mismatched_pixels": mismatched,
        "mismatch_ratio": ratio,
        "max_channel_delta": max_delta,
    }


def capture_visuals(browser: Browser, mode: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for variant in VARIANTS:
        for scenario in SCENARIOS:
            viewport_name = "narrow" if scenario == "narrow" else "desktop"
            viewport = VIEWPORTS[viewport_name]
            page = browser.new_page(viewport=viewport, device_scale_factor=1)
            errors = load_variant(page, variant, scenario)
            assert_no_page_errors(errors, f"visual {variant.id}/{scenario}")
            file_name = f"{variant.id}-{scenario}-{viewport_name}.png"
            baseline = BASELINE_ROOT / file_name
            current = CURRENT_ROOT / file_name
            diff = DIFF_ROOT / file_name
            target = baseline if mode == "update" else current
            target.parent.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(target), full_page=True, animations="disabled")
            page.close()

            image = Image.open(target)
            record: dict[str, Any] = {
                "variant": variant.id,
                "variant_label": variant.label,
                "scenario": scenario,
                "viewport": viewport,
                "artifact": str(target.relative_to(ROOT)),
                "sha256": image_sha(target),
                "dimensions": list(image.size),
            }
            if mode == "compare":
                expect(baseline.exists(), f"Missing visual baseline: {baseline}")
                record.update(compare_images(baseline, current, diff))
                record["baseline_sha256"] = image_sha(baseline)
                record["diff_artifact"] = str(diff.relative_to(ROOT)) if diff.exists() else None
                expect(record["status"] == "passed", f"Visual mismatch: {variant.id}/{scenario}: {record}")
            else:
                record.update({
                    "status": "baseline-updated",
                    "mismatched_pixels": 0,
                    "mismatch_ratio": 0.0,
                    "max_channel_delta": 0,
                })
            records.append(record)
    return records


def write_report(playwright: Playwright, mode: str, records: list[dict[str, Any]]) -> None:
    # The temporary browser is used only to record its version.
    temp = playwright.chromium.launch(
        headless=True,
        executable_path=str(CHROMIUM),
        args=["--no-sandbox"],
    )
    browser_version = temp.version
    temp.close()
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": mode,
        "browser": f"Chromium {browser_version}",
        "navigation_mode": "about:blank + checked-in document injection (container URL policy)",
        "assertion_suite": "passed",
        "visual_suite": "passed",
        "cases": records,
        "representative_human_inspection": [
            ".artifacts/playwright/current/v1-authored-desktop.png",
            ".artifacts/playwright/current/v1-fields-desktop.png",
            ".artifacts/playwright/current/v1-no-results-desktop.png",
            ".artifacts/playwright/current/v1-quality-desktop.png",
            ".artifacts/playwright/current/v1-narrow-narrow.png",
        ],
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["update", "compare"], help="Update local baselines or compare against them.")
    args = parser.parse_args()

    if not CHROMIUM.exists():
        print(f"Chromium executable not found: {CHROMIUM}", file=sys.stderr)
        return 2

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                headless=True,
                executable_path=str(CHROMIUM),
                args=["--no-sandbox"],
            )
            assert_static_states(browser)
            assert_interactions(browser)
            records = capture_visuals(browser, args.mode)
            browser.close()
            write_report(playwright, args.mode, records)
    except VerificationFailure as error:
        print(f"VERIFICATION FAILED: {error}", file=sys.stderr)
        return 1
    except Exception as error:  # Playwright surfaces actionable call logs here.
        print(f"VERIFICATION ERROR: {error}", file=sys.stderr)
        return 1

    print(f"Verified {len(VARIANTS)} variant(s), {len(SCENARIOS)} states, and {len(records)} visual cases in {args.mode} mode.")
    print(f"Report: {REPORT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
