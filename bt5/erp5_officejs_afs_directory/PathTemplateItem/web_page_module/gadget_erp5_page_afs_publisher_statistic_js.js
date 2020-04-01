/*globals window, RSVP, rJS*/
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, RSVP, rJS) {
  "use strict";

  var SORT_STRING = 'field_listbox_sort_list:json';

  rJS(window)
    .ready(function (g) {
      g.props = {};
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
        });
    })

    .declareAcquiredMethod("translate", "translate")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")

    .allowPublicAcquisition('updateHeader', function () {
      return;
    })

    .allowPublicAcquisition('getUrlParameter', function (argument_list) {
      return this.getUrlParameter(argument_list)
        .push(function (result) {
          if ((result === undefined) && (argument_list[0] === SORT_STRING)) {
            return [['line_total', 'descending']];
          }
          return result;
        });
    })

    .declareMethod("render", function () {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return gadget.updateHeader({
            page_title: "Statistics"
          });
        })
        .push(function () {
          return gadget.getDeclaredGadget("form_list");
        })
        .push(function (form_gadget) {
          var column_list = [
            ['title', 'Title'],
            ['country', 'Country'],
            ['line_total', 'Total Lines of Code']
          ],
            sort_column_list = [
              ['line_total', 'Total Lines of Code']
            ];

          return form_gadget.render({
            erp5_document: {"_embedded": {"_view": {
              "listbox": {
                "column_list": column_list,
                "show_anchor": 0,
                "default_params": {},
                "editable": 0,
                "key": "field_listbox",
                "lines": 20,
                "list_method": "portal_catalog",
                "query": 'urn:jio:allDocs?query=' + 'portal_type:"publisher"',
                "portal_type": [],
                "search_column_list": column_list,
                "sort_column_list": sort_column_list,
                "sort_on": ["line_total", "descending"],
                "title": "Documents",
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
              group_list: [
                ["bottom", [["listbox"]]],
                ["hidden",  ["listbox_modification_date"]]
              ]
            }
          });
        });
    });
}(window, RSVP, rJS));
