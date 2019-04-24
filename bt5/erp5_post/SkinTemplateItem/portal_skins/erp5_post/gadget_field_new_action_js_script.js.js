/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  var parent_gadget, form_view_gadget;

  rJS(window)

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod('getUrlParameter', 'getUrlParameter')
    .declareAcquiredMethod("notifySubmitted", 'notifySubmitted')
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("redirect", "redirect")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("render", function (gadget) {
      return form_view_gadget.renderGadget(gadget);
    })

    .declareMethod("handleRender", function (gadget, options, action_reference, form_definition) {
      var child_gadget_url = 'gadget_erp5_pt_form_view_editable.html', this_gadget = this;
      parent_gadget = gadget;
      return RSVP.Queue()
        .push(function () {
          return RSVP.all([
            parent_gadget.getUrlParameter('portal_type'),
            parent_gadget.getUrlParameter('parent_relative_url'),
            parent_gadget.getSetting('portal_type'),
            parent_gadget.getSetting('parent_relative_url'),
            parent_gadget.declareGadget("gadget_officejs_form_view.html")
          ]);
        })
        .push(function (result) {
          if (result[0] !== undefined) {options.portal_type = result[0]; } else {options.portal_type = result[2]; }
          if (result[1] !== undefined) {options.parent_relative_url = result[1]; } else {options.parent_relative_url = result[3]; }
          form_view_gadget = result[4];
          return form_view_gadget.createDocument(options)
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

    .declareMethod("handleSubmit", function (gadget, jio_key, content_dict) {
      return gadget.notifySubmitting()
        .push(function () {
          return gadget.jio_get(jio_key);
        })
        .push(function (document) {
          var property;
          for (property in content_dict) {
            if (content_dict.hasOwnProperty(property)) {
              document[property] = content_dict[property];
            }
          }
          return gadget.jio_put(jio_key, document);
        })
        .push(function () {
          return gadget.notifySubmitted({message: 'Data Updated', status: 'success'});
        })
        .push(function () {
          return gadget.redirect({
            command: 'display',
            options: {
              jio_key: jio_key,
              editable: true
            }
          });
        });
    });

}(window, rJS, RSVP));