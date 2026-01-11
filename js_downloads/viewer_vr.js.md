# viewer_vr.js

## Overview
Minified Sketchfab webpack chunk containing DOM utilities, URL query string parsing, text/string manipulation helpers, and prefetched data management for server-side rendering optimization.

## File Status
- **Type**: Minified JavaScript (Webpack Bundle)
- **Chunk ID**: 148
- **Minified**: Yes
- **Source Map**: Available (referenced in file)

## Key Components

### Module "t3PY" - Query String Parser
URL query parameter parsing:

**Pattern**: `/[&|;]+/g` for parameter separation

**parseQueryString (Qc)**:
```javascript
parseQueryString("?foo=bar&baz=qux")
// => { foo: ["bar"], baz: ["qux"] }
```

**Features**:
- Handles `?`, `&`, `|`, `;` separators
- URL decodes values
- Supports arrays (multiple same keys)
- Converts `+` to space

### Module "cSHm" - Prefetch Data Store
SSR data hydration manager:

**Methods**:
- `get(key)` - Retrieve cached data
- `register(key, value)` - Store data
- `hasInitialPropsOf(component)` - Check SSR props
- `getInitialPropsOf(component)` - Get SSR props
- `invalidate(url)` - Clear specific cache
- `invalidateAllMatchRegExp(pattern)` - Clear matching

**Features**:
- Reads from `window.prefetchedData`
- Extracts from DOM `#js-dom-data-prefetched-data`
- Query string aware invalidation

### Module "45Yh" - DOM Utilities
Comprehensive DOM helper functions:

**Element Position**:
```javascript
getOffset(element)
// => { top, left, bottom, right }

getPosition(element)
// => { top, left, width, height }

getCenterOffset(element)
// => offset from viewport center
```

**Image Loading**:
```javascript
loadImage(url)
// => Promise<HTMLImageElement>

preloadImage(url)
// => Promise<null> (silent load)
```

**SVG to Canvas**:
```javascript
htmlToSVG(html, width, height)
// => SVG element with foreignObject

elementToDataUrl(element, mimeType, quality)
// => base64 data URL
```

**Intersection Observer**:
```javascript
observeVisibility(element, callback, options)
// Returns cleanup function
// Options: margin, threshold, visibilityThreshold
```

**DOM Data Extraction**:
```javascript
getDOMData(id, type)
// Reads from #js-dom-data-{id}
// Types: "string" | "json"
// Handles HTML comment encoding
```

**Event Helpers**:
```javascript
addEventListener(target, event, handler, options)
removeEventListener(target, event, handler, options)
// Works with both DOM and jQuery-like objects
```

**Browser Detection**:
```javascript
isJSDOM() // Test environment
isIE()    // Internet Explorer
```

**Lazy Image Loading**:
```javascript
lazyLoadImage(img, src)
// Uses IntersectionObserver
// Shows/hides based on visibility
```

### Module "JBVY" - Query String Utilities
URL parameter manipulation:

**craft(params)**:
Build query string from object:
```javascript
craft({ page: 1, sort: 'date' })
// => "page=1&sort=date"
```

**string(key, defaultValue)**:
Get single parameter value

**strings(key, defaultValue)**:
Get array of values

**bool(key, defaultValue)**:
Get boolean parameter

**number(key, defaultValue)**:
Get numeric parameter

**color(key, defaultValue)**:
Get valid CSS color

**vec3(key, defaultValue)**:
Get 3D vector from comma-separated

**next(key)**:
Get sanitized redirect URL

### Module "1nxQ" - String Utilities
Text manipulation helpers:

**Case Conversion**:
```javascript
camelToUnderscore("fooBar")  // => "foo_bar"
camelToHyphen("fooBar")      // => "foo-bar"
slugify("Hello World!")      // => "hello-world"
```

**HTML/Text Processing**:
```javascript
sanitizeHtml(html)           // Strip HTML tags
escapeHtml(text)             // Escape special chars
decodeHtml(encoded)          // Decode entities
wrapParagraphs(text)         // Add <p> tags
sanitizeWithAttrs(html, attrs) // DOMPurify whitelist
```

**URL Linkification**:
```javascript
linkify(text, options)
// Converts URLs to <a> tags
// Converts emails to mailto:
// Converts @mentions to profile links
// Options: trimUrlLimit, target, noFollow
```

**Patterns**:
- Email: `\S+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9._-]+`
- URL: Complex URL pattern with TLDs
- Mention: `@[a-zA-Z0-9._-]{2,30}`

**Pluralization**:
```javascript
plural(count, singular, plural)
// => singular if count===1, else plural
```

**Path Normalization**:
```javascript
normalizePath("/foo/../bar/./baz")
// => "/bar/baz"
```

**Miscellaneous**:
- `hexColor(str)` - Extract/validate hex color
- `parseRange(str)` - Parse "start..end"
- `capitalize(str)` - Uppercase first char
- `stripNonAlpha(str)` - Remove non-letters

## Dependencies
- DOMPurify (HTML sanitization)
- jQuery (event handling)
- Lodash (memoize)
- Promise library

## Technical Details
- IntersectionObserver polyfill pattern
- HTML5 Canvas for image conversion
- URL encoding/decoding
- XSS prevention
- SSR hydration

## Use Cases
1. SSR data hydration
2. URL manipulation
3. DOM measurement
4. Image lazy loading
5. Text formatting

## Notes
- Browser compatibility helpers
- Security-focused utilities
- Performance optimizations
- SEO-friendly URL handling
