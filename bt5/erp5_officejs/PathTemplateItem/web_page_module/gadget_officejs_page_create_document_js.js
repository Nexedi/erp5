/*global window, document, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, document, rJS, RSVP) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("getUrlForList", "getUrlForList")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("jio_post", "jio_post")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("render", function (options) {
      var gadget = this,
        allowed_sub_types_list = options.allowed_sub_types_list.split(","),
        parent_portal_type = options.portal_type,
        portal_type,
        document_title;
      return gadget.jio_get(options.jio_key)
        .push(function (document) {
          document_title = document.title;
          return document.portal_type;
        }, function () {
          document_title = options.portal_type;
          return options.portal_type;
        })
        .push(function (portal_type_result) {
          portal_type = portal_type_result;
          // TODO: somehow (a generic action?) get the path string:${object_url}/Base_viewNewContentDialog
          // for now hardcoded
          // get corresponding form definition (only contains a select field)
          return gadget.jio_get("portal_skins/erp5_hal_json_style/Base_viewNewContentDialog");
        })
        .push(function (form_result) {
          form_result.form_definition.title = "Create Document";
          return gadget.changeState({
            doc: { title: document_title, portal_type: allowed_sub_types_list },
            parent_portal_type: parent_portal_type,
            action_options: options,
            child_gadget_url: 'gadget_erp5_pt_form_dialog.html',
            form_type: 'dialog',
            form_definition: form_result.form_definition,
            view: "view"
          });
        });
    })

    .onStateChange(function () {
      var fragment = document.createElement('div'),
        gadget = this;
      while (this.element.firstChild) {
        this.element.removeChild(this.element.firstChild);
      }
      this.element.appendChild(fragment);
      return gadget.declareGadget("gadget_officejs_form_view.html", {element: fragment,
                                                                     scope: 'fg'})
        .push(function (form_view_gadget) {
          return form_view_gadget.render(gadget.state);
        });
    })

    .allowPublicAcquisition('submitContent', function (options) {
      var gadget = this,
        content_dict = options[2],
        doc = {
          title: "Untitled Document",
          portal_type: content_dict.portal_type,
          parent_relative_url: gadget.state.parent_portal_type.replace(/ /g, '_').toLowerCase()
        };
      return gadget.jio_post(doc)
        .push(function (id) {
          return gadget.redirect({
            command: 'display',
            options: {
              jio_key: id,
              editable: true
            }
          });
        });
    });

}(window, document, rJS, RSVP));