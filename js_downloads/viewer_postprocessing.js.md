# viewer_postprocessing.js

## Overview
Minified Sketchfab webpack chunk containing a comprehensive React component library implementing the Sketchfab Design System (DS). Includes UI primitives, form components, navigation, modals, and more.

## File Status
- **Type**: Minified JavaScript (Webpack Bundle)
- **Chunk ID**: 674
- **Framework**: React 18
- **Minified**: Yes
- **Source Map**: Available (referenced in file)

## Key Components

### Layout Components

#### Avatar (`UlaC`)
- Props: `as`, `alt`, `image`, `onLoad`, `size`, `shape`, `outlined`
- Sizes: xs, sm, md, lg, xl, 2xl
- Shapes: round, square
- Loading state with transition

#### AvatarGroup (`rYMG`)
- Props: `max`, `size`, `total`, `onAdd`, `shape`
- Shows overflow count (+N)
- Add button option

#### Container (`HSdz`)
- Props: `size`, `align`
- Sizes: xs, sm, md, lg, xl, 2xl
- Alignment: center, left, right

#### Stack (`23oU`)
- Props: `align`, `justify`, `direction`, `wrap`, `gap`, `block`
- Flexbox layout component
- Gap levels: 1-5

### Form Components

#### Button (`u8Ql`)
- Variants: filled, outlined, ghost
- Intents: primary, neutral, destructive
- Sizes: xs, sm, md, lg
- Icon-only mode, rounded option

#### Checkbox (`UT7Y`)
- Props: `checked`, `indeterminate`, `disabled`, `onChange`
- Controlled and uncontrolled modes

#### Radio (`+JRd`) & RadioGroup (`X0PE`)
- Grouped radio buttons
- Context-based state sharing

#### TextInput (`pmwb`)
- Props: `error`, `left`, `right`, `disabled`, `focused`
- Input container with adornments

#### FormField (`FtXw`)
- Props: `label`, `hint`, `error`, `hideLabel`
- Wraps inputs with labels and hints

### Navigation Components

#### Breadcrumb (`MibD`)
- Props: `separator`, `label`
- BreadcrumbItem children

#### Tab & TabList (`+RMS`, `yYR9`)
- Variants: underlined, ghost, pills
- Directions: horizontal, vertical
- Sizes: sm, md

#### Menu (`MXxw`)
- Props: `value`, `onChange`, `keepOpen`
- MenuItem, MenuGroup children
- Keyboard navigation

### Feedback Components

#### Badge (`LolH`)
- Props: `intent`, `size`, `onDelete`
- Intents: neutral, primary, error, warning, success

#### LinearProgress (`Pgsw`)
- Props: `value`, `min`, `max`, `indeterminate`

#### CircularProgress (`bpiE`)
- Props: `value`, `size`, `semi`, `indeterminate`
- Semi-circle mode available

#### Skeleton (`rcFI`)
- Props: `width`, `height`, `shape`, `transparent`
- Loading placeholder

### Overlay Components

#### Modal (`GGLo`)
- Props: `open`, `onClose`, `size`, `noOverlay`
- ModalHeader, ModalContent, ModalActions

#### Drawer (`75Et`)
- Props: `open`, `placement`, `noOverlay`
- Placements: top, right, bottom, left

#### Dropdown (`37pN`)
- DropdownProvider, DropdownTrigger, DropdownContent
- Focus trap and click-outside handling

#### Tooltip (`/sMP`)
- Props: `title`, `content`, `placement`
- Hover and focus activation

### Data Display

#### Card (`nGYT`)
- CardHeader, CardThumbnail, CardThumbnailGrid
- Props: `outlined`, `elevation`, `selected`

#### List (`yFLE`)
- ListItem with `left`, `right` props
- ListGroup for sectioning

#### Grid (`sSWf`)
- Props: `gap`, `minColWidth`
- Auto-responsive columns

#### Typography (`yjeX`)
- Variants: text, display
- Sizes: xs, sm, md, lg, xl
- Weights: regular, medium, semibold, bold

### Select Components

#### Select (`EH2Y`)
- Searchable, creatable options
- GroupBy support
- Virtual scrolling

#### MultiSelect (`25LF`)
- Badge list display
- Select all option

#### TreeSelect (`87QK`)
- Hierarchical navigation
- Parent/child navigation

### Utilities

#### Collapse (`x9Ta`)
- Animated height transition
- `keepMounted` option

#### Divider (`Zlqx`)
- Horizontal separator
- Content wrapping

#### Link (`QBpD`)
- Props: `intent`, `underlined`, `disabled`

#### StateButton (`b/Jl`)
- Promise-based loading state
- Success/error feedback

## Dependencies
- React 18
- Floating UI (positioning)
- CSS Modules

## Technical Details
- Forward ref support throughout
- CSS-in-JS with CSS Modules
- Accessibility (ARIA) compliance
- Keyboard navigation
- Focus management

## Use Cases
1. Building Sketchfab UI
2. Consistent component library
3. Accessible interfaces
4. Design system implementation

## Notes
- Comprehensive design system
- Production-ready components
- Performance optimized
- Fully typed (TypeScript compatible)
