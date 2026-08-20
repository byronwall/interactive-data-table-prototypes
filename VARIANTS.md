# Interactive table variants tracker

This file is updated in every pushed implementation commit. Screenshot binaries are generated under `.artifacts/playwright/`; durable results are recorded in `tests/visual-report.json`.

## Delivery status

| Variant | Primary interaction premise | Implementation | Required states | Playwright | Visual artifacts |
| --- | --- | --- | --- | --- | --- |
| V1 Quiet Report | Report-first with focused disclosure | Complete | 8/8 | Passed: semantic + interaction suite | 8 baseline/current pairs; 0 pixel mismatches |
| V2 Workbench Rail | Persistent configuration rail | Complete | 8/8 | Passed: semantic states | 8 baseline/current pairs; 0 pixel mismatches |
| V3 Chip-First | Editable condition chips | Not started | Not started | Not run | Not generated |
| V4 Distribution-First | Visual distributions drive filtering | Not started | Not started | Not run | Not generated |
| V5 Inspector Reasoning | Row and query explanation panel | Not started | Not started | Not run | Not generated |
| V6 Hybrid | Explicit report/explore modes | Not started | Not started | Not run | Not generated |

## Push log

### Shared foundation — context and decisions

- **Files touched:** `.task-context/interactive-table-variants.md`, `.gitignore`, `VARIANTS.md`.
- **Interaction mechanics changed:** none; this fixes the state architecture, routing model, variant contracts, and visual verification gate before UI code.
- **Rationale:** six composition modules over one tested state runtime preserve meaningful variation and behavioral parity.
- **Tradeoffs:** shared defects may affect all variants; composition APIs must remain loose enough for distinct topologies.
- **State coverage:** specified, not implemented.
- **Playwright checks:** not yet available.
- **Screenshot results:** not yet available.

### Quiet Report Mode — report shell and focused disclosure

- **Files touched:** `variants/index.html`, `variants/v1-quiet-report.html`, `variants/assets/bootstrap.js`, `variants/assets/runtime/payload-part-*.js`, `variants/assets/manifest.js`, `tests/verify_support.py`, `tests/verify_variants.py`, `tests/visual-report.json`, `.task-context/interactive-table-variants.md`, `VARIANTS.md`.
- **Interaction mechanics changed:** added a 126-row deterministic table runtime; report-first command hierarchy; searchable multi-select field modal with reorder/visibility/width/auto-width controls; explicit type-aware filter builder; editable chips and clear-all; saved views/filter sets; raw/normalized numeric distributions with explicit outliers; category/date distributions; recoverable empty states; side detail with hidden-field match reasoning; quality warning and malformed source-value retention; per-variant persistence.
- **Rationale:** the first concept establishes the calmest reading baseline. Advanced controls remain discoverable through labeled Fields and Add filter actions without occupying table width by default.
- **Tradeoffs:** repeated configuration requires reopening a modal; the compact distribution increases vertical length; detail is a sheet rather than a permanently adjacent inspector.
- **State coverage:** authored default, canonical 24-row filtered exploration, field explorer open, rich detail open, no-results recovery, saved-state variation, data-quality warning, and narrow-width composition all pass.
- **Playwright checks:** static state assertions, canonical counts, field search/multi-select/empty recovery, focus restoration, filter validation/live count, raw/normalized toggle, clear-all recovery, save-name validation, and in-place scenario switching passed on Chromium 144.0.7559.96.
- **Screenshot results:** 8 baselines and 8 current captures; exact dimensions; 0 mismatched pixels in every case. Human inspection completed for authored, field explorer, no-results, quality/detail, and narrow frames. Binary artifacts remain under ignored `.artifacts/playwright/`; hashes and results are committed in `tests/visual-report.json`.

### Workbench Rail Mode — persistent configuration rails

- **Files touched:** `variants/v2-workbench-rail.html`, `variants/assets/v2-workbench.css`, `variants/index.html`, `variants/assets/manifest.js`, `tests/verify_support.py`, `tests/verify_variants.py`, `tests/visual-report.json`, `VARIANTS.md`.
- **Interaction mechanics changed:** moved the complete field explorer into a persistent left rail; kept type-aware distributions and the explicit filter builder in a persistent analysis rail; preserved the table and current-query summary in the central work area; retained rich detail as a focused side sheet.
- **Rationale:** repeated analysis benefits from continuous access to visibility, ordering, width, filter, validation, and distribution controls. The table remains the largest object while configuration no longer requires reopening dialogs.
- **Tradeoffs:** default reading calm and table width are reduced; each rail has an internal scroll region; narrow layouts stack bounded work areas before the table rather than pretending all three columns still fit.
- **State coverage:** authored default, canonical 24-row filtered exploration, emphasized persistent field explorer, rich detail, no-results recovery, saved-state variation, data-quality warning, and narrow-width composition all pass.
- **Playwright checks:** the shared semantic state suite passes for all eight scenarios; the deeper interaction suite remains pinned to the shared V1 runtime contract.
- **Screenshot results:** 8 baselines and 8 current captures for V2; exact dimensions and zero mismatched pixels after the comparison pass. Representative authored, fields, no-results, quality, and narrow frames inspected.
