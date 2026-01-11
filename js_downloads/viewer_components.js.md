# viewer_components.js

## Overview

This file contains **React UI components** including star ratings, tabs, gradient icons, and other reusable interface elements. These are generic UI building blocks used across the Sketchfab application.

## File Information

- **Status**: Active webpack bundle
- **Size**: ~92KB (minified)
- **Type**: React UI components
- **Framework**: React

## Core Components

### 1. StarRating

Interactive or display-only star rating:

```javascript
// Display-only rating
<StarRating
  value={4.5}
  max={5}
  size="medium"
  readonly={true}
/>

// Interactive rating input
<StarRating
  value={rating}
  onChange={setRating}
  max={5}
  size="large"
  allowHalf={true}
/>
```

### StarRating Props

```javascript
StarRating.propTypes = {
  value: PropTypes.number,        // Current rating (0-5)
  max: PropTypes.number,          // Max stars (default 5)
  size: PropTypes.oneOf(['small', 'medium', 'large']),
  readonly: PropTypes.bool,       // Display only
  allowHalf: PropTypes.bool,      // Allow 0.5 increments
  showValue: PropTypes.bool,      // Show numeric value
  onChange: PropTypes.func        // Rating change handler
};
```

### Star Icons

```javascript
// Different star states
const StarIcon = ({ fill }) => (
  <svg className={`star star--${fill}`}>
    {fill === 'full' && <path d="..." />}
    {fill === 'half' && <path d="..." />}
    {fill === 'empty' && <path d="..." />}
  </svg>
);

// fill: 'full' | 'half' | 'empty'
```

### 2. Tabs

Tabbed navigation component:

```javascript
<Tabs
  value={activeTab}
  onChange={setActiveTab}
  variant="default"  // 'default' | 'pills' | 'underline'
>
  <Tab value="models" label="Models" count={45} />
  <Tab value="likes" label="Likes" count={128} />
  <Tab value="collections" label="Collections" count={12} />
</Tabs>

<TabPanel value="models" activeValue={activeTab}>
  <ModelGrid models={models} />
</TabPanel>
<TabPanel value="likes" activeValue={activeTab}>
  <ModelGrid models={likedModels} />
</TabPanel>
```

### Tab Variants

```javascript
// Default: Horizontal with border-bottom
<Tabs variant="default">
  <Tab value="1" label="Tab 1" />
  <Tab value="2" label="Tab 2" />
</Tabs>

// Pills: Rounded button style
<Tabs variant="pills">
  <Tab value="1" label="Tab 1" />
  <Tab value="2" label="Tab 2" />
</Tabs>

// Underline: Simple underline indicator
<Tabs variant="underline">
  <Tab value="1" label="Tab 1" />
  <Tab value="2" label="Tab 2" />
</Tabs>
```

### 3. GradientIcon

Icons with gradient fills:

```javascript
<GradientIcon
  name="heart"
  gradient="primary"   // Gradient preset name
  size={24}
/>

// Custom gradient
<GradientIcon
  name="star"
  gradient={{
    start: '#ff6b6b',
    end: '#ffd93d'
  }}
  size={32}
/>
```

### Gradient Presets

```javascript
const gradientPresets = {
  primary: {
    start: '#1caad9',
    end: '#0e7490'
  },
  success: {
    start: '#10b981',
    end: '#059669'
  },
  warning: {
    start: '#f59e0b',
    end: '#d97706'
  },
  danger: {
    start: '#ef4444',
    end: '#dc2626'
  },
  purple: {
    start: '#8b5cf6',
    end: '#7c3aed'
  },
  rainbow: {
    start: '#ec4899',
    middle: '#8b5cf6',
    end: '#3b82f6'
  }
};
```

### 4. Badge

Status and count badges:

```javascript
// Count badge
<Badge count={5} max={99} />  // Shows "5"
<Badge count={150} max={99} /> // Shows "99+"

// Status badge
<Badge status="success">Active</Badge>
<Badge status="warning">Pending</Badge>
<Badge status="danger">Expired</Badge>

// Dot badge
<Badge dot color="red" />
```

### 5. Tooltip

Hover tooltips:

```javascript
<Tooltip 
  content="This is helpful information"
  placement="top"
  delay={200}
>
  <button>Hover me</button>
</Tooltip>

// Rich content
<Tooltip
  content={
    <div>
      <strong>Title</strong>
      <p>Description text</p>
    </div>
  }
>
  <InfoIcon />
</Tooltip>
```

### 6. Progress

Progress indicators:

```javascript
// Linear progress bar
<Progress
  value={75}
  max={100}
  showLabel={true}
  color="primary"
/>

// Circular progress
<CircularProgress
  value={60}
  size={48}
  strokeWidth={4}
/>

// Indeterminate
<Progress indeterminate />
```

### 7. Skeleton

Loading placeholders:

```javascript
// Text skeleton
<Skeleton width={200} height={16} />

// Circle (avatar)
<Skeleton variant="circle" size={48} />

// Rectangle (image)
<Skeleton variant="rect" width={300} height={200} />

// Paragraph
<Skeleton.Paragraph lines={3} />
```

### 8. Divider

Content separator:

```javascript
// Horizontal divider
<Divider />

// With text
<Divider>OR</Divider>

// Vertical divider
<Divider orientation="vertical" />
```

### 9. Empty State

No content placeholder:

```javascript
<EmptyState
  icon={<SearchIcon />}
  title="No results found"
  description="Try adjusting your search or filters"
  action={
    <Button onClick={clearFilters}>
      Clear Filters
    </Button>
  }
/>
```

## Utility Components

### Truncate

Text truncation:

```javascript
<Truncate lines={2}>
  Long text that will be truncated after two lines...
</Truncate>
```

### VisuallyHidden

Screen reader only:

```javascript
<button>
  <HeartIcon />
  <VisuallyHidden>Like this model</VisuallyHidden>
</button>
```

### Portal

Render outside parent:

```javascript
<Portal container={document.body}>
  <Modal>Content</Modal>
</Portal>
```

## Usage Examples

### Review Form

```jsx
function ReviewForm({ onSubmit }) {
  const [rating, setRating] = useState(0);
  const [review, setReview] = useState('');
  
  return (
    <form onSubmit={() => onSubmit({ rating, review })}>
      <label>
        Rating
        <StarRating
          value={rating}
          onChange={setRating}
          size="large"
        />
      </label>
      
      <textarea
        value={review}
        onChange={e => setReview(e.target.value)}
        placeholder="Write your review..."
      />
      
      <Button type="submit" disabled={rating === 0}>
        Submit Review
      </Button>
    </form>
  );
}
```

### Profile Tabs

```jsx
function UserProfile({ user }) {
  const [tab, setTab] = useState('models');
  
  return (
    <div className="profile">
      <ProfileHeader user={user} />
      
      <Tabs value={tab} onChange={setTab}>
        <Tab value="models" label="Models" count={user.modelCount} />
        <Tab value="likes" label="Likes" count={user.likeCount} />
        <Tab value="collections" label="Collections" />
      </Tabs>
      
      <TabPanel value="models" activeValue={tab}>
        <UserModels userId={user.uid} />
      </TabPanel>
      <TabPanel value="likes" activeValue={tab}>
        <UserLikes userId={user.uid} />
      </TabPanel>
    </div>
  );
}
```

## CSS Classes

```css
/* Star Rating */
.star-rating { }
.star-rating__star { }
.star-rating__star--full { }
.star-rating__star--half { }
.star-rating__star--empty { }
.star-rating__value { }

/* Tabs */
.tabs { }
.tabs--pills { }
.tabs--underline { }
.tab { }
.tab--active { }
.tab__count { }
.tab-panel { }

/* Badge */
.badge { }
.badge--success { }
.badge--warning { }
.badge--danger { }
.badge__dot { }

/* Progress */
.progress { }
.progress__bar { }
.progress__label { }
.progress--circular { }

/* Skeleton */
.skeleton { }
.skeleton--text { }
.skeleton--circle { }
.skeleton--rect { }
```

## Notes

- Generic reusable UI components
- Star rating with half-star support
- Multiple tab variants
- Gradient icon system
- Loading skeletons
- Accessibility features (ARIA)
