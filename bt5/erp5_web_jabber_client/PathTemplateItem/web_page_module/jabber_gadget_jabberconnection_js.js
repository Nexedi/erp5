/*global window, rJS, Strophe, $iq, $pres, $msg, RSVP*/
/*jslint indent: 2, maxerr: 3, nomen: true */

(function (window, rJS, Strophe, $iq, $pres, $msg, RSVP) {
  "use strict";

//   Strophe.log = function (level, msg) {
//     console.log("STROPHE (" + level + "):" + msg);
//   };
  Strophe.Bosh.prototype._hitError = function (reqStatus) {
    if (typeof this.errors !== 'number') {
      this.errors = 0;
    }
    this.errors += 1;
    Strophe.warn("request errored, status: " + reqStatus +
                 ", number of errors: " + this.errors);
    if (this.errors > 2) {
      this._onDisconnectTimeout();
      this._conn._changeConnectStatus(
        Strophe.Status.ERROR,
        "request error: " + reqStatus
      );
    }
  };

  var gadget_klass = rJS(window);

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

  function deferOnMessageStanza(message) {
    var gadget = this;
    enqueueDefer(gadget, function () {

      var to = Strophe.getBareJidFromJid(message.getAttribute('to')),
        from = Strophe.getBareJidFromJid(message.getAttribute('from')),
        type = message.getAttribute('type'),
        body = message.querySelector('body');

      if (type !== "chat") {
        throw new Error("Unsupported message type: " + type);
      }
      if (to !== Strophe.getBareJidFromJid(gadget.props.connection.jid)) {
        throw new Error("Expected message to: " + to);
      }
      if (body !== null) {
        return gadget.notifyXMPPMessageTextReceived(from, to,
                                                    body.textContent);
      }
    });
    return true;
  }

  function deferOnPresenceStanza(presence) {
    var gadget = this;
    enqueueDefer(gadget, function () {

      var to = Strophe.getBareJidFromJid(presence.getAttribute('to')),
        from = Strophe.getBareJidFromJid(presence.getAttribute('from')),
        type = presence.getAttribute('type');

      if (to !== Strophe.getBareJidFromJid(gadget.props.connection.jid)) {
        throw new Error("Expected presence to: " + to);
      }
      if (type === "subscribe") {
        return gadget.notifyXMPPSubscribe(from, to);
      }
      if (type === "unsubscribe") {
        return gadget.notifyXMPPUnsubscribe(from, to);
      }
      if (from !== to) {
        return gadget.notifyXMPPPresence(from, to, type);
      }

    });
    return true;
  }

  function deferServerConnectionNotification(gadget, status) {
    enqueueDefer(gadget, function () {
      var result;
      if (status === Strophe.Status.CONNECTING) {
        result = gadget.notifyXMPPConnecting();
      } else if (status === Strophe.Status.CONNFAIL) {
        result = gadget.notifyXMPPConnectingFail();
      } else if (status === Strophe.Status.AUTHENTICATING) {
        result = gadget.notifyXMPPAuthenticating();
      } else if (status === Strophe.Status.AUTHFAIL) {
        result = gadget.notifyXMPPAuthenticatingFailed();
      } else if (status === Strophe.Status.CONNECTED) {
        result = gadget.notifyXMPPConnected();
      } else if (status === Strophe.Status.DISCONNECTED) {
        result = gadget.notifyXMPPDisconnected();
      } else if (status === Strophe.Status.DISCONNECTING) {
        result = gadget.notifyXMPPDisconnecting();
      } else if (status === Strophe.Status.ATTACHED) {
        result = gadget.notifyXMPPAttached();
      } else {
        if (status === Strophe.Status.ERROR) {
          result = gadget.notifyXMPPConnectionError();
        }
        result = gadget.notifyXMPPError(status);
      }
      return result;
    });
  }

  function deferServerDisconnection(gadget) {
    enqueueDefer(gadget, function () {
      // Try to auto connection
      if (gadget.props.connection !== undefined) {
        gadget.props.connection.disconnect();
        delete gadget.props.connection;
      }
    });
  }

  function deferServerConnection(gadget) {
    deferServerDisconnection(gadget);

    function handleConnectionCallback(status) {
      return deferServerConnectionNotification(gadget, status);
    }

    enqueueDefer(gadget, function () {
      // Try to auto connection
      if (gadget.props.server !== undefined) {
        gadget.props.connection = new Strophe.Connection(gadget.props.server);

//         gadget.props.connection.rawInput = function (data) {
//           console.log("RECEIVING SOMETHING");
//           console.log(data);
//         };
//         gadget.props.connection.rawOutput = function (data) {
//           console.log("SENDING SOMETHING");
//           console.log(data);
//         };

        gadget.props.connection.connect(
          gadget.props.jid,
          gadget.props.passwd,
          handleConnectionCallback
        );
        gadget.props.connection.addHandler(
          deferOnPresenceStanza.bind(gadget),
          null,
          "presence"
        );
        gadget.props.connection.addHandler(
          deferOnMessageStanza.bind(gadget),
          null,
          "message",
          "chat"
        );

      }
    });
  }

  gadget_klass

    .ready(function (g) {
      g.props = {};
    })

    .declareAcquiredMethod('notifyXMPPConnecting',
                           'notifyXMPPConnecting')
    .declareAcquiredMethod('notifyXMPPConnectingFail',
                           'notifyXMPPConnectingFail')
    .declareAcquiredMethod('notifyXMPPAuthenticating',
                           'notifyXMPPAuthenticating')
    .declareAcquiredMethod('notifyXMPPAuthenticatingFailed',
                           'notifyXMPPAuthenticatingFailed')
    .declareAcquiredMethod('notifyXMPPConnected',
                           'notifyXMPPConnected')
    .declareAcquiredMethod('notifyXMPPDisconnected',
                           'notifyXMPPDisconnected')
    .declareAcquiredMethod('notifyXMPPDisconnecting',
                           'notifyXMPPDisconnecting')
    .declareAcquiredMethod('notifyXMPPConnectionError',
                           'notifyXMPPConnectionError')
    .declareAcquiredMethod('notifyXMPPError',
                           'notifyXMPPError')
    .declareAcquiredMethod('notifyXMPPAttached',
                           'notifyXMPPAttached')
    .declareAcquiredMethod('notifyXMPPMessageTextReceived',
                           'notifyXMPPMessageTextReceived')
    .declareAcquiredMethod('notifyXMPPSubscribe',
                           'notifyXMPPSubscribe')
    .declareAcquiredMethod('notifyXMPPUnsubscribe',
                           'notifyXMPPUnsubscribe')
    .declareAcquiredMethod('notifyXMPPPresence',
                           'notifyXMPPPresence')

    .declareService(function () {
      /////////////////////////
      // Handle XMPP connection
      /////////////////////////
      var context = this;

      context.props.service_queue = new RSVP.Queue();
      deferServerConnection(context);

      return new RSVP.Queue()
        .push(function () {
          return context.props.service_queue;
        })
        .push(function () {
          // XXX Handle cancellation
          throw new Error("Service should not have been stopped!");
        })
        .push(undefined, function (error) {
          // Always disconnect in case of error
          if (context.props.connection !== undefined) {
            context.props.connection.disconnect();
          }
          throw error;
        });
    })

    .declareMethod('connect',
                   function (server, jid, passwd) {
        this.props.server = server;
        this.props.jid = jid;
        this.props.passwd = passwd;
        deferServerConnection(this);
      })

    .declareMethod('fetchRoster', function () {
      var defer = RSVP.defer();
      function jsonifyResponse(domElt) {
        try {
          var result = [],
            elt,
            json_elt,
            len,
            i,
            len2,
            j,
            item_list = domElt.querySelectorAll("item");
          len = item_list.length;
          for (i = 0; i < len; i += 1) {
            elt = item_list[i];
            len2 = elt.attributes.length;
            json_elt = {};
            for (j = 0; j < len2; j += 1) {
              json_elt[elt.attributes[j].name] = elt.attributes[j].value;
            }
            result.push(json_elt);
          }
          defer.resolve(result);
        } catch (error) {
          defer.reject(error);
        }
      }
      this.props.connection.sendIQ(
        $iq({type: "get"}).c("query", {xmlns: Strophe.NS.ROSTER}),
        jsonifyResponse,
        defer.reject
      );
      return defer.promise;
    })

    .declareMethod('resetPassword', function (server, new_passwd) {
      var defer = RSVP.defer(),
        uid;
      function jsonifyResponse(domElt) {
        try {
          var result = [],
            type = domElt.getAttribute('type');
          if (type === "result") {
            result.push("Password Reset Success.");
          } else {
            throw new Error("Password Reset Failure.");
          }
          defer.resolve(result);
        } catch (error) {
          defer.reject(error);
        }
      }
      uid = this.props.jid.split('@')[0];
      this.props.connection.sendIQ(
        $iq({to: server, type: "set"})
          .c("query", {xmlns: "jabber:iq:register"})
          .c("username").t(uid).up()
          .c("password").t(new_passwd).up(),
        jsonifyResponse,
        defer.reject
      );
      return defer.promise;
    })
    .declareMethod('sendPresence', function () {
      this.props.connection.send(
        $pres().tree()
      );
    })

    .declareMethod('requestSubscribe', function (jid) {
      this.props.connection.send(
        $pres({to: jid, type: "subscribe"}).tree()
      );
    })

    .declareMethod('acceptSubscription', function (jid) {
      this.props.connection.send(
        $pres({to: jid, type: "subscribed"}).tree()
      );
    })

    .declareMethod('requestUnsubscribe', function (jid) {
      this.props.connection.send(
        $pres({to: jid, type: "unsubscribe"}).tree()
      );
    })

    .declareMethod('acceptUnsubscription', function (jid) {
      this.props.connection.send(
        $pres({to: jid, type: "unsubscribed"}).tree()
      );
    })

    .declareMethod('sendMessage', function (jid, text) {
      this.props.connection.send(
        $msg({to: jid, type: "chat"}).c('body').t(text)
      );
    });

}(window, rJS, Strophe, $iq, $pres, $msg, RSVP));