/*global window, rJS */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS) {
  'use strict';
  /**
   * A gadget which embeds default header, but remove add button, because in the
   * case of support request app, adding is done through fast input.
   */
  var gadgetKlass = rJS(window)
    .declareMethod('render', function (options) {
      delete options.add_url;
      return this.getDeclaredGadget('header').push(function (headerGadget) {
        return headerGadget.render.bind(headerGadget)(options);
      });
    });

  /**
   * Delegate a method to embedded header gadget
   * @param {string}methodName method name
   */
  function delegateMethod(methodName) {
    gadgetKlass.declareMethod(methodName, function () {
      var methodArguments = arguments;
      return this.getDeclaredGadget('header').push(function (headerGadget) {
        return headerGadget[methodName].bind(headerGadget)(methodArguments);
      });
    });
  }
  delegateMethod('notifyLoaded');
  delegateMethod('notifyLoading');
  delegateMethod('notifySubmitted');
  delegateMethod('notifySubmitting');
  delegateMethod('notifyError');
  delegateMethod('notifyChange');
  delegateMethod('setButtonTitle');
}(window, rJS));