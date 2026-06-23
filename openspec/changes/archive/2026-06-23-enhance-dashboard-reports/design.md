## Context

The Dashboard is the primary interface users interact with after login. It must surface:
1. Completed reports as a browsable, filterable grid.
2. Active pipeline jobs as a live status panel.
3. Quick access to report previews without leaving the page.

All rendering is client-side. The backend is not involved in this change — data is static mock data
structured to match the shape the real API will eventually return.

## Goals / Non-Goals

**Goals:**
- Replace the 6-game static prototype with a 50-game interactive catalog.
- Make every sidebar filter and the search bar functionally drive the grid.
- Surface pipeline-in-progress games in a visually distinct section with phase-level detail.
- Show report creation timestamps on every card.
- Keep `Dashboard.tsx` clean by externalizing data to `gameData.ts`.

**Non-Goals:**
- Do not connect filters to a real backend API (mock data only for now).
- Do not implement pagination (50 games fits in a single scrollable grid).
- Do not add user-created report storage — all data is seeded in `gameData.ts`.

## Decisions

### Separate `gameData.ts` + `types/game.ts`
Keeping 50 game entries and 50 full `ReportPreview` objects inside `Dashboard.tsx` would make the
file unmanageable. Externalizing to `gameData.ts` keeps the component focused on rendering logic.
`types/game.ts` is a separate file so types can be imported by both the data layer and the UI layer
without circular dependencies.

### `useMemo` for filter composition
All filter, search, sort, and date logic runs inside `useMemo` hooks. This avoids re-running O(50)
filter passes on every render unrelated to filter state, and keeps the derived state declarative.

### In Pipeline as a separate section, not a filter state
Processing games are architecturally different from completed reports: they are live jobs, not
archived analyses. Showing them in a dedicated `InPhaseSection` above the grid makes this distinction
visually clear and avoids mixing pipeline status into the filter sidebar.

### `REPORT_DATES` as a separate lookup object (not a field on `Report`)
Adding `createdAt` as a field on every `Report` entry would require modifying 50 object literals.
A separate `Record<number, string>` keyed by ID achieves the same result with a single append to
`gameData.ts` and zero changes to the `Report` type or existing entries.

### Date filter as single-select radio, not multi-select checkbox
Date ranges are inherently exclusive (you cannot be in "Last 7 days" AND "Last 30 days"
simultaneously in a meaningful way). A radio pattern prevents logically contradictory selections.
Clicking the currently selected option deselects it (toggle back to "All time").

### Image sourcing strategy
- **Steam CDN** (`shared.akamai.steamstatic.com/store_item_assets/steam/apps/{id}/header.jpg`):
  used for all games available on Steam. Correct App ID lookup via Steam Store search API.
- **Epic Games CDN** (`cdn2.unrealengine.com`): used for Epic-exclusive games (Fortnite, LoL)
  via the public `store-content.ak.epicgames.com` content API.
- **Wikipedia CDN** (`upload.wikimedia.org`): used for platform-exclusive titles not on Steam/Epic
  (Zelda TOTK, Alan Wake 2). Accessed via the Wikipedia REST summary API.
- **`onError` fallback**: `picsum.photos/seed/{id}` ensures every card renders something even if
  the CDN image is unavailable.

### Custom checkbox over native `<input type="checkbox">`
Native checkboxes render with system-default white backgrounds on dark themes. A hidden `sr-only`
checkbox paired with a custom visual `div` gives full design control while preserving keyboard
accessibility and form semantics.

## Risks / Trade-offs

- **Static mock data will diverge from real API**: Acceptable. When the real API is connected,
  `gameData.ts` will be replaced with API calls; the component structure stays the same.
- **50 `ReportPreview` objects are verbose**: The `mkPreview` helper reduces per-entry boilerplate
  to a tuple-based call. Future entries can follow the same pattern.
- **Wikipedia CDN images may change URLs**: Low risk for major titles. The `onError` fallback
  handles breakage gracefully.
