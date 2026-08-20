# Interactive table variants task context

Updated: 2026-08-19

## Source load status

- Read `docs/ui-prototype-brief.md` in full.
- Read `docs/transcripts/README.md` and every transcript listed there, including the empty fragment.
- Read `PRODUCT.md`, `DESIGN.md`, the existing `index.html`, `styles.css`, and `app.js` implementation.
- Read `.codex/skills/consider-contrast/SKILL.md`.
- Read `.codex/skills/impeccable/SKILL.md` plus `reference/new-work.md`, `reference/craft-floor.md`, and `reference/operate.md`.
- Read the existing `docs/consider-contrast-decisions.md` decision record.

## Constraints

- Preserve the existing root prototype. New work belongs under `/variants` with shared library modules.
- Use plain HTML, CSS, and JavaScript. Do not add a backend or heavy runtime dependency.
- Keep all six concepts on `main` and publish every meaningful increment immediately.
- Maintain a 126-row known-schema purchase-order fixture matching the brief. The authored default is unfiltered; the canonical exploration state returns exactly 24 rows.
- Every variant must expose: authored default, filtered exploration, field explorer open, rich detail open, no results, saved state, data-quality warning, and a narrow-width composition.
- All state must be serializable and stored independently by variant so switching concepts does not erase work.
- Playwright navigation, semantic assertions, screenshots, and pixel comparison are release gates.
- Accessibility is part of the interaction contract: keyboard paths, visible focus, ARIA state, focus trap/restore, non-color status signals, and reduced-motion handling.

## Assumptions

- This runtime cannot access the requested existing local checkout or push through the shell. The repository is available through the authenticated GitHub connector.
- A local reconstruction is used for implementation and browser verification. Connector commits preserve the remote `main` tree and advance it with non-force updates.
- Screenshot binaries remain local under `.artifacts/`. A committed visual report records dimensions, hashes, comparison results, and inspected scenarios.
- Chromium 144 at `/usr/bin/chromium` and Python Playwright are the verification environment.
- The existing root prototype remains unchanged except for optional navigation/documentation links added during finalization.

## Decision checkpoints

### Shared implementation architecture

**Decision:** Choose how six materially different interaction concepts share behavior while retaining state across variant switching.

Scores use 0 for failure and 10 for reliably meeting the named table outcome.

| Approach | Interaction-premise separation | State continuity between concepts | Acceptance-criteria parity | Cross-variant defect containment | Main tradeoff |
| --- | ---: | ---: | ---: | ---: | --- |
| Six unrelated pages and scripts | 10 — each can diverge freely | 2 — state models drift or disappear | 4 — required behavior is reimplemented six times | 8 — a defect may stay local | Maximum visual freedom creates inconsistent table semantics |
| One monolithic page with CSS modes | 4 — layout can change, governing mechanics tend to converge | 10 — one state object is trivial | 9 — every mode inherits features | 3 — a render defect affects all concepts | Easy parity, weak variation quality |
| **Shared state/runtime with six composition modules** | **9 — each module owns placement and disclosure mechanics** | **10 — namespaced state is stable across navigation** | **10 — one tested model supplies all required behavior** | **7 — shared logic defects are broad, composition defects remain local** | Requires explicit extension points rather than ad-hoc markup |

- **Choice:** Shared state/runtime with six composition modules.
- **Why:** It is the only option that strongly satisfies state continuity, acceptance parity, and meaningful composition differences at once.
- **Watch:** Shared render helpers must not force every variant into the same information hierarchy.
- **Next:** Keep data, state transitions, filtering, distributions, persistence, focus management, and test IDs shared. Keep shell topology, disclosure surfaces, density, and primary workflow variant-owned.

### Required-state routing

**Decision:** Make every review state reproducible without turning the prototypes into static screenshots.

| Approach | State reproducibility | Real interaction fidelity | Keyboard discoverability | Saved-state isolation | Main tradeoff |
| --- | ---: | ---: | ---: | ---: | --- |
| Manual interaction only | 3 — reviewers must recreate every state | 10 — all state is organic | 6 — controls can be found, but setup is lengthy | 8 — local state is natural | Weak for deterministic testing and review |
| Static duplicated frames | 10 — every URL is fixed | 2 — frames do not prove recovery paths | 8 — route navigation is clear | 2 — state is not actually persisted | Strong screenshots, weak product behavior |
| **Scenario query plus real state engine** | **10 — `?scenario=` deterministically seeds each state** | **10 — seeded state remains editable and recoverable** | **9 — a labeled scenario selector and URLs expose states** | **10 — each variant stores its own working state** | Scenario seeding must not overwrite user state unless explicitly selected |

- **Choice:** Scenario query plus real state engine.
- **Why:** It supports deterministic screenshots and assertions while keeping every state fully interactive.
- **Watch:** The authored scenario must reset to the brief, while ordinary navigation restores the variant’s last state.
- **Next:** Add a labeled scenario selector, query routes, and variant-scoped local storage.

### Visual verification model

**Decision:** Verify desktop, narrow, switching, recovery, warning, and overlay states without committing a large binary artifact set.

| Approach | Regression sensitivity | Review traceability | Repository footprint | Cross-platform stability | Main tradeoff |
| --- | ---: | ---: | ---: | ---: | --- |
| Screenshots without comparison | 4 — gross failures are visible, drift is unmeasured | 7 — artifacts can be inspected | 10 — images stay local | 9 — no brittle threshold | No blocking visual regression signal |
| Commit every baseline PNG | 10 — precise pixel comparisons | 10 — baseline lives with code | 2 — dozens of binaries grow history | 5 — browser/font differences are noisy | Strongest trace, largest and most brittle repository cost |
| **Local baselines plus committed manifest and diff report** | **9 — pixel differences block the local run** | **9 — hashes, dimensions, mismatch counts, and scenario names are committed** | **9 — binary artifacts remain ignored** | **8 — the fixed Chromium runtime controls variance** | Reviewers need to regenerate images to see pixels |

- **Choice:** Local baselines plus a committed visual report.
- **Why:** It gives blocking screenshot comparison and durable evidence without adding dozens of PNGs to Git history.
- **Watch:** Browser upgrades require intentional baseline regeneration.
- **Next:** Generate per-variant baselines, run a second comparison pass, inspect representative PNGs, and commit `tests/visual-report.json`.

## Variant interaction contracts

### V1 — Quiet Report Mode

- Report-first reading surface. Controls live in compact disclosure dialogs and a quiet summary strip.
- Field selection is a searchable modal; filter construction is a focused popover/dialog.
- Distribution summaries are restrained annotations near the active slice, not a permanent workbench.
- Tradeoff: maximum default clarity, slower repeated field/filter iteration.

### V2 — Workbench Rail Mode

- Persistent left field/filter rail and a dedicated distribution workspace keep configuration visible.
- Field rows expose visibility, ordering, width, quality, and compact distributions in place.
- Tradeoff: fastest exploratory iteration, least calm default and least table width.

### V3 — Chip-First Filter Mode

- Active and draft conditions are the primary command surface. Chips are editable objects, not passive summaries.
- Field discovery opens from an add-field chip and remains secondary to query construction.
- Tradeoff: filtering is highly recoverable, initial field-management discoverability is lower.

### V4 — Distribution-First Mode

- A large type-aware distribution canvas precedes the table and acts as the main filter entry point.
- Numeric raw/normalized comparison, date period bars, categories, and outliers are first-class.
- Tradeoff: distribution literacy is excellent, row scanning begins lower on the page.

### V5 — Inspector & Match-Reasoning Mode

- A persistent reasoning inspector explains the active AND chain and why the selected row matched.
- Search hidden-field evidence, malformed values, and row detail share one contextual panel.
- Tradeoff: explanation and recovery are strongest, table width is constrained.

### V6 — Hybrid Report + Workbench Mode

- Opens as a calm report. An explicit Report/Explore mode switch reveals a bounded workbench without replacing the table.
- Combines compact summary reading with high-control field, filter, and distribution panels.
- Tradeoff: strongest overall balance, slightly more conceptual UI because the mode boundary must be understood.

## Open risks

- Connector and local Git histories are separate. Every remote write must use the latest remote parent and base tree; every local commit must remain clean independently.
- Shared runtime abstractions could make variants too similar. Each variant will be reviewed against its interaction contract, not only styling.
- Width controls can destabilize narrow layouts. The narrow presentation must explicitly name hidden/off-screen fields and use sheets rather than silent removal.
- Numeric normalization can confuse users. Raw and normalized modes require labeled units, plain-language captions, and the raw value in tooltips/accessible text.
- Pixel tests can become noisy after Chromium changes. Browser executable/version is recorded in the visual report.
- The environment has no independent visual-review subagent. Representative screenshots will be opened and inspected directly in addition to automated comparison.
