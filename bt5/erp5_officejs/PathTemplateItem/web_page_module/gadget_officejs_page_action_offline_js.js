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
    return gadget.getUrlParameter("extended_search")
      .push(function (query) {
        // obtain RJS links from ERP5 links
        return RSVP.all(
          erp5_link_list.map(function (erp5_link) {
            return gadget.getUrlFor({
              "command": 'change',
              "options": {
                "view": UriTemplate.parse(erp5_link.href).expand({query: query}),
                "page": undefined
              }
            });
          })
        );
      })
      .push(function (url_list) {
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
                "link": url_list[index]
              };
            })
          })
        );
      });
  }


  gadget_klass
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function (options) {
      var gadget = this,
        erp5_document,
        document_title;
      return gadget.jio_get(options.jio_key)
        .push(function (document) {
          var parent = "portal_types/" + document.portal_type,
            query = 'portal_type: "Action Information" AND parent_relative_url: "' + parent + '"';
          document_title = document.title;
          return gadget.jio_allDocs({query: query});
        })
        //TODO: build all action urls with corresponding action reference (ignore view, jio_view, etc)
        .push(function (action_list) {
          return gadget.getUrlFor({command: 'change', options: {page: "ojs_controller", action: "reply"}});
        })
        .push(function (url) {

          //TODO temporarily hardcoded
          var action_list = [{ href: url,
          icon: null,
          name: "reply",
          title: "Reply" }];

          return RSVP.all([
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