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
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("getSetting", "getSetting")

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
        portal_type = parent_options.action_options.parent_portal_type,
        portal_type_dict,
        data,
        blob,
        property;
      delete content_dict.dialog_method;
      delete content_dict.text_content;
      for (property in content_dict) {
        if (content_dict.hasOwnProperty(property)) {
          document[property] = content_dict[property];
        }
      }
      return gadget.getSetting(portal_type.replace(/ /g, '_').toLowerCase() + "_dict")
        .push(function (result) {
          portal_type_dict = window.JSON.parse(result);
          return gadget.jio_getAttachment(parent_options.action_options.jio_key, "data");
        })
        .push(undefined, function (error) {
          if (error.status_code === 404) {
            return new Blob([''], {type: portal_type_dict.blob_type});
          }
          throw new Error(error);
        })
        .push(function (result) {
          blob = result;
          blob.name = parent_options.action_options.jio_key;
          return gadget.jio_post(document);
        })
        .push(function (jio_key) {
          return gadget
            .jio_putAttachment(jio_key, 'data', blob);
        })
        .push(function (jio_key) {
          return_submit_dict.notify.message = "Clone Document Created";
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