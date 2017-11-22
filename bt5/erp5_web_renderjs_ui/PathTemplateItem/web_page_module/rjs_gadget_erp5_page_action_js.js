/*global window, rJS, RSVP, Handlebars, calculatePageTitle */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, Handlebars, calculatePageTitle) {
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
    return new RSVP.Queue()
      .push(function () {
        // obtain RJS links from ERP5 links
        return RSVP.all(
          erp5_link_list.map(function (erp5_link) {
            return gadget.getUrlFor({
              "command": 'change',
              "options": {
                "view": erp5_link.href,
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

  function asArray(obj) {
    if (!obj) {return []; }
    if (Array.isArray(obj)) {return obj; }
    return [obj];
  }

  gadget_klass
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("updateHeader", "updateHeader")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function (options) {
      var gadget = this,
        erp5_document,
        transition_list,
        action_list;

      return gadget.jio_getAttachment(options.jio_key, "links")
        .push(function (result) {
          erp5_document = result;
          action_list = asArray(erp5_document._links.action_workflow);
          transition_list = asArray(erp5_document._links.action_object_jio_action)
                        .concat(asArray(erp5_document._links.action_object_clone_action));

          return RSVP.all([
            renderLinkList(gadget, "Actions", "gear", action_list),
            renderLinkList(gadget, "Workflow-Transitions", "random", transition_list)
          ]);
        })
        .push(function (translated_html_link_list) {
          gadget.element.innerHTML = translated_html_link_list.join("\n");
          return RSVP.all([
            calculatePageTitle(gadget, erp5_document),
            gadget.getUrlFor({command: 'change', options: {page: undefined}})
          ]);
        })
        .push(function (result_list) {
          return gadget.updateHeader({
            page_title: result_list[0],
            back_url: result_list[1]
          });
        });
    });

}(window, rJS, RSVP, Handlebars, calculatePageTitle));