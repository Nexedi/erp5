/*global document, window, rJS, RSVP, jIO, Blob */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (document, window, rJS, RSVP, jIO, Blob) {
  "use strict";

  rJS(window)

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod('render', function (options) {
      var gadget = this,
        state_dict = {
          doc: options.doc,
          form_definition: options.form_definition,
          child_gadget_url: options.child_gadget_url,
          options: options
        },
        portal_type_dict = options.form_definition.portal_type_dict,
        form_view_div = document.createElement('div'),
        extension,
        blob;

      return gadget.getSetting("file_extension")
        .push(function (file_extension) {
          if (file_extension.substring(file_extension.length - 1) == "y") {
            file_extension = file_extension.replace(/.$/, "x");
          }
          extension = file_extension;
          gadget.element.appendChild(form_view_div);
          return gadget.declareGadget("gadget_officejs_form_view.html",
                                      {element: form_view_div, scope: 'form_view'});
        })
        .push(function (form_view_gadget) {
          if (!state_dict.doc.filename) {
            state_dict.doc.filename = "default." + extension;
          }
          state_dict.mime_type = portal_type_dict.file_extension;
          if (options.doc.action) {
            return form_view_gadget.changeState(state_dict);
          }
          state_dict.content_editable = options.doc.content_type === undefined ||
            options.doc.content_type.indexOf("application/x-asc") === 0;
          return new RSVP.Queue()
            .push(function () {
              if (!state_dict.content_editable) {
                return gadget.jio_getAttachment(options.jio_key, "data");
              }
              return gadget.declareGadget("gadget_ojs_cloudooo.html")
                .push(function (ojs_cloudooo) {
                  return ojs_cloudooo.getConvertedBlob({
                    jio_key: options.jio_key,
                    format: state_dict.mime_type,
                    filename: options.doc.filename
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
              if (state_dict.content_editable) {
                return jIO.util.readBlobAsDataURL(blob);
              }
              return jIO.util.readBlobAsText(blob);
            })
            .push(function (result) {
              state_dict.data = result.target.result;
              state_dict.blob_type = portal_type_dict.blob_type;
              if (!state_dict.blob_type) {
                state_dict.blob_type = "application/x-asc-ooffice";
              }
              return form_view_gadget.changeState(state_dict);
            }, function (error) {
              console.log("ERROR rendering custom view");
              throw error;
            });
        });
    })

    .declareMethod("triggerSubmit", function () {
      var argument_list = arguments, gadget = this, child_gadget, view_gadget, content_dict, data, name_list;
      return gadget.notifySubmitting()
        .push(function (view_gadget) {
          return gadget.getDeclaredGadget('form_view');
        })
        .push(function (result) {
          view_gadget = result;
          return view_gadget.getDeclaredGadget('erp5_pt_gadget');
        })
        .push(function (result) {
          child_gadget = result;
          if (!child_gadget.state.editable) {
            return child_gadget.triggerSubmit(argument_list);
          }
          return child_gadget.getContent();
        })
        .push(function (result) {
          content_dict = result;
          if (!content_dict) { return; }
          data = content_dict.text_content;
          delete content_dict.text_content;
          name_list = view_gadget.state.doc.filename.split('.');
          if (name_list.pop() !== view_gadget.state.mime_type) {
            name_list.push(view_gadget.state.mime_type);
            content_dict.filename = name_list.join('.');
          }
          return gadget.getSetting("content_type");
        })
        .push(function (content_type) {
          content_dict.content_type = content_type;
          return child_gadget.submitContent(
            child_gadget.state.jio_key, undefined, content_dict
          );
        })
        .push(function () {
          return gadget
            .jio_putAttachment(child_gadget.state.jio_key, 'data',
                               jIO.util.dataURItoBlob(data))
            .push(function () {
              return gadget.declareGadget("gadget_ojs_cloudooo.html");
            })
            .push(function (cloudooo) {
              return cloudooo
                .putAllCloudoooConvertionOperation({
                  format: view_gadget.state.mime_type,
                  jio_key: child_gadget.state.jio_key
                });
            });
        }, function (error) {
          console.log(error);
          return gadget.notifySubmitted({
            message: "Submit failed",
            status: "error"
          });
        });
    });

}(document, window, rJS, RSVP, jIO, Blob));