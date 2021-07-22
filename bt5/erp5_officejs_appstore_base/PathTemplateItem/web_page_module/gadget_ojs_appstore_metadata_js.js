/*global window, rJS, RSVP*/
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";
  rJS(window)
    .declareMethod('render', function (options) {
      var metadata,
        value = "Not found",
        css_class = "ui-btn orange";
      try {
        metadata = JSON.parse(options.metadata);
        value = metadata.message;
        if (metadata.status === 0) {
          css_class = "ui-btn-disabled green";
        }
      } catch (e) {
        value = "Error getting metadata";
      }
      return this.changeState({
        value: value,
        css_class: css_class
      });
    })
    .onStateChange(function (modification_dict) {
      var a = this.element.querySelector("a");
      if (modification_dict.hasOwnProperty('value')) {
        a.textContent = modification_dict.value;
      }
      if (modification_dict.hasOwnProperty('css_class')) {
        a.setAttribute('class', this.state.css_class);
      }
    });

}(window, rJS, RSVP));