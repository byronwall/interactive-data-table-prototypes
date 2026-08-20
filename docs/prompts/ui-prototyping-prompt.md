# Prompt for UI prototyping tools

Design a high-fidelity, responsive interactive data-table prototype from the attached product brief.

Read `docs/ui-prototype-brief.md` as the source of truth. Do not reduce it to a generic admin table. The central idea is an adaptive interface that starts as a polished, useful report and reveals advanced exploration controls only when needed.

Use the specified 126-row purchase-order fixture and its named fields. Build or render these required states:

1. authored default;
2. filtered exploration;
3. field rail open;
4. rich row or supplier detail open;
5. no results with recovery;
6. narrow-width filtered state;
7. named view in a modified state;
8. malformed-value or data-quality warning.

The design must support the five review tasks in the brief. Keep active filters and result counts unmistakable. Use type-aware controls for category, numeric, date, text, and unique-identifier fields. Keep full detail reachable for truncated or rich cells. Preserve table state when panels open or close. Provide keyboard and click paths for anything shown on hover.

Produce one recommended concept and two meaningful variants:

- a report-like concept with quiet progressive disclosure;
- a more visible exploration workbench;
- a hybrid that combines the strongest mechanisms.

The variants must differ in layout or interaction premise, not only color or typography. For each concept, describe what becomes easier, what becomes less direct, which disclosure surfaces you used, and what you omitted or invented.

Visual direction: calm analytical product, strong typography, restrained borders, deliberate density, visible state changes, and no wall of small icon buttons. Avoid a generic dashboard shell. Do not add spreadsheet formulas, cell editing, pivoting, multi-column sorting, a data-upload flow, or a chart builder.

If you generate code, use fixed local data and serializable local view state. Do not add a backend. Make each required state directly reachable for review. Include a short README with run instructions and an assumption log.

Before finalizing, test your result against the comparison scorecard in the brief. Then identify the single interaction decision that most influenced your design.
