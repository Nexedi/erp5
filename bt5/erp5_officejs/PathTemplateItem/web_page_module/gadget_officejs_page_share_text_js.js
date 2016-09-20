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
        counter: 1,
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

    .declareMethod('onOffer', function(options, offer) {
      var gadget = this;

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
      });
    })

    .declareMethod('postConnection', function(options, offer) {
      var gadget = this,
        counter;
      return new RSVP.Queue()
      .push(function () {
        gadget.connecting = false;
        var ckeditor = window.frames[0].CKEDITOR;
        
        var data = {'content': ckeditor.instances.editor1.getData()};
        
        // Get all the extra properties and send it with data
        var extraprops = options.parent_scope.props.element.querySelector('.ui-collapsible').outerHTML;
        data['extra_props'] = extraprops;
        
        // Get title
        var title = options.parent_scope.props.element.querySelector(".view-web-page-form").title.value;
        data['title'] = title;
        
        counter = gadget.state_parameter_dict.counter;
        options.rtc_gadget.send(JSON.stringify(data), "webrtc"+counter);
        ckeditor.instances.editor1.on('key',function(e){
          options.rtc_gadget.send(JSON.stringify({'content':ckeditor.instances.editor1.getData()}), "webrtc"+counter);
        });
        gadget.state_parameter_dict.counter += 1;
        return updateInfo(gadget);
      });
    })

    .declareMethod('initiate', function (roomid, scope, type, config) {
      var gadget = this,
        options = {
          peerid: "master",
          type: type,
          config: config,
          roomid: "/"+roomid+"/",
          listner: true, // optional
          preConnection: gadget.onOffer.bind(gadget), // optional
          postConnection: gadget.postConnection.bind(gadget), // optional
          parent_scope: scope, // custom 
        },
        rtc_gadget;
        
        return gadget.getDeclaredGadget("gadget_webrtc_jio_bridge.html")
        .push(function (rtc_gadget) {
          options.rtc_gadget = rtc_gadget;
          return rtc_gadget.connect(options);
        });
    })
    .declareMethod('slaveInitiate', function(roomid, g, type, config) {
       var context = this,
        rtc_gadget,
        options = {
          type: type,
          roomid: "/"+roomid+"/",
          initiator: true,
          to: 'master'
        };
 
       return g.notifySubmitting()
        .push(function() {
          return context.getDeclaredGadget("gadget_webrtc_jio_bridge.html")
        })
        .push(function (gadget) {
          options.peerid = UUID();
          context.state_parameter_dict.message_count = 0;
          context.state_parameter_dict.message_dict = {};
          rtc_gadget = gadget;

          if (config) {
            config = JSON.parse(config)
            options.config = config;
          }

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