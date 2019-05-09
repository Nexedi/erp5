/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  // TODO: check if there are other categories that are 'views' and find a less hardcoded way to get this
  var view_categories = ["object_view", "object_jio_view", "object_web_view", "object_list"];

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

    .declareMethod("getFormInfo", function (form_definition) {
      var child_gadget_url,
        form_type,
        action_category = form_definition.action_type;
      switch (action_category) {
      case 'object_list':
        form_type = 'list';
        child_gadget_url = 'gadget_erp5_pt_form_list.html';
        break;
      case 'object_dialog':
        form_type = 'dialog';
        child_gadget_url = 'gadget_erp5_pt_form_dialog.html';
        break;
      case 'object_jio_js_script':
        form_type = 'dialog';
        child_gadget_url = 'gadget_erp5_pt_form_dialog.html';
        break;
      default:
        form_type = 'page';
        child_gadget_url = 'gadget_erp5_pt_form_view_editable.html';
      }
      return [form_type, child_gadget_url];
    })

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

    .declareMethod("checkMoreActions", function (portal_type, action_category) {
      var gadget = this,
        has_more_dict = {views: {}, actions: {}},
        query;
      //if target action is a type of view, get all actions/views for the portal_type
      if (view_categories.includes(action_category)) {
        query = 'portal_type: "Action Information" AND parent_relative_url: "portal_types/' + portal_type + '"';
        return gadget.jio_allDocs({query: query})
          .push(function (action_list) {
            var path_for_jio_get_list = [], row;
            for (row in action_list.data.rows) {
              if (action_list.data.rows.hasOwnProperty(row)) {
                path_for_jio_get_list.push(gadget.jio_get(action_list.data.rows[row].id));
              }
            }
            return RSVP.all(path_for_jio_get_list);
          })
          .push(function (action_document_list) {
            var get_action_settings_list = [], page, action_key, action_doc;
            for (action_key in action_document_list) {
              if (action_document_list.hasOwnProperty(action_key)) {
                action_doc = action_document_list[action_key];
                if (view_categories.includes(action_doc.action_type)) {
                  has_more_dict.has_more_views = true;
                } else {
                  has_more_dict.has_more_actions = true;
                }
              }
            }
            return has_more_dict;
          });
      }
      return has_more_dict;
    })

    .declareMethod("getFormDefinition", function (portal_type, action_reference, source_reference) {
      var gadget = this,
        parent = "portal_types/" + portal_type,
        query = 'portal_type: "Action Information" AND reference: "' + action_reference + '" AND parent_relative_url: "' + parent + '"',
        action_type, action_title, form_definition;
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
          form_definition = form_result.form_definition;
          form_definition.action_type = action_type;
          form_definition.title = action_title;
          return gadget.checkMoreActions(portal_type, action_type);
        })
        .push(function (has_more_dict) {
          //view and actions are managed by same actions-gadget-page
          form_definition.has_more_views = false;
          form_definition.has_more_actions = has_more_dict.has_more_actions;
          //for backward compatibility (header add button - '+' icon)
          if (form_definition.action_type === "object_list") {
            form_definition._links.action_object_new_content_action = {
              page: "handle_action",
              title: "New Post",
              action: "new_html_post",
              reference: "new_html_post",
              action_type: "object_jio_js_script",
              parent_portal_type: "Post Module",
              portal_type: "HTML Post",
              source_reference: source_reference
            };
            //form_definition.has_more_actions = false;
          }
          return form_definition;
        });
    });

}(window, rJS, RSVP));
