/*jslint indent: 2, maxerr: 3, nomen: true */
/*global window, rJS, jIO, loopEventListener, JSON, console */
(function (window, rJS, jIO, loopEventListener, JSON) {
  "use strict";
  rJS(window)
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    .declareMethod('render', function render(options) {
      return this.changeState({
        context_url: JSON.parse(options.value).context_url
      });
    })
    .declareMethod('getContent', function getContent() {
      return {
        "your_command_line": this.element.querySelector("input").value
      };
    })
    .onEvent("submit", function (evt) {
      var gadget = this,
        input_value = evt.target.querySelector("input").value,
        output = gadget.element.querySelector("output");
      return gadget.notifySubmitting()
        .push(function () {
          return jIO.util.ajax({
            url: gadget.state.context_url + "/" + input_value,
            xhrFields: {
              withCredentials: true
            }
          });
        })
        .push(function (response) {
          var content_type = response.target.getResponseHeader("Content-Type");
          if (content_type.indexOf("text/html") !== -1) {
            output.innerHTML = response.target.responseText;
          } else {
            output.value = response.target.responseText;
          }
          return gadget.notifySubmitted();
        }, function (error) {
          if (error.target.status === 404) {
            output.textContent = "404 Not Found";
          } else {
            output.textContent = "Unexpected error. Please debug";
          }
        });
    }, false, true);
}(window, rJS, jIO, loopEventListener, JSON));