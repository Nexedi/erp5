/*global window, rJS, RSVP, jIO, alertify, UriTemplate, indexedDB*/
/*jslint indent: 2, nomen: true */
(function (window, rJS, RSVP, jIO, UriTemplate, alertify, indexedDB) {
  "use strict";
  // xxxxxxxxxxxxxxxxx overwrite 
  /*
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
  };*/

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
      query = split[0] || "";
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
            
            if (regexp.test(auth_page)) {
              site = UriTemplate.parse(
                regexp.exec(auth_page)[1]
              ).expand({
                came_from: window.location.href + "#{&n.me}",
                cors_origin: window.location.origin,
                });
            }

          if (site) {
            return gadget.redirect({ toExternal: true, url: site});
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
        tmp = hashParams(),
        hateoas_url,
        default_view,
        me;
      me = tmp['n.me'] || '';
      return new RSVP.Queue()
        .push(function () {
          if (me) {
            return gadget.setSetting('me', me);
          }
        })
        .push(function () {
          return RSVP.all([
            gadget.getSetting('hateoas_url'),
            gadget.getSetting('default_view_reference'),
            gadget.getSetting('me')
          ]);
        })
        .push(function (setting_list) {
          var jio_storage;
          hateoas_url = setting_list[0];
          default_view = setting_list[1];
          me = setting_list[2];
          if (!me) {
            jio_storage = jIO.createJIO({
              type: "erp5",
              url: setting_list[0],
              default_view_reference: setting_list[1]
            });
            return wrapJioCall(gadget, 'getAttachment', ['acl_users', hateoas_url, {format: "json"}], jio_storage)
              .push(function (result) {
                me = result._links.me.href;
                return gadget.setSetting('me', me);
              });
          }
        })
        .push(function () {
          var current_date = new Date(),
            new_date = new Date(
              current_date.getFullYear(),
              current_date.getMonth(),
              current_date.getDate() - 60
            );
          gadget.state_parameter_dict.me = me;
          //gadget.state_parameter_dict.authenticated = true;
          gadget.state_parameter_dict.jio_storage = jIO.createJIO({
            type: "replicate",
            // XXX This drop the signature lists...
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
                  database: "mmr-erp5-tmp"
                }
              }
            },
            remote_sub_storage: {
              type: "erp5",
              url: hateoas_url,
              default_view_reference: default_view
            },
            signature_sub_storage: {
              type: "query",
              sub_storage: {
                type: "indexeddb",
                database: "expense-hash-list"
              }
            }
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
        })
        .push(function () {
          return gadget.setSetting('last_sync_date', new Date().toLocaleString());
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