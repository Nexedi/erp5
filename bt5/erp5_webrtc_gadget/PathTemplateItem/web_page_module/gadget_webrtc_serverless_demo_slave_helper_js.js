/*global window, rJS, document, RSVP */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS, document, RSVP) {
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

  function wrapJioAccess(gadget, method_name, argument_list) {
    return gadget.getDeclaredGadget('gadget_webrtc_jio_bridge.html')
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
      gadget.state_parameter_dict = {};
      return gadget.getElement()
        .push(function (element) {
          gadget.state_parameter_dict.element = element;
        });
    })

    .allowPublicAcquisition("notifyDataChannelMessage", function (argument_list) {
      var json = JSON.parse(argument_list[0]),
        context = this;
      if (json.type === "jio_response") {
        context.state_parameter_dict.message_dict[json.id].resolve(json.result);
      } else if (json.type === "error") {
        context.state_parameter_dict.message_dict[json.id].reject(json.result);
      }
      // Drop all other kind of messages
    })

    .allowPublicAcquisition("notifyWebSocketMessage", function (argument_list) {

      var json = JSON.parse(argument_list[0]),
        gadget = this;

      if (json.action === "answer") {
        if (json.to === gadget.state_parameter_dict.uuid) {
          gadget.state_parameter_dict.answer_defer.resolve(json.data);
        }
      }

    })

    .declareMethod('createJio', function (options) {
      var context = this,
        roomid = "/"+options.room+"/",
        rtc_gadget,
        handshake_gadget;
        
      return declareSubGadget(context, 'gadget_webrtc_jio_bridge.html')
        .push(function (gadget) {
          context.state_parameter_dict.uuid = UUID();
          context.state_parameter_dict.message_count = 0;
          context.state_parameter_dict.message_dict = {};
          rtc_gadget = gadget;
          
          // register peer
          return rtc_gadget.register(roomid, context.state_parameter_dict.uuid);
        })
        .push(function(peers){
          var options = { roomid: roomid, 
                          peerid: context.state_parameter_dict.uuid,
                          initiator: true,
                          to: 'master' }
          return rtc_gadget.connect(options);
        })
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
}(window, rJS, document, RSVP));