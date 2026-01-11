# viewer_core.js

## Overview
React hooks and state management utilities for the Sketchfab viewer application, including pagination, infinite scrolling, data normalization, and Redux-style store integration.

## File Status
- **Type**: Minified Sketchfab Webpack Bundle
- **Webpack Chunk ID**: 7380
- **Source Map**: `23072640c13bc2c244618d77d0e1cefa-v2.js.map`

## Key Components

### XuRc - Redux-style Reducer Hook
Custom hook for managing state with middleware support:
```javascript
const [state, dispatch] = useReducerWithMiddleware(
  initialState,
  setState,
  reducer,
  middlewares
);
```

### vAnt - Button Component
| Export | Description |
|--------|-------------|
| `Z` | Button component with multiple variants |

#### Button Props
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `text` | string | - | Button label |
| `subtext` | string | - | Secondary text |
| `icon` | node | - | Icon element |
| `size` | string | 'medium' | Size variant |
| `type` | string | 'primary' | Style variant |
| `loading` | bool | false | Show loading state |
| `success` | bool | false | Show success state |
| `progress` | number | - | Progress percentage |
| `disabled` | bool | false | Disable button |

#### Button Types
- `primary` - Main action button
- `secondary` - Secondary action
- `btn-loading` - Loading state
- `btn-disabled` - Disabled state

### lMO9 - Check/Success Icon
Spinner check icon component using macro templates.

### wExz - Loading Spinner
Sketchfab branded loading spinner with SVG animation.

### hk5G - Infinite Scroll Hook
```javascript
useInfiniteScroll(
  containerRef,    // Reference to scroll container
  loadMore,        // Function to load more items
  dependencies,    // Dependency array
  scrollElement    // Scroll target (default: window)
);
```

### BR/Y - Normalized State Hook
```javascript
const [state, dispatch] = useNormalizedState(
  reducer,
  initialState,
  schema,        // Normalizr schema
  middlewares
);
```

### pLUK - Single Execution Hook
Ensures async function executes only once at a time:
```javascript
const executeOnce = useSingleExecution(asyncFn);
```

### ajs0 - Paginated List Hook
```javascript
const {
  list,           // Current items
  loading,        // Loading state
  isLoading,      // Is currently loading
  hasNextPage,    // More items available
  hasPreviousPage,
  onLoadFirst,    // Load first page
  onLoadNext,     // Load next page
  onLoadPrevious, // Load previous page
  onReset,        // Reset list
  dispatch        // Dispatch actions
} = usePaginatedList(fetchFn, dependencies, options);
```

## Dependencies
- React (useRef, useEffect, useState, useCallback, useMemo, useContext)
- Redux (compose)
- Normalizr (normalize, denormalize)
- Lodash (isEqual, isEmpty, isFunction, debounce, throttle)
- Promise utilities
- Custom Sketchfab store

## Technical Details
- Middleware-enhanced dispatch
- Entity normalization for efficient updates
- Cursor-based pagination
- Debounced scroll detection
- Throttled resize handling
- Context-aware store integration

## Use Cases
1. Model list pagination
2. Comment threads loading
3. Search results infinite scroll
4. User profile data management
5. Collection browsing
6. Like/follow state tracking

## Notes
- Integrates with global Sketchfab entity store
- Supports schema-based normalization
- Handles race conditions in async operations
- Memory-efficient pagination with cursor support
- Reusable across different list views
