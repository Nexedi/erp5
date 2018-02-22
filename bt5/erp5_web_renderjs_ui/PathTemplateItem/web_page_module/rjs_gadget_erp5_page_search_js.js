/*global window, rJS */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .allowPublicAcquisition('updateHeader', function () {
      return;
    })
    .allowPublicAcquisition('getUrlParameter', function (argument_list) {
      return this.getUrlParameter.apply(this, argument_list)
        .push(function (result) {
          if ((result === undefined) && (argument_list[0] === 'field_listbox_sort_list:json')) {
            return [['modification_date', 'descending']];
          }
          return result;
        });
    })
    .declareMethod("triggerSubmit", function () {
      var argument_list = arguments;
      return this.getDeclaredGadget('form_list')
        .push(function (gadget) {
          return gadget.triggerSubmit.apply(gadget, argument_list);
        });
    })
    .declareMethod("render", function () {
      var gadget = this,
        header_dict = {
          page_title: 'Search',
          page_icon: 'search',
          filter_action: true
        };

      return gadget.getUrlParameter('history')
        .push(function (result) {
          if (result !== undefined) {
            return gadget.getUrlFor({command: 'history_previous'});
          }
        })
        .push(function (selection_url) {
          if (selection_url === undefined) {
            return gadget.getUrlFor({command: 'display'});
          }
          header_dict.selection_url = selection_url;
        })
        .push(function (front_url) {
          if (front_url !== undefined) {
            header_dict.front_url = front_url;
          }
          return gadget.updateHeader(header_dict);
        })
        .push(function () {
          return gadget.getDeclaredGadget('form_list');
        })
        .push(function (form_gadget) {
          var column_list = [
            ['translated_portal_type', 'Type'],
            ['title', 'Title'],
            ['reference', 'Reference'],
            ['description', 'Description'],
            ['translated_validation_state_title', 'State']
            // ['modification_date', 'Modification Date']
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
                "lines": 30,
                "list_method": "portal_catalog",
                "query": "urn:jio:allDocs?query=",
                "portal_type": [],
                "search_column_list": column_list,
                "sort_column_list": column_list,
                "title": "Documents",
                "type": "ListBox"
              },
              "listbox_modification_date": {
                "date_only": true,
                "title": "Modification Date",
                "type": "DateTimeField",
                "editable": 1
              }
            }},
              "_links": {
                "type": {
                  // form_list display portal_type in header
                  name: ""
                }
              }},
            form_definition: {
              group_list: [[
                "bottom",
                [["listbox"]]
              ], ["hidden", ["listbox_modification_date"]]]
            }
          });
        });
    });
}(window, rJS));