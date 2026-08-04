/*global self, WebAssembly, TextEncoder, TextDecoder, btoa, atob, importScripts, indexedDB, fetch, eval */

(function (self) {
  "use strict";

  importScripts('watr.js');
  var wat2wasm = self.wat2wasm;

  var LIBRARY_DB_NAME = 'gadget_chat_library_cache';
  var LIBRARY_DB_STORE = 'libs';

  function openLibraryDb() {
    return new Promise((resolve, reject) => {
      const req = indexedDB.open(LIBRARY_DB_NAME, 1);
      req.onupgradeneeded = () => { req.result.createObjectStore(LIBRARY_DB_STORE); };
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    });
  }

  function libraryDbGet(db, key) {
    return new Promise((resolve, reject) => {
      const req = db.transaction(LIBRARY_DB_STORE, 'readonly').objectStore(LIBRARY_DB_STORE).get(key);
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    });
  }

  function libraryDbPut(db, key, value) {
    return new Promise((resolve, reject) => {
      const req = db.transaction(LIBRARY_DB_STORE, 'readwrite').objectStore(LIBRARY_DB_STORE).put(value, key);
      req.onsuccess = () => resolve();
      req.onerror = () => reject(req.error);
    });
  }

  /**
   * Resolve a bare https:// URL into a fetchable entry. `global` is left
   * null and loadLibraries() auto-detects it after eval. `.mjs` URLs are
   * treated as ES modules (dynamic `import()`), everything else as a
   * classic/UMD script (indirect `eval`).
   */
  function resolveEntry(nameOrUrl) {
    var file, extension, host;
    if (!/^https:\/\//.test(nameOrUrl)) {
      throw new Error('unknown library "' + nameOrUrl + '" - use an https:// URL');
    }
    file = (nameOrUrl.split('/').pop() || 'library').split('?')[0];
    extension = (file.split('.').pop() || '').toLowerCase();
    try {
      host = new URL(nameOrUrl).host;
    } catch (ignore) {
      host = nameOrUrl;
    }
    return {
      url: nameOrUrl,
      global: null,
      description: 'external library from ' + host,
      kind: extension === 'mjs' ? 'esm' : 'classic'
    };
  }

  /** Fetch (or reuse a cached copy of) an entry's source text, keyed by URL. */
  async function fetchLibrarySource(entry) {
    const db = await openLibraryDb();
    const cached = await libraryDbGet(db, entry.url);
    if (cached) return cached.source;
    const res = await fetch(entry.url);
    if (!res.ok) throw new Error(`fetching "${entry.url}" failed: HTTP ${res.status}`);
    const source = await res.text();
    await libraryDbPut(db, entry.url, { url: entry.url, source, fetched_at: Date.now() });
    return source;
  }

  /**
   * Load libraries by https:// URL, attaching each one onto this worker's
   * global scope (`self`) - classic/UMD bundles via indirect `eval`
   * (auto-detecting the global they attached), ES modules (`.mjs`) via a
   * blob-URL dynamic `import()` - and return a {url: value} map for code
   * that prefers `lib["<url>"]` over the auto-detected bare global.
   */
  async function loadLibraries(names) {
    const lib = {};
    for (const name of names || []) {
      const entry = resolveEntry(name);
      const source = await fetchLibrarySource(entry);

      if (entry.kind === 'esm') {
        const blobUrl = URL.createObjectURL(new Blob([source], { type: 'text/javascript' }));
        try {
          const mod = await import(/* webpackIgnore: true */ blobUrl);
          lib[name] = mod.default && Object.keys(mod).length === 1 ? mod.default : mod;
        } finally {
          URL.revokeObjectURL(blobUrl);
        }
        continue;
      }

      if (entry.global) {
        if (self[entry.global] === undefined) {
          (0, eval)(source); // indirect eval: runs as global-scope code, attaches onto self
        }
        lib[name] = self[entry.global];
        continue;
      }

      // Unknown global (external URL): eval and see what appeared, rather
      // than trusting a hard-coded export name.
      const before = Object.keys(self);
      (0, eval)(source);
      const appeared = Object.keys(self).filter((key) => before.indexOf(key) === -1 && self[key] !== undefined);
      if (!appeared.length) {
        throw new Error(`"${name}" attached no detectable global after loading - it may not be a UMD/IIFE `
          + 'bundle (an ES module needs an .mjs URL to be loaded correctly)');
      }
      lib[name] = self[appeared[appeared.length - 1]];
    }
    return lib;
  }

  function b64encode(bytes) {
    var s = '', i;
    for (i = 0; i < bytes.length; i += 0x8000) {
      s += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
    }
    return btoa(s);
  }

  function b64decode(text) {
    var raw = atob(text.replace(/\s+/g, '')), out = new Uint8Array(raw.length), i;
    for (i = 0; i < raw.length; i++) out[i] = raw.charCodeAt(i);
    return out;
  }

  function jsonSafe(_key, value) {
    if (typeof value === 'bigint') return `${value}n`;
    if (typeof value === 'function') return `[function ${value.name || 'anonymous'}]`;
    if (value instanceof Error) return `${value.name}: ${value.message}`;
    if (value instanceof Map) return Object.fromEntries(value);
    if (value instanceof Set) return [...value];
    if (value instanceof ArrayBuffer) return `[ArrayBuffer ${value.byteLength}]`;
    if (ArrayBuffer.isView(value)) return Array.from(value);
    return value;
  }

  /** Structured-clone-safe, size-bounded rendering of an arbitrary JS value. */
  function describe(value, maxLen = 4000) {
    let text;
    try {
      text = typeof value === 'string' ? value : JSON.stringify(value, jsonSafe, 2);
    } catch {
      text = String(value);
    }
    if (text === undefined) text = String(value);
    return text.length > maxLen ? text.slice(0, maxLen) + `\n… [truncated, ${text.length} chars total]` : text;
  }

  const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor;

  function jsonable(value) {
    try {
      return JSON.parse(JSON.stringify(value ?? null));
    } catch {
      return describe(value);
    }
  }

  /**
   * Evaluate JavaScript. The code body may use `await` and receives `args`,
   * `utils` (b64encode/b64decode/describe/wat2wasm) and `lib` (any
   * libraryNames requested, keyed by the URL passed - those are also
   * attached as their auto-detected global when the loaded bundle sets one).
   * The value of the last `return` - or of the whole source, if it is a
   * single expression - is the result.
   */
  async function execJS(code, args = null, libraryNames = []) {
    const logs = [];
    const record = (level) => (...parts) => {
      logs.push(`[${level}] ${parts.map((p) => describe(p, 2000)).join(' ')}`);
    };
    const sandboxConsole = {
      log: record('log'), info: record('info'), warn: record('warn'),
      error: record('error'), debug: record('debug'),
      table: record('table'), dir: record('dir'), trace: record('trace'),
    };

    let lib;
    try {
      lib = await loadLibraries(libraryNames);
    } catch (err) {
      return { ok: false, error: `library load failed: ${err.message}`, resultText: '', logs };
    }

    let fn;
    const trimmed = code.trim();
    const looksLikeExpression = !/\breturn\b/.test(code) && !/[;{}\n]/.test(trimmed);
    try {
      if (!looksLikeExpression) throw new SyntaxError('not an expression');
      fn = new AsyncFunction('args', 'console', 'utils', 'lib', `return (${trimmed});`);
    } catch {
      try {
        fn = new AsyncFunction('args', 'console', 'utils', 'lib', code);
      } catch (err) {
        return { ok: false, error: `SyntaxError: ${err.message}`, resultText: '', logs };
      }
    }

    try {
      const result = await fn(args, sandboxConsole, { b64encode, b64decode, describe, wat2wasm }, lib);
      return { ok: true, result: jsonable(result), resultText: describe(result), logs };
    } catch (err) {
      return { ok: false, error: `${err.name}: ${err.message}`, resultText: '', logs,
               stack: String(err.stack || '').split('\n').slice(0, 6).join('\n') };
    }
  }

  /** Just checks that `code` compiles as an async function body - never runs it. */
  function compileCheck(code) {
    try {
      new AsyncFunction('args', 'console', 'utils', 'lib', code);
      return { ok: true };
    } catch (err) {
      return { ok: false, error: `SyntaxError: ${err.message}` };
    }
  }

  /**
   * Assemble (if needed) and run a WebAssembly module.
   * @param {object} spec
   * @param {string} [spec.wat]           WAT source
   * @param {string} [spec.wasm_base64]   pre-assembled module
   * @param {Array<{name:string, args?:Array}>} [spec.calls]
   * @param {boolean} [spec.dump_memory]  include the first bytes of exported memory
   */
  async function execWasm(spec) {
    const logs = [];
    const out = { ok: false, logs, exports: [], calls: [] };
    let memory = null;

    const readString = (ptr, len) => {
      if (!memory) return '<no exported memory>';
      return new TextDecoder().decode(new Uint8Array(memory.buffer, ptr, len));
    };

    const imports = {
      env: {
        log_i32: (v) => logs.push(`[wasm] ${v | 0}`),
        log_i64: (v) => logs.push(`[wasm] ${v}`),
        log_f32: (v) => logs.push(`[wasm] ${v}`),
        log_f64: (v) => logs.push(`[wasm] ${v}`),
        log_str: (ptr, len) => logs.push(`[wasm] ${readString(ptr, len)}`),
        abort: (code) => { throw new Error(`wasm called env.abort(${code})`); },
        now: () => Date.now(),
        random: () => Math.random(),
      },
    };

    let binary;
    try {
      if (spec.wat) {
        binary = wat2wasm(spec.wat);
        out.wasm_bytes = binary.length;
        out.wasm_base64 = b64encode(binary);
      } else if (spec.wasm_base64) {
        binary = b64decode(spec.wasm_base64);
        out.wasm_bytes = binary.length;
      } else {
        out.error = 'provide "wat" or "wasm_base64"';
        return out;
      }
    } catch (err) {
      out.error = `WAT assembly failed: ${err.message}`;
      return out;
    }

    let instance;
    try {
      ({ instance } = await WebAssembly.instantiate(binary, imports));
    } catch (err) {
      out.error = `instantiation failed: ${err.message}`;
      try {
        const required = WebAssembly.Module.imports(await WebAssembly.compile(binary))
          .map((i) => `${i.module}.${i.name} (${i.kind})`);
        if (required.length) {
          out.error += `\nthe module imports: ${required.join(', ')}`
            + '\nrun_wasm only provides the env.* host functions.';
        }
      } catch { /* the binary is simply invalid */ }
      return out;
    }

    memory = instance.exports.memory instanceof WebAssembly.Memory ? instance.exports.memory : null;
    out.exports = Object.entries(instance.exports).map(([name, value]) =>
      `${name}: ${value instanceof WebAssembly.Memory ? 'memory'
        : value instanceof WebAssembly.Global ? 'global' : typeof value}`);

    for (const call of spec.calls || []) {
      const fn = instance.exports[call.name];
      if (typeof fn !== 'function') {
        out.calls.push({ name: call.name, error: `no exported function "${call.name}"` });
        continue;
      }
      const args = (call.args || []).map((a) => (typeof a === 'string' && /^-?\d+n$/.test(a) ? BigInt(a.slice(0, -1)) : a));
      try {
        const value = fn(...args);
        out.calls.push({ name: call.name, args: call.args || [], result: typeof value === 'bigint' ? `${value}n` : value ?? null });
      } catch (err) {
        out.calls.push({ name: call.name, args: call.args || [], error: `${err.name}: ${err.message}` });
      }
    }

    if (spec.dump_memory && memory) {
      const n = Math.min(Number(spec.dump_memory) || 128, memory.buffer.byteLength);
      const view = new Uint8Array(memory.buffer, 0, n);
      out.memory_head_hex = Array.from(view).map((b) => b.toString(16).padStart(2, '0')).join(' ');
      out.memory_head_text = new TextDecoder().decode(view).replace(/\0+/g, '·');
      out.memory_pages = memory.buffer.byteLength / 65536;
    }

    out.ok = true;
    return out;
  }

  /** Own + prototype property/method names of a loaded library's value, size-bounded. */
  function describeMembers(value) {
    const proto = Object.getPrototypeOf(value) || {};
    const keys = Object.keys(value).concat(Object.getOwnPropertyNames(proto));
    const seen = new Set();
    const members = [];
    for (const key of keys) {
      if (key === 'constructor' || key.charAt(0) === '_' || seen.has(key)) continue;
      seen.add(key);
      members.push(key);
      if (members.length >= 80) break;
    }
    return members;
  }

  /**
   * Load each named library URL (if not already cached) and report what it
   * actually exposes, so the agent can check a real API surface instead of
   * guessing from the name.
   */
  async function inspectLibraries(names) {
    const out = [];
    for (const name of names || []) {
      try {
        const entry = resolveEntry(name);
        const lib = await loadLibraries([name]);
        const value = lib[name];
        out.push({
          name, global: entry.global, description: entry.description, url: entry.url,
          type: typeof value, members: describeMembers(value),
        });
      } catch (err) {
        out.push({ name, error: err.message });
      }
    }
    return { ok: true, libraries: out };
  }

  self.onmessage = async (event) => {
    const { id, kind, payload } = event.data;
    try {
      let result;
      if (kind === 'js') {
        result = await execJS(payload.code, payload.args ?? null, payload.libraries ?? []);
      } else if (kind === 'wasm') {
        result = await execWasm(payload);
      } else if (kind === 'library_inspect') {
        result = await inspectLibraries(payload.libraries);
      } else if (kind === 'compile_check') {
        result = compileCheck(payload.code);
      } else {
        result = { ok: false, error: `unknown job kind "${kind}"` };
      }
      self.postMessage({ id, ok: true, result });
    } catch (err) {
      self.postMessage({ id, ok: false, error: `${err.name}: ${err.message}` });
    }
  };
}(self));
