/*global window, rJS */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS) {
  "use strict";

  var gadget_klass = rJS(window),
    method_list = ['triggerSubmit', 'checkValidity', 'getContent', 'render'],
    i;

  function propagateMethod(method_name) {
    return function callMethod() {
      var argument_list = arguments;
      return this.getDeclaredGadget('page_form')
        .push(function (g) {
          return g[method_name].apply(g, argument_list);
        });
    };
  }

  for (i = 0; i < method_list.length; i += 1) {
    gadget_klass.declareMethod(method_list[i], propagateMethod(method_list[i]));
  }

}(window, rJS));