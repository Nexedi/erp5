/*jslint nomen: true, indent: 2, maxerr: 3 */
/*global window, Node, rJS, Handlebars */
(function (window, Node, rJS, Handlebars) {
  "use strict";

  var gadget_klass = rJS(window),
    success_button_source = gadget_klass.__template_element
                         .getElementById("success-button-template")
                         .innerHTML,
    success_button_template = Handlebars.compile(success_button_source),

    error_button_source = gadget_klass.__template_element
                         .getElementById("error-button-template")
                         .innerHTML,
    error_button_template = Handlebars.compile(error_button_source);

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
  gadget_klass
    .declareMethod('notify', function (options) {
      if (options) {
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
        if (this.state.status === 'success') {
          this.element.innerHTML = success_button_template({
            message: this.state.message
          });
        } else {
          this.element.innerHTML = error_button_template({
            message: this.state.message
          });
        }
      }

    })

    .onEvent('click', function (evt) {
      if ((evt.target.nodeType === Node.ELEMENT_NODE) &&
          (evt.target.tagName === 'BUTTON')) {
        return this.close();
      }
    }, false, false);

}(window, Node, rJS, Handlebars));