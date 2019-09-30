/*global window, window, rJS, jIO, RSVP, document, URLSearchParams, UriTemplate, atob, console */
/*jslint indent: 2, maxerr: 10, maxlen: 80 */
(function (window, rJS, jIO, RSVP, document, URLSearchParams, UriTemplate, atob,
           console) {
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

  function processHateoasDict(raw_dict) {
    var raw_field_list, type, parent, field_key, field_id, return_dict = {};
    return_dict.raw_dict = raw_dict;
    /*jslint nomen: true*/
    if (raw_dict.hasOwnProperty("_embedded") &&
        raw_dict._embedded.hasOwnProperty("_view")) {
      raw_field_list = raw_dict._embedded._view;
      type = raw_dict._links.type.name;
      parent = raw_dict._links.parent.name;
      return_dict.parent_relative_url = "portal_types/" + parent;
      return_dict.portal_type = type;
      for (field_key in raw_field_list) {
        if (raw_field_list.hasOwnProperty(field_key)) {
          field_id = "";
          if (raw_field_list[field_key]["default"] !== undefined &&
              raw_field_list[field_key]["default"] !== "") {
            if (field_key.startsWith("my_")) {
              field_id = field_key.replace("my_", "");
            } else if (field_key.startsWith("your_")) {
              field_id = field_key.replace("your_", "");
            } else {
              field_id = field_key;
            }
            return_dict[field_id] = raw_field_list[field_key]["default"];
          }
        }
      }
    } else {
      // ignore non configuration elements
      return raw_dict;
    }
    return return_dict;
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
      var appcache_storage,
        origin_url = window.location.href,
        hateoas_section = "./hateoas_appcache/",
        hateoas_section_and_view = hateoas_section + "definition_view/",
        // TODO manifest should come from gadget.props.cache_file
        // add script in html body
        manifest = "gadget_officejs_text_editor.configuration",
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
              type: "memory"
            }
          },
          local_sub_storage: {},
          remote_sub_storage: {
            type: "saferepair",
            sub_storage: {
              type: "appcache",
              manifest: manifest
            }
          }
        },
        sync_flag = "appcache-stored",
        configuration_ids_list = [];
      if (jio_options === undefined) {
        return;
      }
      jio_appchache_options.local_sub_storage = JSON.parse(
        JSON.stringify(jio_options));
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
          if (jio_storage_name === undefined) { return; }
          appcache_storage = jIO.createJIO(jio_appchache_options);
          // verify if appcache-local sync needs to be done
          return appcache_storage.get(sync_flag)
            .push(undefined, function (error) {
              if (error && String(error.status_code) !== "404") {
                throw error;
              }
              return appcache_storage.repair()
                .push(function () {
                  return appcache_storage.allAttachments(origin_url)
                    .push(function (attachment_dict) {
                      var id, base64, promise_list = [], i = 0;
                      for (id in attachment_dict) {
                        if (attachment_dict.hasOwnProperty(id)) {
                          if (id.startsWith(hateoas_section)) {
                            promise_list.push(
                              appcache_storage
                              .getAttachment(origin_url, id,
                                             {"format": "json"}));
                          } else {
                            promise_list.push(
                              appcache_storage
                              .getAttachment(origin_url, id));
                          }
                          configuration_ids_list[i] = id;
                          i += 1;
                        }
                      }
                      return RSVP.all(promise_list);
                    })
                    .push(function (content_list) {
                      var i, id, parser, urlParams, content, promise_list = [];
                      for (i = 0; i < content_list.length; i += 1) {
                        id = configuration_ids_list[i];
                        if (id.startsWith(hateoas_section)) {
                          id = id.replace(hateoas_section_and_view, "");
                          id = atob(id);
                          content = processHateoasDict(content_list[i]);
                          promise_list.push(appcache_storage.put(id, content));
                        }
                      }
                      return RSVP.all(promise_list);
                    })
                    .push(function () {
                      return appcache_storage.put(sync_flag, {})
                        .push(undefined);
                    }, function (error) {
                      console.log("Error while appcache-local " +
                                  "storage synchronization. Bad " +
                                  "configuration maybe?");
                      console.log(error);
                      throw error;
                    });
                }, function (error) {
                  console.log("Error while appcache-local " +
                              "storage synchronization");
                  if (error && error.currentTarget &&
                      error.currentTarget.status === "401") {
                    console.log("Unauthorized access to storage," +
                                "sync cancelled");
                    return;
                  }
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

}(window, rJS, jIO, RSVP, document, URLSearchParams, UriTemplate, atob,
  console));