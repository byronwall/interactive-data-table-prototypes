#!/usr/bin/env python3
"""Verify cross-page variant switching preserves each variant's table configuration."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone

from PIL import Image
from playwright.sync_api import Page, sync_playwright

from verify_support import (
    APP_TEXT,
    BASELINE_ROOT,
    CHROMIUM,
    CURRENT_ROOT,
    DIFF_ROOT,
    MANIFEST_TEXT,
    ROOT,
    Variant,
    VerificationFailure,
    assert_no_page_errors,
    compare_images,
    expect,
    image_sha,
    load_variant,
    state_count,
    strip_external_assets,
    stylesheet_text,
)

REPORT = ROOT / "tests" / "variant-switch-report.json"
V3 = Variant("v3", "v3-chip-first.html", "Chip-First Filter Mode")
V6 = Variant("v6", "v6-hybrid.html", "Hybrid Report + Workbench Mode")
VIEWPORT = {"width": 1440, "height": 1000}


def load_unseeded(page: Page, variant: Variant) -> list[str]:
    source = (ROOT / "variants" / variant.file).read_text(encoding="utf-8")
    html = strip_external_assets(source)
    errors: list[str] = []
    page.on("console", lambda message: errors.append(f"console error: {message.text}") if message.type == "error" else None)
    page.on("pageerror", lambda error: errors.append(f"page error: {error}"))
    page.goto("about:blank")
    page.set_content(html, wait_until="domcontentloaded")
    page.add_style_tag(content=stylesheet_text(source))
    page.add_script_tag(content=MANIFEST_TEXT)
    page.add_script_tag(content=APP_TEXT)
    page.wait_for_selector(".state-summary", state="visible")
    page.wait_for_timeout(30)
    return errors


def capture(page: Page, mode: str, name: str, records: list[dict[str, object]]) -> None:
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
        expect(baseline.exists(), f"Missing variant-switch baseline: {baseline}")
        record.update(compare_images(baseline, target, diff))
        record["baseline_sha256"] = image_sha(baseline)
        record["diff_artifact"] = str(diff.relative_to(ROOT)) if diff.exists() else None
        expect(record["status"] == "passed", f"Variant-switch visual mismatch: {record}")
    records.append(record)


def run(mode: str) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, executable_path=str(CHROMIUM), args=["--no-sandbox"])
        page = browser.new_page(viewport=VIEWPORT, device_scale_factor=1)
        v3_errors = load_variant(page, V3, "authored")
        page.locator("[data-action='scenario']").select_option("filtered")
        expect(state_count(page) == "24 of 126 orders", "V3 must retain its canonical filtered state before switching.")
        expect(page.locator(".filter-chip").count() == 2, "V3 must retain both named condition chips before switching.")
        capture(page, mode, "switch-v3-filtered-before-desktop.png", records)
        assert_no_page_errors(v3_errors, "variant switch v3 before")
        v6_errors = load_variant(page, V6, "authored")
        expect(state_count(page) == "126 orders", "V6 must keep an independent authored state.")
        page.locator("[data-hybrid-mode-control='explore']").click()
        expect(page.locator("body").get_attribute("data-hybrid-mode") == "explore", "V6 Explore mode must remain operable after a cross-page switch.")
        capture(page, mode, "switch-v6-independent-desktop.png", records)
        assert_no_page_errors(v6_errors, "variant switch v6")
        restored_errors = load_unseeded(page, V3)
        expect(state_count(page) == "24 of 126 orders", "Returning to V3 must restore its previous table configuration.")
        expect(page.locator(".filter-chip").count() == 2, "Returning to V3 must restore its condition chips.")
        capture(page, mode, "switch-v3-restored-desktop.png", records)
        assert_no_page_errors(restored_errors, "variant switch v3 restored")
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
        print(f"VARIANT SWITCH VERIFICATION FAILED: {error}", file=sys.stderr)
        return 1
    REPORT.write_text(json.dumps({
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": args.mode,
        "browser": "Chromium",
        "assertions": "passed",
        "cases": records,
    }, indent=2) + "\n", encoding="utf-8")
    print(f"Verified cross-variant state preservation in {args.mode} mode.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
