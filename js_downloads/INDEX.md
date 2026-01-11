# Sketchfab JavaScript Files - Documentation Index

## Overview

This directory contains 45 JavaScript files downloaded from Sketchfab's web application. These are **webpack-bundled chunks** where the filenames do NOT correspond to the actual content inside. Each file is a compiled bundle that may contain multiple libraries, components, or utilities.

## Quick Reference Table

| Filename | Actual Content | Type |
|----------|---------------|------|
| [ai_tools.js](ai_tools.js.md) | AI creative tools config (text-to-3D, image-to-3D) | Configuration |
| [api_client.js](api_client.js.md) | React UI components (Avatar, Link, Analytics) | React Components |
| [challenge.js](challenge.js.md) | AWS WAF bot protection (obfuscated) | Security |
| [error_messages.js](error_messages.js.md) | Redux state management (auth, entities) | State Management |
| [jquery.min.js](jquery.min.js.md) | jQuery library | Library |
| [material_options.js](material_options.js.md) | Viewer embed options parser | Configuration |
| [missing_webgl_popup.js](missing_webgl_popup.js.md) | WebGL errors + model property forms | React Components |
| [model_page.js](model_page.js.md) | Model viewer page, reviews, downloads | React Components |
| [navigation.js](navigation.js.md) | Site navigation, header, search | React Components |
| [otSDKStub.js](otSDKStub.js.md) | OneTrust cookie consent SDK | Third-party SDK |
| [popup_template.js](popup_template.js.md) | Nunjucks popup templates | Templates |
| [shaders.js](shaders.js.md) | Spring animation + card slider | Animation/UI |
| [swagger-ui-bundle.js](swagger-ui-bundle.js.md) | Swagger UI API docs | Library |
| [swagger-ui-standalone-preset.js](swagger-ui-standalone-preset.js.md) | Swagger UI preset | Library |
| [user_profile.js](user_profile.js.md) | User profiles, follow system | React Components |
| [viewer.js](viewer.js.md) | Popup system, WebGL detection, embed | Core Viewer |
| [viewer_analytics.js](viewer_analytics.js.md) | Dropdown/select components | React Components |
| [viewer_animation.js](viewer_animation.js.md) | Form components, org utilities | React Components |
| [viewer_annotations.js](viewer_annotations.js.md) | Banner/countdown components | React Components |
| [viewer_ar.js](viewer_ar.js.md) | Axios HTTP client + Day.js | Libraries |
| [viewer_audio.js](viewer_audio.js.md) | Comment system + emoji picker | React Components |
| [viewer_cache.js](viewer_cache.js.md) | Lodash utility library | Library |
| [viewer_components.js](viewer_components.js.md) | Star ratings, tabs, icons | React Components |
| [viewer_config.js](viewer_config.js.md) | Viewer configuration JSON | Configuration |
| [viewer_controls.js](viewer_controls.js.md) | Floating UI positioning library | Library |
| [viewer_core.js](viewer_core.js.md) | Redux hooks + Button component | React/Redux |
| [viewer_environment.js](viewer_environment.js.md) | jQuery library (duplicate) | Library |
| [viewer_exports.js](viewer_exports.js.md) | Lodash chain utilities | Library |
| [viewer_geometry.js](viewer_geometry.js.md) | SPA routing system | Routing |
| [viewer_hotspots.js](viewer_hotspots.js.md) | CSS module class mappings | CSS Modules |
| [viewer_inspector.js](viewer_inspector.js.md) | Form validation utilities | Utilities |
| [viewer_lighting.js](viewer_lighting.js.md) | Twemoji emoji library | Library |
| [viewer_loading.js](viewer_loading.js.md) | Organization/project management | React Components |
| [viewer_materials.js](viewer_materials.js.md) | CSS design tokens/system | Design System |
| [viewer_models.js](viewer_models.js.md) | Nunjucks logo templates | Templates |
| [viewer_network.js](viewer_network.js.md) | Markdown editor toolbar | React Components |
| [viewer_postprocessing.js](viewer_postprocessing.js.md) | Typography, themes, modals | UI Infrastructure |
| [viewer_settings.js](viewer_settings.js.md) | Webpack runtime bootstrap | Build System |
| [viewer_stats.js](viewer_stats.js.md) | Model transfer popup | React Components |
| [viewer_textures.js](viewer_textures.js.md) | 360° preview + grid layouts | React Components |
| [viewer_ui.js](viewer_ui.js.md) | Public Suffix List (TLD data) | Data |
| [viewer_utils.js](viewer_utils.js.md) | Model card components | React Components |
| [viewer_vr.js](viewer_vr.js.md) | URL parsing utilities | Utilities |
| [visibility_popup.js](visibility_popup.js.md) | Visibility settings, themes, Pro badges | React Components |
| [webgl_recorder.js](webgl_recorder.js.md) | React 18 DOM + React-Redux | Library |

## Content Categories

### React Components (17 files)
- api_client.js, missing_webgl_popup.js, model_page.js, navigation.js
- user_profile.js, viewer_analytics.js, viewer_animation.js, viewer_annotations.js
- viewer_audio.js, viewer_components.js, viewer_loading.js, viewer_network.js
- viewer_stats.js, viewer_textures.js, viewer_utils.js, visibility_popup.js
- viewer_postprocessing.js

### Third-Party Libraries (10 files)
- jquery.min.js, viewer_environment.js (jQuery)
- viewer_ar.js (Axios, Day.js, isMobile)
- viewer_cache.js, viewer_exports.js (Lodash)
- viewer_controls.js (Floating UI)
- viewer_lighting.js (Twemoji)
- swagger-ui-bundle.js, swagger-ui-standalone-preset.js (Swagger UI)
- webgl_recorder.js (React 18, React-Redux)

### State Management (2 files)
- error_messages.js (Redux store, reducers, actions)
- viewer_core.js (Redux hooks, React integration)

### Configuration/Data (5 files)
- ai_tools.js (AI tools configuration)
- viewer_config.js (Viewer settings)
- viewer_ui.js (Public Suffix List)
- viewer_hotspots.js (CSS module mappings)
- viewer_materials.js (Design system tokens)

### Templates (2 files)
- popup_template.js (Nunjucks popups)
- viewer_models.js (Nunjucks logos)

### Utilities (3 files)
- viewer_inspector.js (Form validation)
- viewer_vr.js (URL parsing)
- viewer_geometry.js (SPA routing)

### Core/Infrastructure (4 files)
- viewer.js (Core popup/embed system)
- viewer_settings.js (Webpack runtime)
- shaders.js (Animation system)
- material_options.js (Embed options)

### Security/Privacy (2 files)
- challenge.js (AWS WAF bot protection)
- otSDKStub.js (OneTrust consent)

## Key Technologies

- **React 18** - UI framework
- **Redux** - State management
- **Axios** - HTTP client
- **Lodash** - Utility functions
- **Floating UI** - Positioning
- **Nunjucks** - Server templates
- **Twemoji** - Emoji rendering
- **Day.js** - Date handling
- **Swagger UI** - API documentation
- **Webpack** - Module bundling

## Important Notes

1. **Filename ≠ Content**: These are webpack chunk names that don't reflect actual contents
2. **Minified Code**: All files are minified and may be hard to read directly
3. **Interdependencies**: Files share code through webpack's module system
4. **Version Specific**: This represents a snapshot of Sketchfab's frontend at download time
5. **Subject to Change**: Sketchfab may update their bundles at any time
