# viewer_environment.js

## Overview
Core browser environment utilities bundle containing DOMPurify HTML sanitizer, ES6 Promise polyfill, and jQuery 3.6.3 library for cross-browser compatibility and security.

## File Status
- **Type**: Minified Sketchfab Webpack Bundle
- **Webpack Chunk ID**: 841
- **Source Map**: `bc8e3f5f2b678b1def38df63f34ce14d-v2.js.map`
- **License**: See LICENSE.txt file

## Key Components

### haCR - DOMPurify (v2.4.1)
XSS sanitization library for safe HTML rendering.

#### Features
| Feature | Description |
|---------|-------------|
| `sanitize()` | Clean HTML string of XSS vectors |
| `setConfig()` | Configure sanitization rules |
| `addHook()` | Add processing hooks |
| `isValidAttribute()` | Validate attribute safety |

#### Configuration Options
| Option | Type | Description |
|--------|------|-------------|
| `ALLOWED_TAGS` | array | Permitted HTML tags |
| `ALLOWED_ATTR` | array | Permitted attributes |
| `FORBID_TAGS` | array | Blocked tags |
| `FORBID_ATTR` | array | Blocked attributes |
| `ALLOW_DATA_ATTR` | bool | Allow data-* attributes |
| `ALLOW_ARIA_ATTR` | bool | Allow aria-* attributes |
| `RETURN_DOM` | bool | Return DOM instead of string |
| `SANITIZE_DOM` | bool | Sanitize DOM clobbering |

#### Trusted Types Support
- Creates `dompurify` policy
- `createHTML()` for trusted HTML
- `createScriptURL()` for trusted scripts

### Oyie / 8Vqr - ES6 Promise Polyfill
Full Promise/A+ compliant polyfill.

#### Methods
| Method | Description |
|--------|-------------|
| `Promise.resolve()` | Create resolved promise |
| `Promise.reject()` | Create rejected promise |
| `Promise.all()` | Wait for all promises |
| `Promise.race()` | First settled promise |
| `then()` | Success handler |
| `catch()` | Error handler |

### Hjnd - jQuery 3.6.3
Complete jQuery library with all features.

#### Core Features
- DOM manipulation
- Event handling
- AJAX requests
- Animation
- CSS manipulation
- Deferred/Promise
- Utilities

#### Key Methods
| Category | Methods |
|----------|---------|
| Selection | `$()`, `find()`, `filter()`, `closest()` |
| DOM | `append()`, `prepend()`, `remove()`, `clone()` |
| Events | `on()`, `off()`, `trigger()`, `ready()` |
| AJAX | `$.ajax()`, `$.get()`, `$.post()`, `$.getJSON()` |
| Effects | `show()`, `hide()`, `fadeIn()`, `animate()` |
| CSS | `css()`, `addClass()`, `removeClass()`, `toggleClass()` |

#### jQuery.noConflict()
Releases `$` variable for other libraries.

## Dependencies
- Browser DOM APIs
- XMLHttpRequest
- MutationObserver
- Trusted Types API (optional)

## Technical Details
- DOMPurify: Comprehensive XSS prevention
- Promise: Microtask-based scheduling
- jQuery: Sizzle selector engine included
- All libraries are self-contained
- Browser feature detection included

## Security Features
1. HTML sanitization against XSS
2. DOM clobbering prevention
3. Trusted Types integration
4. Safe attribute validation
5. Template literal protection

## Use Cases
1. User-generated content rendering
2. Markdown preview sanitization
3. Cross-browser compatibility
4. Legacy code support
5. DOM manipulation utilities
6. Async operation handling

## Notes
- DOMPurify is critical for security
- jQuery provides compatibility layer
- Promise polyfill for older browsers
- All components are battle-tested libraries
- Essential for viewer's browser support
