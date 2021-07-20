/*global window, document, rJS, getFirstNonEmpty, isEmpty */
/*jslint indent: 2, maxerr: 3 */
(function (window, document, rJS, getFirstNonEmpty, isEmpty) {
  "use strict";

  rJS(window)
    .setState({
      tag: 'div',
      text_content: '',
      inner_html: '',
      id: undefined,
      name: undefined,
      src: undefined,
      href: undefined,
      alt: undefined,
      append: '',
      prepend: ''
    })

    .declareMethod('render', function render(options) {
      var state_dict = {
          text_content: getFirstNonEmpty(options.text_content, ""),
          inner_html: getFirstNonEmpty(options.inner_html, ""),
          id: options.id,
          tag: options.tag || 'div',
          src: options.src,
          href: options.href,
          alt: options.alt,
          name: options.name,
          title: options.title,
          append: getFirstNonEmpty(options.append, ""),
          prepend: getFirstNonEmpty(options.prepend, "")
        };
      // data are dictionary thus include it only when defined so it appears
      // in modification_dict only when necessary
      // keys are expected to be camelCase
      if (options.data !== undefined) {
        state_dict.data = JSON.stringify(options.data);
      }
      return this.changeState(state_dict);
    })

    .onStateChange(function onStateChange(modification_dict) {
      var element = this.element,
        new_element = document.createElement(this.state.tag),
        content = this.state.text_content,
        data,
        data_attr;
      if (!isEmpty(this.state.text_content)) {
        if (this.state.prepend) {
          content = this.state.prepend + content;
        }
        if (this.state.append) {
          content = content + this.state.append;
        }
        new_element.textContent = content;
      } else if (!isEmpty(this.state.inner_html)) {
        new_element.innerHTML = this.state.inner_html;
      }
      if (this.state.id) {
        new_element.id = this.state.id;
      }
      if (this.state.src) {
        new_element.setAttribute('src', this.state.src);
      }
      if (this.state.href) {
        new_element.setAttribute('href', this.state.href);
      }
      if (this.state.alt) {
        new_element.setAttribute('alt', this.state.alt);
      }
      if (this.state.title) {
        new_element.setAttribute('title', this.state.title);
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
    .declareMethod("getContent", function getContent() {
      var data = {};
      if (!this.state.name) {
        return data;
      }
      if (!isEmpty(this.state.text_content)) {
        data[this.state.name] = this.state.text_content;
      } else if (!isEmpty(this.state.inner_html)) {
        data[this.state.name] = this.state.inner_html;
      } else {
        data[this.state.name] = "";
      }
      return data;
    })

    .declareAcquiredMethod("notifyFocus", "notifyFocus")
    .onEvent('focus', function focus() {
      return this.notifyFocus();
    }, true, false)

    .declareAcquiredMethod("notifyBlur", "notifyBlur")
    .onEvent('blur', function blur() {
      return this.notifyBlur();
    }, true, false)

    .declareMethod("checkValidity", function checkValidity() {
      return true;
    });

}(window, document, rJS, getFirstNonEmpty, isEmpty));