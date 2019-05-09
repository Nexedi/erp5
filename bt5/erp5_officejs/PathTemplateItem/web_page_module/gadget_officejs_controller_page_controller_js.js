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

    .declareMethod("getPortalType", function (jio_document, options) {
      var gadget = this;
      if (jio_document) {
        if (jio_document.portal_type === undefined) {
          throw new Error('Can not display document: ' + options.jio_key);
        }
        return jio_document.portal_type;
      }
      if (options.portal_type) {
        return options.portal_type;
      }
      return gadget.getSetting('parent_portal_type');
    })

    .declareMethod("render", function (options) {
      var gadget = this,
        default_view = "jio_view",
        common_utils_gadget_url = "gadget_officejs_common_utils.html",
        child_gadget_url = 'gadget_erp5_pt_form_view_editable.html',
        gadget_utils,
        jio_document,
        portal_type;
      return gadget.declareGadget(common_utils_gadget_url)
        .push(function (result) {
          gadget_utils = result;
          return gadget.jio_get(options.jio_key);
        })
        .push(function (result) {
          jio_document = result;
        }, function (error) {})
        .push(function () {
          return gadget.getPortalType(jio_document, options);
        })
        .push(function (result) {
          portal_type = result;
          return gadget_utils.getFormDefinition(portal_type, default_view);
        })
        .push(function (form_definition) {
          var form_type = 'page', front_page = false;
          if (form_definition.action_type === "object_list") {
            form_type = 'list';
            child_gadget_url = 'gadget_erp5_pt_form_list.html';
            //TODO: when refactoring is done in ojs_post_list (front-page), this will come from options
            front_page = true;
          }
          return gadget.changeState({
            jio_key: options.jio_key,
            doc: jio_document,
            portal_type: portal_type,
            //TODO child_gadget_url should be decided in utils.getFormDefinition based on form type
            child_gadget_url: child_gadget_url,
            form_definition: form_definition,
            form_type: form_type,
            editable: false,
            view: options.view,
            front_page: front_page, //options.front_page
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