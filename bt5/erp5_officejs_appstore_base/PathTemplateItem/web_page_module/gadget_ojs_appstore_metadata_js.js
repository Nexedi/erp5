/*global window, rJS*/
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS) {
  "use strict";
  rJS(window)
    .declareMethod('render', function (options) {
      var value = "Not found";
      if (options.metadata.message) {
        value = options.metadata.message;
      }
      return this.changeState({
        value: value
      });
    })
    .onStateChange(function (modification_dict) {
      var div = this.element.querySelector("div");
      if (modification_dict.hasOwnProperty('value')) {
        div.textContent = modification_dict.value;
      }
    });
}(window, rJS));