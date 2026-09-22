/*global window, Worker, RSVP, setTimeout, clearTimeout */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window) {
  "use strict";

  var SANDBOX_WORKER_URL = "gadget_chat_sandbox_worker.js",
    SANDBOX_DEFAULT_TIMEOUT_MS = 10000,
    SANDBOX_MAX_TIMEOUT_MS = 120000;

  function createExecuteJavascriptTool() {
    return {
      definition: {
        name: "execute_javascript",
        description: "Execute JavaScript and get the result back. Runs in the same isolated sandbox " +
          "worker as run_wasm - no DOM, no cookies, no access to the page or any other tool's state " +
          "(the only network access is the optional library fetch below, done by this worker itself, " +
          "never by your code). Write the body of an async function: `await` is available, and you " +
          "must \"return <value>;\" to produce a result (only JSON-serializable values are usable; " +
          "console output is captured separately and returned alongside the result). A `utils` object " +
          "with b64encode/b64decode/describe helpers is also available to the code. Pass `libraries` " +
          "(names from library_list, or any https:// URL to a UMD/IIFE script or .mjs ES module) to " +
          "preload third-party helpers, available both as their usual global (e.g. `_` for lodash) and " +
          "via `lib.<name>` (e.g. `lib.lodash`). Errors thrown by the " +
          "code are reported back as an error message; a runaway loop is killed at its deadline, which " +
          "costs one worker, not the tab. USE THIS WHEN: you need custom computation or to " +
          "reshape/combine data you already have (e.g. a previous tool's result) that's easier to do in " +
          "code than by hand. DO NOT USE THIS WHEN: an existing tool (an MCP server's tools, draw_*, " +
          "run_wasm) already does what you need, or you need DOM/arbitrary network access - this sandbox " +
          "cannot reach either.",
        parameters: {
          type: "object",
          properties: {
            code: {
              type: "string",
              description: "Async function body, e.g. \"return 1 + 1;\" or " +
                "\"var total = 0; for (var i = 0; i < 10; i++) { total += i; } return total;\"."
            },
            libraries: {
              type: "array",
              description: "Names from library_list, or https:// URLs, to load before running code, e.g. [\"lodash\", \"dayjs\"].",
              items: { type: "string" }
            },
            timeout_ms: { type: "integer", description: "Deadline in ms (default 10000, max 120000)." }
          },
          required: ["code"]
        }
      },
      execute: function (args) {
        return new RSVP.Queue(runSandboxJob("js", { code: args.code, libraries: args.libraries }, args.timeout_ms))
          .push(function (result) {
            var parts = [];
            if (result.logs && result.logs.length) {
              parts.push("console:\n" + result.logs.join("\n"));
            }
            if (result.ok) {
              parts.push("result:\n" + (result.resultText || "(undefined)"));
            } else {
              parts.push("ERROR: " + result.error + (result.stack ? "\n" + result.stack : ""));
            }
            return parts.join("\n\n");
          });
      }
    };
  }


  function runSandboxJob(kind, payload, timeout_ms) {
    var budget = Math.min(Math.max(Number(timeout_ms) || SANDBOX_DEFAULT_TIMEOUT_MS, 100), SANDBOX_MAX_TIMEOUT_MS),
      settled = false,
      worker,
      timer;

    function cleanup() {
      settled = true;
      clearTimeout(timer);
      worker.terminate();
    }

    return new RSVP.Promise(function (resolve) {
      worker = new Worker(SANDBOX_WORKER_URL);
      function finish(value) {
        if (settled) { return; }
        cleanup();
        resolve(value);
      }
      timer = setTimeout(function () {
        finish({ ok: false, error: "execution exceeded " + budget + " ms and was terminated" });
      }, budget);
      worker.onmessage = function (event) {
        var data = event.data;
        finish(data.ok ? data.result : { ok: false, error: data.error });
      };
      worker.onerror = function (event) {
        finish({ ok: false, error: "worker error: " + (event.message || "unknown") });
      };
      worker.postMessage({ id: "run_wasm", kind: kind, payload: payload });
    }, function canceller() {
      if (settled) { return; }
      cleanup();
    });
  }

  function createRunWasmTool() {
    return {
      definition: {
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
      },
      execute: function (args) {
        var spec = {
          wat: args.wat,
          wasm_base64: args.wasm_base64,
          calls: args.calls,
          dump_memory: args.dump_memory
        };
        return new RSVP.Queue(runSandboxJob("wasm", spec, args.timeout_ms))
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
      }
    };
  }

  function createLibraryListTool() {
    return {
      definition: {
        name: "library_list",
        description: "List the third-party JavaScript libraries execute_javascript's `libraries` " +
          "parameter can load. Each entry names the global variable the library attaches inside the " +
          "sandbox once loaded (e.g. \"_\" for lodash), alongside `lib.<name>`. Any https:// URL to a " +
          "UMD/IIFE script or an .mjs ES module also works, even though it isn't listed here - use " +
          "library_inspect to see what one of these actually exposes before guessing at its API.",
        parameters: { type: "object", properties: {} }
      },
      execute: function () {
        return new RSVP.Queue(runSandboxJob("library_list", {}))
          .push(function (result) {
            if (!result.ok) { return "ERROR: " + result.error; }
            return result.libraries.map(function (lib) {
              return lib.name + " (global \"" + lib.global + "\"): " + lib.description;
            }).join("\n");
          });
      }
    };
  }

  function createLibraryInspectTool() {
    return {
      definition: {
        name: "library_inspect",
        description: "Download a library (if not already cached) and report what it actually exposes - " +
          "its own and prototype property/method names - so you can check its real API surface before " +
          "writing code against it instead of guessing. Accepts names from library_list, or any " +
          "https:// URL to a UMD/IIFE script or an .mjs ES module (the requesting website must allow " +
          "cross-origin fetches, e.g. most CDNs do - there is no proxy to work around one that doesn't).",
        parameters: {
          type: "object",
          properties: {
            libraries: {
              type: "array",
              description: "Names from library_list, or https:// URLs, to inspect, e.g. [\"lodash\", " +
                "\"https://cdn.jsdelivr.net/npm/nanoid@5/bin/index.js\"].",
              items: { type: "string" }
            }
          },
          required: ["libraries"]
        }
      },
      execute: function (args) {
        return new RSVP.Queue(runSandboxJob("library_inspect", { libraries: args.libraries }))
          .push(function (result) {
            if (!result.ok) { return "ERROR: " + result.error; }
            return result.libraries.map(function (lib) {
              if (lib.error) { return lib.name + " - ERROR: " + lib.error; }
              return lib.name + (lib.global ? " (global \"" + lib.global + "\")" : "") + ", " + lib.type +
                ": " + lib.description + "\n  " + lib.url +
                (lib.members.length ? "\n  members: " + lib.members.join(", ") : "");
            }).join("\n\n");
          });
      }
    };
  }

  // ERP5 document access (search/read/write/create) is provided by MCP
  // servers now (window.ChatMCP.buildToolList below), configured per-server
  // by the user - no local HATEOAS-based tools here any more.
  function createToolList(element, mcp_server_list, onMcpServerError, onMcpAuthExpired) {
    var local_tool_list = [
      createExecuteJavascriptTool(),
      createRunWasmTool(),
      createLibraryListTool(),
      createLibraryInspectTool()
    ];
    if (!mcp_server_list || !mcp_server_list.length) {
      return RSVP.resolve(local_tool_list);
    }
    return new RSVP.Queue(window.ChatMCP.buildToolList(mcp_server_list, element, onMcpServerError, onMcpAuthExpired))
      .push(function (mcp_tool_list) {
        return local_tool_list.concat(mcp_tool_list);
      });
  }

  window.ChatTools = { createToolList: createToolList };
}(window));
