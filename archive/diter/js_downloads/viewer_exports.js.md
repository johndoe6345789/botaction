# viewer_exports.js

## Overview

This file contains **Lodash chain utilities** - chainable sequence methods from the Lodash utility library. It provides functional programming helpers for data transformation pipelines.

## File Information

- **Status**: Active webpack bundle
- **Size**: ~42KB (minified)
- **Type**: Utility library (Lodash chain)
- **Library**: Lodash

## Lodash Chain Methods

### Creating Chains

```javascript
import _ from 'lodash';

// Explicit chain
const result = _.chain(data)
  .filter(x => x.active)
  .map(x => x.value)
  .sum()
  .value();  // Execute chain

// Implicit chain (using wrapped value)
const wrapped = _(data);
const result = wrapped
  .filter(x => x.active)
  .map(x => x.value)
  .sum();  // Auto-unwraps for single value results
```

### Collection Methods

```javascript
// Filter
_.chain(users)
  .filter({ active: true })
  .filter(u => u.age > 18)
  .value();

// Map
_.chain(models)
  .map('name')
  .map(name => name.toUpperCase())
  .value();

// Reduce
_.chain(items)
  .reduce((acc, item) => acc + item.price, 0)
  .value();

// Sort
_.chain(users)
  .sortBy('name')
  .sortBy(u => -u.score)  // Descending
  .value();

// Group
_.chain(models)
  .groupBy('category')
  .mapValues(group => group.length)
  .value();
```

### Array Methods

```javascript
// Flatten
_.chain(nested)
  .flatten()
  .flattenDeep()
  .value();

// Unique
_.chain(items)
  .uniq()
  .uniqBy('id')
  .value();

// Chunk
_.chain(items)
  .chunk(3)
  .value();

// Take/Drop
_.chain(items)
  .take(5)
  .drop(2)
  .value();

// Compact (remove falsy)
_.chain(items)
  .compact()
  .value();
```

### Object Methods

```javascript
// Pick/Omit
_.chain(user)
  .pick(['name', 'email'])
  .omit(['password'])
  .value();

// Keys/Values
_.chain(object)
  .keys()
  .filter(k => k.startsWith('_'))
  .value();

// MapKeys/MapValues
_.chain(object)
  .mapKeys((v, k) => `prefix_${k}`)
  .mapValues(v => v * 2)
  .value();

// Merge
_.chain(defaults)
  .merge(userConfig)
  .value();
```

### String Methods

```javascript
// String transformations
_.chain(' hello world ')
  .trim()
  .camelCase()
  .value();  // 'helloWorld'

_.chain('hello_world')
  .kebabCase()
  .value();  // 'hello-world'

_.chain('helloWorld')
  .snakeCase()
  .value();  // 'hello_world'

_.chain('hello world')
  .startCase()
  .value();  // 'Hello World'
```

### Value Extraction

```javascript
// value() - Get final result
const result = _.chain(data).filter().map().value();

// head/first - Get first element
const first = _.chain(data).filter().head().value();

// last - Get last element
const last = _.chain(data).filter().last().value();

// size - Get count
const count = _.chain(data).filter().size().value();

// find - Get first match
const found = _.chain(data).find({ id: 123 }).value();
```

### Lazy Evaluation

```javascript
// Chains are lazy - operations only run when value() is called
const chain = _.chain(hugeArray)
  .filter(x => x > 100)
  .map(x => x * 2)
  .take(10);

// Nothing executed yet

const result = chain.value();  // Now it runs

// Short-circuit optimization
// Only processes items until 10 are found
```

## Common Patterns

### Data Transformation Pipeline

```javascript
const processModels = (models) => 
  _.chain(models)
    .filter({ published: true })
    .map(model => ({
      id: model.uid,
      name: model.name,
      thumbnail: model.thumbnails?.images?.[0]?.url,
      author: model.user?.displayName
    }))
    .sortBy('name')
    .value();
```

### Grouping and Counting

```javascript
const categoryStats = _.chain(models)
  .groupBy('category')
  .mapValues(group => ({
    count: group.length,
    totalViews: _.sumBy(group, 'viewCount'),
    avgLikes: _.meanBy(group, 'likeCount')
  }))
  .value();
```

### Nested Data Flattening

```javascript
const allTags = _.chain(models)
  .map('tags')
  .flatten()
  .uniq()
  .sort()
  .value();
```

### Search/Filter Pipeline

```javascript
const searchModels = (models, query, filters) =>
  _.chain(models)
    // Text search
    .filter(m => 
      m.name.toLowerCase().includes(query.toLowerCase())
    )
    // Category filter
    .filter(m => 
      !filters.category || m.category === filters.category
    )
    // Date filter
    .filter(m => 
      !filters.after || new Date(m.createdAt) > filters.after
    )
    // Sort
    .orderBy(
      [filters.sortBy || 'createdAt'],
      [filters.sortOrder || 'desc']
    )
    // Paginate
    .drop((filters.page - 1) * filters.pageSize)
    .take(filters.pageSize)
    .value();
```

### Aggregate Statistics

```javascript
const userStats = _.chain(models)
  .filter({ userId: user.id })
  .thru(userModels => ({
    totalModels: userModels.length,
    totalViews: _.sumBy(userModels, 'viewCount'),
    totalLikes: _.sumBy(userModels, 'likeCount'),
    avgViews: _.meanBy(userModels, 'viewCount') || 0,
    categories: _.uniq(_.map(userModels, 'category')),
    mostViewed: _.maxBy(userModels, 'viewCount'),
    mostLiked: _.maxBy(userModels, 'likeCount')
  }))
  .value();
```

## Chaining with Side Effects

```javascript
// tap - Execute side effect without modifying chain
_.chain(data)
  .filter(x => x.active)
  .tap(filtered => console.log('Filtered:', filtered.length))
  .map(x => x.value)
  .tap(values => analytics.track('processed', values.length))
  .value();

// thru - Transform the entire wrapped value
_.chain(data)
  .filter(x => x.active)
  .thru(arr => arr.length > 0 ? arr : defaultData)
  .value();
```

## Notes

- Filename is misleading - contains Lodash chain utilities, not export functions
- Lazy evaluation for performance
- Chainable functional transformations
- Useful for complex data pipelines
- Part of Lodash library used throughout Sketchfab
