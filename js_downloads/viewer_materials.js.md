# viewer_materials.js

## Overview

This file contains **CSS design system variables and theme definitions** - NOT 3D material handling. It defines Sketchfab's complete design token system including colors, spacing, and breakpoints.

## File Information

- **Status**: Active webpack bundle
- **Size**: ~68KB (minified)
- **Type**: Design system / CSS variables
- **Format**: CSS-in-JS module exports

## Design Token Categories

### 1. Fab Theme Colors (`vT00`)

Epic Games' Fab marketplace colors:

```javascript
const FabColors = {
  primary: {
    main: '#1a73e8',
    light: '#4285f4',
    dark: '#1557b0',
    contrast: '#ffffff'
  },
  secondary: {
    main: '#5f6368',
    light: '#80868b',
    dark: '#3c4043',
    contrast: '#ffffff'
  }
};
```

### 2. Sketchfab Theme Colors (`oNdp`)

Sketchfab brand colors:

```javascript
const SketchfabColors = {
  primary: {
    50: '#e3f2fd',
    100: '#bbdefb',
    200: '#90caf9',
    300: '#64b5f6',
    400: '#42a5f5',
    500: '#1d7df6',  // Main brand blue
    600: '#1e88e5',
    700: '#1976d2',
    800: '#1565c0',
    900: '#0d47a1'
  }
};
```

### 3. Semantic Colors

```javascript
const SemanticColors = {
  success: {
    main: '#4caf50',
    light: '#81c784',
    dark: '#388e3c',
    background: '#e8f5e9'
  },
  warning: {
    main: '#ff9800',
    light: '#ffb74d',
    dark: '#f57c00',
    background: '#fff3e0'
  },
  error: {
    main: '#f44336',
    light: '#e57373',
    dark: '#d32f2f',
    background: '#ffebee'
  },
  info: {
    main: '#2196f3',
    light: '#64b5f6',
    dark: '#1976d2',
    background: '#e3f2fd'
  }
};
```

### 4. Neutral Colors

```javascript
const NeutralColors = {
  white: '#ffffff',
  black: '#000000',
  gray: {
    50: '#fafafa',
    100: '#f5f5f5',
    200: '#eeeeee',
    300: '#e0e0e0',
    400: '#bdbdbd',
    500: '#9e9e9e',
    600: '#757575',
    700: '#616161',
    800: '#424242',
    900: '#212121'
  }
};
```

### 5. Brand Colors

```javascript
const BrandColors = {
  sketchfab: '#1d7df6',
  epic: '#2a2a2a',
  facebook: '#3b5998',
  twitter: '#1da1f2',
  google: '#db4437',
  apple: '#000000',
  instagram: '#c13584',
  youtube: '#ff0000'
};
```

### 6. Layout Dimensions (`AHX3`)

```javascript
const Layout = {
  header: {
    height: 64,
    heightMobile: 56
  },
  sidebar: {
    width: 240,
    collapsedWidth: 64
  },
  container: {
    maxWidth: 1440,
    padding: 24
  }
};
```

### 7. Breakpoints

```javascript
const Breakpoints = {
  xs: 0,
  sm: 600,
  md: 900,
  lg: 1200,
  xl: 1536
};

// Media queries
const MediaQueries = {
  mobile: '@media (max-width: 599px)',
  tablet: '@media (min-width: 600px) and (max-width: 899px)',
  desktop: '@media (min-width: 900px)',
  wide: '@media (min-width: 1200px)'
};
```

### 8. Spacing Scale

```javascript
const Spacing = {
  0: '0',
  1: '4px',
  2: '8px',
  3: '12px',
  4: '16px',
  5: '20px',
  6: '24px',
  8: '32px',
  10: '40px',
  12: '48px',
  16: '64px'
};
```

### 9. Typography

```javascript
const Typography = {
  fontFamily: {
    primary: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
    mono: "'Fira Code', 'Consolas', monospace"
  },
  fontSize: {
    xs: '12px',
    sm: '14px',
    base: '16px',
    lg: '18px',
    xl: '20px',
    '2xl': '24px',
    '3xl': '30px',
    '4xl': '36px'
  },
  fontWeight: {
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700
  },
  lineHeight: {
    tight: 1.25,
    normal: 1.5,
    relaxed: 1.75
  }
};
```

## CSS Module Exports

The file exports CSS class name mappings for various components:

```javascript
// Example CSS Module exports
export const modelCard = {
  container: 'model-card_container_abc123',
  thumbnail: 'model-card_thumbnail_def456',
  title: 'model-card_title_ghi789',
  author: 'model-card_author_jkl012'
};

export const button = {
  base: 'button_base_mno345',
  primary: 'button_primary_pqr678',
  secondary: 'button_secondary_stu901'
};
```

## Component Theme Variables

### Button Theming

```javascript
const ButtonTheme = {
  primary: {
    background: 'var(--color-primary-500)',
    color: 'var(--color-white)',
    hoverBackground: 'var(--color-primary-600)',
    activeBackground: 'var(--color-primary-700)'
  },
  secondary: {
    background: 'transparent',
    color: 'var(--color-gray-700)',
    border: '1px solid var(--color-gray-300)',
    hoverBackground: 'var(--color-gray-100)'
  }
};
```

### Badge Theming

```javascript
const BadgeTheme = {
  success: {
    background: 'var(--color-success-background)',
    color: 'var(--color-success-dark)'
  },
  warning: {
    background: 'var(--color-warning-background)',
    color: 'var(--color-warning-dark)'
  }
};
```

## Usage in Components

### CSS Variables

```css
:root {
  --color-primary-500: #1d7df6;
  --color-gray-100: #f5f5f5;
  --spacing-4: 16px;
  --font-size-base: 16px;
}

.button {
  background: var(--color-primary-500);
  padding: var(--spacing-4);
  font-size: var(--font-size-base);
}
```

### JavaScript Access

```javascript
import { SketchfabColors, Spacing, Breakpoints } from './viewer_materials';

const StyledComponent = styled.div`
  background: ${SketchfabColors.primary[500]};
  padding: ${Spacing[4]};
  
  @media (min-width: ${Breakpoints.md}px) {
    padding: ${Spacing[6]};
  }
`;
```

## Dark Theme Support

```javascript
const DarkTheme = {
  background: {
    primary: '#121212',
    secondary: '#1e1e1e',
    tertiary: '#2d2d2d'
  },
  text: {
    primary: '#ffffff',
    secondary: 'rgba(255, 255, 255, 0.7)',
    disabled: 'rgba(255, 255, 255, 0.5)'
  }
};
```

## Notes

- Filename is misleading - contains design system, not 3D materials
- Complete design token system for Sketchfab web app
- Supports both Sketchfab and Fab brands
- CSS variables enable runtime theming
- CSS Modules provide scoped class names
