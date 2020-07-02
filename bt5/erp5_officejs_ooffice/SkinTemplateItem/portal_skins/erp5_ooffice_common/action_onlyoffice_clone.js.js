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
        content_editable,
        filename,
        extension,
        blob_type,
        base_blob,
        data,
        clone_jio_key,
        ojs_cloudooo_gadget,
        property;
      delete content_dict.dialog_method;
      for (property in content_dict) {
        if (content_dict.hasOwnProperty(property)) {
          document[property] = content_dict[property];
        }
      }
      return gadget.getSetting("file_extension")
        .push(function (file_extension) {
          extension = file_extension;
          filename = document.filename;
          if (!filename) {
            filename = "default." + file_extension;
          }
          content_editable = document.content_type === undefined ||
            document.content_type.indexOf("application/x-asc") === 0;
          if (!content_editable) {
            return gadget.jio_getAttachment(parent_options.action_options.jio_key, "data");
          }
          return gadget.declareGadget("gadget_ojs_cloudooo.html")
            .push(function (ojs_cloudooo) {
              ojs_cloudooo_gadget = ojs_cloudooo;
              return ojs_cloudooo.getConvertedBlob({
                jio_key: parent_options.action_options.jio_key,
                format: file_extension, //state_dict.mime_type,
                filename: filename
              });
            });
        })
        .push(undefined, function (error) {
          if (error instanceof jIO.util.jIOError &&
              error.status_code === 404) {
            return new Blob();
          }
          throw error;
        })
        .push(function (blob) {
          base_blob = blob;
          return gadget.jio_post(document);
        })
        .push(function (jio_key) {
          clone_jio_key = jio_key;
          return gadget
            .jio_putAttachment(jio_key, 'data',
                               //jIO.util.dataURItoBlob(data))
                               base_blob)
            .push(function () {
              if (ojs_cloudooo_gadget) {
                return ojs_cloudooo_gadget
                  .putAllCloudoooConvertionOperation({
                    format: extension, //mime_type,
                    jio_key: jio_key
                  });
              }
            });
        })
        .push(function () {
          return_submit_dict.notify.message = "Clone Document Created";
          return_submit_dict.notify.status = "success";
          return_submit_dict.redirect.options = {
            jio_key: clone_jio_key,
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