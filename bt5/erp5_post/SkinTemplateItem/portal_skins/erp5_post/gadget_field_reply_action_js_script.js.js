/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  rJS(window)

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_post", "jio_post")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("preRenderDocument", function (parent_options) {
      var gadget = this;
      return gadget.jio_get(parent_options.jio_key)
      .push(function (parent_document) {
        var title = parent_document.title;
        if (!title.startsWith('Re: ')) { title = 'Re: ' + parent_document.title; }
        return {
          title: title,
          parent_relative_url: parent_document.parent_relative_url,
          portal_type: parent_document.portal_type,
          source_reference: parent_document.source_reference
        };
      });
    })

    .declareMethod('handleSubmit', function (content_dict, parent_options) {
      var gadget = this,
        document = parent_options.doc,
        property;
      delete content_dict.dialog_method;
      for (property in content_dict) {
        if (content_dict.hasOwnProperty(property)) {
          document[property] = content_dict[property];
        }
      }
      return gadget.jio_post(document);
    });

}(window, rJS, RSVP));