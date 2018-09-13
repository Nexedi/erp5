/*global window, rJS, jIO, Handlebars, navigator, MediaRecorder, Blob, loopEventListener*/
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS) {
  "use strict";
  rJS(window)
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareMethod('render', function (params) {
      var gadget = this,
        a = gadget.element.querySelector("a");
      a.setAttribute('id', params.value.target_type);
      a.textContent = params.value.textContent || "";

      if (params.value.target_type === "download") {
        a.setAttribute('download', params.value.textContent);
      }
      if (!params.value.direct_url) {
        return gadget.getUrlFor({
          command: 'display',
          options: {page: params.value.target}
        })
          .push(function (url) {
            a.setAttribute('href', url);
          });
      }
      a.setAttribute('href', params.value.direct_url);

    })
    .declareMethod('getContent', function () {
      return {};
    });

}(window, rJS));