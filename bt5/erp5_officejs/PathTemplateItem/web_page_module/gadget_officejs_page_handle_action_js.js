/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
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

    .declareMethod("handleAction", function (jio_key) {
      var gadget = this, action_reference;
      return gadget.getUrlParameter("action")
        .push(function (action_parameter) {
          action_reference = action_parameter;
          return gadget.jio_get(jio_key);
        })
        .push(function (document) {
          // This is the custom code to handle this specific reply action
          if (action_reference == "reply") {
            var doc, title = document.title;
            if (!title.startsWith("Re: ")) {
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
                return [id, action_reference];
              });
          }
          return [jio_key, action_reference];
        });
    })

    .declareMethod("render", function (options) {
      var gadget = this;
      return RSVP.Queue()
        .push(function () {
          return gadget.handleAction(options.jio_key);
        })
        .push(function (action_result) {
          return gadget.redirect({
            command: 'change',
            options: {
              page: undefined,
              jio_key: action_result[0],
              view: action_result[1]
            }
          });
        });
    });
}(window, rJS, RSVP));
