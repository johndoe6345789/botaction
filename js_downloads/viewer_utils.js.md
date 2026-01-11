# viewer_utils.js

## Overview
Minified Sketchfab webpack chunk containing model card components with rich features including thumbnail display, user attribution, like functionality, download badges, and AI-generated content indicators.

## File Status
- **Type**: Minified JavaScript (Webpack Bundle)
- **Chunk ID**: 8446
- **Minified**: Yes
- **Source Map**: Available (referenced in file)

## Key Components

### Module "r8wh" - Model Card Component
Feature-rich model card for grid displays:

**Component: ModelCard (D)**

**Props**:
| Prop | Default | Description |
|------|---------|-------------|
| `deferImages` | true | Lazy load images |
| `withStaffpickFlag` | true | Show staff pick badge |
| `withRestrictedFlag` | true | Show restricted badge |
| `withStaffpickLink` | false | Link staff pick badge |
| `renderQuickSettings` | - | Settings render function |
| `itemProp` | "owns" | Schema.org property |
| `model` | required | Model data object |

**Schema.org Markup**:
- `itemType="http://schema.org/3DModel"`
- `itemProp="commentCount"`, `name`, `url`, `isFamilyFriendly`
- Optional BlogPosting for associatedMedia

**Features**:
- Thumbnail with 360° preview on hover
- Staff pick and restricted badges
- Feature badges (animated, downloadable, AI)
- User/org attribution with avatar
- View count, comment count, like button
- Quick settings menu
- "Say Congrats" for recent staff picks

### Module "VOMu" - Model Features
Feature badge indicators:

**Component: ModelFeatures**

**Badges Displayed**:
- 🎬 **Animated**: Shows when `animationCount > 0`
- ⬇️ **Free Download**: Links to download (downloadType: "free")
- 🏪 **Store**: Shows for store items (downloadType: "store")
- ✨ **Fab AI**: Shows for AI-generated content (requires feature flag)

**Feature Flag Check**:
```javascript
canAccessFeature("ff_fab_ai_release")
```

### Module "DJY/" - Like Button
Interactive like/unlike button:

**Component: LikeButton**

**Props**:
- `likeCount` - Number of likes
- `doesLike` - Current user likes
- `onToggleLike` - Click handler
- `className` - Additional classes
- `tooltipClassName` - Tooltip position

**Features**:
- Star icon with count
- Toggle state (liked/unliked)
- Tooltip: "Like" or "Unlike"
- Formatted count display

### Module "NWyy" - Like Provider
State management for like functionality:

**Component: LikeProvider**

**Props**:
- `model` - Model object
- `children` - Render prop function

**Provides to Children**:
- `doesLike` - Boolean like state
- `onToggleLike` - Toggle function
- `likeCount` - Current count

**Redux Integration**:
- Selects from `entities.models`
- Dispatches `toggleLikeModel`
- Fetches `getDoesLike` on mount
- Caches model entity

## Dependencies
- React (memo, hooks)
- Redux (useSelector, useDispatch)
- Schema.org structured data
- Feature flag system

## Technical Details
- React.memo for performance
- Redux state for like sync
- Schema.org SEO markup
- Conditional feature flags
- Lazy image loading

## Use Cases
1. Model grid displays
2. Search results
3. User profile models
4. Category listings
5. Staff picks page

## Notes
- Optimized with React.memo (UID comparison)
- Full Schema.org 3DModel support
- Feature flag controlled AI badge
- Supports organization and user attribution
- Integrates with 360° preview system
