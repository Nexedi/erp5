/*global window, rJS, RSVP, domsugar, URI, calculatePageTitle, ensureArray */
/*jslint nomen: true, indent: 2, maxerr: 3 */

/** Page for displaying Views, Jump and BreadCrumb navigation for a document.
*/

(function (window, rJS, RSVP, domsugar, URI, calculatePageTitle, ensureArray) {
  "use strict";

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

  function generateSection(title, icon, view_list) {
    var i,
      dom_list = [];

    for (i = 0; i < view_list.length; i += 1) {
      dom_list.push(domsugar('li', [domsugar('a', {
        href: view_list[i].link,
        text: view_list[i].title
      })]));
    }

    return domsugar(null, [
      domsugar('section', {class: 'ui-content-header-plain'}, [
        domsugar('h3', [
          domsugar('span', {class: 'ui-icon ui-icon-' + icon, html: '&nbsp;'}),
          title
        ])
      ]),
      domsugar('ul', {class: 'document-listview'}, dom_list)
    ]);

  }

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("getUrlForList", "getUrlForList")
    .declareAcquiredMethod("getTranslationList", "getTranslationList")
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
        view_list = [],
        tab_list = [],
        jump_action_list = [],
        breadcrumb_action_list = [],
        erp5_document,
        jump_list;

      return gadget.jio_getAttachment(gadget.state.jio_key, "links")

        .push(function (result) {
          var i,
            url_for_kw_list = [];
          erp5_document = result;
          view_list = ensureArray(erp5_document._links.view);
          jump_list = ensureArray(erp5_document._links.action_object_jio_jump);

          for (i = 0; i < view_list.length; i += 1) {
            url_for_kw_list.push({command: 'display_with_history', options: {
              jio_key: gadget.state.jio_key,
              view: view_list[i].href,
              page: undefined  // Views in ERP5 must be forms but because of
                               // OfficeJS we keep it empty for different default
            }});
          }
          for (i = 0; i < jump_list.length; i += 1) {
            url_for_kw_list.push({command: 'display_dialog_with_history', options: {
              jio_key: gadget.state.jio_key,
              view: jump_list[i].href
            }});
          }

          url_for_kw_list.push({command: 'cancel_dialog_with_history'});

          return RSVP.hash({
            url_list: gadget.getUrlForList(url_for_kw_list),
            _: modifyBreadcrumbList(gadget,
                                    erp5_document._links.parent || "#",
                                    breadcrumb_action_list),
            translation_list: gadget.getTranslationList(['Views', 'Jumps', 'Breadcrumb']),
            page_title: calculatePageTitle(gadget, erp5_document)
          });
        })

        .push(function (result_dict) {
          var i,
            j = 0;

          for (i = 0; i < view_list.length; i += 1) {
            tab_list.push({
              title: view_list[i].title,
              link: result_dict.url_list[j]
            });
            j += 1;
          }
          for (i = 0; i < jump_list.length; i += 1) {
            jump_action_list.push({
              title: jump_list[i].title,
              link: result_dict.url_list[j]
            });
            j += 1;
          }

          domsugar(gadget.element, [
            generateSection(result_dict.translation_list[0], 'eye', tab_list),
            generateSection(result_dict.translation_list[1], 'plane', jump_action_list),
            generateSection(result_dict.translation_list[2], 'ellipsis-v', breadcrumb_action_list)
          ]);

          return gadget.updateHeader({
            back_url: result_dict.url_list[j],
            page_title: result_dict.page_title
          });
        });
    })
    .declareMethod("triggerSubmit", function () {
      return;
    });

}(window, rJS, RSVP, domsugar, URI, calculatePageTitle, ensureArray));