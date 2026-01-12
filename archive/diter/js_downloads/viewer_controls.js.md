# viewer_controls.js

## Overview

This file contains **Floating UI positioning system** for tooltips, dropdowns, and popovers. It's NOT related to 3D viewer controls despite its filename.

## File Information

- **Status**: Active webpack bundle
- **Size**: ~89KB (minified)
- **Type**: UI positioning library
- **Library**: Floating UI (similar to Popper.js)

## Core Functionality

### 1. useFloating Hook (`7oK2`)

Main positioning hook:

```javascript
const { x, y, strategy, refs, update } = useFloating({
  placement: 'bottom-start',  // Position relative to reference
  middleware: [
    offset(8),                 // Distance from reference
    flip(),                    // Flip to opposite side if needed
    shift({ padding: 8 }),     // Shift to stay in viewport
    arrow({ element: arrowRef })
  ]
});

// Returns:
// x, y: Computed position coordinates
// strategy: 'absolute' or 'fixed'
// refs: { reference, floating }
// update: Function to recalculate position
```

### 2. Placement Options

```javascript
const placements = [
  'top', 'top-start', 'top-end',
  'right', 'right-start', 'right-end',
  'bottom', 'bottom-start', 'bottom-end',
  'left', 'left-start', 'left-end'
];
```

### 3. Middleware System (`dx2a`)

#### offset

Adds distance between reference and floating element:

```javascript
offset(8)                    // 8px gap
offset({ mainAxis: 8 })      // Same as above
offset({ crossAxis: 4 })     // Offset perpendicular to placement
offset({ alignmentAxis: 4 }) // Offset along alignment axis
```

#### flip

Flips to opposite placement if not enough space:

```javascript
flip()                       // Default behavior
flip({ fallbackPlacements: ['top', 'left'] })
flip({ fallbackStrategy: 'bestFit' })
flip({ boundary: document.body })
```

#### shift

Shifts along axis to stay in viewport:

```javascript
shift()                      // Default behavior
shift({ padding: 8 })        // Minimum distance from boundary
shift({ limiter: limitShift() })
shift({ boundary: 'clippingAncestors' })
```

#### size

Resizes floating element to fit:

```javascript
size({
  apply({ availableWidth, availableHeight, elements }) {
    Object.assign(elements.floating.style, {
      maxWidth: `${availableWidth}px`,
      maxHeight: `${availableHeight}px`
    });
  }
})
```

#### arrow

Positions arrow element:

```javascript
arrow({ element: arrowRef })
arrow({ padding: 8 })        // Minimum distance from edges

// Returns:
// middlewareData.arrow.x: Arrow x position
// middlewareData.arrow.y: Arrow y position
```

### 4. DOM Platform Utilities (`wA4o`)

#### getClippingRect

Calculates visible area:

```javascript
getClippingRect({
  element,
  boundary: 'clippingAncestors',  // or HTMLElement[]
  rootBoundary: 'viewport',       // or 'document'
  strategy: 'absolute'
})
// Returns: { x, y, width, height }
```

#### convertOffsetParent

Handles offset parent calculations:

```javascript
convertOffsetParent(element, offsetParent)
// Returns transformed coordinates
```

#### autoUpdate

Automatically updates position on changes:

```javascript
const cleanup = autoUpdate(
  referenceElement,
  floatingElement,
  updatePosition,
  {
    ancestorScroll: true,     // Update on ancestor scroll
    ancestorResize: true,     // Update on ancestor resize
    elementResize: true,      // Update on element resize
    animationFrame: false     // Use requestAnimationFrame
  }
);

// Call cleanup() to stop auto-updates
```

## Usage Examples

### Tooltip

```jsx
function Tooltip({ label, children }) {
  const [isOpen, setIsOpen] = useState(false);
  const { x, y, strategy, refs, middlewareData } = useFloating({
    placement: 'top',
    open: isOpen,
    middleware: [offset(8), flip(), shift({ padding: 8 })]
  });
  
  return (
    <>
      <div
        ref={refs.setReference}
        onMouseEnter={() => setIsOpen(true)}
        onMouseLeave={() => setIsOpen(false)}
      >
        {children}
      </div>
      {isOpen && (
        <div
          ref={refs.setFloating}
          style={{
            position: strategy,
            top: y ?? 0,
            left: x ?? 0
          }}
        >
          {label}
        </div>
      )}
    </>
  );
}
```

### Dropdown

```jsx
function Dropdown({ trigger, content }) {
  const [isOpen, setIsOpen] = useState(false);
  const { x, y, strategy, refs } = useFloating({
    placement: 'bottom-start',
    open: isOpen,
    middleware: [
      offset(4),
      flip(),
      shift({ padding: 8 }),
      size({
        apply({ availableHeight, elements }) {
          elements.floating.style.maxHeight = `${availableHeight}px`;
        }
      })
    ]
  });
  
  useEffect(() => {
    if (isOpen) {
      return autoUpdate(refs.reference.current, refs.floating.current, () => {
        // Position update
      });
    }
  }, [isOpen, refs]);
  
  return (
    <>
      <button ref={refs.setReference} onClick={() => setIsOpen(!isOpen)}>
        {trigger}
      </button>
      {isOpen && (
        <div
          ref={refs.setFloating}
          style={{ position: strategy, top: y ?? 0, left: x ?? 0 }}
        >
          {content}
        </div>
      )}
    </>
  );
}
```

### With Arrow

```jsx
function Popover({ trigger, content }) {
  const arrowRef = useRef(null);
  const { x, y, strategy, refs, middlewareData, placement } = useFloating({
    placement: 'top',
    middleware: [
      offset(12),
      flip(),
      shift({ padding: 8 }),
      arrow({ element: arrowRef })
    ]
  });
  
  const arrowX = middlewareData.arrow?.x ?? 0;
  const arrowY = middlewareData.arrow?.y ?? 0;
  const staticSide = {
    top: 'bottom',
    right: 'left',
    bottom: 'top',
    left: 'right'
  }[placement.split('-')[0]];
  
  return (
    <>
      <button ref={refs.setReference}>{trigger}</button>
      <div ref={refs.setFloating} style={{ position: strategy, top: y, left: x }}>
        {content}
        <div
          ref={arrowRef}
          style={{
            position: 'absolute',
            left: arrowX,
            top: arrowY,
            [staticSide]: '-4px'
          }}
        />
      </div>
    </>
  );
}
```

## RTL Support

Handles right-to-left languages:

```javascript
useFloating({
  placement: 'bottom-start',  // Becomes 'bottom-end' in RTL
  middleware: [
    flip(),                    // Respects RTL direction
    shift()                    // Respects RTL direction
  ]
});
```

## Performance

- Uses `ResizeObserver` for efficient resize tracking
- Passive scroll listeners
- `requestAnimationFrame` option for smooth animations
- Batched position updates

## Notes

- Based on Floating UI (floatingui.com)
- Framework-agnostic core with React bindings
- Replaces deprecated Popper.js
- Handles complex overflow scenarios
