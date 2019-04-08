/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, Blob) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_post", "jio_post")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("handleAction", function (jio_key, portal_type) {
      var gadget = this, jio_document, action_reference;
      return gadget.getUrlParameter("action")
      .push(function (action_parameter) {
        action_reference = action_parameter;
        return gadget.jio_get(jio_key);
      })
      .push(function (document) {
        // This is the custom code to handle this specific reply action
        if (action_reference == "reply") {
          var doc, title = document.title;
          if (! title.startsWith("Re: ")) {
            title = "Re: " + document.title;
          }
          doc = {
            title: title,
            //thread parent: same as base post
            source_reference: document.source_reference,
            portal_type: document.portal_type,
            parent_relative_url: document.parent_relative_url
          };
          return gadget.jio_post(doc)
          .push(function (id) {
            jio_key = id;
            return gadget.jio_get(jio_key);
          })
          .push(function (created_doc) {
            jio_document = created_doc;
            return [jio_key, jio_document, action_reference];
          });
        }
        return [jio_key, jio_document, action_reference];
      });
    })

    .declareMethod("render", function (options) {
      var gadget = this, doc_id;
      return RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.getSetting('portal_type'),
            gadget.getSetting('parent_relative_url')
          ]);
        })
        .push(function (result) {
          return gadget.handleAction(options.jio_key, result[0]);
        })
        .push(function (action_result) {
          return gadget.redirect({
            command: 'change',
            options: {
              page: undefined,
              jio_key: action_result[0],
              view: action_result[2]
            }
          });
        });
    });
}(window, rJS, RSVP, Blob));
