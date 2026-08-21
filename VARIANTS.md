# Interactive table variants tracker

The six published variants share one deterministic 126-order state engine while retaining distinct interaction premises. Screenshot binaries remain under ignored `.artifacts/`; durable verification results are committed under `tests/`.

## Delivery status

| Variant | Primary interaction premise | Implementation | Required states | Playwright | Visual artifacts |
| --- | --- | --- | --- | --- | --- |
| V1 Quiet Report | Report-first with focused disclosure | Complete | 8/8 | Passed | 8 exact-diff pairs |
| V2 Workbench Rail | Persistent configuration rail | Complete | 8/8 | Passed | 8 exact-diff pairs |
| V3 Chip-First | Editable condition chain | Complete | 8/8 | Passed | 8 exact-diff pairs |
| V4 Distribution-First | Visual distributions drive filtering | Complete | 8/8 | Passed | 8 exact-diff pairs |
| V5 Inspector Reasoning | Query and row evidence panel | Complete | 8/8 | Passed | 8 exact-diff pairs |
| V6 Hybrid | Explicit report/explore postures | Complete | 8/8 | Passed | 8 exact-diff pairs + 2 mode pairs |

Cross-variant restoration adds three exact-diff captures for V3 filtered, V6 independent, and V3 restored state. All 53 comparison cases report zero mismatched pixels.

## Runtime publication repair — 2026-08-21

- **Root cause:** one Base64 character in the originally published compressed stream was mutated at concatenated offset `6701`: `y` was committed where `l` belonged. The mutation altered two compressed bytes. Raw DEFLATE still produced output, but the first block was 20 bytes short, the gzip CRC/ISIZE trailer no longer matched, and the resulting JSON failed at an invalid escape.
- **Runtime repair:** reconstructed the authoritative variant payload and verified all seven fragments as one coherent stream. Parts 2–7 already matched the authoritative bytes at the original shard boundaries, so the repair replaces only corrupted Part 1 and avoids meaningless churn in six byte-identical blobs. A strict integrity test now covers Base64, gzip CRC/ISIZE, JSON keys, and variant-engine markers.
- **Publication repair:** restored the missing V3 Chip-First page and stylesheet; expanded the index, shared manifest, and inline V4/V5 manifests to all six variants.
- **Test repair:** restored all-six-variant coverage in `verify_support.py`, fixed the field-search selector, consolidated the state/screenshot pass, and changed cross-variant persistence to use a real unseeded saved-filter workflow rather than a deliberately non-persistent scenario seed.
- **Static-server evidence:** seven pages and sixteen HTTP resources load through the real bootstrap/fragments with no compressed-payload alert, console error, or page error. Styled 12-row tables mount on every variant.
- **Payload evidence:** seven parts; Base64 length `46,412`; gzip length `34,809`; CRC32 `bef0e8a0`; uncompressed size `170,275`; payload SHA-256 `1dd622dc94f2424523b73cbfbcaf611372897c4bd0a63c5d5cab3142568d94ef`.
- **Playwright evidence:** six variants × eight states, V6 Report/Explore switching, and V3→V6→V3 state restoration pass on Chromium `144.0.7559.96`.
- **Visual evidence:** 48 state pairs + 2 hybrid pairs + 3 variant-switch pairs; exact dimensions; zero mismatched pixels.

## Durable reports

- `tests/payload-integrity-report.json`
- `tests/static-server-report.json`
- `tests/visual-report.json`
- `tests/hybrid-switch-report.json`
- `tests/variant-switch-report.json`
- `tests/final-verification-summary.json`
