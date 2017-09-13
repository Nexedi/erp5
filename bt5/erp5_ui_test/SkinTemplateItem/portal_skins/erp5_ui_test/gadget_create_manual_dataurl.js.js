/*global window, rJS, btoa*/
/*jslint nomen: true, maxlen:80, indent:2*/
(function (rJS) {
  "use strict";

  rJS(window)
    .declareMethod('render', function (options) {
      var gadget = this;
      gadget.element.querySelector('input').key = options.key || "";
      gadget.element.querySelector('input').value = options.value;
      gadget.element.querySelector('input').title = options.key;
    })

    .declareMethod('getContent', function () {
      var input = this.element.querySelector('input'),
        form_gadget = this,
        result = {};
      if (input.value) {
        result[input.key] = "data:text/plain;base64," + btoa(input.value);
      }
      return result;
    });

}(rJS));