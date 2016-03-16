/*global window, rJS, btoa*/
/*jslint nomen: true, maxlen:80, indent:2*/
(function (rJS) {
  "use strict";

  rJS(window)
    .ready(function (g) {
      g.props = {};
    })
    .ready(function (g) {
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
        });
    })
    .declareMethod('render', function (options) {
      var gadget = this;
      gadget.props.key = options.key || "";
      gadget.props.element.querySelector('input').value = options.value;
      gadget.props.element.querySelector('input').title = options.key;
    })

    .declareMethod('getContent', function () {
      var input = this.props.element.querySelector('input'),
        form_gadget = this,
        result = {};
      if (input.value) {
        result[form_gadget.props.key] = "data:text/plain;base64,"
                                                 + btoa(input.value);
      }
      return result;
    });

}(rJS));