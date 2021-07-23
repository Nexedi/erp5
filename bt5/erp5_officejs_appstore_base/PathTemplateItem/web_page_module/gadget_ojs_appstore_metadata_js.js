/*global window, rJS*/
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS) {
  "use strict";
  rJS(window)
    .declareMethod('render', function (options) {
      var value = "Not found",
        css_class = "ui-btn orange";
      if (options.metadata.message) {
        value = options.metadata.message;
        if (options.metadata.status === 0) {
          css_class = "ui-btn-disabled green";
        }
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

}(window, rJS));