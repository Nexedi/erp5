/*global window, rJS, jIO, alert, XMLHttpRequestProgressEvent, UriTemplate */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS, jIO, alert, XMLHttpRequestProgressEvent, UriTemplate) {
  "use strict";

  // jIO call wrapper for redirection to authentication page if needed
  function wrapJioCall(gadget, method_name, argument_list) {
    var storage = gadget.state_parameter_dict.jio_storage;
    return storage[method_name].apply(storage, argument_list)
      .push(undefined, function (error) {
        if (error instanceof XMLHttpRequestProgressEvent &&
            error.target.status === 401) {
          if (gadget.state_parameter_dict.jio_storage_name === "erp5") {
            return gadget.redirect({ page: "login" });
          }
          if (gadget.state_parameter_dict.jio_storage_name === "dav") {
            var regexp = /^Nayookie login_url=(http[s]?:\/\/[\/\-\[\]{}()*+=:?&.,\\\^$|#\s\w%]+)$/,
              auth_page = error.target.getResponseHeader('WWW-Authenticate'),
              site;
            if (regexp.test(auth_page)) {
              site = UriTemplate.parse(
                regexp.exec(auth_page)[1]
              ).expand({back_url: window.location.href,
                        origin: window.location.protocol + '//' +
                                window.location.host});
              return gadget.redirect({ toExternal: true, url: site });
            }
          }
        } else if (gadget.state_parameter_dict.jio_storage_name === "dav" &&
                 error instanceof XMLHttpRequestProgressEvent &&
                 error.target.status === 0) {
          // XXX: need more precision, not all errors with 0 status should be redirected...
          alert("Unable to access the WebDAV server. It may have an invalid" +
                " SSL certificate, or is just not running.\n" +
                "You will be redirected to this server...");
          return gadget.redirect({ toExternal: true,
                                   url: gadget.state_parameter_dict.jio_storage_url +
                                        '/../redirect?back_url=' + window.location.href
                                 });
        }
        throw error;
      });
  }

  rJS(window)

    .ready(function (gadget) {
      // Initialize the gadget local parameters
      // XXX Hardcoded
      gadget.state_parameter_dict = {jio_storage_name: "dav", // "erp5"
                                     jio_storage_url: "https://localhost:5000/webdav"}; // for ERP5: <instance>/web_site_module/hateoas/
    })

    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("getSetting", "getSetting")

    .declareMethod('createJio', function (jio_options) {
      jio_options = {
        type: 'daverp5mapping',
        sub_storage: {
          type: this.state_parameter_dict.jio_storage_name,
          url: this.state_parameter_dict.jio_storage_url,
          with_credentials: true, // webdav
          default_view_reference: 'view' // erp5
        }
      };
      this.state_parameter_dict.jio_storage = jIO.createJIO(jio_options);
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
      return wrapJioCall(this, 'getAttachment', arguments);
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

}(window, rJS, jIO, alert, XMLHttpRequestProgressEvent, UriTemplate));