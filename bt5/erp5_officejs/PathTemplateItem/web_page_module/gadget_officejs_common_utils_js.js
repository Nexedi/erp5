/*global window, rJS */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS) {
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

    .declareMethod("getFormDefinition", function (portal_type, action_reference, extra_params) {
      var gadget = this,
        parent = "portal_types/" + portal_type,
        query = 'portal_type: "Action Information" AND reference: "' + action_reference + '" AND parent_relative_url: "' + parent + '"',
        action_type, action_title;
      //TODO: check all actions to set has_more_views and has_more_actions flags in form def
      //also check if there is a "new" action for object_list.action_info
      return gadget.jio_allDocs({query: query})
        .push(function (data) {
          if (data.data.rows.length === 0) {
            throw "Can not find action '" + action_reference + "' for portal type '" + portal_type + "'";
          }
          return gadget.jio_get(data.data.rows[0].id);
        })
        .push(function (action_result) {
          action_title = action_result.title;
          action_type = action_result.action_type;
          return gadget.jio_get(action_result.action);
        })
        .push(function (form_result) {
          form_result.form_definition.action_type = action_type;
          form_result.form_definition.title = action_title;
          if (action_type === "object_list") {
            //TODO: get child_portal_type from form_definition (listbox->portal_type).
            var child_portal_type = "HTML Post",
              action_info = {
              page: "handle_action",
              action: "new",
              portal_type: child_portal_type,
              parent_portal_type: portal_type,
              my_source_reference: extra_params.source_reference
            };
            form_result.form_definition._links.action_object_new_content_action = action_info;
          }
          return form_result.form_definition;
        });
    });

}(window, rJS));
