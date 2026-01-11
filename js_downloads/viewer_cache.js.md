# viewer_cache.js

## Overview
Minified Sketchfab webpack chunk containing the complete Lodash utility library with data structures, collection methods, array operations, object manipulation, and functional programming utilities.

## File Status
- **Type**: Minified JavaScript (Webpack Bundle)
- **Chunk ID**: 2698
- **Minified**: Yes
- **Source Map**: Available (referenced in file)

## Key Components

### Data Structures

**ListCache** (Module "lQSC")
Array-based key-value store:
- `clear()` - Reset cache
- `delete(key)` - Remove entry
- `get(key)` - Retrieve value
- `has(key)` - Check existence
- `set(key, value)` - Store entry

**MapCache** (Module "swKa")
Hash-based cache with Map fallback:
- Optimized for large datasets
- String/symbol key optimization
- Automatic upgrade from ListCache

**SetCache** (Module "OKBR")
Set-like cache for unique values:
- `add(value)` / `push(value)`
- `has(value)`
- Uses `__lodash_hash_undefined__` sentinel

**Stack** (Module "6Q+K")
Stack with automatic MapCache upgrade:
- Starts as ListCache
- Upgrades at 200 items
- LIFO operations

### Array Operations

**Difference** (Module "R3Zc")
Compute array difference:
```javascript
difference(array, ...values)
// Returns items in array not in values
```

**Flatten** (Module "DBcq")
Flatten nested arrays:
- Configurable depth
- Handles spreadable symbols

**Unique** (Module "u5zv")
Remove duplicates:
- Optional iteratee transform
- Optional comparator function
- Set-based optimization

**Chunk** (Module "BstM")
Split array into chunks:
```javascript
chunk(['a', 'b', 'c', 'd'], 2)
// => [['a', 'b'], ['c', 'd']]
```

### Object Operations

**Clone** (Module "ocRW")
Deep/shallow cloning:
- `clone(value)` - Shallow clone
- `cloneDeep(value)` - Deep clone
- Handles circular references
- Supports all built-in types

**Merge** (Module "FqYX")
Deep merge objects:
```javascript
merge(object, ...sources)
// Deep recursive merge
```

**Pick/Omit** (Modules "R1Z3", "MndH")
Select/exclude properties:
```javascript
pick(object, ['a', 'b'])
omit(object, ['c'])
```

### Collection Methods

**Map** (Module "mv18")
Transform collections:
```javascript
map(collection, iteratee)
```

**Filter** (Module "IAxr")
Select matching items:
```javascript
filter(collection, predicate)
```

**Reduce** (Module "wgEG")
Accumulate values:
```javascript
reduce(collection, iteratee, accumulator)
```

**Find** (Module "X9mO")
Find first match:
```javascript
find(collection, predicate)
findIndex(array, predicate)
findLast(collection, predicate)
```

**GroupBy** (Module "uIBN")
Group by key:
```javascript
groupBy(collection, iteratee)
// => { key: [items] }
```

**SortBy** (Module "UZbZ")
Sort collection:
```javascript
sortBy(collection, iteratees)
```

### Function Utilities

**Debounce** (Module "Cgfs")
Delay execution:
- `leading` option
- `trailing` option
- `maxWait` option
- `cancel()` method
- `flush()` method

**Throttle** (Module "HPk7")
Rate-limit execution:
- Wraps debounce with maxWait

**Curry** (Module "YudV")
Create curried function:
- Partial application
- Placeholder support

**Compose** (Module "oQ3C")
Function composition:
```javascript
flow([func1, func2])
flowRight([func2, func1])
```

### String Operations

**CamelCase** (Module "43iM")
Convert to camelCase

**SnakeCase** (Module "Fnsp")
Convert to snake_case

**Capitalize** (Module "d94b")
Uppercase first letter

**Template** (Module "xr2m")
Template compilation:
- ERB-style delimiters
- Interpolation/evaluation
- HTML escaping

**Deburr** (Module "pbVo")
Remove diacritics:
```javascript
deburr('déjà vu')
// => 'deja vu'
```

### Type Checking

**isArray, isObject, isFunction** - Type predicates
**isEmpty** - Check empty values
**isEqual** - Deep equality
**isPlainObject** - Plain object check
**isTypedArray** - TypedArray check

### Utility Functions

**Identity** (Module "pShu")
Return input unchanged

**Noop** (Module "PKJd")
No-operation function

**UniqueId** (Module "AyNe")
Generate unique IDs

**Times** (Module "PjtK")
Call function N times

**Random** (Module "f9IZ")
Random number/element

## Dependencies
- None (self-contained)

## Technical Details
- Functional programming patterns
- Lazy evaluation support
- Chaining support
- Symbol support
- WeakMap for memory efficiency

## Use Cases
1. Data transformation
2. Collection manipulation
3. Object cloning/merging
4. Function composition
5. Type validation

## Notes
- Industry-standard utility library
- Tree-shakeable modules
- Comprehensive documentation
- Performance optimized
- 100+ utility functions
