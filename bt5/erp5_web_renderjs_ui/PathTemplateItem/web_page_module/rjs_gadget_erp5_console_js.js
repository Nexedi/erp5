/*jslint indent: 2, maxerr: 3, nomen: true */
/*global window, rJS, RSVP, jIO, loopEventListener, JSON, console */
(function (window, rJS, RSVP, jIO, loopEventListener, JSON) {
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
      var data = {
        "your_command_line": this.element.querySelector("input").value
      };
      return data;
    })
    .declareService(function () {
      var gadget = this,
        output = gadget.element.querySelector("output");
      function formSubmit(evt) {
        var input_value = evt.target.querySelector("input").value;
        return gadget.notifySubmitting()
          .push(function () {
            // A hack during the christmas is allowed :)
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
              output.innerText = "404 Not Found";
            }
            output.innerText = "Unexpected error. Please debug";
          });
      }
      return loopEventListener(
        this.element.querySelector("form"),
        "submit",
        false,
        formSubmit,
        true
      );
    });

}(window, rJS, RSVP, jIO, loopEventListener, JSON));