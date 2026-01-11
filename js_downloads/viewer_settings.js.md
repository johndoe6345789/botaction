# viewer_settings.js

## Overview
Sketchfab webpack runtime and chunk loading infrastructure. This file serves as the main entry point for the webpack bundled application, managing module loading, chunk fetching, and CSS asset loading.

## File Status
- **Type**: Webpack Runtime JavaScript
- **Minified**: Yes
- **Role**: Application Bootstrap
- **Source Map**: Available (referenced in file)

## Key Components

### Module System (`r`)
Core module require function with caching:

**Properties**:
- `r.m` - Module definitions map
- `r.c` - Module cache
- `r.d` - Define exports helper
- `r.o` - hasOwnProperty helper
- `r.r` - Mark as ES Module

### Chunk Loading Infrastructure

#### Chunk ID Mapping (`r.u`)
Maps chunk IDs to hashed filenames (~150+ chunks):
```javascript
{
  50: "fc043ffa619e1e0cbfec1b04521b4eb9",
  110: "c14eb62a98c0f1b15a12e24b002d031f",
  // ... 150+ more entries
}
```

#### CSS Chunk Mapping (`r.miniCssF`)
Maps chunk IDs to CSS file hashes (~27 CSS files):
```javascript
{
  50: "35e513a8e046a561d7367bc2b1718470",
  233: "906bd6bad83b4ab72bad5ed5cc4c50ac",
  // ... more CSS entries
}
```

### Dynamic Import System

**`r.e(chunkId)`**:
- Returns Promise for chunk loading
- Handles parallel CSS and JS loading
- Manages load states

**`r.l(url, done, key, chunkId)`**:
- Script loader with timeout (120s)
- Cross-origin support
- Deduplication of concurrent loads
- Error handling with retry logic

### CSS Loading System
**Features**:
- Dynamic link element creation
- Deduplication of existing stylesheets
- Error handling for failed loads
- Cross-origin attribute handling

### Chunk State Management
```javascript
{
  3666: 0,  // Ready
  2130: 0,  // Ready
  // Other chunks loaded on demand
}
```

**States**:
- `0` - Loaded/ready
- `[resolve, reject]` - Loading promise
- `undefined` - Not requested

### webpackChunk Array
**Push Handler** (`d.push`):
- Receives chunk definitions
- Registers modules
- Resolves pending promises
- Executes chunk runtime

## Technical Details

### Error Handling
- Timeout detection (120s)
- ChunkLoadError with details
- CSS_CHUNK_LOAD_FAILED code
- Network error recovery

### Cross-Origin Support
- Adds `crossOrigin="anonymous"` for CDN resources
- Respects same-origin for local assets
- Nonce support for CSP

### Performance Features
- Module caching
- Chunk deduplication
- Parallel loading
- Lazy CSS injection

## Dependencies
- Browser APIs (document, fetch)
- URL/Location APIs
- Promise API

## Use Cases
1. Application bootstrapping
2. Code splitting
3. Dynamic imports
4. CSS-in-JS loading
5. Lazy route loading

## Notes
- Foundation of Sketchfab's code-splitting strategy
- ~150 JavaScript chunks
- ~27 CSS chunks
- Essential for initial page load
- Manages entire dependency graph
