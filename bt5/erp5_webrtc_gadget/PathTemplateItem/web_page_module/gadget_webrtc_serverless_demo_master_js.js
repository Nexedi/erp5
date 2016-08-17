/*global window, rJS, document, RSVP, console, DOMException */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS, document, RSVP, console, DOMException) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // Some functions
  /////////////////////////////////////////////////////////////////
  function createJio(gadget) {
    return gadget.getDeclaredGadget("jio_gadget")
      .push(function (jio_gadget) {
        return jio_gadget.createJio({
          type: "query",
          sub_storage: {
            type: "uuid",
            sub_storage: {
              "type": "indexeddb",
              "database": "serverless"
            }
          }
        });
      });
  }
    
  
  /////////////////////////////////////////////////////////////////
  // Gadget behaviour
  /////////////////////////////////////////////////////////////////
  rJS(window)
    /////////////////////////////////////////////////////////////////
    // ready
    /////////////////////////////////////////////////////////////////
    .ready(function (gadget) {
      gadget.state_parameter_dict = {};
      return gadget.getElement()
        .push(function (element) {
          gadget.state_parameter_dict.element = element;
        });
    })
    
    // Configure jIO to indexeddb
    .ready(function (gadget) {
      return createJio(gadget);
    })

    /////////////////////////////////////////////////////////////////
    // acquired methods
    /////////////////////////////////////////////////////////////////

    /////////////////////////////////////////////////////////////////
    // published methods
    /////////////////////////////////////////////////////////////////
    .allowPublicAcquisition("jio_post", function (my_param_list) {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return gadget.getDeclaredGadget("jio_gadget");
        })
        .push(function (my_gadget) {
          return my_gadget.post.apply(my_gadget, my_param_list);
        });
    })
    .allowPublicAcquisition("jio_get", function (my_param_list) {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return gadget.getDeclaredGadget("jio_gadget");
        })
        .push(function (my_gadget) {
          return my_gadget.get.apply(my_gadget, my_param_list);
        });
    })
    .allowPublicAcquisition("jio_allDocs", function (my_param_list) {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return gadget.getDeclaredGadget("jio_gadget");
        })
        .push(function (my_gadget) {
          return my_gadget.allDocs.apply(my_gadget, my_param_list);
        });
    })

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    /////////////////////////////////////////////////////////////////
    // declared services
    /////////////////////////////////////////////////////////////////
    .declareService(function () {
      var gadget = this;
      return new RSVP.Queue()
      .push(function() {
        return gadget.getElement()
      })
      .push(function (element) {
          function initializeWebrtcConnecton(my_event) {
            var value = element.querySelector(".ops-socket-connector").value;
            return gadget.getDeclaredGadget('share_storage_via_webrtc')
            .push(function(g){
              g.initiate(value);
            })
          }
        
          // Listen to form submit
          return loopEventListener(
            element,
            'submit',
            false,
            initializeWebrtcConnecton
          );
        })
    });
}(window, rJS, document, RSVP, console, DOMException));
