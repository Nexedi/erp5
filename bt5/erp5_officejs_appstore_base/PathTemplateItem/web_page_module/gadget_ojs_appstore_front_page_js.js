/*global window, rJS*/
/*jslint indent:2, maxlen: 80, nomen: true */
(function (window, rJS) {
  "use strict";

  rJS(window)
    .declareAcquiredMethod('updateHeader', 'updateHeader')
    .declareAcquiredMethod('getUrlFor', 'getUrlFor')
    .declareAcquiredMethod('translateHtml', 'translateHtml')
    .declareAcquiredMethod('jio_allDocs', 'jio_allDocs')
    .declareMethod('render', function () {
      var gadget = this;
      return gadget.getDeclaredGadget('form')
        .push(function (form) {
          var column_list = [
            ['title', 'Title']
          ];
          return form.render({
            erp5_document: {
              "_embedded": {"_view": {
                "listbox": {
                  "column_list": column_list,
                  "show_anchor": 0,
                  "default_params": {},
                  "editable": 0,
                  "editable_column_list": [],
                  "key": "software_product_module",
                  "lines": 20,
                  "list_method": "portal_catalog",
                  "query": "urn:jio:allDocs?query=portal_type%3A%22" +
                    "Software%20Product%22" +
                    "%20AND%20validation_state%3A%28%22validated%22%" +
                    "20OR%20%22draft%22%29",
                  "portal_type": [],
                  "search_column_list": column_list,
                  "sort_column_list": column_list,
                  "sort": [],
                  "title": "Application List",
                  "type": "ListBox"
                }
              }},
              "_links": {
                "type": {
                  // form_list display portal_type in header
                  name: ""
                }
              }
            },
            form_definition: {
              group_list: [[
                "bottom",
                [["listbox"]]
              ]]
            }
          });
        })
        .push(function () {
          return gadget.getUrlFor({
            'command': 'display_erp5_action',
            'options': {
              'jio_key': 'software_product_module',
              'page': 'create_new_application_dialog'
            }
          });
        })
        .push(function (url) {
          return gadget.updateHeader({
            page_title: "OfficeJS Appstore",
            add_url: url
          });
        });
    });

}(window, rJS));