# viewer_exports.js

## Overview
Lodash utility functions bundle providing object manipulation, array operations, deep cloning, and general JavaScript utility methods used throughout the Sketchfab viewer.

## File Status
- **Type**: Minified Sketchfab Webpack Bundle
- **Webpack Chunk ID**: 7913
- **Source Map**: `fd3570ce9497bf551397979b128ca7d9-v2.js.map`

## Key Components

### Data Structures

#### Hash (35HM)
Hash table implementation for string keys:
- `clear()` - Remove all entries
- `delete()` - Remove entry
- `get()` - Retrieve value
- `has()` - Check existence
- `set()` - Add/update entry

#### ListCache (FGXF)
Array-based cache for small collections:
- Linear search for key lookup
- Efficient for < 200 entries

#### MapCache (gwo3)
Combined hash/map cache:
- Uses Hash for string keys
- Uses Map for object keys

#### Stack (DllV)
Stack data structure with automatic upgrade:
- Starts as ListCache
- Upgrades to MapCache at 200 entries

### Core Functions

#### Object Operations
| Function | Module | Description |
|----------|--------|-------------|
| `baseClone` | LJ9c | Deep/shallow clone implementation |
| `baseAssign` | r2Vd | Copy own properties |
| `copyObject` | 2nwn | Copy properties to target |
| `keys` | cOdH | Get own enumerable keys |
| `keysIn` | /Lws | Get all enumerable keys |

#### Array Operations
| Function | Module | Description |
|----------|--------|-------------|
| `arrayEach` | mGAD | Iterate array elements |
| `arrayFilter` | KSds | Filter array by predicate |
| `arrayMap` | 7IS0 | Transform array elements |
| `arrayPush` | q6xx | Push multiple values |
| `baseFlatten` | bGca | Flatten nested arrays |

#### Type Checking
| Function | Module | Description |
|----------|--------|-------------|
| `isArray` | sRKp | Check if array |
| `isBuffer` | rGHD | Check if Buffer |
| `isFunction` | w4u4 | Check if function |
| `isObject` | vIro | Check if object |
| `isTypedArray` | 7Cm+ | Check if typed array |
| `isMap` | m8g0 | Check if Map |
| `isSet` | y3ad | Check if Set |
| `isSymbol` | +TiO | Check if Symbol |

#### Path Operations
| Function | Module | Description |
|----------|--------|-------------|
| `baseGet` | cj4Z | Get nested property |
| `castPath` | qcmK | Convert to path array |
| `stringToPath` | 2Cw9 | Parse path string |
| `toKey` | Hrhq | Convert to property key |

### Exported Utilities

#### omit (Idx6)
Remove specified properties from object:
```javascript
omit(object, ['prop1', 'prop2']);
```

#### identity (q1eA)
Return first argument unchanged:
```javascript
identity(value) // => value
```

#### constant (XX4p)
Create function returning constant value:
```javascript
constant(42)() // => 42
```

#### toString (yMRO)
Convert value to string safely.

#### memoize (TWRx)
Cache function results:
```javascript
const cached = memoize(expensiveFn);
```

### Wrapper Classes

#### LodashWrapper (cELj)
Implicit chaining wrapper:
```javascript
_(array).map(fn).filter(fn).value()
```

#### LazyWrapper (bcdL)
Lazy evaluation wrapper for performance.

## Dependencies
- Native JavaScript APIs
- Symbol support detection
- Buffer detection (Node.js)
- Typed Array support

## Technical Details
- Modular architecture
- Tree-shakeable exports
- Native method delegation
- Cross-environment support
- Memory-efficient caching

## Use Cases
1. Deep object cloning
2. Property path access
3. Array transformations
4. Type detection
5. Function memoization
6. Object manipulation

## Notes
- Subset of full Lodash library
- Optimized for viewer needs
- Handles edge cases (circular refs, symbols)
- Compatible with all modern browsers
- Used for data transformation throughout viewer
