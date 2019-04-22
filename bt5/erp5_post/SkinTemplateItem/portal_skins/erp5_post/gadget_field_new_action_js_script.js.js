/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  var gadget_utils;

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

    .declareMethod("render", function (options) {
      console.log("GADGET FIELD RENDER METHOD!!!");
      return;
    })

    .declareMethod("handleRender", function (gadget, gadget_utils, options, action_reference, parent_portal_type, form_definition) {
      console.log("GADGET FIELD handleRender METHOD!!!");
      var child_gadget_url = 'gadget_erp5_pt_form_view_editable.html';
      return RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.getUrlParameter('portal_type'),
            gadget.getUrlParameter('parent_relative_url'),
            gadget.getSetting('portal_type'),
            gadget.getSetting('parent_relative_url')
          ]);
        })
        .push(function (result) {
          if (result[0] !== undefined) {options.portal_type = result[0]; } else {options.portal_type = result[2]; }
          if (result[1] !== undefined) {options.parent_relative_url = result[1]; } else {options.parent_relative_url = result[3]; }
          return gadget_utils.getFormDefinition(parent_portal_type, action_reference)
            .push(function (result) {
              form_definition = result;
              return gadget_utils.createDocument(options);
            })
            .push(function (jio_key) {
              return gadget.jio_get(jio_key)
              .push(function (new_document) {
                return gadget.changeState({
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

    .declareMethod("handleSubmit", function (gadget, gadget_utils, jio_key, content_dict) {
      console.log("GADGET FIELD handleSubmit METHOD!!!");
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

    /*.onStateChange(function () {
      return gadget_utils.renderGadget(this);
    });*/

}(window, rJS, RSVP));