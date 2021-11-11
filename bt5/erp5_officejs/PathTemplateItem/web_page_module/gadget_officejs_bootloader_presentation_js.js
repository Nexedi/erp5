/*global window, rJS, RSVP, Event, XMLHttpRequest*/
/*jslint nomen: true, maxlen:80, indent:2*/
(function (window, rJS, RSVP, Event, XMLHttpRequest) {
  "use strict";

  /*function displayErrorContentOLD(original_error) {
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
  }*/

  function displayErrorContent(error_div, original_error) {
    var error_list = [original_error],
      i,
      error,
      error_text = "",
      addErrorMessage = function (parent_div, content) {
        var sub_error_div = document.createElement('div');
        sub_error_div.classList.add('error-message');
        sub_error_div.textContent = content;
        parent_div.appendChild(sub_error_div);
      };
    error_list.push(new Error('stopping ERP5JS'));
    for (i = 0; i < error_list.length; i += 1) {
      error = error_list[i];
      console.log("ERROR " + i + ":", error);
      if (error instanceof XMLHttpRequest) {
        console.log("instanceof XMLHttpRequest!!");
        addErrorMessage(error_div, "- readyState: " +
                        error.readyState);
        addErrorMessage(error_div, "- status: " +
                        error.status);
        addErrorMessage(error_div, "- statusText: " +
                        error.statusText);
        addErrorMessage(error_div, "- response: " +
                        error.response);
        addErrorMessage(error_div, "- responseUrl: " +
                        error.responseUrl);
        addErrorMessage(error_div, "- response_headers: " +
                        error.getAllResponseHeaders());
      } else if (error instanceof Event) {
        console.log("instanceof Event!!");
        addErrorMessage(error_div, "- type: " +
                        error.type);
        addErrorMessage(error_div, "- target: " +
                        error.target);
        if (error.target !== undefined) {
          error_list.splice(i + 1, 0, error.target);
        }
      }
      if (error.constructor === Array ||
          error.constructor === String ||
          error.constructor === Object) {
        console.log("constructor Array or String or Object!!");
        addErrorMessage(error_div, "- Full error: " +
                        JSON.stringify(error));
      }
      if (error.message) {
        addErrorMessage(error_div, "- message: " +
                        error.message);
      }
      if (error.fileName !== undefined) {
        addErrorMessage(error_div, "- file: " +
                        error.fileName +
                        ': ' + error.lineNumber);
      }
      if (error.stack !== undefined) {
        addErrorMessage(error_div, "- stack: " +
                        error.stack);
      }
    }
  }

  rJS(window)
    .declareMethod('render', function (options) {
      return this.changeState(options);
    })
    .onStateChange(function (modification_dict) {
      var skip_link, error_div, app_name_div, message, error_text,
        gadget = this, line = "-----------------------------------------------",
      addErrorMessage = function (parent_div, content) {
        var sub_error_div = document.createElement('div');
        sub_error_div.classList.add('error-message');
        sub_error_div.textContent = content;
        parent_div.appendChild(sub_error_div);
      };
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
        error_div.textContent = line;
        addErrorMessage(error_div, "Error ");
        if (gadget.state.error.message) {
          addErrorMessage(error_div, gadget.state.error.message);
        }
        if (modification_dict.error.currentTarget) {
          addErrorMessage(error_div, "URL: " +
            modification_dict.error.currentTarget.responseURL);
        }
        addErrorMessage(error_div, line);
        addErrorMessage(error_div, "Full error information:");
        if (gadget.state.error instanceof Event) {
          addErrorMessage(error_div, "- type: " +
                          gadget.state.error.type);
          addErrorMessage(error_div, "- target: " +
                          gadget.state.error.target);
        }
        if (gadget.state.error instanceof XMLHttpRequest) {
          addErrorMessage(error_div, "- readyState: " +
                          gadget.state.error.readyState);
          addErrorMessage(error_div, "- status: " +
                          gadget.state.error.status);
          addErrorMessage(error_div, "- statusText: " +
                          gadget.state.error.statusText);
          addErrorMessage(error_div, "- response: " +
                          gadget.state.error.response);
          addErrorMessage(error_div, "- responseUrl: " +
                          gadget.state.error.responseUrl);
          addErrorMessage(error_div, "- response_headers: " +
                          gadget.state.error.getAllResponseHeaders());
        }
        if (gadget.state.error.constructor === Array ||
            gadget.state.error.constructor === String ||
            gadget.state.error.constructor === Object) {
          try {
            addErrorMessage(error_div, "- Full error: " +
                            JSON.stringify(gadget.state.error));
          } catch (ignore) {}
        }
        if (gadget.state.error.message) {
          addErrorMessage(error_div, "- message: " +
                          gadget.state.error.message);
        }
        if (gadget.state.error.fileName !== undefined) {
          addErrorMessage(error_div, "- file: " +
                          gadget.state.error.fileName +
                          ': ' + gadget.state.error.lineNumber);
        }
        if (gadget.state.error.stack !== undefined) {
          addErrorMessage(error_div, "- stack: " +
                          gadget.state.error.stack);
        }
        displayErrorContent(error_div, gadget.state.error);
        /*if (gadget.state.error instanceof RSVP.CancellationError) {
          error_text = "RSVP cancelation error";
        } else {
          error_text = displayErrorContentOLD(gadget.state.error);
        }
        addErrorMessage(error_div, error_text);*/
      }
      if (modification_dict.redirect_url) {
        skip_link = gadget.element.querySelector(".skip-link");
        skip_link.setAttribute('href', gadget.state.redirect_url);
      }
    });
}(window, rJS, RSVP, Event, XMLHttpRequest));