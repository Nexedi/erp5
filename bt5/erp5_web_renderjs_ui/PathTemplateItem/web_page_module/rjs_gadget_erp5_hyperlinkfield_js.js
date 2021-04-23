/*global window, rJS, domsugar */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS, domsugar) {
  "use strict";

  rJS(window)
    .declareAcquiredMethod("getUrlFor", "getUrlFor")

    .declareMethod('render', function (options) {
      var gadget = this,
        field_json = options.field_json || {};
      if (field_json.is_internal_path) {
        return gadget.getUrlFor({command: 'push_history', options: {jio_key: field_json.href}})
          .push(function (href) {
            return gadget.changeState({
              text: field_json.value || field_json.default || "",
              extra: field_json.extra || "",
              href: href
            });
          });
      }
      return this.changeState({
        text: field_json.value || field_json.default || "",
        extra: field_json.extra || "",
        href: field_json.href || ""
      });
    })

    .onStateChange(function () {
      // XXX How to support dangerous extra
      // XXX Beware, relative links will break the rJS UI
      domsugar(this.element, [domsugar('a', {
        href: this.state.href,
        text: this.state.text
      })]);
    })

    .declareMethod('getContent', function () {
      return {};
    })

    .declareMethod('checkValidity', function () {
      return true;
    });

}(window, rJS, domsugar));