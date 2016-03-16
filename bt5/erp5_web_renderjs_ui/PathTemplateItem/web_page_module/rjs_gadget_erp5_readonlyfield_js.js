/*global window, rJS */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS) {
  "use strict";

  rJS(window)
    .ready(function (gadget) {
      return gadget.getElement()
        .push(function (element) {
          gadget.element = element;
        });
    })
    .declareMethod('render', function (options) {
      var input = this.element.querySelector('p'),
        field_json = options.field_json || {};
      input.textContent = field_json.value || field_json.default || "";
    })

    .declareMethod('getContent', function () {
      return {};
    });

}(window, rJS));