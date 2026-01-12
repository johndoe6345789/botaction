# viewer_cache.js

## Overview

This file contains the **Lodash utility library** - NOT caching functionality. Lodash provides comprehensive JavaScript utilities for array manipulation, object handling, and functional programming.

## File Information

- **Status**: Active webpack bundle
- **Size**: ~72KB (minified)
- **Type**: JavaScript utility library
- **Library**: Lodash (https://lodash.com)

## Core Utilities

### 1. Array Utilities

```javascript
// Chunk
_.chunk([1, 2, 3, 4, 5], 2);
// [[1, 2], [3, 4], [5]]

// Compact (remove falsy)
_.compact([0, 1, false, 2, '', 3]);
// [1, 2, 3]

// Difference
_.difference([1, 2, 3], [2, 3]);
// [1]

// Flatten
_.flatten([1, [2, [3, [4]]]]);  // [1, 2, [3, [4]]]
_.flattenDeep([1, [2, [3, [4]]]]);  // [1, 2, 3, 4]

// Uniq
_.uniq([1, 2, 2, 3, 3, 3]);
// [1, 2, 3]

_.uniqBy([{ x: 1 }, { x: 2 }, { x: 1 }], 'x');
// [{ x: 1 }, { x: 2 }]

// Intersection
_.intersection([1, 2], [2, 3]);
// [2]

// Zip
_.zip(['a', 'b'], [1, 2]);
// [['a', 1], ['b', 2]]
```

### 2. Collection Utilities

```javascript
// Map
_.map([1, 2, 3], n => n * 2);
// [2, 4, 6]

_.map(users, 'name');  // Pluck names
// ['John', 'Jane']

// Filter
_.filter(users, { active: true });
_.filter(users, user => user.age > 18);

// Find
_.find(users, { id: 1 });
_.find(users, user => user.name.startsWith('J'));

// GroupBy
_.groupBy(users, 'department');
// { sales: [...], marketing: [...] }

// SortBy
_.sortBy(users, ['name']);
_.sortBy(users, [user => user.name.toLowerCase()]);

// Reduce
_.reduce([1, 2, 3], (sum, n) => sum + n, 0);
// 6

// Partition
_.partition(users, { active: true });
// [[activeUsers], [inactiveUsers]]
```

### 3. Object Utilities

```javascript
// Get (with default)
_.get(object, 'a.b.c');
_.get(object, 'a.b.c', 'default');
_.get(object, ['a', 'b', 'c']);

// Set
_.set(object, 'a.b.c', value);

// Pick
_.pick(object, ['a', 'b']);
// { a: ..., b: ... }

// Omit
_.omit(object, ['secret', 'internal']);

// Merge (deep)
_.merge({ a: 1, b: { c: 2 } }, { b: { d: 3 } });
// { a: 1, b: { c: 2, d: 3 } }

// Clone
_.clone(object);      // Shallow
_.cloneDeep(object);  // Deep

// Keys/Values
_.keys(object);
_.values(object);
_.entries(object);

// MapKeys/MapValues
_.mapKeys(object, (v, k) => k.toUpperCase());
_.mapValues(object, v => v * 2);
```

### 4. Function Utilities

```javascript
// Debounce
const search = _.debounce(query => {
  fetchResults(query);
}, 300);

// Throttle
const handleScroll = _.throttle(() => {
  checkPosition();
}, 100);

// Once
const initialize = _.once(() => {
  setup();
});

// Memoize
const expensive = _.memoize(compute);

// Curry
const add = _.curry((a, b, c) => a + b + c);
add(1)(2)(3);  // 6
add(1, 2)(3);  // 6

// Partial
const greet = (greeting, name) => `${greeting}, ${name}!`;
const hello = _.partial(greet, 'Hello');
hello('World');  // 'Hello, World!'
```

### 5. Comparison Utilities

```javascript
// IsEqual (deep)
_.isEqual({ a: 1 }, { a: 1 });  // true

// IsEmpty
_.isEmpty([]);        // true
_.isEmpty({});        // true
_.isEmpty('');        // true
_.isEmpty(null);      // true

// Type checks
_.isArray(value);
_.isObject(value);
_.isFunction(value);
_.isString(value);
_.isNumber(value);
_.isBoolean(value);
_.isNull(value);
_.isUndefined(value);
_.isNil(value);       // null or undefined
_.isPlainObject(value);
```

### 6. String Utilities

```javascript
// Case conversion
_.camelCase('hello world');    // 'helloWorld'
_.kebabCase('helloWorld');     // 'hello-world'
_.snakeCase('helloWorld');     // 'hello_world'
_.startCase('helloWorld');     // 'Hello World'
_.capitalize('hello');         // 'Hello'
_.upperFirst('hello');         // 'Hello'

// Trim
_.trim('  hello  ');
_.trimStart('  hello');
_.trimEnd('hello  ');

// Pad
_.pad('abc', 8);        // '  abc   '
_.padStart('abc', 6);   // '   abc'
_.padEnd('abc', 6);     // 'abc   '

// Template
const compiled = _.template('Hello <%= name %>!');
compiled({ name: 'World' });  // 'Hello World!'
```

## Internal Data Structures

### ListCache (`lQSC`)

Key-value storage using array:

```javascript
// Used for small collections
class ListCache {
  set(key, value) { /* ... */ }
  get(key) { /* ... */ }
  has(key) { /* ... */ }
  delete(key) { /* ... */ }
  clear() { /* ... */ }
}
```

### MapCache (`x2Vm`)

Optimized key-value storage:

```javascript
// Uses Map when available
class MapCache {
  set(key, value) { /* ... */ }
  get(key) { /* ... */ }
  has(key) { /* ... */ }
  delete(key) { /* ... */ }
}
```

### Hash (`swKa`)

```javascript
// For string-only keys
class Hash {
  set(key, value) { /* ... */ }
  get(key) { /* ... */ }
}
```

### SetCache (`OKBR`)

```javascript
// For unique value storage
class SetCache {
  add(value) { /* ... */ }
  has(value) { /* ... */ }
}
```

### Stack (`6Q+K`)

```javascript
// Auto-promotes from ListCache to MapCache
class Stack {
  set(key, value) {
    // Uses ListCache for small sizes
    // Promotes to MapCache for larger sizes
  }
}
```

## Usage in Sketchfab

```javascript
// Deep cloning models
const modelCopy = _.cloneDeep(model);

// Debounced search
const debouncedSearch = _.debounce(searchModels, 300);

// Get nested properties safely
const authorName = _.get(model, 'user.displayName', 'Unknown');

// Group models by category
const byCategory = _.groupBy(models, 'category.name');

// Sort models
const sorted = _.sortBy(models, ['likeCount'], ['desc']);
```

## Notes

- Filename is misleading - contains Lodash, not caching logic
- Full Lodash library with all utilities
- Used extensively throughout Sketchfab codebase
- Tree-shakeable imports available in source
