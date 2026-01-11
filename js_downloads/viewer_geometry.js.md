# viewer_geometry.js

## Overview
Minified Sketchfab webpack chunk containing the router system and React page rendering utilities for client-side navigation and page hydration.

## File Status
- **Type**: Minified JavaScript (Webpack Bundle)
- **Chunk ID**: 109
- **Minified**: Yes
- **Source Map**: Available (referenced in file)

## Key Components

### Module "560e" - Router System
Core routing system with lifecycle management:

**Route Types**:
- `Push` - Push new route to history
- `Replace` - Replace current route in history
- `Reload` - Reload current route
- `NoOp` - No operation

**Router Class (h)**:
- `isFirstRouterRun` - Boolean flag for initial run
- `routes[]` - Array of registered routes
- `activeRoutesStack[]` - Stack of currently active routes
- `handlingRoute` - Current route being handled

**Lifecycle Methods**:
- `onRemove` - Route cleanup callback
- `onUpdate` - Route update callback
- `onStartHandling` - Begin route handling
- `onStopHandling` - End route handling
- `onCreate` - Route creation callback

**Functions**:
- `l` - Route action factory (push, replace, reload, noOp)
- `p` - Page reload with scroll position reset

### Module "vxiz" - React Page Rendering
React-based page rendering with server-side hydration support:

**Key Functions**:
- `R` - Route matcher function
- `g/m` - Route creators
- `P/b` - Callback handlers
- `S` - Main React page renderer

**Features**:
- Server-side hydration support
- `hydrateRoot` for existing SSR markup
- `createRoot` for client-side rendering
- Redux store integration for page components

## Dependencies
- React 18.x (`React.createElement`)
- React DOM (`hydrateRoot`, `createRoot`)
- Redux (store integration)
- History API (browser navigation)

## Technical Details
- Uses React 18 concurrent features
- Supports progressive hydration
- Integrates with browser History API
- Redux state management for pages

## Use Cases
1. Single Page Application navigation
2. Server-side rendered page hydration
3. Client-side route handling
4. Progressive page loading

## Notes
- Part of Sketchfab's SPA architecture
- Critical for page navigation without full reloads
- Supports deep linking and back/forward navigation
- Route lifecycle enables resource cleanup
