# viewer_annotations.js

## Overview
Minified Sketchfab webpack chunk containing promotional banner components with countdown timers, calendar displays, and cookie-based state management for dismissing banners.

## File Status
- **Type**: Minified JavaScript (Webpack Bundle)
- **Chunk ID**: 412
- **Minified**: Yes
- **Source Map**: Available (referenced in file)

## Key Components

### Module "UOoA" - Banner Component
Feature-rich promotional banner with countdown functionality:

**useInterval Hook (o)**
Custom React hook for interval-based updates:
```javascript
const useInterval = (callback, delay) => {
  // Updates callback ref on each render
  // Sets interval when delay is not null
  // Clears interval on unmount
}
```

**useTimeRemaining Hook (d)**
Calculates remaining time until deadline:
- Updates every 1000ms
- Returns object with days, hours, mins, secs

**CalendarCountdown Component (m)**
Visual countdown display:
- CSS class: `c-calendar-countdown`
- Shows days, hrs, mins, secs in "page" format
- Empty placeholder variant for loading

**TextCountdown Component (O)**
Inline text countdown:
- CSS class: `c-text-countdown`
- Format: "Ends in Xd Xhrs Xmins Xsecs"

**Main Banner Component (I)**

**Props**:
| Prop | Type | Description |
|------|------|-------------|
| `title` | string | Banner title |
| `description` | string | HTML description |
| `ctaTitle` | string | Call-to-action text |
| `ctaUrl` | string | CTA link |
| `endsAt` | Date | Countdown end time |
| `size` | "big"/"small" | Banner size |
| `theme` | string | Theme modifier |
| `hasCounter` | boolean | Show countdown |
| `onClickClose` | function | Close handler |
| `showCta` | boolean | Show CTA button |

**Features**:
- Close button with X icon
- Analytics tracking on click/close
- Suspense-wrapped countdown
- Multiple themes (store, etc.)

### Module "x66c" - Banner State Management
Redux-style state management for banner dismissal:

**Actions**:
- `INIT` - Check cookie for closed state
- `CLOSE` - Set cookie and close banner

**State Shape**:
```javascript
{ isClosed: boolean }
```

**Cookie Management**:
- Cookie name: `sb_banner_closed`
- Stores banner UID
- Expires at banner end time

**Banner Variants**:
- `SmallBanner` - Header-style banner
- `BigBanner` - Full-width promotional banner

### Module "+fgk" - Custom useReducer
Enhanced reducer hook with middleware support:
- Integrates with context
- Supports async effects
- Memory for previous state

## Dependencies
- React (hooks, Suspense, lazy)
- Date utilities
- Cookie management
- Analytics tracking
- Lodash utilities

## Technical Details
- Interval-based countdown updates
- Cookie persistence for dismissal
- Suspense for lazy loading
- Redux-like state pattern

## Use Cases
1. Sale/promotion banners
2. Time-limited offers
3. Event countdowns
4. Store promotions

## Notes
- Supports multiple banner sizes
- Analytics on user interaction
- Cookie-based dismissal memory
- Responsive design support
