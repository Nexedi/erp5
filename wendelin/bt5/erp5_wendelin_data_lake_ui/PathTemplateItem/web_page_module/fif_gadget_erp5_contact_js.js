/*global window, rJS, UriTemplate */
/*jslint indent: 2, maxerr: 3, nomen: true */
(function (window, rJS, UriTemplate) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // handle acquisition
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("updateHeader", "updateHeader")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
     .declareMethod("render", function () {
      var gadget = this;
      return gadget.updateHeader({page_title: 'Contact us'})
        .push(function () {
          return gadget.translateHtml(gadget.element.innerHTML);
        })
        .push(function (my_translated_html) {
          gadget.element.innerHTML = my_translated_html;
        });
    })

}(window, rJS, UriTemplate));