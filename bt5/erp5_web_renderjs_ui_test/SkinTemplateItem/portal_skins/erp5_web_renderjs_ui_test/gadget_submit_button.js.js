/*global window, rJS, RSVP, jIO, console, document */
/*jslint nomen: true, maxlen:80, indent:2*/
(function (rJS, jIO, RSVP, window, document) {
  "use strict";

  rJS(window)
    .declareMethod('render', function (options) {
      return this.changeState(options);
    })

    .declareMethod('getContent', function () {
      var result = {};
      result[this.state.key] = 'forbarcontent';
      return result;
    })

    .onStateChange(function () {
      var button = document.createElement('button');
      button.type = 'button';
      button.textContent = this.state.title;
      button.name = 'action_custom';
      this.element.innerHTML = '';
      this.element.appendChild(button);
    })

    .declareAcquiredMethod(
      "submitDialogWithCustomDialogMethod", "submitDialogWithCustomDialogMethod")
    .onEvent('click', function click(evt) {
      if (evt.target.type === "button") {
        evt.preventDefault();
        return this.submitDialogWithCustomDialogMethod(false, this.state.python_script_id);
      }
    }, false, false);

}(rJS, jIO, RSVP, window, document));