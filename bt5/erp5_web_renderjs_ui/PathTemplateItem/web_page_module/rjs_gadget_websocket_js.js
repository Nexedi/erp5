/*jslint indent: 2*/
/*global rJS, window, WebSocket, RSVP*/
(function (rJS, window, WebSocket, RSVP) {
  "use strict";

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

  function deferOnClose() {
    var gadget = this;
    enqueueDefer(gadget, function () {
      return gadget.notifyWebSocketClosed();
    });
  }

  function deferOnOpen() {
    var gadget = this;
    enqueueDefer(gadget, function () {
      gadget.props.socket_defer.resolve();
//       return gadget.notifyWebSocketOpened();
    });
  }

  function deferOnMessage(evt) {
    var gadget = this;
    enqueueDefer(gadget, function () {
      return gadget.notifyWebSocketMessage(evt.data);
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

  function deferErrorHandler(error) {
    if ((!this.props.socket_defer.isFulfilled) && (!this.props.socket_defer.isRejected)) {
      this.props.socket_defer.reject(error);
    } else {
      enqueueDefer(this, function () {
        throw error;
      });
    }
  }

  function deferServerConnection(gadget) {
    deferServerDisconnection(gadget);

  }


  rJS(window)
    .ready(function (g) {
      g.props = {};
    })

    .declareAcquiredMethod('notifyWebSocketClosed',
                           'notifyWebSocketClosed')
    .declareAcquiredMethod('notifyWebSocketMessage',
                           'notifyWebSocketMessage')

    .declareService(function () {
      /////////////////////////
      // Handle WebSocket connection
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
            context.props.connection.close();
          }
          throw error;
        });
    })

    .declareMethod('createSocket', function (address) {
      // Improve to support multiple sockets?
      this.props.socket = new WebSocket(address);
      this.props.socket_defer = RSVP.defer();
      this.props.socket.addEventListener('open', deferOnOpen.bind(this));
      this.props.socket.addEventListener('close', deferOnClose.bind(this));
      this.props.socket.addEventListener('message', deferOnMessage.bind(this));
      this.props.socket.addEventListener('error', deferErrorHandler.bind(this));
      return this.props.socket_defer.promise;
    })

    .declareMethod('send', function (message) {
      this.props.socket.send(message);
    })

    .declareMethod('close', function () {
      if (this.props.socket === undefined) {
        return;
      }
      this.props.socket.close();
      delete this.props.socket;
    });

}(rJS, window, WebSocket, RSVP));
