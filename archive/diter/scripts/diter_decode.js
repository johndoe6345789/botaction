#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const vm = require("vm");
const { performance } = require("perf_hooks");
let webcrypto;
try {
  webcrypto = require("crypto").webcrypto;
} catch (err) {
  webcrypto = undefined;
}

function parseArgs(argv) {
  const args = { binz: null, params: null, out: null, debug: false };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--binz") {
      args.binz = argv[++i];
    } else if (arg === "--params") {
      args.params = argv[++i];
    } else if (arg === "--out") {
      args.out = argv[++i];
    } else if (arg === "--debug") {
      args.debug = true;
    }
  }
  if (!args.binz || !args.params || !args.out) {
    const msg = [
      "Usage:",
      "  node scripts/diter_decode.js --binz <file.binz> --params <params.json> --out <output.bin>",
    ].join("\n");
    throw new Error(msg);
  }
  return args;
}

function makeAtob() {
  return (str) => Buffer.from(str, "base64").toString("binary");
}

function makeBtoa() {
  return (str) => Buffer.from(str, "binary").toString("base64");
}

const blobMap = new Map();
let blobCounter = 0;

class BlobShim {
  constructor(parts, options) {
    this._parts = Array.isArray(parts) ? parts : [];
    this.type = options && options.type ? options.type : "";
  }

  _text() {
    return this._parts
      .map((part) => {
        if (typeof part === "string") {
          return part;
        }
        if (Buffer.isBuffer(part)) {
          return part.toString("utf8");
        }
        if (part instanceof ArrayBuffer) {
          return Buffer.from(part).toString("utf8");
        }
        if (ArrayBuffer.isView(part)) {
          return Buffer.from(part.buffer, part.byteOffset, part.byteLength).toString("utf8");
        }
        return String(part);
      })
      .join("");
  }
}

class BlobBuilderShim {
  constructor() {
    this._parts = [];
  }

  append(part) {
    this._parts.push(part);
  }

  getBlob(type) {
    return new BlobShim(this._parts, { type });
  }
}

const URLShim = {
  createObjectURL(blob) {
    const id = `blob:node-${++blobCounter}`;
    blobMap.set(id, blob);
    return id;
  },
  revokeObjectURL(id) {
    blobMap.delete(id);
  },
};

function decodeDataUrl(url) {
  const comma = url.indexOf(",");
  if (comma === -1) {
    throw new Error("Invalid data URL");
  }
  const meta = url.slice(5, comma);
  const data = url.slice(comma + 1);
  if (meta.includes(";base64")) {
    return Buffer.from(data, "base64").toString("utf8");
  }
  return decodeURIComponent(data);
}

class InlineWorker {
  constructor(url) {
    this.onmessage = null;
    this.onerror = null;
    this._listeners = {
      message: [],
      error: [],
    };
    this._terminated = false;

    const code = InlineWorker._resolveCode(url);
    this._context = InlineWorker._makeContext(this);

    try {
      const script = new vm.Script(code, { filename: "inline-worker.js" });
      script.runInNewContext(this._context);
    } catch (err) {
      this._emitError(err);
      throw err;
    }
  }

  static _resolveCode(url) {
    if (typeof url !== "string") {
      throw new Error("Worker URL must be a string");
    }
    if (url.startsWith("blob:")) {
      const blob = blobMap.get(url);
      if (!blob) {
        throw new Error(`Unknown blob URL: ${url}`);
      }
      return blob._text();
    }
    if (url.startsWith("data:")) {
      return decodeDataUrl(url);
    }
    if (fs.existsSync(url)) {
      return fs.readFileSync(url, "utf8");
    }
    throw new Error(`Unsupported worker URL: ${url}`);
  }

  static _makeContext(worker) {
    const ctx = {
      postMessage: (data) => worker._emitMessage(data),
      onmessage: null,
      close: () => worker.terminate(),
      console,
      WebAssembly,
      Uint8Array,
      Uint16Array,
      Uint32Array,
      Int8Array,
      Int16Array,
      Int32Array,
      Float32Array,
      Float64Array,
      ArrayBuffer,
      DataView,
      Date,
      Math,
      setTimeout,
      clearTimeout,
      setInterval,
      clearInterval,
      queueMicrotask,
      performance,
      atob: makeAtob(),
      btoa: makeBtoa(),
      TextEncoder: global.TextEncoder,
      TextDecoder: global.TextDecoder,
      crypto: global.crypto || webcrypto,
      navigator: { userAgent: "node" },
    };

    ctx.self = ctx;
    ctx.window = ctx;
    ctx.globalThis = ctx;
    return ctx;
  }

  addEventListener(type, listener) {
    if (this._listeners[type]) {
      this._listeners[type].push(listener);
    }
  }

  removeEventListener(type, listener) {
    if (!this._listeners[type]) {
      return;
    }
    const idx = this._listeners[type].indexOf(listener);
    if (idx >= 0) {
      this._listeners[type].splice(idx, 1);
    }
  }

  postMessage(data) {
    if (this._terminated) {
      return;
    }
    const handler = this._context.onmessage;
    if (typeof handler === "function") {
      queueMicrotask(() => handler({ data }));
    }
  }

  terminate() {
    this._terminated = true;
  }

  _emitMessage(data) {
    if (this._terminated) {
      return;
    }
    const event = { data };
    if (typeof this.onmessage === "function") {
      this.onmessage(event);
    }
    for (const listener of this._listeners.message) {
      listener(event);
    }
  }

  _emitError(err) {
    if (this._terminated) {
      return;
    }
    if (typeof this.onerror === "function") {
      this.onerror(err);
    }
    for (const listener of this._listeners.error) {
      listener(err);
    }
  }
}

function loadChunks(chunkPaths, registry) {
  const chunks = [];
  chunks.push = function push(chunk) {
    const modules = chunk[1];
    Object.assign(registry, modules);
  };

  global.self = global;
  global.window = global;
  global.Blob = BlobShim;
  global.BlobBuilder = BlobBuilderShim;
  global.WebKitBlobBuilder = BlobBuilderShim;
  global.MozBlobBuilder = BlobBuilderShim;
  global.MSBlobBuilder = BlobBuilderShim;
  global.URL = URLShim;
  global.webkitURL = URLShim;
  global.Worker = InlineWorker;
  global.atob = makeAtob();
  global.btoa = makeBtoa();
  global.TextEncoder = global.TextEncoder || require("util").TextEncoder;
  global.TextDecoder = global.TextDecoder || require("util").TextDecoder;
  if (!global.crypto && webcrypto) {
    global.crypto = webcrypto;
  }

  global.self.webpackChunksketchfab = chunks;

  for (const chunkPath of chunkPaths) {
    const code = fs.readFileSync(chunkPath, "utf8");
    vm.runInThisContext(code, { filename: chunkPath });
  }
}

function createWebpackRequire(registry) {
  const cache = {};
  function __webpack_require__(id) {
    if (cache[id]) {
      return cache[id].exports;
    }
    const factory = registry[id];
    if (!factory) {
      throw new Error(`Module not found: ${id}`);
    }
    const module = { exports: {} };
    cache[id] = module;
    factory.call(module.exports, module, module.exports, __webpack_require__);
    return module.exports;
  }

  __webpack_require__.d = (exports, definition) => {
    for (const key in definition) {
      if (Object.prototype.hasOwnProperty.call(definition, key) && !Object.prototype.hasOwnProperty.call(exports, key)) {
        Object.defineProperty(exports, key, { enumerable: true, get: definition[key] });
      }
    }
  };

  __webpack_require__.n = (module) => {
    const getter = module && module.__esModule ? () => module.default : () => module;
    __webpack_require__.d(getter, { a: getter });
    return getter;
  };

  __webpack_require__.o = (obj, prop) => Object.prototype.hasOwnProperty.call(obj, prop);

  __webpack_require__.r = (exports) => {
    if (typeof Symbol !== "undefined" && Symbol.toStringTag) {
      Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" });
    }
    Object.defineProperty(exports, "__esModule", { value: true });
  };

  return __webpack_require__;
}

function normalizeArrayBuffer(value) {
  if (!value) {
    return null;
  }
  if (value instanceof ArrayBuffer) {
    return value;
  }
  if (ArrayBuffer.isView(value)) {
    return value.buffer.slice(value.byteOffset, value.byteOffset + value.byteLength);
  }
  if (Buffer.isBuffer(value)) {
    return value.buffer.slice(value.byteOffset, value.byteOffset + value.byteLength);
  }
  return null;
}

async function run() {
  const args = parseArgs(process.argv.slice(2));
  const binzPath = path.resolve(args.binz);
  const paramsPath = path.resolve(args.params);
  const outPath = path.resolve(args.out);

  const params = JSON.parse(fs.readFileSync(paramsPath, "utf8"));
  if (!Array.isArray(params) || params.length === 0) {
    throw new Error("params.json must be a non-empty array");
  }
  const param = params[0];

  const buffer = fs.readFileSync(binzPath);
  const arrayBuffer = buffer.buffer.slice(buffer.byteOffset, buffer.byteOffset + buffer.byteLength);

  const registry = {};
  const chunkPaths = [
    path.resolve("js_downloads/remote/ec580af0b531503f94c740ca2873c32e-v2.js"),
    path.resolve("js_downloads/remote/5bcaa88525fab96faffe19e1ce66716c-v2.js"),
    path.resolve("js_downloads/remote/7aa463e7a4f2c770ab2436d6def75af2-v2.js"),
    path.resolve("js_downloads/remote/a25387388d9ea5501c87029166d396ac-v2.js"),
  ];

  loadChunks(chunkPaths, registry);
  const __webpack_require__ = createWebpackRequire(registry);

  const diterModule = __webpack_require__(/*! kbo/ */ "kbo/");
  const diter = diterModule && diterModule.Z ? diterModule.Z : diterModule;
  if (typeof diter !== "function") {
    throw new Error("Failed to load DITER decoder");
  }

  const start = Date.now();
  const decoded = await new Promise((resolve, reject) => {
    let settled = false;
    const timeout = setTimeout(() => {
      if (settled) {
        return;
      }
      settled = true;
      reject(new Error("DITER decode timed out"));
    }, 120000);

    try {
      const maybePromise = diter(arrayBuffer, param.b, param.v, param.d, (result) => {
        if (settled) {
          return;
        }
        settled = true;
        clearTimeout(timeout);
        resolve(result);
      });

      if (maybePromise && typeof maybePromise.then === "function") {
        maybePromise
          .then((result) => {
            if (settled) {
              return;
            }
            settled = true;
            clearTimeout(timeout);
            resolve(result);
          })
          .catch((err) => {
            if (settled) {
              return;
            }
            settled = true;
            clearTimeout(timeout);
            reject(err);
          });
      }
    } catch (err) {
      clearTimeout(timeout);
      reject(err);
    }
  });

  const decodedBuffer = normalizeArrayBuffer(decoded);
  if (!decodedBuffer) {
    throw new Error("DITER decode returned unsupported data type");
  }

  fs.mkdirSync(path.dirname(outPath), { recursive: true });
  fs.writeFileSync(outPath, Buffer.from(decodedBuffer));

  if (args.debug) {
    const ms = Date.now() - start;
    console.log(`Decoded ${Buffer.from(decodedBuffer).length} bytes in ${ms}ms`);
    const head = Buffer.from(decodedBuffer).slice(0, 32);
    console.log(`Head: ${head.toString("hex")}`);
  }
}

run().catch((err) => {
  console.error(err.message || err);
  process.exit(1);
});
