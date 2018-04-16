/*global window, rJS, jIO, FormData, UriTemplate */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS, jIO) {
  "use strict";

  // jIO call wrapper for redirection to authentication page if needed
  function wrapJioCall(gadget, method_name, argument_list) {
    var storage = gadget.state_parameter_dict.jio_storage;
    if (storage === undefined) {
      return gadget.redirect({page: "jio_configurator"});
    }
    return storage[method_name].apply(storage, argument_list)
      .push(undefined, function (error) {
        if ((error.target !== undefined) && (error.target.status === 401)) {
          var regexp,
            site,
            auth_page;
          if (gadget.state_parameter_dict.jio_storage_name === "ERP5") {
            regexp = /^X-Delegate uri=\"(http[s]?:\/\/[\/\-\[\]{}()*+=:?&.,\\\^$|#\s\w%]+)\"$/;
            auth_page = error.target.getResponseHeader('WWW-Authenticate');
            if (regexp.test(auth_page)) {
              site = UriTemplate.parse(
                regexp.exec(auth_page)[1]
              ).expand({
                came_from: window.location.href,
                cors_origin: window.location.origin,
                });
            }
          }
          if (gadget.state_parameter_dict.jio_storage_name === "DAV") {
            regexp = /^Nayookie login_url=(http[s]?:\/\/[\/\-\[\]{}()*+=:?&.,\\\^$|#\s\w%]+)$/;
            auth_page = error.target.getResponseHeader('WWW-Authenticate');
            if (regexp.test(auth_page)) {
              site = UriTemplate.parse(
                regexp.exec(auth_page)[1]
              ).expand({
                back_url: window.location.href,
                origin: window.location.origin,
                });
            }
          }
          if (site) {
            return gadget.redirect({ toExternal: true, url: site});
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
    .declareAcquiredMethod("setSetting", "setSetting")

    .declareMethod('createJio', function (jio_options) {
      var gadget = this;
      if (jio_options === undefined) {
        return;
      }
      this.state_parameter_dict.jio_storage = jIO.createJIO(jio_options);
      return this.getSetting("jio_storage_name")
        .push(function (jio_storage_name) {
          gadget.state_parameter_dict.jio_storage_name = jio_storage_name;
          if (jio_storage_name === 'ERP5') {
            return gadget.getSetting('me')
              .push(function (me) {
                if (!me) {
                 return wrapJioCall(gadget, 'getAttachment', ['acl_users', jio_options.url, {format: "json"}])
                  .push(function (result) {
                    me = result._links.me ? result._links.me.href : 'manager';
                   }, function (error) {
                     //erp5 storage url is error
                     me = 'error';
                   })
                  .push(function () {
                   var configure;
                   //recreate erp5 storage with indexeddb
                   configure = {
                      type: "replicate",
                      query: {
                        query: '(portal_type: "Expense Record" AND (simulation_state:"draft" OR simulation_state:"sent" OR simulation_state:"stopped")) ' +
                          'OR (portal_type: "Travel Request Record" AND (simulation_state:"draft" OR simulation_state:"sent" OR simulation_state:"stopped")) ' +
                          'OR (portal_type: "Leave Report Record" AND simulation_state:"stopped") ' +
                          'OR (portal_type: "Leave Request Record" AND (simulation_state:"draft" OR simulation_state:"sent" OR simulation_state:"stopped")) ' +
                          'OR (portal_type: "Localisation Record" AND (simulation_state:"draft" OR simulation_state:"stopped")) ' +
                          'OR (portal_type: "Expense Sheet" AND (reference: "expense_sheet")) ' +
                          'OR (portal_type: "Currency" AND validation_state:"validated") ' +
                          'OR (portal_type: "Service" AND validation_state:"validated") ' +
                          'OR (portal_type: "Person" AND id: "' + me.split("/")[1] + '")',
                         limit: [0, 1234567890]
                      },
                      use_remote_post: true,
                      conflict_handling: 2,
                      check_local_modification: false,
                      check_local_creation: true,
                      check_local_deletion: false,
                      check_remote_modification: false,
                      check_remote_creation: true,
                      check_remote_deletion: true,
                      local_sub_storage: {
                        type: "query",
                        sub_storage: {
                          type: "uuid",
                          sub_storage: {
                          type: "indexeddb",
                          database: "officejs-erp5"
                        }
                       }
                      },
                      remote_sub_storage: jio_options,
                      signature_sub_storage: {
                        type: "query",
                        sub_storage: {
                          type: "indexeddb",
                          database: "expense-hash-list"
                        }
                     }};
                    gadget.state_parameter_dict.jio_storage = jIO.createJIO(configure);
                    return gadget.setSetting('me', me)
                      .push(function () {
                        return gadget.setSetting('jio_storage_description', configure);
                      });
                 });
                }
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
      var gadget = this;
      return wrapJioCall(gadget, 'repair', arguments)
        .push(function () {
          return gadget.setSetting('last_sync_date', new Date().toLocaleString());
        });
    });

}(window, rJS, jIO));