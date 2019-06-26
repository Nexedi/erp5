/*global window, rJS, RSVP, URI */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, document, RSVP, rJS,
           XMLHttpRequest, location, console) {
  "use strict";
  function download(context, evt) {
    var link = document.createElement('a');
    link.download = "ingestion_tool.zip";
    link.href = window.location.origin + "/erp5/data_stream_module/embulk_download_script/getData";
    link.click();
  }

  rJS(window)
    .allowPublicAcquisition('setFillStyle', function () {
      return {
        height: '100%',
        width: '100%'
      };
    })
    .declareJob('download', function (evt) {
      return download(this, evt);
    })
    .declareMethod("render", function () {
      return this;
    })
    .onEvent('submit', function (evt) {
      if (evt.target.name === 'download') {
        return this.download(evt);
      } else {
        throw new Error('Unknown form');
      }
    });
}(window, document, RSVP, rJS,
  XMLHttpRequest, location, console));