/*global window, rJS, document, RSVP, console, DOMException */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS, document, RSVP, console, DOMException) {
  "use strict";
  
  window.promiseDoWhile = function (loopFunction, input) {
    // calls loopFunction(input) until it returns a non positive value

    // this queue is to protect the inner loop queue from the
    // `promiseDoWhile` caller, avoiding it to enqueue the inner
    // loop queue.
    return new RSVP.Queue()
      .push(function () {
        // here is the inner loop queue
        var loop_queue = new RSVP.Queue();
        function iterate(previous_iteration_result) {
          if (!previous_iteration_result) {
            return input;
          }
          loop_queue.push(iterate);
          return loopFunction(input);
        }
        return loop_queue
          .push(function () {
            return loopFunction(input);
          })
          .push(iterate);
      });
  };

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
      element_list = gadget.state_parameter_dict.element.querySelector(".gadget_webrtc_jio_bridge")
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

    .declareMethod('connect', function(handshake_gadget, room_id, offer) {
      var gadget = this,
        scope,
        rtc_gadget;

      return new RSVP.Queue()
      .push(function(response) {
        gadget.state_parameter_dict.connecting = true;
        gadget.state_parameter_dict.counter += 1;

        var new_element = document.createElement("div");
        gadget.state_parameter_dict.element.querySelector(".gadget_webrtc_jio_bridge").appendChild(new_element);
        scope = "webrtc" + gadget.state_parameter_dict.counter;

        return gadget.declareGadget("gadget_webrtc_jio_bridge.html", {
          scope: scope,
          element: new_element
        })
        .push(function(gg){
          rtc_gadget = gg;
          // https://github.com/diafygi/webrtc-ips
          var ip_regex = /([0-9]{1,3}(\.[0-9]{1,3}){3}|[a-f0-9]{1,4}(:[a-f0-9]{1,4}){7})/,
            ip_list = [],
            ip_dict = {},
            ip_addr,
            line_list = JSON.parse(offer.data).sdp.split('\n'),
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
          return rtc_gadget.connect({ 
                                      roomid: room_id, 
                                      peerid: 'master', 
                                      to: offer.from, 
                                      offer: JSON.stringify(offer.data) 
                                    });
        })         
        .push(function () {
          return RSVP.any([
            RSVP.Queue()
              .push(function () {
                return RSVP.delay(20000);
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
      })
    })
    .declareMethod('initiate', function (roomid) {
      var gadget = this,
        handshake_gadget,
        rtc_gadget,
        blob;
      return this.getDeclaredGadget('gadget_handshake.html')
        .push(function (gad) {
          handshake_gadget = gad;
          roomid = "/"+roomid+"/";
          return handshake_gadget.create_room(roomid);
        })
        .push(function () {
          return gadget.declareGadget("gadget_webrtc_jio_bridge.html")
        })
        .push(function (rg) {
          // register peer
          rtc_gadget = rg;
          return rtc_gadget.register(roomid, 'master');
        })
        .push(function (r) {
          var peerid = 'master';
          return handshake_gadget.wait_until_available(roomid, peerid+'_', function (offers) {
            var connections = [];
            for (var offer in offers) {
              connections.push(gadget.connect(handshake_gadget, roomid, JSON.parse(offers[offer].target.result)));
            }
            return RSVP.all(connections);
          });
        });
    });

}(window, rJS, document, RSVP, console, DOMException));