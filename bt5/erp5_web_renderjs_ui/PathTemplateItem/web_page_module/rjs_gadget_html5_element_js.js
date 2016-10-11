/*global window, document, rJS */
/*jslint indent: 2, maxerr: 3 */
(function (window, document, rJS) {
  "use strict";

  rJS(window)
    .setState({
      tag: 'div',
      text_content: ''
    })

    .declareMethod('render', function (options) {
      var state_dict = {
          text_content: options.text_content || "",
          tag: options.tag || 'div'
        };
      return this.changeState(state_dict);
    })

    .onStateChange(function () {
      var element = this.element,
        new_element = document.createElement(this.state.tag);
      new_element.textContent = this.state.text_content;
      // Clear first to DOM, append after to reduce flickering/manip
      while (element.firstChild) {
        element.removeChild(element.firstChild);
      }
      element.appendChild(new_element);
    });

}(window, document, rJS));