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
          if ((result === undefined) && (argument_list[0] === 'field_listbox_sort_list:json')) {
            return [['doc_id', 'descending']];
          }
          return result;
        });
    })
    .allowPublicAcquisition("jio_allDocs", function (param_list) {
      return this.jio_allDocs.apply(this, param_list)
        .push(function (result) {
          var i,
            len;
          for (i = 0, len = result.data.total_rows; i < len; i += 1) {
            // XXX jIO does not create UUID with module inside
            result.data.rows[i].value.state =
              getWorkflowState(result.data.rows[i].value.portal_type,
                               result.data.rows[i].id,
                               result.data.rows[i].value.sync_flag,
                               result.data.rows[i].value.local_validation,
                               result.data.rows[i].value.local_state);
          }
          return result;
        });
    })
    .declareMethod("render", function (options) {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return gadget.getUrlFor({jio_key: options.jio_key,
                                   page: "add_sale_price_record"});
        })
        .push(function (url) {
          return gadget.updateHeader({
            title: "Sale Price Record",
            right_url: url,
            right_title: "New"
          });
        })
        .push(function () {
          return gadget.getDeclaredGadget("form_list");
        })
        .push(function (form_gadget) {
        var column_list = [
            ['doc_id', 'ID'],
            ['product', 'Product'],
            ['priced_quantity', 'Priced Quantity'],
            ['quantity_unit', 'Quantity Unit'],
            ['base_price', 'Price'],
            ['price_currency', 'Currency'],
            ['nextowner', 'Client'],
            ['comment', 'Comment'],
            ['date', 'Input Date'],
            ['inputusername', 'Input User Name'],
            ['state', 'State'],

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
                "query": 'portal_type:' +
                '("Sale Price Record" OR "Sale Price Record Temp")',
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