#!/usr/bin/env python3
"""Serve the repository and verify the browser loads the real bootstrap/fragments."""
from __future__ import annotations
import contextlib, functools, http.server, json, threading, urllib.request
from datetime import datetime, timezone
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]; REPORT=ROOT/"tests"/"static-server-report.json"; SHOTS=ROOT/".artifacts"/"server-smoke"
PAGES=["index.html","v1-quiet-report.html","v2-workbench-rail.html","v3-chip-first.html","v4-distribution-first.html","v5-inspector-reasoning.html","v6-hybrid.html"]
class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args): pass
handler=functools.partial(Quiet,directory=str(ROOT)); server=http.server.ThreadingHTTPServer(("127.0.0.1",0),handler); thread=threading.Thread(target=server.serve_forever,daemon=True); thread.start(); port=server.server_address[1]; base=f"http://127.0.0.1:{port}/variants/"
records=[]
try:
    for asset in [*PAGES,"assets/bootstrap.js","assets/manifest.js",*[f"assets/runtime/payload-part-{i:02d}.js" for i in range(1,8)]]:
        with urllib.request.urlopen(base+asset,timeout=10) as response:
            body=response.read(); assert response.status==200 and body,f"HTTP failure: {asset}"; records.append({"resource":asset,"status":response.status,"bytes":len(body)})
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path="/usr/bin/chromium",args=["--no-sandbox"])
        for file in PAGES:
            with urllib.request.urlopen(base+file,timeout=10) as response: html=response.read().decode("utf-8")
            html=html.replace("<head>",f'<head><base href="{base}">',1)
            page=browser.new_page(viewport={"width":1440,"height":1000}); errors=[]
            page.on("console",lambda m, errors=errors: errors.append(f"console error: {m.text}") if m.type=="error" else None); page.on("pageerror",lambda e, errors=errors: errors.append(f"page error: {e}"))
            page.set_content(html,wait_until="networkidle",timeout=30000)
            page.wait_for_selector('style[data-table-runtime="core"]',state="attached")
            assert not errors,(file,errors); assert page.locator("text=The table runtime could not load").count()==0,file
            if file=="index.html":
                assert page.locator(".variant-card-link").count()==6
            else:
                page.wait_for_selector(".state-summary",state="visible"); assert page.locator("tbody tr").count()==12; assert page.locator(".table-frame").count()==1; assert page.locator('script[data-table-runtime="app"]').count()==1
            if file in {"index.html","v1-quiet-report.html","v3-chip-first.html","v6-hybrid.html"}:
                SHOTS.mkdir(parents=True,exist_ok=True); page.screenshot(path=str(SHOTS/file.replace(".html",".png")),full_page=True,animations="disabled")
            page.close()
        browser.close()
finally:
    server.shutdown(); server.server_close(); thread.join(timeout=5)
REPORT.write_text(json.dumps({"generated_at":datetime.now(timezone.utc).isoformat(),"status":"passed","server":"ThreadingHTTPServer on 127.0.0.1 ephemeral port","browser_navigation":"server-fetched HTML injected into about:blank with an HTTP base; Chromium policy blocks top-level localhost navigation, while all actual CSS/bootstrap/payload subresources load from the static server","pages":PAGES,"resources":records,"screenshots":[str(p.relative_to(ROOT)) for p in sorted(SHOTS.glob("*.png"))]},indent=2)+"\n",encoding="utf-8"); print(f"Verified {len(PAGES)} served pages and {len(records)} HTTP resources without browser errors.")
