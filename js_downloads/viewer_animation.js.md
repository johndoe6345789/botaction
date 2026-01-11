# viewer_animation.js

## Overview
3D model animation control module - minified webpack bundle managing animation playback, banners, and countdown timers for Sketchfab viewer.

## File Status
- **Type**: Minified JavaScript (webpack bundle)
- **Format**: Production build with source map reference
- **Source Map**: `3cab602213ea1bd82c11556321522f3e-v2.js.map`

## Key Components

### Animation Features
- **Countdown Timers**: Calendar-based countdowns for events
- **Banner System**: Promotional/notification banners with actions
- **Animation Hooks**: React hooks for managing animations
- **State Management**: Redux-style state management for animations

### UI Elements
- **Calendar Countdown**: Visual countdown display with days/hours/mins/secs
- **Text Countdown**: Text-only countdown format
- **Banner Component**: Configurable banners with CTAs and themes
- **Cookie Management**: Banner dismissal state persistence

## Dependencies
- React and React hooks
- Redux-like state management (MBtD, HGbS)
- Cookie handling (CookieBag)
- Date utilities (TUor)

## Technical Details
- **Bundle ID**: 412
- **Module System**: Webpack chunks
- **Export Names**: UOoA (Countdown), x66c (Banners)
- **State Pattern**: Effect-based state management (Pending/Resolved/Rejected)

## Use Cases
- Display promotional banners
- Show countdown timers for events
- Manage banner dismissal state
- Track banner interactions
- Control animation playback

## Notes
- Supports multiple banner sizes and themes
- Cookie-based persistence for user preferences
- Real-time countdown updates
- Store-specific styling available
