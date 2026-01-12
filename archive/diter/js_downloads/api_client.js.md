# api_client.js

## Overview

Despite its filename, this file contains **React UI components** for user interfaces - NOT an API client implementation. It includes avatar components, link handling, visibility badges, and analytics utilities.

## File Information

- **Status**: Active webpack bundle
- **Size**: ~90KB (minified)
- **Type**: React component library
- **Framework**: React 18 with hooks

## Core Components

### 1. Link Component

Smart link handling with external detection:

```javascript
// Features:
// - Auto-detects external URLs
// - Adds target="_blank" rel="noopener noreferrer" for external
// - onClick tracking integration
// - React Router integration for internal links
```

### 2. Avatar Component

```javascript
// Props
{
  user: UserObject,        // User with avatar URLs
  size: 'small' | 'medium' | 'large' | 'xlarge',
  className?: string,
  showOnlineStatus?: boolean
}

// Features:
// - Multiple size presets
// - Fallback avatar for missing images
// - Lazy loading support
```

### 3. VisibilityBadge Component

Model visibility indicators:

```javascript
// Visibility types and icons:
// 'public' - Globe icon
// 'private' - Lock icon
// 'protected' - Shield icon (password protected)
// 'org' - Building icon (organization only)

<VisibilityBadge visibility="private" showLabel />
```

### 4. useWindowSize Hook

Window dimension tracking:

```javascript
const { width, height } = useWindowSize();

// Updates on window resize
// Debounced for performance
```

### 5. OrgModelTitleColumn

Table column component for model lists:

```javascript
// Displays:
// - Model thumbnail
// - Model name (linked)
// - Visibility badge
// - Processing status
```

### 6. Analytics Date Utilities

```javascript
// Presets
const presets = {
  today: [startOfDay(now), now],
  yesterday: [startOfYesterday, endOfYesterday],
  last7days: [subDays(now, 7), now],
  last30days: [subDays(now, 30), now],
  thisMonth: [startOfMonth(now), now],
  lastMonth: [startOfLastMonth, endOfLastMonth],
  thisYear: [startOfYear(now), now],
  allTime: [null, null]
};

// Functions
formatDateForAPI(date)    // ISO format for API
getDateRange(preset)      // { start, end } dates
formatDisplayDate(date)   // Localized display
```

### 7. Chart Data Utilities

```javascript
// Transform raw analytics data for charting
formatChartData(rawData, {
  metric: 'views' | 'downloads' | 'likes',
  groupBy: 'day' | 'week' | 'month',
  fillGaps: true  // Fill missing dates with 0
});
```

### 8. Country/Referrer Filters

```javascript
// Country filter component
<CountryFilter
  data={countryCounts}
  selected={selectedCountry}
  onSelect={handleSelect}
/>

// Referrer categorization
// - direct: No referrer
// - search: Google, Bing, etc.
// - social: Facebook, Twitter, etc.
// - embed: Embedded viewer
```

## Styling

CSS Modules with BEM naming:

```css
.avatar { }
.avatar--small { }
.avatar--large { }
.avatar__image { }
.avatar__fallback { }

.visibility-badge { }
.visibility-badge--private { }
```

## Usage Examples

```jsx
// Avatar
<Avatar user={user} size="medium" />

// Visibility Badge
<VisibilityBadge visibility={model.visibility} showLabel />

// Analytics
const range = getDateRange('last30days');
const chartData = formatChartData(stats, { metric: 'views' });
```

## Dependencies

- React 18
- classnames/clsx
- Date utilities (date-fns style)
- React Router
