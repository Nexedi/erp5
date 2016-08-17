/*jslint indent: 2*/
/*global rJS, window, WebSocket, RSVP*/

(function (window, rJS, RSVP) {
  "use strict";


  rJS(window)
    .ready(function (g) {
      g.props = {};
      g.props.notify_websocket_message = function() {};
    })
    
    .allowPublicAcquisition("notifyWebSocketMessage", function (argument_list) {
      if (JSON.parse(argument_list[0]).action === "offer" && JSON.parse(argument_list[0]).from !== this.props.peerid) {
        return this.props.notify_websocket_message(argument_list);
      }
    })
    
    .allowPublicAcquisition("notifyWebSocketClosed", function () {

    })

    .declareMethod('init', function(url) {
      var gadget = this;

      return this.getDeclaredGadget('gadget_websocket')
        .push(function (socket_gadget) {
          gadget.props.ws_url = url;
          return socket_gadget.createSocket(url);
        })
    })

    .declareMethod('create_room', function(roomid) {
      this.props.roomid = roomid;
      return RSVP.promise
    })
    
    .declareMethod('register', function(roomid, peerid, options) {
      var gadget = this;
      gadget.props.peerid = peerid;
      return gadget.init(options.url);
    })

    .declareMethod('handle_answer', function (roomid, offer) {
      var gadget = this;
      return new RSVP.Queue()
        .push(function() {
          return jIO.util.readBlobAsText(offer.data);
        })
        .push(function (result) {
          offer = result.target.result;
          return gadget.getDeclaredGadget("gadget_websocket");
        })
        .push(function (g) {
          return g.send(offer);
        });
    })

    .declareMethod('get_answer', function (roomid, attachment) {
      var gadget = this;
    })

    .declareMethod('get_offers', function (roomid) {
      var gadget = this;
    })

    .declareMethod('wait_until_available', function (roomid, query, prom) {
      // execute given function on each websocket message 

      var gadget = this,
        response,
        offers;
      
      gadget.props.notify_websocket_message = prom;
      
    })

    .declareMethod('close', function (roomid, peerid, to) {
      var gadget = this;
      return gadget.getDeclaredGadget("gadget_websocket")
      .push(function (socket_gadget) {
        return socket_gadget.close();
      });
    });
})(window, rJS, RSVP);