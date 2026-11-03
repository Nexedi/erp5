/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  rJS(window)
    .declareMethod('setDefinition', function (definition) {
      this.definition = definition;
    })
    .declareMethod('getDefinition', function () {
      return this.definition;
    })
    .declareMethod('render', function () {
      return;
    })
    .declareMethod('execute', function (args) {
      var definition = this.definition;
      return window.ChatToolCommon.runJsCode(definition.code, args, definition.libraries);
    });
}(window, rJS, RSVP));
