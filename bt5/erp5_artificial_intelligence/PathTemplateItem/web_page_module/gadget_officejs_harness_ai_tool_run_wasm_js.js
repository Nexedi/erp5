/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  rJS(window)
    .declareMethod('getDefinition', function () {
      return {
        name: "run_wasm",
        description: "Assemble a WebAssembly text module (.wat), or take a binary one, instantiate it " +
          "and call its exported functions, in the sandbox of run_javascript. Give `wat` " +
          "or `wasm_base64`. Imports of module \"env\": log_i32, log_i64, log_f32, log_f64, " +
          "log_str(ptr, len) (needs an exported \"memory\"), abort(code), now() -> f64, " +
          "random() -> f64. i64 values are strings with an \"n\" suffix, eg. \"42n\". For an " +
          "ordinary computation, use run_javascript.",
        parameters: {
          type: "object",
          properties: {
            wat: { type: "string", description: "WebAssembly text source, starting with (module ...)." },
            wasm_base64: { type: "string", description: "Instead of `wat`: a binary module, base64 encoded." },
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
            dump_memory: { type: "integer", description: "Return the first N bytes of the exported \"memory\"." },
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
