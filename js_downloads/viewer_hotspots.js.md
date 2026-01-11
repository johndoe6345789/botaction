# viewer_hotspots.js

## Overview
Minified Sketchfab webpack chunk containing CSS module class name mappings for the entire Sketchfab UI component library. This file provides the CSS-in-JS class name obfuscation layer.

## File Status
- **Type**: Minified JavaScript (Webpack Bundle)
- **Chunk ID**: 2852
- **Minified**: Yes
- **Source Map**: Available (referenced in file)

## Key Components

### CSS Module Class Mappings (~280+ classes)
This file contains obfuscated CSS class names for styling consistency and conflict avoidance.

**UI Component Categories**:

#### Tags & Lists
- `view`, `list`, `item`, `tagItem`, `icon`

#### Thumbnails
- `thumbnail`, `--loading`

#### Content Containers
- `title`, `text`, `imageContainer`

#### Messages & Alerts
- `message`, `error`, `warning`

#### Navigation
- `header`, `logo`, `tabs`, `breadcrumbs`

#### Forms
- `input`, `checkbox`, `switch`, `textarea`

#### Cards
- `modelCard`, `userCard`, `categoryCard`

#### Tables
- `head`, `row`, `cell`, `body`

#### Popups & Modals
- `popup`, `modal`, `overlay`

#### Carousels & Sliders
- `carousel`, `rail`, `item`, `bullets`

#### Buttons
- `primary`, `secondary`, `ghost`, `disabled`

#### Icons
- Font Awesome classes (`fa-*`)
- Sketchfab custom icons (`skfb-icon-arvr`, `skfb-icon-model`, etc.)

#### Profile Components
- `avatar`, `username`, `stats`, `skills`

#### Settings & Forms
- `form`, `input`, `select`, `dropdown`

#### Downloads
- `downloadsMini`, `progressIcon`, `downloaded`

#### Grid Layouts
- `col-1` through `col-12`

#### Loading States
- Skeleton loaders
- Progress indicators

#### Tooltips & Popovers
- `tooltip`, `popover`, `arrow`

#### Organization Components
- Project components
- Team management
- Transfer popups

## Dependencies
- CSS Modules (webpack css-loader)
- PostCSS (class name transformation)

## Technical Details
- Hash-based class name obfuscation
- Prevents CSS class name collisions
- Enables tree-shaking of unused styles
- Supports theming through CSS variables

## Use Cases
1. Component styling across the Sketchfab platform
2. Theme customization
3. Responsive design implementation
4. UI state representation (loading, error, disabled)

## Notes
- Core styling infrastructure for Sketchfab UI
- Class names are production-obfuscated
- Maps human-readable names to minified hashes
- Essential for consistent visual presentation
