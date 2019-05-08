/*global window, rJS, document */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, document) {
  "use strict";

  rJS(window)

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("jio_post", "jio_post")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("isDesktopMedia", "isDesktopMedia")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("getUrlForList", "getUrlForList")
    .declareAcquiredMethod('getUrlParameter', 'getUrlParameter')
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("notifySubmitted", 'notifySubmitted')
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("redirect", "redirect")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("render", function (options) {
      var gadget = this,
        default_view = "jio_view",
        common_utils_gadget_url = "gadget_officejs_common_utils.html",
        child_gadget_url = 'gadget_erp5_pt_form_view_editable.html',
        gadget_utils,
        jio_document;
      return gadget.declareGadget(common_utils_gadget_url)
        .push(function (result) {
          gadget_utils = result;
          return gadget.jio_get(options.jio_key);
        })
        .push(function (result) {
          jio_document = result;
          if (jio_document.portal_type === undefined) {
            throw new Error('Can not display document: ' + options.jio_key);
          }
          return gadget_utils.getFormDefinition(jio_document.portal_type, default_view);
        })
        .push(function (form_definition) {
          return gadget.changeState({
            jio_key: options.jio_key,
            doc: jio_document,
            //TODO child_gadget_url should be decided in utils.getFormDefinition based on form type
            child_gadget_url: child_gadget_url,
            form_definition: form_definition,
            form_type: 'page',
            editable: false,
            view: options.view,
            has_more_views: form_definition.has_more_views,
            has_more_actions: form_definition.has_more_actions
          });
        });
    })

    .onStateChange(function () {
      var fragment = document.createElement('div'),
        gadget = this,
        options;
      while (this.element.firstChild) {
        this.element.removeChild(this.element.firstChild);
      }
      this.element.appendChild(fragment);
      return gadget.declareGadget("gadget_officejs_form_view.html", {element: fragment,
                                                                     scope: 'fg'})
        .push(function (form_view_gadget) {
          return form_view_gadget.render(gadget.state);
        });
    });

}(window, rJS, document));