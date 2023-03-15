/*jslint indent: 2, maxerr: 3, nomen: true */
/*global window, rJS, jIO, console, convertOriginalErrorToErrorDataList,
         buildErrorElementFromErrorText*/
(function (window, rJS, jIO, convertOriginalErrorToErrorDataList,
           buildErrorElementFromErrorText) {
  "use strict";

  rJS(window)
    .declareAcquiredMethod("getTranslationList", "getTranslationList")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    .declareMethod('render', function render(options) {
      return this.changeState({
        context_url: options.context_url.trim()
      });
    })
    .declareMethod('getContent', function getContent() {
      return {
        "your_command_line": this.element.querySelector("input").value
      };
    })
    .onEvent("submit", function (evt) {
      var gadget = this,
        translation_list,
        input_value = evt.target.querySelector("input").value,
        output = gadget.element.querySelector("output");

      return gadget.notifySubmitting()
        .push(function () {
          return gadget.getTranslationList([
            "Command is empty",
            "Status"
          ]);
        })
        .push(function (result_list) {
          translation_list = result_list;
          if (!input_value.trim()) {
            throw new Error(translation_list[0]);
          }
          return jIO.util.ajax({
            url: gadget.state.context_url + "/" + input_value,
            xhrFields: {
              withCredentials: true
            }
          });
        })
        .push(function (response) {
          var content_type = response.target.getResponseHeader("Content-Type"),
            response_text = response.target.responseText;

          if (response_text) {
            if (content_type.indexOf("text/html") !== -1) {
              output.innerHTML = response_text;
            } else {
              output.innerText = response_text;
            }
          } else {
            // XXX - when response is empty, what we should display?
            output.innerText = translation_list[1] + ": " + response.target.status;
          }
        })
        .push(undefined, function (error) {
          return convertOriginalErrorToErrorDataList(error)
            .push(function (error_list) {
              return buildErrorElementFromErrorText(error_list[1]);
            })
            .push(function (container) {
              while (output.firstChild) {
                output.removeChild(output.firstChild);
              }
              output.appendChild(container);
            });
        })
        .then(function () {
          return gadget.notifySubmitted();
        });
    }, false, true);
}(window, rJS, jIO, convertOriginalErrorToErrorDataList,
  buildErrorElementFromErrorText));