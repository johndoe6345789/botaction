# viewer_core.js

## Overview

This file contains **Redux state management utilities and React hooks** for Sketchfab's UI components. It includes custom hooks for reducer management, button components, loading spinners, and pagination utilities.

## File Information

- **Status**: Active webpack bundle
- **Size**: ~73KB (minified)
- **Type**: React hooks and UI components
- **Framework**: React 18 with hooks

## Core Modules

### 1. useReducerWithMiddleware (`XuRc`)

Custom hook combining useReducer with middleware support:

```javascript
const useReducerWithMiddleware = (reducer, setState, getState, middlewares = []) => {
  const stateRef = useRef(reducer());
  
  const dispatch = useCallback((action) => {
    setState(prev => {
      const next = getState(prev, action);
      stateRef.current = next;
      return next;
    });
  }, []);
  
  const enhancedDispatch = useMemo(() => {
    let d = dispatch;
    const api = { getState: () => stateRef.current, dispatch: (...args) => d(...args) };
    middlewares.forEach(m => {
      d = m(api)(d);
    });
    return d;
  }, []);
  
  return [reducer(), enhancedDispatch];
};
```

### 2. Button Component (`vAnt`)

Versatile button with multiple states:

```javascript
<Button
  text="Submit"
  subtext="Save changes"
  onClick={handleClick}
  icon={<IconSave />}
  size="medium"           // 'small' | 'medium' | 'large'
  type="primary"          // 'primary' | 'secondary' | 'tertiary' | 'danger'
  disabled={false}
  loading={false}
  success={false}
  progress={0.5}          // 0-1 for progress bar
  htmlType="submit"
  href="/path"            // Renders as <a> if provided
/>

// CSS classes generated:
// button btn-primary btn-medium
// btn-loading (when loading)
// btn-disabled (when disabled)
```

### 3. Check/Success Indicator (`lMO9`)

Success checkmark animation:

```javascript
const SuccessCheck = () => (
  <div className="check" dangerouslySetInnerHTML={{
    __html: getMacro('front/macros/logo', 'spinner_check', [])
  }} />
);
```

### 4. Sketchfab Spinner (`wExz`)

Loading spinner component:

```javascript
const SketchfabSpinner = () => (
  <div className="sketchfab-spinner">
    <svg viewBox="0 0 13 16" xmlns="http://www.w3.org/2000/svg">
      <g fillRule="nonzero">
        <path className="shape1" d="M5.3029 8.1731L0 4.9864v5.8286l5.3029 3.1867z"/>
        <path className="shape2" d="M5.9987 6.9902l5.8157-3.495L5.9987 0 .1829 3.4953z"/>
        <path className="shape3" d="M6.6944 8.1731v5.8286l5.303-3.1867V4.9864z"/>
      </g>
    </svg>
  </div>
);
```

### 5. Infinite Scroll Hook (`hk5G`)

Automatic loading when scrolling near bottom:

```javascript
const useInfiniteScroll = (ref, loadMore, deps = [], scrollContainer = window) => {
  const threshold = useRef(Infinity);
  
  const checkScroll = useCallback(debounce(() => {
    const scrollY = scrollContainer === window 
      ? window.scrollY 
      : scrollContainer.scrollTop;
      
    if (scrollY > threshold.current) {
      loadMore().then(() => delay(300));
    }
  }, 200), [scrollContainer, ...deps]);
  
  useEffect(() => {
    scrollContainer.addEventListener('scroll', checkScroll, { passive: true });
    return () => scrollContainer.removeEventListener('scroll', checkScroll);
  }, [scrollContainer, checkScroll]);
  
  // Calculate threshold based on element position
  useEffect(() => {
    if (ref.current) {
      const containerHeight = scrollContainer === window 
        ? document.documentElement.scrollHeight 
        : scrollContainer.scrollHeight;
      const offset = containerHeight - (ref.current.offsetTop + ref.current.offsetHeight);
      threshold.current = containerHeight - (offset + 2 * window.innerHeight);
    }
  }, [scrollContainer, ref]);
};
```

### 6. Entity State Hook (`BR/Y`)

Redux-integrated entity normalization:

```javascript
const useEntityState = (reducer, initialState, schema, middlewares = []) => {
  const store = useContext(ReduxContext);
  const [state, setState] = useState(initialState);
  const entitiesRef = useRef({});
  
  const updateEntities = useCallback((data) => {
    const { entities } = normalize(data, schema);
    if (!isEmpty(entities) && !isEqual(entities, entitiesRef.current)) {
      entitiesRef.current = entities;
      store.dispatch(entitiesActions.update(entities));
    }
  }, [schema]);
  
  // Subscribe to entity store changes
  useEffect(() => {
    return subscribe(store, entitiesSelectors.all, (entities) => {
      // Update local state when global entities change
    });
  }, [schema]);
  
  return [state, dispatch];
};
```

### 7. Promise Memoization Hook (`pLUK`)

Prevents duplicate async calls:

```javascript
const useMemoizedPromise = (asyncFn) => {
  const promiseRef = useRef();
  
  return useCallback((...args) => {
    if (promiseRef.current) return promiseRef.current;
    
    promiseRef.current = asyncFn(...args)
      .catch(err => { promiseRef.current = undefined; throw err; })
      .then(result => { promiseRef.current = undefined; return result; });
    
    return promiseRef.current;
  }, [asyncFn]);
};
```

### 8. Paginated List Hook (`ajs0`)

Cursor-based pagination management:

```javascript
const usePaginatedList = (fetchFn, deps, options = {}) => {
  const { initialState = emptyPagination, reducer = paginationReducer, schema } = options;
  
  const fetch = useCallback((cursor) => 
    fetchFn(cursor).then(({ results, cursors }) => ({ list: results, cursors }))
  , deps);
  
  const [state, dispatch] = useEntityState(reducer, initialState, 
    schema ? { list: [schema] } : {});
  
  const onLoadFirst = useCallback(() => 
    dispatch(paginationActions.first(() => fetch(null))), [fetch]);
    
  const onLoadNext = useCallback(() => 
    dispatch(paginationActions.next((_, cursor) => fetch(cursor))), [fetch]);
    
  const onLoadPrevious = useCallback(() => 
    dispatch(paginationActions.previous((_, cursor) => fetch(cursor))), [fetch]);
    
  const onReset = useCallback(() => 
    dispatch(paginationActions.reset()), []);
  
  return {
    dispatch,
    onLoadFirst,
    onLoadNext,
    onLoadPrevious,
    onReset,
    list: paginationSelectors.list(state),
    loading: paginationSelectors.loading(state),
    isLoading: paginationSelectors.isLoading(state),
    hasPreviousPage: paginationSelectors.hasPreviousPage(state),
    hasNextPage: paginationSelectors.hasNextPage(state)
  };
};
```

## Dependencies

- React 18 (hooks, context)
- Redux (store subscription)
- normalizr (entity normalization)
- lodash utilities (isEmpty, isEqual, debounce)

## CSS Classes

```css
/* Button styles */
.button { }
.btn-primary { }
.btn-secondary { }
.btn-small { }
.btn-medium { }
.btn-large { }
.btn-loading { }
.btn-disabled { }
.button__text-container { }
.button__subtext { }
.button__progress { }

/* Spinner */
.sketchfab-spinner { }
.sketchfab-spinner svg { }
.shape1, .shape2, .shape3 { } /* Animated shapes */

/* Success check */
.check { }
```

## Usage Examples

### Button

```jsx
<Button
  text="Download"
  type="primary"
  size="large"
  loading={isDownloading}
  progress={downloadProgress}
  onClick={handleDownload}
/>
```

### Infinite Scroll

```jsx
function ModelList() {
  const containerRef = useRef();
  const { list, onLoadNext, hasNextPage } = usePaginatedList(fetchModels);
  
  useInfiniteScroll(containerRef, () => {
    if (hasNextPage) return onLoadNext();
  }, [hasNextPage]);
  
  return (
    <div ref={containerRef}>
      {list.map(model => <ModelCard key={model.uid} model={model} />)}
    </div>
  );
}
```

## Notes

- Designed for Sketchfab's specific state patterns
- Tightly integrated with normalizr for entity management
- Hooks handle complex async patterns safely
- Button component supports progress visualization
