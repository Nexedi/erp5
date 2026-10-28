/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  rJS(window)
    .declareAcquiredMethod("undefineDynamicTool", "undefineDynamicTool")
    .declareAcquiredMethod("removeDefinedTool", "removeDefinedTool")
    .declareMethod('getDefinition', function () {
      return {
        name: "undefine_tool",
        executionMode: "sequential",
        description: "Remove a tool you previously created with define_tool, including its persisted " +
          "copy. Built-in and MCP tools cannot be removed.",
        parameters: {
          type: "object",
          properties: { name: { type: "string" } },
          required: ["name"]
        }
      };
    })
    .declareMethod('render', function () {
      return;
    })
    .declareMethod('execute', function (args) {
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
              return "Removed tool \"" + args.name + "\" from this conversation, but deleting its " +
                "persisted copy failed: " + (err && err.message ? err.message : String(err));
            });
        });
    });
}(window, rJS, RSVP));
