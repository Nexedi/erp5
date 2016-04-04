/*global window, rJS, RSVP */
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
      var input = this.element.querySelector('input'),
        field_json = options.field_json || {};
      input.checked = field_json.value || field_json.default;
      input.setAttribute('name', field_json.key);
      input.setAttribute('title', field_json.title);
      if (field_json.editable === 0) {
        input.setAttribute("class", "ui-btn ui-state-readonly");
      }
    })

    .declareMethod('getContent', function () {
      var input = this.element.querySelector('input'),
        result = {};
      result[input.getAttribute('name')] = (input.checked ? 1 : 0);
      return result;
    });
}(window, rJS));