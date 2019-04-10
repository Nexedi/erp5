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
        action_reference,
        gadget_script;
      return RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.getUrlParameter("action"),
            gadget.getSetting('portal_type'),
            gadget.getSetting('parent_relative_url'),
            gadget.declareGadget("gadget_officejs_create_document.html")
          ]);
        })
        .push(function (result) {
          var portal_type = result[1],
            parent_relative_url = result[2];
          action_reference = result[0];
          gadget_script = result[3];
          // This is the custom code to handle each specific action
          // TODO: move to specific gadgets by name? e.g. page: "action_" + portal_type + action_ref
          if (action_reference === "new_post") {
            options.portal_type = portal_type;
            options.parent_relative_url = parent_relative_url;
            return gadget_script.createDocument(options)
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
          if (action_reference === "reply") {
            return gadget.jio_get(options.jio_key)
              .push(function (document) {
                var title = document.title;
                if (!title.startsWith("Re: ")) {
                  title = "Re: " + document.title;
                }
                options.portal_type = document.portal_type;
                options.parent_relative_url = document.parent_relative_url;
                options.my_title = title;
                options.my_source_reference = document.source_reference;
                return gadget_script.createDocument(options);
              })
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
          }
          throw "Action " + action_reference + " not implemented yet";
        });
    });
}(window, rJS, RSVP));
