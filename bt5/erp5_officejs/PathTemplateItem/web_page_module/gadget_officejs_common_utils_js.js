/*global window, rJS, Query, SimpleQuery, ComplexQuery, console */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, Query, SimpleQuery, ComplexQuery, console) {
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

    .declareMethod("checkViewsAndActions", function (portal_type, action_category) {
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

    .declareMethod("formatSettingList", function (configuration_list_string, portal_type) {
      var i = 0, formatted_list = [], configuration_list, pair;
      try {
        configuration_list_string = configuration_list_string.replace(/\(/g, '[')
          .replace(/\)/g, ']')
          .replace(/,\]/g, ']')
          .replace(/\'/g, '"');
        configuration_list = JSON.parse(configuration_list_string);
        for (i = 0; i < configuration_list.length; i += 1) {
          pair = configuration_list[i].split(" | ");
          if (!portal_type || pair[0] === portal_type) {
            formatted_list.push(pair);
          }
        }
      } catch (e) {
        console.log("Error while parsing configuration settings. Format error maybe?");
        console.log(e);
      }
      return formatted_list;
    })

    .declareMethod("getAppActions", function (portal_type) {
      var gadget = this;
      return gadget.getSetting('app_actions')
        .push(function (app_actions_setting) {
          return gadget.formatSettingList(app_actions_setting, portal_type);
        });
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
          return gadget.getSetting("app_allowed_sub_types");
        })
        .push(function (allowed_sub_types_setting) {
          return gadget.formatSettingList(allowed_sub_types_setting, portal_type);
        })
        .push(function (allowed_sub_types_pairs) {
          var allowed_sub_types = allowed_sub_types_pairs.map(function (pair) {
              return pair[1];
            });
          form_definition.allowed_sub_types_list = allowed_sub_types;
          return gadget.checkViewsAndActions(portal_type, action_type);
        })
        .push(function (has_more_dict) {
          //view and actions are managed by same actions-gadget-page
          form_definition.has_more_views = false;
          form_definition.has_more_actions = has_more_dict.has_more_actions;
          return form_definition;
        });
    });

}(window, rJS, Query, SimpleQuery, ComplexQuery, console));
