## 1. Data Layer

- [x] 1.1 Create `frontend/src/types/game.ts` with `Report`, `MacroSkill`, `ReportPreview`, and `ReportStatus` types.
- [x] 1.2 Create `frontend/src/data/gameData.ts` with `mkPreview` helper for compact ReportPreview creation.
- [x] 1.3 Define all 50 `Report` entries in `REPORTS` array with title, developer, year, genre, status, platforms, time, and image path.
- [x] 1.4 Define all 50 `ReportPreview` entries in `REPORT_PREVIEWS` keyed by id (1–50), each with 4 MacroSkill entries and market data.
- [x] 1.5 Define `GENRE_FILTERS`, `DEV_FILTERS`, `PLATFORM_FILTERS`, `STATUS_FILTERS` for sidebar.
- [x] 1.6 Add `REPORT_DATES` lookup (`Record<number, string>`) mapping report id → ISO 8601 creation timestamp.
- [x] 1.7 Add `DATE_FILTERS` array with 5 preset ranges: Today / Last 7 days / Last 30 days / Last 3 months / Last year.

## 2. Game Images

- [x] 2.1 Download 44 Steam CDN header images for games 7–50 via `shared.akamai.steamstatic.com`.
- [x] 2.2 Verify correct Steam App IDs using `store.steampowered.com/api/storesearch` (found Vampire Survivors = 1794680, not 1794460).
- [x] 2.3 Download `alan-wake-2.jpg` via Wikipedia REST API thumbnail for `Alan_Wake_2`.
- [x] 2.4 Download `zelda-totk.jpg` via Wikipedia REST API thumbnail for `The_Legend_of_Zelda:_Tears_of_the_Kingdom`.
- [x] 2.5 Download `lol.jpg` via Epic Games public content API (`store-content.ak.epicgames.com`) → `cdn2.unrealengine.com` gameplay screenshot.
- [x] 2.6 Download `fortnite.jpg` via Epic Games public content API → `cdn2.unrealengine.com` 2560×1440 keyart.
- [x] 2.7 Validate all images: 48 of 50 from real CDNs; 2 (vampire-survivors, lol legacy) replaced with correct sources.

## 3. Dashboard Component Refactor

- [x] 3.1 Update `Dashboard.tsx` import to use `gameData.ts` and `types/game.ts`.
- [x] 3.2 Replace inline type definitions with imports from `types/game.ts`.
- [x] 3.3 Add `useMemo` import and replace static `REPORTS` reference with memoized `filteredReports`.
- [x] 3.4 Add `dateFilter: number | null` state alongside existing filter states.
- [x] 3.5 Implement `filteredReports` memo: search → genre → developer → platform → date → sort.
- [x] 3.6 Implement `inPhaseReports` memo: filter `status === 'processing'` + optional search.
- [x] 3.7 Extract `platformIcon` map to component scope (not inside memo callback).
- [x] 3.8 Update "Recent" sort to order by `REPORT_DATES[id]` descending (ISO string comparison).

## 4. Custom Checkbox & Radio Components

- [x] 4.1 Replace native `<input type="checkbox">` in `FilterCheckbox` with `sr-only` hidden input + custom visual `div`.
- [x] 4.2 Unchecked style: `bg-[#222222] border-[#3A3A3A]` with hover border lightening to `#525252`.
- [x] 4.3 Checked style: `bg-accent border-accent` with `<i class="fas fa-check text-white text-[8px]">` icon.
- [x] 4.4 Create `DateRadio` component with circular indicator (radio-style, single-select).
- [x] 4.5 Wire `DateRadio` toggle: clicking the selected option deselects it (sets `dateFilter` to `null`).

## 5. In Pipeline Section

- [x] 5.1 Create `InPhaseCard` component with horizontal layout: thumbnail left, info right.
- [x] 5.2 Parse `report.time` string (`Phase X/Y` pattern) to extract current and total phase numbers.
- [x] 5.3 Render segmented phase bar: completed phases solid amber, active phase pulsing, pending phases `bg-elevated`.
- [x] 5.4 Show phase name (`Ingestion / Consolidation / Analysis / Synthesis`) and progress percentage.
- [x] 5.5 Show report creation date with calendar icon in `InPhaseCard`.
- [x] 5.6 Create `InPhaseSection` wrapper: pulse dot, "In Pipeline" label, active count badge, auto-fill grid of `InPhaseCard`.
- [x] 5.7 Render `InPhaseSection` above the completed grid, below the search hero bar.
- [x] 5.8 Connect `InPhaseCard` click to `setShowPreview(id)` — opens `ReportPreviewModal`.

## 6. Report Dates on Cards

- [x] 6.1 Add `fmtDate(iso)` helper: `toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })`.
- [x] 6.2 Add date line to `ReportCard` below developer/year: `<i class="fas fa-calendar-alt"> {fmtDate(REPORT_DATES[id])}`.
- [x] 6.3 Add same date line to `InPhaseCard` below developer name.

## 7. Sidebar Date Filter

- [x] 7.1 Add "Date Created" section at bottom of sidebar using `DateRadio` components.
- [x] 7.2 Remove "Status" filter section from sidebar (processing games now in dedicated section).
- [x] 7.3 Include `dateFilter !== null` in `hasFilters` check so "Clear" button appears when date is active.
- [x] 7.4 `clearFilters()` resets `dateFilter` to `null` alongside other filter states.

## 8. Layout & Counters

- [x] 8.1 Add "Completed Reports" sub-header with green dot and `X of Y` counter above main grid.
- [x] 8.2 Counter shows `filteredReports.length` of total completed count (excludes processing).
- [x] 8.3 Empty state shows when `filteredReports.length === 0` with "Clear all" action.
- [x] 8.4 Verify `flex flex-col h-full` layout holds with new `InPhaseSection` inserted above grid.

## 9. Validation

- [x] 9.1 `npx tsc --noEmit` passes with zero errors.
- [x] 9.2 `npx vite build` completes successfully (84 modules, no warnings on code).
- [x] 9.3 All 4 processing games (Zelda TOTK, Alan Wake 2, Palworld, Final Fantasy XVI) appear in In Pipeline section.
- [x] 9.4 Genre / Developer / Platform / Date filters compose correctly and update card count.
- [x] 9.5 Search filters both completed grid and In Pipeline section simultaneously.
- [x] 9.6 Clicking any card (completed or in-pipeline) opens `ReportPreviewModal`.
- [x] 9.7 Sort modes (Recent / A–Z / Year) apply correctly to completed grid only.
