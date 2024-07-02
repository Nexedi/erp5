/*globals window, RSVP, rJS, getWorkflowState*/
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, RSVP, rJS) {
  "use strict";

  rJS(window)
    .ready(function (g) {
      g.props = {};
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
        });
    })

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
            return [['doc_id', 'descending']];
          }
          return result;
        });
    })

    .declareMethod("render", function () {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return gadget.updateHeader({
            page_title: "Sale Record"
          });
        })
        .push(function () {
          return gadget.getDeclaredGadget("form_list");
        })
        .push(function (form_gadget) {
          var column_list = [
            ['doc_id', 'ID'],
            ['product', 'Product'],
            ['quantity', 'Quantity'],
            ['quantity_unit', 'Quantity Unit'],
            ['price', 'Price'],
            ['price_currency', 'Currency'],
            ['next_owner', 'Client'],
            ['previous_owner', 'Sales Organisation'],
            ['previous_location', 'Sender Warehouse'],
            ['batch', 'Batch'],
            ['comment', 'Comment'],
            ['date', 'Input Date']
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
                "lines": 10,
                "list_method": "portal_catalog",
                "query": 'urn:jio:allDocs?query=' + 'portal_type:' +
                  '"Sale Record"',
                "portal_type": [],
                "search_column_list": column_list,
                "sort_column_list": column_list,
                "title": "Documents",
                "type": "ListBox"
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

}(window, RSVP, rJS));