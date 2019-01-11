/*global window, rJS, RSVP, Handlebars, calculatePageTitle, ensureArray */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, Handlebars, calculatePageTitle, ensureArray) {
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
  function renderLinkList(gadget, jio_key, title, icon, erp5_link_list) {
    return new RSVP.Queue()
      .push(function () {
        return RSVP.all(
          erp5_link_list.map(function (erp5_link) {
            return gadget.getUrlFor({
              "command": 'display_with_history_and_cancel',
              "options": {
                "jio_key": jio_key,
                "view": erp5_link.href
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
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function (options) {
      var gadget = this,
        erp5_document;

      // Get the whole view as attachment because actions can change based on
      // what view we are at. If no view available than fallback to "links".
      return gadget.jio_getAttachment(options.jio_key, options.view || "links")
        .push(function (jio_attachment) {
          var transition_list = ensureArray(jio_attachment._links.action_workflow),
            action_list = ensureArray(jio_attachment._links.action_object_jio_action)
              .concat(ensureArray(jio_attachment._links.action_object_jio_button))
              .concat(ensureArray(jio_attachment._links.action_object_jio_fast_input)),
            clone_list = ensureArray(jio_attachment._links.action_object_clone_action);

          erp5_document = jio_attachment;

          return RSVP.all([
            renderLinkList(gadget, options.jio_key, "Workflows", "random", transition_list),
            renderLinkList(gadget, options.jio_key, "Actions", "gear", action_list),
            renderLinkList(gadget, options.jio_key, "Clone", "clone", clone_list)
          ]);
        })
        .push(function (translated_html_link_list) {
          gadget.element.innerHTML = translated_html_link_list.join("\n");
          return RSVP.all([
            calculatePageTitle(gadget, erp5_document),
            gadget.getUrlFor({command: 'cancel_dialog_with_history'})
          ]);
        })
        .push(function (result_list) {
          return gadget.updateHeader({
            page_title: result_list[0],
            back_url: result_list[1]
          });
        });
    })
    .declareMethod("triggerSubmit", function () {
      return;
    });

}(window, rJS, RSVP, Handlebars, calculatePageTitle, ensureArray));