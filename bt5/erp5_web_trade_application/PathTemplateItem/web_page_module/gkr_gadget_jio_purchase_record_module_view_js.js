/*globals window, RSVP, rJS*/
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
      var gadget = this;
      return this.jio_allDocs.apply(this, param_list)
        .push(function (result) {
          var i,
            len;
          for (i = 0, len = result.data.total_rows; i < len; i += 1) {
            // XXX jIO does not create UUID with module inside
            result.data.rows[i].value.state = getWorkflowState(result.data.rows[i].value.portal_type, result.data.rows[i].id, result.data.rows[i].value.sync_flag, result.data.rows[i].value.local_validation, result.data.rows[i].value.local_state);
          }
          return result;
        });
    })
    .declareMethod("render", function (options) {
      var gadget = this;
      return new RSVP.Queue()
        .push(function (url) {
          return gadget.updateHeader({
            title: "Purchase Record",
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
              title: 'Product or Material'
            }, {
              select: 'quantity',
              title: 'Quantity'
            }, {
              select: 'quantity_unit',
              title: 'Quantity Unit'
            }, {
              select: 'price',
              title: 'Price'
            }, {
              select: 'price_currency',
              title: 'Currency'
            }, {
              select: 'previousowner',
              title: 'Supplier'
            }, {
              select: 'nextowner',
              title: 'Purchase Organisation'
            }, {
              select: 'nextlocation',
              title: 'Recipient Warehouse or Bin'
            }, {
              select: 'batch',
              title: 'Batch'
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
              query: 'hidden_in_html5_app_flag:"0" AND portal_type:("Purchase Record" OR "Purchase Record Temp")',
              select_list: ['doc_id', 'product', 'quantity', 'quantity_unit', 'price', 'price_currency',
                            'previousowner', 'nextowner', 'nextlocation', 'batch', 'comment', 'date',
                            'inputusername', 'portal_type', 'sync_flag', 'local_validation', 'local_state'],
              sort_on: [["doc_id", "descending"]]
            }
          });
        });
    });

}(window, RSVP, rJS));