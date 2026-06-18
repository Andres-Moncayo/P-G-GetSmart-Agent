# UI & Login — Functional Specification

> **Artifact:** `ui_login_contract.yaml`  
> **Phase:** Phase 0 (Pre-pipeline)  
> **Status:** Draft  
> **Last Updated:** 2026-06-17

---

## 1. Overview

This document describes the authentication, navigation, and user profile systems for the GetSmart frontend. It covers the SSO login flow, session management, topbar navigation, and profile modal interactions.

The UI follows the **Globant Enterprise Dark Mode — Game Library Edition** design system with a blue accent palette (`#3B82F6`) inspired by PlayStation/Xbox menu aesthetics.

---

## 2. Login Flow

### 2.1 Entry Point

Users land on a centered login screen with:

- **Background:** Dark base (`#0A0A0A`) with a subtle radial gradient (`rgba(59,130,246,0.08)`) and a dot grid pattern (`40px` spacing, `#2A2A2A`)
- **Logo:** `64x64px` rounded-2xl gradient card (blue → violet) with gamepad icon
- **Brand:** "Get**Smart**" with "Smart" in accent blue
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
- Icon: `20px` SVG or FontAwesome
- Text: "Sign in with {Provider}", font-medium, text-sm

### 2.3 Demo Account

A primary CTA button below the divider:
- Text: "Sign in with demo account"
- Style: Full-width, accent blue background (`#3B82F6`)
- Shadow: `shadow-accent/25`
- Hover: Darkens to `#2563EB`, shadow intensifies
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
┌─────────────────────────────────────────────────────────────┐
│  [🔷] GetSmart    Reports  Pipeline  Templates  Docs   [🔍][🔔][👤] │
└─────────────────────────────────────────────────────────────┘
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
- **Notifications:** Bell icon with animated dot pulse (`#3B82F6`, `2s` infinite). Click opens notification dropdown
- **Profile trigger:** Avatar (`28x28px`, gradient circle with initials) + name (hidden on mobile) + chevron down

---

## 4. Profile Modal

Triggered by clicking the profile trigger. Appears as a dropdown below the topbar (`top: 64px`, `right: 24px`).

### 4.1 Layout

```
┌─────────────────────────────┐
│  [👤] Alejandro L.          │
│      alejandro.l@globant.com │
│  ┌─────────────────────────┐│
│  │ Senior AI Engineer ·    ││
│  │ Enterprise              ││
│  └─────────────────────────┘│
├─────────────────────────────┤
│  ✏️ Edit profile            │
│  🛡️ Security & SSO          │
│  ⚙️ Preferences             │
│  🔑 API Keys                │
├─────────────────────────────┤
│  ❓ Help & Support          │
│  🚪 Sign out (danger red)   │
└─────────────────────────────┘
```

### 4.2 Menu Items

Each item:
- `px-5 py-2.5`, text-left
- Icon: `text-muted`, `16px`, fixed width
- Label: `text-secondary`, hover → `text-primary`
- Background: transparent, hover → `bg-elevated`
- "Sign out": `text-danger`, hover → `bg-danger/10`

---

## 5. State Management

### 5.1 Auth Store (Zustand)

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

Persisted to `localStorage` for auth state hydration on refresh.

### 5.2 UI Store (Zustand)

```typescript
interface UIState {
  profileModalOpen: boolean;
  activeNavItem: string;

  toggleProfileModal: () => void;
  setActiveNavItem: (item: string) => void;
}
```

Not persisted (ephemeral UI state).

---

## 6. Security

### 6.1 CORS

```yaml
allow_origins: ["http://localhost:5173", "https://getsmart.dev"]
allow_methods: ["GET", "POST", "PATCH", "DELETE"]
allow_headers: ["Content-Type", "Authorization"]
allow_credentials: true
```

### 6.2 Rate Limiting

| Endpoint | Window | Max Requests |
|----------|--------|-------------|
| Login attempts | 15 min | 5 |
| Block duration | — | 30 min |

### 6.3 CSRF Protection

- Token header: `X-CSRF-Token`
- Cookie name: `csrf_token`
- Required for all `POST`, `PATCH`, `DELETE` requests

---

## 7. API Endpoints Summary

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/api/v1/auth/login/{provider}` | Initiate SSO | None |
| GET | `/api/v1/auth/callback/{provider}` | Handle callback | None |
| POST | `/api/v1/auth/logout` | Terminate session | Cookie |
| POST | `/api/v1/auth/refresh` | Refresh token | Cookie |
| GET | `/api/v1/me` | Get profile | Cookie |
| PATCH | `/api/v1/me` | Update profile | Cookie |
| GET | `/api/v1/me/api-keys` | List API keys | Cookie |
| POST | `/api/v1/me/api-keys` | Generate key | Cookie |
| DELETE | `/api/v1/me/api-keys/{id}` | Revoke key | Cookie |

---

## 8. Error Handling

| Code | HTTP | User Message | Action |
|------|------|-------------|--------|
| AUTH_001 | 400 | "Authentication provider not supported" | — |
| AUTH_002 | 401 | "Authentication failed. Please try again." | — |
| AUTH_003 | 401 | "Your session has expired." | Redirect to login |
| AUTH_004 | 500 | "Authentication service unavailable." | Retry |
| AUTH_005 | 401 | "Unable to refresh session." | Redirect to login |
