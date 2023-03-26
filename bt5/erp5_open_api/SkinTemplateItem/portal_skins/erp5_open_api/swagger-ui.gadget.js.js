/*jslint nomen: true, indent: 2 */
/*global window, rJS, SwaggerUIBundle */
(function (window, rJS, SwaggerUIBundle) {
  'use strict';

  rJS(window)
    .declareMethod('render', function (options) {
      var state_dict = {
        key: options.key,
        url: options.openapi_url
      };
      return this.changeState(state_dict);
    })
    .onStateChange(function (modification_dict) {
      var queue = new RSVP.Queue();
      if (modification_dict.hasOwnProperty('url')) {
        SwaggerUIBundle({
          url: modification_dict.url,
          dom_id: '#swagger-ui'
        });
      }
      return queue;
    })
    .declareMethod('getContent', function () {
      return {};
    });
})(window, rJS, window['SwaggerUIBundle']);
