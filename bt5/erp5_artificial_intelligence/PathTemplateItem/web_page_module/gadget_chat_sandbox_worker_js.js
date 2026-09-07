/*global self, WebAssembly, TextEncoder, TextDecoder, btoa, atob, importScripts */

(function (self) {
  "use strict";

  importScripts('watr.js');
  var wat2wasm = self.wat2wasm;   // exported by watr_js.js

  // =====================================================================
  // js/util.js - the small pieces exec.js needs (b64 codec, safe describe)
  // =====================================================================

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
   * Evaluate JavaScript. The code body may use `await` and receives `args`
   * and `utils` (b64encode/b64decode/describe). The value of the last
   * `return` — or of the whole source, if it is a single expression — is the
   * result.
   */
  async function execJS(code, args = null) {
    const logs = [];
    const record = (level) => (...parts) => {
      logs.push(`[${level}] ${parts.map((p) => describe(p, 2000)).join(' ')}`);
    };
    const sandboxConsole = {
      log: record('log'), info: record('info'), warn: record('warn'),
      error: record('error'), debug: record('debug'),
      table: record('table'), dir: record('dir'), trace: record('trace'),
    };

    let fn;
    const trimmed = code.trim();
    const looksLikeExpression = !/\breturn\b/.test(code) && !/[;{}\n]/.test(trimmed);
    try {
      if (!looksLikeExpression) throw new SyntaxError('not an expression');
      fn = new AsyncFunction('args', 'console', 'utils', `return (${trimmed});`);
    } catch {
      try {
        fn = new AsyncFunction('args', 'console', 'utils', code);
      } catch (err) {
        return { ok: false, error: `SyntaxError: ${err.message}`, resultText: '', logs };
      }
    }

    try {
      const result = await fn(args, sandboxConsole, { b64encode, b64decode, describe });
      return { ok: true, result: jsonable(result), resultText: describe(result), logs };
    } catch (err) {
      return { ok: false, error: `${err.name}: ${err.message}`, resultText: '', logs,
               stack: String(err.stack || '').split('\n').slice(0, 6).join('\n') };
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

  self.onmessage = async (event) => {
    const { id, kind, payload } = event.data;
    try {
      const result = kind === 'js'
        ? await execJS(payload.code, payload.args ?? null)
        : await execWasm(payload);
      self.postMessage({ id, ok: true, result });
    } catch (err) {
      self.postMessage({ id, ok: false, error: `${err.name}: ${err.message}` });
    }
  };
}(self));
