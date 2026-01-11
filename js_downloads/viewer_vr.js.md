# viewer_vr.js

## Overview

This file contains **URL parsing and query string utilities** - NOT VR (Virtual Reality) functionality. It provides URL manipulation, DOM data extraction, and string utilities.

## File Information

- **Status**: Active webpack bundle
- **Size**: ~65KB (minified)
- **Type**: URL and string utilities
- **Framework**: Vanilla JavaScript

## Core Modules

### 1. Query String Parsing (`t3PY`)

```javascript
// Parse query string
const params = parseQueryString('?page=1&sort=name&tags=a,b,c');
// { page: '1', sort: 'name', tags: 'a,b,c' }

// Parse with array support
const params = parseQueryStringArrays('?tags=a&tags=b&tags=c');
// { tags: ['a', 'b', 'c'] }

// Build query string
const qs = buildQueryString({ page: 1, sort: 'name' });
// 'page=1&sort=name'
```

### 2. DOM Data Utilities (`45Yh`)

Extract data from DOM elements:

```javascript
// Get data attribute
const modelId = getDataAttribute(element, 'model-id');
// <div data-model-id="abc123"> → 'abc123'

// Get prefetched data
const prefetchedData = getPrefetchedData('models');
// Returns data from <script type="application/json" data-prefetch="models">

// Get config from DOM
const config = getDomConfig('viewer-config');
// Returns parsed JSON from data attribute
```

### 3. URL Crafting Utilities (`JBVY`)

```javascript
// Named route URLs
const modelUrl = getUrl('models:view', { modelId: 'abc123' });
// '/models/abc123'

const searchUrl = getUrl('search', {}, { q: 'cars', category: 'vehicles' });
// '/search?q=cars&category=vehicles'

// External URLs
const embedUrl = getEmbedUrl(modelId, { autostart: 1, ui_infos: 0 });
// 'https://sketchfab.com/models/abc123/embed?autostart=1&ui_infos=0'

// Download URLs
const downloadUrl = getDownloadUrl(modelId, format);
// 'https://sketchfab.com/models/abc123/download/gltf'
```

### URL Parsing

```javascript
// Parse URL parts
const parsed = parseUrl('https://sketchfab.com/models/abc123?view=3d#comments');
// {
//   protocol: 'https:',
//   host: 'sketchfab.com',
//   pathname: '/models/abc123',
//   search: '?view=3d',
//   hash: '#comments'
// }

// Get current page params
const { modelId } = getPageParams();  // From current URL
```

### 4. String Utilities (`1nxQ`)

```javascript
// Sanitize string
const safe = sanitize('<script>alert("xss")</script>');
// '&lt;script&gt;alert("xss")&lt;/script&gt;'

// Truncate string
const truncated = truncate('Long description text...', 100);
// 'Long description...'

// Slugify
const slug = slugify('My Model Name!');
// 'my-model-name'

// Capitalize
const title = capitalize('hello world');
// 'Hello world'

// Camel case
const camel = toCamelCase('some-property-name');
// 'somePropertyName'

// Kebab case
const kebab = toKebabCase('somePropertyName');
// 'some-property-name'
```

## URL Parameter Helpers

### Get/Set URL Parameters

```javascript
// Get single param
const page = getUrlParam('page');  // From current URL
const page = getUrlParam('page', '?page=2&sort=name');  // From string

// Get multiple params
const { page, sort, tags } = getUrlParams(['page', 'sort', 'tags']);

// Set params (returns new URL string)
const newUrl = setUrlParams({ page: 2, sort: 'date' });
// '/current/path?page=2&sort=date'

// Remove params
const cleanUrl = removeUrlParams(['tracking', 'utm_source']);
```

### URL String Helpers

```javascript
// Check if absolute URL
isAbsoluteUrl('https://example.com');  // true
isAbsoluteUrl('/relative/path');       // false

// Check if external URL
isExternalUrl('https://google.com');   // true
isExternalUrl('/models/abc');          // false
isExternalUrl('https://sketchfab.com/models'); // false

// Get base URL
getBaseUrl();  // 'https://sketchfab.com'

// Join URL parts
joinUrl('https://sketchfab.com', 'models', 'abc123');
// 'https://sketchfab.com/models/abc123'
```

## Query String Type Coercion

```javascript
// String (default)
const str = getUrlParam('q', 'default', String);

// Number
const page = getUrlParam('page', 1, Number);

// Boolean
const enabled = getUrlParam('autostart', false, Boolean);

// Array (comma-separated)
const tags = getUrlParam('tags', [], Array);
// 'tags=a,b,c' → ['a', 'b', 'c']

// Multiple values (repeated params)
const tags = getUrlParams('tags[]');
// 'tags[]=a&tags[]=b' → ['a', 'b']
```

## Named Routes

```javascript
// Route definitions (conceptual)
const routes = {
  'models:view': '/models/:modelId',
  'models:edit': '/models/:modelId/edit',
  'user:profile': '/@:username',
  'search': '/search',
  'store:category': '/store/categories/:category'
};

// Generate URL
getUrl('models:view', { modelId: 'abc123' });
// '/models/abc123'

getUrl('search', {}, { q: 'car', sort: '-date' });
// '/search?q=car&sort=-date'
```

## Usage Examples

### Building API URLs

```javascript
const apiUrl = buildApiUrl('/v3/models', {
  q: searchQuery,
  page: currentPage,
  sort_by: sortOrder,
  categories: selectedCategories.join(',')
});
```

### Parsing Page Data

```javascript
// On page load, extract prefetched data
const modelData = getPrefetchedData('model');
const userData = getPrefetchedData('user');
const configData = getDomConfig('page-config');

// Initialize with data
initializePage(modelData, userData, configData);
```

### URL Navigation

```javascript
// Update URL without reload
const newUrl = setUrlParams({ page: 2 });
history.pushState(null, '', newUrl);

// Read current state
const { page, sort } = getUrlParams(['page', 'sort']);
```

## Security

### XSS Prevention

```javascript
// Always sanitize user input before displaying
const safeDescription = sanitize(userInput);
element.innerHTML = safeDescription;

// Use text content for plain text
element.textContent = userInput;  // Automatically escaped
```

## Notes

- Filename is misleading - contains URL utilities, not VR code
- Core utilities used throughout Sketchfab
- Handles both frontend routing and API URL construction
- Includes security helpers for XSS prevention
