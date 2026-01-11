# viewer_audio.js

## Overview
Minified Sketchfab webpack chunk containing UI components for model information display, popups, comment systems, metadata editing, and store model cards with comprehensive feature sets.

## File Status
- **Type**: Minified JavaScript (Webpack Bundle)
- **Chunk ID**: 9559
- **Minified**: Yes
- **Source Map**: Available (referenced in file)

## Key Components

### Module "uo4Z" - Prevent Page Scroll
Touch/wheel scroll containment utility:
- Prevents parent scroll on touch devices
- Handles wheel events
- Touch start/move/end management

### Module "l5lH" - Natural Sort
Human-friendly string comparison:
- Numeric-aware sorting
- Date recognition
- Case-insensitive option

### Module "xesV" - Comment Placeholder
Loading skeleton for comments:
- Rounded avatar placeholder
- Text line placeholders
- CSS class: `c-list-item-placeholder --comment`

### Module "isBB" - Popup Base
Generic popup component:

**Options**:
- `child` - Content component
- `title` - Header title
- `className` - Additional classes
- `isClosable` - Show close button
- `width` - Popup width

### Module "qlM8" - Model Information Popup
Model details display popup:
- Uses base popup wrapper
- Shows model metadata
- Inspect model action

### Module "Qbh+" - Popup Factory
Higher-order component for popups:
- Wraps content in popup shell
- Provides popup controller methods
- Methods: continue, cancel, open, close, remove, show, hide, resize, autofocus

### Module "zoil" - Twemoji Integration
Emoji parsing with Twemoji:
- CDN: `cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2`
- Returns parsed HTML

### Module "Q63v" - Description Display
Model description component:
- Markdown rendered content
- Edit link for owners
- Empty state handling

### Module "bWE4" - Comment Editor
Rich comment input component:

**Features**:
- @mention autocomplete
- Emoji picker integration
- Debounced user search
- Textarea auto-resize
- Touch/keyboard support

**Props**:
- `value` - Current text
- `onChange` - Text change handler
- `placeholder` - Input placeholder
- `orgUid` - Organization context
- `autofocus` - Auto-focus on mount

### Module "Nhfk" - Emoji Utilities
Emoji text processing:
- `:emoji:` syntax parsing
- Search emoji by name
- Convert shortcodes to unicode
- Smile/heart shortcuts

### Module "TUnU" - Deleted User Name
Display for deleted users:
- Shows "Deleted user" text
- No link/interaction

### Module "4z7H" - Report Link (Legacy)
Report abuse link to FAQ:
- Builds URL with parameters
- Opens in new tab

### Module "u3Zj" - Store Model Card
E-commerce model card:

**Features**:
- Schema.org 3DModel markup
- Star rating display
- Review count
- Price display
- Add to cart button
- 360° preview on hover

### Module "NYqo" - Report Link (DSA)
Digital Services Act compliant reporting:
- Links to Fab report system
- Content type/URL/ID params

### Module "EZio" - Cart Provider
Shopping cart state management:
- Add to cart functionality
- Purchase status check
- Cart limit handling
- Loading states

### Module "xtOe" - Processing Status
Model processing/reprocess detection:
- Version polling
- Reupload vs reprocess context
- Status tracking

### Module "XOQx" - License Display
Creative Commons license view:
- License label/fullname
- Requirements display
- Learn more link
- Material variant

### Module "5Y1a" - Comment Body
Comment text renderer:
- Deleted comment handling
- URL linkification
- Emoji parsing
- Empty message state

### Module "5+EH" - Comment System
Full comment implementation:
- Comment form
- Comment list
- Pagination
- Delete/reply actions
- Optimistic updates

### Module "zmmp" - Version Review
Model version comparison UI:
- Side-by-side preview
- Accept/decline actions
- Reupload vs reprocess labels

### Module "nd6d" - Model Information
Comprehensive model details:
- Geometry stats (triangles, vertices)
- Format information
- Texture/material counts
- License display
- File sizes

## Dependencies
- React (components, hooks, refs)
- Redux (state management)
- jQuery (autocomplete)
- Nunjucks (templates)
- Day.js (dates)

## Technical Details
- Component composition
- HOC pattern for popups
- Optimistic UI updates
- Schema.org structured data
- Suspense/lazy loading

## Use Cases
1. Model page information
2. Comment systems
3. Store product cards
4. Version management
5. Report functionality

## Notes
- Major UI component library
- E-commerce integration
- Accessibility considerations
- DSA compliance features
