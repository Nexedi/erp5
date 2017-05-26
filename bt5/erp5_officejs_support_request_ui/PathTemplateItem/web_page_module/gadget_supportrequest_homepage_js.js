/*global window, rJS */
/*jslint indent: 2, maxerr: 3, nomen: true */
(function (window, rJS) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // handle acquisition
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("updateHeader", "updateHeader")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function () {
      var gadget = this;
      return gadget.updateHeader({
        page_title: 'Home'
      })
        .push(function () {
          return gadget.translateHtml(gadget.element.innerHTML);
        })
        .push(function (my_translated_html) {
          gadget.element.innerHTML = my_translated_html;
          return gadget.jio_getAttachment('support_request_module', 'links');
        })
        .push(function (links) {
          // var fast_create_url = links._links.action_object_new_content_action.href;
          var fast_create_url = links._links.view[1].href;
          return gadget.getUrlFor({
            command: 'display',
            options: {
              jio_key: "support_request_module",
              view: fast_create_url,
              editable: true,
              page: 'support_request_wrapper'
            }
          });
        })
        .push(function (url) {
          gadget.element.querySelector('.add').href = url;
        });
    });
}(window, rJS));