/*global window, rJS, document, RSVP, console, DOMException */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS, document, RSVP, console, DOMException) {
  "use strict";

  function dropSubGadget(gadget, scope) {
    return gadget.getDeclaredGadget(scope)
      .push(function (result) {
        return result.getElement();
      })
      .push(function (element) {
        if (element.parentElement) {
          element.parentElement.removeChild(element);
        }
        delete gadget.state_parameter_dict.scope_ip[scope];
        return gadget.dropGadget(scope);
      });
  }

  function getWebRTCScopeList(gadget) {
    var result_list = [],
      element_list = gadget.state_parameter_dict.element.querySelector(".gadget_webrtc_datachannel")
                                                        .childNodes,
      i;
    for (i = 0; i < element_list.length; i += 1) {
      result_list.push(element_list[i].getAttribute("data-gadget-scope"));
    }
    return result_list;
  }

  function updateInfo(gadget) {
    var scope_list = getWebRTCScopeList(gadget),
      i,
      result = "";
    for (i = 0; i < scope_list.length; i += 1) {
      result += gadget.state_parameter_dict.scope_ip[scope_list[i]] + "\n";
    }
    gadget.state_parameter_dict.element.querySelector(".info").textContent = result;
    gadget.state_parameter_dict.element.querySelector(".peer_count").textContent = i;
  }

  function sendWebRTC(gadget, rtc_gadget, scope, message) {
    return rtc_gadget.send(message)
      .push(undefined, function (error) {
        if ((error instanceof DOMException) && (error.name === 'InvalidStateError')) {
          return dropSubGadget(gadget, scope)
            .push(function () {
              return updateInfo(gadget);
            }, function (error) {
              console.log("-- Can not drop remote subgadget " + scope);
              console.log(error);
              return;
            });
        }
        throw error;
      });
  }

  rJS(window)

    .ready(function (gadget) {
      // Initialize the gadget local parameters
      gadget.state_parameter_dict = {
        websocket_initialized: false,
        counter: 0,
        connecting: false,
        scope_ip: {}
      };
      return gadget.getElement()
        .push(function (element) {
          gadget.state_parameter_dict.element = element;
        })
        .push(function () {
          return updateInfo(gadget);
        });
    })

    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("jio_post", "jio_post")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_repair", "jio_repair")

    .allowPublicAcquisition('notifyDataChannelClosed', function (argument_list, scope) {
      /*jslint unparam:true*/
      var gadget = this;
      return dropSubGadget(this, scope)
        .push(function () {
          return updateInfo(gadget);
        });
    })

    .allowPublicAcquisition("notifyDataChannelMessage", function (argument_list, scope) {
      var json = JSON.parse(argument_list[0]),
        rtc_gadget,
        context = this;
      return context.getDeclaredGadget(scope)
        .push(function (g) {
          rtc_gadget = g;
          // Call jio API
          return context["jio_" + json.method_name].apply(context, json.argument_list);
        })
        .push(function (result) {
          return sendWebRTC(context, rtc_gadget, scope, JSON.stringify({
            id: json.id,
            result: result,
            type: "jio_response"
          }));
        }, function (error) {
          return sendWebRTC(context, rtc_gadget, scope, JSON.stringify({
            id: json.id,
            result: error,
            type: "error"
          }));
        });
    })
/*
    .allowPublicAcquisition("notifyWebSocketClosed", function () {
      if (this.state_parameter_dict.user_type !== "user") {
        throw new Error("Unexpected Web Socket connection close");
      }
    })
*/
    .allowPublicAcquisition("notifyWebSocketMessage", function (argument_list) {
      var json = JSON.parse(argument_list[0]),
        scope,
        rtc_gadget,
        socket_gadget,
        gadget = this;

      if (json.action === "offer") {
        // XXX https://github.com/diafygi/webrtc-ips
        return gadget.getDeclaredGadget("gadget_websocket.html")
          .push(function (gg) {
            gadget.state_parameter_dict.connecting = true;
            gadget.state_parameter_dict.counter += 1;
            socket_gadget = gg;
            var new_element = document.createElement("div");
            gadget.state_parameter_dict.element.querySelector(".gadget_webrtc_datachannel").appendChild(new_element);
            scope = "webrtc" + gadget.state_parameter_dict.counter;
            return gadget.declareGadget("gadget_webrtc_datachannel.html", {
              scope: scope,
              element: new_element
            });
          })
          .push(function (gg) {
            rtc_gadget = gg;
            // https://github.com/diafygi/webrtc-ips
            var ip_regex = /([0-9]{1,3}(\.[0-9]{1,3}){3}|[a-f0-9]{1,4}(:[a-f0-9]{1,4}){7})/,
              ip_list = [],
              ip_dict = {},
              ip_addr,
              line_list = JSON.parse(json.data).sdp.split('\n'),
              i;
            for (i = 0; i < line_list.length; i += 1) {
              if (line_list[i].indexOf('a=candidate:') === 0) {
                ip_addr = ip_regex.exec(line_list[i])[1];
                if (!ip_addr.match(/^[a-f0-9]{1,4}(:[a-f0-9]{1,4}){7}$/)) {
                  // Hide ipv6
                  if (!ip_dict[ip_addr]) {
                    ip_list.push(ip_addr);
                    ip_dict[ip_addr] = true;
                  }
                }
              }
            }
            gadget.state_parameter_dict.scope_ip[scope] = ip_list;
            return rtc_gadget.createAnswer(json.from, json.data);
          })
          .push(function (local_connection) {
            return socket_gadget.send(JSON.stringify({to: json.from, action: "answer", data: local_connection}));
          })
          .push(function () {
            return RSVP.any([
              RSVP.Queue()
                .push(function () {
                  return RSVP.delay(10000);
                })
                .push(function () {
                  console.info('-- webrtc client disappears...');
                  return dropSubGadget(gadget, scope);
                }),
              rtc_gadget.waitForConnection()
            ]);
          })
          .push(function () {
            gadget.state_parameter_dict.connecting = false;
            return updateInfo(gadget);
          });
      }
    })

    .declareService(function () {
      var sgadget,
        gadget = this;
      return this.getDeclaredGadget('gadget_websocket.html')
        .push(function (socket_gadget) {
          sgadget = socket_gadget;
          return socket_gadget.createSocket("ws://127.0.0.1:9999/");
        })
        .push(function () {
          // Wait for the gadget to be dropped from the page
          // and close the socket/rtc connections
          return RSVP.defer().promise;
        })
        .push(undefined, function (error) {
          if (sgadget === undefined) {
            return;
          }
          return sgadget.close()
            .push(function () {
              var scope_list = getWebRTCScopeList(gadget),
                i,
                promise_list = [];

              function close(scope) {
                return gadget.getDeclaredGadget(scope)
                  .push(function (rtc_gadget) {
                    return rtc_gadget.close();
                  });
              }

              for (i = 0; i < scope_list.length; i += 1) {
                promise_list.push(close(scope_list[i]));
              }
              return RSVP.all(promise_list);
            })
            .push(function () {
              throw error;
            });
        });
    });

}(window, rJS, document, RSVP, console, DOMException));