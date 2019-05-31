/*global window, rJS*/
/*jslint nomen: true, maxlen:80, indent:2*/
(function (rJS) {
  "use strict";

  rJS(window)
    .declareAcquiredMethod('notifyChange', 'notifyChange')
    .declareMethod('render', function (options) {
      this.element.firstChild.value = options.value || "";
      this.element.firstChild.title = options.key;
      this.element.firstChild.setAttribute('data-name',
                                           options.key || "");
    })
    .onEvent('change', function () {
      return this.notifyChange();
    })
    .declareMethod('getContent', function () {
      var input = this.element.firstChild,
        form_gadget = this,
        result = {};
      result[input.getAttribute('data-name')] = input.value;
      return result;
    });

}(rJS));