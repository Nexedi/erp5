/*jslint nomen: true, indent: 2, maxerr: 3 */
/*global window, Node, rJS */
(function (window, Node, rJS) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('notify', function (message) {
      if (typeof message === "string") {
        // alertify.log(message);
        return this.changeState({
          visible: true,
          message: message
        });
      }
      return this.changeState({
        visible: false
      });
    })

    .declareMethod('close', function () {
      return this.changeState({
        visible: false
      });
    })

    .onStateChange(function (modification_dict) {
      if (modification_dict.hasOwnProperty('visible')) {
        if (this.state.visible) {
          if (!this.element.classList.contains('visible')) {
            this.element.classList.toggle('visible');
          }
        } else {
          if (this.element.classList.contains('visible')) {
            this.element.classList.remove('visible');
          }
        }
      }

      if (modification_dict.hasOwnProperty('message')) {
        var button = this.element.querySelector('button');
        button.textContent = this.state.message;
      }

    })

    .onEvent('click', function (evt) {
      if ((evt.target.nodeType === Node.ELEMENT_NODE) &&
          (evt.target.tagName === 'BUTTON')) {
        return this.close();
      }
    }, false, false);

}(window, Node, rJS));