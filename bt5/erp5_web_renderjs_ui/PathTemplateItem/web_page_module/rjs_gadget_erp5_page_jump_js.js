/*global window, rJS, renderFormViewHeader, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, renderFormViewHeader, RSVP) {
  "use strict";

  var gadget_klass = rJS(window),
    method_list = ['triggerSubmit', 'checkValidity', 'getContent'],
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

  function disable() {
    return;
  }

  for (i = 0; i < method_list.length; i += 1) {
    gadget_klass.declareMethod(method_list[i], propagateMethod(method_list[i]));
  }

  gadget_klass
    .declareMethod('render', function (options) {
      var argument_list = arguments,
        gadget = this;

      return RSVP.all([
        // Render the form_list...
        gadget.getDeclaredGadget('page_form')
          .push(function (g) {
            return g.render.apply(g, argument_list);
          }),
        // But display the panel/header for the context document
        gadget.jio_getAttachment(options.jio_key, 'links')
          .push(function (erp5_document) {
            return RSVP.all([
              renderFormViewHeader(gadget, options.jio_key,
                                        options.view,
                                        erp5_document, true),
              gadget.updatePanel({
                display_workflow_list: true,
                erp5_document: erp5_document,
                jio_key: options.jio_key,
                view: options.view,
                jump_view: options.jump_view
              })
            ]);
          })
      ]);
    })

    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod('isDesktopMedia', 'isDesktopMedia')
    .declareAcquiredMethod('getUrlParameter', 'getUrlParameter')
    .declareAcquiredMethod("getUrlForList", "getUrlForList")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("updatePanel", "updatePanel")

    // Disable the form_list header/panel
    .allowPublicAcquisition("updateHeader", disable)
    .allowPublicAcquisition("updatePanel", disable);

}(window, rJS, renderFormViewHeader, RSVP));