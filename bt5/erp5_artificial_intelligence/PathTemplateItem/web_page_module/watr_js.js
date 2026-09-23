/*global self */
// Vendored: watr 5.10.1 - wat2wasm in JS: compile WebAssembly text (WAT) to
// wasm binary. Parse, print, minify, optimize. Zero deps.
// https://github.com/dy/watr - https://watr.js.org/
//
// Spec-complete (passes the official WebAssembly testsuite), so - unlike a
// hand-rolled assembler would be - it supports the FULL instruction set
// including tables/call_indirect/SIMD/bulk memory.
//
// Loaded via importScripts() from gadget_chat_sandbox_worker.js, a classic
// (non-module) Worker - this file therefore has no import/export of its own,
// and executes in that same Worker global scope under the SAME Content-
// Security-Policy as the rest of it (importScripts() does not fetch or apply
// a separate CSP per imported file - the worker has exactly one CSP list,
// established once from the worker's own top-level script response). See
// gadget_chat_sandbox_worker_js.js's header comment for why that CSP is
// empty here. Everything below is private to this file's own closure except
// the one explicit export at the bottom, self.wat2wasm - mirrors this
// project's window.ChatTools/window.ChatSkills export convention, just on
// the Worker global (self) instead of the page global (window).
//
// Vendored verbatim (unminified dist/watr.js build) except for stripping the
// trailing ESM `export { ... }` statement and wrapping in an IIFE so its ~115
// internal helper names (compile, parse, assemble, print, backend, ...) stay
// out of the Worker global scope. WAT-format bugs almost certainly belong
// upstream at github.com/dy/watr/issues, not in this file - re-vendor a newer
// release rather than hand-editing this block.
//
// MIT License
//
// Copyright (c) Dmitry Ivanov
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.
(function (self) {
  "use strict";

var __defProp = Object.defineProperty;
var __export = (target, all) => {
  for (var name2 in all)
    __defProp(target, name2, { get: all[name2], enumerable: true });
};

// src/encode.js
var encode_exports = {};
__export(encode_exports, {
  f16: () => f16,
  f32: () => f32,
  f64: () => f64,
  i16: () => i16,
  i32: () => i32,
  i64: () => i64,
  i8: () => i8,
  uleb: () => uleb,
  uleb5: () => uleb5,
  v128: () => v128
});

// src/util.js
var errLoc;
var errSrc;
var LOC = /^;;@(?:[ \t]+(.*?):(\d+):(\d+)(?::(\S+))?)?[ \t]*\r?\n?$/;
var err = (text, pos = errLoc) => {
  if (pos != null && errSrc) {
    let line = 1, col = 1;
    for (let i = 0; i < pos && i < errSrc.length; i++) {
      if (errSrc.charCodeAt(i) === 10) line++, col = 1;
      else col++;
    }
    text += ` at ${line}:${col}`;
    const at = errSrc.lastIndexOf(";;@", pos);
    if (at >= 0) {
      const eol = errSrc.indexOf("\n", at);
      const m = LOC.exec(errSrc.slice(at, eol < 0 ? errSrc.length : eol));
      if (m?.[1] != null) text += ` (${m[1]}:${m[2]}:${m[3]})`;
    }
  }
  throw Error(text);
};
var setErrLoc = (loc2) => {
  errLoc = loc2;
};
var setErrSrc = (src) => {
  errSrc = src;
};
var getErrLoc = () => errLoc;
var getErrSrc = () => errSrc;
var sepRE = /^_|_$|[^\da-f]_|_[^\da-f]/i;
var intRE = /^[+-]?(?:0x[\da-f]+|\d+)$/i;
var tenc = new TextEncoder();
var tdec = new TextDecoder("utf-8", { fatal: true, ignoreBOM: true });
var utf8 = (s) => [...tenc.encode(s)];
var escape = { n: 10, r: 13, t: 9, '"': 34, "'": 39, "\\": 92 };
var str = (s) => {
  let bytes = [], i = 1, code, c, buf = "";
  const commit = () => (buf && bytes.push(...tenc.encode(buf)), buf = "");
  while (i < s.length - 1) {
    c = s[i++], code = null;
    if (c === "\\") {
      if (s[i] === "u") {
        i++, i++;
        c = String.fromCodePoint(parseInt(s.slice(i, i = s.indexOf("}", i)), 16));
        i++;
      } else if (escape[s[i]]) code = escape[s[i++]];
      else if (!isNaN(code = parseInt(s[i] + s[i + 1], 16))) i++, i++;
      else c += s[i];
    }
    code != null ? (commit(), bytes.push(code)) : buf += c;
  }
  commit();
  bytes.valueOf = () => s;
  return bytes;
};
var unescape = (s) => tdec.decode(new Uint8Array(str(s)));

// src/encode.js
var uleb = (n, buffer = []) => {
  if (n == null) return buffer;
  if (typeof n === "string") n = /[_x]/i.test(n) ? BigInt(n.replaceAll("_", "")) : i32.parse(n);
  if (typeof n === "bigint") {
    while (true) {
      const byte2 = Number(n & 0x7Fn);
      n >>= 7n;
      if (n === 0n) {
        buffer.push(byte2);
        break;
      }
      buffer.push(byte2 | 128);
    }
    return buffer;
  }
  let byte = n & 127;
  n >>>= 7;
  if (n === 0) {
    buffer.push(byte);
    return buffer;
  }
  buffer.push(byte | 128);
  return uleb(n, buffer);
};
function uleb5(value) {
  const result = [];
  for (let i = 0; i < 5; i++) {
    let byte = value & 127;
    value >>>= 7;
    if (i < 4) {
      byte |= 128;
    }
    result.push(byte);
  }
  return result;
}
var I32_MEMO = /* @__PURE__ */ new Map();
function i32(n, buffer = []) {
  if (typeof n === "string") {
    let v = I32_MEMO.get(n);
    if (v === void 0) {
      v = i32.parse(n);
      if (I32_MEMO.size > 65536) I32_MEMO.clear();
      I32_MEMO.set(n, v);
    }
    n = v;
  }
  while (true) {
    const byte = Number(n & 127);
    n >>= 7;
    if (n === 0 && (byte & 64) === 0 || n === -1 && (byte & 64) !== 0) {
      buffer.push(byte);
      break;
    }
    buffer.push(byte | 128);
  }
  return buffer;
}
var cleanInt = (v) => !sepRE.test(v) && intRE.test(v = v.replaceAll("_", "")) ? v : err(`Bad int ${v}`);
var i8 = i32;
var i16 = i32;
i32.parse = (n) => {
  n = parseInt(cleanInt(n));
  if (n < -2147483648 || n > 4294967295) err(`i32 constant out of range`);
  return n;
};
function i64(n, buffer = []) {
  if (typeof n === "string") n = i64.parse(n);
  else if (typeof n === "number") n = BigInt(n);
  if (typeof n === "bigint" && n > 0x7fffffffffffffffn) {
    n = n - 0x10000000000000000n;
  }
  while (true) {
    const byte = Number(n & 0x7Fn);
    n >>= 7n;
    if (n === 0n && (byte & 64) === 0 || n === -1n && (byte & 64) !== 0) {
      buffer.push(byte);
      break;
    }
    buffer.push(byte | 128);
  }
  return buffer;
}
var _buf = new ArrayBuffer(8);
var _u8 = new Uint8Array(_buf);
var _i32 = new Int32Array(_buf);
var _f32 = new Float32Array(_buf);
var _f64 = new Float64Array(_buf);
var _i64 = new BigInt64Array(_buf);
var _u64 = new BigUint64Array(_buf);
i64.parse = (n) => {
  n = cleanInt(n);
  const neg = n[0] === "-";
  const body = neg || n[0] === "+" ? n.slice(1) : n;
  let max;
  if (body[0] === "0" && (body[1] === "x" || body[1] === "X")) {
    const hex = body.slice(2).replace(/^0+/, "") || "0";
    max = neg ? "8000000000000000" : "ffffffffffffffff";
    if (hex.length > 16 || hex.length === 16 && hex.toLowerCase() > max) err(`i64 constant out of range`);
  } else {
    const dec = body.replace(/^0+/, "") || "0";
    max = neg ? "9223372036854775808" : "18446744073709551615";
    if (dec.length > max.length || dec.length === max.length && dec > max) err(`i64 constant out of range`);
  }
  let bi = BigInt(body);
  if (neg) bi = 0n - bi;
  _i64[0] = bi;
  return _i64[0];
};
var F32_SIGN = 2147483648;
var F32_NAN = 2139095040;
var F32_QUIET = 4194304;
function f32(input, out, value, idx) {
  if (typeof input === "string" && (idx = input.indexOf("nan")) >= 0) {
    if (input[idx + 3] === ":") {
      const tail = input.slice(idx + 4);
      value = tail === "canonical" || tail === "arithmetic" ? F32_QUIET : i32.parse(tail);
    } else value = F32_QUIET;
    value = (value | F32_NAN) >>> 0;
    if (input[0] === "-") value = (value | F32_SIGN) >>> 0;
    _i32[0] = value | 0;
  } else {
    value = typeof input === "string" ? f32.parse(input) : input;
    _f32[0] = value;
  }
  if (out) {
    out.push(_u8[0], _u8[1], _u8[2], _u8[3]);
    return;
  }
  return [_u8[0], _u8[1], _u8[2], _u8[3]];
}
var F16_SIGN = 32768;
var F16_NAN = 31744;
var F16_QUIET = 512;
function f16(input, out, value, idx) {
  let bits;
  if (typeof input === "string" && (idx = input.indexOf("nan")) >= 0) {
    if (input[idx + 3] === ":") {
      const tail = input.slice(idx + 4);
      bits = tail === "canonical" || tail === "arithmetic" ? F16_QUIET : i32.parse(tail) & 1023;
    } else bits = F16_QUIET;
    bits |= F16_NAN;
    if (input[0] === "-") bits |= F16_SIGN;
  } else {
    value = typeof input === "string" ? f64.parse(input) : input;
    bits = f16.bits(value);
    if ((bits & 32767) === F16_NAN && isFinite(value)) err(`f16 constant out of range`);
  }
  if (out) {
    out.push(bits & 255, bits >>> 8);
    return;
  }
  return [bits & 255, bits >>> 8];
}
f16.bits = (v) => {
  _f64[0] = v;
  const b = _u64[0];
  const sign = Number(b >> 48n) & F16_SIGN;
  const e = Number(b >> 52n & 0x7ffn), m = b & 0xfffffffffffffn;
  if (e === 2047) return sign | F16_NAN | (m ? F16_QUIET : 0);
  if (e === 0) return sign;
  const E = e - 1023;
  if (E > 15) return sign | F16_NAN;
  const full = 1n << 52n | m;
  const shift = 42 + (E < -14 ? -14 - E : 0);
  if (shift > 53) return sign;
  let half = Number(full >> BigInt(shift));
  if (full >> BigInt(shift - 1) & 1n) {
    if ((full & (1n << BigInt(shift - 1)) - 1n) !== 0n || half & 1) half++;
  }
  if (E >= -14) {
    let exp = E + 15;
    if (half >= 2048) half >>= 1, exp++;
    if (exp >= 31) return sign | F16_NAN;
    return sign | exp << 10 | half & 1023;
  }
  if (half >= 1024) return sign | 1024;
  return sign | half;
};
var F64_SIGN = 0x8000000000000000n;
var F64_NAN = 0x7ff0000000000000n;
var F64_QUIET = 0x8000000000000n;
var F64_MEMO = /* @__PURE__ */ new Map();
function f64(input, out, value, idx) {
  if (typeof input === "string") {
    const m = F64_MEMO.get(input);
    if (m !== void 0) {
      if (out) {
        out.push(m[0], m[1], m[2], m[3], m[4], m[5], m[6], m[7]);
        return;
      }
      return m.slice();
    }
  }
  if (typeof input === "string" && (idx = input.indexOf("nan")) >= 0) {
    if (input[idx + 3] === ":") {
      const tail = input.slice(idx + 4);
      value = tail === "canonical" || tail === "arithmetic" ? F64_QUIET : i64.parse(tail);
    } else value = F64_QUIET;
    value |= F64_NAN;
    if (input[0] === "-") value |= F64_SIGN;
    _i64[0] = value;
  } else {
    value = typeof input === "string" ? f64.parse(input) : input;
    _f64[0] = value;
  }
  if (typeof input === "string") {
    if (F64_MEMO.size > 65536) F64_MEMO.clear();
    F64_MEMO.set(input, [_u8[0], _u8[1], _u8[2], _u8[3], _u8[4], _u8[5], _u8[6], _u8[7]]);
  }
  if (out) {
    out.push(_u8[0], _u8[1], _u8[2], _u8[3], _u8[4], _u8[5], _u8[6], _u8[7]);
    return;
  }
  return [_u8[0], _u8[1], _u8[2], _u8[3], _u8[4], _u8[5], _u8[6], _u8[7]];
}
f64.parse = (input, max = Number.MAX_VALUE) => {
  input = input.replaceAll("_", "");
  let sign = 1;
  if (input[0] === "-") sign = -1, input = input.slice(1);
  else if (input[0] === "+") input = input.slice(1);
  if (input[1] === "x") {
    let [sig, exp = "0"] = input.split(/p/i);
    let [int, fract = ""] = sig.split(".");
    let flen = fract.length ?? 0;
    let intVal = 0;
    for (let i = int.length - 1; i >= 2; i--) {
      let digit = parseInt(int[i], 16);
      intVal += digit * 16 ** (int.length - 1 - i);
    }
    let fractVal = fract ? parseInt("0x" + fract) / 16 ** flen : 0;
    exp = parseInt(exp, 10);
    let value = sign * (intVal + fractVal) * 2 ** exp;
    value = Math.max(-max, Math.min(max, value));
    return value;
  }
  if (input.includes("nan")) return sign < 0 ? NaN : NaN;
  if (input.includes("inf")) return sign * Infinity;
  return sign * parseFloat(input);
};
f32.parse = (input) => f64.parse(input, 34028234663852886e22);
var v128 = (input) => {
  let n = typeof input === "string" ? BigInt(input.replaceAll("_", "")) : BigInt(input);
  let arr = new Uint8Array(16);
  for (let i = 0; i < 16; i++) arr[i] = Number(n & 0xffn), n >>= 8n;
  return [...arr];
};

// src/const.js
var TABLE = [
  // 0x00-0x0a: control
  "unreachable",
  "nop",
  "block block",
  "loop block",
  "if block",
  "else",
  "then",
  8,
  "throw tagidx",
  10,
  "throw_ref",
  // 0x0b-0x19: control
  "end end",
  "br labelidx",
  "br_if labelidx",
  "br_table br_table",
  "return",
  "call funcidx",
  "call_indirect call_indirect",
  "return_call funcidx",
  "return_call_indirect call_indirect",
  "call_ref typeidx",
  "return_call_ref typeidx",
  // 0x1a-0x1f: parametric
  26,
  "drop",
  "select select",
  31,
  "try_table try_table",
  // 0x20-0x27: variable
  "local.get localidx",
  "local.set localidx",
  "local.tee localidx",
  "global.get globalidx",
  "global.set globalidx",
  "table.get tableidx",
  "table.set tableidx",
  // 0x28-0x3e: memory
  40,
  "i32.load memarg",
  "i64.load memarg",
  "f32.load memarg",
  "f64.load memarg",
  "i32.load8_s memarg",
  "i32.load8_u memarg",
  "i32.load16_s memarg",
  "i32.load16_u memarg",
  "i64.load8_s memarg",
  "i64.load8_u memarg",
  "i64.load16_s memarg",
  "i64.load16_u memarg",
  "i64.load32_s memarg",
  "i64.load32_u memarg",
  "i32.store memarg",
  "i64.store memarg",
  "f32.store memarg",
  "f64.store memarg",
  "i32.store8 memarg",
  "i32.store16 memarg",
  "i64.store8 memarg",
  "i64.store16 memarg",
  "i64.store32 memarg",
  // 0x3f-0x40: memory size/grow
  "memory.size opt_memory",
  "memory.grow opt_memory",
  // 0x41-0x44: const
  "i32.const i32",
  "i64.const i64",
  "f32.const f32",
  "f64.const f64",
  // 0x45-0x4f: i32 comparison
  "i32.eqz",
  "i32.eq",
  "i32.ne",
  "i32.lt_s",
  "i32.lt_u",
  "i32.gt_s",
  "i32.gt_u",
  "i32.le_s",
  "i32.le_u",
  "i32.ge_s",
  "i32.ge_u",
  // 0x50-0x5a: i64 comparison
  "i64.eqz",
  "i64.eq",
  "i64.ne",
  "i64.lt_s",
  "i64.lt_u",
  "i64.gt_s",
  "i64.gt_u",
  "i64.le_s",
  "i64.le_u",
  "i64.ge_s",
  "i64.ge_u",
  // 0x5b-0x60: f32 comparison
  "f32.eq",
  "f32.ne",
  "f32.lt",
  "f32.gt",
  "f32.le",
  "f32.ge",
  // 0x61-0x66: f64 comparison
  "f64.eq",
  "f64.ne",
  "f64.lt",
  "f64.gt",
  "f64.le",
  "f64.ge",
  // 0x67-0x78: i32 arithmetic
  "i32.clz",
  "i32.ctz",
  "i32.popcnt",
  "i32.add",
  "i32.sub",
  "i32.mul",
  "i32.div_s",
  "i32.div_u",
  "i32.rem_s",
  "i32.rem_u",
  "i32.and",
  "i32.or",
  "i32.xor",
  "i32.shl",
  "i32.shr_s",
  "i32.shr_u",
  "i32.rotl",
  "i32.rotr",
  // 0x79-0x8a: i64 arithmetic
  "i64.clz",
  "i64.ctz",
  "i64.popcnt",
  "i64.add",
  "i64.sub",
  "i64.mul",
  "i64.div_s",
  "i64.div_u",
  "i64.rem_s",
  "i64.rem_u",
  "i64.and",
  "i64.or",
  "i64.xor",
  "i64.shl",
  "i64.shr_s",
  "i64.shr_u",
  "i64.rotl",
  "i64.rotr",
  // 0x8b-0x98: f32 arithmetic
  "f32.abs",
  "f32.neg",
  "f32.ceil",
  "f32.floor",
  "f32.trunc",
  "f32.nearest",
  "f32.sqrt",
  "f32.add",
  "f32.sub",
  "f32.mul",
  "f32.div",
  "f32.min",
  "f32.max",
  "f32.copysign",
  // 0x99-0xa6: f64 arithmetic
  "f64.abs",
  "f64.neg",
  "f64.ceil",
  "f64.floor",
  "f64.trunc",
  "f64.nearest",
  "f64.sqrt",
  "f64.add",
  "f64.sub",
  "f64.mul",
  "f64.div",
  "f64.min",
  "f64.max",
  "f64.copysign",
  // 0xa7-0xc4: conversions (no immediates)
  "i32.wrap_i64",
  "i32.trunc_f32_s",
  "i32.trunc_f32_u",
  "i32.trunc_f64_s",
  "i32.trunc_f64_u",
  "i64.extend_i32_s",
  "i64.extend_i32_u",
  "i64.trunc_f32_s",
  "i64.trunc_f32_u",
  "i64.trunc_f64_s",
  "i64.trunc_f64_u",
  "f32.convert_i32_s",
  "f32.convert_i32_u",
  "f32.convert_i64_s",
  "f32.convert_i64_u",
  "f32.demote_f64",
  "f64.convert_i32_s",
  "f64.convert_i32_u",
  "f64.convert_i64_s",
  "f64.convert_i64_u",
  "f64.promote_f32",
  "i32.reinterpret_f32",
  "i64.reinterpret_f64",
  "f32.reinterpret_i32",
  "f64.reinterpret_i64",
  // 0xc0-0xc4: sign extension
  "i32.extend8_s",
  "i32.extend16_s",
  "i64.extend8_s",
  "i64.extend16_s",
  "i64.extend32_s",
  // 0xd0-0xd6: reference
  208,
  "ref.null ref_null",
  "ref.is_null",
  "ref.func funcidx",
  "ref.eq",
  "ref.as_non_null",
  "br_on_null labelidx",
  "br_on_non_null labelidx",
  // 0xe0-0xe6: stack switching (Phase 3)
  224,
  "cont.new typeidx",
  "cont.bind cont_bind",
  "suspend tagidx",
  "resume resume",
  "resume_throw resume_throw",
  "resume_throw_ref resume_throw_ref",
  "switch switch_cont",
  // 0xfb: GC instructions
  16449536,
  "struct.new typeidx",
  "struct.new_default typeidx",
  "struct.get typeidx_field",
  "struct.get_s typeidx_field",
  "struct.get_u typeidx_field",
  "struct.set typeidx_field",
  "array.new typeidx",
  "array.new_default typeidx",
  "array.new_fixed typeidx_multi",
  "array.new_data typeidx_dataidx",
  "array.new_elem typeidx_elemidx",
  "array.get typeidx",
  "array.get_s typeidx",
  "array.get_u typeidx",
  "array.set typeidx",
  "array.len",
  "array.fill typeidx",
  "array.copy typeidx_typeidx",
  "array.init_data typeidx_dataidx",
  "array.init_elem typeidx_elemidx",
  "ref.test reftype",
  "ref.test_null reftype",
  "ref.cast reftype",
  "ref.cast_null reftype",
  "br_on_cast reftype2",
  "br_on_cast_fail reftype2",
  "any.convert_extern",
  "extern.convert_any",
  "ref.i31",
  "i31.get_s",
  "i31.get_u",
  // custom descriptors (Phase 3): 0xFB 0x20-0x26
  16449568,
  "struct.new_desc typeidx",
  "struct.new_default_desc typeidx",
  "ref.get_desc typeidx",
  "ref.cast_desc_eq reftype",
  16449573,
  "br_on_cast_desc_eq reftype2",
  "br_on_cast_desc_eq_fail reftype2",
  // stringref: 0xFB 0x80-0xB7
  16449664,
  "string.new_utf8 memoryidx?",
  "string.new_wtf16 memoryidx?",
  "string.const stringidx",
  "string.measure_utf8",
  "string.measure_wtf8",
  "string.measure_wtf16",
  "string.encode_utf8 memoryidx?",
  "string.encode_wtf16 memoryidx?",
  "string.concat",
  "string.eq",
  "string.is_usv_sequence",
  "string.new_lossy_utf8 memoryidx?",
  "string.new_wtf8 memoryidx?",
  "string.encode_lossy_utf8 memoryidx?",
  "string.encode_wtf8 memoryidx?",
  16449680,
  "string.as_wtf8",
  "stringview_wtf8.advance",
  "stringview_wtf8.encode_utf8 memoryidx?",
  "stringview_wtf8.slice",
  "stringview_wtf8.encode_lossy_utf8 memoryidx?",
  "stringview_wtf8.encode_wtf8 memoryidx?",
  16449688,
  "string.as_wtf16",
  "stringview_wtf16.length",
  "stringview_wtf16.get_codeunit",
  "stringview_wtf16.encode memoryidx?",
  "stringview_wtf16.slice",
  16449696,
  "string.as_iter",
  "stringview_iter.next",
  "stringview_iter.advance",
  "stringview_iter.rewind",
  "stringview_iter.slice",
  16449712,
  "string.new_utf8_array",
  "string.new_wtf16_array",
  "string.encode_utf8_array",
  "string.encode_wtf16_array",
  "string.new_lossy_utf8_array",
  "string.new_wtf8_array",
  "string.encode_lossy_utf8_array",
  "string.encode_wtf8_array",
  // 0xfc: Bulk memory/table operations + rounding mode control
  16515072,
  "i32.trunc_sat_f32_s",
  "i32.trunc_sat_f32_u",
  "i32.trunc_sat_f64_s",
  "i32.trunc_sat_f64_u",
  "i64.trunc_sat_f32_s",
  "i64.trunc_sat_f32_u",
  "i64.trunc_sat_f64_s",
  "i64.trunc_sat_f64_u",
  "memory.init dataidx_memoryidx",
  "data.drop dataidx",
  "memory.copy memoryidx_memoryidx",
  "memory.fill memoryidx?",
  "table.init reversed",
  "elem.drop elemidx",
  "table.copy tableidx_tableidx",
  "table.grow tableidx",
  "table.size tableidx",
  "table.fill tableidx",
  16515091,
  "i64.add128",
  "i64.sub128",
  "i64.mul_wide_s",
  "i64.mul_wide_u",
  // 0x30: half precision memory ops
  16515120,
  "f32.load_f16 memarg",
  "f32.store_f16 memarg",
  // 0x80-0xBB: rounding mode control
  16515200,
  "f32.sqrt_ceil",
  "f32.add_ceil",
  "f32.sub_ceil",
  "f32.mul_ceil",
  "f32.div_ceil",
  "f64.sqrt_ceil",
  "f64.add_ceil",
  "f64.sub_ceil",
  "f64.mul_ceil",
  "f64.div_ceil",
  "f32.convert_ceil_i32_s",
  "f32.convert_ceil_i32_u",
  "f32.convert_ceil_i64_s",
  "f32.convert_ceil_i64_u",
  "f32.demote_ceil_f64",
  "f64.convert_ceil_i32_s",
  "f64.convert_ceil_i32_u",
  "f64.convert_ceil_i64_s",
  "f64.convert_ceil_i64_u",
  "f64.promote_ceil_f32",
  "f32.sqrt_floor",
  "f32.add_floor",
  "f32.sub_floor",
  "f32.mul_floor",
  "f32.div_floor",
  "f64.sqrt_floor",
  "f64.add_floor",
  "f64.sub_floor",
  "f64.mul_floor",
  "f64.div_floor",
  "f32.convert_floor_i32_s",
  "f32.convert_floor_i32_u",
  "f32.convert_floor_i64_s",
  "f32.convert_floor_i64_u",
  "f32.demote_floor_f64",
  "f64.convert_floor_i32_s",
  "f64.convert_floor_i32_u",
  "f64.convert_floor_i64_s",
  "f64.convert_floor_i64_u",
  "f64.promote_floor_f32",
  "f32.sqrt_trunc",
  "f32.add_trunc",
  "f32.sub_trunc",
  "f32.mul_trunc",
  "f32.div_trunc",
  "f64.sqrt_trunc",
  "f64.add_trunc",
  "f64.sub_trunc",
  "f64.mul_trunc",
  "f64.div_trunc",
  "f32.convert_trunc_i32_s",
  "f32.convert_trunc_i32_u",
  "f32.convert_trunc_i64_s",
  "f32.convert_trunc_i64_u",
  "f32.demote_trunc_f64",
  "f64.convert_trunc_i32_s",
  "f64.convert_trunc_i32_u",
  "f64.convert_trunc_i64_s",
  "f64.convert_trunc_i64_u",
  "f64.promote_trunc_f32",
  // 0xfd: SIMD instructions
  16580608,
  "v128.load memarg",
  "v128.load8x8_s memarg",
  "v128.load8x8_u memarg",
  "v128.load16x4_s memarg",
  "v128.load16x4_u memarg",
  "v128.load32x2_s memarg",
  "v128.load32x2_u memarg",
  "v128.load8_splat memarg",
  "v128.load16_splat memarg",
  "v128.load32_splat memarg",
  "v128.load64_splat memarg",
  "v128.store memarg",
  "v128.const v128const",
  "i8x16.shuffle shuffle",
  "i8x16.swizzle",
  "i8x16.splat",
  "i16x8.splat",
  "i32x4.splat",
  "i64x2.splat",
  "f32x4.splat",
  "f64x2.splat",
  "i8x16.extract_lane_s laneidx",
  "i8x16.extract_lane_u laneidx",
  "i8x16.replace_lane laneidx",
  "i16x8.extract_lane_s laneidx",
  "i16x8.extract_lane_u laneidx",
  "i16x8.replace_lane laneidx",
  "i32x4.extract_lane laneidx",
  "i32x4.replace_lane laneidx",
  "i64x2.extract_lane laneidx",
  "i64x2.replace_lane laneidx",
  "f32x4.extract_lane laneidx",
  "f32x4.replace_lane laneidx",
  "f64x2.extract_lane laneidx",
  "f64x2.replace_lane laneidx",
  "i8x16.eq",
  "i8x16.ne",
  "i8x16.lt_s",
  "i8x16.lt_u",
  "i8x16.gt_s",
  "i8x16.gt_u",
  "i8x16.le_s",
  "i8x16.le_u",
  "i8x16.ge_s",
  "i8x16.ge_u",
  "i16x8.eq",
  "i16x8.ne",
  "i16x8.lt_s",
  "i16x8.lt_u",
  "i16x8.gt_s",
  "i16x8.gt_u",
  "i16x8.le_s",
  "i16x8.le_u",
  "i16x8.ge_s",
  "i16x8.ge_u",
  "i32x4.eq",
  "i32x4.ne",
  "i32x4.lt_s",
  "i32x4.lt_u",
  "i32x4.gt_s",
  "i32x4.gt_u",
  "i32x4.le_s",
  "i32x4.le_u",
  "i32x4.ge_s",
  "i32x4.ge_u",
  "f32x4.eq",
  "f32x4.ne",
  "f32x4.lt",
  "f32x4.gt",
  "f32x4.le",
  "f32x4.ge",
  "f64x2.eq",
  "f64x2.ne",
  "f64x2.lt",
  "f64x2.gt",
  "f64x2.le",
  "f64x2.ge",
  "v128.not",
  "v128.and",
  "v128.andnot",
  "v128.or",
  "v128.xor",
  "v128.bitselect",
  "v128.any_true",
  "v128.load8_lane memlane",
  "v128.load16_lane memlane",
  "v128.load32_lane memlane",
  "v128.load64_lane memlane",
  "v128.store8_lane memlane",
  "v128.store16_lane memlane",
  "v128.store32_lane memlane",
  "v128.store64_lane memlane",
  "v128.load32_zero memarg",
  "v128.load64_zero memarg",
  "f32x4.demote_f64x2_zero",
  "f64x2.promote_low_f32x4",
  "i8x16.abs",
  "i8x16.neg",
  "i8x16.popcnt",
  "i8x16.all_true",
  "i8x16.bitmask",
  "i8x16.narrow_i16x8_s",
  "i8x16.narrow_i16x8_u",
  "f32x4.ceil",
  "f32x4.floor",
  "f32x4.trunc",
  "f32x4.nearest",
  "i8x16.shl",
  "i8x16.shr_s",
  "i8x16.shr_u",
  "i8x16.add",
  "i8x16.add_sat_s",
  "i8x16.add_sat_u",
  "i8x16.sub",
  "i8x16.sub_sat_s",
  "i8x16.sub_sat_u",
  "f64x2.ceil",
  "f64x2.floor",
  "i8x16.min_s",
  "i8x16.min_u",
  "i8x16.max_s",
  "i8x16.max_u",
  "f64x2.trunc",
  "i8x16.avgr_u",
  "i16x8.extadd_pairwise_i8x16_s",
  "i16x8.extadd_pairwise_i8x16_u",
  "i32x4.extadd_pairwise_i16x8_s",
  "i32x4.extadd_pairwise_i16x8_u",
  "i16x8.abs",
  "i16x8.neg",
  "i16x8.q15mulr_sat_s",
  "i16x8.all_true",
  "i16x8.bitmask",
  "i16x8.narrow_i32x4_s",
  "i16x8.narrow_i32x4_u",
  "i16x8.extend_low_i8x16_s",
  "i16x8.extend_high_i8x16_s",
  "i16x8.extend_low_i8x16_u",
  "i16x8.extend_high_i8x16_u",
  "i16x8.shl",
  "i16x8.shr_s",
  "i16x8.shr_u",
  "i16x8.add",
  "i16x8.add_sat_s",
  "i16x8.add_sat_u",
  "i16x8.sub",
  "i16x8.sub_sat_s",
  "i16x8.sub_sat_u",
  "f64x2.nearest",
  "i16x8.mul",
  "i16x8.min_s",
  "i16x8.min_u",
  "i16x8.max_s",
  "i16x8.max_u",
  16580763,
  "i16x8.avgr_u",
  "i16x8.extmul_low_i8x16_s",
  "i16x8.extmul_high_i8x16_s",
  "i16x8.extmul_low_i8x16_u",
  "i16x8.extmul_high_i8x16_u",
  "i32x4.abs",
  "i32x4.neg",
  16580771,
  "i32x4.all_true",
  "i32x4.bitmask",
  16580775,
  "i32x4.extend_low_i16x8_s",
  "i32x4.extend_high_i16x8_s",
  "i32x4.extend_low_i16x8_u",
  "i32x4.extend_high_i16x8_u",
  "i32x4.shl",
  "i32x4.shr_s",
  "i32x4.shr_u",
  "i32x4.add",
  16580785,
  "i32x4.sub",
  16580789,
  "i32x4.mul",
  "i32x4.min_s",
  "i32x4.min_u",
  "i32x4.max_s",
  "i32x4.max_u",
  "i32x4.dot_i16x8_s",
  16580796,
  "i32x4.extmul_low_i16x8_s",
  "i32x4.extmul_high_i16x8_s",
  "i32x4.extmul_low_i16x8_u",
  "i32x4.extmul_high_i16x8_u",
  "i64x2.abs",
  "i64x2.neg",
  16580803,
  "i64x2.all_true",
  "i64x2.bitmask",
  16580807,
  "i64x2.extend_low_i32x4_s",
  "i64x2.extend_high_i32x4_s",
  "i64x2.extend_low_i32x4_u",
  "i64x2.extend_high_i32x4_u",
  "i64x2.shl",
  "i64x2.shr_s",
  "i64x2.shr_u",
  "i64x2.add",
  16580817,
  "i64x2.sub",
  16580821,
  "i64x2.mul",
  "i64x2.eq",
  "i64x2.ne",
  "i64x2.lt_s",
  "i64x2.gt_s",
  "i64x2.le_s",
  "i64x2.ge_s",
  "i64x2.extmul_low_i32x4_s",
  "i64x2.extmul_high_i32x4_s",
  "i64x2.extmul_low_i32x4_u",
  "i64x2.extmul_high_i32x4_u",
  "f32x4.abs",
  "f32x4.neg",
  16580835,
  "f32x4.sqrt",
  "f32x4.add",
  "f32x4.sub",
  "f32x4.mul",
  "f32x4.div",
  "f32x4.min",
  "f32x4.max",
  "f32x4.pmin",
  "f32x4.pmax",
  "f64x2.abs",
  "f64x2.neg",
  16580847,
  "f64x2.sqrt",
  "f64x2.add",
  "f64x2.sub",
  "f64x2.mul",
  "f64x2.div",
  "f64x2.min",
  "f64x2.max",
  "f64x2.pmin",
  "f64x2.pmax",
  "i32x4.trunc_sat_f32x4_s",
  "i32x4.trunc_sat_f32x4_u",
  "f32x4.convert_i32x4_s",
  "f32x4.convert_i32x4_u",
  "i32x4.trunc_sat_f64x2_s_zero",
  "i32x4.trunc_sat_f64x2_u_zero",
  "f64x2.convert_low_i32x4_s",
  "f64x2.convert_low_i32x4_u",
  "i8x16.relaxed_swizzle",
  "i32x4.relaxed_trunc_f32x4_s",
  "i32x4.relaxed_trunc_f32x4_u",
  "i32x4.relaxed_trunc_f64x2_s_zero",
  "i32x4.relaxed_trunc_f64x2_u_zero",
  "f32x4.relaxed_madd",
  "f32x4.relaxed_nmadd",
  "f64x2.relaxed_madd",
  "f64x2.relaxed_nmadd",
  "i8x16.relaxed_laneselect",
  "i16x8.relaxed_laneselect",
  "i32x4.relaxed_laneselect",
  "i64x2.relaxed_laneselect",
  "f32x4.relaxed_min",
  "f32x4.relaxed_max",
  "f64x2.relaxed_min",
  "f64x2.relaxed_max",
  "i16x8.relaxed_q15mulr_s",
  "i16x8.relaxed_dot_i8x16_i7x16_s",
  "i32x4.relaxed_dot_i8x16_i7x16_add_s",
  // 0x120: half precision (f16x8)
  16580896,
  "f16x8.splat",
  "f16x8.extract_lane laneidx",
  "f16x8.replace_lane laneidx",
  16580912,
  "f16x8.abs",
  "f16x8.neg",
  "f16x8.sqrt",
  "f16x8.ceil",
  "f16x8.floor",
  "f16x8.trunc",
  "f16x8.nearest",
  "f16x8.eq",
  "f16x8.ne",
  "f16x8.lt",
  "f16x8.gt",
  "f16x8.le",
  "f16x8.ge",
  "f16x8.add",
  "f16x8.sub",
  "f16x8.mul",
  "f16x8.div",
  "f16x8.min",
  "f16x8.max",
  "f16x8.pmin",
  "f16x8.pmax",
  "i16x8.trunc_sat_f16x8_s",
  "i16x8.trunc_sat_f16x8_u",
  "f16x8.convert_i16x8_s",
  "f16x8.convert_i16x8_u",
  "f16x8.demote_f32x4_zero",
  "f16x8.demote_f64x2_zero",
  "f32x4.promote_low_f16x8",
  16580942,
  "f16x8.madd",
  "f16x8.nmadd",
  // 0xfe: atomic/thread instructions
  16646144,
  "memory.atomic.notify memarg",
  "memory.atomic.wait32 memarg",
  "memory.atomic.wait64 memarg",
  "atomic.fence opt_memory",
  // atomic loads take a trailing ordering keyword (acquire-release atomics proposal)
  16646160,
  "i32.atomic.load memarg_order",
  "i64.atomic.load memarg_order",
  "i32.atomic.load8_u memarg_order",
  "i32.atomic.load16_u memarg_order",
  "i64.atomic.load8_u memarg_order",
  "i64.atomic.load16_u memarg_order",
  "i64.atomic.load32_u memarg_order",
  "i32.atomic.store memarg",
  "i64.atomic.store memarg",
  "i32.atomic.store8 memarg",
  "i32.atomic.store16 memarg",
  "i64.atomic.store8 memarg",
  "i64.atomic.store16 memarg",
  "i64.atomic.store32 memarg",
  "i32.atomic.rmw.add memarg",
  "i64.atomic.rmw.add memarg",
  "i32.atomic.rmw8.add_u memarg",
  "i32.atomic.rmw16.add_u memarg",
  "i64.atomic.rmw8.add_u memarg",
  "i64.atomic.rmw16.add_u memarg",
  "i64.atomic.rmw32.add_u memarg",
  "i32.atomic.rmw.sub memarg",
  "i64.atomic.rmw.sub memarg",
  "i32.atomic.rmw8.sub_u memarg",
  "i32.atomic.rmw16.sub_u memarg",
  "i64.atomic.rmw8.sub_u memarg",
  "i64.atomic.rmw16.sub_u memarg",
  "i64.atomic.rmw32.sub_u memarg",
  "i32.atomic.rmw.and memarg",
  "i64.atomic.rmw.and memarg",
  "i32.atomic.rmw8.and_u memarg",
  "i32.atomic.rmw16.and_u memarg",
  "i64.atomic.rmw8.and_u memarg",
  "i64.atomic.rmw16.and_u memarg",
  "i64.atomic.rmw32.and_u memarg",
  "i32.atomic.rmw.or memarg",
  "i64.atomic.rmw.or memarg",
  "i32.atomic.rmw8.or_u memarg",
  "i32.atomic.rmw16.or_u memarg",
  "i64.atomic.rmw8.or_u memarg",
  "i64.atomic.rmw16.or_u memarg",
  "i64.atomic.rmw32.or_u memarg",
  "i32.atomic.rmw.xor memarg",
  "i64.atomic.rmw.xor memarg",
  "i32.atomic.rmw8.xor_u memarg",
  "i32.atomic.rmw16.xor_u memarg",
  "i64.atomic.rmw8.xor_u memarg",
  "i64.atomic.rmw16.xor_u memarg",
  "i64.atomic.rmw32.xor_u memarg",
  "i32.atomic.rmw.xchg memarg",
  "i64.atomic.rmw.xchg memarg",
  "i32.atomic.rmw8.xchg_u memarg",
  "i32.atomic.rmw16.xchg_u memarg",
  "i64.atomic.rmw8.xchg_u memarg",
  "i64.atomic.rmw16.xchg_u memarg",
  "i64.atomic.rmw32.xchg_u memarg",
  "i32.atomic.rmw.cmpxchg memarg",
  "i64.atomic.rmw.cmpxchg memarg",
  "i32.atomic.rmw8.cmpxchg_u memarg",
  "i32.atomic.rmw16.cmpxchg_u memarg",
  "i64.atomic.rmw8.cmpxchg_u memarg",
  "i64.atomic.rmw16.cmpxchg_u memarg",
  "i64.atomic.rmw32.cmpxchg_u memarg"
];
var OPCODE = {};
var IMM = {};
for (let i = 0, code = 0; i < TABLE.length; i++) {
  const item = TABLE[i];
  if (typeof item === "number") {
    code = item;
    continue;
  }
  const sp = item.indexOf(" ");
  const nm = sp < 0 ? item : item.slice(0, sp);
  if (sp >= 0) IMM[nm] = item.slice(sp + 1);
  OPCODE[nm] = code++;
}
var resultType = (op) => {
  if (typeof op !== "string") return null;
  const dot = op.indexOf(".");
  if (dot < 0) return null;
  const prefix = op.slice(0, dot);
  const scalar = prefix === "i32" || prefix === "i64" || prefix === "f32" || prefix === "f64";
  if (scalar && /^(eqz?|ne|[lg][te])(_[su])?$/.test(op.slice(dot + 1))) return "i32";
  if (scalar || prefix === "v128") return prefix;
  if (op === "memory.size" || op === "memory.grow") return "i32";
  return null;
};
var SECTION = { custom: 0, type: 1, import: 2, func: 3, table: 4, memory: 5, tag: 13, strings: 14, global: 6, export: 7, start: 8, elem: 9, datacount: 12, code: 10, data: 11 };
var TYPE = {
  // Value types
  i8: 120,
  i16: 119,
  i32: 127,
  i64: 126,
  f32: 125,
  f64: 124,
  void: 64,
  v128: 123,
  // Heap types
  exn: 105,
  noexn: 116,
  nofunc: 115,
  noextern: 114,
  none: 113,
  func: 112,
  extern: 111,
  any: 110,
  eq: 109,
  i31: 108,
  struct: 107,
  array: 106,
  data: 107,
  cont: 104,
  nocont: 117,
  // stack switching (Phase 3)
  string: 103,
  stringview_wtf8: 102,
  stringview_wtf16: 96,
  stringview_iter: 97,
  // stringref
  // Reference type abbreviations (absheaptype abbrs)
  nullfuncref: 115,
  nullexternref: 114,
  nullexnref: 116,
  nullref: 113,
  funcref: 112,
  externref: 111,
  exnref: 105,
  anyref: 110,
  eqref: 109,
  i31ref: 108,
  structref: 107,
  arrayref: 106,
  contref: 104,
  nocontref: 117,
  // stack switching abbreviations
  stringref: 103,
  // stringref abbreviation
  // ref, refnull
  ref: 100,
  // -0x1c
  refnull: 99,
  // -0x1d
  // Recursion group / type definition opcodes
  sub: 80,
  subfinal: 79,
  rec: 78
};
var DEFTYPE = { func: 96, struct: 95, array: 94, cont: 93, sub: 80, subfinal: 79, rec: 78 };
var KIND = { func: 0, table: 1, memory: 2, global: 3, tag: 4 };

// src/parse.js
var parse_default = (str2) => {
  let i = 0, level = [], buf = "", q = 0, depth = 0;
  const commit = () => buf && (level.push(buf), buf = "");
  const parseLevel = (pos) => {
    level.loc = pos;
    for (let c, root, p; i < str2.length; ) {
      c = str2.charCodeAt(i);
      if (q === 34) buf += str2[i++], c === 92 ? buf += str2[i++] : c === 34 && (commit(), q = 0);
      else if (q > 59) c === 40 && str2.charCodeAt(i + 1) === 59 ? (q++, buf += str2[i++] + str2[i++]) : (
        // nested (;
        c === 59 && str2.charCodeAt(i + 1) === 41 ? (buf += str2[i++] + str2[i++], --q === 59 && (commit(), q = 0)) : (
          // ;)
          buf += str2[i++]
        )
      );
      else if (q < 0) c === 10 || c === 13 ? (buf += str2[i++], commit(), q = 0) : q === -2 && c === 41 ? (commit(), q = 0) : buf += str2[i++];
      else if (c === 34) buf !== "$" && commit(), q = 34, buf += str2[i++];
      else if (c === 40 && str2.charCodeAt(i + 1) === 59) commit(), q = 60, buf = str2[i++] + str2[i++];
      else if (c === 59 && str2.charCodeAt(i + 1) === 59) commit(), q = str2.indexOf("\n", i) < 0 ? -2 : -1, buf = str2[i++] + str2[i++];
      else if (c === 40 && str2.charCodeAt(i + 1) === 64) commit(), p = i, i += 2, buf = "@", depth++, (root = level).push(level = []), parseLevel(p), level = root;
      else if (c === 40) commit(), p = i++, depth++, (root = level).push(level = []), parseLevel(p), level = root;
      else if (c === 41) return commit(), i++, depth--;
      else if (c <= 32) commit(), i++;
      else buf += str2[i++];
    }
    q < 0 && commit();
    commit();
  };
  parseLevel(0);
  if (q === 34) err(`Unclosed quote`, i);
  if (q > 59) err(`Unclosed block comment`, i);
  if (depth > 0) err(`Unclosed parenthesis`, i);
  if (i < str2.length) err(`Unexpected closing parenthesis`, i);
  return level.length > 1 ? level : level[0] || [];
};

// src/compile.js
var isDroppable = (n) => typeof n === "string" && (n[0] === ";" ? !LOC.test(n) : n[0] === "(" && n[1] === ";") || Array.isArray(n) && n[0]?.[0] === "@" && n[0] !== "@custom" && n[0] !== "@loc" && !n[0]?.startsWith?.("@metadata.code.");
var loc = (s, m = LOC.exec(s)) => m[1] == null ? ["@loc"] : m[4] == null ? ["@loc", m[1], +m[2], +m[3]] : ["@loc", m[1], +m[2], +m[3], m[4]];
var cleanup = (node, result) => {
  if (typeof node === "string") return (
    // normalize quoted ids: $"name" -> $name (if no escapes), else $unescaped
    node[0] === "$" && node[1] === '"' ? node.includes("\\") ? "$" + unescape(node.slice(1)) : "$" + node.slice(2, -1) : (
      // convert string literals to byte arrays with valueOf
      node[0] === '"' ? str(node) : (
        // ;;@ source-location annotation (the only comment isDroppable keeps)
        node[0] === ";" ? loc(node) : node
      )
    )
  );
  if (!Array.isArray(node)) return node;
  result = node.filter((c) => !isDroppable(c)).map(cleanup);
  result.loc = node.loc;
  return result.length === 1 && result[0]?.[0] === "module" ? result[0] : result;
};
var isStr = (n) => Array.isArray(n) && typeof n.valueOf() === "string";
function assemble(nodes, sizeOnly) {
  if (typeof nodes === "string") setErrSrc(nodes), nodes = parse_default(nodes) || [];
  else setErrSrc("");
  setErrLoc(0);
  nodes = isDroppable(nodes) ? [] : cleanup(nodes) ?? [];
  let idx = 0, pendingLoc;
  if (nodes[0] === "module") idx++, isId(nodes[idx]) && idx++;
  else if (typeof nodes[0] === "string") nodes = [nodes];
  if (nodes[idx] === "binary") {
    const b = Uint8Array.from(nodes.slice(++idx).flat());
    return sizeOnly ? b.length : b;
  }
  if (nodes[idx] === "quote") return assemble(nodes.slice(++idx).map((v) => v.valueOf().slice(1, -1)).flat().join(""), sizeOnly);
  nodes = nodes.flatMap((n, i) => {
    if (i < idx || !Array.isArray(n) || n[0] !== "import") return [n];
    const [, mod, ...rest] = n;
    if (!rest.some((r) => Array.isArray(r) && r[0] === "item")) return [n];
    const lastIsType = Array.isArray(rest.at(-1)) && rest.at(-1)[0] !== "item";
    if (lastIsType) {
      const type = rest.at(-1);
      return rest.slice(0, -1).filter((r) => r[0] === "item").map(([, nm]) => ["import", mod, nm, type]);
    }
    return rest.filter((r) => r[0] === "item").map(([, nm, type]) => ["import", mod, nm, type]);
  });
  const ctx = [];
  for (let kind in SECTION) (ctx[SECTION[kind]] = ctx[kind] = []).name = kind;
  ctx.metadata = {};
  nodes.slice(idx).filter((n) => {
    if (!Array.isArray(n)) {
      let pos = getErrLoc(), src = getErrSrc(), c;
      while ((pos = src.indexOf(n, pos)) >= 0) {
        c = src.charCodeAt(pos - 1);
        if (pos > 0 && (c > 47 && c < 58 || c > 64 && c < 91 || c > 96 && c < 123 || c === 95 || c === 36)) {
          pos++;
          continue;
        }
        c = src.charCodeAt(pos + n.length);
        if (c > 47 && c < 58 || c > 64 && c < 91 || c > 96 && c < 123 || c === 95) {
          pos++;
          continue;
        }
        break;
      }
      if (pos >= 0) setErrLoc(pos);
      err(`Unexpected token ${n}`);
    }
    let [kind, ...node] = n;
    setErrLoc(n.loc);
    if (kind === "@custom") {
      ctx.custom.push(node);
    } else if (kind === "rec") {
      for (let i = 0; i < node.length; i++) {
        let [, ...subnode] = node[i];
        name(subnode, ctx.type);
        const tdesc = [];
        while (subnode[0]?.[0] === "descriptor" || subnode[0]?.[0] === "describes") tdesc.push(subnode.shift());
        (subnode = typedef(subnode, ctx)).push(i ? true : [ctx.type.length, node.length]);
        if (tdesc.length) subnode.desc = subnode.desc ? [...tdesc, ...subnode.desc] : tdesc;
        ctx.type.push(subnode);
      }
    } else if (kind === "type") {
      name(node, ctx.type);
      const tdesc = [];
      while (node[0]?.[0] === "descriptor" || node[0]?.[0] === "describes") tdesc.push(node.shift());
      const td = typedef(node, ctx);
      if (tdesc.length) td.desc = td.desc ? [...tdesc, ...td.desc] : tdesc;
      ctx.type.push(td);
    } else if (kind === "export") {
      if (!isStr(node[0])) err("Missing export name");
      if (!Array.isArray(node[1])) err("Missing export desc");
      ctx.export.push(node);
    } else if (kind === "start") ctx.start.push(node);
    else return true;
  }).forEach((n) => {
    let [kind, ...node] = n;
    if (kind === "@loc") {
      pendingLoc = n;
      return;
    }
    setErrLoc(n.loc);
    let imported;
    if (kind === "import") {
      imported = node;
      if (!isStr(imported[0]) || !isStr(imported[1])) err("Missing import name");
      if (imported.length !== 3 || !Array.isArray(imported[2])) err("Bad import desc");
      [kind, ...node] = imported.pop();
    }
    let items = ctx[kind];
    if (!items) err(`Unknown section ${kind}`);
    name(node, items);
    while (node[0]?.[0] === "export") {
      let ex = node.shift(), [, nm, ...rest] = ex;
      if (!isStr(nm) || rest.length) err("Bad export name", ex.loc ?? n.loc);
      ctx.export.push([nm, [kind, items.length]]);
    }
    if (node[0]?.[0] === "import") {
      let im = node.shift();
      [, ...imported] = im;
      if (imported.length !== 2 || !isStr(imported[0]) || !isStr(imported[1])) err("Missing import name", im.loc ?? n.loc);
    }
    if (kind === "table") {
      const is64 = node[0] === "i64", idx2 = is64 ? 1 : 0;
      if (node[idx2 + 1]?.[0] === "elem") {
        let [reftype2, [, ...els]] = [node[idx2], node[idx2 + 1]];
        node = is64 ? ["i64", els.length, els.length, reftype2] : [els.length, els.length, reftype2];
        ctx.elem.push([["table", items.length], ["offset", [is64 ? "i64.const" : "i32.const", is64 ? 0n : 0]], reftype2, ...els]);
      }
    } else if (kind === "memory") {
      const is64 = node[0] === "i64", idx2 = is64 ? 1 : 0;
      if (node[idx2]?.[0] === "data") {
        const ps = node.find((n2) => Array.isArray(n2) && n2[0] === "pagesize")?.[1] ?? 65536;
        let [, ...data] = node.splice(idx2, 1)[0], m = "" + Math.ceil(data.reduce((s, d) => s + d.length, 0) / ps);
        ctx.data.push([["memory", items.length], [is64 ? "i64.const" : "i32.const", is64 ? 0n : 0], ...data]);
        node = is64 ? ["i64", m, m] : [m, m];
      }
    } else if (kind === "func") {
      let locs = [];
      while (node[0]?.[0] === "@loc") locs.push(node.shift());
      let [idx2, param, result] = typeuse(node, ctx);
      idx2 ??= regtype(param, result, ctx);
      if (!imported) {
        pendingLoc && (locs.unshift(pendingLoc), pendingLoc = null);
        ctx.code.push([[idx2, param, result], ...locs, ...normalize(node, ctx)]);
      }
      node = [["type", idx2]];
    } else if (kind === "tag") {
      let [idx2, param] = typeuse(node, ctx);
      idx2 ??= regtype(param, [], ctx);
      node = [["type", idx2]];
    }
    if (imported) ctx.import.push([...imported, [kind, ...node]]), node = null;
    items.push(node);
  });
  const bin = (kind, count = true) => {
    const items = ctx[kind].filter(Boolean).map((item) => build[kind](item, ctx)).filter(Boolean);
    if (kind === SECTION.custom) return items.flatMap((content) => [kind, ...vec(content)]);
    return !items.length ? [] : [kind, ...vec(count ? vec(items) : items.flat())];
  };
  const binMeta = () => {
    const sections2 = [];
    for (const type in ctx.metadata) {
      const name2 = vec(str(`"metadata.code.${type}"`));
      const content = vec(ctx.metadata[type].map(
        ([funcIdx, instances]) => [...uleb(funcIdx), ...vec(instances.map(([pos, data]) => [...uleb(pos), ...vec(data)]))]
      ));
      sections2.push(0, ...vec([...name2, ...content]));
    }
    return sections2;
  };
  const globalSection = bin(SECTION.global);
  const elemSection = bin(SECTION.elem);
  if (sizeOnly) {
    const codeSizes = ctx.code.filter(Boolean).map((item) => codeItemSize(item, ctx));
    const innerLen = codeSizes.length ? ulebSize(codeSizes.length) + codeSizes.reduce((a, b) => a + b, 0) : 0;
    const codeSecLen = codeSizes.length ? 1 + ulebSize(innerLen) + innerLen : 0;
    const metaSection2 = binMeta();
    const dataSection2 = bin(SECTION.data);
    const stringsSection2 = ctx.strings.length ? [SECTION.strings, ...vec([0, ...vec(ctx.strings.map((s) => vec(s)))])] : [];
    const others = [
      bin(SECTION.custom),
      bin(SECTION.type),
      bin(SECTION.import),
      bin(SECTION.func),
      bin(SECTION.table),
      bin(SECTION.memory),
      bin(SECTION.tag),
      stringsSection2,
      globalSection,
      bin(SECTION.export),
      bin(SECTION.start, false),
      elemSection,
      bin(SECTION.datacount, false),
      metaSection2,
      dataSection2
    ];
    return 8 + codeSecLen + others.reduce((s, sec) => s + sec.length, 0);
  }
  const codeItems = ctx.code.filter(Boolean).map((item) => build[SECTION.code](item, ctx)).filter(Boolean);
  let codeSection = [];
  if (codeItems.length) {
    const inner = uleb(codeItems.length);
    for (const it of codeItems) for (let i = 0; i < it.length; i++) inner.push(it[i]);
    codeSection = [SECTION.code, ...uleb(inner.length)];
    for (let i = 0; i < inner.length; i++) codeSection.push(inner[i]);
  }
  const metaSection = binMeta();
  const dataSection = bin(SECTION.data);
  const stringsSection = ctx.strings.length ? [SECTION.strings, ...vec([0, ...vec(ctx.strings.map((s) => vec(s)))])] : [];
  const sections = [
    bin(SECTION.custom),
    bin(SECTION.type),
    bin(SECTION.import),
    bin(SECTION.func),
    bin(SECTION.table),
    bin(SECTION.memory),
    bin(SECTION.tag),
    stringsSection,
    globalSection,
    bin(SECTION.export),
    bin(SECTION.start, false),
    elemSection,
    bin(SECTION.datacount, false),
    codeSection,
    metaSection,
    dataSection
  ];
  let total = 8;
  for (const sec of sections) total += sec.length;
  const wasm = new Uint8Array(total);
  wasm.set([0, 97, 115, 109, 1, 0, 0, 0]);
  let off = 8;
  for (const sec of sections) {
    if (sec.length) {
      wasm.set(sec, off);
      off += sec.length;
    }
  }
  const md = metadataOffsets();
  if (md) wasm.metadata = md;
  const sm = sourceMap();
  if (sm) wasm.sourceMap = sm;
  return wasm;
  function bodyOffsets() {
    const codeBase = 8 + sections.slice(0, sections.indexOf(codeSection)).reduce((n, s) => n + s.length, 0);
    const itemsBase = codeBase + codeSection.length - codeItems.reduce((n, it) => n + it.length, 0);
    const bodyBase = [];
    for (let i = 0, off2 = itemsBase; i < codeItems.length; i++) {
      bodyBase[i] = off2 + (ctx.codeSizePrefix?.[i] ?? 0);
      off2 += codeItems[i].length;
    }
    return [bodyBase, ctx.import.filter((imp) => imp[2][0] === "func").length, codeBase + codeSection.length];
  }
  function metadataOffsets() {
    let has = false;
    for (const _ in ctx.metadata) has = true;
    if (!has) return;
    const [bodyBase, importedFuncs] = bodyOffsets();
    const out = {};
    for (const type in ctx.metadata) {
      const entries = [];
      for (const [funcIdx, instances] of ctx.metadata[type]) {
        const base = bodyBase[funcIdx - importedFuncs];
        for (const [pos, data] of instances) entries.push([base + pos, data]);
      }
      out[type] = entries.sort((a, b) => a[0] - b[0]);
    }
    return out;
  }
  function sourceMap() {
    if (!ctx.sourcemap) return;
    const [bodyBase, importedFuncs, codeEnd] = bodyOffsets();
    const entries = [];
    for (const [funcIdx, locs] of ctx.sourcemap)
      for (const e of locs) entries.push([bodyBase[funcIdx - importedFuncs] + e[0], ...e.slice(1)]);
    entries.push([codeEnd]);
    const sources = [], names = [], mappings = [];
    let cleared = true, p0 = 0, p1 = 0, p2 = 1, p3 = 0, p4 = 0;
    for (const [off2, file, line, col, sym] of entries) {
      if (file == null) {
        if (!cleared) mappings.push(vlq(off2 - p0)), p0 = off2, cleared = true;
        continue;
      }
      let seg = vlq(off2 - p0);
      p0 = off2, cleared = false;
      let s = sources.indexOf(file);
      s < 0 && (s = sources.push(file) - 1);
      seg += vlq(s - p1) + vlq(line - p2) + vlq(col - p3);
      p1 = s, p2 = line, p3 = col;
      if (sym != null) {
        let n = names.indexOf(sym);
        n < 0 && (n = names.push(sym) - 1);
        seg += vlq(n - p4), p4 = n;
      }
      mappings.push(seg);
    }
    return { version: 3, sources, names, mappings: mappings.join(",") };
  }
}
var B64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
var vlq = (n) => {
  let v = n < 0 ? -n << 1 | 1 : n << 1, s = "";
  do {
    s += B64[v > 31 ? v & 31 | 32 : v], v >>>= 5;
  } while (v);
  return s;
};
function compile(nodes) {
  return assemble(nodes);
}
function sourceMapURL(wasm, url) {
  const section = [0, ...vec([...vec(utf8("sourceMappingURL")), ...vec(utf8(url))])];
  const out = new Uint8Array(wasm.length + section.length);
  out.set(wasm), out.set(section, wasm.length);
  return out;
}
var isIdx = (n) => n?.[0] === "$" || !isNaN(n);
var isId = (n) => n?.[0] === "$";
var isMemParam = (n) => n?.[0] === "a" && n[1] === "l" || n?.[0] === "o" && n[1] === "f";
var NCLS = /* @__PURE__ */ Object.create(null);
for (const k in OPCODE) {
  if (k === "block" || k === "if" || k === "loop") NCLS[k] = 1;
  else if (k === "else" || k === "end") NCLS[k] = 2;
  else if (k === "select") NCLS[k] = 3;
  else if (k.endsWith("call_indirect")) NCLS[k] = 4;
  else if (k === "table.init") NCLS[k] = 5;
  else if (k === "table.copy" || k === "memory.copy") NCLS[k] = 6;
  else if (k.startsWith("table.")) NCLS[k] = 7;
  else if (k === "memory.init") NCLS[k] = 8;
  else if (k === "data.drop" || k === "array.new_data" || k === "array.init_data") NCLS[k] = 9;
  else if (k.startsWith("memory.") || k.endsWith("load") || k.endsWith("store")) NCLS[k] = 10;
}
var nclsOf = (op) => NCLS[op];
function normalize(nodes, ctx, out = [], owned = false) {
  if (!owned) nodes = [...nodes];
  while (nodes.length) {
    let node = nodes.shift();
    if (typeof node === "string") {
      out.push(node);
      const cls = nclsOf(node);
      if (cls === void 0) continue;
      if (cls === 1) {
        if (isId(nodes[0])) out.push(nodes.shift());
        out.push(blocktype(nodes, ctx));
      } else if (cls === 2) {
        if (isId(nodes[0])) nodes.shift();
      } else if (cls === 3) out.push(paramres(nodes)[1]);
      else if (cls === 4) {
        let tableidx = isIdx(nodes[0]) ? nodes.shift() : 0, [idx, param, result] = typeuse(nodes, ctx);
        out.push(tableidx, ["type", idx ?? regtype(param, result, ctx)]);
      } else if (cls === 5) out.push(isIdx(nodes[1]) ? nodes.shift() : 0, nodes.shift());
      else if (cls === 6) out.push(isIdx(nodes[0]) ? nodes.shift() : 0, isIdx(nodes[0]) ? nodes.shift() : 0);
      else if (cls === 7) out.push(isIdx(nodes[0]) ? nodes.shift() : 0);
      else if (cls === 8) {
        out.push(...isIdx(nodes[1]) ? [nodes.shift(), nodes.shift()].reverse() : [nodes.shift(), 0]);
        ctx.datacount && (ctx.datacount[0] = true);
      } else if (cls === 9) {
        node === "data.drop" && out.push(nodes.shift());
        ctx.datacount && (ctx.datacount[0] = true);
      } else if (isIdx(nodes[0])) out.push(nodes.shift());
    } else if (Array.isArray(node)) {
      let op = node[0];
      node.loc != null && setErrLoc(node.loc);
      if (op?.startsWith?.("@metadata.code.")) {
        let type = op.slice(15);
        out.push(["@metadata", type, node[1]]);
        continue;
      }
      if (typeof op !== "string" || typeof OPCODE[op] !== "number") {
        out.push(node);
        continue;
      }
      const parts = node.slice(1);
      if (op === "block" || op === "loop") {
        out.push(op);
        if (isId(parts[0])) out.push(parts.shift());
        out.push(blocktype(parts, ctx));
        normalize(parts, ctx, out, true);
        out.push("end");
      } else if (op === "if") {
        let then = [], els = [];
        if (parts.at(-1)?.[0] === "else") els = normalize(parts.pop().slice(1), ctx, [], true);
        if (parts.at(-1)?.[0] === "then") then = normalize(parts.pop().slice(1), ctx, [], true);
        let immed = [op];
        if (isId(parts[0])) immed.push(parts.shift());
        immed.push(blocktype(parts, ctx));
        normalize(parts, ctx, out, true);
        for (let i = 0; i < immed.length; i++) out.push(immed[i]);
        for (let i = 0; i < then.length; i++) out.push(then[i]);
        if (els.length) {
          out.push("else");
          for (let i = 0; i < els.length; i++) out.push(els[i]);
        }
        out.push("end");
      } else if (op === "try_table") {
        out.push(op);
        if (isId(parts[0])) out.push(parts.shift());
        out.push(blocktype(parts, ctx));
        while (parts[0]?.[0] === "catch" || parts[0]?.[0] === "catch_ref" || parts[0]?.[0] === "catch_all" || parts[0]?.[0] === "catch_all_ref") {
          out.push(parts.shift());
        }
        normalize(parts, ctx, out, true);
        out.push("end");
      } else if (op === "ref.test" || op === "ref.cast") {
        const type = parts[0];
        const isNullable = !Array.isArray(type) || type[1] === "null" || type[0] !== "ref";
        if (isNullable) op += "_null";
        normalize(parts.slice(1), ctx, out, true);
        out.push(op, type);
        nodes.unshift(...out.splice(out.length - 2));
      } else {
        const imm = [];
        while (parts.length && (!Array.isArray(parts[0]) || parts[0].valueOf !== Array.prototype.valueOf || "type,param,result,ref,exact,on".includes(parts[0][0]))) imm.push(parts.shift());
        normalize(parts, ctx, out, true);
        out.push(op, ...imm);
        nodes.unshift(...out.splice(out.length - 1 - imm.length));
      }
    } else out.push(node);
  }
  return out;
}
var regtype = (param, result, ctx, idx = "$" + param + ">" + result) => (ctx.type[idx] ??= ctx.type.push(["func", [param, result]]) - 1, idx);
var fieldseq = (nodes, field) => {
  let seq = [];
  while (nodes[0]?.[0] === field) {
    let [, ...args] = nodes.shift(), nm = isId(args[0]) && args.shift();
    if (nm) nm in seq ? (() => {
      throw Error(`Duplicate ${field} ${nm}`);
    })() : seq[nm] = seq.length;
    seq.push(...args);
  }
  return seq;
};
var paramres = (nodes) => {
  let param = fieldseq(nodes, "param"), result = fieldseq(nodes, "result");
  if (nodes[0]?.[0] === "param") throw Error("Unexpected param");
  return [param, result];
};
var typeuse = (nodes, ctx) => {
  if (nodes[0]?.[0] !== "type") return [, ...paramres(nodes)];
  let [, idx] = nodes.shift(), [param, result] = paramres(nodes);
  const entry = ctx.type[typeof idx === "string" && isNaN(idx) ? ctx.type[idx] : +idx];
  if (!entry) throw Error(`Unknown type ${idx}`);
  if ((param.length || result.length) && entry[1].join(">") !== param + ">" + result) throw Error(`Type ${idx} mismatch`);
  return [idx, ...entry[1]];
};
var blocktype = (nodes, ctx) => {
  let [idx, param, result] = typeuse(nodes, ctx);
  if (!param.length && !result.length) return;
  if (!param.length && result.length === 1) return ["result", ...result];
  return ["type", idx ?? regtype(param, result, ctx)];
};
var name = (node, list) => {
  let nm = isId(node[0]) && node.shift();
  if (nm) nm in list ? err(`Duplicate ${list.name} ${nm}`) : list[nm] = list.length;
  return nm;
};
var typedef = ([dfn], ctx) => {
  let subkind = "subfinal", supertypes = [], compkind, desc = [];
  if (dfn[0] === "sub") {
    subkind = dfn.shift(), dfn[0] === "final" && (subkind += dfn.shift());
    dfn = (supertypes = dfn).pop();
    supertypes = supertypes.filter((n) => Array.isArray(n) && (n[0] === "descriptor" || n[0] === "describes") ? (desc.push(n), false) : true);
  }
  [compkind, ...dfn] = dfn;
  if (compkind === "func") dfn = paramres(dfn), ctx.type["$" + dfn.join(">")] ??= ctx.type.length;
  else if (compkind === "struct") dfn = fieldseq(dfn, "field");
  else if (compkind === "array") [dfn] = dfn;
  const result = [compkind, dfn, subkind, supertypes];
  if (desc.length) result.desc = desc;
  return result;
};
var build = [
  // (@custom "name" placement? data) - custom section builder
  ([name2, ...rest], ctx) => {
    let data = rest;
    if (rest[0]?.[0] === "before" || rest[0]?.[0] === "after") {
      data = rest.slice(1);
    }
    return [...vec(name2), ...data.flat()];
  },
  // type kinds
  // (func params result)
  // (array i8)
  // (struct ...fields)
  // (cont $ft) - stack switching (Phase 3)
  (node, ctx) => {
    const [kind, fields, subkind, supertypes, rec] = node;
    if (rec === true) return;
    const descPfx = (node.desc ?? []).flatMap(([clause, ref]) => [clause === "descriptor" ? 77 : 76, ...uleb(id(ref, ctx.type))]);
    const comptype = (k, f) => {
      if (k === "func") return [DEFTYPE.func, ...vec(f[0].map((t) => reftype(t, ctx))), ...vec(f[1].map((t) => reftype(t, ctx)))];
      if (k === "array") return [DEFTYPE.array, ...fieldtype(f, ctx)];
      if (k === "struct") return [DEFTYPE.struct, ...vec(f.map((t) => fieldtype(t, ctx)))];
      if (k === "cont") return [DEFTYPE.cont, ...uleb(id(f[0] ?? f, ctx.type))];
      return [DEFTYPE[k]];
    };
    if (rec) {
      let [from, length] = rec;
      const subtypes = Array.from({ length }, (_, i) => {
        const t = ctx.type[from + i], sub = t.slice(0, 4);
        if (t.desc) sub.desc = t.desc;
        return build[SECTION.type](sub, ctx);
      });
      return [DEFTYPE.rec, ...vec(subtypes)];
    } else if (subkind === "sub" || supertypes?.length) {
      return [DEFTYPE[subkind], ...vec(supertypes.map((n) => id(n, ctx.type))), ...descPfx, ...comptype(kind, fields)];
    }
    return [...descPfx, ...comptype(kind, fields)];
  },
  // (import "math" "add" (func|table|global|memory|tag dfn?))
  ([mod, field, [kind, ...dfn]], ctx) => {
    let details, kindByte = KIND[kind];
    if (kind === "func") {
      const isExact = dfn[0] === "exact" && dfn.shift();
      if (isExact) kindByte = 32;
      let [[, typeidx]] = dfn;
      details = uleb(id(typeidx, ctx.type));
    } else if (kind === "tag") {
      let [[, typeidx]] = dfn;
      details = [0, ...uleb(id(typeidx, ctx.type))];
    } else if (kind === "memory") {
      details = limits(dfn);
    } else if (kind === "global") {
      details = fieldtype(dfn[0], ctx);
    } else if (kind === "table") {
      details = [...reftype(dfn.pop(), ctx), ...limits(dfn)];
    } else err(`Unknown kind ${kind}`);
    return [...vec(mod), ...vec(field), kindByte, ...details];
  },
  // (func $name? ...params result ...body)
  ([[, typeidx]], ctx) => uleb(id(typeidx, ctx.type)),
  // (table 1 2 funcref)
  (node, ctx) => {
    let lims = limits(node), t = reftype(node.shift(), ctx), [init] = node;
    return init ? [64, 0, ...t, ...lims, ...expr(init, ctx)] : [...t, ...lims];
  },
  // (memory id? export* min max shared)
  (node, ctx) => limits(node),
  // (global $id? (mut i32) (i32.const 42))
  ([t, init], ctx) => [...fieldtype(t, ctx), ...expr(init, ctx)],
  // (export "name" (func|table|mem $name|idx))
  ([nm, [kind, l]], ctx) => [...vec(nm), KIND[kind], ...uleb(id(l, ctx[kind]))],
  // (start $main)
  ([l], ctx) => uleb(id(l, ctx.func)),
  // (elem elem*) - passive
  // (elem declare elem*) - declarative
  // (elem (table idx)? (offset expr)|(expr) elem*) - active
  // ref: https://webassembly.github.io/spec/core/binary/modules.html#element-section
  (parts, ctx) => {
    let passive = 0, declare = 0, elexpr = 0, nofunc = 0, tabidx, offset, rt;
    if (parts[0] === "declare") parts.shift(), declare = 1;
    if (parts[0]?.[0] === "table") {
      [, tabidx] = parts.shift();
      tabidx = id(tabidx, ctx.table);
    } else if ((typeof parts[0] === "string" || typeof parts[0] === "number") && (parts[1]?.[0] === "offset" || Array.isArray(parts[1]) && parts[1][0] !== "item" && !parts[1][0]?.startsWith("ref"))) {
      tabidx = id(parts.shift(), ctx.table);
    }
    if (parts[0]?.[0] === "offset" || Array.isArray(parts[0]) && parts[0][0] !== "item" && !parts[0][0].startsWith("ref")) {
      offset = parts.shift();
      if (offset[0] === "offset") [, offset] = offset;
      offset = expr(offset, ctx);
    } else if (!declare) passive = 1;
    if (TYPE[parts[0]] || parts[0]?.[0] === "ref") rt = reftype(parts.shift(), ctx);
    else if (parts[0] === "func") rt = [TYPE[parts.shift()]];
    else rt = [TYPE.func];
    parts = parts.map((el) => {
      if (el[0] === "item") el = el.length === 3 && el[1] === "ref.func" ? el[2] : el[1];
      if (el[0] === "ref.func") [, el] = el;
      if (typeof el !== "string") elexpr = 1;
      return el;
    });
    if (rt[0] !== TYPE.funcref) nofunc = 1, elexpr = 1;
    let mode = elexpr << 2 | (passive || declare ? declare : !!tabidx || nofunc) << 1 | (passive || declare);
    return [
      mode,
      ...// 0b000 e:expr y*:vec(funcidx)                     | type=(ref func), init ((ref.func y)end)*, active (table=0,offset=e)
      mode === 0 ? offset : (
        // 0b001 et:elkind y*:vec(funcidx)                  | type=0x00, init ((ref.func y)end)*, passive
        mode === 1 ? [0] : (
          // 0b010 x:tabidx e:expr et:elkind y*:vec(funcidx)  | type=0x00, init ((ref.func y)end)*, active (table=x,offset=e)
          mode === 2 ? [...uleb(tabidx || 0), ...offset, 0] : (
            // 0b011 et:elkind y*:vec(funcidx)                  | type=0x00, init ((ref.func y)end)*, passive declare
            mode === 3 ? [0] : (
              // 0b100 e:expr el*:vec(expr)                       | type=(ref null func), init el*, active (table=0, offset=e)
              mode === 4 ? offset : (
                // 0b101 et:reftype el*:vec(expr)                   | type=et, init el*, passive
                mode === 5 ? rt : (
                  // 0b110 x:tabidx e:expr et:reftype el*:vec(expr)   | type=et, init el*, active (table=x, offset=e)
                  mode === 6 ? [...uleb(tabidx || 0), ...offset, ...rt] : (
                    // 0b111 et:reftype el*:vec(expr)                   | type=et, init el*, passive declare
                    rt
                  )
                )
              )
            )
          )
        )
      ),
      ...vec(
        parts.map(
          elexpr ? (
            // ((ref.func y)end)*
            (el) => expr(typeof el === "string" ? ["ref.func", el] : el, ctx)
          ) : (
            // el*
            (el) => uleb(id(el, ctx.func))
          )
        )
      )
    ];
  },
  // (code)
  (body, ctx) => {
    let [typeidx, param] = body.shift();
    if (!param) [, [param]] = ctx.type[id(typeidx, ctx.type)];
    ctx.local = Object.create(param);
    ctx.block = [];
    ctx.local.name = "local";
    ctx.block.name = "block";
    if (ctx._codeIdx === void 0) ctx._codeIdx = 0;
    let codeIdx = ctx._codeIdx++;
    let leadloc = [];
    while (body[0]?.[0] === "local" || body[0]?.[0] === "@loc") {
      if (body[0][0] === "@loc") {
        leadloc.push(body.shift());
        continue;
      }
      let [, ...types] = body.shift();
      if (isId(types[0])) {
        let nm = types.shift();
        if (nm in ctx.local) err(`Duplicate local ${nm}`);
        else ctx.local[nm] = ctx.local.length;
      }
      ctx.local.push(...types);
    }
    for (let i = leadloc.length; i--; ) body.unshift(leadloc[i]);
    ctx.meta = {};
    ctx.loc = [];
    const bytes = instr(body, ctx);
    let loctypes = ctx.local.slice(param.length).reduce((a, type) => (type == a[a.length - 1]?.[1] ? a[a.length - 1][0]++ : a.push([1, type]), a), []);
    const locals = vec(loctypes.map(([n, t]) => [...uleb(n), ...reftype(t, ctx)]));
    const funcIdx = ctx.import.filter((imp) => imp[2][0] === "func").length + codeIdx;
    for (const type in ctx.meta) {
      for (const inst of ctx.meta[type]) inst[0] += locals.length;
      ((ctx.metadata ??= {})[type] ??= []).push([funcIdx, ctx.meta[type]]);
    }
    if (ctx.loc.length) {
      for (const e of ctx.loc) e[0] += locals.length;
      (ctx.sourcemap ??= []).push([funcIdx, ctx.loc]);
    }
    ctx.local = ctx.block = ctx.meta = ctx.loc = null;
    const item = uleb(locals.length + bytes.length);
    (ctx.codeSizePrefix ??= [])[codeIdx] = item.length;
    for (let i = 0; i < locals.length; i++) item.push(locals[i]);
    for (let i = 0; i < bytes.length; i++) item.push(bytes[i]);
    return item;
  },
  // (data (i32.const 0) "\aa" "\bb"?)
  // (data (memory ref) (offset (i32.const 0)) "\aa" "\bb"?)
  // (data (global.get $x) "\aa" "\bb"?)
  // (data (i8 1 2 3) ...) numeric values (WAT numeric values, Phase 2)
  (inits, ctx) => {
    let offset, memidx = 0;
    if (inits[0]?.[0] === "memory") {
      [, memidx] = inits.shift();
      memidx = id(memidx, ctx.memory);
    } else if ((typeof inits[0] === "string" || typeof inits[0] === "number") && (inits[1]?.[0] === "offset" || Array.isArray(inits[1]) && typeof inits[1][0] === "string")) {
      memidx = id(inits.shift(), ctx.memory);
    }
    if (Array.isArray(inits[0]) && typeof inits[0]?.[0] === "string") {
      offset = inits.shift();
      if (offset[0] === "offset") [, offset] = offset;
      offset ?? err("Bad offset", offset);
    }
    return [
      ...// active: 2, x=memidx, e=expr
      memidx ? [2, ...uleb(memidx), ...expr(offset, ctx)] : (
        // active: 0, e=expr
        offset ? [0, ...expr(offset, ctx)] : (
          // passive: 1
          [1]
        )
      ),
      ...vec(inits.flatMap((item) => numdata(item) ?? [...item]))
    ];
  },
  // datacount
  (nodes, ctx) => uleb(ctx.data.length),
  // (tag $name? (type idx))
  ([[, typeidx]], ctx) => [0, ...uleb(id(typeidx, ctx.type))]
];
var reftype = (t, ctx) => t[0] === "ref" ? t[1] == "null" ? (
  // (ref null (exact $T)) - exact nullable ref
  Array.isArray(t[2]) && t[2][0] === "exact" ? [TYPE.refnull, 98, ...uleb(id(t[2][1], ctx.type))] : TYPE[t[2]] ? [TYPE[t[2]]] : [TYPE.refnull, ...uleb(id(t[t.length - 1], ctx.type))]
) : (
  // (ref (exact $T)) - exact non-null ref
  Array.isArray(t[1]) && t[1][0] === "exact" ? [TYPE.ref, 98, ...uleb(id(t[1][1], ctx.type))] : [TYPE.ref, ...uleb(TYPE[t[t.length - 1]] || id(t[t.length - 1], ctx.type))]
) : (
  // abbrs
  [TYPE[t] ?? err(`Unknown type ${t}`)]
);
var fieldtype = (t, ctx, mut = t[0] === "mut" ? 1 : 0) => [...reftype(mut ? t[1] : t, ctx), mut];
var wleb = (v, out) => {
  if (out) {
    uleb(v, out);
    return;
  }
  return uleb(v);
};
var HANDLER = {
  reversed: (n, c) => {
    let t = n.pop(), e = n.pop();
    return [...uleb(id(e, c.elem)), ...uleb(id(t, c.table))];
  },
  block: (n, c, op, out) => {
    c.block.push(1);
    isId(instrPeek(n)) && (c.block[n.pop()] = c.block.length);
    let t = n.pop();
    const b = !t ? [TYPE.void] : t[0] === "result" ? reftype(t[1], c) : uleb(id(t[1], c.type));
    if (out) {
      for (let i = 0; i < b.length; i++) out.push(b[i]);
      return;
    }
    return b;
  },
  try_table: (n, c) => {
    isId(instrPeek(n)) && (c.block[n.pop()] = c.block.length + 1);
    let blocktype2 = n.pop();
    let result = !blocktype2 ? [TYPE.void] : blocktype2[0] === "result" ? reftype(blocktype2[1], c) : uleb(id(blocktype2[1], c.type));
    let catches = [], count = 0;
    while (instrPeek(n)?.[0] === "catch" || instrPeek(n)?.[0] === "catch_ref" || instrPeek(n)?.[0] === "catch_all" || instrPeek(n)?.[0] === "catch_all_ref") {
      let clause = n.pop();
      let kind = clause[0] === "catch" ? 0 : clause[0] === "catch_ref" ? 1 : clause[0] === "catch_all" ? 2 : 3;
      if (kind <= 1) catches.push(kind, ...uleb(id(clause[1], c.tag)), ...uleb(blockid(clause[2], c.block)));
      else catches.push(kind, ...uleb(blockid(clause[1], c.block)));
      count++;
    }
    c.block.push(1);
    return [...result, ...uleb(count), ...catches];
  },
  end: (_n, c) => (c.block.pop(), []),
  call_indirect: (n, c, op, out) => {
    let t = n.pop(), [, idx] = n.pop();
    if (out) {
      uleb(id(idx, c.type), out);
      uleb(id(t, c.table), out);
      return;
    }
    return [...uleb(id(idx, c.type)), ...uleb(id(t, c.table))];
  },
  br_table: (n, c) => {
    let labels = [], count = 0;
    while (instrPeek(n) && (!isNaN(instrPeek(n)) || isId(instrPeek(n)))) labels.push(...uleb(blockid(n.pop(), c.block))), count++;
    return [...uleb(count - 1), ...labels];
  },
  select: (n, c) => {
    let r = n.pop() || [];
    return r.length ? vec(r.map((t) => reftype(t, c))) : [];
  },
  ref_null: (n, c) => {
    let t = n.pop();
    return Array.isArray(t) && t[0] === "exact" ? [98, ...uleb(id(t[1], c.type))] : TYPE[t] ? [TYPE[t]] : uleb(id(t, c.type));
  },
  memarg: (n, c, op, out) => memargEnc(n, op, isIdx(instrPeek(n)) && !isMemParam(instrPeek(n)) ? id(n.pop(), c.memory) : 0, out),
  // memarg + trailing ordering keyword (acquire-release atomics): seqcst=0x00, acqrel=0x01;
  // flags bit 4 signals the ordering byte, placed between align (+memidx) and offset
  memarg_order: (n, c, op, out) => {
    const memIdx = isIdx(instrPeek(n)) && !isMemParam(instrPeek(n)) ? id(n.pop(), c.memory) : 0;
    const [a, o] = memarg(n);
    const ord = instrPeek(n) === "seqcst" ? 0 : instrPeek(n) === "acqrel" ? 1 : -1;
    if (ord >= 0) n.pop();
    const alignVal = (a ?? align(op)) | (memIdx && 64) | (ord >= 0 && 16);
    if (out) {
      uleb(alignVal, out);
      if (memIdx) uleb(memIdx, out);
      if (ord >= 0) out.push(ord);
      uleb(o ?? 0, out);
      return;
    }
    const r = uleb(alignVal);
    if (memIdx) r.push(...uleb(memIdx));
    if (ord >= 0) r.push(ord);
    r.push(...uleb(o ?? 0));
    return r;
  },
  opt_memory: (n, c, op, out) => wleb(id(isIdx(instrPeek(n)) ? n.pop() : 0, c.memory), out),
  reftype: (n, c) => {
    let ht = reftype(n.pop(), c);
    return ht.length > 1 ? ht.slice(1) : ht;
  },
  reftype2: (n, c) => {
    let b = blockid(n.pop(), c.block), h1 = reftype(n.pop(), c), h2 = reftype(n.pop(), c), ht = (h) => h.length > 1 ? h.slice(1) : h;
    return [(h2[0] !== TYPE.ref) << 1 | h1[0] !== TYPE.ref, ...uleb(b), ...ht(h1), ...ht(h2)];
  },
  v128const: (n) => {
    let [t, num] = n.pop().split("x"), bits = +t.slice(1), stride = bits >>> 3;
    num = +num;
    if (t[0] === "i") {
      let arr2 = num === 16 ? new Uint8Array(16) : num === 8 ? new Uint16Array(8) : num === 4 ? new Uint32Array(4) : new BigUint64Array(2);
      for (let j = 0; j < num; j++) arr2[j] = encode_exports[t].parse(n.pop());
      return [...new Uint8Array(arr2.buffer)];
    }
    let arr = new Uint8Array(16);
    for (let j = 0; j < num; j++) arr.set(encode_exports[t](n.pop()), j * stride);
    return [...arr];
  },
  shuffle: (n) => {
    let result = [];
    for (let j = 0; j < 16; j++) result.push(parseUint(n.pop(), 32));
    if (typeof instrPeek(n) === "string" && !isNaN(instrPeek(n))) err(`invalid lane length`);
    return result;
  },
  memlane: (n, c, op) => {
    const memIdx = isId(instrPeek(n)) || isIdx(instrPeek(n)) && (isMemParam(instrPeek(n, 1)) || isIdx(instrPeek(n, 1))) ? id(n.pop(), c.memory) : 0;
    return [...memargEnc(n, op, memIdx), ...uleb(parseUint(n.pop()))];
  },
  // *idx types — write-mode (out present) pushes in place and returns undefined;
  // return-mode hands back a fresh array. The sentinel is EXPLICIT: a boxed-
  // pointer identity compare (`returned !== out`) misfires under the jz kernel.
  labelidx: (n, c, op, out) => wleb(blockid(n.pop(), c.block), out),
  laneidx: (n, c, op, out) => {
    const v = parseUint(n.pop(), 255);
    if (out) {
      out.push(v);
      return;
    }
    return [v];
  },
  funcidx: (n, c, op, out) => wleb(id(n.pop(), c.func), out),
  typeidx: (n, c, op, out) => wleb(id(n.pop(), c.type), out),
  tableidx: (n, c, op, out) => wleb(id(n.pop(), c.table), out),
  memoryidx: (n, c, op, out) => wleb(id(n.pop(), c.memory), out),
  globalidx: (n, c, op, out) => wleb(id(n.pop(), c.global), out),
  localidx: (n, c, op, out) => wleb(id(n.pop(), c.local), out),
  dataidx: (n, c, op, out) => wleb(id(n.pop(), c.data), out),
  elemidx: (n, c, op, out) => wleb(id(n.pop(), c.elem), out),
  tagidx: (n, c, op, out) => wleb(id(n.pop(), c.tag), out),
  "memoryidx?": (n, c, op, out) => wleb(id(isIdx(instrPeek(n)) ? n.pop() : 0, c.memory), out),
  stringidx: (n, c, op, out) => {
    let s = n.pop(), key = s.valueOf(), idx = c.strings.findIndex((x) => x.valueOf() === key);
    if (idx < 0) idx = c.strings.push(s) - 1;
    return wleb(idx, out);
  },
  // Value type
  i32: (n, c, op, out) => {
    if (out) {
      i32(n.pop(), out);
      return;
    }
    return i32(n.pop());
  },
  i64: (n, c, op, out) => {
    if (out) {
      i64(n.pop(), out);
      return;
    }
    return i64(n.pop());
  },
  f32: (n, c, op, out) => f32(n.pop(), out),
  f64: (n, c, op, out) => f64(n.pop(), out),
  v128: (n) => v128(n.pop()),
  // Combinations
  typeidx_field: (n, c) => {
    let typeId = id(n.pop(), c.type);
    return [...uleb(typeId), ...uleb(id(n.pop(), c.type[typeId][1]))];
  },
  typeidx_multi: (n, c) => [...uleb(id(n.pop(), c.type)), ...uleb(n.pop())],
  typeidx_dataidx: (n, c) => [...uleb(id(n.pop(), c.type)), ...uleb(id(n.pop(), c.data))],
  typeidx_elemidx: (n, c) => [...uleb(id(n.pop(), c.type)), ...uleb(id(n.pop(), c.elem))],
  typeidx_typeidx: (n, c) => [...uleb(id(n.pop(), c.type)), ...uleb(id(n.pop(), c.type))],
  dataidx_memoryidx: (n, c) => [...uleb(id(n.pop(), c.data)), ...uleb(id(n.pop(), c.memory))],
  memoryidx_memoryidx: (n, c) => [...uleb(id(n.pop(), c.memory)), ...uleb(id(n.pop(), c.memory))],
  tableidx_tableidx: (n, c) => [...uleb(id(n.pop(), c.table)), ...uleb(id(n.pop(), c.table))],
  // stack switching handlers (Phase 3)
  cont_bind: (n, c) => [...uleb(id(n.pop(), c.type)), ...uleb(id(n.pop(), c.type))],
  switch_cont: (n, c) => [...uleb(id(n.pop(), c.type)), ...uleb(id(n.pop(), c.tag))],
  resume: (n, c) => {
    const typeidx = uleb(id(n.pop(), c.type));
    const handlers = [];
    let cnt = 0;
    while (instrPeek(n)?.[0] === "on") {
      const [, tag, label] = n.pop();
      if (label === "switch") handlers.push(1, ...uleb(id(tag, c.tag)));
      else handlers.push(0, ...uleb(id(tag, c.tag)), ...uleb(blockid(label, c.block)));
      cnt++;
    }
    return [...typeidx, ...uleb(cnt), ...handlers];
  },
  resume_throw: (n, c) => {
    const typeidx = uleb(id(n.pop(), c.type));
    const exnidx = uleb(id(n.pop(), c.tag));
    const handlers = [];
    let cnt = 0;
    while (instrPeek(n)?.[0] === "on") {
      const [, tag, label] = n.pop();
      if (label === "switch") handlers.push(1, ...uleb(id(tag, c.tag)));
      else handlers.push(0, ...uleb(id(tag, c.tag)), ...uleb(blockid(label, c.block)));
      cnt++;
    }
    return [...typeidx, ...exnidx, ...uleb(cnt), ...handlers];
  },
  resume_throw_ref: (n, c) => {
    const typeidx = uleb(id(n.pop(), c.type));
    const handlers = [];
    let cnt = 0;
    while (instrPeek(n)?.[0] === "on") {
      const [, tag, label] = n.pop();
      if (label === "switch") handlers.push(1, ...uleb(id(tag, c.tag)));
      else handlers.push(0, ...uleb(id(tag, c.tag)), ...uleb(blockid(label, c.block)));
      cnt++;
    }
    return [...typeidx, ...uleb(cnt), ...handlers];
  }
};
var instrPeek = (nodes, ahead = 0) => nodes[nodes.length - 1 - ahead];
var instr = (nodes, ctx) => {
  nodes.reverse();
  let out = [], meta = [];
  while (nodes.length) {
    let op = nodes.pop();
    if (op?.[0] === "@metadata") {
      meta.push(op.slice(1));
      continue;
    }
    if (op?.[0] === "@loc") {
      const locs = ctx.loc;
      if (locs) {
        const e = [out.length, ...op.slice(1)];
        locs.length && locs[locs.length - 1][0] === out.length ? locs[locs.length - 1] = e : locs.push(e);
      }
      continue;
    }
    if (Array.isArray(op)) {
      op.loc != null && setErrLoc(op.loc);
      err(`Unknown instruction ${op[0]}`);
    }
    const code = OPCODE[op];
    if (typeof code !== "number") err(`Unknown instruction ${op}`);
    if (meta.length) {
      for (const [type, data] of meta) (ctx.meta[type] ??= []).push([out.length, data]);
      meta = [];
    }
    const at = out.length;
    if (code > 65535) {
      out.push(code >>> 16);
      uleb(code & 65535, out);
    } else out.push(code);
    const imm = IMM[op];
    if (imm) {
      if (op === "select" && instrPeek(nodes)?.length) out[at]++;
      else if (imm === "reftype" && !op.endsWith("_null") && (instrPeek(nodes)[1] === "null" || instrPeek(nodes)[0] !== "ref")) {
        out[out.length - 1]++;
      }
      const b = HANDLER[imm](nodes, ctx, op, out);
      if (b) for (let i = 0; i < b.length; i++) out.push(b[i]);
    }
  }
  return out.push(11), out;
};
var ulebSize = (n) => {
  if (typeof n !== "number" || n < 0) return uleb(n).length;
  let k = 1;
  n >>>= 7;
  while (n) k++, n >>>= 7;
  return k;
};
var slebSize32 = (n) => {
  if (typeof n === "string") n = i32.parse(n);
  let k = 1;
  while (true) {
    const byte = n & 127;
    n >>= 7;
    if (n === 0 && (byte & 64) === 0 || n === -1 && (byte & 64) !== 0) return k;
    k++;
  }
};
var memargSize = (nodes, op, memIdx = 0) => {
  const [a, o] = memarg(nodes), alignVal = (a ?? align(op)) | (memIdx && 64);
  return memIdx ? ulebSize(alignVal) + ulebSize(memIdx) + ulebSize(o ?? 0) : ulebSize(alignVal) + ulebSize(o ?? 0);
};
var SIZE_HANDLER = {};
for (const k in HANDLER) SIZE_HANDLER[k] = (n, c, op) => HANDLER[k](n, c, op).length;
Object.assign(SIZE_HANDLER, {
  i32: (n) => slebSize32(n.pop()),
  f32: (n) => (n.pop(), 4),
  f64: (n) => (n.pop(), 8),
  localidx: (n, c) => ulebSize(id(n.pop(), c.local)),
  funcidx: (n, c) => ulebSize(id(n.pop(), c.func)),
  typeidx: (n, c) => ulebSize(id(n.pop(), c.type)),
  tableidx: (n, c) => ulebSize(id(n.pop(), c.table)),
  memoryidx: (n, c) => ulebSize(id(n.pop(), c.memory)),
  globalidx: (n, c) => ulebSize(id(n.pop(), c.global)),
  dataidx: (n, c) => ulebSize(id(n.pop(), c.data)),
  elemidx: (n, c) => ulebSize(id(n.pop(), c.elem)),
  tagidx: (n, c) => ulebSize(id(n.pop(), c.tag)),
  labelidx: (n, c) => ulebSize(blockid(n.pop(), c.block)),
  laneidx: (n) => (parseUint(n.pop(), 255), 1),
  memarg: (n, c, op) => memargSize(n, op, isIdx(instrPeek(n)) && !isMemParam(instrPeek(n)) ? id(n.pop(), c.memory) : 0),
  opt_memory: (n, c) => ulebSize(id(isIdx(instrPeek(n)) ? n.pop() : 0, c.memory)),
  "memoryidx?": (n, c) => ulebSize(id(isIdx(instrPeek(n)) ? n.pop() : 0, c.memory)),
  call_indirect: (n, c) => {
    const t = n.pop(), [, ti] = n.pop();
    return ulebSize(id(ti, c.type)) + ulebSize(id(t, c.table));
  },
  block: (n, c) => {
    c.block.push(1);
    isId(instrPeek(n)) && (c.block[n.pop()] = c.block.length);
    const t = n.pop();
    return !t ? 1 : t[0] === "result" ? reftype(t[1], c).length : ulebSize(id(t[1], c.type));
  },
  end: (_n, c) => (c.block.pop(), 0),
  stringidx: (n, c) => {
    const str2 = n.pop(), key = str2.valueOf();
    let idx = c.strings.findIndex((x) => x.valueOf() === key);
    if (idx < 0) idx = c.strings.push(str2) - 1;
    return ulebSize(idx);
  }
});
var instrSize = (nodes, ctx) => {
  nodes.reverse();
  let size = 0, meta = [];
  while (nodes.length) {
    let op = nodes.pop();
    if (op?.[0] === "@metadata") {
      meta.push(op.slice(1));
      continue;
    }
    if (op?.[0] === "@loc") continue;
    if (Array.isArray(op)) {
      op.loc != null && setErrLoc(op.loc);
      err(`Unknown instruction ${op[0]}`);
    }
    const code = OPCODE[op];
    if (typeof code !== "number") err(`Unknown instruction ${op}`);
    let n = code > 65535 ? 1 + ulebSize(code & 65535) : 1;
    if (IMM[op]) n += SIZE_HANDLER[IMM[op]](nodes, ctx, op);
    if (meta.length) {
      for (const [type, data] of meta) (ctx.meta[type] ??= []).push([size, data]);
      meta = [];
    }
    size += n;
  }
  return size + 1;
};
var codeItemSize = (body, ctx) => {
  let [typeidx, param] = body.shift();
  if (!param) [, [param]] = ctx.type[id(typeidx, ctx.type)];
  ctx.local = Object.create(param);
  ctx.block = [];
  ctx.local.name = "local";
  ctx.block.name = "block";
  if (ctx._codeIdx === void 0) ctx._codeIdx = 0;
  let codeIdx = ctx._codeIdx++;
  while (body[0]?.[0] === "local" || body[0]?.[0] === "@loc") {
    if (body[0][0] === "@loc") {
      body.shift();
      continue;
    }
    let [, ...types] = body.shift();
    if (isId(types[0])) {
      let nm = types.shift();
      if (nm in ctx.local) err(`Duplicate local ${nm}`);
      else ctx.local[nm] = ctx.local.length;
    }
    ctx.local.push(...types);
  }
  ctx.meta = {};
  const bytesLen = instrSize(body, ctx);
  let loctypes = ctx.local.slice(param.length).reduce((a, type) => (type == a[a.length - 1]?.[1] ? a[a.length - 1][0]++ : a.push([1, type]), a), []);
  const locals = vec(loctypes.map(([n, t]) => [...uleb(n), ...reftype(t, ctx)]));
  const funcIdx = ctx.import.filter((imp) => imp[2][0] === "func").length + codeIdx;
  for (const type in ctx.meta) {
    for (const inst of ctx.meta[type]) inst[0] += locals.length;
    ((ctx.metadata ??= {})[type] ??= []).push([funcIdx, ctx.meta[type]]);
  }
  ctx.local = ctx.block = ctx.meta = null;
  const bodyLen = locals.length + bytesLen;
  (ctx.codeSizePrefix ??= [])[codeIdx] = ulebSize(bodyLen);
  return ulebSize(bodyLen) + bodyLen;
};
var expr = (node, ctx) => instr(normalize([node], ctx), ctx);
var id = (nm, list, n) => (n = isId(nm) ? list[nm] : +nm, n >= 0 && n < list.length ? n : n in list ? n : err(`Unknown ${list.name} ${nm}`));
var blockid = (nm, block, i) => (i = isId(nm) ? block.length - block[nm] : +nm, isNaN(i) || i > block.length ? err(`Bad label ${nm}`) : i);
var memarg = (args) => {
  let align2, offset, k, v;
  while (isMemParam(instrPeek(args))) [k, v] = args.pop().split("="), k === "offset" ? offset = +v : k === "align" ? align2 = +v : err(`Unknown param ${k}=${v}`);
  if (offset < 0 || offset > 4294967295) err(`Bad offset ${offset}`);
  if (align2 <= 0 || align2 > 4294967295) err(`Bad align ${align2}`);
  if (align2) (align2 = Math.log2(align2)) % 1 && err(`Bad align ${align2}`);
  return [align2, offset];
};
var memargEnc = (nodes, op, memIdx = 0, out) => {
  const [a, o] = memarg(nodes), alignVal = (a ?? align(op)) | (memIdx && 64);
  if (out) {
    uleb(alignVal, out);
    if (memIdx) uleb(memIdx, out);
    uleb(o ?? 0, out);
    return;
  }
  return memIdx ? [...uleb(alignVal), ...uleb(memIdx), ...uleb(o ?? 0)] : [...uleb(alignVal), ...uleb(o ?? 0)];
};
var align = (op) => {
  let i = op.indexOf(".", 3) + 1, group = op.slice(1, op[0] === "v" ? 4 : 3);
  if (op[i] === "a") i = op.indexOf(".", i) + 1;
  if (op[0] === "m") return op.includes("64") ? 3 : 2;
  if (op[i] === "r") {
    let m2 = op.slice(i, i + 6).match(/\d+/);
    return m2 ? Math.log2(m2[0] / 8) : Math.log2(+group / 8);
  }
  let k = op[i] === "l" ? i + 4 : i + 5, m = op.slice(k).match(/(\d+)(x|_|$)/);
  return Math.log2(m ? m[2] === "x" ? 8 : m[1] / 8 : +group / 8);
};
var numdata = (item) => {
  if (!Array.isArray(item)) return null;
  const [t, ...vs] = item;
  if (t !== "i8" && t !== "i16" && t !== "i32" && t !== "i64" && t !== "f32" && t !== "f64") return null;
  const out = [], dv = new DataView(new ArrayBuffer(8));
  for (const v of vs) {
    if (t === "i8") out.push(i32.parse(v) & 255 + 256 & 255);
    else if (t === "i16") dv.setInt16(0, i32.parse(v), true), out.push(...new Uint8Array(dv.buffer, 0, 2));
    else if (t === "i32") dv.setInt32(0, i32.parse(v), true), out.push(...new Uint8Array(dv.buffer, 0, 4));
    else if (t === "i64") dv.setBigInt64(0, BigInt(v), true), out.push(...new Uint8Array(dv.buffer, 0, 8));
    else if (t === "f32") out.push(...f32(v));
    else if (t === "f64") out.push(...f64(v));
  }
  return out;
};
var limits = (node) => {
  const is64 = node[0] === "i64" && node.shift();
  const shared = node[node.length - 1] === "shared" && node.pop();
  const psIdx = node.findIndex((n) => Array.isArray(n) && n[0] === "pagesize");
  let psLog2 = -1;
  if (psIdx >= 0) psLog2 = Math.log2(+node.splice(psIdx, 1)[0][1]);
  const hasMax = !isNaN(parseInt(node[1]));
  const flag = (psLog2 >= 0 ? 8 : 0) | (is64 ? 4 : 0) | (shared ? 2 : 0) | (hasMax ? 1 : 0);
  const parse = is64 ? (v) => {
    if (typeof v === "bigint") return v;
    const str2 = typeof v === "string" ? v.replaceAll("_", "") : String(v);
    return BigInt(str2);
  } : parseUint;
  const ps = psLog2 >= 0 ? uleb(psLog2) : [];
  return hasMax ? [flag, ...uleb(parse(node.shift())), ...uleb(parse(node.shift())), ...ps] : [flag, ...uleb(parse(node.shift())), ...ps];
};
var parseUint = (v, max = 4294967295) => {
  const n = typeof v === "string" && v[0] !== "+" ? i32.parse(v) : typeof v === "number" ? v : err(`Bad int ${v}`);
  return n > max ? err(`Value out of range ${v}`) : n;
};
var vec = (a) => [...uleb(a.length), ...a.flat()];

// src/print.js
function print(tree, options = {}) {
  if (typeof tree === "string") tree = parse_default(tree);
  let { indent = "  ", newline = "\n", comments = true } = options;
  indent ||= "", newline ||= "";
  if (typeof tree[0] === "string" && tree[0][0] !== ";") return printNode(tree);
  return tree.filter((node) => comments || !isComment(node)).map((node) => printNode(node)).join(newline);
  function isComment(node) {
    return typeof node === "string" && (node[0] === ";" || node[0] === "(" && node[1] === ";");
  }
  function printNode(node, level = 0) {
    if (!Array.isArray(node)) return node;
    let content = node[0];
    if (!content) return "";
    let afterLineComment = false;
    if (content === "try_table") {
      let i = 1;
      if (typeof node[i] === "string" && node[i][0] === "$") content += " " + node[i++];
      if (Array.isArray(node[i]) && (node[i][0] === "result" || node[i][0] === "type")) content += " " + printNode(node[i++], level);
      while (Array.isArray(node[i]) && /^catch/.test(node[i][0])) content += " " + printNode(node[i++], level).trim();
      for (; i < node.length; i++) content += Array.isArray(node[i]) ? newline + indent.repeat(level + 1) + printNode(node[i], level + 1) : " " + node[i];
      return `(${content + newline + indent.repeat(level)})`;
    }
    let flat = !!newline && node.length < 4 && !node.some((n) => typeof n === "string" && n[0] === ";" && n[1] === ";");
    let curIndent = indent.repeat(level + 1);
    for (let i = 1; i < node.length; i++) {
      const raw = node[i]?.valueOf?.() ?? node[i];
      const sub = typeof raw === "number" && (raw - raw !== 0 || raw === 0 && 1 / raw < 0) ? raw > 0 ? "inf" : raw < 0 ? "-inf" : raw === 0 ? "-0" : "nan" : raw;
      if (typeof sub === "string" && (sub[0] === ";" || sub[0] === "(" && sub[1] === ";")) {
        if (!comments) continue;
        if (sub[0] === ";") {
          if (newline) {
            content += newline + curIndent + sub.trimEnd();
            afterLineComment = true;
          } else {
            const last = content[content.length - 1];
            if (last && last !== " " && last !== "(") content += " ";
            content += sub.trimEnd() + "\n";
          }
        } else {
          const last = content[content.length - 1];
          if (last && last !== " " && last !== "(") content += " ";
          content += sub.trimEnd();
        }
      } else if (Array.isArray(sub)) {
        if (flat) flat = sub.every((sub2) => !Array.isArray(sub2));
        content += newline + curIndent + printNode(sub, level + 1);
        afterLineComment = false;
      } else if (node[0] === "data") {
        flat = false;
        if (newline || content[content.length - 1] !== ")") content += newline || " ";
        content += curIndent + sub;
        afterLineComment = false;
      } else {
        const last = content[content.length - 1];
        if (afterLineComment && newline) content += newline + curIndent;
        else if (last === "\n") content += "";
        else if (last && last !== ")" && last !== " ") content += " ";
        else if (newline || last === ")") content += " ";
        content += sub;
        afterLineComment = false;
      }
    }
    if (flat) return `(${content.replaceAll(newline + curIndent + "(", " (")})`;
    return `(${content + newline + indent.repeat(level)})`;
  }
}

// src/template.js
var PUA = "\uE000";
function applyTransform(fn, name2, ast, opt) {
  if (typeof fn !== "function")
    throw Error(`watr: '${name2}' is not bundled in this entry \u2014 import it from 'watr/${name2}' and compose: compile(${name2}(src))`);
  return fn(ast, opt);
}
var exprType = (node, ctx = {}) => {
  if (!Array.isArray(node)) {
    if (typeof node === "string" && node[0] === "$" && ctx.locals?.[node]) return ctx.locals[node];
    return null;
  }
  const [op, ...args] = node;
  const rt = resultType(op);
  if (rt) return rt;
  if (op === "local.get" && ctx.locals?.[args[0]]) return ctx.locals[args[0]];
  if (op === "call" && ctx.funcs?.[args[0]]) return ctx.funcs[args[0]].result?.[0];
  return null;
};
function walk(node, fn) {
  node = fn(node);
  if (Array.isArray(node)) {
    for (let i = 0; i < node.length; i++) {
      let child = walk(node[i], fn);
      if (child?._splice) node.splice(i, 1, ...child), i += child.length - 1;
      else node[i] = child;
    }
  }
  return node;
}
function inferImports(ast, funcs) {
  const imports = [];
  const importMap = /* @__PURE__ */ new Map();
  walk(ast, (node) => {
    if (!Array.isArray(node)) return node;
    if (node[0] === "call" && typeof node[1] === "function") {
      const fn = node[1];
      if (!importMap.has(fn)) {
        const params = [];
        for (let i = 2; i < node.length; i++) {
          const t = exprType(node[i]);
          if (t) params.push(t);
        }
        const idx = imports.length;
        const name2 = fn.name || `$fn${idx}`;
        importMap.set(fn, { idx, name: name2.startsWith("$") ? name2 : "$" + name2, params, fn });
        imports.push(importMap.get(fn));
      }
      const imp = importMap.get(fn);
      node[1] = imp.name;
    }
    return node;
  });
  return imports;
}
function genImports(imports) {
  return imports.map(
    ({ name: name2, params }) => ["import", '"env"', `"${name2.slice(1)}"`, ["func", name2, ...params.map((t) => ["param", t])]]
  );
}
function compile2(backend2, source, values) {
  const { parse, compile: emit, optimize, polyfill } = backend2;
  let opts = {};
  if (!Array.isArray(source) && values.length && typeof values[values.length - 1] === "object" && values[values.length - 1] !== null && !values[values.length - 1].byteLength) {
    opts = values.pop();
  }
  if (Array.isArray(source) && source.raw) {
    let src = source[0];
    for (let i = 0; i < values.length; i++) {
      src += PUA + source[i + 1];
    }
    let ast = parse(src);
    const funcsToImport = [];
    let idx = 0;
    ast = walk(ast, (node) => {
      if (node === PUA) {
        const value = values[idx++];
        if (typeof value === "function") {
          funcsToImport.push(value);
          return value;
        }
        if (typeof value === "string" && (value[0] === "(" || /^\s*\(/.test(value))) {
          const parsed = parse(value);
          if (Array.isArray(parsed) && Array.isArray(parsed[0])) {
            parsed._splice = true;
          }
          return parsed;
        }
        if (value?.byteLength !== void 0) return [...value];
        if (typeof value === "bigint") return value.toString();
        return value;
      }
      return node;
    });
    let importObjs = null;
    if (funcsToImport.length) {
      const imports = inferImports(ast, funcsToImport);
      if (imports.length) {
        const importDecls = genImports(imports);
        if (ast[0] === "module") {
          ast.splice(1, 0, ...importDecls);
        } else if (typeof ast[0] === "string") {
          ast = [...importDecls, ast];
        } else {
          ast.unshift(...importDecls);
        }
        importObjs = { env: {} };
        for (const imp of imports) {
          importObjs.env[imp.name.slice(1)] = imp.fn;
        }
      }
    }
    if (opts.polyfill) ast = applyTransform(polyfill, "polyfill", ast, opts.polyfill);
    if (opts.optimize) ast = applyTransform(optimize, "optimize", ast, opts.optimize);
    const binary = emit(ast);
    if (importObjs) binary._imports = importObjs;
    return binary;
  }
  if (opts.polyfill || opts.optimize) {
    let ast = typeof source === "string" ? parse(source) : source;
    if (opts.polyfill) ast = applyTransform(polyfill, "polyfill", ast, opts.polyfill);
    if (opts.optimize) ast = applyTransform(optimize, "optimize", ast, opts.optimize);
    return emit(ast);
  }
  return emit(source);
}
function watr(backend2, source, values) {
  const binary = compile2(backend2, source, values);
  const module = new WebAssembly.Module(binary);
  const instance = new WebAssembly.Instance(module, binary._imports);
  return instance.exports;
}

// watr.js
var backend = { parse: parse_default, compile };
function compile3(source, ...values) {
  return compile2(backend, source, values);
}
function watr2(source, ...values) {
  return watr(backend, source, values);
}
var watr_default = watr2;

  self.wat2wasm = compile3;
}(self));
