/*globals window, rJS*/
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, rJS) {
  "use strict";

  rJS(window)
    .ready(function (g) {
      g.props = {};
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
        });
    })

    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareMethod("render", function (options) {
      var gadget = this;
      return gadget
        .updateHeader({
          title: "Gkr Reports"
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
              select: 'title',
              title: 'Title'
            },
            {select: 'follow_up_title',
              title: 'Organisation'
            },
            {select: 'date',
              title: 'Date'
            }],
            query: {
              query: 'portal_type:("Report Item" OR "Report Total")',
              select_list: ['title', 'follow_up_title', 'production_packing_list', 'purchase_packing_list_of_product', 'purchase_packing_list_of_raw_material', 'sale_packing_list', 'date'],
              sort_on: [["title", "descending"]]
            }
          });
        });
    });

}(window, rJS));