/*global window, rJS, Handlebars */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, Handlebars) {
  "use strict";

  var gadget_klass = rJS(window),
    source = gadget_klass.__template_element
                         .getElementById("dispatch-template")
                         .innerHTML,
    dispatch_template = Handlebars.compile(source);

  gadget_klass

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("updateHeader", "updateHeader")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function (options) {
      var gadget = this;

      gadget.element.innerHTML = dispatch_template({item: options.query || undefined});
      return gadget.getUrlFor({command: 'display', options: {page: 'ojsm_status_list'}})
        .push(function (url) {
          return gadget.updateHeader({
            back_url: url,
            page_title: "Jump to Object"
          });
        });
    });

}(window, rJS, Handlebars));