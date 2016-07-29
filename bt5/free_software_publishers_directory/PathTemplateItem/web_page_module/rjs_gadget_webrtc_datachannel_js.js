/*jslint indent: 2*/
/*global rJS, RSVP, window*/
(function (rJS, window, RSVP) {
  "use strict";

  var connection_options = [
      {
        // No need for stun server on the same lan / ipv6
        iceServers: []
      },
      {
        'optional': [{DtlsSrtpKeyAgreement: true}]
      }
    ],
    data_channel_options = {reliable: true},
    offer_contraints = {
      mandatory: {
        OfferToReceiveAudio: false,
        OfferToReceiveVideo: false
      }
    };

  rJS(window)
    .ready(function (g) {
      g.props = {};
      return g.getDeclaredGadget('webrtc')
        .push(function (gadget) {
          g.props.webrtc = gadget;
          g.props.description_defer = RSVP.defer();
          g.props.channel_defer = RSVP.defer();
        });
    })

    .allowPublicAcquisition("notifyDescriptionCalculated", function (args) {
      this.props.description_defer.resolve(args[0]);
    })

    .allowPublicAcquisition("notifyDataChannelOpened", function () {
      this.props.channel_defer.resolve();
    })

    .declareMethod('createOffer', function (title) {
      var gadget = this,
        webrtc = this.props.webrtc;
      return webrtc.createConnection.apply(webrtc, connection_options)
        .push(function () {
          return webrtc.createDataChannel(title, data_channel_options);
        })
        .push(function () {
          return webrtc.createOffer(offer_contraints);
        })
        .push(function (local_description) {
          return webrtc.setLocalDescription(local_description);
        })
        .push(function () {
          return gadget.props.description_defer.promise;
        });
    })

    .declareMethod('registerAnswer', function (description) {
      var gadget = this;
      return gadget.props.webrtc.setRemoteDescription(description)
        .push(function () {
          return gadget.props.channel_defer.promise;
        });
    })

    .declareMethod('createAnswer', function (title, description) {
      var gadget = this,
        webrtc = this.props.webrtc;
      return webrtc.createConnection.apply(webrtc, connection_options)
        .push(function () {
          return webrtc.setRemoteDescription(description);
        })
        .push(function () {
          return webrtc.createAnswer(offer_contraints);
        })
        .push(function (local_description) {
          return webrtc.setLocalDescription(local_description);
        })
        .push(function () {
          return gadget.props.description_defer.promise;
        });
    })

    .declareMethod('waitForConnection', function () {
      return this.props.channel_defer.promise;
    })

    .declareMethod('send', function () {
      var webrtc = this.props.webrtc;
      return webrtc.send.apply(
        webrtc,
        arguments
      );
    });

}(rJS, window, RSVP));
