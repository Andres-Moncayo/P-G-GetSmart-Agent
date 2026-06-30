# GetSmart Frontend

Frontend application for GetSmart - Game Intelligence Library, built with React, Vite, and TypeScript.

## Features

- **Modern Stack**: React 18, TypeScript, Vite
- **Styling**: Tailwind CSS with custom design system
- **Authentication**: Social OAuth (Google, Microsoft, Okta)
- **State Management**: Zustand
- **UI Components**: Custom components with Tailwind
- **Routing**: React Router v6
- **HTTP Client**: Axios with interceptors
- **Development**: ESLint + Prettier

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Copy environment file:
```bash
cp .env.example .env
```

3. Start development server:
```bash
npm run dev
```

4. Open [http://localhost:5173](http://localhost:5173)

## Development Scripts

```bash
npm run dev      # Start development server
npm run build    # Build for production
npm run preview  # Preview production build
npm run lint     # Run ESLint
npm run lint:fix # Fix ESLint issues
```

## Project Structure

```
src/
├── components/         # Reusable UI components
│   ├── LoginScreen.tsx
│   ├── Topbar.tsx
│   └── ProfileModal.tsx
├── pages/            # Page components
│   └── Dashboard.tsx
├── stores/           # State management
│   ├── authStore.ts
│   └── uiStore.ts
├── services/         # API services
│   └── api.ts
├── types/            # TypeScript definitions
│   └── types.ts
├── App.tsx           # Main app component
└── main.tsx          # App entry point
```

## Components

### LoginScreen
- Social login with Google, Microsoft, Okta
- Demo account access
- Loading states and error handling
- Responsive design

### Topbar
- Navigation menu
- User profile dropdown
- Notification indicators
- Search functionality

### ProfileModal
- User profile management
- Role and permissions display
- Edit profile options
- Logout functionality

## State Management

Using Zustand for state management:
- `authStore`: Authentication state and user data
- `uiStore`: UI state (modals, navigation)

## Authentication Workflow

1. User clicks social login button
2. Redirects to OAuth provider
3. Provider redirects back with auth code
4. Frontend exchanges code for tokens
5. Sets user session in zustand store
6. Redirects to dashboard

## Environment Variables

```env
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=GetSmart
VITE_APP_DESCRIPTION=Game Intelligence Library
```

## Styling

Tailwind CSS with custom design system:
- Color palette based on CSS variables
- Custom animations
- Component utilities
- Grid patterns

## Build

Production build with Vite:
- TypeScript compilation
- Tree shaking
- Code splitting
- Asset optimization

## Contributing

1. Follow existing code patterns
2. Use TypeScript strictly
3. Follow component structure
4. Test across browsers
5. Update documentation

## License

MIT
