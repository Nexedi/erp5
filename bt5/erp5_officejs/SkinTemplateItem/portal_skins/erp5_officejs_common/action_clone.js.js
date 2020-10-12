/*global window, rJS, RSVP, jIO */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, jIO) {
  "use strict";

  rJS(window)

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_post", "jio_post")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("jio_allAttachments", "jio_allAttachments")

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
        all_attachments,
        promise_list = [],
        parent_jio_key = parent_options.action_options.jio_key,
        jio_key;
      return gadget.jio_allAttachments(parent_jio_key)
        .push(function (result) {
          var property;
          all_attachments = result;
          return gadget.jio_post(document);
        })
        .push(function (result_jio_key) {
          var attachment_id;
          jio_key = result_jio_key;
          for (attachment_id in all_attachments) {
            if (all_attachments.hasOwnProperty(attachment_id)) {
              promise_list.push(gadget.jio_getAttachment(parent_jio_key, attachment_id));
            }
          }
          return RSVP.all(promise_list);
        })
        .push(function (result_list) {
          var i;
          promise_list = [];
          for (i = 0; i < result_list.length; i += 1) {
            promise_list.push(gadget.jio_putAttachment(jio_key, Object.keys(all_attachments)[i], result_list[i]));
          }
          return RSVP.all(promise_list);
        })
        .push(function () {
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

}(window, rJS, RSVP, jIO));