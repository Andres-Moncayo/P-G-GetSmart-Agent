# UI & Login — Functional Specification

> **Artifact:** `ui_login_contract.yaml`
> **Phase:** Phase 0 (Pre-pipeline) + Dashboard (Post-login)
> **Status:** Active
> **Last Updated:** 2026-06-23
> **Version:** 2.0.0

---

## 1. Overview

This document describes the authentication, navigation, user profile, and dashboard systems for the
GetSmart frontend. It covers the SSO login flow, session management, topbar navigation, profile
modal, and the full **Dashboard / Reports Catalog** including the In Pipeline section, functional
filters, real-time search, and report preview modal.

The UI follows the **Globant Enterprise Dark Mode — Game Library Edition** design system with an
**indigo accent palette** (`#6366F1`) and dark surface tokens.

---

## 2. Login Flow

### 2.1 Entry Point

Users land on a centered login screen with:

- **Background:** Dark base (`#0A0A0A`) with a subtle radial gradient (`rgba(99,102,241,0.08)`) and
  a dot grid pattern (`40px` spacing, `#2A2A2A`)
- **Logo:** `64x64px` rounded-2xl gradient card (indigo → violet) with gamepad icon
- **Brand:** "Get**Smart**" with "Smart" in accent indigo (`#6366F1`)
- **Subtitle:** "Game Intelligence Library"

### 2.2 SSO Providers

Three OAuth2 providers are supported, rendered as full-width buttons with provider icons:

| Provider | Icon | Color | Endpoint |
|----------|------|-------|----------|
| Google | `fab fa-google` | `#4285F4` | `accounts.google.com` |
| Microsoft | `fab fa-microsoft` | `#00A4EF` | `login.microsoftonline.com` |
| Okta | `fas fa-shield-alt` | `#007DC1` | `${OKTA_DOMAIN}` |

Each button:
- Background: `surface` (`#161616`)
- Border: `border` (`#2A2A2A`)
- Hover: border transitions to `border-hover` (`#3A3A3A`)
- Icon: `20px` FontAwesome
- Text: "Sign in with {Provider}", font-medium, text-sm

### 2.3 Demo Account

A primary CTA button below the divider:
- Text: "Sign in with demo account"
- Style: Full-width, accent indigo background (`#6366F1`)
- Shadow: `shadow-accent/25`
- Hover: Darkens to `#4F46E5`, shadow intensifies
- Generates a time-limited JWT (24h TTL) with `role: viewer`

### 2.4 Session Lifecycle

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Login     │────▶│   Session   │────▶│   Refresh   │
│   (OAuth)   │     │   (1h TTL)  │     │   (7d TTL)  │
└─────────────┘     └─────────────┘     └─────────────┘
                           │                   │
                           ▼                   ▼
                    ┌─────────────┐     ┌─────────────┐
                    │  Idle 30m   │     │  Absolute   │
                    │  timeout    │     │  8h timeout │
                    └─────────────┘     └─────────────┘
```

**Cookies:**
- `access_token`: httpOnly, secure, SameSite=strict, 1h
- `refresh_token`: httpOnly, secure, SameSite=strict, 7d, path `/api/v1/auth/refresh`
- `csrf_token`: Required for state-changing requests

---

## 3. Topbar Navigation

### 3.1 Structure

Sticky topbar (`64px` height) with glassmorphism (`backdrop-blur: 20px`):

```
┌──────────────────────────────────────────────────────────────────┐
│  [▪] GetSmart    Reports  Pipeline  Templates  Docs   [][][] │
└──────────────────────────────────────────────────────────────────┘
```

### 3.2 Navigation Items

| Item | Path | Active Style | Inactive Style |
|------|------|-------------|----------------|
| Reports | `/reports` | `bg-elevated text-primary` | `text-muted hover:text-primary hover:bg-elevated` |
| Pipeline | `/pipeline` | — | — |
| Templates | `/templates` | — | — |
| Docs | `/docs` | — | — |

Active state uses `bg-elevated` (`#1C1C1C`) background with `text-primary` (`#F5F5F5`).

### 3.3 Right Section

- **Search icon:** `36x36px`, surface + border, opens global search
- **Notifications:** Bell icon with animated dot pulse (`#6366F1`, `2s` infinite)
- **Profile trigger:** Avatar (`28x28px`, gradient circle with initials) + name + chevron down

---

## 4. Profile Modal

Triggered by clicking the profile trigger. Appears as a dropdown at `top: 64px`, `right: 24px`.

### 4.1 Layout

```
┌─────────────────────────────┐
│  [] Alejandro L.          │
│      alejandro.l@globant.com │
│  ┌─────────────────────────┐│
│  │ Senior AI Engineer ·    ││
│  │ Enterprise              ││
│  └─────────────────────────┘│
├─────────────────────────────┤
│  ✏️  Edit profile            │
│  ️  Security & SSO          │
│  ⚙️  Preferences             │
│    API Keys                │
├─────────────────────────────┤
│  ❓  Help & Support          │
│    Sign out (danger red)   │
└─────────────────────────────┘
```

### 4.2 Menu Items

- `px-5 py-2.5`, text-left
- Icon: `text-muted`, `16px`, fixed width
- Label: `text-secondary`, hover → `text-primary`, hover bg → `bg-elevated`
- "Sign out": `text-danger`, hover → `bg-danger/10`

---

## 5. Dashboard — Layout

After login, users land on the Dashboard. It uses a two-column layout:

```
┌──────────────────────────────────────────────────────────────────┐
│  [Search bar ......................] [Sort: Recent ▼] [New +]      │
├────────────┬─────────────────────────────────────────────────────┤
│  Sidebar   │  IN PIPELINE  (pulsing amber section)               │
│  256px     │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│            │  │  Game A  │  │  Game B  │  │  Game C  │          │
│  Genre     │  └──────────┘  └──────────┘  └──────────┘          │
│  Developer │                                                      │
│  Platform  │  COMPLETED REPORTS  ● 46 of 46                      │
│  Date      │  ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐        │
│  Created   │  │    │ │    │ │    │ │    │ │    │ │    │        │
│            │  └────┘ └────┘ └────┘ └────┘ └────┘ └────┘        │
└────────────┴─────────────────────────────────────────────────────┘
```

---

## 6. Dashboard — In Pipeline Section

Games with `status: 'processing'` appear in a dedicated section **above** the completed grid.

### 6.1 Section Header

- Pulsing amber dot (`warning` color, `pulse_dot` animation)
- Label: "In Pipeline" in `text-warning`
- Count badge showing number of active jobs

### 6.2 InPhaseCard Layout (horizontal)

```
┌──────────────────────────────────────────────────────┐
│ [thumbnail]  Title of Game                           │
│  112×63px    Developer Name                          │
│               Jun 23, 2026                         │
│              [Phase 2/4]  Consolidation              │
│              ■■□□  (segmented bar)  45%              │
│              ▓▓▓▓▓▓░░░░ (thin progress)              │
└──────────────────────────────────────────────────────┘
```

- Phase badge: `bg-warning/20 text-warning text-xs font-medium`
- Segmented bar: 4 segments. Completed → `bg-warning`, Active → `bg-warning animate-pulse`,
  Pending → `bg-elevated`
- Phase names: `['Ingestion', 'Consolidation', 'Analysis', 'Synthesis']`
- Clicking the card opens the `ReportPreviewModal`

---

## 7. Dashboard — Completed Reports Grid

### 7.1 Section Header

- Green dot (`success` color)
- Label: "Completed Reports"
- Counter: "**N** of **M**" (filtered count / total completed)

### 7.2 ReportCard Layout

```
┌──────────────────────────────┐
│  [image 16:9]                │
│  ──────────────────────────  │
│  [Action RPG] ●              │
│  Elden Ring                  │
│  FromSoftware · 2022         │
│   Jun 10, 2026             │
│  ️                      │
└──────────────────────────────┘
```

- Genre badge: `bg-accent/20 text-accent-light text-xs rounded-full px-2 py-0.5`
- Success dot: `bg-success` `w-2 h-2 rounded-full`
- Report date: `fas fa-calendar-alt text-disabled` + `fmtDate(REPORT_DATES[id])`
- Platform icons: `fab fa-windows`, `fab fa-playstation`, `fab fa-xbox`, `fas fa-gamepad`
- Image `onError` fallback: `picsum.photos/seed/{id}/400/225`
- Clicking opens `ReportPreviewModal`

### 7.3 Empty State

When no reports match the active filters:
- Icon: `fas fa-search text-muted text-4xl`
- Text: "No reports match your filters"
- CTA: "Clear all" resets every filter

---

## 8. Dashboard — Filters & Search

### 8.1 Search Bar

- Real-time, zero-debounce
- Scope: `title` and `developer` fields
- Affects both the completed grid and the In Pipeline section simultaneously

### 8.2 Sidebar Filters

All filter sections use `FilterCheckbox` — a custom checkbox component:

| State | Background | Border | Icon |
|-------|-----------|--------|------|
| Unchecked | `#222222` | `#3A3A3A` (hover: `#525252`) | — |
| Checked | `bg-accent` | `bg-accent` | `fas fa-check text-white 8px` |

Implementation: hidden `sr-only` `<input type="checkbox">` + custom `div` overlay.

**Sections:**

| Section | Type | Behavior |
|---------|------|----------|
| Genre | Multi-select checkbox | AND with other genres (OR within genre set) |
| Developer | Multi-select checkbox | Same |
| Platform | Multi-select checkbox | Matches via `platformIcon` map |
| Date Created | Single-select radio | Lookback window against `REPORT_DATES[id]` |

### 8.3 Date Created Filter (DateRadio)

Radio variant with circular indicator (rounded-full). Clicking the selected option deselects it
(toggles back to "All Time").

| Option | Lookback |
|--------|---------|
| Today | 1 day |
| Last 7 days | 7 days |
| Last 30 days | 30 days |
| Last 3 months | 90 days |
| Last year | 365 days |

### 8.4 Filter Composition

- All active filters compose with **AND** logic.
- Search term combines with sidebar filters.
- "Clear" button appears when `hasFilters === true` (any checkbox or date radio active).
- `clearFilters()` resets `genreFilters`, `devFilters`, `platformFilters`, `dateFilter` to empty/null.

### 8.5 Sort Modes

| Key | Label | Sort Field | Direction |
|-----|-------|-----------|-----------|
| `recent` | Most Recent | `REPORT_DATES[id]` ISO string | Descending |
| `alpha` | A–Z | `title` | Ascending |
| `year` | Release Year | `year` | Descending |

Sorting applies only to the completed grid, not the In Pipeline section.

---

## 9. Data Types (frontend/src/types/game.ts)

```typescript
export type ReportStatus = 'completed' | 'processing' | 'queued';

export interface Report {
  id: number;
  title: string;
  developer: string;
  year: number;
  genre: string;
  status: ReportStatus;
  platforms: string[];
  time: string;       // "Phase X/4" for processing; "2h ago" for completed
  image: string;      // path relative to /public
  progress?: number;  // 0–100, only when status=processing
}

export interface MacroSkill {
  name: string;       // "Diseño & Arte" | "UX" | "Tecnología & Sistemas" | "Estrategia & Mercado"
  icon: string;       // FontAwesome class
  score: number;      // 0–100
  color: string;      // Tailwind bg class
  textColor: string;  // Tailwind text class
  summary: string;
  strengths: string[];
  weaknesses: string[];
}

export interface ReportPreview {
  overallScore: number;   // 0–100
  tag: string;            // "Outstanding" | "Very Good" | etc.
  summary: string;
  macroSkills: MacroSkill[];  // exactly 4
  market: Record<string, string>;
}
```

**Supporting data objects (frontend/src/data/gameData.ts):**

```typescript
// 50 game entries
const REPORTS: Report[]

// Full preview per report, keyed by id
const REPORT_PREVIEWS: Record<number, ReportPreview>

// Report creation timestamps, keyed by id (ISO 8601)
const REPORT_DATES: Record<number, string>

// Sidebar filter metadata
const GENRE_FILTERS:    { label: string; count: number }[]
const DEV_FILTERS:      { label: string; count: number }[]
const PLATFORM_FILTERS: { label: string; count: number }[]

// Date lookback presets
const DATE_FILTERS: { label: string; days: number }[]
```

---

## 10. State Management

### 10.1 Auth Store (Zustand — persisted)

```typescript
interface AuthState {
  user: UserProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  login: (provider: string) => void;
  logout: () => void;
  setUser: (user: UserProfile) => void;
  clearError: () => void;
}
```

### 10.2 UI Store (Zustand — ephemeral)

```typescript
interface UIState {
  profileModalOpen: boolean;
  activeNavItem: string;

  toggleProfileModal: () => void;
  setActiveNavItem: (item: string) => void;
}
```

### 10.3 Dashboard State (React local state + useMemo)

```typescript
// State
const [search, setSearch] = useState('');
const [sortKey, setSortKey] = useState<'recent' | 'alpha' | 'year'>('recent');
const [genreFilters, setGenreFilters] = useState<Set<string>>(new Set());
const [devFilters, setDevFilters] = useState<Set<string>>(new Set());
const [platformFilters, setPlatformFilters] = useState<Set<string>>(new Set());
const [dateFilter, setDateFilter] = useState<number | null>(null); // days lookback
const [showPreview, setShowPreview] = useState<number | null>(null);

// Derived (useMemo)
const filteredReports = useMemo(...)  // completed only, search+filter+sort applied
const inPhaseReports  = useMemo(...)  // processing only, search applied
const hasFilters      = useMemo(...)  // true if any dimension is active
```

---

## 11. API Endpoints Summary

### Authentication

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/api/v1/auth/login/{provider}` | Initiate SSO | None |
| GET | `/api/v1/auth/callback/{provider}` | Handle callback | None |
| POST | `/api/v1/auth/logout` | Terminate session | Cookie |
| POST | `/api/v1/auth/refresh` | Refresh token | Cookie |

### User Profile

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/v1/me` | Get profile | Cookie |
| PATCH | `/api/v1/me` | Update profile | Cookie |
| GET | `/api/v1/me/api-keys` | List API keys | Cookie |
| POST | `/api/v1/me/api-keys` | Generate key | Cookie |
| DELETE | `/api/v1/me/api-keys/{id}` | Revoke key | Cookie |

### Reports / Dashboard

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/v1/reports` | List all reports (supports `status`, `genre`, `developer`, `platform`, `since`, `sort` query params) | Cookie |
| GET | `/api/v1/reports/{id}` | Get full `ReportPreview` for one game | Cookie |

> **Note:** Currently implemented with static mock data in `gameData.ts`. When the backend
> `/api/v1/reports` endpoint is ready, replace the import in `Dashboard.tsx` with API calls.
> The component structure and filter logic remain unchanged.

---

## 12. Security

### 12.1 CORS

```yaml
allow_origins: ["http://localhost:5173", "https://getsmart.dev"]
allow_methods: ["GET", "POST", "PATCH", "DELETE"]
allow_headers: ["Content-Type", "Authorization"]
allow_credentials: true
```

### 12.2 Rate Limiting

| Endpoint | Window | Max Requests |
|----------|--------|-------------|
| Login attempts | 15 min | 5 |
| Block duration | — | 30 min |

### 12.3 CSRF Protection

- Token header: `X-CSRF-Token`
- Cookie name: `csrf_token`
- Required for all `POST`, `PATCH`, `DELETE` requests

---

## 13. Error Handling

| Code | HTTP | User Message | Action |
|------|------|-------------|--------|
| AUTH_001 | 400 | "Authentication provider not supported" | — |
| AUTH_002 | 401 | "Authentication failed. Please try again." | — |
| AUTH_003 | 401 | "Your session has expired." | Redirect to login |
| AUTH_004 | 500 | "Authentication service unavailable." | Retry |
| AUTH_005 | 401 | "Unable to refresh session." | Redirect to login |
