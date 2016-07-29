/*jslint indent: 2*/
/*global rJS, RSVP, window*/
(function (rJS, RSVP, window) {
  "use strict";

  var RTCPeerConnection = window.RTCPeerConnection || window.mozRTCPeerConnection ||
                         window.webkitRTCPeerConnection || window.msRTCPeerConnection,
    RTCSessionDescription = window.RTCSessionDescription || window.mozRTCSessionDescription ||
                           window.webkitRTCSessionDescription || window.msRTCSessionDescription;

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

  function deferOnIceCandidate(candidate) {
    var gadget = this;
    enqueueDefer(gadget, function () {
      // Firing this callback with a null candidate indicates that
      // trickle ICE gathering has finished, and all the candidates
      // are now present in pc.localDescription.  Waiting until now
      // to create the answer saves us from having to send offer +
      // answer + iceCandidates separately.
      if (candidate.candidate === null) {
        return gadget.notifyDescriptionCalculated(JSON.stringify(gadget.props.connection.localDescription));
      }
    });
  }

  function deferDataChannelOnOpen() {
    var gadget = this;
    enqueueDefer(gadget, function () {
      return gadget.notifyDataChannelOpened();
    });
  }

  function deferDataChannelOnClose() {
    var gadget = this;
    enqueueDefer(gadget, function () {
      return gadget.notifyDataChannelClosed();
    });
  }

  function deferDataChannelOnMessage(evt) {
    var gadget = this;
    enqueueDefer(gadget, function () {
      return gadget.notifyDataChannelMessage(evt.data);
//         var data = JSON.parse(evt.data);
//         console.log(data.message);
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

//   function deferOfferSuccessCallback(description) {
//     var gadget = this;
//     enqueueDefer(gadget, function () {
//       gadget.props.connection.setLocalDescription(description);
//     });
//   }

  function deferErrorHandler(error) {
    enqueueDefer(this, function () {
      throw error;
    });
  }

  function deferServerConnection(gadget) {
    deferServerDisconnection(gadget);

  }

  function listenToChannelEvents(gadget) {
    gadget.props.channel.onopen = deferDataChannelOnOpen.bind(gadget);
    gadget.props.channel.onclose = deferDataChannelOnClose.bind(gadget);
    gadget.props.channel.onmessage = deferDataChannelOnMessage.bind(gadget);
    gadget.props.channel.onerror = deferErrorHandler.bind(gadget);
  }

  rJS(window)
    .ready(function (g) {
      g.props = {};
    })

    .declareAcquiredMethod('notifyDescriptionCalculated',
                           'notifyDescriptionCalculated')
    .declareAcquiredMethod('notifyDataChannelOpened',
                           'notifyDataChannelOpened')
    .declareAcquiredMethod('notifyDataChannelMessage',
                           'notifyDataChannelMessage')
    .declareAcquiredMethod('notifyDataChannelClosed',
                           'notifyDataChannelClosed')

    .declareService(function () {
      /////////////////////////
      // Handle WebRTC connection
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


    .declareMethod('createConnection', function (configuration, constraints) {
      this.props.connection = new RTCPeerConnection(configuration, constraints);
      this.props.connection.onicecandidate = deferOnIceCandidate.bind(this);
      var context = this;
      this.props.connection.ondatachannel = function (evt) {
        context.props.channel = evt.channel;
        listenToChannelEvents(context);
      };
    })

    .declareMethod('createDataChannel', function (title, options) {
      // XXX Improve to support multiple data channel
      this.props.channel = this.props.connection.createDataChannel(title, options);
      listenToChannelEvents(this);
      // console.log("Channel type: " + this.props.channel.binarytype);
    })

    .declareMethod('createOffer', function (constraints) {
      var gadget = this;
      return new RSVP.Promise(function (resolve, reject) {
        gadget.props.connection.createOffer(
          resolve,
          reject,
          constraints
        );
      });
    })

    .declareMethod('setRemoteDescription', function (description) {
      var gadget = this;
      return new RSVP.Promise(function (resolve, reject) {
        gadget.props.connection.setRemoteDescription(
          new RTCSessionDescription(JSON.parse(description)),
          resolve,
          reject
        );
      });
    })

    .declareMethod('setLocalDescription', function (description) {
      var gadget = this;
      return new RSVP.Promise(function (resolve, reject) {
        gadget.props.connection.setLocalDescription(
          new RTCSessionDescription(description),
          resolve,
          reject
        );
      });
    })

    .declareMethod('createAnswer', function (constraints) {
      var gadget = this;
      return new RSVP.Promise(function (resolve, reject) {
        gadget.props.connection.createAnswer(
          resolve,
          reject,
          constraints
        );
      });
    })

    .declareMethod('send', function (message) {
      this.props.channel.send(message);
    })

    .declareMethod('close', function () {
      // XXX Of course, this will fail if connection is not open yet...
      this.props.channel.close();
      this.props.connection.close();
      delete this.props.channel;
      delete this.props.connection;
    });

}(rJS, RSVP, window));
