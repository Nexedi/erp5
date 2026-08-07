/*global window */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window) {
  "use strict";

  var SKILL_LIST = [
    {
      name: "draw_house",
      triggers: ["house", "home"],
      instructions: "Skill: draw_house\n" +
        "To draw a simple house on the canvas using the drawing tools:\n" +
        "1. Call clear_canvas first.\n" +
        "2. Call draw_rectangle for the main body.\n" +
        "3. Call draw_polygon with 3 points for a triangular roof sitting on top of the body.\n" +
        "4. Optionally add a door and windows with draw_rectangle.\n"
    },
    {
      name: "draw_stick_figure",
      triggers: ["stick figure", "stickman", "person", "human"],
      instructions: "Skill: draw_stick_figure\n" +
        "To draw a simple stick figure on the canvas using the drawing tools:\n" +
        "1. Call clear_canvas first.\n" +
        "2. Call draw_circle for the head.\n" +
        "3. Call draw_line for the body (vertical line down from the head).\n" +
        "4. Call draw_line twice for the arms.\n" +
        "5. Call draw_line twice for the legs.\n"
    }
  ];

  function matchSkillList(text) {
    var lower = String(text).toLowerCase();
    return SKILL_LIST.filter(function (skill) {
      return skill.triggers.some(function (trigger) {
        return lower.indexOf(trigger.toLowerCase()) !== -1;
      });
    });
  }

  window.ChatSkills = {
    SKILL_LIST: SKILL_LIST,
    matchSkillList: matchSkillList
  };
}(window));
