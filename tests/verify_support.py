"""Shared state, interaction, screenshot, and payload helpers for table variants."""
from __future__ import annotations

import base64
import gzip
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops
from playwright.sync_api import Browser, Page

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_ROOT = ROOT / ".artifacts" / "playwright"
BASELINE_ROOT = ARTIFACT_ROOT / "baselines"
CURRENT_ROOT = ARTIFACT_ROOT / "current"
DIFF_ROOT = ARTIFACT_ROOT / "diffs"
REPORT_PATH = ROOT / "tests" / "visual-report.json"
CHROMIUM = Path("/usr/bin/chromium")
RUNTIME_ROOT = ROOT / "variants" / "assets" / "runtime"


def read_runtime_payload() -> dict[str, str]:
    parts = sorted(RUNTIME_ROOT.glob("payload-part-*.js"))
    if len(parts) != 7:
        raise RuntimeError(f"Expected seven runtime payload parts, found {len(parts)}")
    encoded: list[str] = []
    for path in parts:
        source = path.read_text(encoding="utf-8")
        match = re.fullmatch(r'window\.__TABLE_RUNTIME_PAYLOAD__\.push\("([A-Za-z0-9+/=]+)"\);\s*', source)
        if match is None:
            raise RuntimeError(f"Malformed runtime payload part: {path}")
        encoded.append(match.group(1))
    compressed = base64.b64decode("".join(encoded), validate=True)
    payload = json.loads(gzip.decompress(compressed).decode("utf-8"))
    if set(payload) != {"css", "app"}:
        raise RuntimeError(f"Unexpected runtime payload keys: {sorted(payload)}")
    return payload


RUNTIME = read_runtime_payload()
CSS_TEXT = RUNTIME["css"]
APP_TEXT = RUNTIME["app"]
MANIFEST_TEXT = (ROOT / "variants" / "assets" / "manifest.js").read_text(encoding="utf-8")


@dataclass(frozen=True)
class Variant:
    id: str
    file: str
    label: str


VARIANTS = [
    Variant("v1", "v1-quiet-report.html", "Quiet Report Mode"),
    Variant("v2", "v2-workbench-rail.html", "Workbench Rail Mode"),
    Variant("v3", "v3-chip-first.html", "Chip-First Filter Mode"),
    Variant("v4", "v4-distribution-first.html", "Distribution-First Mode"),
    Variant("v5", "v5-inspector-reasoning.html", "Inspector & Match-Reasoning Mode"),
    Variant("v6", "v6-hybrid.html", "Hybrid Report + Workbench Mode"),
]

SCENARIOS = ["authored", "filtered", "fields", "detail", "no-results", "saved", "quality", "narrow"]
VIEWPORTS = {
    "desktop": {"width": 1440, "height": 1000},
    "narrow": {"width": 760, "height": 1000},
}


class VerificationFailure(AssertionError):
    pass


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationFailure(message)


def image_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compare_images(baseline: Path, current: Path, diff_path: Path) -> dict[str, Any]:
    baseline_image = Image.open(baseline).convert("RGBA")
    current_image = Image.open(current).convert("RGBA")
    if baseline_image.size != current_image.size:
        return {
            "status": "failed", "reason": "dimension mismatch",
            "baseline_dimensions": list(baseline_image.size),
            "current_dimensions": list(current_image.size),
            "mismatched_pixels": baseline_image.size[0] * baseline_image.size[1],
            "mismatch_ratio": 1.0, "max_channel_delta": 255,
        }
    diff = ImageChops.difference(baseline_image, current_image)
    if diff.getbbox() is None:
        if diff_path.exists(): diff_path.unlink()
        return {
            "status": "passed", "reason": "identical",
            "baseline_dimensions": list(baseline_image.size),
            "current_dimensions": list(current_image.size),
            "mismatched_pixels": 0, "mismatch_ratio": 0.0, "max_channel_delta": 0,
        }
    import numpy as np
    pixels = np.asarray(diff)
    pixel_delta = pixels.max(axis=2)
    mismatched = int(np.count_nonzero(pixel_delta))
    max_delta = int(pixel_delta.max())
    total = baseline_image.size[0] * baseline_image.size[1]
    diff_path.parent.mkdir(parents=True, exist_ok=True)
    diff.point(lambda value: min(255, value * 4)).save(diff_path)
    return {
        "status": "failed", "reason": "pixel mismatch",
        "baseline_dimensions": list(baseline_image.size),
        "current_dimensions": list(current_image.size),
        "mismatched_pixels": mismatched,
        "mismatch_ratio": mismatched / total if total else 0.0,
        "max_channel_delta": max_delta,
    }


def stylesheet_text(html: str) -> str:
    chunks = [CSS_TEXT]
    for inline in re.findall(r"<style>(.*?)</style>", html, flags=re.DOTALL):
        chunks.append(inline)
    for href in re.findall(r'<link[^>]+href="([^"]+\.css)"[^>]*>', html):
        relative = href.removeprefix("./")
        path = ROOT / "variants" / relative
        expect(path.exists(), f"Missing linked stylesheet: {relative}")
        chunks.append(path.read_text(encoding="utf-8"))
    return "\n".join(chunks)


def strip_external_assets(html: str) -> str:
    html = re.sub(r'<link[^>]+href="[^"]+"[^>]*>', "", html)
    html = re.sub(r'<script[^>]+src="[^"]+"[^>]*></script>', "", html)
    return html


def with_scenario(html: str, scenario: str) -> str:
    pattern = r'(<body\b[^>]*\bdata-variant="[^"]+")'
    updated, count = re.subn(pattern, rf'\1 data-scenario="{scenario}"', html, count=1)
    expect(count == 1, "Variant HTML must expose data-variant on <body>.")
    return updated


def load_variant(page: Page, variant: Variant, scenario: str) -> list[str]:
    source = (ROOT / "variants" / variant.file).read_text(encoding="utf-8")
    html = with_scenario(strip_external_assets(source), scenario)
    if not hasattr(page, "_table_runtime_errors"):
        page._table_runtime_errors = []
        page.on("console", lambda message: page._table_runtime_errors.append(f"console error: {message.text}") if message.type == "error" else None)
        page.on("pageerror", lambda error: page._table_runtime_errors.append(f"page error: {error}"))
    errors = page._table_runtime_errors
    errors.clear()
    page.goto("about:blank")
    page.set_content(html, wait_until="domcontentloaded")
    page.add_style_tag(content=stylesheet_text(source))
    page.add_script_tag(content=MANIFEST_TEXT)
    page.add_script_tag(content=APP_TEXT)
    page.wait_for_selector(".state-summary", state="visible")
    page.wait_for_timeout(10)
    return errors


def state_count(page: Page) -> str:
    return page.locator(".state-summary__counts strong").inner_text().strip()


def assert_no_page_errors(errors: list[str], context: str) -> None:
    expect(not errors, f"{context} emitted browser errors: {errors}")


def assert_state(page: Page, variant: Variant, scenario: str, viewport: dict[str, int], errors: list[str]) -> None:
    expected = {
        "authored": "126 orders", "filtered": "24 of 126 orders", "fields": "126 orders",
        "detail": "1 of 126 orders", "no-results": "0 of 126 orders",
        "saved": "24 of 126 orders", "quality": "1 of 126 orders", "narrow": "24 of 126 orders",
    }
    context = f"{variant.id}/{scenario}"
    expect(state_count(page) == expected[scenario], f"{context}: unexpected result count {state_count(page)!r}")
    expect(page.locator("[data-component='variant-nav']").count() == 1, f"{context}: variant navigation missing")
    expect(page.locator("[data-component='scenario-nav'] select").count() == 1, f"{context}: scenario selector missing")
    expect(page.locator("[data-action='search']").count() == 1, f"{context}: global search missing")
    expect(page.locator("[data-action='open-fields']").count() == 1, f"{context}: field entry point missing")
    expect(page.locator("[data-action='open-filters']").count() == 1, f"{context}: filter entry point missing")
    expect(page.locator("[data-component='table'] .table-frame").count() == 1, f"{context}: styled table frame missing")
    expect(page.locator("[role='alert']", has_text="The table runtime could not load").count() == 0, f"{context}: compressed-payload alert present")

    if scenario == "authored":
        expect(page.locator("tbody tr").count() == 12, f"{context}: authored state must render 12 rows")
        expect(page.locator("thead th").count() == 6, f"{context}: authored state must show six fields")
        expect(page.locator(".filter-chip").count() == 0, f"{context}: authored state must start without chips")
        expect(page.locator(".save-indicator").inner_text().strip().endswith("Saved"), f"{context}: authored state must be saved")
    elif scenario == "filtered":
        expect(page.locator(".filter-chip").count() == 2, f"{context}: filtered state must expose two conditions")
        chip_text = " ".join(page.locator(".filter-chip").all_inner_texts()).lower()
        expect("category" in chip_text and "range" in chip_text, f"{context}: chip modes missing")
    elif scenario == "fields":
        surface = page.locator("[data-surface='fields']")
        expect(surface.is_visible(), f"{context}: field explorer surface must be visible")
        if surface.evaluate("el => el.tagName === 'DIALOG'"):
            expect(surface.get_attribute("open") is not None, f"{context}: field dialog must be open")
        expect(page.locator(".field-item").count() == 12, f"{context}: field explorer must list twelve fields")
        expect(page.locator(".field-item.is-selected").count() == 6, f"{context}: six fields must remain selected")
        expect(page.locator("input[data-action='field-width']").count() == 12, f"{context}: width controls missing")
    elif scenario == "detail":
        surface = page.locator("[data-surface='detail']")
        expect(surface.is_visible(), f"{context}: detail/reasoning surface must be visible")
        expect(page.locator(".match-reasoning").count() >= 1, f"{context}: match reasoning missing")
        reasoning = " ".join(page.locator(".match-reasoning").all_inner_texts())
        expect("Why this row is here" in reasoning, f"{context}: match explanation heading missing")
        expect("Hidden field disclosed" in reasoning, f"{context}: hidden-field evidence missing")
    elif scenario == "no-results":
        expect(page.locator(".no-results").count() == 1, f"{context}: no-results recovery missing")
        expect(page.locator(".no-results [data-action='clear-all']").count() == 1, f"{context}: clear-all recovery missing")
        expect(page.locator("tbody tr").count() == 0, f"{context}: rows remain in no-results state")
    elif scenario == "saved":
        expect(page.locator("[data-action='load-view'] option:checked").inner_text() == "Regional risk review", f"{context}: named view not selected")
        expect("Modified" in page.locator(".save-indicator").inner_text(), f"{context}: modified state not disclosed")
        expect(any("REGION" in header for header in page.locator("thead th").all_inner_texts()), f"{context}: saved Region field missing")
    elif scenario == "quality":
        expect(page.locator(".quality-warning").is_visible(), f"{context}: quality warning hidden")
        expect("2026-99-14" in page.locator(".quality-warning").inner_text(), f"{context}: malformed source value missing")
        expect(page.locator(".detail-quality").count() == 1, f"{context}: detail quality explanation missing")
    elif scenario == "narrow":
        expect(page.locator(".narrow-note").is_visible(), f"{context}: narrow disclosure missing")
        dimensions = page.locator(".table-scroll").evaluate("el => ({client: el.clientWidth, scroll: el.scrollWidth})")
        expect(dimensions["scroll"] > dimensions["client"], f"{context}: narrow table must retain explicit overflow")
        body_width = page.locator("body").evaluate("el => el.scrollWidth")
        expect(body_width <= viewport["width"] + 1, f"{context}: body overflow collapsed the composition ({body_width})")
    assert_no_page_errors(errors, context)


def assert_static_states(browser: Browser) -> None:
    page = browser.new_page(viewport=VIEWPORTS["desktop"], device_scale_factor=1)
    for variant in VARIANTS:
        expect((ROOT / "variants" / variant.file).exists(), f"Missing published page: {variant.file}")
        for scenario in SCENARIOS:
            viewport = VIEWPORTS["narrow" if scenario == "narrow" else "desktop"]
            page.set_viewport_size(viewport)
            errors = load_variant(page, variant, scenario)
            assert_state(page, variant, scenario, viewport, errors)
    page.close()


def assert_interactions(browser: Browser) -> None:
    variant = VARIANTS[0]
    page = browser.new_page(viewport=VIEWPORTS["desktop"])
    errors = load_variant(page, variant, "authored")

    page.locator("body").press("/")
    search_control = page.locator("[data-action='search']")
    expect(search_control.evaluate("el => document.activeElement === el"), "Slash shortcut must focus global search")

    scenario = page.locator("[data-action='scenario']")
    scenario.select_option("filtered")
    expect(state_count(page) == "24 of 126 orders", "Scenario selector must load the canonical filtered state")
    scenario.select_option("authored")
    expect(state_count(page) == "126 orders", "Scenario selector must recover the authored default")

    fields_trigger = page.locator("[data-component='command-bar'] [data-action='open-fields']")
    fields_trigger.focus()
    fields_trigger.click()
    page.wait_for_selector("dialog[data-surface='fields'][open]")
    page.locator("[data-action='field-search']").fill("Source")
    expect(page.locator(".field-item").count() == 1, "Field search must narrow to Source ID")
    page.locator("[data-action='field-search']").fill("")
    page.locator("[data-action='clear-fields']").click()
    expect(page.locator(".selected-counter strong").inner_text() == "0", "Clear selection must persist a zero-selected indicator")
    expect(page.locator(".selection-empty").count() == 1, "Field explorer must show its zero-selected recovery state")
    page.locator("[data-action='close-surface'][data-surface-name='fields']").click()
    expect(fields_trigger.evaluate("el => document.activeElement === el"), "Closing fields must restore trigger focus")
    expect(page.locator(".table-empty").count() == 1, "Table frame must remain stable with no selected fields")
    page.locator(".table-empty [data-action='select-authored-fields']").click()
    expect(page.locator("thead th").count() == 6, "Authored fields must recover from an empty selection")

    page.locator("[data-action='open-filters']").click()
    page.wait_for_selector("dialog[data-surface='filters'][open]")
    expect(page.locator(".validation-message.is-error").count() == 1, "Blank category condition must explain validation")
    page.locator("[data-action='builder-category'][value='At risk']").check()
    page.locator("[data-action='builder-category'][value='Blocked']").check()
    expect("orders would match" in page.locator(".validation-message").inner_text(), "Builder must report live result count")
    page.locator("form[data-filter-form] button[type='submit']").click()
    expect(page.locator(".filter-chip").count() == 1, "Applied condition must become a removable chip")

    normalized = page.locator("[data-action='distribution-scale'][value='normalized']")
    page.locator(".scale-toggle label", has_text="Normalized").click()
    expect(normalized.is_checked(), "Distribution must switch to normalized rendering")
    page.locator(".scale-toggle label", has_text="Raw").click()

    scenario.select_option("no-results")
    page.locator(".no-results [data-action='clear-all']").click()
    expect(state_count(page) == "126 orders", "Clear-all must recover complete data from no results")

    page.locator("[data-action='save-view']").click()
    save_dialog = page.locator("dialog[data-global-dialog='save-view']")
    expect(save_dialog.get_attribute("open") is not None, "Save as new must open a dialog")
    save_dialog.locator("input[name='name']").fill("")
    save_dialog.locator("button[value='confirm']").click()
    expect(save_dialog.locator("[data-name-error]").is_visible(), "Empty view name must show validation")
    save_dialog.locator("input[name='name']").fill("Playwright checkpoint")
    save_dialog.locator("button[value='confirm']").click()
    page.wait_for_function("""() => [...document.querySelectorAll('[data-action="load-view"] option')].some((option) => option.textContent === 'Playwright checkpoint')""")
    expect(page.locator("[data-action='load-view'] option", has_text="Playwright checkpoint").count() == 1, "Named view missing")
    expect("Saved" in page.locator(".save-indicator").inner_text(), "Saving must clear modified state")

    assert_no_page_errors(errors, "v1 interactions")
    page.close()
