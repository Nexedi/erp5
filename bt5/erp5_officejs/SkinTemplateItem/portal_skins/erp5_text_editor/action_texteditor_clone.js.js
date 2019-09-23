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
        return parent_document;
      });
    })

    .declareMethod('handleSubmit', function (content_dict, parent_options) {
      //must return a dict with:
      //notify: options_dict for notifySubmitted
      //redirect: options_dict for redirect
      var return_submit_dict = {
        notify: {
          message: "",
          status: ""
        },
        redirect: {
          command: 'display',
          options: {}
        }
      }, gadget = this,
        document = parent_options.doc,
        property;
      delete content_dict.dialog_method;
      for (property in content_dict) {
        if (content_dict.hasOwnProperty(property)) {
          document[property] = content_dict[property];
        }
      }
      return gadget.jio_post(document)
        .push(function (jio_key) {
          return_submit_dict.notify.message = "Data Updated";
          return_submit_dict.notify.status = "success";
          return_submit_dict.redirect.options = {
            jio_key: jio_key,
            editable: true
          };
          return return_submit_dict;
        }, function (error) {
          if (error instanceof jIO.util.jIOError) {
            return_submit_dict.notify.message = "Failure cloning document";
            return_submit_dict.notify.status = "error";
            return return_submit_dict;
          }
          throw error;
        });
    });

}(window, rJS, RSVP));