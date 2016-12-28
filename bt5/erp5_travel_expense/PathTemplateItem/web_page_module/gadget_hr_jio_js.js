/*global window, rJS, RSVP, jIO, alertify, UriTemplate, indexedDB*/
/*jslint indent: 2, nomen: true */
(function (window, rJS, RSVP, jIO, UriTemplate, alertify, indexedDB) {
  "use strict";
  // xxxxxxxxxxxxxxxxx overwrite 
  function openIndexedDB(jio_storage) {
    var db_name = jio_storage._database_name;
    function resolver(resolve, reject) {
      // Open DB //
      var request = indexedDB.open(db_name);
      request.onerror = function (error) {
        if (request.result) {
          request.result.close();
        }
        reject(error);
      };

      request.onabort = function () {
        request.result.close();
        reject("Aborting connection to: " + db_name);
      };

      request.ontimeout = function () {
        request.result.close();
        reject("Connection to: " + db_name + " timeout");
      };

      request.onblocked = function () {
        request.result.close();
        reject("Connection to: " + db_name + " was blocked");
      };

      // Create DB if necessary //
      request.onupgradeneeded = function () {
        return;
      };

      request.onversionchange = function () {
        request.result.close();
        reject(db_name + " was upgraded");
      };

      request.onsuccess = function () {
        resolve(request.result);
      };
    }
    // XXX Canceller???
    return new RSVP.Queue()
      .push(function () {
        return new RSVP.Promise(resolver);
      });
  }
  function openTransaction(db, stores, flag, autoclosedb) {
    var tx = db.transaction(stores, flag);
    if (autoclosedb !== false) {
      tx.oncomplete = function () {
        db.close();
      };
    }
    tx.onabort = function () {
      db.close();
    };
    return tx;
  }
  function handleRequest(request) {
    function resolver(resolve, reject) {
      request.onerror = reject;
      request.onsuccess = function () {
        resolve(request.result);
      };
    }
    return new RSVP.Promise(resolver);
  }

  jIO.__storage_types.indexeddb.prototype.remove = function (id) {
    return openIndexedDB(this)
      .push(function (db) {
        var transaction = openTransaction(db, ["metadata"], "readwrite");
        return handleRequest(transaction
                        .objectStore("metadata")["delete"](id));
      });
  };

  function endsWith(str, suffix) {
    return str.indexOf(suffix, str.length - suffix.length) !== -1;
  }
  function hashParams() {
    var hash = window.location.toString().split('#')[1],
      split,
      query = "",
      subhashes,
      subhash,
      keyvalue,
      index,
      key,
      tmp,
      args = {};
    if (hash !== undefined) {
      split = hash.split('?');
      query = split[1] || "";
    }
    subhashes = query.split('&');
    for (index in subhashes) {
      if (subhashes.hasOwnProperty(index)) {
        subhash = subhashes[index];
        if (subhash !== '') {
          keyvalue = subhash.split('=');
          if (keyvalue.length === 2) {
            key = decodeURIComponent(keyvalue[0]);
            tmp = decodeURIComponent(keyvalue[1]);
            if (tmp && (endsWith(key, ":json"))) {
              tmp = JSON.parse(tmp);
            }
            args[key] = tmp;
          }
        }
      }
    }
    return args;
  }


  function handleHTTPError(gadget, error, method_name) {
    var regexp = /^X-Delegate uri="(http[s]*:\/\/[\/\-\[\]{}()*+:?.,\\\^$|#\s\w%]+)"$/,
      login_page;

    if ((error.target !== undefined) && (error.target.status === 401)) {
      login_page = error.target.getResponseHeader('WWW-Authenticate');
      // Only connect to https to login
            var regexp = /^X-Delegate uri="(http[s]*:\/\/[\/\-\[\]{}()*+:?.,\\\^$|#\s\w%]+)"$/
            var auth_page = error.target.getResponseHeader('WWW-Authenticate'),
              site;
           if (! auth_page) {
              auth_page = window.location.href + 'hateoas/connection/login_form';
            }
           /* if (regexp.test(auth_page)) {
              site = UriTemplate.parse(
                regexp.exec(auth_page)[1]
              ).expand({
                came_from: window.location.href,
                cors_origin: window.location.origin,
                });
            }*/
    
          if (auth_page) {
            return gadget.redirect({ toExternal: true, url: auth_page});
          }
        }
       
    if ((error.target !== undefined) && (error.target.status === 0)) {
      alertify.error("you are offline");
      window.setTimeout(function () {
        if (method_name === 'repair') {
          alertify.error("synchronisation failed");
        }
        if (method_name === 'getAttachment') {
          alertify.error("please try again when online");
        }
      }, 2000);
      return;
    }
    throw error;
  }

  function wrapJioCall(gadget, method_name, argument_list, default_storage) {
    var storage = default_storage || gadget.state_parameter_dict.jio_storage;

    /*if (!gadget.state_parameter_dict.authenticated) {
      // Access ERP5 to get information about the login page
      return gadget.state_parameter_dict.jio_storage.__storage._remote_sub_storage.getAttachment(
        'acl_users',
        'links',
        {format: 'json'}
      )
        .push(function () {
          gadget.state_parameter_dict.authenticated = true;
          return wrapJioCall(gadget, method_name, argument_list);
        }, function (error) {
          return handleHTTPError(gadget, error);
        });
    }*/

    return storage[method_name].apply(storage, argument_list)
      .push(undefined, function (error) {
        return handleHTTPError(gadget, error, method_name);
      });
  }


  function setUserTitle(gadget, no_auto_resync) {
    // Get user information
    return;
    return gadget.getSetting('user_title')
      .push(function (user_title) {
        if (!user_title) {
          // Force synchro when user login
          return wrapJioCall(gadget, 'repair');
        }
      })
      .push(function () {
        return wrapJioCall(gadget, 'get', [gadget.state_parameter_dict.me]);
      })
      .push(function (person) {
        if (person) {
          return gadget.setSetting('user_title', person.first_name + " " + person.last_name);
        } else {
          return gadget.setSetting('user_title', '');
        }
      }, function (error) {
        if ((error instanceof jIO.util.jIOError) && (error.status_code === 404)) {
          if (no_auto_resync !== true) {
            // Prevent repair infinite loop if person document is not synchronized
            // This is the first automatic synchro to init DB
            return wrapJioCall(gadget, 'repair')
              .push(function () {
                return setUserTitle(gadget, true);
              });
          }
          return gadget.setSetting('user_title', '');
        }
        return gadget.setSetting('user_title', '')
          .push(function () {
            throw error;
          });
      });
  }

  rJS(window)

    .ready(function (gadget) {
      alertify.set({ delay: 1500 });
      gadget.state_parameter_dict = {
        authenticated: false
      };
    })

    .declareAcquiredMethod('setSetting', 'setSetting')
    .declareAcquiredMethod('getSetting', 'getSetting')
    .declareAcquiredMethod('getUrlFor', 'getUrlFor')
    .declareAcquiredMethod('redirect', 'redirect')
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")

    .declareMethod('createJio', function () {
      var gadget = this,
        logout_url_template,
        tmp;
      //localStorage.clear();
      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.getSetting('hateoas_url'),
            gadget.getSetting('default_view_reference'),
            gadget.getSetting('me')
          ]);
        })
        .push(function (setting_list) {
          var me = setting_list[2],
            current_date = new Date(),
            new_date = new Date(
              current_date.getFullYear(),
              current_date.getMonth(),
              current_date.getDate() - 60
            );
          //office router can't handler me parameter
          me = 'tmp';
          gadget.state_parameter_dict.me = me;
          //gadget.state_parameter_dict.authenticated = true;
          gadget.state_parameter_dict.jio_storage = jIO.createJIO({
            type: "replicate",
            // XXX This drop the signature lists...
            query: {
              query: '(portal_type: "Expense Record" AND simulation_state:("draft","sent","stopped"))' +
                'OR (portal_type: "Travel Request Record" AND simulation_state:("draft","sent","stopped")) ' +
                'OR (portal_type: "Leave Request Record" AND validation_state:"draft") ' +
                'OR (portal_type: "Currency" AND validation_state:"validated") ' +
                'OR (portal_type: "Service" AND validation_state:"validated") ' +
                'OR (portal_type: "Person" AND id: "' + me.split("/")[1] + '")',
              limit: [0, 1234567890]
            },
            use_remote_post: true,
            conflict_handling: 3,
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
                  database: "mmr-erp5-" + me
                }
              }
            },
            remote_sub_storage: {
              type: "erp5",
              url: setting_list[0],
              default_view_reference: setting_list[1]
            }
          });
          gadget.state_parameter_dict.jio_storage.__storage._signature_sub_storage = jIO.createJIO({
            type: "indexeddb",
            database: gadget.state_parameter_dict.jio_storage.__storage._signature_hash
          });
          gadget.state_parameter_dict.jio_storage.__storage._signature_sub_storage.__storage._sub_storage = gadget.state_parameter_dict.jio_storage.__storage._local_sub_storage;
          return gadget.setSetting('user_title', '')
            .push(function () {
              return wrapJioCall(gadget, 'repair');
            });
        });

    })
    .declareMethod('get', function () {
      return wrapJioCall(this, 'get', arguments);
    })
    .declareMethod('getAttachment', function () {
      if (this.state_parameter_dict.online) {
        return wrapJioCall(this, 'getAttachment', [arguments[0], arguments[1], {format: "json"}]);
      }
      return wrapJioCall(this, 'getAttachment', [arguments[0], arguments[1], {format: "json"}], this.state_parameter_dict.jio_storage.__storage._remote_sub_storage);
    })
    .declareMethod('post', function () {
      return wrapJioCall(this, 'post', arguments);
    })
    .declareMethod('put', function () {
      return wrapJioCall(this, 'put', arguments);
    })
    .declareMethod('remove', function () {
      return wrapJioCall(this, 'remove', arguments);
    })
    .declareMethod('repair', function () {
      var gadget = this;
      return wrapJioCall(this, 'repair', arguments)
        .push(function () {
          return setUserTitle(gadget);
        });
    })
    .declareMethod('allDocs', function () {
      if (arguments[0].query) {
        if (arguments[0].query.indexOf('relative_url') !== -1) {
          return this.getSetting('user_title')
            .push(function (result) {
              return {
                'data': {
                  'rows': [{
                    'value': {
                      'title': result
                    }
                  }]
                }
              };
            });
        }
      }
      return wrapJioCall(this, 'allDocs', arguments);
    });

}(window, rJS, RSVP, jIO, UriTemplate, alertify, indexedDB));