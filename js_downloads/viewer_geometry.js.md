# viewer_geometry.js

## Overview

This file contains **client-side routing system** for Sketchfab's SPA (Single Page Application) - NOT 3D geometry handling. It implements route matching, history management, and React page rendering.

## File Information

- **Status**: Active webpack bundle
- **Size**: ~54KB (minified)
- **Type**: SPA routing system
- **Framework**: Custom router with React

## Core Components

### 1. Router Class (`560e`)

Main routing system:

```javascript
const router = new Router({
  routes: routeDefinitions,
  container: document.getElementById('app'),
  onNavigate: (route, params) => {
    analytics.trackPageView(route.name);
  }
});

// Methods:
router.push('/models/abc123');           // Navigate with history push
router.replace('/models/def456');        // Navigate with history replace
router.reload();                         // Reload current route
router.back();                           // Go back
router.forward();                        // Go forward
```

### 2. Route Definition Helpers (`vxiz`)

```javascript
import { renderReactPage, redirectRoute } from './viewer_geometry';

const routes = [
  // React page route
  {
    name: 'model:view',
    path: '/models/:modelId',
    handler: renderReactPage(ModelPage),
    meta: { title: 'View Model' }
  },
  
  // Redirect route
  {
    name: 'legacy:model',
    path: '/3d-models/:slug',
    handler: redirectRoute(({ params }) => `/models/${params.slug}`)
  },
  
  // Route with data loading
  {
    name: 'user:profile',
    path: '/@:username',
    handler: renderReactPage(UserProfile),
    loader: async ({ params }) => {
      return { user: await fetchUser(params.username) };
    }
  }
];
```

## Route Matching

### Pattern Syntax

```javascript
// Static segments
'/about'                    // Matches exactly '/about'

// Parameters
'/models/:modelId'          // Matches '/models/abc123'
                           // params.modelId = 'abc123'

// Optional parameters
'/search/:query?'           // Matches '/search' or '/search/cars'

// Wildcard
'/docs/*'                   // Matches '/docs/anything/here'

// Regex constraints
'/users/:id(\\d+)'          // Only matches numeric IDs
```

### Route Matching Algorithm

```javascript
const matchRoute = (pathname, routes) => {
  for (const route of routes) {
    const pattern = createPattern(route.path);
    const match = pattern.exec(pathname);
    
    if (match) {
      return {
        route,
        params: extractParams(match, route.path),
        query: parseQueryString(location.search)
      };
    }
  }
  return null;  // 404
};
```

## React Page Rendering

### renderReactPage Helper

```javascript
const renderReactPage = (Component, options = {}) => {
  return async (context) => {
    const { params, query, loader } = context;
    
    // Load data if loader exists
    let data = {};
    if (options.loader) {
      data = await options.loader(context);
    }
    
    // Render or hydrate
    const container = document.getElementById('app');
    const element = <Component {...params} {...query} {...data} />;
    
    if (window.__HYDRATE__) {
      hydrateRoot(container, element);
      window.__HYDRATE__ = false;
    } else {
      createRoot(container).render(element);
    }
  };
};
```

### SSR Hydration Support

```javascript
// Server renders initial HTML with:
window.__INITIAL_STATE__ = { /* serialized state */ };
window.__HYDRATE__ = true;

// Client hydrates instead of full render
if (window.__HYDRATE__) {
  hydrateRoot(container, <App />);
} else {
  createRoot(container).render(<App />);
}
```

## Route Lifecycle Callbacks

```javascript
const route = {
  name: 'model:view',
  path: '/models/:modelId',
  handler: renderReactPage(ModelPage),
  
  // Called when route is first created
  onCreate: ({ params }) => {
    console.log('Route created');
  },
  
  // Called when params change (same route, different model)
  onUpdate: ({ params, prevParams }) => {
    if (params.modelId !== prevParams.modelId) {
      console.log('Model changed');
    }
  },
  
  // Called when leaving this route
  onRemove: () => {
    console.log('Route removed');
  },
  
  // Called at start of navigation
  onStartHandling: () => {
    showLoadingIndicator();
  },
  
  // Called at end of navigation
  onStopHandling: () => {
    hideLoadingIndicator();
  }
};
```

## Navigation Methods

### Programmatic Navigation

```javascript
// Push new history entry
router.push('/models/abc123');
router.push('/models/abc123', { replace: false });

// Replace current history entry
router.replace('/models/def456');

// Navigate with state
router.push('/models/abc123', { 
  state: { fromSearch: true, searchQuery: 'car' }
});

// Access navigation state
const { state } = useLocation();
if (state?.fromSearch) {
  showBackToSearchButton();
}
```

### Link Component

```javascript
import { Link } from './router';

// Internal link (uses router)
<Link to="/models/abc123">View Model</Link>

// With params
<Link to={`/models/${model.uid}`}>View Model</Link>

// With query string
<Link to="/search?q=cars&category=vehicles">Search Cars</Link>

// External link (normal <a>)
<Link to="https://external.com" external>External</Link>
```

## URL Parameters

### Named Parameters

```javascript
// Route: '/models/:modelId'
// URL: '/models/abc123'

const { params } = useParams();
console.log(params.modelId);  // 'abc123'
```

### Query Parameters

```javascript
// URL: '/search?q=cars&page=2'

const { query } = useLocation();
console.log(query.q);     // 'cars'
console.log(query.page);  // '2'
```

### Hash/Fragment

```javascript
// URL: '/models/abc123#comments'

const { hash } = useLocation();
console.log(hash);  // 'comments'
```

## Error Handling

### 404 Not Found

```javascript
const routes = [
  // ... other routes
  {
    name: 'notFound',
    path: '*',
    handler: renderReactPage(NotFoundPage)
  }
];
```

### Route Guards

```javascript
const protectedRoute = {
  name: 'settings',
  path: '/settings',
  handler: renderReactPage(SettingsPage),
  beforeEnter: async (context) => {
    if (!isAuthenticated()) {
      return { redirect: '/login?next=/settings' };
    }
    return true;  // Allow navigation
  }
};
```

## Usage Example

```javascript
// Initialize router
const router = new Router({
  routes: [
    {
      name: 'home',
      path: '/',
      handler: renderReactPage(HomePage)
    },
    {
      name: 'model:view',
      path: '/models/:modelId',
      handler: renderReactPage(ModelPage)
    },
    {
      name: 'user:profile',
      path: '/@:username',
      handler: renderReactPage(UserProfile)
    },
    {
      name: 'search',
      path: '/search',
      handler: renderReactPage(SearchPage)
    },
    {
      name: 'notFound',
      path: '*',
      handler: renderReactPage(NotFoundPage)
    }
  ]
});

// Start listening
router.start();
```

## Notes

- Filename is misleading - contains routing, not 3D geometry
- Custom implementation similar to React Router
- Supports SSR hydration
- History API based navigation
- Type-safe route definitions
