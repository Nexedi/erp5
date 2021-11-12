/*global window, rJS, RSVP, Event, XMLHttpRequest*/
/*jslint nomen: true, maxlen:80, indent:2*/
(function (window, rJS, RSVP, Event, XMLHttpRequest) {
  "use strict";

  function displayErrorContent(error_div, original_error) {
    var error_list = [original_error],
      i,
      error,
      line = "-----------------------------------------------",
      addErrorMessage = function (parent_div, content) {
        var sub_error_div = document.createElement('div');
        sub_error_div.classList.add('error-message');
        sub_error_div.textContent = content;
        parent_div.appendChild(sub_error_div);
      };
    error_div.textContent = line;
    addErrorMessage(error_div, "ERROR");
    if (original_error.message) {
      addErrorMessage(error_div, original_error.message);
    }
    if (original_error.currentTarget) {
      addErrorMessage(error_div, "URL: " +
        original_error.currentTarget.responseURL);
    }
    addErrorMessage(error_div, line);
    addErrorMessage(error_div, "FULL ERROR INFORMATION:");
    error_list.push(new Error('stopping ERP5JS'));
    for (i = 0; i < error_list.length; i += 1) {
      error = error_list[i];
      if (error instanceof XMLHttpRequest) {
        addErrorMessage(error_div, "- readyState: " + error.readyState);
        addErrorMessage(error_div, "- status: " + error.status);
        addErrorMessage(error_div, "- statusText: " + error.statusText);
        addErrorMessage(error_div, "- response: " + error.response);
        addErrorMessage(error_div, "- responseUrl: " + error.responseUrl);
        addErrorMessage(error_div, "- response_headers: " +
                        error.getAllResponseHeaders());
      } else if (error instanceof Event) {
        addErrorMessage(error_div, "- type: " + error.type);
        addErrorMessage(error_div, "- target: " + error.target);
        if (error.target !== undefined) {
          error_list.splice(i + 1, 0, error.target);
        }
      }
      if (error.constructor === Array ||
          error.constructor === String ||
          error.constructor === Object) {
        addErrorMessage(error_div, "- Full error: " + JSON.stringify(error));
      }
      if (error.message) {
        addErrorMessage(error_div, "- message: " + error.message);
      }
      if (error.fileName !== undefined) {
        addErrorMessage(error_div, "- file: " + error.fileName +
                        ': ' + error.lineNumber);
      }
      if (error.stack !== undefined) {
        addErrorMessage(error_div, line);
        addErrorMessage(error_div, "STACK");
        addErrorMessage(error_div, error.stack);
      }
      addErrorMessage(error_div, line);
    }
  }

  rJS(window)
    .declareMethod('render', function (options) {
      return this.changeState(options);
    })
    .onStateChange(function (modification_dict) {
      var skip_link, error_div, app_name_div,
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
        if (gadget.state.error instanceof RSVP.CancellationError) {
          error_div.textContent = "RSVP cancelation error";
        } else {
          displayErrorContent(error_div, gadget.state.error);
        }
      }
      if (modification_dict.redirect_url) {
        skip_link = gadget.element.querySelector(".skip-link");
        skip_link.setAttribute('href', gadget.state.redirect_url);
      }
    });
}(window, rJS, RSVP, Event, XMLHttpRequest));