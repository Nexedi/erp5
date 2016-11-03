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
          inner_html: options.inner_html || "",
          tag: options.tag || 'div',
          src: options.src,
          alt: options.alt
        };
      return this.changeState(state_dict);
    })

    .onStateChange(function () {
      var element = this.element,
        new_element = document.createElement(this.state.tag);
      if (this.state.text_content) {
        new_element.textContent = this.state.text_content;
      } else if (this.state.inner_html) {
        new_element.innerHTML = this.state.inner_html;
      }
      if (this.state.src) {
        new_element.setAttribute('src', this.state.src);
      }
      if (this.state.alt) {
        new_element.setAttribute('alt', this.state.alt);
      }
      // Clear first to DOM, append after to reduce flickering/manip
      while (element.firstChild) {
        element.removeChild(element.firstChild);
      }
      element.appendChild(new_element);
    })

    .declareMethod('getTextContent', function (options) {
      return this.state.text_content;
    });

}(window, document, rJS));