/*global window, rJS*/
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS) {
  "use strict";

  rJS(window)

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    .declareAcquiredMethod("notifyChange", "notifyChange")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('render', function () {
      return this.changeState({
        // No need to update the form if render is called twice
        first_render: true
      });
    })

    .onStateChange(function (modification_dict) {
      var gadget = this;

      if (modification_dict.hasOwnProperty('first_render')) {
        return gadget.getUrlFor({
          command: 'change',
          options: {page: "jabberclient_contact"}
        })
          .push(function (url) {
            return gadget.updateHeader({
              page_title: 'New Contact',
              cancel_url: url
            });
          })
          .push(function () {
            return gadget.getDeclaredGadget("form_dialog");
          })
          .push(function (form_gadget) {
            return form_gadget.render({
              erp5_document: {"_embedded": {"_view": {
                "jid": {
                  "description": "",
                  "title": "Jabber ID",
                  "default": "",
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "jid",
                  "hidden": 0,
                  "type": "StringField"
                }
              }}},
              form_definition: {
                group_list: [[
                  "left",
                  [["jid"]]
                ]]
              }
            });
          });

      }
    })

    .allowPublicAcquisition("submitContent", function submitContent(param_list) {
      var gadget = this,
        content_dict = param_list[0];
      return gadget.jio_put(
        'SUBSCRIBE',
        content_dict
      )
        .push(function () {
          return gadget.redirect({
            command: 'change',
            options: {page: "jabberclient_contact"}
          });
        });
    });

}(window, rJS));