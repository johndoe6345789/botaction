# viewer_models.js

## Overview
Minified Sketchfab webpack chunk containing Nunjucks precompiled templates for the Sketchfab logo and branding SVG assets, including various logo variations and spinner animations.

## File Status
- **Type**: Minified JavaScript (Webpack Bundle)
- **Chunk ID**: 4197
- **Template Engine**: Nunjucks (precompiled)
- **Minified**: Yes
- **Source Map**: Available (referenced in file)

## Key Components

### Nunjucks Template: "front/macros/logo.jinja"
Precompiled SVG logo macros for server and client rendering.

### Exported Macros

#### `header_logo(headerStyle)`
Main header logo with style options:
- **Parameters**: `headerStyle` (default: "normal")
- **Transparent Mode**: White logo with hover effect for dark backgrounds
- **Features**:
  - Responsive sizing (121x30 default)
  - Hover state with color change
  - Link to homepage

#### `responsive_header_logo()`
Simplified responsive logo:
- Smaller dimensions (96x20)
- No style parameters
- Homepage link

#### `sketchfab_spinner()`
Loading spinner SVG animation:
- Three animated shapes
- Hexagonal spinner design
- CSS class-based animation
- Shape fills: shape1, shape2, shape3

#### `spinner_check(height, width)`
Success checkmark icon:
- Default size: 16x16
- Animated appearance
- Hover state styling

#### `logo(width, height, options)`
Full customizable logo SVG:

**Options Object**:
| Option | Default | Description |
|--------|---------|-------------|
| `brand` | true | Include text logo |
| `color` | #555555 | Text color |
| `logo_color` | #FFFFFF | Icon fill |
| `circle_color` | #1CAAD9 | Circle outline |

**Features**:
- Full "Sketchfab" text when `brand: true`
- Icon-only mode when `brand: false`
- ViewBox: 0 0 121 25 (with text) or 0 0 25 25 (icon only)
- Multiple color customization points

#### `store_logo(width, height, options)`
Sketchfab Store branded logo:

**Options Object**:
| Option | Default | Description |
|--------|---------|-------------|
| `color` | #FFFFFF | All elements color |

**Content**:
- Full "Sketchfab Store" text
- Icon with store branding
- Single color mode for versatility

### Static Asset Exports

**Module "BlOJ"**:
- White logo SVG path
- File: `bf6f7388c48a8b89e44ea4d69f6b6dfb-v2.svg`

**Module "QWE0"**:
- Standard logo SVG path
- File: `0eb04d2256c1b2f30c132e3257f4b807-v2.svg`

## Dependencies
- Nunjucks runtime (precompiled)
- Webpack asset handling
- SVG rendering support

## Technical Details
- Precompiled for performance (no runtime compilation)
- Server-side rendering compatible
- Dynamic color customization
- Accessible (includes alt text and aria labels)
- CDN-served static assets

## Use Cases
1. Header branding
2. Loading states (spinner)
3. Footer logos
4. Marketing materials
5. Print/export watermarks

## Notes
- Core branding assets for Sketchfab
- Multiple color schemes supported
- Performance optimized (precompiled)
- Maintains brand consistency
- SVG ensures scalability
