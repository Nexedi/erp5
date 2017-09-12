/*global window, rJS*/
/*jslint nomen: true, maxlen:80, indent:2*/
(function (rJS) {
  "use strict";

  rJS(window)
    .declareMethod('render', function (options) {
      this.element.querySelector('input').value = options.value || "";
      this.element.querySelector('input').title = options.key;
      this.element.querySelector('input').setAttribute('data-name',
                                                       options.key || "");
    })

    .declareMethod('getContent', function () {
      var input = this.element.querySelector('input'),
        form_gadget = this,
        result = {};
      result[input.getAttribute('data-name')] = input.value;
      return result;
    });

}(rJS));