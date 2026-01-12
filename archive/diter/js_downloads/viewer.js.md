# viewer.js

## Overview

This file contains **popup/modal system components, WebGL support detection, and viewer iframe embedding**. It's part of Sketchfab's core UI infrastructure for displaying modals and embedding the 3D viewer.

## File Information

- **Status**: Active webpack bundle
- **Size**: ~90KB (minified)
- **Type**: Popup system and WebGL utilities
- **Framework**: React + Backbone.js

## Core Components

### 1. WebGL Support Detection (`7txH`)

Tests WebGL capability with shader compilation:

```javascript
// Tests performed:
// 1. WebGL context creation (webgl, webgl2, experimental-webgl)
// 2. Shader compilation test
// 3. sRGB/linear color space conversion

// Test shaders:
const vertexShader = `
  attribute vec3 aPosition;
  void main() { gl_Position = vec4(aPosition, 1.0); }
`;

const fragmentShader = `
  precision mediump float;
  uniform vec4 uColor;
  void main() { gl_FragColor = uColor; }
`;

// Detection result:
{ supported: boolean, webgl2: boolean, renderer: string, vendor: string }
```

### 2. Base Popup Class (`7e5f`)

Foundation for all popups:

```javascript
class Popup {
  constructor(options) {
    this.title = options.title;
    this.className = options.className;
    this.isClosable = options.isClosable ?? true;
  }
  
  open() {
    // Add to DOM
    // Set up event listeners
    // Focus management
  }
  
  close() {
    // Cleanup
    // Remove from DOM
    // Return focus
  }
  
  cancel() {
    // Close without action
    this.close();
    this.onCancel?.();
  }
  
  continue() {
    // Close with action
    this.close();
    this.onContinue?.();
  }
}
```

### 3. MessagePopup (`g6dK`)

Standard message dialog:

```javascript
<MessagePopup
  title="Confirm Action"
  message="Are you sure you want to continue?"
  buttons={[
    { label: 'Cancel', action: 'cancel', variant: 'secondary' },
    { label: 'Continue', action: 'continue', variant: 'primary' }
  ]}
  onContinue={handleContinue}
  onCancel={handleCancel}
/>
```

### 4. React Popup Wrapper (`ULsr`)

Wraps React components in popup container:

```javascript
// Bridges React components with popup system
const wrapInPopup = (Component, options) => {
  return class extends Popup {
    render() {
      return createRoot(this.el).render(<Component {...this.props} />);
    }
  };
};
```

### 5. Switch Component (`KGKI`)

Toggle switch UI element:

```javascript
<Switch
  checked={isEnabled}
  onChange={setIsEnabled}
  label="Enable feature"
  disabled={false}
/>
```

### 6. Viewer Iframe Embed (`e+fc`)

Embeds 3D viewer in iframe:

```javascript
<ViewerEmbed
  modelId="abc123"
  options={{
    autostart: true,
    ui_controls: true,
    ui_infos: false,
    camera: true
  }}
  onReady={handleReady}
  onError={handleError}
/>

// Communication via postMessage:
// - start: Begin loading
// - stop: Pause viewer
// - setCamera: Update camera position
// - getScreenshot: Capture current view
```

## WebGL Shaders for Validation

Color space conversion (used for capability testing):

```glsl
// sRGB to Linear
vec3 sRGBToLinear(vec3 srgb) {
  return mix(
    srgb / 12.92,
    pow((srgb + 0.055) / 1.055, vec3(2.4)),
    step(0.04045, srgb)
  );
}

// Linear to sRGB
vec3 linearToSRGB(vec3 linear) {
  return mix(
    linear * 12.92,
    1.055 * pow(linear, vec3(1.0/2.4)) - 0.055,
    step(0.0031308, linear)
  );
}
```

## Popup System Architecture

```
PopupManager (singleton)
    ├── Stack of open popups
    ├── Focus trap management
    ├── Escape key handling
    └── Backdrop click handling

Popup (base class)
    ├── MessagePopup
    ├── ConfirmPopup
    ├── FormPopup
    └── ReactPopup (wrapper)
```

### PopupManager

```javascript
const PopupManager = {
  stack: [],
  
  add(popup) {
    this.stack.push(popup);
    this.updateBackdrop();
  },
  
  remove(popup) {
    this.stack = this.stack.filter(p => p !== popup);
    this.updateBackdrop();
  },
  
  getTopPopup() {
    return this.stack[this.stack.length - 1];
  },
  
  isEmpty() {
    return this.stack.length === 0;
  }
};
```

## iframe Communication Protocol

```javascript
// Parent → iframe messages:
const commands = {
  start: {},
  stop: {},
  setCamera: { position: [x,y,z], target: [x,y,z] },
  setBackground: { color: '#ffffff' },
  getScreenshot: { width: 1920, height: 1080 }
};

// iframe → Parent messages:
const events = {
  ready: { version: '1.0' },
  error: { code: 'WEBGL_NOT_SUPPORTED', message: '...' },
  viewerready: { model: { uid, name, vertexCount } },
  screenshot: { dataUrl: 'data:image/png;base64,...' }
};

// Usage:
iframe.contentWindow.postMessage({ type: 'start' }, '*');

window.addEventListener('message', (event) => {
  if (event.data.type === 'viewerready') {
    // Viewer is ready
  }
});
```

## Dependencies

- React (component rendering)
- Backbone.js (legacy view system)
- DOM APIs (popups, iframes)
- WebGL APIs (capability detection)

## Usage Examples

### Opening a Popup

```javascript
import { MessagePopup } from './viewer';

const popup = new MessagePopup({
  title: 'Delete Model',
  message: 'This action cannot be undone.',
  onContinue: () => deleteModel(modelId),
  onCancel: () => console.log('Cancelled')
});

popup.open();
```

### Embedding Viewer

```javascript
import { ViewerEmbed } from './viewer';

function ModelViewer({ modelId }) {
  return (
    <ViewerEmbed
      modelId={modelId}
      options={{ autostart: true }}
      onReady={(api) => {
        api.addEventListener('viewerready', () => {
          console.log('Model loaded');
        });
      }}
    />
  );
}
```

## Notes

- Combines React and Backbone.js patterns
- WebGL detection is critical for viewer functionality
- Popup system manages focus and accessibility
- iframe embedding uses Sketchfab's viewer API
