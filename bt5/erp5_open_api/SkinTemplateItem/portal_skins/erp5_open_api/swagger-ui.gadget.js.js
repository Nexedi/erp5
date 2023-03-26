/*jslint nomen: true, indent: 2 */
/*global window, rJS, SwaggerUIBundle */
(function (window, rJS, SwaggerUIBundle) {
  'use strict';

  rJS(window)
    .declareAcquiredMethod('notifySubmit', 'notifySubmit')
    .declareJob('deferNotifySubmit', function () {
      // Ensure error will be correctly handled
      return this.notifySubmit();
    })
    .declareAcquiredMethod('notifyChange', 'notifyChange')
    .declareJob('deferNotifyChange', function () {
      // Ensure error will be correctly handled
      return this.notifyChange();
    })
    .ready(function (context) {
      console.log('ready');
    })
    .declareMethod('render', function (options) {
      var state_dict = {
        key: options.key,
        url: options.openapi_url
      };
      console.log('render', options);
      return this.changeState(state_dict);
    })

    .onStateChange(function (modification_dict) {
      var queue = new RSVP.Queue(),
        gadget = this;
      console.log('onStateChange', modification_dict);
      if (modification_dict.hasOwnProperty('url')) {
        SwaggerUIBundle({
          url: modification_dict.url,
          dom_id: '#swagger-ui'
        });
      }
    })
    .declareMethod('getContent', function () {
      var form_data = {};
      if (this.state) {
        form_data[this.state.key] = this.editor.getValue();
      }
      return form_data;
    });
})(window, rJS, window['SwaggerUIBundle']);
