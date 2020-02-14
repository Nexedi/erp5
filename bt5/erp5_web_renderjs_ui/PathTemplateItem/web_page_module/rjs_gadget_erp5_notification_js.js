/*jslint nomen: true, indent: 2, maxerr: 3 */
/*global window, Node, rJS, domsugar */
(function (window, Node, rJS, domsugar) {
  "use strict";

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
  rJS(window)
    .declareMethod('notify', function (options) {
      if (options && options.message) {
        return this.changeState({
          visible: true,
          message: options.message,
          status: options.status
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
        domsugar(this.element, [
          domsugar('button', {
            type: 'submit',
            class: (this.state.status === 'success') ? 'success' : 'error',
            text: this.state.message
          })
        ]);
      }

    })

    .onEvent('click', function (evt) {
      if ((evt.target.nodeType === Node.ELEMENT_NODE) &&
          (evt.target.tagName === 'BUTTON')) {
        return this.close();
      }
    }, false, false);

}(window, Node, rJS, domsugar));