/*jslint indent:2, maxlen:100, nomen:true*/
/*global rJS, RSVP, window*/

(function (rJS, window, RSVP) {
  "use strict";

  var connection_options = [
    {
      // No need for stun server on the same lan / ipv6
      iceServers: [
        {'url': 'stun:23.21.150.121'},
        {url: 'stun:stun.1.google.com:19302'}
      ]
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

  function declareSubGadget(gadget, url) {
    var container_element = gadget.props.element.querySelector("." + url.split(".")[0]),
      element = document.createElement("div");

    container_element.innerHTML = "";
    container_element.appendChild(element);
    return gadget.declareGadget(url, {
      element: element,
      scope: url,
      sandbox: "public"
    });
  }

  function dropSubGadget(gadget, scope) {
    return gadget.getDeclaredGadget(scope)
      .push(function (result) {
        return result.getElement();
      })
      .push(function (element) {
        if (element.parentElement) {
          element.parentElement.removeChild(element);
        }
        return gadget.dropGadget(scope);
      });
  }

  function createOffer(gadget, title) {
      var webrtc = gadget.props.webrtc_connections["webrtc" + gadget.props.counter];
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
    }

  function registerAnswer (gadget, description) {
    return gadget.props.webrtc_connections["webrtc" + gadget.props.counter]
      .setRemoteDescription(description)
      .push(function () {
        return gadget.props.channel_defer.promise;
      });
  }

  function createAnswer(gadget, description) {
    var webrtc = gadget.props.webrtc_connections["webrtc" + gadget.props.counter];

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
  }

  function waitForConnection (gadget) {
    return gadget.props.channel_defer.promise;
  }

  function handleConnection(gadget, handler_gadget, options, offer) {
    // create a new webrtc gadget instance
    var new_element = document.createElement("div");
    gadget.props.element.querySelector(".gadget_webrtc").appendChild(new_element);
    var scope = "webrtc" + gadget.props.counter;
    return gadget.declareGadget("gadget_webrtc.html", {
      scope: scope,
      element: new_element
    })
    .push(function(webrtc_gadget) {
      gadget.props.webrtc_connections[scope] = webrtc_gadget;
      if (options.initiator === true) {
        return createOffer(gadget, options.peerid)
        .push(function (description) {
          var params = {'name': options.to+'_'+options.peerid,
                        'data' : new Blob([JSON.stringify({ from: options.peerid,
                                                            action: "offer",
                                                            data: description})],
                                          {type : "application/json"})};
          return handler_gadget.handle_offer_answer(options.roomid, params);
        })
        .push(function(){
          return handler_gadget.wait_until_available(options.roomid, options.peerid+'_',
            function(response){
              return registerAnswer(gadget, JSON.parse(response).data)
              .push(function () {
                return handler_gadget.close(options.roomid,
                                            options.peerid,
                                            options.to,
                                            options.listner);
              })
              .push(function () {
                return false;
              });
            });
        });
      } else {
        if (!offer.data) {
          throw new Error("No offer provided in connect function");
        }
        return createAnswer(gadget, offer.data)
        .push(function (answer) {
          var params = {name: options.to+'_'+options.peerid,
                        data: new Blob([JSON.stringify({ to: options.to,
                                                         action: "answer",
                                                         data: answer})],
                                        {type : "application/json"}) };
          return handler_gadget.handle_offer_answer(options.roomid, params);
        })
        .push(function () {
          return handler_gadget.close(options.roomid, options.peerid, options.to, options.listner);
        })
        .push(function(){
          return RSVP.any([
            RSVP.Queue()
            .push(function () {
              return RSVP.delay(20000);
            })
            .push(function () {
              console.info('-- webrtc client disappears...');
              return dropSubGadget(gadget, "webrtc"+gadget.props.counter);
            }),
            waitForConnection(gadget)
          ]);
        });
      }
    });
  }

  rJS(window)
    .ready(function (g) {
      g.props = {};
      g.props.description_defer = RSVP.defer();
      g.props.channel_defer = RSVP.defer();
      g.props.counter = 0;
      g.props.webrtc_connections = {};
      
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
        });
    })
    .declareAcquiredMethod("notifyDataChannelMessage", "notifyDataChannelMessage")

    .allowPublicAcquisition('notifyDataChannelClosed', function (argument_list, scope) {
      var gadget = this;
      return dropSubGadget(this, scope)
        .push(function () {
          return updateInfo(gadget);
        });
    })

    .allowPublicAcquisition("notifyDescriptionCalculated", function (args) {
      this.props.description_defer.resolve(args[0]);
      this.props.description_defer = RSVP.defer();
    })

    .allowPublicAcquisition("notifyDataChannelOpened", function () {
      this.props.channel_defer.resolve();
    })

    .declareMethod('send', function (args, to) {
      //TODO: Add sent-to by name, functionality here
      var webrtc = this.props.webrtc_connections[to];
      return webrtc.send.apply(
        webrtc,
        arguments
      );
    })

    .declareMethod('connect', function(options){
      var gadget = this,
        jsonOffer,
        handler,
        roomid = options.roomid,
        peerid = options.peerid;

      if (options.type === "websocket")  {
        handler = "websocket_handshake_gadget";
      } else if (options.type === "jio") {
        handler = "handshake_gadget";
      }

      gadget.props.handler_gadget = handler;

      return this.getDeclaredGadget(handler)
        .push(function (handler_gadget){
          return handler_gadget.register(options.roomid, options.peerid, options.config);
        })
        .push(function (){

          function connectCallback (offer, handler_gadget) {
            return RSVP.Queue()
            .push(function(){
              if (options.preConnection) {
                return options.preConnection(options, offer);
              } else {
                return;
              }
            })
            .push(function() {
              return handleConnection(gadget, handler_gadget, options, offer);
            })
            .push(function() {
              if (options.postConnection) {
                return options.postConnection(options, offer);
              } else {
                return;
              }
            });
          }

          if (gadget.props.handler_gadget)  {
            return gadget.getDeclaredGadget(gadget.props.handler_gadget)
            .push(function(handler_gadget) {
              if (options.listner) {
                return handler_gadget.wait_until_available(roomid, peerid+'_', function(offers){
                  var connections = [];
                  // TODO: have a array for channel_defer for concurency?
                  gadget.props.channel_defer = RSVP.defer();
                  for (var offer in offers) {
                    jsonOffer = JSON.parse(offers[offer]);
                    if (jsonOffer.action === "offer") {
                      gadget.props.counter += 1;
                      connections.push(connectCallback(jsonOffer, handler_gadget));
                    }
                  }
                  return RSVP.all(connections);
                });
              } else {
                return handleConnection(gadget, handler_gadget, options);
              }
            });
          } else {
            throw new Error("Peer is not registered");
          }
        });
    });
}(rJS, window, RSVP));