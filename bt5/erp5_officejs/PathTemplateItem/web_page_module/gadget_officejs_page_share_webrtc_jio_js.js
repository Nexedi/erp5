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

  function getWebRTCScopeList(gadget) {
    var result_list = [],
      element_list = gadget.state_parameter_dict.element.querySelector(".gadget_webrtc")
                                                        .childNodes,
      i;
    for (i = 0; i < element_list.length; i += 1) {
      if (element_list[i].getAttribute) {
        result_list.push(element_list[i].getAttribute("data-gadget-scope"));
      }
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
    return rtc_gadget.send(message, "webrtc"+gadget.state_parameter_dict.counter)
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

    .declareMethod("onOffer", function (options, offer) {
      var gadget = this;
      gadget.state_parameter_dict.counter += 1;
      return new RSVP.Queue()
      .push(function(response) {
        gadget.connecting = true;

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

        gadget.state_parameter_dict.scope_ip["webrtc"+gadget.state_parameter_dict.counter] = ip_list
        options.to = offer.from; 
        return;
      })
    })
      
    .declareMethod('postConnection', function(options, offer) {
      var gadget = this;

      return new RSVP.Queue()
      .push(function () {
        gadget.state_parameter_dict.connecting = false;
        return updateInfo(gadget);
      });
    })

    .declareMethod('initiate', function (roomid) {
      var gadget = this,
        options = {
          peerid: "master",
          roomid: "/"+roomid+"/",
          type: "websocket",
          config: {'url': "ws://127.0.0.1:9999/"},
          listner: true,
          preConnection: gadget.onOffer.bind(gadget),
          postConnection: gadget.postConnection.bind(gadget),
        };
        
      return gadget.getDeclaredGadget("gadget_webrtc_jio_bridge.html")
        .push(function (rtc_gadget) {
          options.rtc_gadget = rtc_gadget;
          return rtc_gadget.connect(options);
        });

        /*.push(undefined, function (error) {
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
        }); */
    });

}(window, rJS, document, RSVP, console, DOMException));