# swagger-ui-standalone-preset.js

## Overview

This file contains the **Swagger UI Standalone Preset** - a configuration preset that adds the standalone layout and additional features to the base Swagger UI bundle.

## File Information

- **Status**: Active library companion
- **Size**: ~45KB (minified)
- **Type**: Swagger UI preset/plugin
- **Dependency**: Requires swagger-ui-bundle.js

## Purpose

The Standalone Preset adds:

1. **StandaloneLayout** - Full-page layout with navigation
2. **TopBar** - Header with search and URL input
3. **Filter Plugin** - Operation filtering by tag/text
4. **Custom Styling** - Standalone appearance

## Usage

```javascript
import SwaggerUI from 'swagger-ui-bundle';
import SwaggerUIStandalonePreset from 'swagger-ui-standalone-preset';

const ui = SwaggerUI({
  url: '/api/swagger.json',
  dom_id: '#swagger-ui',
  
  // Use standalone preset
  presets: [
    SwaggerUI.presets.apis,
    SwaggerUIStandalonePreset
  ],
  
  // Enable standalone layout
  layout: 'StandaloneLayout'
});
```

## Standalone Layout Components

### TopBar

```javascript
// TopBar component structure
<div class="topbar">
  <div class="wrapper">
    <a class="link" href="#">
      <img class="logo" src="logo.png" alt="Logo" />
    </a>
    
    <form class="download-url-wrapper">
      <input 
        class="download-url-input" 
        type="text" 
        placeholder="Enter OpenAPI spec URL"
      />
      <button class="download-url-button">
        Explore
      </button>
    </form>
  </div>
</div>
```

### Filter Bar

```javascript
// Filter operations by text
<div class="filter-container">
  <input 
    class="filter"
    placeholder="Filter by tag"
    type="text"
  />
</div>

// Filter state
const filterConfig = {
  filter: true,                    // Enable filter input
  filterMatchType: 'contains',     // 'contains' | 'startsWith'
  caseSensitive: false
};
```

### Standalone Layout Structure

```html
<div class="swagger-ui">
  <!-- Top navigation bar -->
  <section class="topbar">
    <!-- Logo, URL input, explore button -->
  </section>
  
  <!-- Main content area -->
  <div class="wrapper">
    <!-- Filter input -->
    <section class="filter-container"></section>
    
    <!-- API info header -->
    <section class="information-container"></section>
    
    <!-- Servers selector -->
    <section class="servers-container"></section>
    
    <!-- Authentication buttons -->
    <section class="auth-wrapper"></section>
    
    <!-- Operations grouped by tag -->
    <section class="operations-container"></section>
    
    <!-- Schema models -->
    <section class="models-container"></section>
  </div>
</div>
```

## Configuration with Standalone

```javascript
const ui = SwaggerUI({
  url: '/api/swagger.json',
  dom_id: '#swagger-ui',
  
  presets: [
    SwaggerUI.presets.apis,
    SwaggerUIStandalonePreset
  ],
  
  // Standalone-specific options
  layout: 'StandaloneLayout',
  
  // TopBar customization
  plugins: [
    // Custom logo plugin
    () => ({
      components: {
        Logo: () => <img src="/custom-logo.png" alt="My API" />
      }
    })
  ],
  
  // Filter configuration
  filter: true,
  
  // Doc expansion
  docExpansion: 'list',  // 'none' | 'list' | 'full'
  
  // Deep linking for sharing
  deepLinking: true
});
```

## Customizing Standalone Layout

### Custom TopBar

```javascript
const CustomTopBarPlugin = () => ({
  wrapComponents: {
    Topbar: (Original, { React }) => (props) => (
      <div className="custom-topbar">
        <div className="custom-topbar__logo">
          <img src="/my-logo.png" alt="My API" />
        </div>
        <div className="custom-topbar__title">
          <h1>My API Documentation</h1>
        </div>
        {/* Keep URL input from original */}
        <Original {...props} />
      </div>
    )
  }
});

const ui = SwaggerUI({
  plugins: [CustomTopBarPlugin],
  // ...
});
```

### Hide TopBar

```javascript
const ui = SwaggerUI({
  layout: 'BaseLayout',  // Use BaseLayout instead of StandaloneLayout
  // ...
});

// Or with CSS
/* Hide topbar */
.swagger-ui .topbar {
  display: none;
}
```

### Custom Standalone CSS

```css
/* Standalone layout customization */
.swagger-ui {
  max-width: 1200px;
  margin: 0 auto;
}

.swagger-ui .topbar {
  background-color: #1a1a1a;
  padding: 10px 0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.swagger-ui .topbar .download-url-wrapper {
  display: flex;
  gap: 8px;
}

.swagger-ui .topbar .download-url-input {
  flex: 1;
  padding: 8px 12px;
  border-radius: 4px;
  border: 1px solid #444;
  background: #2d2d2d;
  color: #fff;
}

.swagger-ui .topbar .download-url-button {
  background: #1caad9;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.swagger-ui .filter-container {
  padding: 20px;
  background: #f8f8f8;
  border-bottom: 1px solid #e0e0e0;
}

.swagger-ui .filter {
  width: 100%;
  max-width: 400px;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
}
```

## Multiple Specs Support

```javascript
const ui = SwaggerUI({
  // Multiple API specs
  urls: [
    { url: '/api/v3/swagger.json', name: 'V3 API' },
    { url: '/api/v2/swagger.json', name: 'V2 API (Deprecated)' }
  ],
  'urls.primaryName': 'V3 API',
  
  presets: [
    SwaggerUI.presets.apis,
    SwaggerUIStandalonePreset
  ],
  layout: 'StandaloneLayout'
});

// Adds dropdown to switch between specs in TopBar
```

## Preset Contents

The standalone preset bundles:

```javascript
const SwaggerUIStandalonePreset = [
  // Core plugins from bundle
  ...SwaggerUI.presets.apis,
  
  // Standalone-specific
  TopbarPlugin,
  StandaloneLayoutPlugin,
  ConfigsPlugin,
  
  // Additional components
  {
    components: {
      StandaloneLayout,
      Topbar,
      TopbarInsert,
      FilterContainer,
      VersionPragmaFilter,
      VersionStamp
    }
  }
];
```

## Notes

- Companion to swagger-ui-bundle.js
- Provides full-page standalone documentation layout
- Adds TopBar with URL input for exploring different specs
- Includes filtering capabilities
- Required for the common "Swagger UI" appearance
- Can be customized or replaced with base layout
