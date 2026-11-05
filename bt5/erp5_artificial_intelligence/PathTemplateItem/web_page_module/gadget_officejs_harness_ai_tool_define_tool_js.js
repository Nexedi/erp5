/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  rJS(window)
    .declareAcquiredMethod("isToolNameTaken", "isToolNameTaken")
    .declareAcquiredMethod("persistAndRegisterDynamicTool", "persistAndRegisterDynamicTool")
    .declareAcquiredMethod("listDynamicToolSpecs", "listDynamicToolSpecs")
    .declareAcquiredMethod("undefineDynamicTool", "undefineDynamicTool")
    .declareAcquiredMethod("removeDefinedTool", "removeDefinedTool")
    .declareMethod('getDefinition', function () {
      return {
        name: "define_tool",
        executionMode: "sequential",
        // Listing again is harmless, and defining an existing name fails.
        allow_repeat: true,
        description: "Manage the tools you define for yourself. command \"define\" creates a new, " +
          "named tool, available to call (by name, with its own argument schema) from now on, " +
          "including by any sub-agent you spawn afterwards. It is saved in this browser and shared " +
          "by all tasks: it is also available in the other tasks, and still there next time you open " +
          "one, until command \"remove\" removes it. Its implementation is an async function body, " +
          "exactly like execute_javascript's `code` (receives `args` matching its `parameters` " +
          "schema, plus `console`/`utils`/`lib`); it runs in the same isolated sandbox worker, with " +
          "the global `WebAssembly` and `utils.wat2wasm`. command \"list\" lists the defined tools " +
          "(of all tasks) with their description, parameters and code. command \"remove\" removes " +
          "one, with its saved copy - built-in and MCP tools can not be removed. USE \"define\" WHEN: " +
          "you expect to call the same piece of logic again, with different arguments, and want a " +
          "clean, named, schema-checked tool instead of repeating execute_javascript calls with inline " +
          "code. DO NOT USE it for a one-off computation - just use execute_javascript directly.",
        parameters: {
          type: "object",
          properties: {
            command: {
              type: "string",
              "enum": ["define", "list", "remove"],
              description: "\"define\" (default), \"list\" or \"remove\"."
            },
            name: { type: "string", description: "define, remove: the tool name, e.g. " +
              "\"fahrenheit_to_celsius\". To define, it must not clash with an existing tool." },
            description: { type: "string", description: "define: shown to yourself on future turns - " +
              "describe what it does and when to use it." },
            parameters: {
              type: "object",
              description: "define: JSON schema object for this tool's own arguments, e.g. " +
                "{\"type\":\"object\",\"properties\":{\"fahrenheit\":{\"type\":\"number\"}},\"required\":[\"fahrenheit\"]}."
            },
            code: { type: "string", description: "define: async function body implementing the tool, " +
              "e.g. \"return (args.fahrenheit - 32) * 5 / 9;\"." },
            libraries: {
              type: "array",
              description: "define: https:// URLs to preload before each call.",
              items: { type: "string" }
            }
          }
        }
      };
    })
    .declareMethod('render', function () {
      return;
    })
    .declareMethod('execute', function (args) {
      var command = args.command || "define";
      if (command === "list") {
        return this.listTool();
      }
      if (command === "remove") {
        return this.removeTool(args);
      }
      if (command === "define") {
        return this.defineTool(args);
      }
      return "ERROR: unknown command \"" + command + "\" - use \"define\", \"list\" or \"remove\".";
    })
    .declareMethod('defineTool', function (args) {
      var gadget = this,
        name = String(args.name || "").trim();
      if (!name) {
        return "ERROR: a tool name is required.";
      }
      if (!args.code) {
        return "ERROR: the code of the tool is required.";
      }
      return gadget.isToolNameTaken(name)
        .push(function (taken) {
          if (taken) {
            return "ERROR: a tool named \"" + name + "\" already exists (built-in, MCP, or " +
              "previously defined) - pick another name, or remove it first.";
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
    })
    .declareMethod('listTool', function () {
      return this.listDynamicToolSpecs()
        .push(function (spec_list) {
          if (!spec_list.length) {
            return "(no tools defined yet)";
          }
          return spec_list.map(function (spec) {
            return spec.name + ": " + spec.description + "\nparameters: " + JSON.stringify(spec.parameters || {}) +
              "\ncode:\n" + spec.code;
          }).join("\n\n");
        });
    })
    .declareMethod('removeTool', function (args) {
      var gadget = this;
      return gadget.undefineDynamicTool(args.name)
        .push(function (result) {
          if (result === "not_found") {
            return "ERROR: no such defined tool \"" + args.name + "\".";
          }
          if (result === "not_dynamic") {
            return "ERROR: \"" + args.name + "\" is a built-in tool and cannot be removed.";
          }
          return gadget.removeDefinedTool(args.name)
            .push(function () {
              return "Removed tool \"" + args.name + "\".";
            }, function (err) {
              return "Removed tool \"" + args.name + "\" from this task, but deleting its saved " +
                "copy failed, so it comes back in the other tasks: " +
                (err && err.message ? err.message : String(err));
            });
        });
    });
}(window, rJS, RSVP));
