/*global window, rJS, FormData, document, RSVP, console */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS) {
  "use strict";

  var timeout = 10000;

  function S4() {
    return ('0000' + Math.floor(
      Math.random() * 0x10000 /* 65536 */
    ).toString(16)).slice(-4);
  }

  function UUID() {
    return S4() + S4() + "-" +
      S4() + "-" +
      S4() + "-" +
      S4() + "-" +
      S4() + S4() + S4();
  }

  function wrapManagerJioAccess(gadget, method_name, argument_list) {
    return gadget.getDeclaredGadget('jio_gadget')
      .push(function (jio_gadget) {
        return jio_gadget[method_name].apply(jio_gadget, argument_list);
      });
  }

  function wrapJioAccess(gadget, method_name, argument_list) {
    if (gadget.state_parameter_dict.user_type === "manager") {
      return wrapManagerJioAccess(gadget, method_name, argument_list);
    }
    if (gadget.state_parameter_dict.user_type === "user") {
      return gadget.getDeclaredGadget('gadget_webrtc_datachannel.html')
        .push(function (rtc_gadget) {
          gadget.state_parameter_dict.message_count += 1;
          gadget.state_parameter_dict.message_dict[gadget.state_parameter_dict.message_count] = RSVP.defer();
          return RSVP.all([
            rtc_gadget.send(JSON.stringify({
              id: gadget.state_parameter_dict.message_count,
              type: "jio_query",
              method_name: method_name,
              argument_list: Array.prototype.slice.call(argument_list)
            })),
            RSVP.any([
              RSVP.timeout(timeout),
              gadget.state_parameter_dict.message_dict[gadget.state_parameter_dict.message_count].promise
            ])
          ]);
        })
        .push(function (result_list) {
          return result_list[1];
        });
    }

    throw new Error("NotImplemented wrapJioAccess for: " + gadget.state_parameter_dict.user_type);
  }

  function declareSubGadget(gadget, url) {
    var container_element = gadget.state_parameter_dict.element.querySelector("." + url.split(".")[0]),
      element = document.createElement("div");
    container_element.innerHTML = "";
    container_element.appendChild(element);
    return gadget.declareGadget(url, {
      element: element,
      scope: url,
      sandbox: "public"
    });
  }

  rJS(window)

    .ready(function (gadget) {
      // Initialize the gadget local parameters
      gadget.state_parameter_dict = {
        websocket_initialized: false,
        user_type: null
      };
      return gadget.getElement()
        .push(function (element) {
          gadget.state_parameter_dict.element = element;
        });
    })

    .allowPublicAcquisition('notifyDataChannelClosed', function () {
      return;
    })

    .allowPublicAcquisition("notifyDataChannelMessage", function (argument_list, scope) {
      var json = JSON.parse(argument_list[0]),
        rtc_gadget,
        context = this;
      if (context.state_parameter_dict.user_type === "manager") {
        return context.getDeclaredGadget(scope)
          .push(function (g) {
            rtc_gadget = g;
            // XXX Propagate arguments
            return wrapManagerJioAccess(context, json.method_name, json.argument_list);
          })
          .push(function (result) {
            return rtc_gadget.send(JSON.stringify({
              id: json.id,
              result: result,
              type: "jio_response"
            }));
          }, function (error) {
            return rtc_gadget.send(JSON.stringify({
              id: json.id,
              result: error,
              type: "error"
            }));
          });
      }
      if (context.state_parameter_dict.user_type === "user") {
        if (json.type === "jio_response") {
          context.state_parameter_dict.message_dict[json.id].resolve(json.result);
        } else {
          context.state_parameter_dict.message_dict[json.id].reject(json.result);
        }
      } else {
        throw new Error("Unexpected WebRTC message");
      }
    })

    .allowPublicAcquisition("notifyWebSocketClosed", function () {
      if (this.state_parameter_dict.user_type !== "user") {
        throw new Error("Unexpected Web Socket connection close");
      }
    })

    .allowPublicAcquisition("notifyWebSocketMessage", function (argument_list) {

      var json = JSON.parse(argument_list[0]),
        rtc_gadget,
        socket_gadget,
        gadget = this;

      if ((json.action === "offer") && (gadget.state_parameter_dict.user_type === "manager")) {
        return gadget.getDeclaredGadget("gadget_websocket.html")
          .push(function (gg) {
            gadget.state_parameter_dict.counter += 1;
            socket_gadget = gg;
            var new_element = document.createElement("div");
            gadget.state_parameter_dict.element.querySelector(".gadget_webrtc_datachannel").appendChild(new_element);
            return gadget.declareGadget("gadget_webrtc_datachannel.html", {
              scope: "webrtc" + gadget.state_parameter_dict.counter,
              element: new_element
            });
          })
          .push(function (gg) {
            rtc_gadget = gg;
            return rtc_gadget.createAnswer(json.from, json.data);
          })
          .push(function (local_connection) {
            return socket_gadget.send(JSON.stringify({to: json.from, action: "answer", data: local_connection}));
          })
          .push(function () {
            return rtc_gadget.waitForConnection();
          })
          .push(undefined, function (error) {
            console.error(error);
            throw error;
          });
      }

      if ((json.action === "answer") && (gadget.state_parameter_dict.user_type === "user")) {
        if (json.to === gadget.state_parameter_dict.uuid) {
          gadget.state_parameter_dict.answer_defer.resolve(json.data);
        }
      }

    })

    .declareMethod('createJio', function (jio_options) {
      var context = this,
        socket_gadget,
        rtc_gadget;

      return declareSubGadget(context, 'gadget_websocket.html')
        .push(function (gadget) {
          socket_gadget = gadget;
          // Check if this is a manager access
          return socket_gadget.createSocket("ws://127.0.0.1:9999/")
            .push(function () {
              // Nothing to do except waiting for new webrtc offer
              context.state_parameter_dict.user_type = "manager";
              context.state_parameter_dict.counter = 0;
              return context.getDeclaredGadget('jio_gadget')
                .push(function (jio_gadget) {
                  return jio_gadget.createJio(jio_options);
                });
            }, function () {
              // XXX Catch right type of error
              context.state_parameter_dict.user_type = "user";
              context.state_parameter_dict.uuid = UUID();
              context.state_parameter_dict.answer_defer = RSVP.defer();
              context.state_parameter_dict.message_count = 0;
              context.state_parameter_dict.message_dict = {};
              return declareSubGadget(context, 'gadget_websocket.html')
                .push(function (gadget) {
                  socket_gadget = gadget;
                  // XXX Drop hardcoded URL
                  return socket_gadget.createSocket("ws://192.168.242.76:9999/");
                })
                .push(function () {
                  return declareSubGadget(context, 'gadget_webrtc_datachannel.html');
                })
                .push(function (gadget) {
                  rtc_gadget = gadget;
                  return rtc_gadget.createOffer(context.state_parameter_dict.uuid);
                })
                .push(function (description) {
                  // Send offer and expect answer in less than XXXms (arbitrary value...)
                  return RSVP.any([
                    RSVP.timeout(timeout),
                    RSVP.all([
                      socket_gadget.send(JSON.stringify({from: context.state_parameter_dict.uuid, action: "offer", data: description})),
                      context.state_parameter_dict.answer_defer.promise
                    ])
                  ]);
                })
                .push(function (response_list) {
                  return rtc_gadget.registerAnswer(response_list[1]);
                })
                .push(function () {
                  return socket_gadget.close();
                });
            });
        });
    })
    .declareMethod('allDocs', function () {
      return wrapJioAccess(this, 'allDocs', arguments);
    })
    .declareMethod('get', function () {
      return wrapJioAccess(this, 'get', arguments);
    })
    .declareMethod('put', function () {
      return wrapJioAccess(this, 'put', arguments);
    })
    .declareMethod('post', function () {
      return wrapJioAccess(this, 'post', arguments);
    })
    .declareMethod('remove', function () {
      return wrapJioAccess(this, 'remove', arguments);
    })
    /*
    .declareMethod('allAttachments', function () {
      return wrapJioAccess(this, 'allAttachments', arguments);
    })
    .declareMethod('getAttachment', function () {
      return wrapJioAccess(this, 'getAttachment', arguments);
    })
    .declareMethod('putAttachment', function () {
      return wrapJioAccess(this, 'putAttachment', arguments);
    })
    .declareMethod('removeAttachment', function () {
      return wrapJioAccess(this, 'removeAttachment', arguments);
    })
    */
    .declareMethod('repair', function () {
      return wrapJioAccess(this, 'repair', arguments);
    });

}(window, rJS));