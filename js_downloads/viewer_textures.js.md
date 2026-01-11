# viewer_textures.js

## Overview
Minified Sketchfab webpack chunk containing UI components for 360-degree model preview, responsive grid layouts, and model card features (staff picks, restrictions).

## File Status
- **Type**: Minified JavaScript (Webpack Bundle)
- **Chunk ID**: 9799
- **Minified**: Yes
- **Source Map**: Available (referenced in file)

## Key Components

### Module "nnpx" - 360° Model Preview
Interactive 360-degree image preview component:

**Class: Model360Preview**

**Props**:
| Prop | Default | Description |
|------|---------|-------------|
| `color` | "" | Loading bar color |
| `previewOnDrag` | true | Enable drag interaction |
| `targetHeight` | 400 | Target image height |
| `modelUid` | required | Model identifier |

**State**:
- `isVisible` - Preview visibility
- `image` - Loaded image data (width, height)
- `containerWidth/Height` - Container dimensions
- `loadingPercent` - Load progress (0-1)
- `cursorX` - Current cursor position
- `startCursorX` - Drag start position

**Methods**:
- `onStart()` - Initialize drag/hover
- `onMove(event)` - Handle cursor movement
- `onEnd()` - Cleanup and hide
- `isActive()` - Check if visible and loaded
- `loadPreview()` - Fetch model preview images
- `show(position)` - Display preview

**Features**:
- Debounced image loading (500ms)
- 15-frame sprite sheet animation
- Touch and mouse support
- Progress indicator
- Automatic size fitting

### Module "AhsD" - Grid Item
Responsive grid item wrapper:

**Component: GridItem**

**Props**:
- `columns` - Number of columns to span
- `children` - Content
- `className` - Additional classes

**CSS Classes**:
- `c-grid__item`
- `--columns-{n}` - Column span modifier

### Module "hpsH" - Model Grid
Paginated grid layout for model cards:

**Component: ModelGrid**

**Props**:
| Prop | Default | Description |
|------|---------|-------------|
| `cards` | required | Card components array |
| `onLoadPrevious` | - | Previous page callback |
| `onLoadNext` | - | Next page callback |
| `scrollableElement` | window | Scroll container |
| `gridSize` | "normal" | Grid density |
| `loading` | "none" | Loading state |
| `isLoading` | false | Loading flag |
| `hasPreviousPage` | false | Has previous |
| `hasNextPage` | false | Has next |
| `maxAutoLoadedPages` | 3 | Auto-load limit |
| `emptyState` | null | Empty content |

**Features**:
- Infinite scroll with intersection observer
- Auto-load with page limit
- Previous/Next buttons
- Empty state handling
- Schema.org itemProp support

### Module "QFI+" - Model Flags
Model status indicator badges:

**Component: ModelFlags**

**Props**:
- `model` - Model data
- `withStaffpickFlag` - Show staff pick (default: true)
- `withStaffpickLink` - Link to staff picks (default: false)
- `withRestrictedFlag` - Show restricted (default: true)
- `displayRecentlyStaffpicked` - Highlight new picks

**Badges**:
- **Staff Pick**: Award badge with optional link
- **Restricted**: Link to content policy

**Schema.org**:
- `itemProp="award"` for staff picks

## Dependencies
- React (Component class, memo)
- Lodash (debounce)
- Promise library
- Intersection Observer API

## Technical Details
- Class-based 360 preview (lifecycle methods)
- Functional grid components
- Debounced API calls
- Sprite sheet animation technique
- Schema.org structured data

## Use Cases
1. Model card 360° previews
2. Responsive model grids
3. Staff pick highlighting
4. Restricted content warnings
5. Infinite scroll galleries

## Notes
- 360 preview uses 15-frame sprite sheets
- Grid supports various layouts
- Flags follow Sketchfab content policy
- Optimized for large model lists
