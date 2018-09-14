/*global window, rJS, URL, jIO, RSVP*/
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, URL, jIO) {
  "use strict";
  rJS(window)
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("redirect", "redirect")
    .declareMethod('render', function (options) {
      var value,
        css_class = "ui-btn orange",
        url_options,
        url;
      if (options.state === "Accepted") {
        if (options.select) {
          value = "Current";
          css_class = "ui-btn-disabled green";
        } else {
          value = "Select";
          css_class = "ui-btn blue";
          url = new URL('./' + options.jio_key + '/SoftwarePublication_selectVersion', new URL(window.location.pathname, window.location.origin));
        }
      } else if (options.state === "Submitted") {
        value = "Open";
        css_class = 'blue';
        url_options = {
          command: 'display_erp5_action',
          options: {page: 'open_action', jio_key: options.jio_key}
        };
      } else if (options.state === "Draft") {
        value = "Wait For Submit";
      } else {
        value = "Wait For Approval";
      }
      return this.changeState({
        value: value,
        css_class: css_class,
        url: url,
        url_options: url_options
      });
    })
    .onStateChange(function (modification_dict) {
      var a = this.element.querySelector("a");
      if (modification_dict.hasOwnProperty('value')) {
        a.textContent = modification_dict.value;
      }
      if (modification_dict.hasOwnProperty('css_class')) {
        a.setAttribute('class', this.state.css_class);
      }
    })
    .onEvent('click', function () {
      var gadget = this;
      if (gadget.state.url) {
        return new RSVP.Queue()
          .push(function () {
            return jIO.util.ajax({
              type: 'POST',
              url: gadget.state.url
            });
          })
          .push(function () {
            return gadget.redirect({command: 'change', options: {}});
          });
      }
      if (gadget.state.url_options) {
        return gadget.redirect(gadget.state.url_options);
      }
    })
    .declareMethod('getContent', function () {
      return {};
    });

}(window, rJS, URL, jIO, RSVP));