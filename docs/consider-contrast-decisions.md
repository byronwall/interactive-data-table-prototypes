# Interactive table decision log

This log keeps the options that three parallel workers considered for the prototype. It records selected and rejected approaches so later experiments can revisit them.

Scores use `0` for failure against the named table outcome. A score of `10` means the approach reliably meets that outcome.

## Control architecture

**Decision:** Arrange search, filters, field controls, saved views, and record detail without turning the default view into a control wall.

| Approach | Default-table clarity | Active-slice legibility | Field-control discoverability | Detail context retention | Main tradeoff |
| --- | ---: | ---: | ---: | ---: | --- |
| Permanent workbench rail | 3 — the control wall is always present | 9 — filters stay visible | 10 — all controls are exposed | 5 — rail and detail compete for table width | Discoverability harms the calm default |
| Header-only contextual menus | 9 — the first view stays minimal | 7 — chips show state, but controls are scattered | 6 — hidden fields need a separate discovery path | 8 — the inspector can remain adjacent | Hidden-field discovery is weak |
| Collapsible rail and inspector | 8 — the rail stays hidden initially | 8 — count and chips are visible | 6 — filter activation can become implicit | 7 — state survives, but an overlay can hide the source row | The structure works, but control affordances need care |
| **Bounded hybrid: collapsible rail, explicit field actions, and inspector** | **9 — the command row stays calm** | **9 — chips and a plain-language summary explain the slice** | **9 — labeled Explore and Filter actions expose controls** | **9 — the selected row stays identifiable and narrow layouts use sheets** | Open exploration consumes width, so narrow layouts need sheets |

- **Choice:** Use the bounded hybrid.
- **Why:** It preserves the authored default and makes fields, filters, and current state easy to find.
- **Watch:** The open rail consumes width. Narrow layouts must present the rail and inspector as sheets.
- **Next:** Keep one serializable table-view state for filters, field order, visibility, sort, saved state, and open detail.

## Row rendering strategy

**Decision:** Render about 1,000 rows without confusing the filtered set, visible rows, keyboard model, or detail context.

| Approach | Filtered vs. visible rows | Detail-close row context | Keyboard/table semantics | Sort/filter transitions | DOM-bound rows |
| --- | ---: | ---: | ---: | ---: | ---: |
| **Pagination** | **10 — the footer names the filtered set and page text names visible rows** | **10 — the page and row button remain addressable** | **9 — a native table renders only 30 rows** | **9 — filtering and sorting derive one result set** | **9 — a 30-row page bounds the table** |
| Incremental or load-more | 7 — loaded rows can blur the difference from matching rows | 8 — existing buttons persist, but inserts can shift context | 8 — native semantics hold until the list grows | 8 — append and resort need reconciliation | 4 — the DOM grows toward 1,000 rows |
| Fixed-height virtualization | 5 — it needs explicit set and viewport announcements | 4 — recycled rows can lose focus or detail anchors | 4 — it needs careful row indexes, set size, and focus logic | 7 — window recalculation can preserve results, but focus needs care | 10 — only the viewport renders |
| Pagination with threshold windowing | 10 — pagination remains the count model | 9 — stable IDs and an anchor preserve context | 8 — the native table works, but a virtual fallback adds semantics work | 9 — one filtered and sorted model feeds both renderers | 9 — the page or future window stays bounded |

- **Choice:** Use pagination.
- **Why:** It keeps counts, table semantics, and inspector return paths clear. One thousand rows do not justify virtualization yet.
- **Watch:** Keep the full-data count, filtered count, visible-page count, and page count distinct after every state change.
- **Next:** Keep stable row IDs and focus anchors. Reconsider virtualization only after a larger fixture shows a measured need.

## First implementation strategy

**Decision:** Choose the first bounded renderer and exploration model for a crude vanilla-JavaScript demo.

| Approach | First-view readability | Bounded DOM rows | Context retention during exploration | Long-list access |
| --- | ---: | ---: | ---: | ---: |
| **Pagination, 30 rows per page** | **9 — the initial scan stays controlled** | **10 — the DOM has an exact row bound** | **9 — page context stays stable while controls open** | **8 — page controls reach the full set** |
| Fixed-height virtual scrolling | 8 — the first viewport remains compact | 10 — viewport rendering bounds the DOM | 7 — rail and inspector changes can disturb scroll position | 9 — continuous scrolling exposes the list |
| Incremental load-more | 7 — the initial view is readable, but the list grows | 7 — each action adds DOM rows | 8 — the continuous list preserves nearby context | 8 — repeated loading reaches the full set |

- **Choice:** Use 30-row pagination with a collapsible field rail.
- **Why:** It best combines a readable initial state, bounded rendering, and stable context.
- **Watch:** Adjacent records across a page boundary are not visible until the user navigates.
- **Next:** Keep pagination controls clear and preserve the current page when detail opens and closes.

## Options kept for later experiments

- Try the permanent workbench rail as a deliberate comparison variant when maximum control discovery matters more than a calm default.
- Try header-only contextual menus when visible-column actions dominate and hidden-field discovery has a separate strong entry point.
- Add threshold windowing only after row counts or measured rendering behavior exceed pagination's useful range.
- Try virtual scrolling as its own prototype. It needs explicit accessibility and focus work, not a hidden renderer swap.
- Try load-more when uninterrupted reading matters more than a fixed page model.

## Browser test: core workflow repair packages

**Decision:** Repair the defects found while a clean-room tester attempted the brief's five review tasks.

| Package | Five-task completion | State legibility | Progressive-disclosure fit | Prototype playability | Main tradeoff |
| --- | ---: | ---: | ---: | ---: | --- |
| Minimal contract repairs | 5 — fixes only the most direct blockers | 6 — key counts remain, but state gaps remain | 7 — keeps the existing rail and inspector | 6 — some brief tasks still fail | Amount and inspector repairs do not finish save and state behavior |
| **Workflow-complete repairs** | **10 — targets all five review tasks** | **9 — filters, views, and current state remain clear** | **9 — preserves the calm default and explicit exploration** | **9 — restores the main interactive loop** | Does not create every brief frame or variant |
| Full brief-state infrastructure | 10 — all review tasks get explicit paths | 10 — every required state becomes directly selectable | 8 — permanent test infrastructure adds visible controls | 8 — broad coverage makes the crude demo larger | Expands beyond the initial single-page playground |

- **Choice:** Use workflow-complete repairs with focused state fixes.
- **Why:** It is the smallest package that completes all five review tasks and preserves progressive disclosure.
- **Watch:** The 1,000-row request conflicts with the brief's 126-record fixture.
- **Next:** Fix inspector hit testing, amount bounds, saved views, field-filter focus, and region variety. Keep exact brief frames as an optional next layer.

## Browser test: quality and state repair packages

**Decision:** Improve accessibility, responsive integrity, state fidelity, data-type behavior, and required-state coverage after browser verification.

| Package | Accessibility task completion | Responsive integrity | State fidelity | Data-type fit | Review-state coverage | Main tradeoff |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Interaction patch only | 5 — removes the overlay blocker | 5 — preserves the current scroller | 5 — repairs blocked pagination and controls | 3 — leaves date and attachment gaps | 4 — core tasks work, but explicit states remain absent | Leaves major brief omissions |
| **Brief-complete current shell** | **8 — controls and overlays become reachable** | **8 — narrow layouts keep explicit disclosure** | **9 — filters, views, and saved states stay faithful** | **8 — type-specific gaps are addressed** | **9 — required states and review tasks receive clear paths** | Adds more controls and state logic to the single page |
| New workbench rebuild | 8 — accessibility can start from a new structure | 9 — responsive behavior can be purpose-built | 8 — the state model must be rebuilt | 9 — offers the strongest type controls | 8 — coverage depends on rebuild discipline | Risks losing the calm default concept |

- **Choice from the quality tester:** Use a brief-complete repair of the current shell.
- **Why:** It improves state fidelity and review-state coverage without discarding the useful default table.
- **Watch:** Replacing 1,000 rows with 126 would conflict with the explicit playground request.
- **Next:** Separate hard defects from optional brief expansion before implementation.

## Orchestrator synthesis after browser evidence

**Decision:** Select the repair boundary after combining both browser reports with the original 1,000-row request.

| Package | Five-task completion | Brief-state coverage | 1,000-row playground value | Progressive-disclosure integrity | Data-type fit | Main tradeoff |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Blocker-only patch | 7 — main clicks work, but focus and state gaps can remain | 4 — required states stay implicit | 9 — keeps the playground small | 8 — keeps the current structure | 5 — category and amount controls remain the focus | Fast repair leaves verified workflow gaps |
| **Workflow-complete repair with focused test states** | **10 — all five tasks get working paths** | **8 — key states become reproducible without a new product shell** | **9 — keeps 1,000 deterministic rows and bounded rendering** | **9 — keeps the rail and inspector progressive** | **7 — repairs the tested types and records deeper type controls as follow-up** | Does not implement every high-fidelity brief feature |
| Full brief expansion | 10 — all tasks and supporting paths are explicit | 10 — all frames, variants, and fixture rules are represented | 5 — the 126-row fixture and extra surfaces dilute the requested 1,000-row sandbox | 8 — added routes and variants increase visible structure | 10 — date, exact ID, attachments, resize, and share are included | Becomes a larger comparison product instead of a crude demo |

- **Choice:** Use the workflow-complete repair with focused test states.
- **Why:** It fixes direct browser failures and preserves the requested 1,000-row sandbox.
- **Watch:** The exact 126-record and 24-row brief fixture remains an intentional conflict, not a silent omission.
- **Next:** Repair the overlay, amount input, region generator, saved-view path, and narrow filter behavior. Add small reproducible state presets if they do not crowd the command row.

## Saved-view naming interaction

**Decision:** Replace the unsupported browser prompt with a save-name interaction that works by pointer and keyboard.

| Approach | In-app Browser support | Keyboard completion | Table-context continuity | Saved-state legibility |
| --- | ---: | ---: | ---: | ---: |
| Inline labeled name field | 10 — uses ordinary form controls | 10 — stays in the command flow | 10 — never obscures the table | 8 — save intent competes with nearby controls |
| **Small accessible dialog** | **10 — avoids unsupported prompt APIs** | **9 — clear Save, Cancel, Escape, and focus trap** | **9 — the table stays unchanged behind one transient surface** | **10 — the named checkpoint is explicit** |
| Automatic generated name with rename path | 10 — needs no restricted browser API | 7 — completion is easy, but rename adds a second path | 8 — save is immediate, but naming moves elsewhere | 7 — generated names weaken checkpoint meaning |

- **Choice:** Use a small accessible dialog.
- **Why:** It gives the checkpoint a clear name and removes unsupported prompt, alert, and confirm APIs.
- **Watch:** The dialog needs focus trapping and reliable focus restoration.
- **Next:** Reuse this bounded pattern if local saved views later gain sharing or persistence.
