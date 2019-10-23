/*globals window, RSVP, rJS*/
/*jslint indent: 2, nomen: true, maxlen: 80*/

(function (window, RSVP, rJS) {
  "use strict";
  rJS(window)
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
          if ((result === undefined) &&
              (argument_list[0] === 'field_listbox_sort_list:json')) {
            return [['title', 'ascending']];
          }
          return result;
        });
    })

    .declareMethod("render", function () {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return gadget.updateHeader({
            page_title: "Publisher List"
          });
        })
        .push(function () {
          return gadget.getDeclaredGadget("form_list");
        })
        .push(function (form_gadget) {
          var column_list = [
            //['logo', 'Logo'],
            ['title', 'Title'],
            ['country', 'Country'],
            ['founded_year', 'Founded'],
            ['presence', 'Presence']
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
                "query": 'urn:jio:allDocs?query=' + 'portal_type:' +
                         '"publisher"',
                "portal_type": [],
                "search_column_list": column_list,
                "sort_column_list": column_list,
                "sort_on": ["title", "ascending"],
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
                  [
                    "bottom",
                    [["listbox"]]
                  ],
                  [
                    "hidden",
                    ["listbox_modification_date"]
                  ]
                ]
              }
            });
        });
    });
}(window, RSVP, rJS));