/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  rJS(window)
    .declareAcquiredMethod("getSkillByName", "getSkillByName")
    .declareMethod('getDefinition', function () {
      return {
        name: "load_skill",
        description: "Load the full instructions for a skill listed in <available_skills> by " +
          "name, when the current task matches its description.",
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
      return gadget.getSkillByName(args.name)
        .push(function (skill) {
          if (!skill) {
            return "ERROR: no such skill \"" + args.name + "\".";
          }
          return skill.instructions;
        });
    });
}(window, rJS, RSVP));
