/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  rJS(window)
    .declareAcquiredMethod("isToolNameTaken", "isToolNameTaken")
    .declareAcquiredMethod("persistAndRegisterDynamicTool", "persistAndRegisterDynamicTool")
    .declareMethod('getDefinition', function () {
      return {
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
      };
    })
    .declareMethod('render', function () {
      return;
    })
    .declareMethod('execute', function (args) {
      var gadget = this,
        name = String(args.name || "").trim();
      if (!name) {
        return "ERROR: a tool name is required.";
      }
      return gadget.isToolNameTaken(name)
        .push(function (taken) {
          if (taken) {
            return "ERROR: a tool named \"" + name + "\" already exists (built-in, MCP, or " +
              "previously defined) - pick another name, or call undefine_tool first.";
          }
          return new RSVP.Queue(window.ChatToolCommon.runSandboxJob("compile_check", { code: args.code }))
            .push(function (result) {
              var spec;
              if (!result.ok) {
                throw new Error(result.error);
              }
              spec = { name: name, description: args.description || "", parameters: args.parameters, code: args.code, libraries: args.libraries };
              return gadget.persistAndRegisterDynamicTool(spec)
                .push(function () {
                  return "Defined tool \"" + name + "\": " + (args.description || "") +
                    "\nparameters: " + JSON.stringify(spec.parameters || {});
                });
            });
        })
        .push(undefined, function (err) {
          return "ERROR: could not define \"" + name + "\": " + (err && err.message ? err.message : String(err));
        });
    });
}(window, rJS, RSVP));
