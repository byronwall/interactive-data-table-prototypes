#!/usr/bin/env python3
"""Strict integrity and semantic checks for the seven-part compressed runtime."""
from __future__ import annotations
import base64, binascii, gzip, hashlib, json, re, struct, zlib
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; RUNTIME=ROOT/"variants"/"assets"/"runtime"; REPORT=ROOT/"tests"/"payload-integrity-report.json"
parts=sorted(RUNTIME.glob("payload-part-*.js")); assert len(parts)==7, f"expected 7 parts, got {len(parts)}"
chunks=[]
for path in parts:
    match=re.fullmatch(r'window\.__TABLE_RUNTIME_PAYLOAD__\.push\("([A-Za-z0-9+/=]+)"\);\s*',path.read_text(encoding="utf-8")); assert match,f"malformed {path}"; chunks.append(match.group(1))
encoded="".join(chunks); compressed=base64.b64decode(encoded,validate=True); expected_crc,expected_size=struct.unpack("<II",compressed[-8:]); raw=gzip.decompress(compressed); assert len(raw)==expected_size; assert zlib.crc32(raw)&0xffffffff==expected_crc
payload=json.loads(raw.decode("utf-8")); assert set(payload)=={"css","app"}; app=payload["app"]; markers=["FIXED_TODAY","PAGE_SIZE = 12","AUTHORED_FIELDS","const VARIANTS","IMPLEMENTED_VARIANTS","const SCENARIOS","const FIELD_DEFS"]
missing=[marker for marker in markers if marker not in app]; assert not missing,missing
assert all(f'{{ id: "v{i}"' in app for i in range(1,7)),"six-variant registry missing"
report={"generated_at":datetime.now(timezone.utc).isoformat(),"status":"passed","parts":len(parts),"base64_length":len(encoded),"gzip_bytes":len(compressed),"gzip_crc32":f"{expected_crc:08x}","uncompressed_bytes":len(raw),"payload_sha256":hashlib.sha256(raw).hexdigest(),"css_bytes":len(payload["css"].encode()),"app_bytes":len(payload["app"].encode()),"keys":sorted(payload),"markers":markers}
REPORT.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8"); print(json.dumps(report,indent=2))
