/*global window, rJS, Query, SimpleQuery, ComplexQuery */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, Query, SimpleQuery, ComplexQuery) {
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

    .declareMethod("checkMoreActions", function (portal_type, action_category) {
      var gadget = this,
        //for now, views and actions are handle together via handle_action gadget
        has_more_dict = {views: {}, actions: {}},
        query,
        query_type,
        query_parent;
      // get all actions/views for the portal_type, if target action is a type of view
      // (exclude custom scripts and dialogs)
      if (view_categories.includes(action_category)) {
        query_type = new SimpleQuery({
          key: "portal_type",
          operator: "",
          type: "simple",
          value: "Action Information"
        });
        query_parent = new SimpleQuery({
          key: "parent_relative_url",
          operator: "",
          type: "simple",
          value: "portal_types/" + portal_type
        });
        query = Query.objectToSearchText(new ComplexQuery({
          operator: "AND",
          query_list: [query_type, query_parent],
          type: "complex"
        }));
        return gadget.jio_allDocs({query: query})
          .push(function (action_list) {
            if (action_list.data.rows.length > 0) {
              has_more_dict.has_more_actions = true;
            }
            return has_more_dict;
          });
      }
      return has_more_dict;
    })

    .declareMethod("getFormDefinition", function (portal_type, action_reference) {
      var gadget = this,
        query,
        action_type,
        action_title,
        form_definition,
        query_type,
        query_parent,
        query_reference;
      query_reference = new SimpleQuery({
        key: "reference",
        operator: "",
        type: "simple",
        value: action_reference
      });
      query_type = new SimpleQuery({
        key: "portal_type",
        operator: "",
        type: "simple",
        value: "Action Information"
      });
      query_parent = new SimpleQuery({
        key: "parent_relative_url",
        operator: "",
        type: "simple",
        value: "portal_types/" + portal_type
      });
      query = Query.objectToSearchText(new ComplexQuery({
        operator: "AND",
        query_list: [query_type, query_parent, query_reference],
        type: "complex"
      }));
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
          return gadget.jio_get("portal_types/" + portal_type);
        })
        .push(function (portal_type_definition) {
          form_definition.allowed_sub_types_list = portal_type_definition.type_allowed_content_type_list;
          return gadget.checkMoreActions(portal_type, action_type);
        })
        .push(function (has_more_dict) {
          //view and actions are managed by same actions-gadget-page
          form_definition.has_more_views = false;
          form_definition.has_more_actions = has_more_dict.has_more_actions;
          return form_definition;
        });
    });

}(window, rJS, Query, SimpleQuery, ComplexQuery));
