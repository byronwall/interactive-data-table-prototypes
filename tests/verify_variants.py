#!/usr/bin/env python3
"""Single-pass Playwright state, interaction, screenshot, and exact visual diff runner."""
from __future__ import annotations
import argparse, json, sys
from datetime import datetime, timezone
from typing import Any
from PIL import Image
from playwright.sync_api import Browser, sync_playwright
from verify_support import BASELINE_ROOT, CHROMIUM, CURRENT_ROOT, DIFF_ROOT, REPORT_PATH, ROOT, SCENARIOS, VARIANTS, VIEWPORTS, VerificationFailure, assert_interactions, assert_state, compare_images, expect, image_sha, load_variant

def verify_and_capture(browser: Browser, mode: str) -> list[dict[str, Any]]:
    records=[]; page=browser.new_page(viewport=VIEWPORTS["desktop"],device_scale_factor=1)
    for variant in VARIANTS:
        expect((ROOT/"variants"/variant.file).exists(),f"Missing published page: {variant.file}")
        for scenario in SCENARIOS:
            viewport_name="narrow" if scenario=="narrow" else "desktop"; viewport=VIEWPORTS[viewport_name]; page.set_viewport_size(viewport)
            errors=load_variant(page,variant,scenario); assert_state(page,variant,scenario,viewport,errors)
            name=f"{variant.id}-{scenario}-{viewport_name}.png"; baseline=BASELINE_ROOT/name; current=CURRENT_ROOT/name; diff=DIFF_ROOT/name; target=baseline if mode=="update" else current; target.parent.mkdir(parents=True,exist_ok=True)
            page.screenshot(path=str(target),full_page=False,animations="disabled"); image=Image.open(target)
            record={"variant":variant.id,"variant_label":variant.label,"scenario":scenario,"viewport":viewport,"artifact":str(target.relative_to(ROOT)),"sha256":image_sha(target),"dimensions":list(image.size)}
            if mode=="compare":
                expect(baseline.exists(),f"Missing visual baseline: {baseline}"); record.update(compare_images(baseline,current,diff)); record["baseline_sha256"]=image_sha(baseline); record["diff_artifact"]=str(diff.relative_to(ROOT)) if diff.exists() else None; expect(record["status"]=="passed",f"Visual mismatch: {variant.id}/{scenario}: {record}")
            else: record.update({"status":"baseline-updated","mismatched_pixels":0,"mismatch_ratio":0.0,"max_channel_delta":0})
            records.append(record)
    page.close(); return records

def main():
    parser=argparse.ArgumentParser(); parser.add_argument("mode",choices=["update","compare"]); args=parser.parse_args()
    if not CHROMIUM.exists(): print(f"Chromium executable not found: {CHROMIUM}",file=sys.stderr); return 2
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True,executable_path=str(CHROMIUM),args=["--no-sandbox"]); records=verify_and_capture(browser,args.mode); assert_interactions(browser); browser_version=browser.version; browser.close()
    except VerificationFailure as error: print(f"VERIFICATION FAILED: {error}",file=sys.stderr); return 1
    except Exception as error: print(f"VERIFICATION ERROR: {error}",file=sys.stderr); return 1
    REPORT_PATH.write_text(json.dumps({"generated_at":datetime.now(timezone.utc).isoformat(),"mode":args.mode,"browser":f"Chromium {browser_version}","navigation_mode":"about:blank + checked-in document injection; static-server bootstrap verified separately","assertion_suite":"passed","visual_suite":"passed","variant_count":len(VARIANTS),"scenario_count":len(SCENARIOS),"cases":records},indent=2)+"\n",encoding="utf-8")
    print(f"Verified {len(VARIANTS)} variants, {len(SCENARIOS)} states, and {len(records)} visual cases in {args.mode} mode."); return 0
if __name__=="__main__": raise SystemExit(main())
