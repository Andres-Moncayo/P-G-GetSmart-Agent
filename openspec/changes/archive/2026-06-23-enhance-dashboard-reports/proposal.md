## Why

The GetSmart Dashboard was a static prototype with only 6 hardcoded games, non-functional sidebar
filters, a decorative search bar, and no visibility into games currently running through the pipeline.
Users had no way to filter, search, or understand the real-time state of the system.

This change implements the full interactive layer of the Dashboard as defined in
`openspec/specs/ui_and_login/ui_login_contract.yaml`, making it a production-ready reports browser.

## What Changes

### Game Catalog
- Expands from 6 to **50 games** covering all major genres and platforms.
- Each entry includes title, developer, release year, genre, platforms, status, image, and report
  creation date (`REPORT_DATES`).
- Full `ReportPreview` data for all 50 games (4 Macro-Skill scores, market metrics, summary).
- Data extracted into `frontend/src/data/gameData.ts` and types into `frontend/src/types/game.ts`
  to keep `Dashboard.tsx` focused on rendering logic.

### Functional Filters
- **Genre** — multi-select checkbox, filters main grid in real time.
- **Developer** — multi-select checkbox, filters main grid in real time.
- **Platform** — multi-select checkbox, maps label → platform icon class for matching.
- **Date Created** — single-select radio (Today / Last 7 / 30 / 90 / 365 days), filters by
  `REPORT_DATES` ISO timestamps.
- All filters compose with AND logic and combine with the search term.
- "Clear" button resets all active filters.

### Real-Time Search
- Filters both completed and in-pipeline games simultaneously by title or developer.
- Drives the `useMemo`-computed `filteredReports` and `inPhaseReports` lists.

### In Pipeline Section
- Dedicated section above the completed grid showing all `status: 'processing'` games.
- `InPhaseCard` — horizontal card with thumbnail, title, developer, report date, `Phase X/4` badge,
  segmented phase progress bar (active phase pulses amber), and overall percentage bar.
- Clicking an in-pipeline card opens the same `ReportPreviewModal` as completed cards.
- Also filtered by the search bar.

### Report Dates on Cards
- Every `ReportCard` and `InPhaseCard` shows the report creation date formatted as `Mon DD, YYYY`
  with a calendar icon, sourced from `REPORT_DATES`.

### Custom Checkbox Design
- Native browser checkboxes replaced with custom divs (`sr-only` hidden input + visual overlay).
- Unchecked state: `#222222` background with `#3A3A3A` border (dark gray).
- Checked state: accent (indigo) background with white checkmark icon.
- Date filter uses radio variant with circular indicator.

### Image Assets
- 44 new game header images downloaded from Steam CDN (akamai / cloudflare), Epic Games CDN
  (`cdn2.unrealengine.com`), and Wikipedia CDN.
- `onError` fallback on every card uses `picsum.photos` with seed for a consistent placeholder.

## Impact

- Implements the interactive dashboard layer of `openspec/specs/ui_and_login/ui_login_contract.yaml`.
- No backend changes — purely frontend data and rendering.
- No changes to macro-skill, scraper, or synthesis contracts.
- `Dashboard.tsx` now depends on `gameData.ts` and `types/game.ts`; both files are owned by the
  `ui_and_login` contract.
