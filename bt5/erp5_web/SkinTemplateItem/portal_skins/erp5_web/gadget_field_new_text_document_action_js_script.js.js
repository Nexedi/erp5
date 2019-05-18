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

    .declareMethod("preRenderDocument", function (parent_options) {
      return {title: "Untitled Document"};
    })

    .declareMethod('handleSubmit', function (content_dict, parent_options) {
      var gadget = this,
        document = {
          title: parent_options.doc.title,
          //hardcoded portal_type and relative url (because this action is 'new Text Document' on 'web_page_module')
          //or, we can get those values from parent_options.form_definition if needed
          portal_type: "Web Page",
          parent_relative_url: "web_page_module"
        }, property;
      delete content_dict.dialog_method;
      for (property in content_dict) {
        if (content_dict.hasOwnProperty(property)) {
          document[property] = content_dict[property];
        }
      }
      return gadget.jio_post(document);
    });

}(window, rJS, RSVP));