/*globals window, RSVP, rJS, document*/
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, RSVP, rJS, document) {
  "use strict";
   var gadget_klass = rJS(window);
  gadget_klass
    .ready(function (g) {
      g.props = {};
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
        });
    })
    .declareAcquiredMethod("translate", "translate")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod('getSetting', 'getSetting')
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .allowPublicAcquisition("jio_allDocs", function (param_list) {
      var gadget = this;
      return this.jio_allDocs.apply(this, param_list)
        .push(function (result) {
          var i,
            len;
          for (i = 0, len = result.data.total_rows; i < len; i += 1) {
            if (result.data.rows[i].id.indexOf("module") === -1) {
              result.data.rows[i].value.state = "Not synced!";
            } else {
              result.data.rows[i].value.state = "Synced!";
            }
          }
          return result;
        });
    })
    .declareMethod("render", function (options) {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          gadget.props.portal_type = "Expense Sheet";
          gadget.props.document_title_plural = "Expense Sheets";
          return gadget.getUrlFor({page: "add_expense_sheet"});
        })
        .push(function (url) {
          return gadget.updateHeader({
            title: gadget.props.document_title_plural,
            add_url: url
          });
        })
        .push(function () {
          return gadget.declareGadget("gadget_officejs_widget_listbox.html", {element: gadget.props.element.querySelector('.expense_sheet_listbox')});
        })
        .push(function (listbox) {
          return listbox.render({
            search_page: 'expense_sheet_list',
            search: options.search,
            column_list: [{
              select: 'title',
              title: 'Title'
            }, {
              select: 'number',
              title: 'Number'
            }, {
              select: 'state',
              title: 'State'
            }],
            query: {
              query: 'portal_type:("' + gadget.props.portal_type + '")',
              select_list: ['title','number', 'state'],
              sort_on: [["title", "descending"]]
            }
          });
        });
    });

}(window, RSVP, rJS, document));