/*global window, rJS */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS) {
  "use strict";

  rJS(window)
    .setState({
      tag: 'p'
    })

    .declareMethod('render', function (options) {
      var field_json = options.field_json || {};
      return this.changeState({
        value: field_json.value || field_json.default || ""
      });
    })

    .onStateChange(function () {
      this.element.innerHTML = this.state.value;
    })

    .declareMethod('getContent', function () {
      return {};
    })

    .declareMethod('checkValidity', function () {
      return true;
    });

}(window, rJS));