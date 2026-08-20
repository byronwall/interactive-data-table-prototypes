# Interactive table variants task context

Updated: 2026-08-19

## Source load status

- Read `docs/ui-prototype-brief.md` in full.
- Read `docs/transcripts/README.md` and every transcript listed there, including the empty fragment.
- Read `PRODUCT.md`, `DESIGN.md`, `index.html`, `styles.css`, and `app.js`.
- Read `.codex/skills/consider-contrast/SKILL.md`.
- Read `.codex/skills/impeccable/SKILL.md` plus `reference/new-work.md`, `reference/craft-floor.md`, and `reference/operate.md`.
- Read `docs/consider-contrast-decisions.md`.

## Constraints

- Preserve the existing root prototype. New work belongs under `/variants` with shared modules.
- Use plain HTML, CSS, and JavaScript. No backend or heavy runtime dependency.
- Keep all concepts on `main`; publish each meaningful increment immediately.
- Use a deterministic 126-row purchase-order fixture. The authored default is unfiltered; the canonical exploration state returns exactly 24 rows.
- Every variant exposes authored default, filtered exploration, field explorer open, rich detail open, no-results recovery, narrow width, saved-state, and data-quality warning.
- State is serializable and namespaced by variant so switching concepts does not erase work.
- Playwright navigation, semantic assertions, screenshots, and pixel comparison are release gates.
- Accessibility is part of the interaction contract: keyboard paths, visible focus, overlay focus trap/restore, ARIA state, non-color signals, and reduced-motion handling.

## Assumptions

- The requested local checkout was absent and shell DNS cannot reach GitHub. The authenticated GitHub connector is used for remote commits and pushes.
- A local reconstruction is used for implementation and browser verification. Connector commits preserve the existing remote tree.
- Screenshot binaries remain local under `.artifacts/`; a committed report records hashes, dimensions, comparisons, and inspected scenarios.
- Chromium and Python Playwright are the verification environment.
- The existing root prototype remains unchanged except for optional documentation/navigation links during finalization.

## Decision checkpoints

### Shared implementation architecture

**Decision:** Choose how six materially different concepts share behavior while retaining state.

Scores use 0 for failure and 10 for reliably meeting the named table outcome.

| Approach | Interaction-premise separation | State continuity | Acceptance parity | Defect containment | Main tradeoff |
| --- | ---: | ---: | ---: | ---: | --- |
| Six unrelated pages/scripts | 10 | 2 | 4 | 8 | Maximum freedom creates inconsistent semantics. |
| One monolithic page with CSS modes | 4 | 10 | 9 | 3 | Easy parity, weak variation quality. |
| **Shared runtime with six composition modules** | **9** | **10** | **10** | **7** | Requires explicit extension points. |

- **Choice:** Shared runtime with six composition modules.
- **Why:** It best combines meaningful topology changes, stable state, and acceptance parity.
- **Watch:** Shared helpers must not force identical information hierarchy.
- **Next:** Share data, transitions, filters, distributions, persistence, focus, and test IDs. Keep shell topology, disclosure, density, and primary workflow variant-owned.

### Required-state routing

**Decision:** Make every review state reproducible without reducing prototypes to static frames.

| Approach | Reproducibility | Interaction fidelity | Keyboard discoverability | Saved-state isolation | Main tradeoff |
| --- | ---: | ---: | ---: | ---: | --- |
| Manual setup only | 3 | 10 | 6 | 8 | Weak deterministic review. |
| Static duplicate frames | 10 | 2 | 8 | 2 | Strong screenshots, weak behavior. |
| **Scenario query plus real state engine** | **10** | **10** | **9** | **10** | Scenario seeding must not overwrite ordinary restored state. |

- **Choice:** Scenario query plus real state engine.
- **Why:** Deterministic screenshots and assertions remain fully interactive and recoverable.
- **Watch:** Ordinary navigation restores variant state; explicit scenarios intentionally seed state.
- **Next:** Add a labeled scenario selector, query routes, and variant-scoped storage.

### Visual verification model

**Decision:** Block visual regressions without adding a large binary history.

| Approach | Regression sensitivity | Review traceability | Repository footprint | Runtime stability | Main tradeoff |
| --- | ---: | ---: | ---: | ---: | --- |
| Capture only | 4 | 7 | 10 | 9 | No blocking diff signal. |
| Commit every PNG baseline | 10 | 10 | 2 | 5 | Strong trace, brittle and heavy. |
| **Local baselines plus committed manifest/report** | **9** | **9** | **9** | **8** | Reviewers regenerate pixels locally. |

- **Choice:** Local baselines plus committed manifest/report.
- **Why:** Pixel differences block the run while durable evidence stays small.
- **Watch:** Chromium upgrades require intentional baseline regeneration.
- **Next:** Capture per-variant baselines, compare a second pass, inspect representative images, and commit `tests/visual-report.json`.

## Variant interaction contracts

### V1 — Quiet Report Mode
- Report-first reading surface. Controls use focused dialogs and a quiet summary strip.
- Field selection is a searchable modal; filter construction is a focused overlay.
- Distribution summaries stay restrained near the active slice.
- Tradeoff: maximum default clarity, slower repeated configuration.

### V2 — Workbench Rail Mode
- Persistent left field/filter rail plus dedicated distribution workspace.
- Field rows expose visibility, ordering, width, quality, and compact distributions.
- Tradeoff: fastest iteration, least calm default and least table width.

### V3 — Chip-First Filter Mode
- Active and draft conditions are the primary command surface. Chips are editable objects.
- Field discovery opens from an add-field chip and remains secondary to query construction.
- Tradeoff: filtering is highly recoverable; field-management discovery is less immediate.

### V4 — Distribution-First Mode
- A large type-aware distribution canvas precedes the table and drives filtering.
- Numeric raw/normalized comparison, periods, categories, and outliers are first-class.
- Tradeoff: distribution literacy is strongest; row scanning begins lower.

### V5 — Inspector & Match-Reasoning Mode
- A persistent reasoning inspector explains the active AND chain and selected-row match.
- Hidden-field evidence, malformed values, and record detail share one panel.
- Tradeoff: explanation/recovery are strongest; table width is constrained.

### V6 — Hybrid Report + Workbench Mode
- Opens as a calm report. An explicit Report/Explore switch reveals a bounded workbench without replacing the table.
- Combines compact summary reading with high-control field, filter, and distribution panels.
- Tradeoff: strongest balance; the mode boundary adds one concept to learn.

## Open risks

- Connector and local Git histories are separate. Every remote write must use the latest parent/base tree; every local commit must remain clean.
- Shared abstractions can make variants too similar. Review each against its governing interaction premise.
- Width controls can destabilize narrow layouts. Narrow views explicitly name hidden/off-screen fields and use sheets rather than silent removal.
- Numeric normalization can confuse. Every normalized display keeps raw units in labels and accessible text.
- Pixel tests can be noisy after Chromium changes. Record browser version in the report.
- No independent visual-review subagent is available. Open and inspect representative screenshots directly in addition to automated comparison.

## Implemented checkpoint: V1 Quiet Report Mode

- **Structure:** An editorial report header combines context and a compact command row. State remains a ruled, plain-language line. A compact distribution is always visible, while field/filter configuration uses focused modal surfaces and record detail uses a right sheet.
- **State engine:** One deterministic 126-row fixture produces the exact 24-row canonical slice. Scenario seeding is isolated from the normal per-variant saved state so review URLs do not overwrite a user's working configuration.
- **Storage:** `localStorage` is primary. A `window.name` session fallback allows the same state code to execute under browsers where storage is denied, including the constrained verification runtime.
- **Field mechanics:** Search, all/selected/hidden scopes, multi-select, persistent selected/hidden labels, empty-selection recovery, order controls, range width controls, auto width, field signals, and compact distributions.
- **Filter mechanics:** Explicit field/operator/value builder; exact substring, category, range, presence, list count, explicit date bounds, and period presets; live count, validation states, editable/removable chips, saved filter sets, clear conditions, and clear-all recovery.
- **Distribution mechanics:** Working-set overlays against all 126 rows, raw/normalized amount scale, capped main histogram, explicit high-outlier lane, category bars, date periods, and malformed-date disclosure.
- **Accessibility:** Native table and dialog semantics, slash shortcut, visible focus, modal close and focus restoration, live result/validation announcements, Escape handling, non-color symbols, and explicit narrow-width overflow disclosure.
- **Verification:** Python Playwright assertions cover all eight required states and primary interaction recovery. Eight desktop/narrow screenshots were captured twice with zero mismatched pixels on Chromium 144. Directly inspected authored, field explorer, no-results, warning/detail, and narrow frames.
- **Runtime packaging:** A small bootstrap inflates one deterministic gzip JSON payload split into Git-friendly fragments. The test harness decodes the same payload before injection, so browser verification covers the exact shipped CSS and JavaScript.

### V1 tradeoffs and risks

- The always-visible compact distribution adds useful context but makes the default report longer than a table-only design.
- Native modal field and filter surfaces preserve table width and focus, but repeated configuration requires reopening surfaces.
- The verification container blocks top-level HTTP, HTTPS, and file navigation. The harness navigates to `about:blank`, injects checked-in documents verbatim, and separately asserts switch hrefs; this is recorded in `tests/visual-report.json`.
- Screenshot baselines are intentionally local and ignored. The committed report records dimensions, SHA-256 hashes, browser version, mismatch counts, and the representative frames inspected.

## Implementation observations

### V1 Quiet Report

- The report-first shell remains the strongest calm baseline. Eight deterministic scenarios pass semantic, interaction, and exact screenshot comparison checks.
- Modal field/filter disclosure preserves table width and focus, but repeated configuration requires reopening surfaces.

### V2 Workbench Rail

- Persistent rails make field and query mechanics continuously legible without weakening validation, recovery, or saved-state behavior.
- A three-column desktop composition remains readable at 1440px. At 760px the rails become bounded stacked work areas and the table retains explicit horizontal overflow.
- The tradeoff is measurable: less default table width and a substantially longer narrow review path. This is intentional, not a responsive collapse.
