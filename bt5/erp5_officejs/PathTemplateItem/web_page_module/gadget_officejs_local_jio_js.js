/*global window, window, rJS, jIO, RSVP, UriTemplate, console */
/*jslint indent: 2, maxerr: 10, maxlen: 95 */
(function (window, rJS, jIO, RSVP, UriTemplate, console) {
  "use strict";

  // jIO call wrapper for redirection to authentication page if needed
  function wrapJioCall(gadget, method_name, argument_list) {
    var storage = gadget.state_parameter_dict.jio_storage;
    if (storage === undefined) {
      return gadget.redirect({command: 'display',
                              options: {page: 'ojs_configurator'}});
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
                      url: UriTemplate.parse(regexp.exec(login_page)[1])
                        .expand({came_from: came_from})
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
          return gadget.notifySubmitted({message: 'Unauthorized storage access',
                                         status: 'error'})
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
      gadget.state_parameter_dict = {};
    })

    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod('getUrlFor', 'getUrlFor')

    .declareMethod('clean', function (appcache_storage) {
      //clean previous app version documents
      var sync_flag = "appcache-stored",
        document_id_list = [sync_flag,
                            "portal_skins/erp5_text_editor/" +
                            "Base_cloneDocumentForTextEditor",
                            "portal_skins/erp5_text_editor/" +
                            "Base_viewNewContentDialogForTextEditor",
                            "portal_skins/erp5_text_editor/" +
                            "WebPageModule_viewWebPageListAsJioForTextEditor",
                            "portal_skins/erp5_text_editor/" +
                            "WebPage_viewAsTextDocumentForTextEditor",
                            "portal_types/Web Page",
                            "portal_types/Web Page Module",
                            "portal_types/Web Page Module/text_editor_view",
                            "portal_types/Web Page/text_editor_clone",
                            "portal_types/Web Page/text_editor_clone"],
        promise_list = [],
        i = 0;
      return appcache_storage.get(sync_flag)
        .push(function () {
          for (i = 0; i < document_id_list.length; i += 1) {
            promise_list = [appcache_storage.remove(document_id_list[i])];
          }
          return RSVP.all(promise_list);
        }, function (error) {
          if (error && String(error.status_code) !== "404") {
            throw error;
          }
        });
    })

    .declareMethod('createJio', function (jio_options) {
      if (jio_options === undefined) { return; }
      var gadget = this,
        appcache_storage,
        origin_url = window.location.href;
      return RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.getSetting('app_configuration'),
            gadget.getSetting('hateoas_appcache'),
            gadget.getSetting('jio_storage_name')
          ]);
        })
        .push(function (result_list) {
          var jio_appchache_options = {
            type: "replicate",
            parallel_operation_attachment_amount: 10,
            parallel_operation_amount: 1,
            conflict_handling: 2, //keep remote
            signature_hash_key: 'hash',
            check_remote_attachment_modification: true,
            check_remote_attachment_creation: true,
            check_remote_attachment_deletion: true,
            check_remote_deletion: true,
            check_local_creation: false,
            check_local_deletion: false,
            check_local_modification: false,
            signature_sub_storage: {
              type: "query",
              sub_storage: {
                type: "indexeddb",
                database: "configuration-hash"
              }
            },
            local_sub_storage: JSON.parse(JSON.stringify(jio_options)),
            remote_sub_storage: {
              type: "saferepair",
              sub_storage: {
                type: "configuration",
                origin_url: origin_url,
                current_storage: result_list[2],
                hateoas_appcache: result_list[1],
                manifest: result_list[0],
                sub_storage: {
                  type: "appcache",
                  manifest: result_list[0]
                }
              }
            }
          };
          jio_options = {
            type: 'dateupdater',
            sub_storage: jio_options,
            property_list: ['modification_date']
          };
          try {
            gadget.state_parameter_dict.jio_storage = jIO.createJIO(jio_options);
          } catch (error) {
            gadget.state_parameter_dict.jio_storage = undefined;
          }
          if (result_list[2] === undefined) { return; }
          appcache_storage = jIO.createJIO(jio_appchache_options);
        })
        .push(function () {
          return gadget.clean(appcache_storage);
        })
        .push(function () {
          return appcache_storage.repair();
        })
        .push(undefined, function (error) {
          console.log("Error while appcache-local " +
                      "storage synchronization");
          if (error && error.currentTarget &&
              error.currentTarget.status === 401) {
            console.log("Unauthorized access to storage," +
                        "sync cancelled");
            gadget.state_parameter_dict.jio_storage_name = "ERP5";
            return;
          }
          console.log(error);
          throw error;
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

}(window, rJS, jIO, RSVP, UriTemplate, console));