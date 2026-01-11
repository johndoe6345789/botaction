# viewer_textures.js

## Overview

This file contains **360° model preview, grid layout, and staff pick display components** - NOT texture handling code. It provides interactive preview thumbnails and grid-based model displays.

## File Information

- **Status**: Active webpack bundle
- **Size**: ~85KB (minified)
- **Type**: React preview and grid components
- **Framework**: React

## Core Components

### 1. Model360Preview (`nnpx`)

Interactive 360° thumbnail preview:

```javascript
<Model360Preview
  model={model}
  spriteUrl={model.thumbnails.spriteUrl}
  spriteCount={24}                    // Number of frames
  width={400}
  height={300}
  autoRotate={false}                  // Auto-rotate on hover
  onInteraction={handleInteraction}
/>

// Features:
// - Sprite sheet animation
// - Drag to rotate
// - Touch support
// - Hover activation
```

### Sprite Sheet Animation Logic

```javascript
// Sprite sheet format:
// - Horizontal strip of frames
// - Each frame is the same width
// - spriteCount determines frame positions

const getFramePosition = (frameIndex, spriteCount, width) => {
  const frameWidth = width / spriteCount;
  return -(frameIndex * frameWidth);
};

// Mouse/touch drag to rotate:
const handleDrag = (deltaX) => {
  const frameChange = Math.floor(deltaX / dragSensitivity);
  const newFrame = (currentFrame + frameChange + spriteCount) % spriteCount;
  setCurrentFrame(newFrame);
};
```

### 2. Grid Item Component (`AhsD`)

Individual item in grid layout:

```javascript
<GridItem
  item={model}
  renderContent={(item) => <ModelCard model={item} />}
  aspectRatio={4/3}
  onClick={handleClick}
/>
```

### 3. Grid Layout (`hpsH`)

Paginated grid with infinite scroll:

```javascript
<Grid
  items={models}
  renderItem={(model) => <ModelCard model={model} />}
  columns={{ mobile: 2, tablet: 3, desktop: 4 }}
  gap={16}
  loadMore={handleLoadMore}
  hasMore={hasNextPage}
  loading={isLoading}
  maxPages={10}                       // Auto-load up to 10 pages
/>

// Pagination options:
// - Load more button
// - Infinite scroll
// - Previous/next pages
```

### 4. StaffPickFlags (`QFI+`)

Staff pick and content badges:

```javascript
<StaffPickFlags
  isStaffPicked={model.isStaffPicked}
  isRestricted={model.isRestricted}
  showLabels={false}
/>

// Displays badges:
// - Staff Pick: Star icon
// - Restricted: 18+ indicator
```

## Grid Implementation Details

### Responsive Columns

```javascript
const gridColumns = {
  mobile: {
    breakpoint: 0,
    columns: 2
  },
  tablet: {
    breakpoint: 768,
    columns: 3
  },
  desktop: {
    breakpoint: 1024,
    columns: 4
  },
  wide: {
    breakpoint: 1440,
    columns: 5
  }
};
```

### Infinite Scroll Logic

```javascript
const useGridInfiniteScroll = (containerRef, loadMore, { maxPages = 10 }) => {
  const loadedPages = useRef(0);
  
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && loadedPages.current < maxPages) {
          loadMore().then(() => {
            loadedPages.current++;
          });
        }
      },
      { rootMargin: '400px' }
    );
    
    if (containerRef.current) {
      observer.observe(containerRef.current);
    }
    
    return () => observer.disconnect();
  }, [loadMore, maxPages]);
};
```

### Load More Button

```javascript
const LoadMoreButton = ({ onClick, loading, hasMore }) => {
  if (!hasMore) return null;
  
  return (
    <Button
      onClick={onClick}
      loading={loading}
      disabled={loading}
    >
      Load More
    </Button>
  );
};
```

## 360° Preview Technical Details

### Sprite URL Format

```
https://static.sketchfab.com/models/{modelId}/thumbnails/360x270/{spriteId}.jpg
```

### Animation Performance

```javascript
// Use CSS transform for performance
const previewStyle = {
  backgroundImage: `url(${spriteUrl})`,
  backgroundPosition: `${framePosition}px 0`,
  backgroundSize: `${spriteCount * 100}% 100%`,
  transition: isAnimating ? 'none' : 'background-position 0.1s ease'
};
```

### Touch Handling

```javascript
const handleTouchMove = (e) => {
  e.preventDefault();  // Prevent page scroll
  const touch = e.touches[0];
  const deltaX = touch.clientX - lastTouchX.current;
  updateFrame(deltaX);
  lastTouchX.current = touch.clientX;
};
```

## Usage Examples

### Model Grid Page

```jsx
function ModelsPage({ category }) {
  const { models, loadMore, hasNext, loading } = useModels(category);
  
  return (
    <Grid
      items={models}
      renderItem={(model) => (
        <div className="model-item">
          <Model360Preview model={model} />
          <StaffPickFlags
            isStaffPicked={model.isStaffPicked}
            isRestricted={model.isRestricted}
          />
          <h3>{model.name}</h3>
        </div>
      )}
      loadMore={loadMore}
      hasMore={hasNext}
      loading={loading}
    />
  );
}
```

### Interactive Thumbnail

```jsx
function ModelThumbnail({ model }) {
  const [showPreview, setShowPreview] = useState(false);
  
  return (
    <div
      onMouseEnter={() => setShowPreview(true)}
      onMouseLeave={() => setShowPreview(false)}
    >
      {showPreview && model.thumbnails.spriteUrl ? (
        <Model360Preview
          model={model}
          spriteUrl={model.thumbnails.spriteUrl}
          autoRotate
        />
      ) : (
        <img src={model.thumbnails.defaultUrl} alt={model.name} />
      )}
    </div>
  );
}
```

## CSS Classes

```css
.grid { }
.grid__container { }
.grid__item { }
.grid__load-more { }

.model-360-preview { }
.model-360-preview--active { }
.model-360-preview__frame { }

.staff-pick-flags { }
.staff-pick-flags__staff-pick { }
.staff-pick-flags__restricted { }
```

## Notes

- Filename is misleading - contains no texture code
- 360° preview requires sprite sheet generation
- Grid supports responsive column counts
- Infinite scroll is optional with configurable limits
