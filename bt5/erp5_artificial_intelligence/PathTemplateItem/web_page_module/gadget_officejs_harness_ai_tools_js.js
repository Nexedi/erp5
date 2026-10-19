/*global window, Worker, RSVP, setTimeout, clearTimeout */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window) {
  "use strict";

  var SANDBOX_WORKER_URL = "gadget_officejs_harness_ai_sandbox_worker.js",
    SANDBOX_DEFAULT_TIMEOUT_MS = 10000,
    SANDBOX_MAX_TIMEOUT_MS = 120000,
    HTTP_FETCH_LIMIT = 200000;

  function truncate(text, max_len) {
    if (typeof text !== "string") {
      text = String(text);
    }
    return text.length > max_len ? text.slice(0, max_len) + "\n... [truncated at " + max_len + " chars]" : text;
  }

  // Strip tags/scripts from an HTML document, leaving readable text.
  function htmlToText(html) {
    return html
      .replace(/<script[\s\S]*?<\/script>/gi, " ")
      .replace(/<style[\s\S]*?<\/style>/gi, " ")
      .replace(/<!--[\s\S]*?-->/g, " ")
      .replace(/<\/(p|div|li|tr|h[1-6]|section|article)>/gi, "\n")
      .replace(/<br\s*\/?>/gi, "\n")
      .replace(/<[^>]+>/g, " ")
      .replace(/&nbsp;/g, " ")
      .replace(/&amp;/g, "&")
      .replace(/&lt;/g, "<")
      .replace(/&gt;/g, ">")
      .replace(/&quot;/g, "\"")
      .replace(/&#(\d+);/g, function (match, code) { return String.fromCharCode(+code); })
      .replace(/&#x([0-9a-f]+);/gi, function (match, hex) { return String.fromCharCode(parseInt(hex, 16)); })
      .replace(/[ \t]+/g, " ")
      .replace(/\n\s*\n\s*\n+/g, "\n\n")
      .replace(/^\s+|\s+$/g, "");
  }

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
          "with b64encode/b64decode/describe/wat2wasm helpers is also available to the code. Pass " +
          "`libraries` (https:// URLs to a UMD/IIFE script or .mjs ES module) to preload third-party " +
          "helpers, available both as their usual global (e.g. a UMD bundle's own global, auto-detected) " +
          "and via `lib[\"<the URL you passed>\"]`. Errors thrown by the " +
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
              description: "https:// URLs to load before running code, e.g. [\"https://cdn.jsdelivr.net/npm/lodash@4.17.21/lodash.min.js\"].",
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

  function createLibraryInspectTool() {
    return {
      definition: {
        name: "library_inspect",
        description: "Download a library (if not already cached) and report what it actually exposes - " +
          "its own and prototype property/method names - so you can check its real API surface before " +
          "writing code against it instead of guessing. Accepts any https:// URL to a UMD/IIFE script or " +
          "an .mjs ES module (the requesting website must allow cross-origin fetches, e.g. most CDNs do " +
          "- there is no proxy to work around one that doesn't).",
        parameters: {
          type: "object",
          properties: {
            libraries: {
              type: "array",
              description: "https:// URLs to inspect, e.g. [\"https://cdn.jsdelivr.net/npm/nanoid@5/bin/index.js\"].",
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

  // requestHttp is the acquired transport (gadget_officejs_harness_ai_artificial_task_view_js.js's
  // requestHttp): it does the actual fetch, relayed through the configured
  // Server URL forwarder when one is set, direct otherwise. This tool only
  // shapes the result for the model (HTML -> text, truncation).
  function createHttpRequestTool(requestHttp) {
    return {
      definition: {
        name: "http_request",
        description: "Fetch a URL - a web page, a JSON API, any public HTTP(S) resource. Relayed " +
          "through the configured forwarder (Server URL, in External Service) when one is set, purely " +
          "to get around the browser's own CORS restriction on the target; without one, this is a " +
          "plain, unproxied fetch, which only succeeds if the target itself allows cross-origin " +
          "requests. HTML is converted to readable text unless `raw` is requested. This is not a " +
          "general web browser - no JavaScript on the fetched page runs, and there is no rendering.",
        parameters: {
          type: "object",
          properties: {
            url: { type: "string" },
            method: { type: "string", enum: ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD"] },
            headers: { type: "object", description: "Extra request headers." },
            body: { type: "string" },
            raw: { type: "boolean", description: "Return the body verbatim instead of extracted text." },
            max_chars: { type: "integer", description: "Truncation limit (default 20000)." }
          },
          required: ["url"]
        }
      },
      execute: function (args) {
        if (!requestHttp) {
          return RSVP.resolve("ERROR: http_request is unavailable (no transport configured).");
        }
        return new RSVP.Queue(requestHttp(args))
          .push(function (result) {
            var text, is_html;
            if (result.error) {
              return "ERROR: " + result.error;
            }
            text = truncate(result.text || "", HTTP_FETCH_LIMIT);

            is_html = /html/i.test(result.content_type || "") ||
              /<(!doctype\s+html|html|head)[\s>]/i.test(text.slice(0, 2000));
            is_html = true;
            if (!args.raw && is_html) {
              text = htmlToText(text);
            }
            return "HTTP " + result.status + " " + (result.content_type || "") + "\n\n" +
              truncate(text, Math.min(args.max_chars || 20000, HTTP_FETCH_LIMIT));
          });
      }
    };
  }

  // A dynamic tool's implementation runs exactly like execute_javascript's
  // `code`, in the same sandbox worker - including access to `utils.wat2wasm`
  // and the worker's global `WebAssembly`, so a dynamic tool is free to be
  // JS-only or JS-driving-WASM.
  function createDynamicJsTool(spec) {
    return {
      definition: {
        name: spec.name,
        description: spec.description,
        parameters: spec.parameters || { type: "object", properties: {} }
      },
      dynamic: true,
      source: { code: spec.code, libraries: spec.libraries },
      execute: function (args) {
        return new RSVP.Queue(runSandboxJob("js", { code: spec.code, args: args, libraries: spec.libraries }))
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

  function createDefineToolTool(registerTool, isNameTaken, persistTool) {
    return {
      definition: {
        name: "define_tool",
        description: "Define a new, named tool for yourself, available to call (by name, with its own " +
          "argument schema) for the rest of this conversation, including by any sub-agent you spawn " +
          "afterwards, and persisted so it is still there next time you open this task. The " +
          "implementation is an async function body, exactly like execute_javascript's `code` (receives " +
          "`args` matching the `parameters` schema below, plus `console`/`utils`/`lib`); it runs in the " +
          "same isolated sandbox worker, with the same WebAssembly access execute_javascript and " +
          "run_wasm use internally - a dynamic tool can assemble/instantiate/call a WASM module itself " +
          "via `utils.wat2wasm` plus the global `WebAssembly`. USE THIS WHEN: you expect to call the same " +
          "piece of logic again, with different arguments, and want a clean, named, schema-checked tool " +
          "instead of repeating execute_javascript calls with inline code. DO NOT USE for a one-off " +
          "computation - just use execute_javascript directly.",
        parameters: {
          type: "object",
          properties: {
            name: { type: "string", description: "Tool name, e.g. \"fahrenheit_to_celsius\". Must not clash with an existing tool." },
            description: { type: "string", description: "Shown to yourself on future turns - describe what it does and when to use it." },
            parameters: {
              type: "object",
              description: "JSON schema object for this tool's own arguments, e.g. " +
                "{\"type\":\"object\",\"properties\":{\"fahrenheit\":{\"type\":\"number\"}},\"required\":[\"fahrenheit\"]}."
            },
            code: { type: "string", description: "Async function body implementing the tool, e.g. \"return (args.fahrenheit - 32) * 5 / 9;\"." },
            libraries: {
              type: "array",
              description: "https:// URLs to preload before each call.",
              items: { type: "string" }
            }
          },
          required: ["name", "description", "code"]
        }
      },
      execute: function (args) {
        var name = String(args.name || "").trim();
        if (!name) {
          return RSVP.resolve("ERROR: a tool name is required.");
        }
        if (isNameTaken(name)) {
          return RSVP.resolve("ERROR: a tool named \"" + name + "\" already exists (built-in, MCP, or " +
            "previously defined) - pick another name, or call undefine_tool first.");
        }
        return new RSVP.Queue(runSandboxJob("compile_check", { code: args.code }))
          .push(function (result) {
            var spec;
            if (!result.ok) {
              throw new Error(result.error);
            }
            spec = { name: name, description: args.description || "", parameters: args.parameters, code: args.code, libraries: args.libraries };
            return new RSVP.Queue(persistTool(spec))
              .push(function () {
                registerTool(createDynamicJsTool(spec));
                return "Defined tool \"" + name + "\": " + (args.description || "") +
                  "\nparameters: " + JSON.stringify(spec.parameters || {});
              });
          })
          .push(undefined, function (err) {
            return "ERROR: could not define \"" + name + "\": " + (err && err.message ? err.message : String(err));
          });
      }
    };
  }

  function createListDefinedToolsTool(listDynamicToolSpecs) {
    return {
      definition: {
        name: "list_defined_tools",
        description: "List the tools you have defined for yourself with define_tool in this " +
          "conversation, with their description, parameters and source code.",
        parameters: { type: "object", properties: {} }
      },
      execute: function () {
        var spec_list = listDynamicToolSpecs();
        if (!spec_list.length) {
          return RSVP.resolve("(no tools defined yet)");
        }
        return RSVP.resolve(spec_list.map(function (spec) {
          return spec.name + ": " + spec.description + "\nparameters: " + JSON.stringify(spec.parameters || {}) +
            "\ncode:\n" + spec.code;
        }).join("\n\n"));
      }
    };
  }

  function renderPlanText(plan) {
    if (!plan) {
      return "(no execution plan set)";
    }
    return "Goal: " + plan.goal + "\n" + plan.step_list.map(function (step, i) {
      return i + ". [" + step.status + "] " + step.title + (step.note ? " - " + step.note : "");
    }).join("\n");
  }

  function createSetExecutionPlanTool(updateExecutionPlan) {
    return {
      definition: {
        name: "set_execution_plan",
        description: "Create or completely replace your execution plan: an ordered checklist of steps " +
          "working towards a stated goal, shown to the user as a live checklist right in your current " +
          "chat message. Call this first for any non-trivial multi-step request, before doing any work, " +
          "and call it again with the FULL, updated step list whenever you revise the plan - e.g. after " +
          "reasoning through a step (a \"dry run\": predict what would happen without actually doing it " +
          "yet) reveals the plan needs to change. Every call replaces the checklist shown in the CURRENT " +
          "message with a new one (fresh steps, every status reset to \"pending\" - re-mark already-" +
          "finished steps as \"done\" again afterwards with update_execution_plan_step if they still are). " +
          "Nothing is lost: once this turn finishes, its final checklist state is kept permanently " +
          "attached to it, so calling this again later (in a new message, for a new/different goal) never " +
          "overwrites or hides the earlier one - scrolling up still shows exactly how each past plan " +
          "ended up. USE THIS WHEN: the request " +
          "needs several distinct actions, or asks you to create and iteratively improve a plan until " +
          "some condition holds. DO NOT USE for a single-step request a direct reply or tool call already " +
          "answers.",
        parameters: {
          type: "object",
          properties: {
            goal: { type: "string", description: "The overall goal / success condition this plan works towards." },
            step_list: {
              type: "array",
              description: "Ordered list of steps.",
              items: {
                type: "object",
                properties: { title: { type: "string" } },
                required: ["title"]
              }
            }
          },
          required: ["goal", "step_list"]
        }
      },
      execute: function (args) {
        return new RSVP.Queue(updateExecutionPlan({
            command: "set",
            goal: args.goal,
            step_list: args.step_list
          }))
          .push(function (plan) {
            return renderPlanText(plan);
          });
      }
    };
  }

  function createUpdateExecutionPlanStepTool(updateExecutionPlan) {
    return {
      definition: {
        name: "update_execution_plan_step",
        description: "Update one step of the current execution plan (set by set_execution_plan): its " +
          "status and an optional note - e.g. a dry-run prediction before actually doing the step, or " +
          "the real outcome afterwards. This is how the live checklist shown to the user reflects " +
          "progress - call it after reasoning through or actually executing every step.",
        parameters: {
          type: "object",
          properties: {
            index: { type: "integer", description: "0-based index of the step in the current plan's step_list." },
            status: { type: "string", "enum": ["pending", "in_progress", "done", "failed", "skipped"] },
            note: { type: "string", description: "Optional: dry-run prediction, real result, or reason for failure/skip." }
          },
          required: ["index", "status"]
        }
      },
      execute: function (args) {
        return new RSVP.Queue(updateExecutionPlan({
            command: "update_step",
            index: args.index,
            status: args.status,
            note: args.note
          }))
          .push(function (plan) {
            if (!plan) {
              return "ERROR: no execution plan has been set yet (or no step at index " +
                args.index + ") - call set_execution_plan first.";
            }
            return renderPlanText(plan);
          });
      }
    };
  }

  function createUndefineToolTool(unregisterTool, removePersistedTool) {
    return {
      definition: {
        name: "undefine_tool",
        description: "Remove a tool you previously created with define_tool, including its persisted " +
          "copy. Built-in and MCP tools cannot be removed.",
        parameters: {
          type: "object",
          properties: { name: { type: "string" } },
          required: ["name"]
        }
      },
      execute: function (args) {
        var result = unregisterTool(args.name);
        if (result === "not_found") {
          return RSVP.resolve("ERROR: no such defined tool \"" + args.name + "\".");
        }
        if (result === "not_dynamic") {
          return RSVP.resolve("ERROR: \"" + args.name + "\" is a built-in tool and cannot be removed.");
        }
        return new RSVP.Queue(removePersistedTool(args.name))
          .push(function () {
            return "Removed tool \"" + args.name + "\".";
          }, function (err) {
            return "Removed tool \"" + args.name + "\" from this conversation, but deleting its " +
              "persisted copy failed: " + (err && err.message ? err.message : String(err));
          });
      }
    };
  }

  // ERP5 document access (search/read/write/create) is provided by MCP
  // servers now (window.ChatMCP.buildToolList below), configured per-server
  // by the user - no local HATEOAS-based tools here any more.
  function createToolList(element, mcp_server_list, onMcpServerError, onMcpAuthExpired, requestHttp, persistTool, removePersistedTool, updateExecutionPlan) {
    var local_tool_list = [
      createExecuteJavascriptTool(),
      createRunWasmTool(),
      createLibraryInspectTool(),
      createHttpRequestTool(requestHttp),
      createSetExecutionPlanTool(updateExecutionPlan),
      createUpdateExecutionPlanStepTool(updateExecutionPlan)
    ];

    // tool_list stays the live array that gadget_officejs_harness_ai_agent_js.js
    // assigns as gadget.tool_list and later pushes spawn_subagent onto - the
    // register/unregister closures below mutate this same array in place, so
    // a tool defined mid-conversation is visible wherever gadget.tool_list is
    // read afterwards (no separate registry to keep in sync).
    function buildToolList(mcp_tool_list) {
      var tool_list = local_tool_list.concat(mcp_tool_list || []);

      function isNameTaken(name) {
        return tool_list.some(function (tool) { return tool.definition.name === name; });
      }
      function registerTool(tool) {
        tool_list.push(tool);
      }
      function unregisterTool(name) {
        var i;
        for (i = 0; i < tool_list.length; i += 1) {
          if (tool_list[i].definition.name === name) {
            if (!tool_list[i].dynamic) {
              return "not_dynamic";
            }
            tool_list.splice(i, 1);
            return "removed";
          }
        }
        return "not_found";
      }
      function listDynamicToolSpecs() {
        return tool_list.filter(function (tool) { return tool.dynamic; }).map(function (tool) {
          return {
            name: tool.definition.name,
            description: tool.definition.description,
            parameters: tool.definition.parameters,
            code: tool.source.code,
            libraries: tool.source.libraries
          };
        });
      }

      tool_list.push(createDefineToolTool(registerTool, isNameTaken, persistTool));
      tool_list.push(createListDefinedToolsTool(listDynamicToolSpecs));
      tool_list.push(createUndefineToolTool(unregisterTool, removePersistedTool));

      // Exposed so gadget_officejs_harness_ai_agent_js.js can rehydrate
      // previously-defined tools (fetched via getDefinedToolList) on render().
      tool_list.registerDynamicTool = registerTool;
      tool_list.createDynamicJsTool = createDynamicJsTool;
      tool_list.listDynamicToolSpecs = listDynamicToolSpecs;
      return tool_list;
    }

    if (!mcp_server_list || !mcp_server_list.length) {
      return RSVP.resolve(buildToolList([]));
    }
    return new RSVP.Queue(window.ChatMCP.buildToolList(mcp_server_list, element, onMcpServerError, onMcpAuthExpired))
      .push(function (mcp_tool_list) {
        return buildToolList(mcp_tool_list);
      });
  }

  window.ChatTools = { createToolList: createToolList };
}(window));
