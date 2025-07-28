/*global window, rJS, RSVP, URI */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, document, RSVP, rJS,
           XMLHttpRequest, location, console) {
  "use strict";

  rJS(window)
    .declareAcquiredMethod("getUrlForList", "getUrlForList")
    .allowPublicAcquisition('setFillStyle', function () {
      return {
        height: '100%',
        width: '100%'
      };
    })
    .declareMethod("render", function (reference) {
      var html = "pull <i>" + reference + "</i>";
      if (reference === undefined)
        html = "push <i>my-data-set</i>";
      return this.changeState({"dataset_reference" : html});
    })
    .declareService(function () {
      var gadget = this,
        url_parameter_list = [];
      document.getElementById("dataset_reference").innerHTML = this.state.dataset_reference;
      url_parameter_list.push({
        command: 'display_stored_state',
        options: {page: 'download'}
      });
      url_parameter_list.push({
        command: 'display_stored_state',
        options: {page: 'register'}
      });
      return gadget.getUrlForList(url_parameter_list)
        .push(function (url_list) {
          document.querySelector("#download_link").href = url_list[0];
          document.querySelector("#register_link").href = url_list[1];
        })
        .push(undefined, function (error) {
          throw error;
        });
    });
}(window, document, RSVP, rJS,
  XMLHttpRequest, location, console));