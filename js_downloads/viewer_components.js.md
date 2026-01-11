# viewer_components.js

## Overview
Minified Sketchfab webpack chunk containing reusable UI components including collection displays, star ratings, tabs, icon components with gradients, and keyboard event handling utilities.

## File Status
- **Type**: Minified JavaScript (Webpack Bundle)
- **Chunk ID**: 9802
- **Minified**: Yes
- **Source Map**: Available (referenced in file)

## Key Components

### Module "pDOP" - Collection Name
Display component for collection links:

```jsx
<CollectionName collection={collection} />
```

**Features**:
- Link to collection URL
- Stop event propagation on click
- Schema.org itemProp="name"

### Module "y7HB" - Names List
Display list of names with "and X others":

**Props**:
- `totalCount` - Total number of items
- `names` - Array of name components
- `othersHref` - Link for "others"
- `onOtherClick` - Click handler
- `maxDisplay` - Max names shown (default: 3)

**Output Examples**:
- "Alice"
- "Alice, Bob and Charlie"
- "Alice, Bob and 5 others"

### Module "rv44" - Star Rating
Interactive 5-star rating component:

**Star Component (v)**
Individual SVG star:
- Uses mask for partial fill
- Customizable color
- Percentage-based fill

**StarRating Class (h)**

**Props**:
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `value` | number | - | Rating value (0-5) |
| `color` | string | - | Star fill color |
| `size` | string | "medium" | small/medium/large |
| `onChange` | function | noop | Click handler |
| `identifier` | string | "skfb" | Unique ID prefix |

**Sizes**:
- small: 10px
- medium: 16px
- large: 20px

**Features**:
- Partial star fill (percentage)
- Interactive mode with onClick
- Accessible with refs

### Module "AFjX" - Tabs
Tab navigation component:

**Props**:
- `tabs` - Array of tab objects
- `selectedTabIndex` - Active tab
- `onSelectTab` - Selection handler
- `className` - Additional classes
- `headerProps` - Header attributes

**Tab Object**:
```javascript
{
  title: string,
  isDisabled: boolean,
  render: () => ReactNode
}
```

**Features**:
- Keyboard accessible (tabIndex)
- ARIA attributes
- Disabled state support
- Custom header props

### Module "ESrx" - Gradient Icons
SVG icons with gradient fills:

**Available Icons**:
1. `MB` - 3D Model icon (cube with sparkle)
2. `HX` - Image/gallery icon
3. `VP` - Brush/paint icon
4. `pH` - Table/grid icon
5. `vV` - Airplane/travel icon

**Features**:
- Dynamic gradient IDs (useId)
- CSS custom properties for colors:
  - `--icon-stroke`
  - `--icon-fill`
  - `--icon-gradient-start`
  - `--icon-gradient-end`
- SVG linearGradient

**Usage**:
```jsx
<ModelIcon style={{
  '--icon-gradient-start': '#ff0000',
  '--icon-gradient-end': '#0000ff'
}} />
```

### Module "/7yb" - Keyboard Hook
Throttled keyboard event handler:

**useKeyPress Hook**:
```javascript
useKeyPress(key, callback, eventType = 'keypress')
```

**Features**:
- Throttled (1000ms) via lodash
- Configurable event type
- Cleanup on unmount
- Global window listener

## Dependencies
- React (hooks, classes, refs)
- Lodash (throttle, omit)
- SVG utilities
- CSS modules

## Technical Details
- Class and functional components
- SVG masking for partial stars
- Dynamic gradient IDs
- Keyboard event optimization
- ARIA accessibility

## Use Cases
1. Collection displays
2. Rating systems
3. Tabbed interfaces
4. Icon systems
5. Keyboard shortcuts

## Notes
- Reusable UI primitives
- Accessibility-focused
- CSS custom property theming
- React 18 compatible (useId)
