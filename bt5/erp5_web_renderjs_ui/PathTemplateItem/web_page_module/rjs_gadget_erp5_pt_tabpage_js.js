/*global window, rJS, RSVP, Handlebars, URI, calculatePageTitle, ensureArray */
/*jslint nomen: true, indent: 2, maxerr: 3 */

/** Page for displaying Views, Jump and BreadCrumb navigation for a document.
*/

(function (window, rJS, RSVP, Handlebars, URI, calculatePageTitle, ensureArray) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // Handlebars
  /////////////////////////////////////////////////////////////////
  // Precompile the templates while loading the first gadget instance
  var gadget_klass = rJS(window),
    table_template = Handlebars.compile(gadget_klass.__template_element
                         .getElementById("table-template")
                         .innerHTML);

  /** Go recursively up the parent-chain and insert breadcrumbs in the last argument.
   */
  function modifyBreadcrumbList(gadget, parent_link, breadcrumb_action_list) {
    if (parent_link === undefined) {
      return;
    }
    var uri = new URI(parent_link.href),
      jio_key = uri.segment(2);

    if ((uri.protocol() !== 'urn') || (uri.segment(0) !== 'jio') || (uri.segment(1) !== "get")) {
      // Parent is the ERP5 site thus recursive calling ends here
      breadcrumb_action_list.unshift({
        title: "ERP5",
        link: "#"
      });
      return;
    }

    // Parent is an ERP5 document
    return gadget.getUrlFor({command: 'display_stored_state', options: {jio_key: jio_key}})
      .push(function (parent_href) {
        breadcrumb_action_list.unshift({
          title: parent_link.name,
          link: parent_href
        });
        return gadget.jio_getAttachment(jio_key, "links");
      })
      .push(function (result) {
        return modifyBreadcrumbList(gadget, result._links.parent || "#", breadcrumb_action_list);
      });
  }

  gadget_klass
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("updateHeader", "updateHeader")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    /** Render only transforms its arguments and passes them to mutex-protected onStateChange

    options:
      jio_key: {string} currently viewed document (e.g. foo/1)
      page: {string} selected page (always "tab" for page_tab)
      view: {string} always "view"
      selection, history, selection_index
    */
    .declareMethod("render", function (options) {
      return this.changeState({
        jio_key: options.jio_key,
        editable: options.editable
      });
    })

    .onStateChange(function () {
      var gadget = this,
        breadcrumb_action_list = [],
        erp5_document;

      return gadget.jio_getAttachment(gadget.state.jio_key, "links")
        .push(function (result) {
          erp5_document = result;

          var i,
            tab_promise_list = [],
            jump_action_promise_list = [],
            view_list = ensureArray(erp5_document._links.view)
              .concat(ensureArray(erp5_document._links.action_object_jio_view)),
            jump_list = ensureArray(erp5_document._links.action_object_jump);

          for (i = 0; i < view_list.length; i += 1) {
            tab_promise_list.push(RSVP.hash({
              title: view_list[i].title,
              i18n: view_list[i].title,
              link: gadget.getUrlFor({command: 'display_with_history', options: {
                jio_key: gadget.state.jio_key,
                view: view_list[i].href,
                page: undefined  // Views in ERP5 must be forms but because of
                                 // OfficeJS we keep it empty for different default
              }})
            }));
          }

          for (i = 0; i < jump_list.length; i += 1) {
            jump_action_promise_list.push(RSVP.hash({
              title: jump_list[i].title,
              i18n: jump_list[i].title,
              link: gadget.getUrlFor({command: 'push_history', options: {
                extended_search: new URI(jump_list[i].href).query(true).query,
                page: 'search'
              }})
            }));
          }

          return RSVP.hash({
            tab_list: RSVP.all(tab_promise_list),
            jump_action_list: RSVP.all(jump_action_promise_list),
            _: modifyBreadcrumbList(gadget,
                                    erp5_document._links.parent || "#",
                                    breadcrumb_action_list)
          });
        })
        .push(function (result_dict) {

          return gadget.translateHtml(table_template({
            definition_title: "Views",
            definition_i18n: "Views",
            definition_icon: "eye",
            documentlist: result_dict.tab_list
          }) + table_template({
            definition_title: "Jumps",
            documentlist: result_dict.jump_action_list,
            definition_icon: "plane",
            definition_i18n: "Jumps"
          }) + table_template({
            definition_title: "Breadcrumb",
            documentlist: breadcrumb_action_list,
            definition_icon: "ellipsis-v",
            definition_i18n: "Breadcrumb"
          }));
        })
        .push(function (my_translated_html) {
          gadget.element.innerHTML = my_translated_html;

          return RSVP.hash({
            back_url: gadget.getUrlFor({command: 'cancel_dialog_with_history'}),
            page_title: calculatePageTitle(gadget, erp5_document)
          });
        })
        .push(gadget.updateHeader.bind(gadget));
    })
    .declareMethod("triggerSubmit", function () {
      return;
    });

}(window, rJS, RSVP, Handlebars, URI, calculatePageTitle, ensureArray));