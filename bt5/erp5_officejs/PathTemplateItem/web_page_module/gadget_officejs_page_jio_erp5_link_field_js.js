/*global window, rJS, jIO, Handlebars, navigator, MediaRecorder, Blob, loopEventListener*/
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, jIO, RSVP, document) {
  "use strict";
  rJS(window)
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareMethod('render', function (params) {
      var gadget = this;
      var label = gadget.element.querySelector("label");
      label.setAttribute('for', params.value.target_type);
    
      return gadget.getUrlFor({command: 'display', options: {page: params.value.target}})
    
      .push(function (url) {
        var a = gadget.element.querySelector("a");
        a.setAttribute('href', url);
      });
    })
  .declareMethod('getContent', function () {
    return {};
  });

}(window, rJS, jIO, RSVP, document));