/*globals window, RSVP, rJS*/
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, RSVP, rJS) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // some parameters
  /////////////////////////////////////////////////////////////////
  var STR = "",
    QUERY = 'urn:jio:allDocs?query=' + 'portal_type:"publisher"',
    SORT = 'field_listbox_sort_list:json',
    COLUMN_LIST = [
      ['title', 'Title'],
      ['country', 'Country'],
      ['total_lines', 'Total Lines of Code']
    ],
    SORT_LIST = [
      ['total_lines', 'Total Lines of Code']
    ];

  rJS(window)

    /////////////////////////////////////////////////////////////////
    // acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("updateHeader", "updateHeader")

    /////////////////////////////////////////////////////////////////
    // published methods
    /////////////////////////////////////////////////////////////////
    .allowPublicAcquisition('updateHeader', function () {
      return;
    })

    .allowPublicAcquisition('getUrlParameter', function (argument_list) {
      return this.getUrlParameter(argument_list)
        .push(function (result) {
          if ((result === undefined) && (argument_list[0] === SORT)) {
            return [['title', 'ascending']];
          }
          return result;
        });
    })

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function () {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.updateHeader({page_title: "Statistics"}),
            gadget.getDeclaredGadget("form_list")
          ]);
        })
        .push(function (result_list) {
          return result_list[1].render({
            erp5_document: {
              "_embedded": {
                "_view": {
                  "listbox": {
                    "column_list": COLUMN_LIST,
                    "show_anchor": 0,
                    "default_params": {},
                    "editable": 0,
                    "key": "field_listbox",
                    "lines": 20,
                    "list_method": "portal_catalog",
                    "query": QUERY,
                    "portal_type": [],
                    "search_column_list": COLUMN_LIST,
                    "sort_column_list": SORT_LIST,
                    "sort_on": ["total_lines", "descending"],
                    "title": "Documents",
                    "type": "ListBox"
                  }
                }
              },
              "_links": {"type": {name: STR}}
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
