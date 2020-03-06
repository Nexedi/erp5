/*global window, rJS, RSVP, domsugar, calculatePageTitle, ensureArray */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, domsugar, calculatePageTitle, ensureArray) {
  "use strict";

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
        editable: options.editable,
        view: options.view
      });
    })

    .onStateChange(function () {
      var gadget = this,
        erp5_document,
        group_list;

      // Get the whole view as attachment because actions can change based on
      // what view we are at. If no view available than fallback to "links".
      return gadget.jio_getAttachment(gadget.state.jio_key, gadget.state.view || "links")
        .push(function (jio_attachment) {
          erp5_document = jio_attachment;

          var i,
            j,
            url_for_kw_list = [];

          group_list = [
            // Action list, icon
            ensureArray(erp5_document._links.action_object_jio_exchange), "exchange",
            ensureArray(erp5_document._links.action_object_jio_report), "bar-chart-o",
            ensureArray(erp5_document._links.action_object_jio_print), "print"
          ];

          for (i = 0; i < group_list.length; i += 2) {
            for (j = 0; j < group_list[i].length; j += 1) {
              url_for_kw_list.push({command: 'display_with_history_and_cancel', options: {
                jio_key: gadget.state.jio_key,
                view: group_list[i][j].href
              }});
            }
          }

          url_for_kw_list.push({command: 'cancel_dialog_with_history'});

          return RSVP.hash({
            url_list: gadget.getUrlForList(url_for_kw_list),
            translation_list: gadget.getTranslationList(['Export', 'Reports', 'Print']),
            page_title: calculatePageTitle(gadget, erp5_document)
          });
        })

        .push(function (result_dict) {
          var i,
            j,
            k = 0,
            dom_list = [],
            link_list;

          for (i = 0; i < group_list.length; i += 2) {
            link_list = [];
            for (j = 0; j < group_list[i].length; j += 1) {
              link_list.push({
                title: group_list[i][j].title,
                link: result_dict.url_list[k]
              });
              k += 1;
            }
            dom_list.push(
              generateSection(result_dict.translation_list[i / 2], group_list[i + 1], link_list)
            );

          }

          domsugar(gadget.element, dom_list);

          return gadget.updateHeader({
            back_url: result_dict.url_list[result_dict.url_list.length - 1],
            page_title: result_dict.page_title
          });
        });
    })
    .declareMethod("triggerSubmit", function () {
      return;
    });

}(window, rJS, RSVP, domsugar, calculatePageTitle, ensureArray));