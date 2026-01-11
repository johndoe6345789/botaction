# visibility_popup.js

## Overview
Sketchfab utility components module - minified webpack bundle providing various UI utilities including visibility settings, theming, forms, and helper components.

## File Status
- **Type**: Minified JavaScript (webpack bundle)
- **Format**: Production build with source map reference
- **Source Map**: `6ce812b2431334783034d02de2b36689-v2.js.map`

## Key Components

### Visibility & Privacy
- **Theme Management**: Light/dark theme switching with persistence
- **Visibility Select**: Model privacy settings (public, private, protected, org)
- **Visibility Radio**: Alternative radio button interface for visibility
- **Settings Integration**: Connect to Sketchfab settings API

### UI Components
- **Message Boxes**: Info, warning, error message displays
- **Tooltips**: Contextual help tooltips
- **Radio Buttons**: Custom styled radio inputs
- **Help Links**: Contextual help with tooltip support

### Utility Features
- **Theme Switching**: System for managing UI themes
- **URL Helpers**: FAB/Sketchfab URL construction
- **Escape HTML**: Security helper for user content
- **Credits System**: Store credit requirements display

## Dependencies
- React and hooks
- Redux state management (VDcQ, +zma)
- Routing utilities (iu9k)
- Icon system (ESrx)

## Technical Details
- **Bundle ID**: 8048
- **Module System**: Webpack chunks
- **Export Names**: Foai (Theme), +TPG (Switch), JT1T (RadioList), hK4n (VisibilitySelect)

## Use Cases
- Model visibility/privacy settings
- Theme switching (light/dark/high-contrast)
- Form controls for user preferences
- Help documentation links
- Store upgrade prompts

## Notes
- Integrates with Sketchfab privacy system
- LocalStorage for theme persistence
- Supports organizational context
- Cart limit handling for store items
- Accessibility features included
