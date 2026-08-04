/*global window */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window) {
  "use strict";

  var SKILL_LIST = [];

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
