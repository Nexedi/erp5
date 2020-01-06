/*global window, rJS, renderFormViewHeader */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, renderFormViewHeader) {
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

  for (i = 0; i < method_list.length; i += 1) {
    gadget_klass.declareMethod(method_list[i], propagateMethod(method_list[i]));
  }

  gadget_klass
    .declareMethod('render', function (options) {
      var argument_list = arguments;
      this.state.jio_key = options.jio_key;
      this.state.view = options.view;
      return this.getDeclaredGadget('page_form')
        .push(function (g) {
          return g.render.apply(g, argument_list);
        });
    })

    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod('isDesktopMedia', 'isDesktopMedia')
    .declareAcquiredMethod('getUrlParameter', 'getUrlParameter')
    .declareAcquiredMethod("getUrlForList", "getUrlForList")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("updatePanel", "updatePanel")

    .allowPublicAcquisition("updateHeader", function updateHeader() {
      var gadget = this;
      return gadget.jio_getAttachment(gadget.state.jio_key,
                                            'links')
        .push(function (erp5_document) {
          return renderFormViewHeader(gadget, gadget.state.jio_key,
                                      gadget.state.view,
                                      erp5_document);
        });
    })

    .allowPublicAcquisition("updatePanel", function updatePanel(param_list) {
      var gadget = this;
      return gadget.jio_getAttachment(gadget.state.jio_key,
                                            'links')
        .push(function (erp5_document) {
          return gadget.updatePanel({
            display_workflow_list: true,
            erp5_document: erp5_document,
            editable: true,
            jio_key: gadget.state.jio_key,
            view: gadget.state.view
          });
        });
    });

}(window, rJS, renderFormViewHeader));