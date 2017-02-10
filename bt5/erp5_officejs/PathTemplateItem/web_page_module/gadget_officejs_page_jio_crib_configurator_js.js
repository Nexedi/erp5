/*global window, document, rJS, RSVP, URI, location,
    loopEventListener*/
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS, RSVP) {
  "use strict";

  function setCribConfiguration(gadget) {
    var communication_url = gadget.element.querySelector('[name="communication_url"]').value,
      application_name = gadget.element.querySelector('[name="edited_application_name"]').value,
      erp5_url = gadget.element.querySelector('[name="erp5_url"]').value;

    return gadget.declareGadget(communication_url, {element: gadget.element.querySelector(".test_communication_url"), sandbox: "iframe", scope: "test_communication_gadget"}) 
      .push(function (crib_gadget) {
        return crib_gadget.createStorage();
      })
      .push(function () {
        return gadget.setSetting("communication_gadget", communication_url);
      })
      .push(function () {
        return gadget.setSetting("edited_application_name", application_name);
      })
      .push(function () {
        return gadget.setSetting("edited_erp5_url", erp5_url);
      })
      .push(function () {
        return gadget.getSetting("edited_app_dict", {});
      })
      .push(function (dict) {
        dict[application_name] = {
          "name": application_name,
          "communication_gadget": communication_url,
          "erp5_url": erp5_url
        }; 
        return gadget.setSetting("edited_app_dict", dict)
      })
      .push(function () {
        return gadget.reload();
      })
      .push(function () {
        return gadget.redirect({page: "document_list"});
      })
      .push(undefined, function (error) {
        gadget.element.querySelector(".communication_url_error").innerHTML = "Bad Free Web Gadget Url";
      });
  }

  var gadget_klass = rJS(window);

  gadget_klass
    .ready(function (g) {
      g.props = {};
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
        });
    })
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("reload", "reload")
    .declareAcquiredMethod("setSetting", "setSetting")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareMethod("render", function (options) {
      var gadget = this;
      gadget.props.options = options || {};  
      return gadget.updateHeader({
        title: "Storage Configuration"
      }).push(function () {
        return RSVP.all([
          gadget.getSetting("communication_gadget", ""),
          gadget.getSetting("edited_application_name", ""),
          gadget.getSetting("edited_erp5_url", "")
        ]);
      }).push(function (result) {
        gadget.props.element.querySelector('[name="communication_url"]').value = gadget.props.options.communication_gadget || result[0];
        gadget.props.element.querySelector('[name="edited_application_name"]').value = gadget.props.options.application_name || result[1];
        gadget.props.element.querySelector('[name="erp5_url"]').value = gadget.props.options.erp5_url || result[2];
      });
    })

    /////////////////////////////////////////
    // Form submit
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this;

      if (gadget.props.options !== undefined && gadget.props.options.auto_connect) {
        return setCribConfiguration(gadget, gadget.props.options);
      }
      return new RSVP.Queue()
        .push(function () {
          loopEventListener(
            gadget.props.element.querySelector('form.communication-configuration-form'),
            'submit',
            true,
            function () {
              return setCribConfiguration(gadget);
            }
          );
        });
    });


}(window, rJS, RSVP));