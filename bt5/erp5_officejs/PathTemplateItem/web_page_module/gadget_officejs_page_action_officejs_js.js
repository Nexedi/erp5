/*global window, rJS, RSVP, Handlebars */
/*jslint nomen: true, indent: 2, maxerr: 10, maxlen: 80 */
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

  function getHTMLElementList(gadget, element_list) {
    var i = 0,
      element_info_list = [],
      url_for_parameter_list = [],
      element_info,
      key;
    for (key in element_list) {
      if (element_list.hasOwnProperty(key)) {
        element_info = element_list[key];
        url_for_parameter_list.push({ command: 'change',
                                      options: element_info });
        element_info_list[i] = { reference: element_info.reference,
                                 title: element_info.title};
        i += 1;
      }
    }
    return gadget.getUrlForList(url_for_parameter_list)
      .push(function (url_list) {
        var html_element_list = [], j, element;
        for (j = 0; j < url_list.length; j += 1) {
          element = { href: url_list[j],
            icon: null,
            name: element_info_list[j].reference,
            title: element_info_list[j].title };
          html_element_list.push(element);
        }
        return html_element_list;
      });
  }

  gadget_klass
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("getUrlForList", "getUrlForList")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getSettingList", "getSettingList")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("render", function (options) {
      var gadget = this,
        portal_type,
        document_title,
        gadget_utils;
      return gadget.jio_get(options.jio_key)
        .push(function (document) {
          document_title = document.title;
          return document.portal_type;
        }, function () {
          document_title = options.portal_type;
          return options.portal_type;
        })
        .push(function (result) {
          portal_type = result;
          return gadget.declareGadget("gadget_officejs_common_util.html");
        })
        .push(function (result) {
          gadget_utils = result;
          return gadget.getSettingList(['app_view_reference',
                                        'default_view_reference',
                                        'app_actions']);
        })
        .push(function (setting_list) {
          // TODO views are also listed here
          // should views be handled in another gadget like "..tab_office.js" ?
          return gadget_utils.getViewAndActionDict(portal_type, setting_list[0],
            setting_list[1], setting_list[2], options.jio_key);
        })
        .push(function (action_info_dict) {
          return RSVP.all([
            getHTMLElementList(gadget, action_info_dict.view_list),
            getHTMLElementList(gadget, action_info_dict.action_list)
          ]);
        })
        .push(function (all_html_elements) {
          return RSVP.all([
            renderLinkList(gadget, "Views", "eye", all_html_elements[0]),
            renderLinkList(gadget, "Actions", "gear", all_html_elements[1])
          ]);
        })
        .push(function (translated_html_link_list) {
          gadget.element.innerHTML = translated_html_link_list.join("\n");
          return gadget.getUrlFor({command: 'change',
                                   options: {page: undefined}});
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