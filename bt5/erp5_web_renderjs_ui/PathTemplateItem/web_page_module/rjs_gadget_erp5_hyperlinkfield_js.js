/*global window, rJS, domsugar */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS, domsugar) {
  "use strict";

  rJS(window)
    .declareMethod('render', function (options) {
      var gadget = this,
        field_json = options.field_json || {},
        relative_url = field_json.relative_url;
      if (relative_url) {
        return gadget.getUrlFor({command: 'display', options: {jio_key: relative_url}})
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