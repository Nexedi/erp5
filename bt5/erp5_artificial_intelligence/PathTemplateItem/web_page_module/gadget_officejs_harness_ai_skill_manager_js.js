/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  var STATIC_SKILL_SCOPE_LIST = [
      "skill_create_html_report"
    ];

  rJS(window)
    .declareMethod('render', function (options) {
      var gadget = this;
      return new RSVP.Queue(RSVP.all(STATIC_SKILL_SCOPE_LIST.map(function (scope) {
          return gadget.getDeclaredGadget(scope);
        })))
        .push(function (skill_gadget_list) {
          return new RSVP.Queue(RSVP.all(skill_gadget_list.map(function (skill_gadget) {
              return skill_gadget.render(options);
            })))
            .push(function () {
              return RSVP.all(skill_gadget_list.map(function (skill_gadget) {
                return skill_gadget.getDefinition();
              }));
            });
        })
        .push(function (definition_list) {
          gadget.skill_list = definition_list;
        });
    })
    .declareMethod('getSkillByName', function (name) {
      var skill_list = this.skill_list || [], i;
      for (i = 0; i < skill_list.length; i += 1) {
        if (skill_list[i].name === name) {
          return skill_list[i];
        }
      }
      return null;
    })
    .declareMethod('formatSkillListForPrompt', function () {
      var skill_list = this.skill_list || [];
      if (!skill_list.length) {
        return null;
      }
      return "Skills give instructions for specific tasks. When the task matches the description of a " +
        "skill, call load_skill with its name to get its instructions.\n\n<available_skills>\n" +
        skill_list.map(function (skill) {
          return "  <skill>\n    <name>" + skill.name + "</name>\n    <description>" +
            skill.description + "</description>\n  </skill>";
        }).join("\n") + "\n</available_skills>";
    });
}(window, rJS, RSVP));
