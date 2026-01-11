# webgl_recorder.js

## Overview
WebGL recording and utility module - minified webpack bundle providing WebGL context recording, device detection, and core React utilities.

## File Status
- **Type**: Minified JavaScript (webpack bundle)
- **Format**: Production build with source map reference
- **Source Map**: `da8ed87c0adc4ddd8992e5e8cbf906fc-v2.js.map`

## Key Components

### WebGL Features
- **Context Recording**: Capture WebGL rendering context
- **Device Detection**: Mobile/tablet/desktop identification
- **Platform Detection**: iOS, Android, Windows detection
- **Browser Detection**: Chrome, Firefox, Safari, Opera identification

### Core React
- **React 18.2.0**: Core React library
- **Component System**: Base component classes
- **Hooks**: useState, useEffect, useContext, etc.
- **JSX Runtime**: createElement and Fragment support

### Device Categories
- Apple devices (iPhone, iPad, iPod)
- Android devices (phones and tablets)
- Windows devices
- BlackBerry devices
- Other mobile platforms

## Dependencies
- Standalone React library
- Symbol.observable polyfill
- Object polyfills

## Technical Details
- **Bundle IDs**: 7065, includes React core
- **Module System**: Webpack chunks
- **Export Names**: K9VK (DeviceDetect), JWea (React), keQT (Axios HTTP client)
- **React Version**: 18.2.0

## Use Cases
- Detect device capabilities for adaptive rendering
- Record WebGL sessions for debugging
- Provide React runtime for viewer
- HTTP requests via Axios
- Cross-platform compatibility detection

## Notes
- Contains full React 18.2.0 library
- Axios HTTP client for API calls
- Comprehensive device detection (mobile, tablet, desktop)
- Supports touch events and hover detection
- Includes Redux utilities for state management
