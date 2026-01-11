# viewer_models.js

## Overview

This file contains **Nunjucks logo templates** - server-side rendered templates for Sketchfab's logo in various formats and contexts. NOT 3D model management as the filename suggests.

## File Information

- **Status**: Active webpack bundle
- **Size**: ~15KB (minified)
- **Type**: Nunjucks templates
- **Framework**: Nunjucks

## Logo Templates

### Main Logo

```html
{% macro logo(options) %}
<a href="{{ options.href or '/' }}" 
   class="logo {{ options.className }}"
   aria-label="Sketchfab">
   
  {% if options.variant == 'full' %}
    {# Full logo with wordmark #}
    <svg class="logo__full" viewBox="0 0 200 40">
      {# Logo SVG paths #}
      <path class="logo__mark" d="..."/>
      <path class="logo__wordmark" d="Sketchfab"/>
    </svg>
    
  {% elif options.variant == 'mark' %}
    {# Logo mark only #}
    <svg class="logo__mark-only" viewBox="0 0 40 40">
      <path d="..."/>
    </svg>
    
  {% elif options.variant == 'wordmark' %}
    {# Text only #}
    <svg class="logo__wordmark-only" viewBox="0 0 160 40">
      <path d="Sketchfab"/>
    </svg>
    
  {% endif %}
</a>
{% endmacro %}
```

### Logo Variants

```javascript
const logoVariants = {
  full: {
    name: 'Full Logo',
    width: 200,
    height: 40,
    description: 'Logo mark + wordmark'
  },
  mark: {
    name: 'Logo Mark',
    width: 40,
    height: 40,
    description: 'Icon only'
  },
  wordmark: {
    name: 'Wordmark',
    width: 160,
    height: 40,
    description: 'Text only'
  }
};
```

### Color Variants

```html
{% macro logo(options) %}
<a href="/" class="logo logo--{{ options.color or 'default' }}">
  <svg>
    <!-- Logo paths -->
  </svg>
</a>
{% endmacro %}

{# Color options:
   - default: Blue (#1caad9)
   - white: White on dark backgrounds
   - black: Black for light backgrounds
   - mono: Single color (inherits)
#}
```

### Responsive Logo

```html
{# Shows mark on mobile, full on desktop #}
{% macro responsiveLogo() %}
<a href="/" class="logo">
  <svg class="logo__mark-only d-md-none" viewBox="0 0 40 40">
    <!-- Mark only -->
  </svg>
  <svg class="logo__full d-none d-md-block" viewBox="0 0 200 40">
    <!-- Full logo -->
  </svg>
</a>
{% endmacro %}
```

## Logo Contexts

### Header Logo

```html
{% macro headerLogo() %}
{{ logo({
  variant: 'full',
  color: 'default',
  href: '/',
  className: 'header__logo'
}) }}
{% endmacro %}
```

### Footer Logo

```html
{% macro footerLogo() %}
{{ logo({
  variant: 'full',
  color: 'white',
  href: '/',
  className: 'footer__logo'
}) }}
{% endmacro %}
```

### Loading Screen Logo

```html
{% macro loadingLogo() %}
<div class="loading-screen__logo">
  {{ logo({
    variant: 'mark',
    color: 'default',
    className: 'loading-screen__logo-mark'
  }) }}
  <div class="loading-screen__spinner"></div>
</div>
{% endmacro %}
```

### Email Logo

```html
{% macro emailLogo() %}
{# Inline styles for email compatibility #}
<a href="https://sketchfab.com" style="display: inline-block;">
  <img 
    src="https://static.sketchfab.com/email/logo.png" 
    alt="Sketchfab"
    width="150"
    height="30"
    style="display: block;"
  />
</a>
{% endmacro %}
```

### Watermark

```html
{% macro watermark(options) %}
<a href="https://sketchfab.com" 
   class="watermark {{ options.position or 'bottom-right' }}"
   target="_blank"
   rel="noopener">
  <svg class="watermark__logo" viewBox="0 0 100 20">
    <text>on</text>
    <path d="..."/> {# Sketchfab mark #}
    <text>Sketchfab</text>
  </svg>
</a>
{% endmacro %}

{# Position options: top-left, top-right, bottom-left, bottom-right #}
```

## SVG Logo Paths

```javascript
// Logo mark paths (simplified)
const logoMark = `
  M20 0
  L40 20
  L20 40
  L0 20
  Z
  M20 10
  L30 20
  L20 30
  L10 20
  Z
`;

// Wordmark paths
const wordmark = `
  S: M10 0 ...
  k: M25 0 ...
  e: M35 0 ...
  t: M45 0 ...
  c: M55 0 ...
  h: M65 0 ...
  f: M80 0 ...
  a: M90 0 ...
  b: M100 0 ...
`;
```

## Logo Animation

```html
{% macro animatedLogo() %}
<div class="animated-logo">
  <svg viewBox="0 0 40 40" class="animated-logo__svg">
    <path 
      class="animated-logo__outer" 
      d="M20 0 L40 20 L20 40 L0 20 Z">
      <animate 
        attributeName="stroke-dashoffset" 
        from="100" 
        to="0" 
        dur="1s" 
        fill="freeze" 
      />
    </path>
    <path 
      class="animated-logo__inner" 
      d="M20 10 L30 20 L20 30 L10 20 Z">
      <animate 
        attributeName="opacity" 
        from="0" 
        to="1" 
        dur="0.5s" 
        begin="0.5s" 
        fill="freeze" 
      />
    </path>
  </svg>
</div>
{% endmacro %}
```

## Usage

```javascript
import nunjucks from 'nunjucks';

// Render header logo
const headerHtml = nunjucks.render('partials/logo.njk', {
  variant: 'full',
  color: 'default'
});

// Render footer logo
const footerHtml = nunjucks.render('partials/logo.njk', {
  variant: 'full',
  color: 'white'
});
```

## CSS Classes

```css
/* Logo base */
.logo { }
.logo__full { }
.logo__mark-only { }
.logo__wordmark-only { }

/* Color variants */
.logo--default { fill: #1caad9; }
.logo--white { fill: #ffffff; }
.logo--black { fill: #1a1a1a; }
.logo--mono { fill: currentColor; }

/* Contexts */
.header__logo { }
.footer__logo { }
.loading-screen__logo { }
.watermark { }

/* Animation */
.animated-logo { }
.animated-logo__outer { }
.animated-logo__inner { }
```

## Notes

- Filename is misleading - contains logo templates, not model management
- SVG-based logo in multiple variants
- Color variants for different backgrounds
- Responsive logo (mark on mobile, full on desktop)
- Animated logo for loading states
- Email-compatible image version
