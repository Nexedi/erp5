/*global window, window, rJS, jIO, RSVP, UriTemplate, console */
/*jslint indent: 2, maxerr: 10, maxlen: 95 */
(function (window, rJS, jIO, RSVP, UriTemplate, console) {
  "use strict";

  function redirectToLogin(gadget, error) {
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
          return redirectToLogin(gadget, error);
        }
        throw error;
      });
  }

  function safeJioRemove(storage, id) {
    return storage.remove(id)
      .push(undefined, function (error) {
        if ((error instanceof jIO.util.jIOError) &&
            (error.status_code === 404)) {
          return;
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
    .declareAcquiredMethod("getSettingList", "getSettingList")
    .declareAcquiredMethod("setSettingList", "setSettingList")
    .declareAcquiredMethod('getUrlFor', 'getUrlFor')

    .declareMethod('updateConfiguration', function (appcache_storage, origin_url,
                                                    migration_version, current_version,
                                                    storage_name) {
      if (!appcache_storage) { return; }
      var gadget = this,
        document_id_list = [origin_url,
                            "appcache-stored",
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
                            "portal_types/Web Page/text_editor_clone"],
        promise_list = [],
        i = 0;
      if (migration_version !== current_version) {
        //clean storage if app version changed
        for (i = 0; i < document_id_list.length; i += 1) {
          promise_list = [safeJioRemove(appcache_storage, document_id_list[i])];
        }
      }
      return RSVP.Queue()
        .push(function () {
          return RSVP.all(promise_list);
        })
        .push(function () {
          return appcache_storage.repair(current_version);
        })
        .push(function () {
          return gadget.setSettingList({"migration_version": current_version,
                                        "previous_storage_name": storage_name});
        });
    })

    .declareMethod('createJio', function (jio_options) {
      if (jio_options === undefined) { return; }
      var gadget = this,
        appcache_storage,
        current_version,
        migration_version,
        selected_storage_name,
        previous_storage_name,
        index,
        origin_url = window.location.href;
      return gadget.getSettingList(['configuration_manifest',
                                    'jio_storage_name',
                                    'previous_storage_name',
                                    'migration_version'])
        .push(function (result_list) {
          selected_storage_name = result_list[1];
          previous_storage_name = result_list[2];
          migration_version = result_list[3];
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
                database: selected_storage_name + "-configuration-hash"
              }
            },
            local_sub_storage: JSON.parse(JSON.stringify(jio_options)),
            remote_sub_storage: {
              type: "saferepair",
              sub_storage: {
                type: "configuration",
                origin_url: origin_url,
                hateoas_appcache: "hateoas_appcache",
                manifest: result_list[0],
                sub_storage: {
                  type: "appcache",
                  origin_url: origin_url,
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
          if (result_list[0] === undefined) { return; }
          if (selected_storage_name === undefined) { return; }
          gadget.state_parameter_dict.jio_storage_name = selected_storage_name;
          appcache_storage = jIO.createJIO(jio_appchache_options);
          current_version = window.location.href.replace(window.location.hash, "");
          index = current_version.indexOf(window.location.host) + window.location.host.length;
          current_version = current_version.substr(index);
          if (migration_version !== current_version ||
              previous_storage_name !== selected_storage_name) {
            return gadget.updateConfiguration(appcache_storage, origin_url, migration_version,
                                              current_version, selected_storage_name);
          }
        })
        .push(undefined, function (error) {
          console.log("Error while appcache-local storage synchronization");
          if (error && error.currentTarget &&
              error.currentTarget.status === 401) {
            console.log("Unauthorized access to storage, sync cancelled");
            return redirectToLogin(gadget, error);
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