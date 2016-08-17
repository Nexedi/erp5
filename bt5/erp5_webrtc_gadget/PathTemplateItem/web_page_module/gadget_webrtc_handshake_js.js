/*jslint indent: 2*/
/*global rJS, window, WebSocket, RSVP*/

(function (window, rJS, RSVP) {
  "use strict";

  function createJio(gadget, config) {
    if (!config) {
      config = {
        type: "query",
        sub_storage: {
          type: "uuid",
          sub_storage: {
            //type: "indexeddb",
            "type": "dav",
            //"type": "erp5",
            //"url": "https://softinst67525.host.vifib.net/erp5",
            "url": "https://softinst67513.host.vifib.net/share/",
            "basic_login": btoa("admin:vowhkida")
            //"database": "handshake"
          }
        }
      }
    }
    return gadget.getDeclaredGadget("jio_gadget")
      .push(function (jio_gadget) {
        return jio_gadget.createJio(config);
      })
      .push(null, function(e) {
        // TODO: Throw error in a correct way
        throw new Error("Wrong Config", config);
      })
  }

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

  rJS(window)
    .ready(function (g) {
      g.props = {};
    })

    .declareMethod('init', function(config) {
      // configure jio to given storage
      return createJio(this, config);
    })

    .declareMethod('create_room', function(roomid) {
      var gadget = this;
       return new RSVP.Queue()
        .push(function () {
          return gadget.getDeclaredGadget("jio_gadget");
        })
        .push(function (jio_gadget) {
          return jio_gadget.put(roomid, {});
        })
        .push(null, function(e){
          console.log(e);
        })
    })
    
    .declareMethod('register', function(roomid, peerid, config) {
      var gadget = this,
        jio_gadget;

      return new RSVP.Queue()
        .push(function() {
          return gadget.init(config);
        })
        .push(function() {
          return gadget.create_room(roomid);
        })
        .push(function () {
          return gadget.getDeclaredGadget("jio_gadget");
        })
        .push(function (jg) {
          jio_gadget = jg;
          return jio_gadget.putAttachment(roomid, peerid, '');
        })
        .push(function () {
          return jio_gadget.allAttachments(roomid);
        })
        .push(function (d) {
          //TODO: only return docs with peerid
          var peers ={},
            docs = Object.keys(d);
          for (var doc in docs) {
            if (docs[doc].split('_').length === 1) {
              peers[docs[doc]] = 1;
            }
          }
          return peers
        })
        .push(null, function(e){
          // if registered ignore
          //console.info(e);
        })
    })

    .declareMethod('handle_answer', function (roomid, options) {
      var gadget = this,
          jio_gadget;
      return new RSVP.Queue()
        .push(function () {
          return gadget.getDeclaredGadget("jio_gadget");
        })
        .push(function (jio_gadget) {
          return jio_gadget.putAttachment(roomid, options.name, options.data);
        })
    })

    .declareMethod('get_answer', function (roomid, attachment) {
      var gadget = this,
          jio_gadget;
      return new RSVP.Queue()
        .push(function () {
          return gadget.getDeclaredGadget("jio_gadget");
        })
        .push(function (jio_gadget) {
          return jio_gadget.getAttachment(roomid, attachment);
        });
    })

    .declareMethod('get_offers', function (roomid) {
      var gadget = this,
          jio_gadget;
      return new RSVP.Queue()
        .push(function () {
          return gadget.getDeclaredGadget("jio_gadget");
        })
        .push(function (jio_gadget) {
          return jio_gadget.allAttachments(roomid);
        });
    })

    .declareMethod('wait_until_available', function (roomid, query, prom) {
      // Pool the document until available

      var gadget = this,
        response,
        offers = [];

      var action = function(response) {
        return gadget.get_offers(roomid)
        .push(function(response) {
          var offers = [];
          for (var doc_name in response) {
            if(doc_name.split('_').length === 1 && doc_name === query) {
              return gadget.get_answer(roomid, query);
            } else if (doc_name.split('_').length === 2 && doc_name.split('_')[0]+'_' === query) {
              offers.push(gadget.get_answer(roomid, doc_name));
            }
          }
          return RSVP.all(offers);
        })
        .push(function(responses) {
          if (responses.constructor !== Array ) {
            responses = [responses];  
          }
          if (!responses.length) {
            return  new RSVP.Queue()
            .push(function() {
              return RSVP.delay(5000);
            })
            .push(function() {
              return true
            });
          }
          var blobs = responses;
          
          var texts = [];
          for (var blob in blobs) {
            texts.push(jIO.util.readBlobAsText(blobs[blob]));
          }
          return new RSVP.Queue()
          .push(function() {
            return RSVP.all(texts);
          })
          .push(function(o){
            var a = [];
            for (var offer in o) {
              a.push(o[offer].target.result)
            }

            if (typeof prom === "function") {
              return prom(a)
            } else {
              offers = a;
              return false;
            } 
          })
        });
      };

      return promiseDoWhile(action, prom);
    })

    .declareMethod('close', function (roomid, peerid, to) {
      var gadget = this,
        jio_gadget;
      
      return new RSVP.Queue()
        .push(function () {
          return gadget.getDeclaredGadget("jio_gadget");
        })
        .push(function (jio_gadget) {
          return jio_gadget.removeAttachment(roomid, peerid+"_"+to);
        });
    });
})(window, rJS, RSVP);