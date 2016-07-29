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

    .declareMethod("render", function (options) {
      var gadget = this;
      gadget.props.options = options;

      return gadget.updateHeader({
        title: "New Spreadsheet"
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
            parent_relative_url: "document_module",
            portal_type: "Spreadsheet"
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