# viewer_settings.js

## Overview

This file contains the **Webpack runtime bootstrap** - the core webpack module loading and execution system. This is the webpack runtime that manages module loading, chunk loading, and inter-module communication.

## File Information

- **Status**: Core webpack runtime
- **Size**: ~18KB (minified)
- **Type**: Module system runtime
- **Build Tool**: Webpack 5

## Webpack Runtime Functions

### Module Cache

```javascript
// Webpack module cache
var __webpack_module_cache__ = {};

// Module execution function
function __webpack_require__(moduleId) {
  // Check if module is in cache
  var cachedModule = __webpack_module_cache__[moduleId];
  if (cachedModule !== undefined) {
    return cachedModule.exports;
  }
  
  // Create a new module and put it into the cache
  var module = __webpack_module_cache__[moduleId] = {
    id: moduleId,
    loaded: false,
    exports: {}
  };
  
  // Execute the module function
  __webpack_modules__[moduleId](module, module.exports, __webpack_require__);
  
  // Flag the module as loaded
  module.loaded = true;
  
  // Return the exports of the module
  return module.exports;
}
```

### Chunk Loading

```javascript
// Object to store loaded chunks
// "0" means "already loaded"
var installedChunks = {
  "main": 0
};

// Function to load a chunk
__webpack_require__.e = function(chunkId) {
  return Promise.all(
    Object.keys(__webpack_require__.f).reduce((promises, key) => {
      __webpack_require__.f[key](chunkId, promises);
      return promises;
    }, [])
  );
};

// JSONP chunk loading
__webpack_require__.f.j = function(chunkId, promises) {
  // Check if chunk is already loaded
  var installedChunkData = installedChunks[chunkId];
  
  if (installedChunkData !== 0) {
    // Chunk not loaded, load it
    if (installedChunkData) {
      promises.push(installedChunkData[2]);
    } else {
      // Create promise for chunk loading
      var promise = new Promise((resolve, reject) => {
        installedChunkData = installedChunks[chunkId] = [resolve, reject];
      });
      promises.push(installedChunkData[2] = promise);
      
      // Start chunk loading
      var url = __webpack_require__.p + chunkId + ".js";
      var script = document.createElement('script');
      script.src = url;
      document.head.appendChild(script);
    }
  }
};
```

### Module Exports Helpers

```javascript
// Define getter functions for harmony exports
__webpack_require__.d = function(exports, definition) {
  for (var key in definition) {
    if (__webpack_require__.o(definition, key) && 
        !__webpack_require__.o(exports, key)) {
      Object.defineProperty(exports, key, {
        enumerable: true,
        get: definition[key]
      });
    }
  }
};

// Object.prototype.hasOwnProperty.call
__webpack_require__.o = function(obj, prop) {
  return Object.prototype.hasOwnProperty.call(obj, prop);
};

// Mark module as ES module
__webpack_require__.r = function(exports) {
  if (typeof Symbol !== 'undefined' && Symbol.toStringTag) {
    Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
  }
  Object.defineProperty(exports, '__esModule', { value: true });
};
```

### Dynamic Imports

```javascript
// Dynamic import implementation
// import('./module.js') becomes:
__webpack_require__.e(/* import() */ "chunk-name")
  .then(__webpack_require__.bind(__webpack_require__, /* moduleId */ 12345))
  .then(module => {
    // Use module
  });
```

### Public Path

```javascript
// Get the public path for assets
__webpack_require__.p = "/static/js/";

// Used for loading chunks:
// /static/js/chunk-12345.js
```

### Module Factory

```javascript
// Module factories object
var __webpack_modules__ = {
  // Each module is a function
  "./src/index.js": function(module, exports, __webpack_require__) {
    "use strict";
    __webpack_require__.r(exports);
    
    // Module code here
    var _component = __webpack_require__("./src/component.js");
    
    console.log(_component.default);
  },
  
  "./src/component.js": function(module, exports, __webpack_require__) {
    "use strict";
    __webpack_require__.r(exports);
    __webpack_require__.d(exports, {
      "default": function() { return Component; }
    });
    
    function Component() { }
  }
};
```

### JSONP Callback

```javascript
// Chunk loaded callback (for async chunks)
var webpackJsonpCallback = function(data) {
  var chunkIds = data[0];
  var moreModules = data[1];
  var runtime = data[2];
  
  // Add modules to the modules object
  for (var moduleId in moreModules) {
    if (__webpack_require__.o(moreModules, moduleId)) {
      __webpack_modules__[moduleId] = moreModules[moduleId];
    }
  }
  
  // Execute runtime if provided
  if (runtime) runtime(__webpack_require__);
  
  // Mark chunks as loaded
  for (var i = 0; i < chunkIds.length; i++) {
    if (installedChunks[chunkIds[i]]) {
      installedChunks[chunkIds[i]][0]();  // Resolve promise
    }
    installedChunks[chunkIds[i]] = 0;
  }
};

// Install JSONP callback
var webpackJsonp = window["webpackJsonp"] = window["webpackJsonp"] || [];
webpackJsonp.push = webpackJsonpCallback;
```

### Module Interop

```javascript
// Get default export from module
__webpack_require__.n = function(module) {
  var getter = module && module.__esModule
    ? function() { return module['default']; }
    : function() { return module; };
  __webpack_require__.d(getter, { a: getter });
  return getter;
};

// CommonJS/AMD compatibility
// import x from 'cjs-module'
var _cjs_module = __webpack_require__("cjs-module");
var _cjs_module_default = __webpack_require__.n(_cjs_module);
```

### Hot Module Replacement (Development)

```javascript
// HMR runtime (development only)
__webpack_require__.h = function() {
  return "abc123";  // Current compilation hash
};

module.hot = {
  accept: function(dep, callback) {
    // Accept updates for dependency
  },
  decline: function(dep) {
    // Decline updates
  },
  dispose: function(callback) {
    // Cleanup before module is replaced
  },
  check: function() {
    // Check for updates
  },
  apply: function(options) {
    // Apply updates
  }
};
```

## Loading Flow

```
1. Initial Script Load
   └── Execute webpack runtime

2. Runtime Initialization
   ├── Set up module cache
   ├── Set up chunk loading
   └── Set up JSONP callback

3. Entry Point Execution
   └── __webpack_require__("./src/index.js")

4. Module Resolution
   ├── Check cache
   ├── Execute module factory
   └── Return exports

5. Async Chunk Loading (when needed)
   ├── Create script element
   ├── Wait for load
   └── Execute chunk modules
```

## Usage

```javascript
// This is internal webpack code, not directly used

// When you write:
import { Component } from './Component';

// Webpack compiles to:
var _Component = __webpack_require__("./src/Component.js");
console.log(_Component.Component);
```

## Notes

- Core webpack module loading system
- Handles synchronous and async (dynamic) imports
- Manages chunk loading for code splitting
- Provides CommonJS/ES module interop
- JSONP-based async chunk loading
- Critical infrastructure, not application code
