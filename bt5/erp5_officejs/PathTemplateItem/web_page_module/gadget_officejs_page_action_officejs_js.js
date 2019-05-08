/*global window, rJS, RSVP, Handlebars */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, Handlebars) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // Handlebars
  /////////////////////////////////////////////////////////////////
  // Precompile the templates while loading the first gadget instance
  var gadget_klass = rJS(window),
    table_template = Handlebars.compile(gadget_klass.__template_element
                         .getElementById("table-template")
                         .innerHTML),
    // TODO: check if there are other categories that are 'views' and find a less hardcoded way to get this
    view_categories = ["object_view", "object_jio_view", "object_web_view", "object_list"];

  /** Render translated HTML of title + links
   *
   * @param {string} title - H3 title of the section with the links
   * @param {string} icon - alias used in font-awesome iconset
   * @param {Array} command_list - array of links obtained from ERP5 HATEOAS
   */
  function renderLinkList(gadget, title, icon, erp5_link_list) {
    // prepare links for template (replace @href for RJS link)
    return gadget.translateHtml(
      table_template({
        "definition_i18n": title,
        "definition_title": title,
        "definition_icon": icon,
        "document_list": erp5_link_list.map(function (erp5_link, index) {
          return {
            "title": erp5_link.title,
            "i18n": erp5_link.title,
            "link": erp5_link_list[index].href
          };
        })
      })
    );
  }

  gadget_klass
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("getUrlForList", "getUrlForList")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getSetting", "getSetting")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("getActionSettings", function (action_doc, portal_type) {
      var gadget = this, page = "handle_action", action_settings = {};
      if (view_categories.includes(action_doc.action_type)) {
        page = "ojs_controller";
      }
      action_settings = {
        page: page,
        title: action_doc.title,
        action: action_doc.reference,
        reference: action_doc.reference,
        action_type: action_doc.action_type,
        parent_portal_type: portal_type,
        portal_type: portal_type
      };
      //TODO find a better way to handle "add" actions (how to get child portal type?)
      if (action_doc.reference === "new") {
        return gadget.getSetting('portal_type')
        .push(function (child_portal_type) {
          action_settings.portal_type = child_portal_type;
          return action_settings;
        });
      }
      return action_settings;
    })

    .declareMethod("getAllActions", function (portal_type, action_category) {
      var gadget = this,
        action_info_dict = {views: {}, actions: {}},
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
              get_action_settings_list.push(gadget.getActionSettings(action_document_list[action_key], portal_type));
            }
          }
          return RSVP.all(get_action_settings_list);
        })
        .push(function (action_settings_list) {
          for (var key in action_settings_list) {
            if (action_settings_list.hasOwnProperty(key)) {
              var action_settings = action_settings_list[key];
              if (view_categories.includes(action_settings.action_type)) {
                action_info_dict.views[action_settings.action] = action_settings;
              } else {
                action_info_dict.actions[action_settings.action] = action_settings;
              }
            }
          }
          //if portal_type has both view and jio_view, remove classic 'view'
          //TODO use action type instead of reference
          if (action_info_dict.views.hasOwnProperty("view") && action_info_dict.views.hasOwnProperty("jio_view")) {
            delete action_info_dict.views.view;
          }
          return action_info_dict;
        });
    })

    .declareMethod("render", function (options) {
      var gadget = this,
        url_for_parameter_list = [],
        action_info_list = [],
        action_info_dict = {},
        document_title;
      return gadget.jio_get(options.jio_key)
        .push(function (document) {
          document_title = document.title;
          return gadget.getAllActions(document.portal_type, view_categories[0]);
        }, function (error) {
          document_title = options.portal_type;
          return gadget.getAllActions(options.portal_type, view_categories[0]);
        })
        .push(function (all_actions) {
          var action_info, i = 0;
          action_info_dict = all_actions;
          //TODO refactor this (actions and views)
          for (var action_key in action_info_dict.actions) {
            if (action_info_dict.actions.hasOwnProperty(action_key)) {
              action_info = action_info_dict.actions[action_key];
              url_for_parameter_list.push({ command: 'change', options: action_info });
              action_info_list[i] = { reference: action_info.reference, title: action_info.title};
              i += 1;
            }
          }
          for (var view_key in action_info_dict.views) {
            if (action_info_dict.views.hasOwnProperty(view_key)) {
              action_info = action_info_dict.views[view_key];
              url_for_parameter_list.push({ command: 'change', options: action_info });
              action_info_list[i] = { reference: action_info.reference, title: action_info.title};
              i += 1;
            }
          }
          return gadget.getUrlForList(url_for_parameter_list);
        })
        .push(function (url_list) {
          var action_list = [], view_list = [], i, element;
          for (i = 0; i < url_list.length; i += 1) {
            element = { href: url_list[i],
              icon: null,
              name: action_info_list[i].reference,
              title: action_info_list[i].title };
            if (action_info_dict.views.hasOwnProperty(element.name)) {
              view_list.push(element);
            } else {
              action_list.push(element);
            }
          }
          // TODO: check other lists like clone or delete?
          return RSVP.all([
            renderLinkList(gadget, "Views", "eye", view_list),
            renderLinkList(gadget, "Actions", "gear", action_list)
          ]);
        })
        .push(function (translated_html_link_list) {
          gadget.element.innerHTML = translated_html_link_list.join("\n");
          return gadget.getUrlFor({command: 'change', options: {page: undefined}});
        })
        .push(function (back_url) {
          return gadget.updateHeader({
            page_title: document_title,
            back_url: back_url
          });
        });
    })

    .declareMethod("triggerSubmit", function () {
      return;
    });

}(window, rJS, RSVP, Handlebars));