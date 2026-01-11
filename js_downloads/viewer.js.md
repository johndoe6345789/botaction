# viewer.js

## Overview
Main Sketchfab 3D viewer component - minified webpack bundle that provides the core 3D model viewing functionality.

## File Status
- **Type**: Minified JavaScript (webpack bundle)
- **Format**: Production build with source map reference
- **Source Map**: `003e17cf8436f71742af34ea31fea135-v2.js.map`

## Key Components

### Core Viewer Features
- **WebGL Support Detection**: Checks browser capabilities, validates WebGL context
- **3D Model Viewer**: Core viewer component with embed support
- **Popup System**: Modal dialogs and popups for UI interactions
- **Message Popups**: User notifications and confirmations
- **React Integration**: Wrapper for integrating React components into Backbone views
- **Lazy Loading**: Deferred image loading for performance

### Technical Modules
- **ShaderValidation**: WebGL shader compilation and testing
- **Camera**: Countdown timers and calendar components
- **Form Controls**: Switches, dropdowns, input elements
- **Inspector**: Model property inspection and debugging

### WebGL Capabilities
- Tests for shader precision, uniform vectors, varying vectors
- SwiftShader detection and filtering
- Context loss handling
- Validates minimum requirements (64 fragment uniform vectors, 8 varying vectors)

## Dependencies
- React 18 ecosystem
- Webpack chunk loading (`webpackChunksketchfab`)
- Various Sketchfab internal modules (lotc, KDlt, X40V, etc.)

## Technical Details
- **Bundle ID**: 6138
- **Module System**: Self-executing webpack chunks
- **React Version**: 18.2.0 (from createRoot API usage)
- **Architecture**: Component-based with mixins support

## Use Cases
- Primary 3D model viewer initialization
- Embed iframe management and communication
- User interface popup management
- Form handling and validation
- WebGL capability testing

## Notes
- Minified for production use
- Contains multiple sub-modules bundled together
- Uses modern React patterns (Hooks, createRoot)
- Includes fallback handling for older browsers
- Source map available for debugging
