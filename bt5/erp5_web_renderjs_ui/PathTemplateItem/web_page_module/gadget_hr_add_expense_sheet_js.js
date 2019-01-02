/*globals window, RSVP, rJS*/
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, RSVP, rJS) {
  "use strict";

  var gadget_klass = rJS(window);

  gadget_klass
    .ready(function (g) {
      g.props = {};
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
          g.props.deferred = RSVP.defer();
        });
    })

    .declareAcquiredMethod("post", "jio_post")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod('getSetting', 'getSetting')

    .declareMethod("render", function (options) {
      var gadget = this;
      gadget.props.options = options;
      return new RSVP.Queue()
        .push(function () {
          gadget.props.portal_type = "Expense Sheet";
          gadget.props.parent_relative_url = "expense_sheet_module";
          return gadget.updateHeader({
            title: "New Expense Sheet"
          });
        })
        .push(function () {
          gadget.props.deferred.resolve();
        });
    })

    .declareService(function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {
          var doc = {
            // XXX Hardcoded
            parent_relative_url: gadget.props.parent_relative_url,
            portal_type: gadget.props.portal_type
          };
          return gadget.post(doc);
        })
        .push(function (data) {
          return gadget.redirect({
            jio_key: data,
            page: "view"
          });
        });

    });

}(window, RSVP, rJS));