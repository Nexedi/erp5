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
          title: "Organisations"
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
            }, {
              select: 'default_email_coordinate_text',
              title: 'Email'
            }, {
              select: 'default_telephone_coordinate_text',
              title: 'Telephone'
            }, {
              select: 'portal_type',
              title: 'Portal Type'
            }],
            query: {
              query: 'portal_type:("Organisation" OR "Organisation Temp")',
              select_list: ['title', 'default_email_coordinate_text',
                            'default_telephone_coordinate_text', 'portal_type'],
              sort_on: [["title", "ascending"]]
            }
          });
        });
    });

}(window, rJS));