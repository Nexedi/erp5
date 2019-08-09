/*global window, rJS, RSVP, Event, XMLHttpRequest*/
/*jslint nomen: true, maxlen:80, indent:2*/
(function (window, rJS, RSVP, Event, XMLHttpRequest) {
  "use strict";

  function displayErrorContent(original_error) {
    var error_list = [original_error],
      i,
      error,
      error_text = "";
    error_list.push(new Error('stopping ERP5JS'));
    for (i = 0; i < error_list.length; i += 1) {
      error = error_list[i];
      if (error instanceof Event) {
        error = {
          string: error.toString(),
          message: error.message,
          type: error.type,
          target: error.target
        };
        if (error.target !== undefined) {
          error_list.splice(i + 1, 0, error.target);
        }
      }
      if (error instanceof XMLHttpRequest) {
        error = {
          message: error.toString(),
          readyState: error.readyState,
          status: error.status,
          statusText: error.statusText,
          response: error.response,
          responseUrl: error.responseUrl,
          response_headers: error.getAllResponseHeaders()
        };
      }
      if (error.constructor === Array ||
          error.constructor === String ||
          error.constructor === Object) {
        try {
          error = JSON.stringify(error);
        } catch (ignore) {
        }
      }
      error_text += error.message || error;
      error_text += '\n';
      if (error.fileName !== undefined) {
        error_text += 'File: ' +
          error.fileName +
          ': ' + error.lineNumber + '\n';
      }
      if (error.stack !== undefined) {
        error_text += 'Stack: ' + error.stack + '\n';
      }
      error_text += '---\n';
    }
    return error_text;
  }

  function displayError(error) {
    if (error instanceof RSVP.CancellationError) {
      return "RSVP cancelation error";
    }
    return displayErrorContent(error);
  }

  rJS(window)
    .declareMethod('render', function (options) {
      return this.changeState(options);
    })
    .onStateChange(function (modification_dict) {
      var skip_link, error_div, app_name_div, message, error_text,
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
        error_text = displayError(gadget.state.error);
        if (gadget.state.error.message) {
          message += gadget.state.error.message;
        } else {
          message += JSON.stringify(gadget.state.error);
        }
        if (modification_dict.error.currentTarget) {
          message += " - URL: " +
            modification_dict.error.currentTarget.responseURL;
        } else {
          message += " " + modification_dict.error;
        }
        message += " - FULL ERROR: " + error_text;
        error_div.textContent = message;
      }
      if (modification_dict.redirect_url) {
        skip_link = gadget.element.querySelector(".skip-link");
        skip_link.setAttribute('href', gadget.state.redirect_url);
      }
    });
}(window, rJS, RSVP, Event, XMLHttpRequest));