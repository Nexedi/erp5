/*global window, rJS, jIO, FormData, UriTemplate, RSVP, URL,
         navigator */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS, jIO, RSVP, URL, navigator) {
  "use strict";

  function buildPortalTypeQuery(portal_type_string) {
    var types = portal_type_string.split(','),
      queries = [],
      i;
    for (i = 0; i < types.length; i += 1) {
      queries.push('portal_type: "' + types[i].trim() + '"');
    }
    if (queries.length === 1) {
      return queries[0];
    }
    return '(' + queries.join(' OR ') + ')';
  }

  function autoConfigureERP5Storage(gadget) {
    // Auto-configure ERP5 storage when the app is embedded in ERP5JS.
    // Derives the HATEOAS URL from the app's own URL by navigating to
    // the sibling renderjs_runner Web Site.
    var base_url = window.location.href.split('#')[0],
      erp5_url = new URL('../../renderjs_runner/', base_url).href,
      hateoas_url = erp5_url + 'hateoas/',
      is_low_memory = (navigator.userAgent.indexOf("Chrome") > 0) &&
        (navigator.userAgent.indexOf('Mobile') > 0);
    return gadget.getSetting("portal_type", "Web Page")
      .push(function (portal_type) {
        var query = buildPortalTypeQuery(portal_type);
        return gadget.getSetting("erp5_attachment_synchro", "")
          .push(function (erp5_attachment_synchro) {
            var attachment_synchro = erp5_attachment_synchro !== "",
              extended_attachment_url = erp5_attachment_synchro;
            return gadget.getSetting("default_view_reference", 'jio_view')
              .push(function (default_view_reference) {
                var configuration = {
                  debug: true,
                  report_level: 1000,
                  type: "replicate",
                  query: {
                    query: query,
                    limit: [0, 50],
                    sort_on: [["modification_date", "descending"]]
                  },
                  use_remote_post: true,
                  conflict_handling: 1,
                  parallel_operation_attachment_amount:
                    is_low_memory ? 1 : 10,
                  parallel_operation_amount: is_low_memory ? 1 : 10,
                  check_local_attachment_modification: attachment_synchro,
                  check_local_attachment_creation: attachment_synchro,
                  check_remote_attachment_modification: attachment_synchro,
                  check_remote_attachment_creation: attachment_synchro,
                  check_remote_attachment_deletion: attachment_synchro,
                  check_local_modification: true,
                  check_local_creation: true,
                  check_local_deletion: false,
                  check_remote_modification: true,
                  check_remote_creation: true,
                  check_remote_deletion: true,
                  signature_sub_storage: {
                    type: "query",
                    sub_storage: {
                      type: "uuid",
                      sub_storage: {
                        type: "indexeddb",
                        database: "officejs-erp5-hash"
                      }
                    }
                  },
                  local_sub_storage: {
                    type: "query",
                    schema: {
                      "modification_date": {
                        type: "string",
                        format: "date-time"
                      }
                    },
                    sub_storage: {
                      type: "uuid",
                      sub_storage: {
                        type: "indexeddb",
                        database: "officejs-erp5"
                      }
                    }
                  },
                  remote_sub_storage: {
                    type: "saferepair",
                    sub_storage: {
                      type: "mapping",
                      attachment_list: ["data"],
                      attachment: {
                        "data": {
                          "get": {
                            "uri_template": hateoas_url +
                              extended_attachment_url
                          },
                          "put": {
                            "erp5_put_template": hateoas_url +
                              "/{+id}/Base_edit"
                          }
                        }
                      },
                      sub_storage: {
                        type: "erp5",
                        url: hateoas_url,
                        default_view_reference: default_view_reference
                      }
                    }
                  }
                };
                return gadget.setSetting(
                  'jio_storage_description',
                  configuration
                );
              });
          });
      })
      .push(function () {
        return gadget.setSetting('jio_storage_name', "ERP5");
      })
      .push(function () {
        return gadget.setSetting('sync_reload', true);
      })
      .push(function () {
        return gadget.redirect({
          command: "display",
          options: {page: 'ojs_sync', auto_repair: 'true'}
        });
      });
  }

  // jIO call wrapper for redirection to authentication page if needed
  function wrapJioCall(gadget, method_name, argument_list) {
    var storage = gadget.state_parameter_dict.jio_storage;
    if (storage === undefined) {
      return gadget.getSetting('embedded_erp5_storage')
        .push(function (embedded) {
          if (embedded === 'true') {
            return autoConfigureERP5Storage(gadget);
          }
          return gadget.redirect({
            command: 'display',
            options: {page: 'ojs_configurator'}
          });
        });
    }
    return storage[method_name].apply(storage, argument_list)
      .push(undefined, function (error) {
        if ((error.target !== undefined) && (error.target.status === 401)) {
          var regexp,
            site,
            login_page;
          if (gadget.state_parameter_dict.jio_storage_name === "ERP5") {
            regexp = /^X-Delegate uri=\"(http[s]?:\/\/[\/\-\[\]{}()*+=:?&.,\\\^$|#\s\w%]+)\"$/;
            login_page = error.target.getResponseHeader('WWW-Authenticate');
            if (regexp.test(login_page)) {
              return gadget.getUrlFor({
                command: 'login',
                absolute_url: true
              })
                .push(function (came_from) {
                  return gadget.redirect({
                    command: 'raw',
                    options: {
                      url: UriTemplate.parse(regexp.exec(login_page)[1]).expand({came_from: came_from})
                    }
                  });
                });
            }
          }
          if (gadget.state_parameter_dict.jio_storage_name === "DAV") {
            regexp = /^Nayookie login_url=(http[s]?:\/\/[\/\-\[\]{}()*+=:?&.,\\\^$|#\s\w%]+)$/;
            login_page = error.target.getResponseHeader('WWW-Authenticate');
            if (regexp.test(login_page)) {
              site = UriTemplate.parse(
                regexp.exec(login_page)[1]
              ).expand({
                back_url: window.location.href,
                origin: window.location.origin
              });
            }
          }
          if (site) {
            return gadget.redirect({ command: "row", url: site});
          }
          // User entered wrong password ?
          // Notify
          return gadget.notifySubmitted({message: 'Unauthorized storage access', status: 'error'})
            .push(function () {
              return gadget.redirect({command: 'display',
                                      options: {page: 'ojs_configurator'}});
            });
        }
        throw error;
      });
  }

  rJS(window)

    .ready(function (gadget) {
      // Initialize the gadget local parameters
      gadget.state_parameter_dict = {};
    })

    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("setSetting", "setSetting")
    .declareAcquiredMethod('getUrlFor', 'getUrlFor')

    .declareMethod('createJio', function (jio_options) {
      var gadget = this;
      if (jio_options === undefined) {
        return;
      }
      jio_options = {
        type: 'dateupdater',
        sub_storage: jio_options,
        property_list: ['modification_date']
      };
      try {
        this.state_parameter_dict.jio_storage = jIO.createJIO(jio_options);
      } catch (error) {
        this.state_parameter_dict.jio_storage = undefined;
      }
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

}(window, rJS, jIO, RSVP, URL, navigator));