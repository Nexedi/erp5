/*global window, rJS, RSVP, URI, location,
    loopEventListener, btoa */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS, RSVP) {
  "use strict";

  function setPageShareConfiguration(gadget) {
    return gadget.getSetting("portal_type")
      .push(function (portal_type) {
        var configuration = {
          url: gadget.props.element.querySelector("input[name='websocket_url']").value
        };
        return gadget.setSetting('webrtc_share_description', configuration);
      })
      .push(function () {
        return gadget.setSetting('webrtc_share_name', "WEBSOCKET");
      })
      .push(function () {
        return gadget.reload();
      });
  }

  var gadget_klass = rJS(window);

  gadget_klass
    .ready(function (g) {
      g.props = {};
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
          g.props.deferred = RSVP.defer();
          return g.getSetting('webrtc_share_name');
        })
        .push(function (webrtc_share_name) {
          if (webrtc_share_name === "WEBSOCKET") {
            return g.getSetting('webrtc_share_description')
              .push(function (webrtc_share_description) {
                g.props.element.querySelector("input[name='websocket_url']").value = webrtc_share_description.url;
              });
          }
        });
    })
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("reload", "reload")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("setSetting", "setSetting")
    .declareMethod("render", function () {
      var gadget = this;
      return gadget.updateHeader({
        title: "Handshake Using Websocket",
        back_url: "#page=share_configurator",
        panel_action: false
      }).push(function () {
        return gadget.props.deferred.resolve();
      });
    })

    /////////////////////////////////////////
    // Form submit
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {
          return loopEventListener(
            gadget.props.element.querySelector('form'),
            'submit',
            true,
            function () {
              return setPageShareConfiguration(gadget);
            }
          );
        });
    });


}(window, rJS, RSVP));