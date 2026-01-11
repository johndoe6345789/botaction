# viewer_controls.js

## Overview
Floating UI positioning library for creating tooltips, popovers, dropdowns, and other floating elements with intelligent positioning and collision detection.

## File Status
- **Type**: Minified Sketchfab Webpack Bundle
- **Webpack Chunk ID**: 1612
- **Source Map**: `2a63f2db655c1f7e6b86930c0195af16-v2.js.map`

## Key Components

### Module Exports (7oK2)
| Export | Description |
|--------|-------------|
| `YF` | `useFloating` - React hook for floating element positioning |
| `x7` | Arrow middleware for tooltip arrows |

### Floating UI Core (dx2a)
| Export | Description |
|--------|-------------|
| `JB` | Convert rect to viewport-relative |
| `RR` | Flip middleware |
| `cv` | Offset middleware |
| `dp` | Size middleware |
| `oo` | Core compute position function |
| `uY` | Shift middleware |
| `x7` | Arrow positioning |

### Placement Calculations
```javascript
// Supported placements
"top", "bottom", "left", "right"
// With alignment
"top-start", "top-end", "bottom-start", "bottom-end"
"left-start", "left-end", "right-start", "right-end"
```

### Middleware System
1. **Offset** - Add distance between reference and floating element
2. **Flip** - Change placement when there's insufficient space
3. **Shift** - Move along axis to fit in viewport
4. **Arrow** - Position arrow element
5. **Size** - Resize floating element to fit

### Platform Utilities (wA4o)
| Function | Description |
|----------|-------------|
| `Me` | `autoUpdate` - Reposition on scroll/resize |
| `oo` | `computePosition` - Calculate position |
| `getClippingRect` | Get clipping boundaries |
| `getOffsetParent` | Find offset parent element |
| `getDimensions` | Get element dimensions |
| `isElement` | Check if DOM element |
| `isRTL` | Check right-to-left direction |

## React Integration
```javascript
// useFloating hook
const {
  x, y,           // Position coordinates
  strategy,       // 'absolute' | 'fixed'
  placement,      // Final placement
  middlewareData, // Data from middleware
  refs,           // Reference and floating refs
  update          // Manual update function
} = useFloating({
  middleware: [...],
  placement: 'bottom',
  strategy: 'absolute',
  whileElementsMounted: autoUpdate
});
```

## Dependencies
- React (useRef, useEffect, useState, useCallback, useMemo)
- React DOM (flushSync)
- ResizeObserver API
- MutationObserver API (browser)

## Technical Details
- Collision detection with clipping ancestors
- Support for virtual elements
- RTL (right-to-left) language support
- Shadow DOM compatibility
- Scroll container detection
- Viewport-relative positioning

## Use Cases
1. Tooltip positioning
2. Dropdown menus
3. Popover dialogs
4. Context menus
5. Autocomplete suggestions
6. Date picker positioning

## Notes
- Floating UI is the successor to Popper.js
- Middleware is composable and extensible
- Handles edge cases like scrolling containers
- Performance optimized with lazy updates
- Used throughout Sketchfab UI components
