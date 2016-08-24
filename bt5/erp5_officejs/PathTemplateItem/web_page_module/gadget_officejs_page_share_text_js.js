/*global window, rJS, document, RSVP, console, DOMException */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS, document, RSVP, console, DOMException) {
  "use strict";

  var timeout = 600000;

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
    console.log(result);
    console.log("peer count", i);
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
    .allowPublicAcquisition('notifyDataChannelClosed', function (argument_list, scope) {
      /*jslint unparam:true*/
      var gadget = this;
      return dropSubGadget(this, scope)
        .push(function () {
          return updateInfo(gadget);
        });
    })

    .declareMethod('connect', function(room_id, offer, parent_scope, config) {
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
          return rtc_gadget.register(room_id, 'master', config);
        })
        .push(function(){
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
          var ckeditor = window.frames[0].CKEDITOR;
          
          var data = {'content': ckeditor.instances.editor1.getData()};
          
          // Get all the extra properties and send it with data
          var extraprops = parent_scope.props.element.querySelector('.ui-collapsible').outerHTML;
          data['extra_props'] = extraprops;
          
          // Get title
          var title = parent_scope.props.element.querySelector('.ui-field-contain').childNodes[3].firstChild.value;
          data['title'] = title;

          rtc_gadget.send(JSON.stringify(data));
          ckeditor.instances.editor1.on('key',function(e){
            rtc_gadget.send(JSON.stringify({'content':ckeditor.instances.editor1.getData()}));
          });
          return updateInfo(gadget);
        });
      })
    })
    .declareMethod('initiate', function (roomid, scope, config) {
      var gadget = this,
        rtc_gadget,
        blob;
        
        return gadget.declareGadget("gadget_webrtc_jio_bridge.html")
        .push(function (rg) {
          // register peer
          rtc_gadget = rg;
          roomid = "/"+roomid+"/";
          return rtc_gadget.register(roomid, 'master', config);
        })
        .push(function (r) {
          var peerid = 'master';
          return rtc_gadget.wait_until_available(roomid, peerid+'_', function (offers) {
            var connections = [];
            for (var offer in offers) {
              connections.push(gadget.connect(roomid, JSON.parse(offers[offer].target.result), scope, config));
            }
            return RSVP.all(connections);
          });
        });
    })
    .declareMethod('slaveInitiate', function(roomid, g, config) {
       var context = this,
        rtc_gadget, gadget;
       
       roomid = "/"+roomid+"/";
 
       return g.notifySubmitting()
        .push(function() {
          return declareSubGadget(context, "gadget_webrtc_jio_bridge.html")
        })
        .push(function (gadget) {
          context.state_parameter_dict.uuid = UUID();
          context.state_parameter_dict.message_count = 0;
          context.state_parameter_dict.message_dict = {};
          rtc_gadget = gadget;

          // register peer
          if (config) {
            config = JSON.parse(config)
          }
          return rtc_gadget.register(roomid, context.state_parameter_dict.uuid, config);
        })
        .push(function(peers){
          var options = { roomid: roomid, 
                          peerid: context.state_parameter_dict.uuid,
                          initiator: true,
                          to: 'master' }
          return rtc_gadget.connect(options);
        })
        .push(null, function(error){
              return g.notifySubmitted()
                .push(function () {
                  throw error;
                });
        });
    })

}(window, rJS, document, RSVP, console, DOMException));