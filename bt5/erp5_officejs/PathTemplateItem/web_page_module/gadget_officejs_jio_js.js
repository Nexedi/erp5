/*global window, rJS, jIO, FormData, UriTemplate */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS, jIO, RSVP, document, URLSearchParams) {
  "use strict";

  // jIO call wrapper for redirection to authentication page if needed
  function wrapJioCall(gadget, method_name, argument_list) {
    var storage = gadget.state_parameter_dict.jio_storage;
    if (storage === undefined) {
      return gadget.redirect({command: 'display', options: {page: 'ojs_configurator'}});
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
      var gadget = this,
        origin_url = window.location.protocol + "//" + window.location.hostname + window.location.pathname,
        prefix = "./",
        hateoas_script = "hateoas/ERP5Document_getHateoas",
        // TODO manifest should come from gadget.props.cache_file -add script in html body
        manifest = "gadget_officejs_discussion_tool.configuration",
        // TODO review this storage because is not necessary to save the attachments into data storage
        // it should be enough with only the appcache (and a aux local storage) in order to get the attachments
        jio_appchache_options = {
          type: "replicate",
          parallel_operation_attachment_amount: 10,
          parallel_operation_amount: 1,
          conflict_handling: 2,
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
              database: "officejs-hash"
            }
          },
          local_sub_storage: {},
          remote_sub_storage: {
            type: "appcache",
            manifest: manifest,
            origin_url: origin_url
          }
        }, appcache_storage,
        sync_flag = "appcache-stored",
        configuration_ids_dict = {};
      if (jio_options === undefined) {
        return;
      }
      jio_appchache_options.local_sub_storage = JSON.parse(JSON.stringify(jio_options));
      jio_options = {
        type: 'dateupdater',
        sub_storage: jio_options,
        property_list: ['modification_date']
      };
      try {
        this.state_parameter_dict.jio_storage = jIO.createJIO(jio_options);
        appcache_storage = jIO.createJIO(jio_appchache_options);
      } catch (error) {
        this.state_parameter_dict.jio_storage = undefined;
        appcache_storage = undefined;
      }
      return this.getSetting("jio_storage_name")
        .push(function (jio_storage_name) {
          // check if appcache-local sync needs to be done
          // TODO: find a better flag for this
          return appcache_storage.get(sync_flag)
            .push(undefined, function (error) {
                return appcache_storage.repair()
                  .push(function () {
                    return appcache_storage.allAttachments(origin_url)
                      .push(function (attachment_dict) {
                        return new RSVP.Queue()
                          .push(function () {
                            var promise_list = [], i = 0;
                            for (var id in attachment_dict) {
                              if (id.indexOf(hateoas_script) === -1) {
                                promise_list.push(appcache_storage.getAttachment(origin_url, id));
                              } else {
                                promise_list.push(appcache_storage.getAttachment(origin_url, id, {"format": "json"}));
                              }
                              configuration_ids_dict["" + i] = id;
                              i += 1;
                            }
                            return RSVP.all(promise_list);
                          })
                          .push(function (content_list) {
                            var promise_list = [];
                            for (var i = 0; i < content_list.length; i += 1) {
                              var id = configuration_ids_dict["" + i],
                                  parser = document.createElement('a');
                              parser.href = id;
                              var urlParams = new URLSearchParams(parser.search);
                              id = urlParams.get("relative_url");
                              if (id === null) { id = configuration_ids_dict["" + i]; }
                              promise_list.push(appcache_storage.put(id, content_list[i]));
                            }
                            return RSVP.all(promise_list);
                          })
                          .push(function () {
                            return appcache_storage.put(sync_flag, {})
                              .push(undefined);
                          });
                      });
                  }, function (error) {
                  console.log("Error while appcache-local storage synchronization");
                  throw error;
                });
              });
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

}(window, rJS, jIO, RSVP, document, URLSearchParams));