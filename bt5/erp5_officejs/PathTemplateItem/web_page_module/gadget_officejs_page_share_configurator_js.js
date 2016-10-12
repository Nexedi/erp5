/*global window, document, rJS, RSVP, URI, location,
    loopEventListener*/
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS, RSVP) {
  "use strict";

  function setERP5Configuration(gadget) {
    var configuration = {
      remote_sub_storage: {
        type: "erp5",
        url: (new URI("hateoas"))
          .absoluteTo(location.href)
          .toString(),
        default_view_reference: "view"
      }
    };
    
    return gadget.setSetting('webrtc_share_description', configuration)
      .push(function () {
        return gadget.setSetting('webrtc_share_name', "ERP5");
      })
      .push(function () {
        return gadget.reload();
      });
  }

  function setWebsocketConfiguration(gadget) {
    return gadget.redirect({page: 'share_websocket_configurator'});
  }

  function setDAVConfiguration(gadget) {
    return gadget.redirect({page: 'share_dav_configurator'});
  }

  var gadget_klass = rJS(window);

  gadget_klass
    .ready(function (g) {
      g.props = {};
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
          g.props.deferred = RSVP.defer();
        });
    })
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("reload", "reload")
    .declareAcquiredMethod("setSetting", "setSetting")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareMethod("render", function () {
      var gadget = this;
      return gadget.updateHeader({
        title: "Webrtc Page Share Configuration"
      }).push(function () {
        return RSVP.all([
          gadget.getSetting('webrtc_share_name'),
          gadget.getSetting('application_title')
        ]);
      }).push(function (setting_list) {
        switch (setting_list[0]) {
        case "ERP5":
          gadget.props.element.querySelector("form.select-erp5-form button").classList.add("ui-btn-active");
          break;
        case "DAV":
          gadget.props.element.querySelector("form.select-dav-form button").classList.add("ui-btn-active");
          break;
        case "WEBSOCKET":
          gadget.props.element.querySelector("form.select-websocket-form button").classList.add("ui-btn-active");
          break;
        default:
          gadget.props.element.querySelector(".message h3").appendChild(document.createTextNode("Welcome in OfficeJS " + setting_list[1] + ". Please start by choosing an option."));
          gadget.props.element.querySelector(".message").setAttribute("style", "");
          gadget.props.element.querySelector(".document-access").setAttribute("style", "display: none;");
          break;
        }
        return;
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
          return RSVP.all([
            loopEventListener(
              gadget.props.element.querySelector('form.select-erp5-form'),
              'submit',
              true,
              function () {
                return setERP5Configuration(gadget);
              }
            ),
            loopEventListener(
              gadget.props.element.querySelector('form.select-websocket-form'),
              'submit',
              true,
              function () {
                return setWebsocketConfiguration(gadget);
              }
            ),
            loopEventListener(
              gadget.props.element.querySelector('form.select-dav-form'),
              'submit',
              true,
              function () {
                return setDAVConfiguration(gadget);
              }
            )
          ]);
        });
    });


}(window, rJS, RSVP));