/*jslint indent: 2 */
/*global window, rJS, RSVP, svgCanvas, editor */
(function (window, rJS, RSVP) {
  "use strict";

  rJS(window)
    .declareMethod('render', function (options) {
      return this.changeState({
        key: options.key,
        value: options.value
      });
    })
    .onStateChange(function () {
      svgCanvas.setSvgString(this.state.value);
    })
    .declareService(function () {
      if (/(?:^\?|&)auto_focus=(true|1)(?:&|$)/.test(window.location.search)) {
        window.focus();  // should be done by the parent gadget?
      }
    })
    .declareMethod('getContent', function () {
      var form_data = {};
      editor.escapeMode();
      form_data[this.state.key] = svgCanvas.getSvgString();
      this.state.value = form_data[this.state.key];
      return form_data;
    }, {mutex: 'statechange'});

}(window, rJS, RSVP));
