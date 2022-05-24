/*globals window, RSVP, rJS*/
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, RSVP, rJS) {
  "use strict";
  rJS(window)
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .allowPublicAcquisition('updateHeader', function () {
      return;
    })
    .allowPublicAcquisition('getUrlParameter', function (argument_list) {
      return this.getUrlParameter(argument_list)
        .push(function (result) {
          if ((result === undefined) &&
              (argument_list[0] === 'field_listbox_sort_list:json')) {
            return [['title', 'ascending']];
          }

          return result;
        });
    })

    .declareMethod("render", function () {
      var gadget = this;
      return gadget.updateHeader({
        page_title: "Success Story List"
      })
      .push(function () {
        return gadget.getDeclaredGadget("form_list");
      })
      .push(function (form_gadget) {
        var column_list = [
          ['title', 'Title'],
          ['software', 'Software'],
          ['publisher', 'Provider'],
          ['industry', 'Industry'],
          ['category_list', 'Software Categories'],
          ['customer', 'Customer'],
          ['country', 'Country'],
          ['language', 'Language']
        ];

        return form_gadget.render({
          erp5_document: {"_embedded": {"_view": {
            "listbox": {
              "column_list": column_list,
              "show_anchor": 0,
              "default_params": {},
              "editable": 1,
              "editable_column_list": [],
              "key": "field_listbox",
              "lines": 20,
              "list_method": "portal_catalog",
              "query": 'urn:jio:allDocs?query=portal_type:"success_case"',
              "portal_type": [],
              "search_column_list": column_list,
              "sort_column_list": column_list,
              "title": "",
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
            ],
              ["hidden", ["listbox_modification_date"]]]
          }
        });
      });
    });
}(window, RSVP, rJS));