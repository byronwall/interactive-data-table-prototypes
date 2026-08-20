# Interactive Data Table Prototypes

This repository converts Byron Wall's June 2026 interactive-data-table transcripts into a source-backed product brief.

Start with [the UI prototype brief](docs/ui-prototype-brief.md). It is the handoff document for interface-design tools. Use [the prototyping prompt](docs/prompts/ui-prototyping-prompt.md) when a tool accepts a detailed natural-language request.

The Software Design Sleuth artifacts live in `docs/intent/interactive-data-table-explorer/`. Raw transcript copies live in `docs/transcripts/`. The source archive remains unchanged.

## Scope

The source set covers the early interactive-table series from June 25 through June 29, 2026. It excludes the broader interactive-data-visualization series that began in late July.

## Run the prototype

Open index.html directly in a browser, or serve this folder with any simple local HTTP server. No package install or build step is required.

Use the search, sort, filter, and pagination controls above the table. Select a row to open its detail inspector. Use Explore fields to show, hide, move, and filter fields. Save as new stores a view in the current browser session.

The Demo state selector loads repeatable review states and stores the selected state in the URL hash.

## Intentional follow-ups

The prototype does not yet include the exact 126/24 fixture variant, date-period filters, an exact Source ID filter, an attachment item view, column resize, share URLs, autosaving or save-failed states, supplier hover cards, or two additional interaction variants.

## Review order

1. `docs/ui-prototype-brief.md`
2. `docs/intent/interactive-data-table-explorer/intent-brief.md`
3. `docs/intent/interactive-data-table-explorer/shape-brief.md`
4. `docs/intent/interactive-data-table-explorer/initiative-map.json`
5. `docs/prompts/ui-prototyping-prompt.md`
