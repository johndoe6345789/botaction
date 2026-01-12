# error_messages.js

## Overview

Despite its filename, this file contains **Sketchfab's core Redux state management infrastructure** - NOT error message handling. This is the central state management layer for the Sketchfab web application, handling authentication, entities, messages, and search functionality.

## File Information

- **Status**: Active webpack bundle
- **Size**: ~147KB (minified)
- **Type**: Redux state management infrastructure
- **Bundle Hash**: Part of Sketchfab's main application chunks

## Core Modules

### 1. Authentication State (`authUser`)

Manages user authentication state, sessions, and user-related actions:

```javascript
// Action Types
v.GET_LIKES
v.GET_PURCHASES  
v.GET_SUBSCRIPTIONS
v.GET_FOLLOWINGS
v.GET_UPVOTES
v.INIT_CLIENT
v.GET_FROM_PREFETCHED
v.AUTHENTICATE
v.LOGOUT
v.SIGNUP
v.LOGIN
v.LIKE_MODEL / v.UNLIKE_MODEL
v.SUBSCRIBE / v.UNSUBSCRIBE
v.FOLLOW / v.UNFOLLOW
v.SET_ALLOWS_RESTRICTED
v.UPVOTE_REVIEW / v.DOWNVOTE_REVIEW
v.CAN_REVIEW_MODEL
v.UPDATE_AVATAR
```

### 2. State Selectors (`S` object)

```javascript
S = {
  isInflated: e => null !== e.authUser.uid,
  uid: e => e.authUser.uid,
  user: e => getEntity(e.authUser.uid, userSchema, e.entities),
  isAuthenticated: e => S.isInflated(e) && S.user(e).isAnonymous !== true,
  isLimited: e => !S.isAuthenticated(e) || S.user(e).isLimited,
  allowsRestricted: e => e.authUser.allowsRestricted,
  isSeller: e => e.authUser.isSeller,
  isStaff: e => S.isAuthenticated(e) && S.user(e).isStaff,
  canAccessFeature: (feature, state) => S.user(state).features.includes(feature),
  likes: e => e.authUser.likes,
  doesLike: (modelId, state) => state.authUser.likes[modelId] || false,
  hasPurchased: (modelId, state) => state.authUser.purchases[modelId] || false,
  hasSubscribed: (collectionId, state) => state.authUser.subscriptions[collectionId] || false,
  doesFollow: (userId, state) => state.authUser.followings[userId] || false,
  hasCredits: e => hasRemainingCredits(S.user(e)),
  plan: e => S.user(e).isAnonymous ? "basic" : S.user(e).account,
  getOrgRole: memoize((orgId, state) => /* returns org role */)
}
```

### 3. Entity Normalization (`entities`)

Uses normalizr for API response normalization:

```javascript
// Entity Schemas
const schemas = {
  models: new Entity('models'),
  users: new Entity('users'),
  collections: new Entity('collections'),
  categories: new Entity('categories'),
  licenses: new Entity('licenses'),
  comments: new Entity('comments'),
  reviews: new Entity('reviews'),
  orgs: new Entity('orgs'),
  orgMembers: new Entity('orgMembers'),
  orgProjects: new Entity('orgProjects'),
  materials: new Entity('materials'),
  activities: new Union({...}, 'verb')
}

// Entity relationships
models.define({ user, license, categories: [categories], org, orgProject })
users.define({ models: [models] })
comments.define({ user })
```

### 4. Messages/Notifications (`messages`)

Flash message system:

```javascript
// Actions
g.add(message)           // Add persistent message
g.addMultiple(messages)  // Add multiple messages
g.remove(uid)            // Remove by ID
g.flash(message, 5000)   // Show for 5 seconds then remove

// Message types: 'success', 'warning', 'error', 'info'
```

### 5. Organization Search (`orgGlobalSearch`)

```javascript
// State
{
  query: "",
  filters: { sortBy: "-createdAt", type: ["models", "projects"] },
  models: paginationState,
  folders: paginationState
}

// Actions
FIRST_MODELS, NEXT_MODELS, FIRST_FOLDERS, NEXT_FOLDERS
ADD_MODEL, DELETE_MODEL, DELETE_FOLDER, RESET_SEARCH
```

### 6. Pagination Utilities (`pagination`)

Cursor-based pagination:

```javascript
// State
{ list: [], cursors: { next: null, previous: null }, loading: 'none' }

// Loading states: 'none', 'refresh', 'next', 'previous'

// Selectors
list(state), cursors(state), isLoading(state), hasNextPage(state), hasPreviousPage(state)
```

## Utility Functions

### Number Formatting

```javascript
formatWithCommas(1000000)  // "1,000,000"
formatCurrency(1299)       // "$12.99"
formatRating(4.5)          // "4.5/5"
formatCompact(1500000)     // "1.5M"
formatFileSize(1048576)    // "1MB"
```

### Search Query Parser

```javascript
// Parses: "tag:vehicle user:john sports car"
// Returns: { tags: ["vehicle"], user: "john", q: "sports car" }
```

## Architecture

```
Action Creator → Effect Middleware → Reducer → Selectors → UI
                      ↓
              API calls, cookies, localStorage
```

## Dependencies

- normalizr (entity normalization)
- Custom effect middleware
- Memoized selectors
- Deep merge utilities
