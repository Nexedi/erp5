/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (document, window, rJS, RSVP) {
  "use strict";

  var gadget_utils, action_reference;

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("notifySubmitted", 'notifySubmitted')
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("render", function (options) {
      var gadget = this,
        child_gadget_url = 'gadget_erp5_pt_form_view_editable.html',
        portal_type, parent_portal_type,
        parent_relative_url, form_definition;
      return RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.getUrlParameter("action"),
            //maybe these settings should come as url parameters too
            gadget.getSetting('portal_type'),
            gadget.getSetting('parent_relative_url'),
            gadget.getSetting('parent_portal_type'),
            gadget.declareGadget("gadget_officejs_common_utils.html")
          ]);
        })
        .push(function (result) {
          action_reference = result[0];
          portal_type = result[1];
          parent_relative_url = result[2];
          parent_portal_type = result[3];
          gadget_utils = result[4];
          // This is the custom code to handle each specific action
          if (action_reference === "new") {
            var doc_options = {};
            doc_options.portal_type = portal_type;
            doc_options.parent_relative_url = parent_relative_url;
            return gadget_utils.getFormDefinition(parent_portal_type, action_reference)
              .push(function (result) {
                form_definition = result;
                return gadget_utils.createDocument(doc_options);
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
                    //HARDCODED: following fields should be indicated by the configuration
                    editable: true,
                    has_more_views: false,
                    has_more_actions: true,
                    is_form_list: false
                  });
                });
              });
          }
          if (action_reference === "reply") {
            var parent_document, child_document, child_jio_key;
            return gadget.jio_get(options.jio_key)
              .push(function (result) {
                parent_document = result;
                return gadget_utils.getFormDefinition(parent_document.portal_type, action_reference);
              })
              .push(function (result) {
                var title = parent_document.title;
                form_definition = result;
                if (!title.startsWith("Re: ")) {
                  title = "Re: " + parent_document.title;
                }
                return gadget.changeState({
                  doc: {title: title},
                  parent_document: parent_document,
                  child_gadget_url: child_gadget_url,
                  form_definition: form_definition,
                  view: action_reference,
                  //HARDCODED: following fields should be indicated by the configuration
                  editable: true,
                  has_more_views: false,
                  has_more_actions: false,
                  is_form_list: false
                });
              });
          }
          throw "Action " + action_reference + " not implemented yet";
        });
    })

    .onStateChange(function () {
      return gadget_utils.renderGadget(this);
    })
    .allowPublicAcquisition('notifySubmit', function () {
      return this.triggerSubmit();
    })
    .declareMethod('triggerSubmit', function () {
      return this.getDeclaredGadget('fg')
        .push(function (gadget) {
          return gadget.triggerSubmit();
        });
    })

    .allowPublicAcquisition('submitContent', function (options) {
      var gadget = this,
        jio_key = options[0],
        //target_url = options[1],
        content_dict = options[2],
        property;
      // This is the custom code to handle each specific action
      if (action_reference === "reply") {
        var document = {
          my_title: gadget.state.doc.title,
          portal_type: gadget.state.parent_document.portal_type,
          parent_relative_url: gadget.state.parent_document.parent_relative_url,
          my_source_reference: gadget.state.parent_document.source_reference
        };
        for (property in content_dict) {
          if (content_dict.hasOwnProperty(property)) {
            document["my_" + property] = content_dict[property];
          }
        }
        return gadget_utils.createDocument(document)
        .push(function (jio_key) {
          return gadget.notifySubmitting();
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
      }
      if (action_reference === "new") {
        return gadget.notifySubmitting()
        .push(function () {
          // this should be jio_getattachment (using target_url)
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
      }
    });
}(document, window, rJS, RSVP));
