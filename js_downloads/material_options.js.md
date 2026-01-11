# material_options.js

## Overview

This file contains **3D viewer initialization and embed options parsing**. It handles URL hash parameters for controlling material display options, viewer analytics, and embed configuration.

## File Information

- **Status**: Active webpack bundle
- **Size**: ~74KB (minified)
- **Type**: Viewer configuration parser
- **Framework**: Vanilla JavaScript

## Core Modules

### 1. Embed Options Parser (`MQQR`)

Parses viewer embed parameters from URL:

```javascript
const options = parseEmbedOptions(urlHash);

// Supported parameters:
// ?autostart=1          - Auto-load model
// ?autospin=0.5         - Auto-rotate speed
// ?camera=0             - Disable camera controls
// ?ui_controls=0        - Hide UI controls
// ?ui_infos=0           - Hide info panel
// ?ui_inspector=0       - Hide inspector
// ?ui_watermark=0       - Hide watermark (requires plan)
// ?annotations_visible=0 - Hide annotations
// ?animation_autoplay=1 - Auto-play animation
// ?preload=1            - Preload textures
// ?transparent=1        - Transparent background
// ?scrollwheel=0        - Disable scroll zoom
// ?double_click=0       - Disable double-click
```

### 2. Hash Parameter Parser (`ng3c`)

```javascript
// Parse hash parameters
const params = parseHashParams('#material=1&wireframe=1');
// { material: '1', wireframe: '1' }

// Build hash string
const hash = buildHashParams({
  material: 1,
  wireframe: 1
});
// 'material=1&wireframe=1'
```

### 3. Material Display Options

Material rendering toggles:

```javascript
const materialOptions = {
  // Textures
  diffuse: true,          // Base color texture
  normal: true,           // Normal map
  emissive: true,         // Emissive/glow
  transparency: true,     // Alpha/transparency
  
  // PBR properties
  metalness: true,        // Metalness map
  roughness: true,        // Roughness map
  glossiness: true,       // Glossiness (spec workflow)
  specular: true,         // Specular map
  f0: true,               // Fresnel reflectance
  
  // Other maps
  cavity: true,           // Cavity/AO detail
  ao: true,               // Ambient occlusion
  displacement: true,     // Displacement/height
  
  // Display modes
  wireframe: false,       // Show wireframe
  vertexColors: false,    // Show vertex colors
  matcap: null,           // MatCap material override
  
  // Quality
  shadowQuality: 'high',  // Shadow resolution
  ssaoEnabled: true,      // Screen-space AO
  ssrEnabled: false       // Screen-space reflections
};
```

### 4. Pixel Ratio Utilities (`JueD`)

Device pixel ratio handling:

```javascript
// Get optimal pixel ratio
const pixelRatio = getPixelRatio({
  max: 2,              // Cap at 2x
  deviceRatio: window.devicePixelRatio,
  canvasWidth: 1920,
  maxTextureSize: 4096
});

// Performance-based adjustment
const adjustedRatio = getPerformancePixelRatio({
  preferredRatio: 2,
  fps: currentFps,
  threshold: 30
});
```

### 5. Analytics Initialization (`GuWZ`)

Viewer analytics setup:

```javascript
// Initialize analytics tracking
initViewerAnalytics({
  modelId: 'abc123',
  userId: 'user456',
  embedType: 'iframe',
  referrer: document.referrer
});

// Track events
trackViewerEvent('model_loaded', {
  loadTime: 2500,
  textureCount: 12,
  vertexCount: 50000
});

trackViewerEvent('interaction', {
  type: 'rotate',
  duration: 5000
});
```

### 6. Event Utilities (`yTkX`)

DOM event helpers:

```javascript
// Cross-browser event handling
addEvent(element, 'click', handler);
removeEvent(element, 'click', handler);

// Event delegation
delegateEvent(container, '.button', 'click', handler);

// Pointer events normalization
const pointer = normalizePointerEvent(event);
// { x, y, pressure, button, pointerType }
```

## URL Hash Material Options

Complete material option parameters:

```
#showcase=1             // Inspector showcase mode
&names=1               // Show material names
&normal=1              // Enable normal maps
&emissive=1            // Enable emissive
&transparency=1        // Enable transparency
&diffuse=1             // Enable diffuse textures
&metalness=1           // Enable metalness
&roughness=1           // Enable roughness  
&glossiness=1          // Enable glossiness
&specular=1            // Enable specular
&cavity=1              // Enable cavity maps
&f0=1                  // Enable F0 reflectance
&ao=1                  // Enable ambient occlusion
&displacement=1        // Enable displacement
```

## Embed Parameter Parsing

```javascript
// Full embed URL parsing
const config = parseViewerUrl(
  'https://sketchfab.com/models/abc123/embed' +
  '?autostart=1&ui_controls=0&annotation=1#material=2'
);

// Returns:
{
  modelId: 'abc123',
  embed: {
    autostart: true,
    ui_controls: false,
    annotation: 1
  },
  material: {
    selectedIndex: 2
  }
}
```

## Integration with Viewer

```javascript
// Initialize viewer with parsed options
function initViewer(iframe, options) {
  const viewerOptions = {
    ...defaultOptions,
    ...parseEmbedOptions(location.hash)
  };
  
  iframe.src = buildViewerUrl(modelId, viewerOptions);
  
  // Wait for viewer ready
  iframe.addEventListener('load', () => {
    // Send material options to viewer
    iframe.contentWindow.postMessage({
      type: 'setMaterialOptions',
      options: parseMaterialOptions(location.hash)
    }, '*');
  });
}
```

## Usage Examples

### Embed with Custom Options

```html
<iframe 
  src="https://sketchfab.com/models/abc123/embed?autostart=1&ui_infos=0#diffuse=1&normal=1"
  width="640"
  height="480"
  frameborder="0"
></iframe>
```

### JavaScript Configuration

```javascript
const viewerConfig = {
  autostart: true,
  ui_controls: true,
  ui_infos: false,
  camera: true,
  scrollwheel: true,
  
  material: {
    diffuse: true,
    normal: true,
    metalness: true,
    roughness: true
  }
};

const url = buildViewerUrl('abc123', viewerConfig);
// https://sketchfab.com/models/abc123/embed?autostart=1&...#diffuse=1&normal=1&...
```

### Dynamic Material Toggle

```javascript
function toggleMaterial(option, enabled) {
  const hash = parseHashParams(location.hash);
  hash[option] = enabled ? '1' : '0';
  location.hash = buildHashParams(hash);
  
  // Notify viewer
  viewerIframe.contentWindow.postMessage({
    type: 'materialOptionChanged',
    option,
    enabled
  }, '*');
}
```

## Notes

- Accurately named - handles material/viewer options
- Parses URL hash for material display settings
- Integrates with Sketchfab's embedded viewer
- Used for viewer customization via URL parameters
- Analytics integration for viewer usage tracking
