# viewer_utils.js

## Overview

This file contains **React model card components** - UI components for displaying 3D model previews in lists and grids. NOT generic utility functions as the filename suggests.

## File Information

- **Status**: Active webpack bundle
- **Size**: ~85KB (minified)
- **Type**: React components
- **Framework**: React

## Core Components

### 1. ModelCard

Main model preview card:

```javascript
<ModelCard
  model={model}
  size="medium"      // 'small' | 'medium' | 'large'
  showAuthor={true}
  showStats={true}
  showActions={false}
  orientation="vertical"  // 'vertical' | 'horizontal'
/>
```

### Model Card Structure

```jsx
function ModelCard({ model, size, showAuthor, showStats }) {
  return (
    <article className="model-card">
      {/* Thumbnail with play button for animated models */}
      <div className="model-card__thumbnail">
        <img 
          src={model.thumbnails.images[0].url} 
          alt={model.name}
          loading="lazy"
        />
        {model.isAnimated && <PlayIndicator />}
        {model.staffpickedAt && <StaffPickBadge />}
      </div>
      
      {/* Model info */}
      <div className="model-card__info">
        <h3 className="model-card__name">{model.name}</h3>
        
        {showAuthor && (
          <UserLink user={model.user} size="small" />
        )}
        
        {showStats && (
          <ModelStats 
            views={model.viewCount}
            likes={model.likeCount}
          />
        )}
      </div>
    </article>
  );
}
```

### 2. ModelCardSkeleton

Loading placeholder:

```javascript
<ModelCardSkeleton 
  count={12}
  size="medium"
/>

// Renders shimmer animation placeholders
```

### 3. ModelCardGrid

Grid layout wrapper:

```javascript
<ModelCardGrid
  models={models}
  columns={{ sm: 2, md: 3, lg: 4 }}
  gap={16}
  loading={isLoading}
  onLoadMore={loadMoreModels}
>
  {(model) => (
    <ModelCard model={model} showAuthor />
  )}
</ModelCardGrid>
```

### 4. ModelThumbnail

Standalone thumbnail component:

```javascript
<ModelThumbnail
  model={model}
  size={320}
  showOverlay={true}
  quality="high"
/>

// Features:
// - Lazy loading
// - Multiple size options
// - Hover overlay
// - Animated preview on hover
```

### Thumbnail Quality Sizes

```javascript
const thumbnailSizes = {
  small: { width: 200, height: 150 },
  medium: { width: 320, height: 240 },
  large: { width: 640, height: 480 },
  xlarge: { width: 1280, height: 720 }
};

// Get appropriate thumbnail URL
function getThumbnailUrl(model, size) {
  const { width, height } = thumbnailSizes[size];
  const images = model.thumbnails.images;
  
  // Find closest size
  const image = images.find(img => img.width >= width) || images[images.length - 1];
  return image.url;
}
```

### 5. AnimatedThumbnail

Preview animation on hover:

```javascript
<AnimatedThumbnail
  model={model}
  autoPlay={false}       // Play on hover only
  playOnHover={true}
  loop={true}
/>

// Uses preview video or animated GIF
```

### 6. ModelBadges

Overlay badges:

```javascript
<ModelBadges model={model}>
  {model.staffpickedAt && <StaffPickBadge />}
  {model.isPurchasable && <StoreBadge price={model.price} />}
  {model.isDownloadable && <DownloadableBadge />}
  {model.isAnimated && <AnimatedBadge />}
  {model.hasSound && <SoundBadge />}
</ModelBadges>
```

### 7. ModelStats

View/like counters:

```javascript
<ModelStats
  views={model.viewCount}
  likes={model.likeCount}
  comments={model.commentCount}
  compact={true}
/>

// Formats numbers: 1500 -> "1.5K"
```

## Model Object Structure

```javascript
const model = {
  uid: 'abc123',
  name: 'Model Name',
  
  // Thumbnails
  thumbnails: {
    images: [
      { url: '...', width: 200, height: 150 },
      { url: '...', width: 320, height: 240 },
      { url: '...', width: 640, height: 480 }
    ]
  },
  
  // Author
  user: {
    uid: 'user123',
    username: 'author',
    displayName: 'Author Name',
    avatars: { images: [...] }
  },
  
  // Stats
  viewCount: 10500,
  likeCount: 523,
  commentCount: 45,
  
  // Flags
  isAnimated: true,
  hasSound: false,
  isDownloadable: true,
  isPurchasable: false,
  staffpickedAt: '2023-01-15T00:00:00Z',
  
  // Timestamps
  publishedAt: '2023-01-10T00:00:00Z',
  createdAt: '2023-01-05T00:00:00Z'
};
```

## Usage Examples

### Model Grid Page

```jsx
function ModelsPage({ category }) {
  const { models, loading, loadMore, hasMore } = useModels({ category });
  
  return (
    <div className="models-page">
      <h1>{category} Models</h1>
      
      <ModelCardGrid
        models={models}
        columns={{ sm: 2, md: 3, lg: 4 }}
        loading={loading}
      >
        {(model) => (
          <Link to={`/models/${model.uid}`}>
            <ModelCard
              model={model}
              showAuthor
              showStats
            />
          </Link>
        )}
      </ModelCardGrid>
      
      {hasMore && (
        <button onClick={loadMore} disabled={loading}>
          {loading ? 'Loading...' : 'Load More'}
        </button>
      )}
    </div>
  );
}
```

### Search Results

```jsx
function SearchResults({ query }) {
  const { results, loading } = useSearch(query);
  
  if (loading) {
    return <ModelCardSkeleton count={12} />;
  }
  
  return (
    <ModelCardGrid models={results}>
      {(model) => (
        <ModelCard 
          model={model}
          orientation="horizontal"
          showAuthor
        />
      )}
    </ModelCardGrid>
  );
}
```

### User Profile Models

```jsx
function UserModels({ userId }) {
  const { models } = useUserModels(userId);
  
  return (
    <section className="user-models">
      {models.map(model => (
        <ModelCard
          key={model.uid}
          model={model}
          showAuthor={false}  // Already on user profile
          showStats
        />
      ))}
    </section>
  );
}
```

## CSS Classes

```css
.model-card { }
.model-card--small { }
.model-card--medium { }
.model-card--large { }
.model-card--horizontal { }

.model-card__thumbnail { }
.model-card__thumbnail img { }
.model-card__overlay { }
.model-card__badges { }

.model-card__info { }
.model-card__name { }
.model-card__author { }
.model-card__stats { }

.model-card-skeleton { }
.model-card-skeleton__thumbnail { }
.model-card-skeleton__text { }
```

## Notes

- Filename is misleading - contains React card components, not utilities
- Main model display component for grids/lists
- Supports various sizes and orientations
- Lazy loading for performance
- Animated preview support
- Skeleton loading states
