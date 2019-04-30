/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  rJS(window)

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_post", "jio_post")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("createDocument", function (options) {
      var gadget = this,
        doc = {
          title: "Untitled Post",
          portal_type: options.portal_type,
          parent_relative_url: options.parent_relative_url
        },
        key,
        doc_key;
      for (key in options) {
        if (options.hasOwnProperty(key)) {
          if (key.startsWith("my_")) {
            doc_key = key.replace("my_", "");
            doc[doc_key] = options[key];
          }
        }
      }
      return gadget.jio_post(doc);
    })

    .declareMethod("preRenderDocument", function (parent_options) {
      return {title: "Untitled Post"};
    })

    .declareMethod('handleSubmit', function (content_dict, parent_options) {
      var document = {
        my_title: parent_options.doc.title,
        portal_type: parent_options.parent_options.portal_type,
        parent_relative_url: parent_options.parent_options.parent_relative_url
      }, property;
      delete content_dict.dialog_method;
      for (property in content_dict) {
        if (content_dict.hasOwnProperty(property)) {
          document['my_' + property] = content_dict[property];
        }
      }
      document.my_source_reference = parent_options.parent_options.my_source_reference;
      return this.createDocument(document);
    });

}(window, rJS, RSVP));