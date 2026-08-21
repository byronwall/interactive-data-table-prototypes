# Published variant runtime repair

## Root cause

The seven JavaScript fragment wrappers were valid and their concatenated string was valid Base64. The decoded gzip member was not valid: its trailer expected CRC32 `bef0e8a0` and 170,275 uncompressed bytes, while raw DEFLATE emitted 170,255 bytes with a different CRC. The output then failed JSON parsing.

A byte-level search against the gzip trailer isolated one corrupted Base64 character at concatenated offset 6,701. The published character was `y`; the authoritative character was `l`. That one six-bit mutation changed two compressed bytes. The DEFLATE stream remained structurally decodable but one back-reference sequence changed, shortening the first block by 20 bytes and invalidating both gzip integrity and JSON.

## Repair

- Reconstructed the authoritative `{ "css", "app" }` payload containing the variant-specific runtime.
- Recompressed it deterministically with gzip level 9 and `mtime=0`, then compared the authoritative Base64 stream against the published seven-part stream.
- Re-splitting at the original publication boundaries proved Parts 2–7 were already byte-identical to the authoritative stream. Only Part 1 contained the mutation, so the committed repair replaces that shard while retaining the six already-correct blobs. The seven files are still validated together as one concatenated stream.
- Restored the missing V3 Chip-First page and stylesheet.
- Published all six pages through the index and variant manifests.
- Added strict payload, static-server, state, visual, hybrid-mode, and cross-variant persistence checks.

## Verification

The repaired stream has:

- Base64 length: 46,412
- gzip length: 34,809 bytes
- gzip CRC32: `bef0e8a0`
- uncompressed length: 170,275 bytes
- payload SHA-256: `1dd622dc94f2424523b73cbfbcaf611372897c4bd0a63c5d5cab3142568d94ef`
- JSON keys: `app`, `css`

The decoded app includes `FIXED_TODAY`, `PAGE_SIZE = 12`, `AUTHORED_FIELDS`, `VARIANTS`, `IMPLEMENTED_VARIANTS`, `SCENARIOS`, and `FIELD_DEFS`.

A local static server served the index, six variants, bootstrap, manifest, and seven fragments. Browser smoke checks reported no compressed-payload alert, console error, or page error, and all six styled tables mounted. Playwright then passed 48 required-state cases, two V6 mode cases, and three cross-variant restoration cases with zero pixel mismatches.
