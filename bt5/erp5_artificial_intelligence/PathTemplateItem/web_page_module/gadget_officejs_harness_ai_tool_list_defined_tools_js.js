/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  rJS(window)
    .declareAcquiredMethod("listDynamicToolSpecs", "listDynamicToolSpecs")
    .declareMethod('getDefinition', function () {
      return {
        name: "list_defined_tools",
        description: "List the tools you have defined for yourself with define_tool in this " +
          "conversation, with their description, parameters and source code.",
        parameters: { type: "object", properties: {} }
      };
    })
    .declareMethod('render', function () {
      return;
    })
    .declareMethod('execute', function () {
      var gadget = this;
      return gadget.listDynamicToolSpecs()
        .push(function (spec_list) {
          if (!spec_list.length) {
            return "(no tools defined yet)";
          }
          return spec_list.map(function (spec) {
            return spec.name + ": " + spec.description + "\nparameters: " + JSON.stringify(spec.parameters || {}) +
              "\ncode:\n" + spec.code;
          }).join("\n\n");
        });
    });
}(window, rJS, RSVP));
