/*global window, rJS*/
/*jslint nomen: true, maxlen:80, indent:2*/
(function (window, rJS) {
  "use strict";

  rJS(window)
    .declareMethod('render', function (options) {
      return this.changeState(options);
    })
    .onStateChange(function (modification_dict) {
      var skip_link, error_div, app_name_div, message,
        gadget = this;

      if (modification_dict.app_name) {
        app_name_div = gadget.element.querySelector(".app-name");
        app_name_div.textContent = gadget.state.app_name +
          " is being prepared for 100 % offline mode";
      }
      if (modification_dict.error_amount) {
        app_name_div = gadget.element.querySelector(".error-amount");
        app_name_div.textContent = "Retry: " + gadget.state.error_amount;
      }
      if (modification_dict.error) {
        error_div = gadget.element.querySelector(".error-message");
        message = "Last Error: ";
        if (gadget.state.error.message) {
          message += gadget.state.error.message;
        } else {
          message += JSON.stringify(gadget.state.error);
        }
        error_div.textContent = message;
      }
      if (modification_dict.redirect_url) {
        skip_link = gadget.element.querySelector(".skip-link");
        skip_link.setAttribute('href', gadget.state.redirect_url);
      }
    });

}(window, rJS));