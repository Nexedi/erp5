/*global window, rJS, RSVP, Handlebars, UriTemplate, calculatePageTitle, ensureArray */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, Handlebars, UriTemplate, calculatePageTitle, ensureArray) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // Handlebars
  /////////////////////////////////////////////////////////////////
  // Precompile the templates while loading the first gadget instance
  var gadget_klass = rJS(window),
    table_template = Handlebars.compile(gadget_klass.__template_element
                         .getElementById("table-template")
                         .innerHTML);

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

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function (options) {
      var gadget = this,
        action_info_list = [],
        erp5_document,
        document_title;
      return gadget.jio_get(options.jio_key)
        .push(function (document) {
          var parent = "portal_types/" + document.portal_type,
            query = 'portal_type: "Action Information" AND parent_relative_url: "' + parent + '"';
          document_title = document.title;
          return gadget.jio_allDocs({query: query});
        })
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
          var url_for_parameter_list = [], i = 0,
              page, action_key, action_doc;
          for (action_key in action_document_list) {
            page = "handle_action";
            action_doc = action_document_list[action_key];
            if (action_doc.reference == "view" || action_doc.reference == "jio_view") {
              page = "ojs_controller";
            }
            url_for_parameter_list.push({command: 'change', options: {page: page, action: action_doc.reference}});
            action_info_list[i] = { reference: action_doc.reference, title: action_doc.title};
            i += 1;
          }
          return gadget.getUrlForList(url_for_parameter_list);
        })
        .push(function (url_list) {
          var action_list = [], view_list = [], url, i, element;
          for (i = 0; i < url_list.length; i += 1) {
            element = { href: url_list[i],
              icon: null,
              name: action_info_list[i].reference,
              title: action_info_list[i].title };
            // TODO: maybe both view and jio_view should be ignored here
            if (element.name != "view") {
              if (element.name == "jio_view") {
                view_list.push(element);
              } else {
                action_list.push(element);
              }
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

}(window, rJS, RSVP, Handlebars, UriTemplate, calculatePageTitle, ensureArray));