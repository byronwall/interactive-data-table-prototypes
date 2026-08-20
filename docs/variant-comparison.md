# Interactive table variant comparison

## Decision summary

All six concepts use the same deterministic 126-order fixture, shared state engine, typed filter semantics, per-variant persistence, field controls, distribution model, accessibility contract, and eight required review states. The variants differ in interaction premise and information topology rather than color or spacing alone.

## Comparison matrix

| Variant | Field selection | Distribution rendering | Filtering | Recovery and trust | Primary strength | Principal tradeoff |
| --- | --- | --- | --- | --- | --- | --- |
| **V1 Quiet Report** | Searchable multi-select modal; persistent selected/hidden labels; reorder, visibility, width, and auto-width controls | Compact always-visible summary; numeric raw/normalized scale, working-vs-total overlay, explicit outlier lane, category bars, and date periods | Focused explicit builder with named modes, live count, editable/removable chips, saved sets, and clear-all | Strong empty/no-results recovery, focus restoration, validation, quality warning, and hidden-field reasoning in detail | Calm authored reading and maximum table width | Repeated configuration requires reopening focused surfaces |
| **V2 Workbench Rail** | Full field explorer remains in a persistent left rail | Type-aware visual summary remains in the persistent analysis rail | Explicit builder remains visible with validation, chips, sets, reset, and recovery | Continuous access makes iterative correction fast; rich detail stays a focused sheet | Fastest repeated field/filter tuning | Narrower table and the longest narrow-width work path |
| **V3 Chip-First** | Searchable field dialog reached from the primary query shelf; full reorder/width controls remain available | Compact sidecar preserves shape and outlier context | Active conditions are primary editable objects with visible mode labels, live count, remove/edit, saved sets, and clear-all | Best query recoverability and clearest AND-chain manipulation | Filtering clarity and reversible exploration | Field shaping is one layer deeper; query shelf is visually assertive |
| **V4 Distribution-First** | Focused field explorer preserves table configuration depth without crowding the visual canvas | Largest and most legible type-aware canvas; raw/normalized numeric comparison, working-vs-total overlays, categories, periods, malformed values, and outlier lane | Persistent rail supports range, category, period, exact/substring, validation, sets, and reset while visuals stay visible | Visual no-results state retains the full distribution baseline and explicit recovery | Distribution literacy, range selection, and outlier discovery | Row scanning begins lower; authored and narrow states are taller |
| **V5 Inspector & Match-Reasoning** | Focused field explorer distinguishes visible columns from hidden evidence fields | Compact supporting distribution keeps query shape available | Explicit builder and chips feed a persistent AND-chain explanation | Strongest explanation of why a row matches, hidden-field evidence, malformed source values, and data-quality risk | Trust, auditability, and support/debug workflows | Persistent inspector constrains table width |
| **V6 Hybrid Report + Workbench** | Report keeps controls quiet; Explore reveals the full searchable multi-select field surface without remounting the table | Compact in Report; full bounded distribution panel in Explore, with the same raw/normalized and outlier semantics | Report shows the active query; Explore reveals the explicit builder, live count, chips, saved sets, validation, reset, and clear-all | Preserves table/configuration state across mode and variant switches; no-results scenarios intentionally open in Explore | Best overall balance of calm reading and high-control analysis | Adds one explicit posture concept and one action before repeated configuration |

## Recommendation

**Use V6 Hybrid Report + Workbench as the integration baseline.**

- It preserves the authored report as the default instead of making every user pay the visual cost of a permanent workbench.
- It exposes field, filter, validation, recovery, and distribution controls together when the task changes from reading to exploration.
- The mode boundary is explicit, keyboard reachable, and represented with `aria-pressed`; the table and its configuration remain mounted while the posture changes.
- It provides a practical integration path for the strongest specialized mechanics: V3's editable condition shelf, V4's larger distribution canvas, and V5's persistent match evidence can be introduced inside Explore without weakening Report.

V6 is not the universal winner for every role. Use V2 for an analyst-only tool with continuous configuration, V4 for distribution-led investigation, and V5 where auditability or support reasoning dominates. V1 remains the strongest low-complexity report baseline.

## Merge-ready next step

1. Integrate V6's Report/Explore shell into the existing root prototype behind a feature flag while preserving the current table behavior and data contract.
2. Promote three proven mechanics into the Explore posture: V3's editable query shelf, V4's large distribution option, and V5's evidence inspector.
3. Run a task-based evaluation using the shared fixture: authored scan, field reshaping, canonical 24-row query, no-results recovery, outlier identification, and hidden-field match explanation.
4. Keep the six variant pages and Playwright baselines as regression fixtures until the integrated shell passes the same semantic, keyboard, narrow-width, quality, screenshot, and cross-variant persistence gates.

## Verification gate

The release gate covers all six variants and all eight required states at desktop and narrow widths. It asserts semantic state, canonical counts, field search/multi-select/empty recovery, filter validation and live counts, chip removal and clear-all, saved-state validation, raw/normalized distribution controls, outlier visibility, focus restoration, rich detail, quality warning, and no page errors. Dedicated suites also verify keyboard Report/Explore switching and cross-variant state restoration. Screenshot baselines and current captures are compared pixel-for-pixel; reports record browser version, dimensions, hashes, mismatched pixels, and representative frames inspected.
