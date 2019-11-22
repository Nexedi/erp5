/*global window, rJS, RSVP, Query, SimpleQuery, ComplexQuery, console */
/*jslint nomen: true, indent: 2, maxerr: 10, maxlen: 80 */
(function (window, rJS, RSVP, Query, SimpleQuery, ComplexQuery, console) {
  "use strict";

  // TODO: check if there are other categories that are 'views'
  // and find a less hardcoded way to get this
  var view_categorie_list = ["object_view", "object_jio_view",
                             "object_web_view", "object_list"];

  function filterViewList(views_dict, app_view, default_view) {
    // there must be only one "View" action (title = "View")
    // this is for scenarios were the portal type has several "View"
    // (like view, jio_view, custom_view)
    // priority: app_view ; default_view ; other
    var only_view, key,
      view_list = Object.keys(views_dict).map(function (key) {
        if (views_dict[key].title === "View") { return key; }
      });
    if (view_list.includes(app_view)) {
      only_view = app_view;
    } else if (view_list.includes(default_view)) {
      only_view = default_view;
    } else {
      only_view = view_list[0];
    }
    for (key in view_list) {
      if (view_list[key] !== only_view) {
        delete views_dict[view_list[key]];
      }
    }
    return views_dict;
  }

  function formatSettingList(configuration_list_string, portal_type) {
    var i = 0, formatted_list = [], configuration_list, pair;
    try {
      configuration_list_string = configuration_list_string.replace(/\(/g, '[')
        .replace(/\)/g, ']')
        .replace(/,\]/g, ']')
        .replace(/\'/g, '"');
      configuration_list = JSON.parse(configuration_list_string);
      for (i = 0; i < configuration_list.length; i += 1) {
        pair = configuration_list[i].split(" | ");
        if (pair.length !== 2) {
          throw new SyntaxError();
        }
        if (!portal_type || pair[0] === portal_type) {
          formatted_list.push(pair);
        }
      }
    } catch (e) {
      if (e instanceof SyntaxError) {
        console.log("Error parsing configuration settings. Format error?");
        console.log("Please check site configuration 'app_allowed_sub_types'");
        console.log(e);
        formatted_list = [];
      } else {
        throw e;
      }
    }
    return formatted_list;
  }

  function buildSearchQuery(portal_type, action_reference) {
    var query_list = [];
    query_list.push(new SimpleQuery({
      key: "portal_type",
      operator: "",
      type: "simple",
      value: "Action Information"
    }));
    query_list.push(new SimpleQuery({
      key: "parent_relative_url",
      operator: "",
      type: "simple",
      value: "portal_types/" + portal_type
    }));
    if (action_reference) {
      query_list.push(new SimpleQuery({
        key: "reference",
        operator: "",
        type: "simple",
        value: action_reference
      }));
    }
    return Query.objectToSearchText(new ComplexQuery({
      operator: "AND",
      query_list: query_list,
      type: "complex"
    }));
  }

  function getFormInfo(form_definition) {
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
  }

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("getSettingList", "getSettingList")
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("getViewAndActionDict", function (portal_type, app_view,
      default_view, app_actions_string, jio_key) {
      var gadget = this,
        action_info_dict = {view_list: {}, action_list: {}},
        query = buildSearchQuery(portal_type),
        app_actions,
        app_actions_result = formatSettingList(app_actions_string, portal_type);
      app_actions = app_actions_result.map(function (pair) {
        return pair[1];
      });
      return gadget.jio_allDocs({query: query})
        .push(function (action_list) {
          var path_for_jio_get_list = [], row;
          for (row in action_list.data.rows) {
            if (action_list.data.rows.hasOwnProperty(row)) {
              path_for_jio_get_list.push(gadget.jio_get(action_list
                                                        .data.rows[row].id));
            }
          }
          return RSVP.all(path_for_jio_get_list);
        })
        .push(function (action_document_list) {
          var action_key, action_doc, action_settings;
          for (action_key in action_document_list) {
            if (action_document_list.hasOwnProperty(action_key)) {
              action_doc = action_document_list[action_key];
              if (app_actions.includes(action_doc.reference)) {
                action_settings = {
                  page: undefined,
                  jio_key: jio_key,
                  title: action_doc.title,
                  action: action_doc.reference,
                  reference: action_doc.reference,
                  action_type: action_doc.action_type,
                  parent_portal_type: portal_type
                };
                if (view_categorie_list.includes(action_settings.action_type)) {
                  action_settings.page = "ojs_local_controller";
                  action_info_dict.view_list[action_settings.action] =
                    action_settings;
                } else {
                  action_settings.page = "handle_action";
                  action_info_dict.action_list[action_settings.action] =
                    action_settings;
                }
              }
            }
          }
          action_info_dict.view_list =
            filterViewList(action_info_dict.view_list, app_view, default_view);
          return action_info_dict;
        });
    })

    .declareMethod("getDialogFormDefinition", function (form_name, category) {
      var gadget = this,
        form_definition,
        form_info;
      return gadget.getSetting('portal_skin_folder')
        .push(function (portal_skin_folder) {
          return gadget.jio_get("portal_skins/" + portal_skin_folder + "/" +
                                form_name);
        })
        .push(function (form_result) {
          form_definition = form_result.raw_dict._embedded._view
            ._embedded.form_definition;
          form_definition.fields_raw_properties = form_result.raw_dict._embedded
            ._view.my_fields_raw_properties["default"];
          form_definition._actions = form_result.raw_dict._embedded
            ._view._actions;
          form_definition.group_list = form_result.raw_dict.group_list;
          form_definition.title = form_result.raw_dict.title;
          form_definition.portal_type_dict = {};
          form_definition.action_type = category;
          form_info = getFormInfo(form_definition);
          form_definition.form_type = form_info[0];
          form_definition.child_gadget_url = form_info[1];
          return form_definition;
        });
    })

    .declareMethod("getFormDefinition", function (portal_type,
                                                  action_reference) {
      var gadget = this,
        query = buildSearchQuery(portal_type, action_reference),
        portal_type_dict_setting = portal_type.replace(/ /g, '_')
                                    .toLowerCase() + "_dict",
        portal_type_dict = {},
        action_type,
        action_title,
        form_definition,
        portal_skin_folder,
        app_allowed_sub_types,
        app_view,
        default_view,
        app_actions_string,
        form_info,
        error;
      return gadget.getSettingList([portal_type_dict_setting,
                                    'portal_skin_folder',
                                    'app_allowed_sub_types',
                                    'app_view_reference',
                                    'default_view_reference',
                                    'app_actions'])
        .push(function (result_list) {
          app_allowed_sub_types = result_list[2];
          app_view = result_list[3];
          default_view = result_list[4];
          app_actions_string = result_list[5];
          if (!result_list[1]) {
            throw new Error("Missing site configuration 'portal_skin_folder'");
          }
          portal_skin_folder = "portal_skins/" + result_list[1];
          if (result_list[0]) {
            try {
              portal_type_dict = window.JSON.parse(result_list[0]);
            } catch (e) {
              if (e instanceof SyntaxError) {
                throw new Error("Bad JSON dict in configuration setting '" +
                                portal_type_dict_setting + "'");
              }
              throw e;
            }
          }
          return gadget.jio_allDocs({query: query});
        })
        .push(function (data) {
          if (data.data.rows.length === 0) {
            error = new Error("Can not find action '" + action_reference +
                              "' for portal type '" + portal_type + "'");
            error.status_code = 400;
            throw error;
          }
          return gadget.jio_get(data.data.rows[0].id);
        })
        .push(function (action_result) {
          action_title = action_result.title;
          action_type = action_result.action_type;
          if (action_result.action.includes("string:${object_url}")) {
            action_result.action = action_result.action
              .replace("string:${object_url}", portal_skin_folder);
          }
          return gadget.jio_get(action_result.action);
        })
        .push(function (form_result) {
          form_definition = form_result.raw_dict._embedded._view
            ._embedded.form_definition;
          form_definition.fields_raw_properties = form_result.raw_dict
            ._embedded._view.my_fields_raw_properties["default"];
          form_definition._actions = form_result.raw_dict._embedded
            ._view._actions;
          //[PATCH] if custom action and anonymous
          // get _actions field from fields_raw_properties
          if (form_definition.fields_raw_properties
              .hasOwnProperty("_actions")) {
            if (!form_definition._actions &&
                action_type === "object_jio_js_script") {
              form_definition._actions = form_definition
                .fields_raw_properties._actions;
            }
            delete form_definition.fields_raw_properties._actions;
          }
          form_definition.group_list = form_result.raw_dict.group_list;
          form_definition.action_type = action_type;
          form_info = getFormInfo(form_definition);
          form_definition.form_type = form_info[0];
          form_definition.child_gadget_url = form_info[1];
          form_definition.title = action_title;
          form_definition.portal_type_dict = portal_type_dict;
          return formatSettingList(app_allowed_sub_types, portal_type);
        })
        .push(function (allowed_sub_types_pairs) {
          var allowed_sub_types = allowed_sub_types_pairs.map(function (pair) {
              return pair[1];
            });
          form_definition.allowed_sub_types_list = allowed_sub_types;
          form_definition.new_content_dialog_form = portal_type_dict
            .new_content_dialog_form;
          form_definition.new_content_category = portal_type_dict
            .new_content_category;
          return gadget.getViewAndActionDict(portal_type, app_view,
                                             default_view, app_actions_string);
        })
        .push(function (action_view_dict) {
          form_definition.portal_type_dict.has_more_views =
            Object.keys(action_view_dict.view_list).length > 1;
          form_definition.portal_type_dict.has_more_actions =
            Object.keys(action_view_dict.action_list).length > 0;
          return form_definition;
        });
    });

}(window, rJS, RSVP, Query, SimpleQuery, ComplexQuery, console));
