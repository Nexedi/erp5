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
        description: "Manage your own tools. \"define\" creates a tool that you, and the sub-agents you " +
          "spawn, can call by name from now on. It is saved in this browser for all the " +
          "tasks, until \"remove\" removes it. Its `code` is like the code of " +
          "run_javascript, run in the same sandbox, and receives the arguments of the call " +
          "in `args`. \"list\" returns the tools you defined, with their description, " +
          "parameters and code. \"remove\" removes one of them (built-in and MCP tools can " +
          "not be removed). Define a tool only for logic you will call again with other " +
          "arguments: for a one-off computation, use run_javascript.",
        parameters: {
          type: "object",
          properties: {
            command: { type: "string", "enum": ["define", "list", "remove"], description: "Default \"define\"." },
            name: { type: "string", description: "For \"define\" and \"remove\": the tool name, eg. \"fahrenheit_to_celsius\". A new tool can not take the name of an existing one." },
            description: { type: "string", description: "For \"define\": what the tool does and when to use it." },
            parameters: {
              type: "object",
              description: "For \"define\": JSON schema of the arguments of the tool, eg. {\"type\": \"object\", " +
              "\"properties\": {\"fahrenheit\": {\"type\": \"number\"}}, \"required\": [\"fahrenheit\"]}."
            },
            code: { type: "string", description: "For \"define\": the async function body, eg. \"return (args.fahrenheit - 32) * 5 / 9;\"." },
            libraries: {
              type: "array",
              items: { type: "string" },
              description: "For \"define\": https:// URLs of scripts to load before each call, like for run_javascript."
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
