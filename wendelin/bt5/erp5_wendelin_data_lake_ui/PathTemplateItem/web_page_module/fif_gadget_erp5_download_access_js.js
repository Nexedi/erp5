/*global window, rJS, RSVP, URI */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, document, RSVP, rJS,
           XMLHttpRequest, location, console) {
  "use strict";
  function download_tool(context, evt) {
    var link = document.createElement('a');
    link.href = window.location.origin + "/erp5/web_site_module/fif_data_runner/#/?page=download";
    link.click();
  }

  rJS(window)
    .allowPublicAcquisition('setFillStyle', function () {
      return {
        height: '100%',
        width: '100%'
      };
    })
    .declareJob('download_tool', function (evt) {
      return download_tool(this, evt);
    })
    .declareMethod("render", function (reference) {
      var html = "pull <i>" + reference + "</i>";
      if (reference === undefined)
        html = "push <i>my-data-set</i>";
      return this.changeState({"dataset_reference" : html});
    })
    .declareService(function () {
      document.getElementById("dataset_reference").innerHTML = this.state.dataset_reference;
    })
    .onEvent('submit', function (evt) {
      if (evt.target.name === 'download-tool') {
        return this.download_tool(evt);
      } else {
        throw new Error('Unknown form');
      }
    });
}(window, document, RSVP, rJS,
  XMLHttpRequest, location, console));