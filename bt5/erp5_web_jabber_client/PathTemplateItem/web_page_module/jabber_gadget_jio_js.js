/*global window, rJS, RSVP, jIO, document, loopEventListener */
/*jslint indent: 2, maxerr: 3, nomen: true */
(function (window, rJS, RSVP, jIO, document, loopEventListener) {
  "use strict";

  var CONNECTION_GADGET_SCOPE = "connection",
    CONNECTION_GADGET_URL = "connection/",
    JIO_GADGET_URL = "gadget_jio.html";

  function dropNotification() {
    document.querySelector("link[rel='shortcut icon']").setAttribute("href", "gadget_jabberclient_notification_ok.ico");
  }

  function wrapJioCall(gadget, method_name, argument_list) {
    var storage = gadget.state_parameter_dict.persistent_jio;
    return storage[method_name].apply(storage, argument_list);
  }

  function zfill(s, size) {
    s = String(s);
    while (s.length < size) {
      s = "0" + s;
    }
    return s;
  }

  function getLogString(text, is_incomming) {
    var prefix,
      date = new Date(),
      timestamp = date.getFullYear() + "-" +
        zfill(date.getMonth() + 1, 2) + "-" +
        zfill(date.getDate(), 2) + " " +
        date.toTimeString();
    if (is_incomming) {
      prefix = '<';
    } else {
      prefix = '>';
    }
    return "[" + timestamp + "] " + prefix + " " + text + "\n";
  }

  function getStorageIdFromJid(gadget, jid) {
    return gadget.state_parameter_dict.my_jid + '-' + jid;
  }

  function enqueueDefer(gadget, callback) {
    var deferred = gadget.props.current_deferred;

    // Unblock queue
    if (deferred !== undefined) {
      deferred.resolve("Another event added");
    }

    // Add next callback
    try {
      gadget.props.service_queue.push(callback);
    } catch (error) {
      throw new Error("Connection gadget already crashed... " +
                      gadget.props.service_queue.rejectedReason.toString());
    }

    // Block the queue
    deferred = RSVP.defer();
    gadget.props.current_deferred = deferred;
    gadget.props.service_queue.push(function () {
      return deferred.promise;
    });
  }

  function getLog(gadget, jid, options) {
    return wrapJioCall(gadget, 'getAttachment', [getStorageIdFromJid(gadget, jid), 'enclosure', options])
      .push(undefined, function (error) {
        if ((error instanceof jIO.util.jIOError) &&
            (error.status_code === 404)) {
          return '';
        }
        throw error;
      });
  }

  function addLog(gadget, jid, text, is_incoming) {
    var deferred = RSVP.defer();
    enqueueDefer(gadget, function () {
      return getLog(gadget, jid, {format: 'text'})
        .push(function (result) {
          var new_history = result + getLogString(text, is_incoming);
          return wrapJioCall(gadget, 'putAttachment', [getStorageIdFromJid(gadget, jid), 'enclosure', new_history]);
        })
        .push(function () {
          deferred.resolve();
          return true;
        });
    });
    return new RSVP.Queue().push(function () {
      return deferred.promise;
    });
  }

  function dropConnectionGadget(gadget) {
    gadget.state_parameter_dict.connection_element.innerHTML = "";
    gadget.state_parameter_dict.connected = false;
    delete gadget.state_parameter_dict.my_jid;
    return gadget.dropGadget(CONNECTION_GADGET_SCOPE)
      .push(function () {
        gadget.state_parameter_dict.connection_defer.cancel("Drop previous connection");
      });
  }

  function initConnectionGadget(gadget, data) {
    // Always kill the previous connection gadget to ensure disconnection
    return dropConnectionGadget(gadget)
      .push(undefined, function () {
        // Do not crash if connection gadget was not yet instanciated
        return;
      })
      .push(function () {
        return gadget.declareGadget(JIO_GADGET_URL);
      })
      .push(function (volatile_jio) {
        gadget.state_parameter_dict.volatile_jio = volatile_jio;
        return volatile_jio.createJio({
          type: "query",
          sub_storage: {
            type: "document",
            document_id: "/",
            sub_storage: {
              type: "local",
              sessiononly: true
            }
          }
        });
      })
      .push(function () {
        // Mark all contacts as offline
        return gadget.state_parameter_dict.volatile_jio.allDocs();
      })
      .push(function (result) {
        var i, promise_list = [];

        function markOffline(key) {
          return gadget.state_parameter_dict.volatile_jio.get(key)
            .push(function (doc) {
              doc.connected = false;
              return gadget.state_parameter_dict.volatile_jio.put(key, doc);
            });
        }

        for (i = 0; i < result.data.rows.length; i += 1) {
          promise_list.push(markOffline(result.data.rows[i].id));
        }
        return RSVP.all(promise_list);
      })
      .push(function () {
        return gadget.declareGadget(CONNECTION_GADGET_URL, {
          scope: CONNECTION_GADGET_SCOPE,
          sandbox: 'iframe',
          element: gadget.state_parameter_dict.connection_element
        });
      })
      .push(function (connect_gadget) {
        gadget.state_parameter_dict.connection_defer = RSVP.defer();
        gadget.state_parameter_dict.server = data.server;
        gadget.state_parameter_dict.jid = data.jid;
        gadget.state_parameter_dict.passwd = data.passwd;
        return connect_gadget.connect(data.server, data.jid, data.passwd);
      })
      .push(function () {
        gadget.state_parameter_dict.my_jid = data.jid;
        return gadget.state_parameter_dict.connection_defer.promise;
      });
  }

  function initializeContact(gadget, jid) {
    var doc;
    return gadget.state_parameter_dict.volatile_jio.get(jid)
      .push(undefined, function (error) {
        if ((error instanceof jIO.util.jIOError) &&
            (error.status_code === 404)) {
          return {
            jid: jid,
            connected: false,
            notification: false
          };
        }
        throw error;
      })
      .push(function (result) {
        doc = result;
        return gadget.state_parameter_dict.volatile_jio.put(jid, doc);
      })
      .push(function () {
        return doc;
      });
  }

  rJS(window)
    .ready(function (g) {
      g.props = {};
    })

    .allowPublicAcquisition("notifyXMPPConnecting", function () {
      return;
    })

    .allowPublicAcquisition("notifyXMPPConnectingFail", function () {
      this.state_parameter_dict.connection_defer.reject('Connection Failed. Please login again.');
    })

    .allowPublicAcquisition("notifyXMPPConnected", function () {
      var gadget = this;
      // gadget.props.connected = true;
      return gadget.getDeclaredGadget(CONNECTION_GADGET_SCOPE)
        .push(function (connection_gadget) {
          return RSVP.all([
            connection_gadget.sendPresence(),
            connection_gadget.fetchRoster()
          ]);
        })
        .push(function (result_list) {
          var key,
            contact_list = result_list[1],
            promise_list = [];
          for (key in contact_list) {
            if (contact_list.hasOwnProperty(key)) {
              promise_list.push(
                initializeContact(gadget, contact_list[key].jid)
              );
            }
          }
          return RSVP.all(promise_list);
        })
        .push(function () {
          gadget.state_parameter_dict.connected = true;
          gadget.state_parameter_dict.connection_defer.resolve();
        });
    })

    .allowPublicAcquisition("notifyXMPPAuthenticatingFailed", function () {
      this.state_parameter_dict.connection_defer.reject('Authentication Failed. Please try again.');
    })

    .allowPublicAcquisition("notifyXMPPDisconnecting", function () {
      return;
    })

    .allowPublicAcquisition("notifyXMPPPresence", function (argument_list) {
      var gadget = this,
        from = argument_list[0],
        type = argument_list[2];

      return initializeContact(gadget, from)
        .push(function (doc) {
          if ((type === "unavailable") || (type === "unsubscribed")) {
            // Bye dear contact
            doc.connected = false;
          } else {
            doc.connected = true;
          }
          return gadget.state_parameter_dict.volatile_jio.put(from, doc);
        })
        .push(function () {
          return gadget.refresh();
        });
    })

    .allowPublicAcquisition("notifyXMPPMessageTextReceived",
                            function (argument_list) {

        if (!document.hasFocus()) {
          // Only notify when page has no focused.
          // It simplifies a lot notification status
          document.querySelector("link[rel='shortcut icon']").setAttribute("href", "gadget_jabberclient_notification_warning.ico");

	  if ("Notification" in window) {
            if (Notification.permission === "granted") {
              var notification = new Notification(argument_list[0], {body: argument_list[2]});
            }
            else if (Notification.permission !== "denied") {
              Notification.requestPermission(function (permission) {
                if (permission === "granted") {
                  var notification = new Notification(argument_list[0], {body: argument_list[2]});
                }
              });
            }
          }
        }

        var gadget = this;
        return addLog(this, argument_list[0], argument_list[2], true)
          .push(function () {
            return initializeContact(gadget, argument_list[0]);
          })
          .push(function (doc) {
            doc.notification = true;
            return gadget.state_parameter_dict.volatile_jio.put(argument_list[0], doc);
          })
          .push(function () {
            return gadget.refresh();
          });
      })

    .allowPublicAcquisition("notifyXMPPSubscribe", function (argument_list) {
      var gadget = this,
        connection_gadget;
      // Auto subscribe to any request
      return gadget.getDeclaredGadget(CONNECTION_GADGET_SCOPE)
        .push(function (declared_gadget) {
          connection_gadget = declared_gadget;
          return connection_gadget.requestSubscribe(argument_list[0]);
        })
        .push(function () {
          return connection_gadget.acceptSubscription(
            argument_list[0]
          );
        })
        .push(function () {
          return connection_gadget.sendPresence();
        });
    })

    .allowPublicAcquisition("notifyXMPPUnsubscribe", function (argument_list) {
      var gadget = this,
        connection_gadget;
      // Auto unsubscribe to any request
      return gadget.getDeclaredGadget(CONNECTION_GADGET_SCOPE)
        .push(function (declared_gadget) {
          connection_gadget = declared_gadget;
          return connection_gadget.requestUnsubscribe(argument_list[0]);
        })
        .push(function () {
          return connection_gadget.acceptUnsubscription(
            argument_list[0]
          );
        })
        .push(function () {
          return connection_gadget.sendPresence();
        });
    })

    .allowPublicAcquisition("notifyXMPPDisconnected", function () {
      var gadget = this;
      // Notify about disconnection
      document.querySelector("link[rel='shortcut icon']").setAttribute("href", "gadget_jabberclient_notification_warning.ico");
      return dropConnectionGadget(gadget)
        .push(function () {
          return this.redirect({command: 'display', options: {page: 'connect'}});
        });
    })

    .allowPublicAcquisition("notifyXMPPConnectionError", function () {
      var gadget = this;
      // Notify about disconnection
      document.querySelector("link[rel='shortcut icon']").setAttribute("href", "gadget_jabberclient_notification_warning.ico");

      return dropConnectionGadget(gadget)
        .push(function () {
          return this.redirect({command: 'display', options: {page: 'connect'}});
        });
    })

    .allowPublicAcquisition("notifyXMPPError", function () {
      var gadget = this;
      // Notify about disconnection
      document.querySelector("link[rel='shortcut icon']").setAttribute("href", "gadget_jabberclient_notification_warning.ico");

      return dropConnectionGadget(gadget)
        .push(function () {
          return this.redirect({command: 'display', options: {page: 'connect'}});
        });
    })

    .ready(function (gadget) {
      gadget.state_parameter_dict = {
        connected: false,
        server: 'https://mail.nexedi.net/chat/http-bind/',
        jio: '',
        passwd: ''
      };
      dropNotification();
    })
    .ready(function (gadget) {
      return gadget.getDeclaredGadget('persistent_jio')
        .push(function (jio_gadget) {
          // Initialize the gadget local parameters
          gadget.state_parameter_dict.persistent_jio = jio_gadget;
        });
    })
    .ready(function (gadget) {
      return gadget.getElement()
        .push(function (element) {
          gadget.state_parameter_dict.connection_element = element.querySelector('.connection-gadget-container');
        });
    })

    .declareAcquiredMethod('getSetting', 'getSetting')
    .declareAcquiredMethod('redirect', 'redirect')
    .declareAcquiredMethod('getUrlFor', 'getUrlFor')
    .declareAcquiredMethod('refresh', 'refresh')

    .declareMethod('createJio', function () {
      return this.state_parameter_dict.persistent_jio.createJio({
        type: "indexeddb",
        database: "jabberclient"
      });
    })

    .declareMethod('get', function (id) {
      if (id === 'CONNECTION') {
        return {
          server: this.state_parameter_dict.server,
          jid: this.state_parameter_dict.jid,
          passwd: this.state_parameter_dict.passwd
        };
      }
      throw new Error('Unsupported get: ' + id);
    })

    .declareMethod('put', function (id, data) {
      if (id === 'CONNECTION') {
        return initConnectionGadget(this, data);
      }
      if (id === 'SUBSCRIBE') {
        return this.getDeclaredGadget(CONNECTION_GADGET_SCOPE)
          .push(function (connection_gadget) {
            return connection_gadget.requestSubscribe(data.jid);
          });
      }
      if (id === 'PASSWORD') {
        return this.getDeclaredGadget(CONNECTION_GADGET_SCOPE)
          .push(function (connection_gadget) {
            return connection_gadget.resetPassword(data.server, data.new_passwd);
          });
      }
      throw new Error('Unsupported put: ' + id);
    })

    .declareMethod('allDocs', function (options) {
      if (!this.state_parameter_dict.connected) {
        return this.redirect({command: 'display', options: {page: 'jabberclient_connect'}});
      }
      return this.state_parameter_dict.volatile_jio.allDocs(options);
    })

    .declareMethod('getAttachment', function (id, name, options) {
      var gadget = this,
        result;
      if (!this.state_parameter_dict.connected) {
        return this.redirect({command: 'display', options: {page: 'jabberclient_connect'}});
      }
      if (name === 'enclosure') {
        return getLog(this, id, options)
          .push(function (text) {
            result = text;
            return initializeContact(gadget, id);
          })
          .push(function (doc) {
            doc.notification = false;
            return gadget.state_parameter_dict.volatile_jio.put(id, doc);
          })
          .push(function () {
            return result;
          });
      }
      throw new Error('Unsupported getAttachment: ' + id + ' ' + name);
    })

    .declareMethod('putAttachment', function (id, name, blob) {
      var gadget = this;
      if (!this.state_parameter_dict.connected) {
        return this.redirect({command: 'display', options: {page: 'jabberclient_connect'}});
      }
      if (name === 'MESSAGE') {
        return this.getDeclaredGadget(CONNECTION_GADGET_SCOPE)
          .push(function (connection_gadget) {
            return connection_gadget.sendMessage(id, blob);
          })
          .push(function () {
            return addLog(gadget, id, blob, false);
          });
      }
      throw new Error('Unsupported putAttachment: ' + id + ' ' + name);
    })

    .declareService(function () {
      // queue for addLog
      var context = this;

      context.props.service_queue = new RSVP.Queue();
      enqueueDefer(context);

      return new RSVP.Queue()
        .push(function () {
          return context.props.service_queue;
        })
        .push(function () {
          throw new Error("Service should not have been stopped!");
        });
    })

    .declareService(function () {
      return loopEventListener(
        window,
        'focus',
        false,
        dropNotification
      );
    });

}(window, rJS, RSVP, jIO, document, loopEventListener));