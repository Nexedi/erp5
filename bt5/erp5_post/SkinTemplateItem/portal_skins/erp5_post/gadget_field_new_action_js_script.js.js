/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  var child_gadget_url = 'gadget_erp5_pt_form_view_editable.html',
    form_view_gadget_url = "gadget_officejs_form_view.html";

  rJS(window)

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("jio_post", "jio_post")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod('getUrlParameter', 'getUrlParameter')
    .declareAcquiredMethod("notifySubmitted", 'notifySubmitted')
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("redirect", "redirect")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("createDocument", function (options) {
      var gadget = this,
        doc = {
          title: "Untitled Document",
          portal_type: options.portal_type,
          parent_relative_url: options.parent_relative_url
        },
        key,
        doc_key;
      for (key in options) {
        if (options.hasOwnProperty(key)) {
          if (key.startsWith("my_")) {
            doc_key = key.replace("my_", "");
            doc[doc_key] = options[key];
          }
        }
      }
      return gadget.jio_post(doc);
    })

    .declareMethod("render", function (parent_gadget) {
      var gadget = this;
      return gadget.declareGadget(form_view_gadget_url)
      .push(function (form_view_gadget) {
        return form_view_gadget.renderGadget(parent_gadget);
      });
    })

    .declareMethod("handleRender", function (parent_gadget, options, action_reference, form_definition) {
      var this_gadget = this;
      return RSVP.Queue()
        .push(function () {
          return RSVP.all([
            parent_gadget.getUrlParameter('portal_type'),
            parent_gadget.getUrlParameter('parent_relative_url'),
            parent_gadget.getSetting('portal_type'),
            parent_gadget.getSetting('parent_relative_url')
          ]);
        })
        .push(function (result) {
          if (result[0] !== undefined) {options.portal_type = result[0]; } else {options.portal_type = result[2]; }
          if (result[1] !== undefined) {options.parent_relative_url = result[1]; } else {options.parent_relative_url = result[3]; }
          return this_gadget.createDocument(options)
            .push(function (jio_key) {
              return parent_gadget.jio_get(jio_key)
              .push(function (new_document) {
                return parent_gadget.changeState({
                  jio_key: jio_key,
                  doc: new_document,
                  child_gadget_url: child_gadget_url,
                  form_definition: form_definition,
                  view: action_reference,
                  editable: true,
                  has_more_views: false,
                  has_more_actions: true,
                  is_form_list: false
                });
              });
            });
        });
    })

    .declareMethod("handleSubmit", function (parent_gadget, jio_key, content_dict) {
      return parent_gadget.notifySubmitting()
        .push(function () {
          return parent_gadget.jio_get(jio_key);
        })
        .push(function (document) {
          var property;
          for (property in content_dict) {
            if (content_dict.hasOwnProperty(property)) {
              document[property] = content_dict[property];
            }
          }
          return parent_gadget.jio_put(jio_key, document);
        })
        .push(function () {
          return parent_gadget.notifySubmitted({message: 'Data Updated', status: 'success'});
        })
        .push(function () {
          return parent_gadget.redirect({
            command: 'display',
            options: {
              jio_key: jio_key,
              editable: true
            }
          });
        });
    });

}(window, rJS, RSVP));