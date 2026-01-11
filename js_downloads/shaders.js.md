# shaders.js

## Overview

This file contains **spring animation system and card slider carousel** - NOT WebGL shaders. It provides physics-based animations and horizontal scrolling card components.

## File Information

- **Status**: Active webpack bundle
- **Size**: ~52KB (minified)
- **Type**: Animation and carousel components
- **Framework**: React

## Core Components

### 1. Spring Animation (`jSUW`)

Physics-based spring animation:

```javascript
// Create spring with configuration
const spring = createSpring({
  stiffness: 170,    // How "springy" (higher = bouncier)
  damping: 26,       // Friction (higher = less oscillation)
  mass: 1,           // Mass of object
  velocity: 0        // Initial velocity
});

// Animate from current to target
spring.animate(targetValue, {
  onUpdate: (value) => {
    element.style.transform = `translateX(${value}px)`;
  },
  onComplete: () => {
    console.log('Animation complete');
  }
});
```

### Spring Configuration Presets

```javascript
const springPresets = {
  // Smooth and natural
  default: { stiffness: 170, damping: 26 },
  
  // Quick and snappy
  snappy: { stiffness: 300, damping: 30 },
  
  // Slow and smooth
  gentle: { stiffness: 120, damping: 14 },
  
  // Bouncy
  bouncy: { stiffness: 500, damping: 15 },
  
  // Stiff (minimal bounce)
  stiff: { stiffness: 210, damping: 20 }
};
```

### Spring Math

```javascript
// Spring physics calculation
function springStep(position, velocity, target, config, dt) {
  const { stiffness, damping, mass } = config;
  
  // Spring force: F = -k * x
  const springForce = -stiffness * (position - target);
  
  // Damping force: F = -c * v
  const dampingForce = -damping * velocity;
  
  // Acceleration: a = F / m
  const acceleration = (springForce + dampingForce) / mass;
  
  // Update velocity and position
  const newVelocity = velocity + acceleration * dt;
  const newPosition = position + newVelocity * dt;
  
  return { position: newPosition, velocity: newVelocity };
}
```

### 2. Card Slider Carousel (`crlq`)

Horizontal scrolling card carousel:

```javascript
<CardSlider
  items={models}
  renderItem={(model) => <ModelCard model={model} />}
  cardWidth={280}
  gap={16}
  showArrows={true}
  showDots={false}
  scrollBehavior="smooth"
  snapToCard={true}
/>
```

### Props

```javascript
CardSlider.propTypes = {
  // Data
  items: PropTypes.array.isRequired,
  renderItem: PropTypes.func.isRequired,
  
  // Layout
  cardWidth: PropTypes.number,        // Fixed card width
  minCardWidth: PropTypes.number,     // Or responsive width
  gap: PropTypes.number,              // Space between cards
  
  // Navigation
  showArrows: PropTypes.bool,         // Show prev/next arrows
  showDots: PropTypes.bool,           // Show dot indicators
  arrowPosition: PropTypes.oneOf(['inside', 'outside']),
  
  // Behavior
  scrollBehavior: PropTypes.oneOf(['smooth', 'instant']),
  snapToCard: PropTypes.bool,         // Snap scroll to cards
  autoPlay: PropTypes.bool,           // Auto advance
  autoPlayInterval: PropTypes.number, // ms between advances
  
  // Interaction
  enableDrag: PropTypes.bool,         // Drag to scroll
  dragThreshold: PropTypes.number,    // Min drag distance
  
  // Callbacks
  onScrollStart: PropTypes.func,
  onScrollEnd: PropTypes.func,
  onCardChange: PropTypes.func
};
```

### Momentum Scrolling

```javascript
// Drag-to-scroll with velocity projection
const handleDragEnd = (velocity) => {
  // Project where scroll would end based on velocity
  const projectedEnd = currentScroll + velocity * decayRate;
  
  // Find nearest card position
  const nearestCard = Math.round(projectedEnd / cardWidth);
  const targetScroll = nearestCard * cardWidth;
  
  // Animate with spring physics
  spring.animate(targetScroll, {
    initialVelocity: velocity,
    onUpdate: (value) => setScrollPosition(value)
  });
};
```

### Responsive Card Count

```javascript
// Calculate visible cards based on container width
const useResponsiveCards = (containerRef, cardWidth, gap) => {
  const [visibleCount, setVisibleCount] = useState(1);
  
  useEffect(() => {
    const updateCount = () => {
      const containerWidth = containerRef.current?.clientWidth ?? 0;
      const count = Math.floor((containerWidth + gap) / (cardWidth + gap));
      setVisibleCount(Math.max(1, count));
    };
    
    updateCount();
    window.addEventListener('resize', updateCount);
    return () => window.removeEventListener('resize', updateCount);
  }, [cardWidth, gap]);
  
  return visibleCount;
};
```

## Usage Examples

### Spring Animation

```jsx
function AnimatedCard({ isActive }) {
  const [style, setStyle] = useState({ scale: 1, y: 0 });
  const springRef = useRef(createSpring({ stiffness: 300, damping: 25 }));
  
  useEffect(() => {
    springRef.current.animate(isActive ? 1.1 : 1, {
      onUpdate: (scale) => setStyle(s => ({ ...s, scale }))
    });
  }, [isActive]);
  
  return (
    <div style={{ transform: `scale(${style.scale})` }}>
      Card content
    </div>
  );
}
```

### Model Carousel

```jsx
function RelatedModels({ models }) {
  return (
    <CardSlider
      items={models}
      renderItem={(model) => (
        <ModelCard
          model={model}
          showAuthor
          showStats
        />
      )}
      cardWidth={240}
      gap={16}
      showArrows
      enableDrag
    />
  );
}
```

### Homepage Slider

```jsx
function FeaturedModels() {
  const { models, loading } = useFeaturedModels();
  
  if (loading) {
    return <CardSliderSkeleton count={4} />;
  }
  
  return (
    <section className="featured">
      <h2>Featured Models</h2>
      <CardSlider
        items={models}
        renderItem={(model) => <FeaturedCard model={model} />}
        minCardWidth={300}
        gap={24}
        showArrows
        autoPlay
        autoPlayInterval={5000}
      />
    </section>
  );
}
```

## CSS Classes

```css
.card-slider { }
.card-slider__container { }
.card-slider__track { }
.card-slider__item { }

.card-slider__arrow { }
.card-slider__arrow--prev { }
.card-slider__arrow--next { }
.card-slider__arrow--disabled { }

.card-slider__dots { }
.card-slider__dot { }
.card-slider__dot--active { }
```

## Notes

- Filename is misleading - contains UI animations, not WebGL shaders
- Spring physics for natural-feeling animations
- Card slider supports drag, arrows, dots
- Responsive card count calculation
- Momentum-based scrolling
