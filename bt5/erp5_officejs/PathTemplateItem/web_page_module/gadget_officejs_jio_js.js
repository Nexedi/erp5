/*global window, rJS, jIO, FormData, XMLHttpRequestProgressEvent, UriTemplate */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS, jIO) {
  "use strict";

  // jIO call wrapper for redirection to authentication page if needed
  function wrapJioCall(gadget, method_name, argument_list) {
    var storage = gadget.state_parameter_dict.jio_storage;
    return storage[method_name].apply(storage, argument_list)
      .push(undefined, function (error) {
        if (error instanceof XMLHttpRequestProgressEvent &&
            error.target.status === 401) {
          if (gadget.state_parameter_dict.jio_storage_name === "ERP5") {
            return gadget.redirect({ page: "login" });
          }
          if (gadget.state_parameter_dict.jio_storage_name === "DAV") {
            var regexp = /^Nayookie login_url=(http[s]?:\/\/[\/\-\[\]{}()*+=:?&.,\\\^$|#\s\w%]+)$/,
              auth_page = error.target.getResponseHeader('WWW-Authenticate'),
              site;
            if (regexp.test(auth_page)) {
              site = UriTemplate.parse(
                regexp.exec(auth_page)[1]
              ).expand({back_url: window.location.href,
                        origin: window.location.protocol + '//' +
                                window.location.host});
              return gadget.redirect({ toExternal: true, url: site});
            }
          }
        }
        throw error;
      });
  }

  rJS(window)

    .ready(function (gadget) {
      // Initialize the gadget local parameters
      gadget.state_parameter_dict = {};
    })

    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("getSetting", "getSetting")

    .declareMethod('createJio', function (jio_options) {
      var gadget = this;
      if (jio_options === undefined) {
        jio_options = {
          type: "query",
          sub_storage: {
            type: "uuid",
            sub_storage: {
              type: "indexeddb",
              database: "officejs"
            }
          }
        };
      }
      this.state_parameter_dict.jio_storage = jIO.createJIO(jio_options);
      return this.getSetting("jio_storage_name")
        .push(function (jio_storage_name) {
          gadget.state_parameter_dict.jio_storage_name = jio_storage_name;
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