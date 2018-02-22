/*global window, document, rJS */
/*jslint indent: 2, maxerr: 3 */
(function (window, document, rJS) {
  "use strict";

  rJS(window)
    .setState({
      tag: 'div',
      text_content: '',
      inner_html: '',
      id: undefined,
      name: undefined,
      src: undefined,
      alt: undefined,
      append: '',
      prepend: ''
    })

    .declareMethod('render', function (options) {
      var state_dict = {
          text_content: options.text_content || "",
          inner_html: options.inner_html || "",
          id: options.id,
          tag: options.tag || 'div',
          src: options.src,
          alt: options.alt,
          name: options.name,
          append: options.append || '',
          prepend: options.prepend || ''
        };
      // data are dictionary thus include it only when defined so it appears
      // in modification_dict only when necessary
      // keys are expected to be camelCase
      if (options.data !== undefined) {
        state_dict.data = JSON.stringify(options.data);
      }
      return this.changeState(state_dict);
    })

    .onStateChange(function (modification_dict) {
      var element = this.element,
        new_element = document.createElement(this.state.tag),
        content = this.state.text_content,
        data, data_attr;

      if (this.state.text_content) {
        if (this.state.prepend) {
          content = this.state.prepend + "&nbsp;" + content;
        }
        if (this.state.append) {
          content = content + "&nbsp;" + this.state.append;
        }
        new_element.textContent = content;
      } else if (this.state.inner_html) {
        new_element.innerHTML = this.state.inner_html;
      }
      if (this.state.id) {
        new_element.id = this.state.id;
      }
      if (this.state.src) {
        new_element.setAttribute('src', this.state.src);
      }
      if (this.state.alt) {
        new_element.setAttribute('alt', this.state.alt);
      }
      if (modification_dict.hasOwnProperty("data")) {
        data = JSON.parse(modification_dict.data);
        for (data_attr in data) {
          if (data.hasOwnProperty(data_attr)) {
            new_element.dataset[data_attr] = data[data_attr];
          }
        }
      }
      // Clear first to DOM, append after to reduce flickering/manip
      while (element.firstChild) {
        element.removeChild(element.firstChild);
      }
      element.appendChild(new_element);
    })

    /** Because of meta-fields (controlling MatrixBox for example) we need to
     * obtain value of readonly fields.
     * In order to make it more developer-friendly, only named fields return their values.
     */
    .declareMethod("getContent", function () {
      var data = {};
      if (!this.state.name) {
        return data;
      }
      data[this.state.name] = this.state.text_content || this.state.inner_html || "";
      return data;
    });

}(window, document, rJS));