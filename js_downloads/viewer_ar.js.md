# viewer_ar.js

## Overview
Minified Sketchfab webpack chunk containing the Axios HTTP client library and supporting utilities for making API requests with interceptors, cancellation, and various data transformers.

## File Status
- **Type**: Minified JavaScript (Webpack Bundle)
- **Chunk ID**: 7065
- **Minified**: Yes
- **License**: Available in separate LICENSE.txt file
- **Source Map**: Available (referenced in file)

## Key Components

### Axios HTTP Client
Complete HTTP client implementation:

**Core Features**:
- Promise-based requests
- Request/response interceptors
- Automatic JSON transformation
- CSRF protection
- Request cancellation

### Module "ntQ3" - Main Axios Export

**API Methods**:
```javascript
axios.get(url, config)
axios.post(url, data, config)
axios.put(url, data, config)
axios.patch(url, data, config)
axios.delete(url, config)
axios.head(url, config)
axios.options(url, config)
```

**Factory Methods**:
- `axios.create(config)` - Create custom instance
- `axios.all(promises)` - Parallel requests
- `axios.spread(callback)` - Spread array to args

### Module "waLb" - XHR Adapter
XMLHttpRequest-based transport:

**Features**:
- Progress events (download/upload)
- Timeout handling
- Authentication (Basic auth)
- FormData support
- Response types (text, json, blob, etc.)

### Module "g/4l" - Axios Class
Core Axios constructor:

**Properties**:
- `defaults` - Default configuration
- `interceptors.request` - Request interceptors
- `interceptors.response` - Response interceptors

**Methods**:
- `request(config)` - Make request
- Chain of interceptors → dispatch → transform

### Module "Lo+a" - Cancel Token
Request cancellation support:

**Cancel Class**:
```javascript
{
  message: string,
  __CANCEL__: true
}
```

**CancelToken**:
- `source()` - Create token/cancel pair
- `throwIfRequested()` - Check if cancelled

### Module "sxAL" - Interceptor Manager
Manages request/response interceptors:

**Methods**:
- `use(fulfilled, rejected)` - Add interceptor
- `eject(id)` - Remove interceptor
- `forEach(fn)` - Iterate handlers

### Module "bDWl" - Default Configuration
Default Axios settings:

| Setting | Default |
|---------|---------|
| `timeout` | 0 |
| `xsrfCookieName` | "XSRF-TOKEN" |
| `xsrfHeaderName` | "X-XSRF-TOKEN" |
| `maxContentLength` | -1 |
| `validateStatus` | 200-299 |
| `headers.Accept` | "application/json, text/plain" |

### Additional Libraries

**Day.js** - Date manipulation:
- Parsing and formatting
- Relative time
- UTC support
- Min/max operations

**isMobile** - Device detection:
- Apple devices (iPhone, iPad, iPod)
- Android
- Amazon devices
- Windows Phone
- Other (BlackBerry, Opera Mini, etc.)

**Redux** - State management:
- `createStore`
- `combineReducers`
- `compose`
- `applyMiddleware`

## Dependencies
- Promise library
- Browser APIs (XMLHttpRequest)
- Cookie utilities
- URL utilities

## Technical Details
- Promise-based async/await
- Interceptor chain pattern
- CSRF token automation
- Cross-origin support
- Content-Type detection

## Use Cases
1. API communication
2. File uploads
3. Authentication requests
4. Data fetching
5. Form submissions

## Notes
- Industry-standard HTTP client
- Comprehensive error handling
- Request/response transformation
- Browser and Node.js support
