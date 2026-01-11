# webgl_recorder.js

## Overview

This file contains **React 18 DOM rendering and React-Redux state management** - NOT WebGL recording functionality. It's the core React runtime and Redux integration for Sketchfab's web application.

## File Information

- **Status**: Active webpack bundle
- **Size**: ~380KB (minified)
- **Type**: Core framework libraries
- **Libraries**: React 18, React DOM, React-Redux, Redux-Thunk

## React DOM (`react-dom`)

### Rendering APIs

```javascript
import { createRoot, hydrateRoot } from 'react-dom/client';

// Client-side rendering
const root = createRoot(document.getElementById('root'));
root.render(<App />);

// SSR hydration
const root = hydrateRoot(
  document.getElementById('root'),
  <App />
);

// Legacy render (deprecated in React 18)
import { render } from 'react-dom';
render(<App />, document.getElementById('root'));
```

### Portals

```javascript
import { createPortal } from 'react-dom';

function Modal({ children }) {
  return createPortal(
    <div className="modal">{children}</div>,
    document.getElementById('modal-root')
  );
}
```

### Concurrent Features

```javascript
// Suspense for data fetching
<Suspense fallback={<Loading />}>
  <AsyncComponent />
</Suspense>

// Transitions for non-urgent updates
const [isPending, startTransition] = useTransition();

startTransition(() => {
  // Low priority update
  setSearchResults(results);
});

// Deferred values
const deferredValue = useDeferredValue(value);
```

## React-Redux

### Provider

```javascript
import { Provider } from 'react-redux';
import store from './store';

function App() {
  return (
    <Provider store={store}>
      <RootComponent />
    </Provider>
  );
}
```

### Hooks

```javascript
import { useSelector, useDispatch } from 'react-redux';

function ModelCard({ modelId }) {
  // Select state
  const model = useSelector(state => 
    state.entities.models[modelId]
  );
  
  // Dispatch actions
  const dispatch = useDispatch();
  
  const handleLike = () => {
    dispatch(likeModel(modelId));
  };
  
  return (
    <div onClick={handleLike}>
      {model.name}
    </div>
  );
}
```

### Connect HOC (Legacy)

```javascript
import { connect } from 'react-redux';

const mapStateToProps = (state, ownProps) => ({
  model: state.entities.models[ownProps.modelId],
  isLiked: state.authUser.likes[ownProps.modelId]
});

const mapDispatchToProps = {
  likeModel,
  unlikeModel
};

export default connect(
  mapStateToProps, 
  mapDispatchToProps
)(ModelCard);
```

### useSyncExternalStore

```javascript
import { useSyncExternalStore } from 'react';

function useStore(selector) {
  return useSyncExternalStore(
    store.subscribe,
    () => selector(store.getState()),
    () => selector(store.getState())  // Server snapshot
  );
}
```

## Redux-Thunk

Async action creators:

```javascript
import { createAsyncThunk } from '@reduxjs/toolkit';

// Or manual thunk
const fetchModel = (modelId) => async (dispatch, getState) => {
  dispatch({ type: 'models/fetchPending' });
  
  try {
    const model = await api.getModel(modelId);
    dispatch({ type: 'models/fetchSuccess', payload: model });
  } catch (error) {
    dispatch({ type: 'models/fetchFailed', error: error.message });
  }
};

// Usage
dispatch(fetchModel('abc123'));
```

## React 18 Fiber Architecture

### Reconciliation

```javascript
// React's internal fiber node structure (conceptual)
const fiber = {
  tag: FunctionComponent,      // Component type
  type: MyComponent,           // Component function/class
  key: null,
  stateNode: domNode,          // DOM reference
  
  // Fiber tree links
  return: parentFiber,         // Parent
  child: firstChildFiber,      // First child
  sibling: nextSiblingFiber,   // Next sibling
  
  // State
  memoizedState: hooksList,    // Hooks linked list
  memoizedProps: props,
  
  // Effects
  flags: Update,               // Side effects to perform
  updateQueue: updates         // Pending updates
};
```

### Concurrent Rendering

```javascript
// React 18 enables concurrent features
// - Automatic batching
// - Transitions
// - Suspense improvements

// Automatic batching (all updates batched)
function handleClick() {
  setCount(c => c + 1);  // Batched
  setFlag(f => !f);      // Batched
  // Single re-render
}

// Even in async callbacks
setTimeout(() => {
  setCount(c => c + 1);  // Batched in React 18
  setFlag(f => !f);      // Batched in React 18
}, 100);
```

## Hooks Implementation

```javascript
// Internal hooks registry (conceptual)
const HooksDispatcher = {
  useState: (initialState) => {
    const hook = getWorkInProgressHook();
    if (isMount) {
      hook.memoizedState = initialState;
    }
    const setState = (action) => {
      scheduleUpdate(hook, action);
    };
    return [hook.memoizedState, setState];
  },
  
  useEffect: (create, deps) => {
    const hook = getWorkInProgressHook();
    const prevDeps = hook.memoizedState?.deps;
    if (depsChanged(prevDeps, deps)) {
      hook.memoizedState = { create, deps };
      scheduleEffect(create);
    }
  },
  
  // ... other hooks
};
```

## Batch Updates

```javascript
import { unstable_batchedUpdates } from 'react-dom';

// Force batching outside React event handlers
unstable_batchedUpdates(() => {
  setA(1);
  setB(2);
  setC(3);
  // Single re-render
});
```

## Usage in Sketchfab

```javascript
// Store setup
const store = configureStore({
  reducer: rootReducer,
  middleware: [thunk, effectMiddleware]
});

// Root component
function SketchfabApp() {
  return (
    <Provider store={store}>
      <Router>
        <App />
      </Router>
    </Provider>
  );
}

// Mount
const root = createRoot(document.getElementById('app'));
root.render(<SketchfabApp />);
```

## Notes

- Filename is misleading - contains React/Redux, not WebGL recording
- Full React 18 with concurrent features
- React-Redux for state management
- Redux-Thunk for async actions
- Critical runtime for Sketchfab's web application
