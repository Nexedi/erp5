/*global window, rJS, URI, document */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, document) {
  "use strict";

  rJS(window)
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlForList", "getUrlForList")
    .declareMethod("render", function (options) {
      return this.changeState(options);
    })
    .onStateChange(function () {
      return this.updateHeader({
        page_title: 'Wendelin Data Lake Sharing Platform'
      });
    })
    .declareService(function () {
      var gadget = this,
        url_parameter_list = [];
      url_parameter_list.push({
        command: 'display'
      });
      url_parameter_list.push({
        command: 'display_stored_state',
        options: {page: 'download'}
      });
      url_parameter_list.push({
        command: 'display_stored_state',
        options: {page: 'fifdata'}
      });
      url_parameter_list.push({
        command: 'display_stored_state',
        options: {page: 'register'}
      });
      url_parameter_list.push({
        command: 'display_stored_state',
        options: {page: 'ebulk_doc'}
      });
      return gadget.getUrlForList(url_parameter_list)
        .push(function (url_list) {
          document.querySelector("#home_link").href = url_list[0];
          document.querySelector("#download_link").href = url_list[1];
          document.querySelector("#download_ebulk_link").href = url_list[1];
          document.querySelector("#dataset_link").href = url_list[2];
          document.querySelector("#dataset_link_img").href = url_list[2];
          document.querySelector("#register_link").href = url_list[3];
          document.querySelector("#documentation_link").href = url_list[4];
        })
        .push(undefined, function (error) {
          throw error;
        });
    });

}(window, rJS, document));