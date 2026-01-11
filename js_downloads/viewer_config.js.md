# viewer_config.js

## Overview

This file contains **3D viewer configuration JSON** - the settings and options for the Sketchfab WebGL viewer. It defines default values, viewer parameters, and configuration schemas.

## File Information

- **Status**: Active webpack bundle
- **Size**: ~35KB (minified)
- **Type**: Configuration module
- **Format**: JSON/JavaScript objects

## Configuration Structure

### Viewer Options

```javascript
const viewerConfig = {
  // Renderer settings
  renderer: {
    antialias: true,
    alpha: false,
    preserveDrawingBuffer: false,
    powerPreference: 'high-performance',  // 'default' | 'high-performance' | 'low-power'
    failIfMajorPerformanceCaveat: false,
    maxPixelRatio: 2
  },
  
  // Camera defaults
  camera: {
    fov: 45,
    near: 0.1,
    far: 10000,
    position: [0, 0, 5],
    target: [0, 0, 0],
    upVector: [0, 1, 0],
    constrainPan: false,
    constrainZoom: false,
    minDistance: 0.01,
    maxDistance: 1000
  },
  
  // Controls
  controls: {
    enabled: true,
    autoRotate: false,
    autoRotateSpeed: 1,
    enablePan: true,
    enableZoom: true,
    enableRotate: true,
    dampingFactor: 0.1,
    rotateSpeed: 1,
    zoomSpeed: 1,
    panSpeed: 1,
    scrollWheel: true,
    doubleClickToFocus: true
  },
  
  // Lighting
  lighting: {
    environment: 'studio',
    exposure: 1,
    shadowsEnabled: true,
    shadowBias: 0.001,
    lightIntensity: 1
  },
  
  // Post-processing
  postProcessing: {
    enabled: true,
    toneMappingEnabled: true,
    toneMappingExposure: 1,
    ssaoEnabled: false,
    ssaoRadius: 0.5,
    ssaoIntensity: 0.5,
    bloomEnabled: false,
    bloomThreshold: 0.8,
    bloomIntensity: 0.5,
    sharpenEnabled: false,
    sharpenAmount: 0.5,
    vignetteEnabled: false
  },
  
  // UI settings
  ui: {
    controls: true,
    infos: true,
    inspector: true,
    watermark: true,
    hint: true,
    help: true,
    settings: true,
    annotations: true,
    fullscreen: true,
    autoplay: true
  }
};
```

### Environment Presets

```javascript
const environmentPresets = {
  studio: {
    name: 'Studio',
    hdri: null,
    backgroundColor: [0.18, 0.18, 0.18],
    intensity: 1,
    shadowsEnabled: true
  },
  urban: {
    name: 'Urban',
    hdri: 'urban_hdri.hdr',
    backgroundColor: [0.4, 0.6, 0.8],
    intensity: 0.8,
    shadowsEnabled: true
  },
  dawn: {
    name: 'Dawn',
    hdri: 'dawn_hdri.hdr',
    backgroundColor: [0.9, 0.7, 0.5],
    intensity: 0.6,
    shadowsEnabled: true
  },
  night: {
    name: 'Night',
    hdri: 'night_hdri.hdr',
    backgroundColor: [0.05, 0.05, 0.1],
    intensity: 0.3,
    shadowsEnabled: false
  },
  custom: {
    name: 'Custom',
    hdri: null,
    backgroundColor: [1, 1, 1],
    intensity: 1,
    shadowsEnabled: true
  }
};
```

### Quality Presets

```javascript
const qualityPresets = {
  low: {
    name: 'Low',
    pixelRatio: 1,
    shadows: false,
    ssao: false,
    antialiasing: false,
    textureQuality: 0.5
  },
  medium: {
    name: 'Medium',
    pixelRatio: 1.5,
    shadows: true,
    ssao: false,
    antialiasing: true,
    textureQuality: 0.75
  },
  high: {
    name: 'High',
    pixelRatio: 2,
    shadows: true,
    ssao: true,
    antialiasing: true,
    textureQuality: 1
  },
  ultra: {
    name: 'Ultra',
    pixelRatio: window.devicePixelRatio,
    shadows: true,
    ssao: true,
    antialiasing: true,
    textureQuality: 1,
    supersample: true
  }
};
```

### Annotation Schema

```javascript
const annotationSchema = {
  type: 'object',
  properties: {
    uid: { type: 'string' },
    index: { type: 'number' },
    
    // Position
    position: {
      type: 'array',
      items: { type: 'number' },
      minItems: 3,
      maxItems: 3
    },
    
    // Camera
    eye: { type: 'array', items: { type: 'number' } },
    target: { type: 'array', items: { type: 'number' } },
    
    // Content
    title: { type: 'string', maxLength: 100 },
    content: { type: 'string', maxLength: 2000 },
    
    // Visibility
    visible: { type: 'boolean' }
  },
  required: ['position', 'title']
};
```

### Animation Settings

```javascript
const animationConfig = {
  // Playback
  autoplay: false,
  loop: true,
  speed: 1,
  
  // Timeline
  showTimeline: true,
  timelinePosition: 'bottom',
  
  // Blending
  crossFade: true,
  crossFadeDuration: 0.3,
  
  // Constraints
  minSpeed: 0.1,
  maxSpeed: 10
};
```

### Material Override Schema

```javascript
const materialOverrideSchema = {
  // PBR properties
  albedoPBR: { type: 'color', default: [1, 1, 1] },
  metallicPBR: { type: 'number', min: 0, max: 1, default: 0 },
  roughnessPBR: { type: 'number', min: 0, max: 1, default: 0.5 },
  
  // Emission
  emissive: { type: 'color', default: [0, 0, 0] },
  emissiveIntensity: { type: 'number', min: 0, max: 10, default: 1 },
  
  // Transparency
  opacity: { type: 'number', min: 0, max: 1, default: 1 },
  alphaMode: { 
    type: 'enum', 
    values: ['OPAQUE', 'MASK', 'BLEND'],
    default: 'OPAQUE'
  },
  alphaCutoff: { type: 'number', min: 0, max: 1, default: 0.5 },
  
  // Rendering
  doubleSided: { type: 'boolean', default: false },
  wireframe: { type: 'boolean', default: false }
};
```

## Embed Configuration

```javascript
const embedConfig = {
  // URL parameters
  autostart: { type: 'boolean', default: false, urlParam: 'autostart' },
  autospin: { type: 'number', default: 0, urlParam: 'autospin' },
  preload: { type: 'boolean', default: true, urlParam: 'preload' },
  
  // UI toggles
  ui_controls: { type: 'boolean', default: true, urlParam: 'ui_controls' },
  ui_infos: { type: 'boolean', default: true, urlParam: 'ui_infos' },
  ui_inspector: { type: 'boolean', default: true, urlParam: 'ui_inspector' },
  ui_watermark: { type: 'boolean', default: true, urlParam: 'ui_watermark' },
  ui_hint: { type: 'boolean', default: true, urlParam: 'ui_hint' },
  ui_help: { type: 'boolean', default: true, urlParam: 'ui_help' },
  ui_annotations: { type: 'boolean', default: true, urlParam: 'annotations_visible' },
  
  // Interaction
  scrollwheel: { type: 'boolean', default: true, urlParam: 'scrollwheel' },
  double_click: { type: 'boolean', default: true, urlParam: 'double_click' },
  
  // Appearance
  transparent: { type: 'boolean', default: false, urlParam: 'transparent' },
  
  // Animation
  animation_autoplay: { type: 'boolean', default: false, urlParam: 'animation_autoplay' }
};
```

## Usage

### Get Config Value

```javascript
function getConfig(path, defaultValue) {
  const parts = path.split('.');
  let value = viewerConfig;
  
  for (const part of parts) {
    if (value && typeof value === 'object' && part in value) {
      value = value[part];
    } else {
      return defaultValue;
    }
  }
  
  return value;
}

// Usage
const fov = getConfig('camera.fov', 45);
const ssao = getConfig('postProcessing.ssaoEnabled', false);
```

### Merge User Config

```javascript
function mergeConfig(userConfig) {
  return deepMerge(viewerConfig, userConfig);
}

// Usage
const config = mergeConfig({
  camera: { fov: 60 },
  controls: { autoRotate: true }
});
```

### Validate Config

```javascript
function validateConfig(config, schema) {
  const errors = [];
  
  for (const [key, def] of Object.entries(schema)) {
    const value = config[key];
    
    if (def.required && value === undefined) {
      errors.push(`${key} is required`);
    }
    
    if (def.type === 'number' && typeof value !== 'number') {
      errors.push(`${key} must be a number`);
    }
    
    if (def.min !== undefined && value < def.min) {
      errors.push(`${key} must be >= ${def.min}`);
    }
    
    if (def.max !== undefined && value > def.max) {
      errors.push(`${key} must be <= ${def.max}`);
    }
  }
  
  return errors;
}
```

## Notes

- Central configuration for 3D viewer
- Quality presets for different hardware
- Environment/lighting presets
- Schema definitions for validation
- Embed URL parameter mappings
- Default values for all settings
