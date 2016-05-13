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
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
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
          return gadget.getDeclaredGadget("listbox");
        })
        .push(function (listbox) {
          return listbox.render({
            jio_key: options.jio_key,
            search: options.search,
            begin_from: options.begin_from,
            column_list: [{
              select: 'doc_id',
              title: 'ID'
            }, {
              select: 'product',
              title: 'Product'
            }, {
              select: 'priced_quantity',
              title: 'Priced Quantity'
            }, {
              select: 'quantity_unit',
              title: 'Quantity Unit'
            }, {
              select: 'base_price',
              title: 'Price'
            }, {
              select: 'price_currency',
              title: 'Currency'
            }, {
              select: 'nextowner',
              title: 'Client'
            }, {
              select: 'comment',
              title: 'Comment'
            }, {
              select: 'date',
              title: 'Input Date'
            }, {
              select: 'inputusername',
              title: 'Input User Name'
            }, {
              select: 'state',
              title: 'State'
            }],
            query: {
              /*
              new ComplexQuery({
                operator: "NOT",
                query_list: [new SimpleQuery({
                  key: key,
                  operator: simple_operator,
                  type: "simple",
                  value: value
                })],
                type: "complex"
              })
              */
              query: 'portal_type:' +
                '("Sale Price Record" OR "Sale Price Record Temp")',
              select_list:
                 ['doc_id', 'product', 'priced_quantity',
                  'quantity_unit', 'base_price', 'price_currency',
                   'nextowner', 'comment', 'date', 'inputusername',
                   'local_state', 'sync_flag', 'local_validation',
                   'portal_type'],
              sort_on: [["doc_id", "descending"]]
            }
          });
        });
    });

}(window, RSVP, rJS));