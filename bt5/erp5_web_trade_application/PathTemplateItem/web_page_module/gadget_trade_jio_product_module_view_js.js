/*globals window, RSVP, rJS, Handlebars*/
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
          title: "Products"
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
              select: 'reference',
              title: 'Reference'
            }, {
              select: 'title',
              title: 'Title'
            }, {
              select: 'product_line_title',
              title: 'Product or Material Line'
            }, {
              select: 'quantity_unit_title',
              title: 'Quantity Unit'
            }, {
              select: 'portal_type',
              title: 'Portal Type'
            }],
            query: {
              query: 'portal_type:"Product"',
              select_list: ['title', 'reference', 'product_line_title',
                            'quantity_unit_title', 'portal_type'],
              sort_on: [["reference", "ascending"]]
            }
          });
        });
    });

}(window, rJS));