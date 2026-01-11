# viewer_materials.js

## Overview
Minified Sketchfab webpack chunk containing the comprehensive design system theme configuration with CSS custom properties (variables) for colors, typography, spacing, and component styling.

## File Status
- **Type**: Minified JavaScript (Webpack Bundle)
- **Chunk ID**: 6952
- **Minified**: Yes
- **Source Map**: Available (referenced in file)

## Key Components

### Module "vT00" - Accessibility Theme
Dark/high-contrast accessible color scheme:

**Primary Colors**:
- `--color-primary-25`: #f7f9fa
- `--color-primary-100`: #006c9a
- `--color-primary-500`: #013349

**Secondary Colors** (Pink/Magenta):
- `--color-secondary-300`: #b51b54
- `--color-secondary-500`: #740930

### Module "oNdp" - Default Theme
Standard Sketchfab color palette:

**Color Categories**:

| Category | Range | Usage |
|----------|-------|-------|
| Primary (Cyan) | 25-900 | Brand colors, links |
| Secondary (Pink) | 25-800 | Accents, CTAs |
| Neutral | 0-1000 | Text, backgrounds |
| Success (Green) | 25-800 | Confirmations |
| Warning (Orange) | 25-800 | Alerts |
| Error (Red) | 25-800 | Errors |
| Editor | 0-1000 | 3D editor UI |

**Brand Colors**:
- Sketchfab: #1caad9
- Epic: #0b0b0b
- Facebook: #3a589a
- Twitter: #1d9bf0
- Apple: #050708

**User Plan Colors**:
- Pro: #00aad8
- Premium: #007395
- Enterprise: #222222
- Staff: #ff9e3a
- Master: #28cca7

**Alpha Variants**:
- Black alpha (10-90%)
- White alpha (10-90%)
- Primary alpha (10-90%)

### Module "AHX3" - Layout Dimensions
Spacing and sizing constants:

**Website Layout**:
- `website-top-height`: 60px
- `website-max-width`: 2000px
- `website-fullscreen-padding`: 30px

**Editor Dimensions**:
- `editor-header-height`: 55px
- `editor-panel-width`: 320px
- `editor-scrollbar-width`: 10px

**Responsive Breakpoints**:
- x-small: 576px
- small: 768px
- medium: 1024px
- large: 1440px
- x-large: 1920px

### CSS Module Exports (60+ modules)
Component-specific class mappings for:

**UI Components**:
- Buttons (store, primary, danger)
- Badges (neutral, success, primary)
- Cards (thumbnail, darken overlay)
- Tables (container, column labels)
- Forms (inputs, checkboxes, switches)
- Modals (transfer popups, plan subscribe)
- Navigation (tabs, breadcrumbs, menus)
- Lists (search results, user lists)

**Feature Components**:
- Analytics graphs & filters
- Project/folder pickers
- User profiles & avatars
- Download managers
- Settings panels
- Workflow steps

## Dependencies
- CSS Custom Properties
- CSS Modules (webpack)
- PostCSS

## Technical Details
- Centralized theme system
- Dark mode support
- Accessibility considerations
- Component isolation via CSS modules
- Gradient and alpha support

## Use Cases
1. Platform-wide theming
2. Component styling
3. Responsive design
4. Accessibility compliance
5. Brand consistency

## Notes
- Foundation of Sketchfab's visual design
- Supports multiple color themes
- Designed for maintainability
- Follows design token patterns
