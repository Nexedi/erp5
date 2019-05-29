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
                         .innerHTML);

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

    .declareMethod("getHTMLElementList", function (portal_type_list, jio_key, parent_portal_type) {
      var gadget = this,
        i = 0,
        portal_type_info_list = [],
        portal_type,
        url_for_parameter_list = [],
        x;
      for (x = 0; x < portal_type_list.length; x += 1) {
        portal_type = portal_type_list[x];
        url_for_parameter_list.push({ command: 'change', options: {page: "add_element", jio_key: jio_key, portal_type: portal_type, parent_portal_type: parent_portal_type} });
        portal_type_info_list[i] = { reference: portal_type, title: portal_type};
        i += 1;
      }
      return gadget.getUrlForList(url_for_parameter_list)
        .push(function (url_list) {
          var html_element_list = [], j, element;
          for (j = 0; j < url_list.length; j += 1) {
            element = { href: url_list[j],
              icon: null,
              name: portal_type_info_list[j].reference,
              title: portal_type_info_list[j].title };
            html_element_list.push(element);
          }
          return html_element_list;
        });
    })

    .declareMethod("render", function (options) {
      var gadget = this,
        allowed_sub_types_list = options.allowed_sub_types_list.split(","),
        document_title;
      return gadget.jio_get(options.jio_key)
        .push(function (document) {
          document_title = document.title;
          return document.portal_type;
        }, function () {
          document_title = options.portal_type;
          return options.portal_type;
        })
        // TODO: this gadget must load the form dialog to select the type of document
        // somehow (a generic action?) get the path string:${object_url}/Base_viewNewContentDialog
        // get corresponding form definition (only contains a select field)
        // fill select field with allowed_sub_types_list
        .push(function (portal_type) {
          return gadget.getHTMLElementList(allowed_sub_types_list, options.jio_key, portal_type);
        })
        .push(function (all_html_elements) {
          return RSVP.all([
            renderLinkList(gadget, "Create Document", "file", all_html_elements)
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