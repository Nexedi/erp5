/*global window, rJS, jIO, FormData */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS, jIO) {
  "use strict";


  // jIO call wrapper for redirection to authentication page if needed
  function wrapJioCall(gadget, method_name, argument_list) {
    var storage = gadget.state_parameter_dict.jio_storage;
    if (storage === undefined) {
      return gadget.redirect({page: "jio_crib_configurator"});
    }
    return storage[method_name].apply(storage, argument_list);
  }

  rJS(window)

    .ready(function (gadget) {
      gadget.state_parameter_dict = {};
    })

    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("getSetting", "getSetting")

    .declareMethod('createJio', function (jio_options) {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return new RSVP.all([
            gadget.getSetting("communication_gadget", false),
            gadget.getSetting("edited_erp5_url", "")
          ]);
        })
        .push(function (url_list) {
          if (url_list[0]) {
            return gadget.declareGadget(url_list[0], {
              scope: "communication_gadget",
              element: gadget.element.querySelector("div"),
              sandbox: "iframe"
            })
              .push(function (bridge_gadget) {
                gadget.state_parameter_dict.jio_storage = bridge_gadget;
                return bridge_gadget.createStorage(url_list[1]);
              });
          }
        });
    })
    .declareMethod('allDocs', function () {
      return wrapJioCall(this, 'allDocs', arguments);
    })
    .declareMethod('allAttachments', function () {
      return wrapJioCall(this, 'allAttachments', arguments);
    })
    .declareMethod('get', function () {
      return wrapJioCall(this, 'get', arguments);
    })
    .declareMethod('put', function () {
      return wrapJioCall(this, 'put', arguments);
    })
    .declareMethod('post', function () {
      return wrapJioCall(this, 'post', arguments);
    })
    .declareMethod('remove', function () {
      return wrapJioCall(this, 'remove', arguments);
    })
    .declareMethod('getAttachment', function () {
      return wrapJioCall(this, 'gettAttachment', arguments);
    })
    .declareMethod('putAttachment', function () {
      return wrapJioCall(this, 'putAttachment', arguments);
    })
    .declareMethod('removeAttachment', function () {
      return wrapJioCall(this, 'removeAttachment', arguments);
    })
    .declareMethod('repair', function () {
      return wrapJioCall(this, 'repair', arguments);
    });

}(window, rJS, jIO));