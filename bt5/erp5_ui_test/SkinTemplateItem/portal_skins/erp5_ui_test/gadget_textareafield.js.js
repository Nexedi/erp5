/*global window, rJS*/
/*jslint nomen: true, maxlen:80, indent:2*/
(function (rJS) {
  "use strict";

  rJS(window)
    .declareAcquiredMethod('notifyChange', 'notifyChange')
    .declareAcquiredMethod('translateHtml', 'translateHtml')
    .declareMethod('render', function (options) {
      var form_gadget = this;
      // gadgets can use translation methods also in xhtml style,
      // this test gadget also exercise this.
      return form_gadget
        .translateHtml(form_gadget.element.innerHtml)
        .push(function (html) {
          form_gadget.element.innerHtml = html;
          form_gadget.element.firstChild.value = options.value || "";
          form_gadget.element.firstChild.title = options.key;
          form_gadget.element.firstChild.setAttribute(
            "data-name",
            options.key || ""
          );
        });
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