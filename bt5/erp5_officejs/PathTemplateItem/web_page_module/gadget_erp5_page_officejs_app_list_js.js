/*global window, rJS, RSVP, domsugar, URL */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, domsugar, URL) {
  "use strict";

  function getWebSiteModuleUrl() {
    // Derive the web_site_module base URL from the current page URL.
    // Current page is at e.g. /erp5/web_site_module/renderjs_runner/app/...
    // We navigate up to web_site_module/ to build sibling app URLs.
    var base = window.location.href.split('#')[0],
      url = new URL(base),
      parts = url.pathname.split('/'),
      wsm_index = parts.indexOf('web_site_module'),
      wsm_path;
    if (wsm_index !== -1) {
      wsm_path = parts.slice(0, wsm_index + 1).join('/') + '/';
      return url.origin + wsm_path;
    }
    // Fallback: go up one level from current site
    return new URL('../', base).href;
  }

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getTranslationList", "getTranslationList")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('triggerSubmit', function () {
      return;
    })

    .declareMethod('render', function () {
      var gadget = this;

      return gadget.jio_allDocs({
        query: 'portal_type: "Web Site"',
        select_list: ['title', 'id', 'relative_url'],
        limit: 200
      })
        .push(function (result) {
          var i,
            row,
            app_list = [],
            len = result.data.total_rows;

          for (i = 0; i < len; i += 1) {
            row = result.data.rows[i];
            // Filter for OfficeJS apps by convention:
            // Web Site IDs starting with "officejs_"
            if (row.value.id &&
                row.value.id.indexOf('officejs_') === 0) {
              app_list.push({
                title: row.value.title || row.value.id,
                id: row.value.id
              });
            }
          }

          // Sort alphabetically by title
          app_list.sort(function (a, b) {
            return a.title.localeCompare(b.title);
          });

          return RSVP.all([
            app_list,
            gadget.getTranslationList([
              'OfficeJS Applications',
              'No OfficeJS applications found.'
            ])
          ]);
        })
        .push(function (result_list) {
          var app_list = result_list[0],
            translation_list = result_list[1],
            dom_list = [],
            i,
            base_url = getWebSiteModuleUrl();

          if (app_list.length === 0) {
            domsugar(
              gadget.element.querySelector('.document_list'),
              [domsugar('p', {text: translation_list[1]})]
            );
          } else {
            for (i = 0; i < app_list.length; i += 1) {
              dom_list.push(domsugar('li', [
                domsugar('a', {
                  href: base_url + app_list[i].id + '/',
                  text: app_list[i].title,
                  target: '_blank',
                  rel: 'noopener'
                })
              ]));
            }
            domsugar(
              gadget.element.querySelector('.document_list'),
              [domsugar('ul', {'class': 'document-listview'},
                        dom_list)]
            );
          }

          return gadget.updateHeader({
            page_title: translation_list[0],
            page_icon: 'th'
          });
        });
    });

}(window, rJS, RSVP, domsugar, URL));
