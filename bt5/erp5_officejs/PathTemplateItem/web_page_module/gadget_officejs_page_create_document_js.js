/*global window, document, rJS */
/*jslint nomen: true, indent: 2, maxerr: 10, maxlen: 80 */
(function (window, document, rJS) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("jio_post", "jio_post")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("createDocument", function (portal_type,
                                               parent_portal_type) {
      var gadget = this,
        doc = {
          title: "Untitled Document",
          portal_type: portal_type,
          parent_relative_url: parent_portal_type
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
    })

    .declareMethod("render", function (options) {
      var gadget = this,
        allowed_sub_types_list = options.allowed_sub_types_list.split(","),
        parent_portal_type = options.portal_type,
        portal_type,
        form_definition,
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
          return gadget.getSetting("new_content_action");
        })
        .push(function (new_content_action) {
          if (!new_content_action) {
            throw new Error("Missing site configuration 'new_content_action'");
          }
          return gadget.jio_get(new_content_action);
        })
        .push(function (form_result) {
          form_definition = form_result.raw_dict._embedded._view
            ._embedded.form_definition;
          form_definition.fields_raw_properties = form_result.raw_dict._embedded
            ._view.my_fields_raw_properties["default"];
          form_definition._actions = form_result.raw_dict._embedded
            ._view._actions;
          form_definition.group_list = form_result.raw_dict.group_list;
          form_definition.title = "Create Document";
          return gadget.changeState({
            doc: { title: document_title, portal_type: allowed_sub_types_list },
            parent_portal_type: parent_portal_type,
            action_options: options,
            child_gadget_url: 'gadget_erp5_pt_form_dialog.html',
            form_type: 'dialog',
            form_definition: form_definition,
            view: "view",
            show_dialog: allowed_sub_types_list.length > 1
          });
        });
    })

    .onStateChange(function () {
      var fragment = document.createElement('div'),
        gadget = this;
      if (gadget.state.show_dialog) {
        while (this.element.firstChild) {
          this.element.removeChild(this.element.firstChild);
        }
        this.element.appendChild(fragment);
        return gadget.declareGadget("gadget_officejs_form_view.html",
                                    {element: fragment, scope: 'fg'})
          .push(function (form_view_gadget) {
            return form_view_gadget.render(gadget.state);
          });
      } else {
        // if there is only one sub portal type
        // skip create document dialog rendering
        return gadget.createDocument(gadget.state.doc.portal_type[0],
                                     gadget.state.parent_portal_type
                                     .replace(/ /g, '_').toLowerCase());
      }
    })

    .allowPublicAcquisition('submitContent', function (options) {
      var gadget = this,
        content_dict = options[2];
      return gadget.createDocument(content_dict.portal_type,
                                   gadget.state.parent_portal_type
                                   .replace(/ /g, '_').toLowerCase());
    });

}(window, document, rJS));