---
title: "Interactive data table explorer — shape brief"
slug: "interactive-data-table-explorer"
phase: shape
status: current
last_updated: "2026-08-17"
---

# Interactive data table explorer — shape brief

## Recommendation

Prototype one responsive exploration screen with three explicit capability levels: a polished default table, an opened exploration layer, and a focused detail layer. Do not ask each tool to design a complete spreadsheet or data platform. Give every tool the same known-schema fixture and the same required states. Let the visual system vary, but hold the information hierarchy and interaction contract constant. This creates a useful comparison of how tools handle progressive disclosure instead of a comparison of unrelated product concepts.

## Problem and appetite

- **Problem:** Common tables either expose too little control or surround simple data with permanent complexity.
- **Outcome:** Users can begin with a readable answer and reach advanced exploration without losing context.
- **Appetite:** A high-fidelity prototype brief and one representative desktop flow, with responsive guidance and key states.
- **Not in this shape:** Data upload, ETL, pivoting, formulas, collaboration, production persistence, or a full visualization builder.

## Core shape

The default screen presents a useful title, result count, compact global search, primary sort, view selector, save status, and a table with six carefully chosen columns. A small summary above the table states the current slice. Active filters appear as removable chips with one clear reset action.

An Explore control opens a collapsible field rail. It lists available fields with type, visibility, sample values, null or unique signals, and small distributions. Users can show, hide, and reorder fields. A field action opens a type-aware filter popover. Numeric values use an editable inclusive range and compact histogram. Categories use direct toggles. Dates use natural ranges plus explicit start and end values. Text uses exact substring matching by default.

Cells stay compact. Long text is clamped and expands into a nearby preview or side inspector. Related entities open a hover card, with click access to a stable detail panel. Images or charts can open a modal. The detail layer must not change table state unless the user takes an explicit action.

View configuration lives in one serializable state object. The prototype can keep it local. It must still show clean, modified, autosaved, and named-checkpoint states.

## Current fit

- **Reuse:** The transcript evidence and a fixed synthetic operations data set.
- **Add:** One comparison fixture, a state matrix, and tool-neutral interaction requirements.
- **Avoid or replace:** No framework choice, backend, upload flow, or live service is needed for the first proof.

## How to make this go better

- **Hold the fixture constant.** Give every tool identical fields, rows, tasks, and states. This makes output differences meaningful.
- **Require state variants, not only a hero screen.** Ask for default, filtered, field-rail, detail, empty, and narrow-width states.
- **Separate required behavior from visual freedom.** Fix interaction semantics. Invite variation in layout, density, motion, and style.
- **Test the smallest useful control set first.** Delay arbitrary schemas and spreadsheet behavior until the known-schema flow feels clear.
- **Capture tool assumptions.** Require each tool to list omissions, invented behavior, and two alternate concepts.

## First proof

- **Question:** Can a user understand the current data slice and reach deeper controls without confronting a permanent settings panel?
- **Proof:** Six linked prototype states for one operations table.
- **Observe:** Control discovery, filter clarity, context retention, density, and return-to-default behavior.
- **Pass / fail:** A reviewer can complete five tasks without explanation and can always state what data is shown.
- **Deliberately excludes:** Real persistence, user data, server filtering, and editable cells.

## Rabbit holes and no-gos

- Do not let charts become a separate dashboard product.
- Do not make hover the only path to required information.
- Do not use hidden right-click actions as the sole control path.
- Do not solve responsive width by silently removing columns.
- Do not add multi-column sort, formulas, grouping, or pivot controls.
- Do not let auto-save overwrite a named view without a visible modified state.

## Serious alternative

A permanent spreadsheet-like field and filter panel would make every option discoverable. It would also erase the central product premise: most users should start with an authored view and reveal complexity only when needed. Keep it only as a comparison variant.

## Plan handoff

First prove the interaction hierarchy with fixed JSON and local state. Add arbitrary-schema detection only after the prototype comparison identifies a clear disclosure model.
