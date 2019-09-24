/*global window, document, rJS */
/*jslint nomen: true, indent: 2, maxerr: 10, maxlen: 80 */
(function (window, document, rJS) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("jio_post", "jio_post")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("render", function (options) {
      var gadget = this,
        allowed_sub_types_list = options.allowed_sub_types_list.split(","),
        parent_portal_type = options.portal_type,
        dialog_form = options.new_content_dialog_form,
        dialog_category = options.new_content_category,
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
          if (dialog_form) {
            return gadget.declareGadget("gadget_officejs_common_util.html")
              .push(function (gadget_util) {
                return gadget_util.getDialogFormDefinition(dialog_form,
                                                           dialog_category);
              })
              .push(function (form_definition) {
                return gadget.changeState({
                  doc: { header_title: form_definition.title || document_title,
                         portal_type: allowed_sub_types_list },
                  //TODO this should be a portal_dict setting and not global
                  parent_portal_type: parent_portal_type,
                  action_options: options,
                  child_gadget_url: form_definition.child_gadget_url,
                  form_type: form_definition.form_type,
                  form_definition: form_definition,
                  view: "view",
                  show_dialog: true
                });
              });
          }
          return gadget.changeState({
            doc: { header_title: document_title,
                   portal_type: allowed_sub_types_list },
            parent_portal_type: parent_portal_type,
            show_dialog: false
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
      }
      // if no form, skip dialog assuming there is only one portal type
      return gadget.createDocument(gadget.state.doc.portal_type[0],
                                   gadget.state.parent_portal_type
                                   .replace(/ /g, '_').toLowerCase());
    })

    .declareMethod("createDocument", function (portal_type,
                                               parent_portal_type,
                                               content) {
      var gadget = this,
        doc = {};
      if (!content) {
        doc.portal_type = portal_type;
        doc.parent_relative_url = parent_portal_type;
      } else {
        doc = content;
      }
      if (!doc.title) {
        doc.title = "Untitled document";
      }
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

    .declareMethod("triggerSubmit", function () {
      return this.element.querySelector('button[type="submit"]').click();
    })

    .allowPublicAcquisition('submitContent', function (options) {
      var gadget = this,
        content_dict = options[2];
      if (!content_dict.portal_type) {
        content_dict.portal_type = gadget.state.doc.portal_type[0];
      }
      if (!content_dict.parent_relative_url) {
        content_dict.parent_relative_url = gadget.state.parent_portal_type
          .replace(/ /g, '_').toLowerCase();
      }
      return gadget.createDocument(gadget.state.doc.portal_type[0],
                                   gadget.state.parent_portal_type
                                   .replace(/ /g, '_').toLowerCase(),
                                   content_dict);
    });

}(window, document, rJS));