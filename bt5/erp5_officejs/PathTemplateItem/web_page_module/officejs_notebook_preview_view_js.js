/*global window, rJS, RSVP, Blob, jIO */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, Blob, jIO) {
  "use strict";

  rJS(window)

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////

    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod('preRenderDocument', function (parent_options) {
      var gadget = this, document;
      return gadget.jio_get(parent_options.jio_key)
        .push(function (doc) {
          document = doc;
          return gadget.getUrlFor({command: 'history_previous'});
        })
        .push(function (url) {
          document.header_dict = { "page_title": document.title,
                                   "selection_url": url
                                 };
          return document;
        });
    })

    .declareMethod('handleSubmit', function (content_dict, parent_options) {
      return {};
    });

}(window, rJS, RSVP, Blob, jIO));