/*global window, rJS */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (document, window, rJS, RSVP) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("isDesktopMedia", "isDesktopMedia")
    .declareAcquiredMethod("getUrlForList", "getUrlForList")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("jio_post", "jio_post")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("notifySubmitted", 'notifySubmitted')
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")

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

    .declareMethod("getFormDefinition", function (portal_type, action_reference) {
      var gadget = this,
        parent = "portal_types/" + portal_type,
        query = 'portal_type: "Action Information" AND reference: "' + action_reference + '" AND parent_relative_url: "' + parent + '"';
      return gadget.jio_allDocs({query: query})
        .push(function (data) {
          if (data.data.rows.length === 0) {
            throw "Can not find action '" + action_reference + "' for portal type '" + portal_type + "'";
          }
          return gadget.jio_get(data.data.rows[0].id);
        })
        .push(function (action_result) {
          return gadget.jio_get(action_result.action);
        })
        .push(function (form_result) {
          return form_result.form_definition;
        });
    });

}(document, window, rJS, RSVP));
