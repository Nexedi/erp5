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

    .declareMethod("render", function (options) {
      var gadget = this,
        action_reference;
      return RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.getUrlParameter("action"),
            gadget.getSetting('portal_type'),
            gadget.getSetting('parent_relative_url')
          ]);
        })
          .push(function (result) {
            action_reference = result[0];
            // This is the custom code to handle each specific action
            // TODO: move to specific gadgets by name? e.g. page: "action_" + portal_type + action_ref
            if (action_reference === "new_post") {
              //TODO refactor doc creation to be reused by other actions (e.g. reply action)
              // move to a js script?
              var doc = {
                title: "Untitled Document",
                portal_type: result[1],
                parent_relative_url: result[2]
              }, key, doc_key;
              for (key in options) {
                if (options.hasOwnProperty(key)) {
                  if (key.startsWith("my_")) {
                    doc_key = key.replace("my_", "");
                    doc[doc_key] = options[key];
                  }
                }
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
            }
            if (action_reference == "reply") {
              return gadget.jio_get(options.jio_key)
              .push(function (document) {
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
                    return gadget.redirect({
                      command: "change",
                      options: {
                        page: undefined,
                        jio_key: id,
                        view: action_reference
                      }
                    });
                  });
              });
            } else {
              throw "Action " + action_reference + " not implemented yet";
            }
          });
    });
}(window, rJS, RSVP));
