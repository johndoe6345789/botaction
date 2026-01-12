#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const acorn = require("acorn");
const astring = require("astring");

function parseArgs(argv) {
  const args = {
    input: "downloads/diter_standalone.js",
    output: "downloads/diter_standalone_deob.js",
    wasm: "downloads/diter_wasm_blob.js",
    renameLen: 2,
  };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--in") {
      args.input = argv[++i];
    } else if (arg === "--out") {
      args.output = argv[++i];
    } else if (arg === "--wasm") {
      args.wasm = argv[++i];
    } else if (arg === "--rename-len") {
      args.renameLen = Number(argv[++i]);
    }
  }
  return args;
}

function forEachChild(node, callback) {
  for (const value of Object.values(node)) {
    if (Array.isArray(value)) {
      for (const child of value) {
        if (child && typeof child.type === "string") {
          callback(child);
        }
      }
    } else if (value && typeof value.type === "string") {
      callback(value);
    }
  }
}

function walkWithParent(node, parent, callback) {
  callback(node, parent);
  forEachChild(node, (child) => walkWithParent(child, node, callback));
}

const RESERVED = new Set([
  "__registry",
  "__cache",
  "__webpack_require__",
  "module",
  "exports",
  "require",
  "console",
  "Math",
  "Date",
  "JSON",
  "Object",
  "Array",
  "String",
  "Number",
  "Boolean",
  "RegExp",
  "Error",
  "Symbol",
  "BigInt",
  "Uint8Array",
  "Uint16Array",
  "Uint32Array",
  "Int8Array",
  "Int16Array",
  "Int32Array",
  "Float32Array",
  "Float64Array",
  "ArrayBuffer",
  "DataView",
  "Promise",
  "Set",
  "Map",
  "WeakMap",
  "WeakSet",
  "Reflect",
  "Proxy",
  "Buffer",
  "global",
  "globalThis",
  "window",
  "self",
  "process",
  "arguments",
  "undefined",
  "NaN",
  "Infinity",
  "DITER_WASM_B64",
]);

function createScope(parent, type) {
  return {
    parent,
    type,
    renames: new Map(),
    usedNames: new Set(),
  };
}

function findFunctionScope(scope) {
  let current = scope;
  while (current && current.type !== "function") {
    current = current.parent;
  }
  return current || scope;
}

function shouldRename(name, renameLen, shorthandNames) {
  if (!name) {
    return false;
  }
  if (name.length > renameLen) {
    return false;
  }
  if (name.startsWith("__")) {
    return false;
  }
  if (RESERVED.has(name)) {
    return false;
  }
  if (shorthandNames.has(name)) {
    return false;
  }
  return true;
}

function makeName(prefix, scope, counters) {
  let name = "";
  do {
    counters[prefix] += 1;
    name = `__${prefix}_${counters[prefix]}`;
  } while (scope.usedNames.has(name) || RESERVED.has(name));
  scope.usedNames.add(name);
  return name;
}

function declareFixedName(original, fixedName, scope) {
  scope.usedNames.add(original);
  scope.usedNames.add(fixedName);
  scope.renames.set(original, fixedName);
}

function declareName(original, kind, scope, renameLen, shorthandNames, counters) {
  scope.usedNames.add(original);
  if (!shouldRename(original, renameLen, shorthandNames)) {
    return;
  }
  const prefix = kind === "fn" ? "fn" : kind === "arg" ? "arg" : kind === "cls" ? "cls" : "v";
  const newName = makeName(prefix, scope, counters);
  scope.renames.set(original, newName);
}

function collectPatternBindings(
  node,
  scope,
  kind,
  renameLen,
  shorthandNames,
  counters,
  moduleFactories,
  allowRename = true
) {
  if (!node) {
    return;
  }
  switch (node.type) {
    case "Identifier":
      if (allowRename) {
        declareName(node.name, kind, scope, renameLen, shorthandNames, counters);
      } else {
        scope.usedNames.add(node.name);
      }
      break;
    case "RestElement":
      collectPatternBindings(node.argument, scope, kind, renameLen, shorthandNames, counters, moduleFactories, allowRename);
      break;
    case "AssignmentPattern":
      collectPatternBindings(node.left, scope, kind, renameLen, shorthandNames, counters, moduleFactories, allowRename);
      collectScopes(node.right, scope, renameLen, shorthandNames, counters, moduleFactories);
      break;
    case "ArrayPattern":
      for (const element of node.elements) {
        collectPatternBindings(element, scope, kind, renameLen, shorthandNames, counters, moduleFactories, allowRename);
      }
      break;
    case "ObjectPattern":
      for (const prop of node.properties) {
        if (prop.type === "Property") {
          if (prop.computed) {
            collectScopes(prop.key, scope, renameLen, shorthandNames, counters, moduleFactories);
          }
          const isShorthand = prop.shorthand && prop.value && prop.key === prop.value;
          collectPatternBindings(
            prop.value,
            scope,
            kind,
            renameLen,
            shorthandNames,
            counters,
            moduleFactories,
            allowRename && !isShorthand
          );
        } else if (prop.type === "RestElement") {
          collectPatternBindings(
            prop.argument,
            scope,
            kind,
            renameLen,
            shorthandNames,
            counters,
            moduleFactories,
            allowRename
          );
        }
      }
      break;
    default:
      break;
  }
}

const scopeByNode = new WeakMap();

function collectScopes(node, scope, renameLen, shorthandNames, counters, moduleFactories = new Set()) {
  if (!node) {
    return;
  }
  switch (node.type) {
    case "Program": {
      const programScope = createScope(null, "function");
      scopeByNode.set(node, programScope);
      for (const child of node.body) {
        collectScopes(child, programScope, renameLen, shorthandNames, counters, moduleFactories);
      }
      return;
    }
    case "BlockStatement": {
      const blockScope = createScope(scope, "block");
      scopeByNode.set(node, blockScope);
      for (const child of node.body) {
        collectScopes(child, blockScope, renameLen, shorthandNames, counters, moduleFactories);
      }
      return;
    }
    case "FunctionDeclaration": {
      if (node.id && node.id.type === "Identifier") {
        const fnScope = findFunctionScope(scope);
        declareName(node.id.name, "fn", fnScope, renameLen, shorthandNames, counters);
      }
      const funcScope = createScope(scope, "function");
      scopeByNode.set(node, funcScope);
      const fixedParams = moduleFactories.has(node) ? ["module", "exports", "__webpack_require__"] : null;
      node.params.forEach((param, index) => {
        if (fixedParams && fixedParams[index] && param.type === "Identifier") {
          declareFixedName(param.name, fixedParams[index], funcScope);
        } else {
          collectPatternBindings(
            param,
            funcScope,
            "arg",
            renameLen,
            shorthandNames,
            counters,
            moduleFactories
          );
        }
      });
      collectScopes(node.body, funcScope, renameLen, shorthandNames, counters, moduleFactories);
      return;
    }
    case "FunctionExpression":
    case "ArrowFunctionExpression": {
      const funcScope = createScope(scope, "function");
      scopeByNode.set(node, funcScope);
      if (node.type === "FunctionExpression" && node.id && node.id.type === "Identifier") {
        declareName(node.id.name, "fn", funcScope, renameLen, shorthandNames, counters);
      }
      const fixedParams = moduleFactories.has(node) ? ["module", "exports", "__webpack_require__"] : null;
      node.params.forEach((param, index) => {
        if (fixedParams && fixedParams[index] && param.type === "Identifier") {
          declareFixedName(param.name, fixedParams[index], funcScope);
        } else {
          collectPatternBindings(
            param,
            funcScope,
            "arg",
            renameLen,
            shorthandNames,
            counters,
            moduleFactories
          );
        }
      });
      collectScopes(node.body, funcScope, renameLen, shorthandNames, counters, moduleFactories);
      return;
    }
    case "CatchClause": {
      const catchScope = createScope(scope, "block");
      scopeByNode.set(node, catchScope);
      if (node.param) {
        collectPatternBindings(
          node.param,
          catchScope,
          "arg",
          renameLen,
          shorthandNames,
          counters,
          moduleFactories
        );
      }
      collectScopes(node.body, catchScope, renameLen, shorthandNames, counters, moduleFactories);
      return;
    }
    default:
      break;
  }

  if (node.type === "VariableDeclaration") {
    const targetScope = node.kind === "var" ? findFunctionScope(scope) : scope;
    for (const decl of node.declarations) {
      collectPatternBindings(
        decl.id,
        targetScope,
        "var",
        renameLen,
        shorthandNames,
        counters,
        moduleFactories
      );
      if (decl.init) {
        collectScopes(decl.init, scope, renameLen, shorthandNames, counters, moduleFactories);
      }
    }
    return;
  }

  if (node.type === "ClassDeclaration" && node.id && node.id.type === "Identifier") {
    declareName(node.id.name, "cls", scope, renameLen, shorthandNames, counters);
  }

  if (node.type === "ClassExpression") {
    const classScope = createScope(scope, "block");
    scopeByNode.set(node, classScope);
    if (node.id && node.id.type === "Identifier") {
      declareName(node.id.name, "cls", classScope, renameLen, shorthandNames, counters);
    }
    collectScopes(node.body, classScope, renameLen, shorthandNames, counters, moduleFactories);
    return;
  }

  forEachChild(node, (child) =>
    collectScopes(child, scope, renameLen, shorthandNames, counters, moduleFactories)
  );
}

function resolveName(scope, original) {
  let current = scope;
  while (current) {
    const mapped = current.renames.get(original);
    if (mapped) {
      return mapped;
    }
    current = current.parent;
  }
  return null;
}

function renamePattern(node, bindingScope) {
  if (!node) {
    return;
  }
  switch (node.type) {
    case "Identifier": {
      const mapped = bindingScope.renames.get(node.name);
      if (mapped) {
        node.name = mapped;
      }
      break;
    }
    case "RestElement":
      renamePattern(node.argument, bindingScope);
      break;
    case "AssignmentPattern":
      renamePattern(node.left, bindingScope);
      break;
    case "ArrayPattern":
      for (const element of node.elements) {
        renamePattern(element, bindingScope);
      }
      break;
    case "ObjectPattern":
      for (const prop of node.properties) {
        if (prop.type === "Property") {
          const isShorthand = prop.shorthand && prop.value && prop.key === prop.value;
          if (!isShorthand) {
            renamePattern(prop.value, bindingScope);
          }
        } else if (prop.type === "RestElement") {
          renamePattern(prop.argument, bindingScope);
        }
      }
      break;
    default:
      break;
  }
}

function isReferenceIdentifier(node, parent) {
  if (!parent) {
    return false;
  }
  if (parent.type === "MemberExpression" && parent.property === node && !parent.computed) {
    return false;
  }
  if (parent.type === "Property" && parent.key === node && !parent.computed) {
    return false;
  }
  if (parent.type === "Property" && parent.shorthand && parent.value === node) {
    return false;
  }
  if (parent.type === "MethodDefinition" && parent.key === node && !parent.computed) {
    return false;
  }
  if (parent.type === "LabeledStatement" && parent.label === node) {
    return false;
  }
  if ((parent.type === "BreakStatement" || parent.type === "ContinueStatement") && parent.label === node) {
    return false;
  }
  if (parent.type === "FunctionDeclaration" && parent.id === node) {
    return false;
  }
  if (parent.type === "FunctionExpression" && parent.id === node) {
    return false;
  }
  if (parent.type === "ClassDeclaration" && parent.id === node) {
    return false;
  }
  if (parent.type === "ClassExpression" && parent.id === node) {
    return false;
  }
  if (parent.type === "VariableDeclarator" && parent.id === node) {
    return false;
  }
  if (parent.type === "CatchClause" && parent.param === node) {
    return false;
  }
  if (parent.type === "ImportSpecifier" || parent.type === "ImportDefaultSpecifier" || parent.type === "ImportNamespaceSpecifier") {
    return false;
  }
  return true;
}

function applyRenames(node, scope, parent) {
  if (!node) {
    return;
  }
  let currentScope = scope;
  const nodeScope = scopeByNode.get(node);
  if (nodeScope) {
    currentScope = nodeScope;
  }

  if (node.type === "FunctionDeclaration") {
    if (node.id && node.id.type === "Identifier") {
      const bindingScope = findFunctionScope(scope);
      const mapped = bindingScope.renames.get(node.id.name);
      if (mapped) {
        node.id.name = mapped;
      }
    }
  }

  if (node.type === "FunctionExpression" && node.id && node.id.type === "Identifier") {
    const mapped = currentScope.renames.get(node.id.name);
    if (mapped) {
      node.id.name = mapped;
    }
  }

  if (node.type === "ArrowFunctionExpression" || node.type === "FunctionExpression" || node.type === "FunctionDeclaration") {
    node.params.forEach((param) => renamePattern(param, currentScope));
  }

  if (node.type === "VariableDeclaration") {
    const bindingScope = node.kind === "var" ? findFunctionScope(currentScope) : currentScope;
    for (const decl of node.declarations) {
      renamePattern(decl.id, bindingScope);
    }
  }

  if (node.type === "ClassDeclaration" && node.id && node.id.type === "Identifier") {
    const mapped = currentScope.renames.get(node.id.name);
    if (mapped) {
      node.id.name = mapped;
    }
  }

  if (node.type === "ClassExpression" && node.id && node.id.type === "Identifier") {
    const mapped = currentScope.renames.get(node.id.name);
    if (mapped) {
      node.id.name = mapped;
    }
  }

  if (node.type === "CatchClause" && node.param) {
    renamePattern(node.param, currentScope);
  }

  if (node.type === "Identifier" && isReferenceIdentifier(node, parent)) {
    const mapped = resolveName(currentScope, node.name);
    if (mapped) {
      node.name = mapped;
    }
  }

  forEachChild(node, (child) => applyRenames(child, currentScope, node));
}

function extractWasmLiteral(ast) {
  let wasmLiteral = null;
  walkWithParent(ast, null, (node) => {
    if (wasmLiteral) {
      return;
    }
    if (node.type === "Literal" && typeof node.value === "string") {
      if (node.value.includes("AGFzbQE") && node.value.length > 1000) {
        wasmLiteral = node;
      }
    }
  });
  return wasmLiteral;
}

function replaceLiteralWithIdentifier(node, identifierName) {
  node.type = "Identifier";
  node.name = identifierName;
  delete node.value;
  delete node.raw;
}

function insertWasmRequire(ast, wasmPath) {
  const decl = {
    type: "VariableDeclaration",
    kind: "const",
    declarations: [
      {
        type: "VariableDeclarator",
        id: { type: "Identifier", name: "DITER_WASM_B64" },
        init: {
          type: "CallExpression",
          callee: { type: "Identifier", name: "require" },
          arguments: [
            {
              type: "Literal",
              value: wasmPath,
            },
          ],
          optional: false,
        },
      },
    ],
  };

  if (ast.body.length > 0) {
    const first = ast.body[0];
    if (
      first.type === "ExpressionStatement" &&
      first.expression &&
      first.expression.type === "Literal" &&
      first.expression.value === "use strict"
    ) {
      ast.body.splice(1, 0, decl);
      return;
    }
  }
  ast.body.unshift(decl);
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const inputPath = path.resolve(args.input);
  const outputPath = path.resolve(args.output);
  const wasmPath = path.resolve(args.wasm);

  if (!fs.existsSync(inputPath)) {
    throw new Error(`Input file not found: ${inputPath}`);
  }

  const code = fs.readFileSync(inputPath, "utf8");
  const ast = acorn.parse(code, {
    ecmaVersion: "latest",
    sourceType: "script",
    allowReturnOutsideFunction: true,
  });

  const shorthandNames = new Set();
  walkWithParent(ast, null, (node, parent) => {
    if (
      parent &&
      parent.type === "Property" &&
      parent.shorthand &&
      parent.value === node &&
      node.type === "Identifier"
    ) {
      shorthandNames.add(node.name);
    }
  });

  const moduleFactories = new Set();
  walkWithParent(ast, null, (node) => {
    if (node.type !== "AssignmentExpression") {
      return;
    }
    const left = node.left;
    if (!left || left.type !== "MemberExpression") {
      return;
    }
    if (!left.object || left.object.type !== "Identifier") {
      return;
    }
    if (left.object.name !== "__registry") {
      return;
    }
    const right = node.right;
    if (right && (right.type === "FunctionExpression" || right.type === "ArrowFunctionExpression")) {
      moduleFactories.add(right);
    }
  });

  const wasmLiteral = extractWasmLiteral(ast);
  if (wasmLiteral) {
    fs.mkdirSync(path.dirname(wasmPath), { recursive: true });
    fs.writeFileSync(wasmPath, `module.exports = ${JSON.stringify(wasmLiteral.value)};\n`);
    replaceLiteralWithIdentifier(wasmLiteral, "DITER_WASM_B64");
    insertWasmRequire(ast, `./${path.basename(wasmPath)}`);
  }

  const counters = { fn: 0, arg: 0, var: 0, cls: 0, v: 0 };
  collectScopes(ast, null, args.renameLen, shorthandNames, counters, moduleFactories);
  applyRenames(ast, scopeByNode.get(ast), null);

  const output = astring.generate(ast, {
    indent: "  ",
    lineEnd: "\n",
  });

  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, output);
  console.log(`Wrote deobfuscated output to ${outputPath}`);
  if (wasmLiteral) {
    console.log(`Extracted wasm blob to ${wasmPath}`);
  }
}

try {
  main();
} catch (err) {
  console.error(err.message || err);
  process.exit(1);
}
