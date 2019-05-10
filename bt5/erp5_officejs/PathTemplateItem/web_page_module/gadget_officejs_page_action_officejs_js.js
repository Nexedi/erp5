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

    .declareMethod("getHTMLElements", function (element_list) {
      var gadget = this,
        i = 0,
        element_info_list = [],
        url_for_parameter_list = [],
        element_info;
      for (var key in element_list) {
        if (element_list.hasOwnProperty(key)) {
          element_info = element_list[key];
          url_for_parameter_list.push({ command: 'change', options: element_info });
          element_info_list[i] = { reference: element_info.reference, title: element_info.title};
          i += 1;
        }
      }
      return gadget.getUrlForList(url_for_parameter_list)
        .push(function (url_list) {
          var html_element_list = [], i, element;
          for (i = 0; i < url_list.length; i += 1) {
            element = { href: url_list[i],
              icon: null,
              name: element_info_list[i].reference,
              title: element_info_list[i].title };
            html_element_list.push(element);
          }
          return html_element_list;
        });
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
          var action_settings_list = [], page, action_key, action_doc;
          for (action_key in action_document_list) {
            if (action_document_list.hasOwnProperty(action_key)) {
              action_doc = action_document_list[action_key];
              page = "handle_action";
              if (view_categories.includes(action_doc.action_type)) {
                page = "ojs_controller";
              }
              action_settings_list.push({
                page: page,
                title: action_doc.title,
                action: action_doc.reference,
                reference: action_doc.reference,
                action_type: action_doc.action_type,
                parent_portal_type: portal_type
              });
            }
          }
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
          //is the 'classic view' action needed at all here? -maybe don't add it in appcache manifest
          if (action_info_dict.views.hasOwnProperty("view") && action_info_dict.views.hasOwnProperty("jio_view")) {
            delete action_info_dict.views.view;
          }
          return action_info_dict;
        });
    })

    .declareMethod("render", function (options) {
      var gadget = this,
        document_title;
      return gadget.jio_get(options.jio_key)
        .push(function (document) {
          document_title = document.title;
          return document.portal_type;
        }, function (error) {
          document_title = options.portal_type;
          return options.portal_type;
        })
        .push(function (portal_type) {
          return gadget.getAllActions(portal_type, view_categories[0]);
        })
        .push(function (action_info_dict) {
          return RSVP.all([
            gadget.getHTMLElements(action_info_dict.views),
            gadget.getHTMLElements(action_info_dict.actions)
          ]);
        })
          // TODO: check other lists like clone or delete?
        .push(function (all_html_elements) {
          return RSVP.all([
            renderLinkList(gadget, "Views", "eye", all_html_elements[0]),
            renderLinkList(gadget, "Actions", "gear", all_html_elements[1])
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