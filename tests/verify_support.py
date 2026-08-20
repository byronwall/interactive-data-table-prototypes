"""Shared state and interaction assertions for the table variant verifier.

The container's Chromium policy blocks http://, https://, and file:// top-level
navigation. The harness therefore navigates to about:blank, injects the checked-in
HTML/CSS/JS verbatim, and exercises the resulting browser document. Relative hrefs
and cross-page switch targets are asserted separately; later variant-switch checks
load the referenced document into the same browser page so session fallback storage
is preserved.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops
from playwright.sync_api import Browser, Page, Playwright, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_ROOT = ROOT / ".artifacts" / "playwright"
BASELINE_ROOT = ARTIFACT_ROOT / "baselines"
CURRENT_ROOT = ARTIFACT_ROOT / "current"
DIFF_ROOT = ARTIFACT_ROOT / "diffs"
REPORT_PATH = ROOT / "tests" / "visual-report.json"
CHROMIUM = Path("/usr/bin/chromium")

RUNTIME_ROOT = ROOT / "variants" / "assets" / "runtime"


def read_runtime_payload() -> dict[str, str]:
    encoded: list[str] = []
    for path in sorted(RUNTIME_ROOT.glob("payload-part-*.js")):
        source = path.read_text(encoding="utf-8")
        match = re.fullmatch(r'window\.__TABLE_RUNTIME_PAYLOAD__\.push\("([A-Za-z0-9+/=]+)"\);\s*', source)
        if match is None:
            raise RuntimeError(f"Malformed runtime payload part: {path}")
        encoded.append(match.group(1))
    if not encoded:
        raise RuntimeError("No runtime payload parts found.")
    import base64
    import gzip
    compressed = base64.b64decode("".join(encoded))
    return json.loads(gzip.decompress(compressed).decode("utf-8"))


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
]

SCENARIOS = [
    "authored",
    "filtered",
    "fields",
    "detail",
    "no-results",
    "saved",
    "quality",
    "narrow",
]

VIEWPORTS = {
    "desktop": {"width": 1440, "height": 1000},
    "narrow": {"width": 760, "height": 1000},
}


class VerificationFailure(AssertionError):
    pass


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationFailure(message)


def stylesheet_text(html: str) -> str:
    chunks = [CSS_TEXT]
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
    replacement = rf'\1 data-scenario="{scenario}"'
    updated, count = re.subn(pattern, replacement, html, count=1)
    expect(count == 1, "Variant HTML must expose data-variant on <body>.")
    return updated


def load_variant(page: Page, variant: Variant, scenario: str) -> list[str]:
    source = (ROOT / "variants" / variant.file).read_text(encoding="utf-8")
    css_text = stylesheet_text(source)
    html = with_scenario(strip_external_assets(source), scenario)
    errors: list[str] = []

    def on_console(message: Any) -> None:
        if message.type == "error":
            errors.append(f"console error: {message.text}")

    page.on("console", on_console)
    page.on("pageerror", lambda error: errors.append(f"page error: {error}"))
    page.goto("about:blank")
    page.set_content(html, wait_until="domcontentloaded")
    page.add_style_tag(content=css_text)
    page.add_script_tag(content=MANIFEST_TEXT)
    page.add_script_tag(content=APP_TEXT)
    page.wait_for_selector(".state-summary", state="visible")
    page.wait_for_timeout(30)
    return errors


def state_count(page: Page) -> str:
    return page.locator(".state-summary__counts strong").inner_text().strip()


def assert_no_page_errors(errors: list[str], context: str) -> None:
    expect(not errors, f"{context} emitted browser errors: {errors}")


def assert_static_states(browser: Browser) -> None:
    variant = VARIANTS[0]
    expected = {
        "authored": "126 orders",
        "filtered": "24 of 126 orders",
        "fields": "126 orders",
        "detail": "1 of 126 orders",
        "no-results": "0 of 126 orders",
        "saved": "24 of 126 orders",
        "quality": "1 of 126 orders",
        "narrow": "24 of 126 orders",
    }

    for scenario in SCENARIOS:
        viewport = VIEWPORTS["narrow" if scenario == "narrow" else "desktop"]
        page = browser.new_page(viewport=viewport)
        errors = load_variant(page, variant, scenario)
        context = f"{variant.id}/{scenario}"
        expect(state_count(page) == expected[scenario], f"{context}: unexpected result count")
        expect(page.locator("[data-component='variant-nav']").count() == 1, f"{context}: variant navigation missing")
        expect(page.locator("[data-component='scenario-nav'] select").count() == 1, f"{context}: scenario selector missing")
        expect(page.locator("[data-action='search']").count() == 1, f"{context}: global search missing")
        expect(page.locator("[data-action='open-fields']").count() == 1, f"{context}: field entry point missing")
        expect(page.locator("[data-action='open-filters']").count() == 1, f"{context}: filter entry point missing")

        if scenario == "authored":
            expect(page.locator("tbody tr").count() == 12, "Authored state must render the first 12-row page.")
            expect(page.locator("thead th").count() == 6, "Authored state must show six fields.")
            expect(page.locator(".filter-chip").count() == 0, "Authored state must start without query chips.")
            expect(page.locator(".save-indicator").inner_text().strip().endswith("Saved"), "Authored state must be saved.")
        elif scenario == "filtered":
            expect(page.locator(".filter-chip").count() == 2, "Filtered state must expose two removable conditions.")
            chip_text = " ".join(page.locator(".filter-chip").all_inner_texts()).lower()
            expect("category" in chip_text and "range" in chip_text, "Filter chips must name their modes.")
        elif scenario == "fields":
            field_dialog = page.locator("dialog[data-surface='fields']")
            expect(field_dialog.get_attribute("open") is not None, "Field explorer scenario must open the modal.")
            expect(page.locator(".field-item").count() == 12, "Field explorer must list all twelve fields.")
            expect(page.locator(".field-item.is-selected").count() == 6, "Field explorer must persist six selected fields.")
            expect(page.locator("input[data-action='field-width']").count() == 12, "Every field needs a width control.")
        elif scenario == "detail":
            expect(page.locator("[data-surface='detail']").is_visible(), "Detail scenario must open rich detail.")
            expect("Why this row is here" in page.locator(".match-reasoning").inner_text(), "Detail must explain match reasoning.")
            expect("Hidden field disclosed" in page.locator(".match-reasoning").inner_text(), "Hidden search evidence must be disclosed.")
        elif scenario == "no-results":
            expect(page.locator(".no-results").count() == 1, "No-results state must retain a recovery surface.")
            expect(page.locator("[data-action='clear-all']").count() >= 1, "No-results state needs clear-all recovery.")
            expect(page.locator("tbody tr").count() == 0, "No-results state must render no rows.")
        elif scenario == "saved":
            selected_view = page.locator("[data-action='load-view'] option:checked").inner_text()
            expect(selected_view == "Regional risk review", "Saved state must select the named view.")
            expect("Modified" in page.locator(".save-indicator").inner_text(), "Saved-state variation must make later edits explicit.")
            headers = page.locator("thead th").all_inner_texts()
            expect(any("REGION" in header for header in headers), "Saved view must restore the Region field.")
        elif scenario == "quality":
            expect(page.locator(".quality-warning").is_visible(), "Quality state must show a persistent warning.")
            expect("2026-99-14" in page.locator(".quality-warning").inner_text(), "Warning must retain the malformed source value.")
            expect(page.locator(".detail-quality").count() == 1, "Detail must repeat the quality issue with recovery context.")
        elif scenario == "narrow":
            expect(page.locator(".narrow-note").is_visible(), "Narrow state must explain off-screen fields.")
            dimensions = page.locator(".table-scroll").evaluate("el => ({client: el.clientWidth, scroll: el.scrollWidth})")
            expect(dimensions["scroll"] > dimensions["client"], "Narrow table must keep explicit horizontal overflow.")
            body_width = page.locator("body").evaluate("el => el.scrollWidth")
            expect(body_width <= viewport["width"] + 1, "Narrow composition must not collapse the page into body overflow.")

        assert_no_page_errors(errors, context)
        page.close()


def assert_interactions(browser: Browser) -> None:
    variant = VARIANTS[0]
    page = browser.new_page(viewport=VIEWPORTS["desktop"])
    errors = load_variant(page, variant, "authored")

    # Keyboard search path.
    page.locator("body").press("/")
    search_control = page.locator("[data-action='search']")
    expect(search_control.evaluate("el => document.activeElement === el"), "Slash shortcut must focus global search.")

    # Scenario changes are in-place and deterministic.
    scenario = page.locator("[data-action='scenario']")
    scenario.select_option("filtered")
    expect(state_count(page) == "24 of 126 orders", "Scenario selector must load canonical filtered state without a page reload.")
    scenario.select_option("authored")
    expect(state_count(page) == "126 orders", "Scenario selector must recover authored default.")

    # Field dialog focus restoration, field search, multi-select, and empty selection.
    fields_trigger = page.locator("[data-component='command-bar'] [data-action='open-fields']")
    fields_trigger.focus()
    fields_trigger.click()
    page.wait_for_selector("dialog[data-surface='fields'][open]")
    page.locator("[data-action='field-searchW]").fill("Source")
    expect(page.locator(".field-item").count() == 1, "Field search must narrow to Source ID.")
    page.locator("[data-action='field-searchW]").fill("")
    page.locator("[data-action='clear-fields']").click()
    expect(page.locator(".selected-counter strong").inner_text() == "0", "Clear selection must persist a zero-selected indicator.")
    expect(page.locator(".selection-empty").count() == 1, "Field explorer must show its zero-selected recovery state.")
    page.locator("[data-action='close-surface'][data-surface-name='fields']").click()
    expect(fields_trigger.evaluate("el => document.activeElement === el"), "Closing the field explorer must restore focus to its trigger.")
    expect(page.locator(".table-empty").count() == 1, "The table frame must remain stable with no selected fields.")
    page.locator(".table-empty [data-action='select-authored-fields']").click()
    expect(page.locator("thead th").count() == 6, "Authored fields must recover from an empty selection.")

    # Filter builder validation and explicit category mode.
    page.locator("[data-action='open-filters']").click()
    page.wait_for_selector("dialog[data-surface='filters'][open]")
    expect(page.locator(".validation-message.is-error").count() == 1, "Blank category condition must explain its validation error.")
    page.locator("[data-action='builder-category'][value='At risk']").check()
    page.locator("[data-action='builder-category'][value='Blocked']").check()
    expect("orders would match" in page.locator(".validation-message").inner_text(), "Builder must report a live result count.")
    page.locator("form[data-filter-form] button[type='submit']").click()
    expect(page.locator(".filter-chip").count() == 1, "Applied condition must become a removable chip.")

    # Numeric raw/normalized control remains explicit.
    normalized = page.locator("[data-action='distribution-scale'][value='normalized']")
    page.locator(".scale-toggle label", has_text="Normalized").click()
    expect(normalized.is_checked(), "Numeric distribution must switch to normalized rendering.")
    page.locator(".scale-toggle label", has_text="Raw").click()

    # No-results recovery.
    scenario.select_option("no-results")
    page.locator(".no-results [data-action='clear-all']").click()
    expect(state_count(page) == "126 orders", "Clear-all must recover the complete dataset from no results.")

    # Save dialog validation and named checkpoint.
    page.locator("[data-action='save-view']").click()
    save_dialog = page.locator("dialog[data-global-dialog='save-view']")
    expect(save_dialog.get_attribute("open") is not None, "Save-as-new must open an accessible dialog.")
    save_dialog.locator("input[name='name']").fill("")
    save_dialog.locator("button[value='confirm']").click()
    expect(save_dialog.locator("[data-name-error]").is_visible(), "Empty view name must show validation feedback.")
    save_dialog.locator("input[name='name']").fill("Playwright checkpoint")
    save_dialog.locator("button[value='confirm']").click()
    page.wait_for_function("""() => [...document.querySelectorAll('[data-action="load-view"] option')].some((option) => option.textContent === 'Playwright checkpoint')""")
    expect(page.locator("[data-action='load-view'] option", has_text="Playwright checkpoint").count() == 1, "Named view must be added to the selector.")
    expect("Saved" in page.locator(".save-indicator").inner_text(), "Saving must clear the modified indicator.")

    assert_no_page_errors(errors, "v1 interactions")
    page.close()


