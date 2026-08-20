# UI prototype brief: adaptive interactive data table

## Purpose

Design a high-fidelity interface for exploring a known-schema operations data set. The interface must begin as a polished, useful table. It must reveal advanced controls only when the user asks for them or when the data makes them relevant.

This brief is a comparison fixture for several UI prototyping tools. Preserve the required behavior and test states. Vary the visual language, layout, density, and motion where useful. Do not turn the concept into a spreadsheet or a dashboard builder.

## Product premise

Most tables should not expose every possible control. A well-designed table uses what it knows about the data, the available width, and the likely task. It chooses useful fields and formats. It gives users clear search, sort, and reset paths. It then reveals field discovery, type-aware filtering, view management, and rich detail in layers.

The interface should feel calm in its default state and powerful in its explored state. Added capability must not destroy context.

## Primary user and task

The primary user is an operations analyst or manager. They understand the business records but are not a database expert. They need to answer questions such as:

- Which open orders have high value and delivery risk?
- Why did this row match my search?
- What records belong to a specific region or status?
- Which fields are hidden, empty, unique, or poorly formatted?
- What did I change from the saved view?
- Can I share or restore this exact slice?

## Example data fixture

Use 126 purchase-order records. Show 24 rows after the default filter. Include these fields:

| Field | Type | Default display | Important behavior |
|---|---|---|---|
| Order | identifier | Visible, pinned first | Natural sort: PO-9 before PO-10. Exact search. |
| Supplier | related entity | Visible | Name plus small mark. Hover card and stable detail path. |
| Description | long text | Visible, two-line clamp | Expand full content without changing filters. |
| Status | category | Visible | Four values: On track, At risk, Blocked, Complete. Direct toggles. |
| Amount | currency | Visible, right aligned | $1,250–$184,500. Range inputs plus compact histogram. |
| Needed by | date | Visible | Natural date ranges and explicit start/end. |
| Region | category | Hidden by default | Five short values. Show visibility and distribution in field rail. |
| Buyer | related entity | Hidden by default | Avatar, name, team detail. |
| Updated | timestamp | Hidden by default | Relative display with exact timestamp in detail. |
| Notes | rich text | Hidden by default | Some long values and some nulls. |
| Attachments | list/media | Hidden by default | Zero to four files. Summary plus modal or panel. |
| Source ID | unique identifier | Hidden by default | 126 unique values. Exact search only. |

Include deliberate edge cases: long supplier names, one malformed date, null notes, two similar identifiers, a very large amount, and a search that matches a hidden field.

## Information hierarchy

### 1. Page context

Show a clear title, one-sentence purpose, current view name, and total or filtered result count. The user should understand the table before touching it.

### 2. Primary command row

Keep this row compact. It contains:

- global search;
- one visible primary sort control with direction;
- active view selector;
- Explore fields and filters control;
- save or modified-state control;
- overflow menu for secondary actions.

Do not put every field filter in this row.

### 3. Active-state summary

When the table differs from its default state, show removable filter chips and a plain-language result statement. Example: `24 of 126 orders · Status is At risk or Blocked · Amount is $25k–$100k`. Include one clear Reset action.

The summary must distinguish the complete data set, the current working set, and the visible rows. Do not make pagination or virtualization look like filtering.

### 4. Table

The default table shows six fields. Use a compact but readable row height. Keep headers visible during vertical scroll. Provide a visible sort indicator and an accessible menu on each header.

Use data-appropriate alignment and formats. Numbers align right. Text aligns left. Dates stay legible at narrow widths. Do not allow one long string to set the width for every row.

### 5. Exploration layer

The Explore action opens a collapsible field rail or equivalent surface. It must preserve the table in view on desktop. Each field entry can show:

- label and type icon;
- visible or hidden state;
- sample or compact preview;
- null, unique, or cardinality signal;
- compact distribution when useful;
- filter status;
- show, hide, reorder, or configure action.

Filtered fields should move into a prominent section or receive strong emphasis. The user must be able to close the exploration layer and keep the configured table.

### 6. Detail layer

Use progressively stronger surfaces:

- tooltip only for short explanatory labels;
- hover card for a related supplier or buyer, with a keyboard and click path;
- small popover for a focused filter or format control;
- inline row expansion or side inspector for full record detail;
- modal only for media, attachments, or content that needs isolation.

The user should always know which row or field produced the detail. Closing the detail must restore focus.

## Interaction requirements

### Search

- Update results as the user types.
- Use exact substring matching by default.
- Highlight the matching text without changing its layout.
- If a hidden field matches, disclose that field or state why the row matched.
- Do not mix fuzzy results into an exact count without a clear distinction.
- Reset must restore the authored default.

### Sort

- Support ascending, descending, and default states.
- Use natural order for identifiers containing numbers.
- Offer a labeled sort control in addition to header clicks.
- Do not include multi-column sort in the main prototype.

### Field choice and layout

- Let users show and hide fields.
- Make hidden fields discoverable.
- Let users reorder visible fields.
- Show a direct resize affordance where appropriate.
- Set sensible minimum and maximum widths.
- Auto-size must ignore extreme outliers or cap at a useful percentile.
- If width is insufficient, identify hidden or off-screen fields. Do not remove them silently.

### Filters

- Combine filters with AND by default.
- Categories use visible toggles when cardinality is low.
- Numeric data uses editable bounds and a small distribution.
- Dates offer natural periods such as This month, Last 30 days, and Previous quarter, plus explicit start and end.
- Text filters state whether they use exact, substring, or fuzzy matching.
- Unique identifiers use exact matching and state that values are unique.
- Empty results retain the active query and show how to recover.

### Rich cells

- Clamp long descriptions to two lines.
- Reveal full content near its row through a stable click path.
- Summarize lists, such as `3 attachments`, and reveal individual items on demand.
- Use sparklines only when a small trend materially improves scanning.
- Do not make every number clickable.

### Views and persistence

- Treat the complete table configuration as serializable state.
- Show named saved views and one authored default.
- Distinguish Saved, Modified, Autosaving, and Save failed.
- Do not overwrite a named checkpoint silently.
- A share action may copy a URL for the current state.
- Keep the number of authored default views small. User-created views may be longer.

## Required prototype states

Create each state as a distinct frame or route. Keep navigation between states clear.

1. **Authored default:** Six visible fields, 126 records, no active filters, calm command row.
2. **Filtered exploration:** Status is At risk or Blocked. Amount is $25k–$100k. Show 24 of 126 records and clear chips.
3. **Field rail open:** Region and Buyer are hidden. Amount shows its distribution. Source ID shows 126 unique values. Notes shows a high null rate.
4. **Rich detail open:** One supplier or order opens in a side inspector or inline expansion. Preserve the table's scroll and filter state.
5. **No results and recovery:** A valid query returns zero rows. Keep the query visible and offer targeted reset actions.
6. **Narrow width:** Show the same filtered state near 768 pixels. Make hidden or moved information explicit.
7. **Save-state variation:** Show a named view after a change, with a visible Modified state and Save as new option.
8. **Data-quality warning:** Show the malformed date or unexpected value without breaking the table.

## Five review tasks

The prototype should let a reviewer attempt these tasks without instructions:

1. Find blocked orders between $25,000 and $100,000.
2. Explain why one row matched a search.
3. Add Region, remove Updated, and move Amount beside Order.
4. Open the full description and then return to the same table state.
5. Save the changed layout as a new view, then restore the authored default.

## Responsive behavior

Desktop should retain the table while the field rail or detail inspector opens. At narrower widths, those surfaces can become sheets. Preserve row identity and state.

For mobile, prefer a clear record-list treatment or explicit horizontal table mode. Do not pretend a twelve-field grid fits. Keep the primary identity and status visible. Put secondary values behind an obvious row-detail action. State how many fields are not shown.

## Accessibility and input

- Provide keyboard paths for every hover or context-menu action.
- Use visible focus and restore focus after overlays close.
- Announce result-count changes without excessive chatter.
- Label sort direction, filter state, and disclosure controls.
- Use sufficient contrast without relying on color alone.
- Keep click targets usable at narrow widths.
- Respect reduced-motion preferences.

## Visual direction

Aim for a calm analytical product, not a generic admin template. Use a strong typographic hierarchy, restrained borders, and deliberate density. Make state changes visible through more than color. Avoid a dense toolbar of small unlabeled icons.

The tool may explore these axes:

- editorial report versus technical workbench;
- compact versus comfortable row density;
- left field rail versus top command surface;
- side inspector versus inline row expansion;
- subtle monochrome styling versus restrained semantic color.

## Variation request

Produce one recommended concept and two meaningful variants. Each variant must change a governing interaction premise, not only colors.

- One should make the table feel like a polished report that reveals controls quietly.
- One should make field exploration more visible and workbench-like.
- The third may propose a stronger hybrid.

For each concept, state:

- what becomes easier;
- what becomes less direct;
- which progressive-disclosure surfaces it uses;
- what it omits from this brief;
- what it invented beyond this brief.

## Comparison scorecard

Review outputs on a 0–5 scale:

| Dimension | What good looks like |
|---|---|
| Default clarity | The table is immediately useful and calm. |
| State legibility | Users can explain the current slice and restore default. |
| Progressive disclosure | Power appears near the need without losing context. |
| Data-type fit | Each field receives a suitable control and format. |
| Density and scanability | Many records remain readable without hiding meaning. |
| Responsive integrity | Narrow width changes the layout without silent data loss. |
| Accessibility | Required actions do not depend on hover, color, or precision pointing. |
| Variation quality | Alternatives differ in interaction premise and explain tradeoffs. |

## Non-goals

- No spreadsheet formulas, cell editing, pivoting, grouping, or multi-column sort.
- No data upload or schema-cleaning workflow in the first prototype.
- No backend, authentication, permissions, or real collaboration.
- No full dashboard or chart authoring environment.
- No production-ready design system requirement.
