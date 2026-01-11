# viewer_ar.js

## Overview

This file contains **HTTP client (Axios) and date utilities (Day.js)** - NOT AR (Augmented Reality) functionality. It provides API request handling and date formatting for Sketchfab.

## File Information

- **Status**: Active webpack bundle
- **Size**: ~78KB (minified)
- **Type**: HTTP and date libraries
- **Libraries**: Axios, Day.js, isMobile

## Core Components

### 1. Axios HTTP Client (`keQT/ntQ3`)

Full-featured HTTP client:

```javascript
// GET request
axios.get('/api/models')
  .then(response => response.data)
  .catch(error => console.error(error));

// POST request
axios.post('/api/models', { name: 'Model' })
  .then(response => response.data);

// Full configuration
axios({
  method: 'get',
  url: '/api/models',
  params: { page: 1, limit: 20 },
  headers: { 'Authorization': 'Bearer token' },
  timeout: 5000
});
```

### Request Configuration

```javascript
const config = {
  // URL
  url: '/api/endpoint',
  baseURL: 'https://api.sketchfab.com',
  
  // Method
  method: 'get',  // get, post, put, delete, patch
  
  // Parameters
  params: { key: 'value' },  // URL query params
  data: { key: 'value' },    // Request body
  
  // Headers
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer token'
  },
  
  // Timeout
  timeout: 10000,
  
  // Response type
  responseType: 'json',  // json, blob, arraybuffer, text
  
  // Upload/download progress
  onUploadProgress: (progressEvent) => { },
  onDownloadProgress: (progressEvent) => { }
};
```

### Interceptors

```javascript
// Request interceptor
axios.interceptors.request.use(
  config => {
    config.headers.Authorization = `Bearer ${getToken()}`;
    return config;
  },
  error => Promise.reject(error)
);

// Response interceptor
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      redirectToLogin();
    }
    return Promise.reject(error);
  }
);
```

### Instance Creation

```javascript
const api = axios.create({
  baseURL: 'https://api.sketchfab.com/v3',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});
```

### 2. XMLHttpRequest Wrapper (`waLb`)

Low-level XHR utilities:

```javascript
// For cases where Axios isn't suitable
const xhr = new XMLHttpRequest();
xhr.open('GET', '/api/models');
xhr.setRequestHeader('Authorization', 'Bearer token');
xhr.onload = function() {
  if (xhr.status === 200) {
    console.log(JSON.parse(xhr.responseText));
  }
};
xhr.send();
```

### 3. Day.js Date Library (`SHI0`)

Lightweight date manipulation:

```javascript
// Current date
dayjs();
dayjs(new Date());
dayjs('2023-01-15');
dayjs(1673740800000);  // Unix timestamp

// Formatting
dayjs().format('YYYY-MM-DD');         // '2023-01-15'
dayjs().format('MMMM D, YYYY');       // 'January 15, 2023'
dayjs().format('MMM D, YYYY h:mm A'); // 'Jan 15, 2023 3:30 PM'

// Relative time
dayjs().fromNow();     // '2 hours ago'
dayjs().toNow();       // 'in 2 hours'

// Manipulation
dayjs().add(1, 'day');
dayjs().subtract(1, 'week');
dayjs().startOf('month');
dayjs().endOf('year');

// Comparison
dayjs('2023-01-15').isBefore('2023-01-20');
dayjs('2023-01-15').isAfter('2023-01-10');
dayjs('2023-01-15').isSame('2023-01-15', 'day');
```

### Day.js Plugins

```javascript
// Relative time plugin
dayjs.extend(relativeTime);
dayjs().fromNow();  // '2 days ago'

// Duration plugin
dayjs.extend(duration);
dayjs.duration(3600000).humanize();  // '1 hour'

// UTC plugin
dayjs.extend(utc);
dayjs.utc().format();

// Timezone plugin
dayjs.extend(timezone);
dayjs().tz('America/New_York');
```

### 4. isMobile Detection (`K9VK`)

Device type detection:

```javascript
const isMobile = require('ismobilejs');

// Check device type
isMobile.phone;    // true if phone
isMobile.tablet;   // true if tablet
isMobile.any;      // true if any mobile device

// Check specific platforms
isMobile.apple.phone;
isMobile.apple.tablet;
isMobile.android.phone;
isMobile.android.tablet;
isMobile.windows.phone;
isMobile.windows.tablet;

// Usage in Sketchfab
if (isMobile.any) {
  // Show mobile-optimized UI
  showMobileViewer();
} else {
  // Show full desktop viewer
  showDesktopViewer();
}
```

## Sketchfab API Usage

### Model API

```javascript
// Get model
const model = await axios.get(`/v3/models/${modelId}`);

// Search models
const results = await axios.get('/v3/search', {
  params: {
    type: 'models',
    q: 'car',
    sort_by: '-likeCount'
  }
});

// Like model
await axios.post(`/v3/models/${modelId}/like`);
```

### Upload API

```javascript
// Upload with progress
const response = await axios.post('/v3/models', formData, {
  headers: {
    'Content-Type': 'multipart/form-data'
  },
  onUploadProgress: (progressEvent) => {
    const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
    updateProgressBar(percent);
  }
});
```

### Date Formatting

```javascript
// Model timestamps
const createdAt = dayjs(model.createdAt).format('MMM D, YYYY');
const updatedAt = dayjs(model.updatedAt).fromNow();

// Comment timestamps
const commentTime = dayjs(comment.createdAt).fromNow();  // '2 hours ago'
```

## Error Handling

```javascript
try {
  const response = await axios.get('/api/models');
} catch (error) {
  if (error.response) {
    // Server responded with error status
    console.log(error.response.status);
    console.log(error.response.data);
  } else if (error.request) {
    // Request made but no response
    console.log('Network error');
  } else {
    // Error setting up request
    console.log(error.message);
  }
}
```

## Notes

- Filename is misleading - contains HTTP/date libs, not AR code
- Axios is the primary HTTP client for API calls
- Day.js handles date formatting and manipulation
- isMobile provides device detection
- All used throughout Sketchfab's web application
