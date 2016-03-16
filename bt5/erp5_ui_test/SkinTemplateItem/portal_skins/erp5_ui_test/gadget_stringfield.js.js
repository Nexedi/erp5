/*global window, rJS*/
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
      this.props.key = options.key || "";
      this.props.element.querySelector('input').value = options.value || "";
      this.props.element.querySelector('input').title = options.key;
    })

    .declareMethod('getContent', function () {
      var input = this.props.element.querySelector('input'),
        form_gadget = this,
        result = {};
      result[form_gadget.props.key] = input.value;
      return result;
    });

}(rJS));