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
    .declareAcquiredMethod("put", "jio_put")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod('getSetting', 'getSetting')

    .declareMethod("render", function (options) {
      var gadget = this;
      gadget.props.options = options;
      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.getSetting("portal_type"),
            gadget.getSetting("document_title"),
            gadget.getSetting("parent_relative_url"),
            gadget.getSetting("filename_extension")
          ]);
        }).push(function (answer_list) {
          gadget.props.portal_type = answer_list[0];
          gadget.props.document_title = answer_list[1];
          gadget.props.parent_relative_url = answer_list[2];
          gadget.props.filename_extension = answer_list[3];
          return gadget.updateHeader({
            title: "New " + gadget.props.document_title
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
          return gadget.post({});
        })
        .push(function (data) {
          var doc = {
            // XXX Hardcoded
            parent_relative_url: gadget.props.parent_relative_url,
            portal_type: gadget.props.portal_type
          };
          if (gadget.props.filename_extension) {
            doc.filename = data + '.' + gadget.props.filename_extension;
          }
          return gadget.put(data, doc).then(function () {return data; });
        })
        .push(function (data) {
          return gadget.redirect({
            jio_key: data,
            page: "view"
          });
        });

    });

}(window, RSVP, rJS));