/*global document, window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (document, window, rJS, RSVP) {
  "use strict";

  var default_view = "jio_view",
    gadget_utils;

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
        child_gadget_url = 'gadget_erp5_pt_form_view_editable.html',
        jio_document;
      return gadget.declareGadget("gadget_officejs_form_view.html")
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
          child_gadget_url: child_gadget_url,
          form_definition: form_definition,
          editable: false,
          view: options.view,
          //HARDCODED: following fields should be indicated by the configuration
          has_more_views: false,
          has_more_actions: options.view === "view",
          is_form_list: false
        });
      });
    })

    .onStateChange(function () {
      return gadget_utils.renderGadget(this);
    });

}(document, window, rJS, RSVP));