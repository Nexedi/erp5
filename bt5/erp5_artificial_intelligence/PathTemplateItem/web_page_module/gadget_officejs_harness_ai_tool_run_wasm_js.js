/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  rJS(window)
    .declareMethod('getDefinition', function () {
      return {
        name: "run_wasm",
        description: "Assemble WebAssembly text format (.wat) into a module, instantiate it and call " +
          "its exports. Use this when you want the result to be a real WASM artifact, or for hot " +
          "numeric loops. Runs in an isolated sandbox worker with no DOM and no network access, using a " +
          "spec-complete WAT assembler - the full instruction set is supported, including tables and " +
          "call_indirect. Both folded (i32.add (local.get 0) (local.get 1)) and flat notation work. " +
          "Host functions importable from module \"env\": log_i32, log_i64, log_f32, log_f64, " +
          "log_str(ptr,len), abort(code), now() -> f64, random() -> f64. Export a memory as \"memory\" " +
          "if you want log_str or a memory dump to work. i64 arguments and results are exchanged as " +
          "decimal strings with an \"n\" suffix, e.g. \"42n\".",
        parameters: {
          type: "object",
          properties: {
            wat: { type: "string", description: "WebAssembly text source, starting with (module …)." },
            wasm_base64: { type: "string", description: "Alternative to `wat`: a pre-assembled module, base64-encoded." },
            calls: {
              type: "array",
              description: "Exported functions to call, in order.",
              items: {
                type: "object",
                properties: {
                  name: { type: "string" },
                  args: { type: "array", description: "Numbers, or \"123n\" strings for i64." }
                },
                required: ["name"]
              }
            },
            dump_memory: { type: "integer", description: "Show the first N bytes of exported memory." },
            timeout_ms: { type: "integer", description: "Deadline in ms (default 10000, max 120000)." }
          }
        }
      };
    })
    .declareMethod('render', function () {
      return;
    })
    .declareMethod('execute', function (args) {
      var spec = {
        wat: args.wat,
        wasm_base64: args.wasm_base64,
        calls: args.calls,
        dump_memory: args.dump_memory
      };
      return new RSVP.Queue(window.ChatToolCommon.runSandboxJob("wasm", spec, args.timeout_ms))
        .push(function (result) {
          var lines, i, call;
          if (!result.ok) {
            return "ERROR: " + result.error;
          }
          lines = ["assembled " + result.wasm_bytes + " bytes", "exports: " + (result.exports.join(", ") || "(none)")];
          for (i = 0; i < (result.calls || []).length; i += 1) {
            call = result.calls[i];
            lines.push(call.error ?
                call.name + "(" + (call.args || []).join(", ") + ") -> ERROR " + call.error :
                call.name + "(" + (call.args || []).join(", ") + ") -> " + JSON.stringify(call.result));
          }
          if (result.logs && result.logs.length) {
            lines.push("log:\n" + result.logs.join("\n"));
          }
          if (result.memory_head_hex) {
            lines.push("memory (" + result.memory_pages + " pages) hex: " + result.memory_head_hex);
            lines.push("memory as text: " + result.memory_head_text);
          }
          return lines.join("\n");
        });
    });
}(window, rJS, RSVP));
