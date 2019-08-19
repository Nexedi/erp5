/*global window, document, rJS, RSVP, jIO */
/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80  */
(function (window, document, rJS, RSVP, jIO) {
  "use strict";

  var ATT_NAME = "data";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_post", "jio_post")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("redirect", "redirect")
    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .allowPublicAcquisition('submitContent', function () {
      var gadget = this;
      return gadget.notifySubmitting()
        .push(function () {
          return gadget.getDeclaredGadget('form_view');
        })
        .push(function (form_view_gadget) {
          return form_view_gadget.getDeclaredGadget("erp5_pt_gadget");
        })
        .push(function (erp5_pt_gadget) {
          return erp5_pt_gadget.getDeclaredGadget("erp5_form");
        })
        .push(function (form_gadget) {
          return RSVP.all([
            form_gadget.getContent(),
            gadget.getSetting('portal_type'),
            gadget.getSetting('content_type'),
            gadget.getSetting('file_extension'),
            gadget.getSetting('parent_relative_url')
          ]);
        })
        .push(function (result) {
          var file_name_list, from, jio_key, data, to, att_name = ATT_NAME,
            filename;
          if (result[0].file !== undefined) {
            file_name_list = result[0].file.file_name.split('.');
            from = file_name_list.pop();
            file_name_list.push(result[3]);
            filename = file_name_list.join('.');
            data = jIO.util.dataURItoBlob(result[0].file.url);
            if (gadget.state.upload.hasOwnProperty(from)) {
              if (result[3] !== from) {
                att_name = from;
              }
              to = gadget.state.upload[from];
              return gadget.jio_post({
                title: filename,
                portal_type: result[1],
                content_type: result[2],
                filename: filename,
                parent_relative_url: result[4]
              })
                .push(function (doc_id) {
                  jio_key = doc_id;
                  return gadget.jio_putAttachment(jio_key, att_name, data);
                })
                .push(function () {
                  if (result[3] === from) {
                    return;
                  }
                  return gadget.getDeclaredGadget('ojs_cloudooo')
                    .push(function (ojs_cloudooo) {
                      return RSVP.all([
                        ojs_cloudooo.putCloudoooConvertOperation({
                          status: "convert",
                          from: from,
                          to: to,
                          id: jio_key,
                          name: att_name,
                          to_name: ATT_NAME
                        }),
                        ojs_cloudooo.putCloudoooConvertOperation({
                          status: "converted",
                          from: to,
                          to: from,
                          id: jio_key,
                          name: ATT_NAME
                        })
                      ]);
                    })
                    .push(function () {
                      return gadget.redirect({
                        'command': 'display',
                        'options': {
                          'page': 'ojs_sync',
                          'auto_repair': true
                        }
                      });
                    });
                })
                .push(function () {
                  return gadget.redirect({
                    'command': 'display',
                    'options': {
                      'jio_key': jio_key
                    }
                  });
                });
            }
            return gadget.notifySubmitted({
              message: "Can not convert, use format : " +
                window.Object.keys(gadget.state.upload).join(', '),
              status: "error"
            });
          }
          return gadget.notifySubmitted({
            message: "File is required",
            status: "error"
          });
        })
        .push(function () {
          return;
        });
    })

    .declareMethod("triggerSubmit", function () {
      return this.element.querySelector('button[type="submit"]').click();
    })

    .declareMethod("render", function () {
      var gadget = this, upload_document_form;
      return gadget.getSetting('upload_document_form')
        .push(function (result) {
          upload_document_form = result;
          return gadget.getSetting('upload_dict');
        })
        .push(function (upload_dict) {
          return gadget.changeState({
            upload: window.JSON.parse(upload_dict),
            upload_document_form: upload_document_form
          });
        });
    })

    .onStateChange(function () {
      var fragment = document.createElement('div'),
        gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return gadget.declareGadget("gadget_officejs_common_util.html");
        })
        .push(function (gadget_util) {
          return gadget_util.getDialogFormDefinition(gadget.state
                                                     .upload_document_form);
        })
        .push(function (form_definition) {
          while (gadget.element.firstChild) {
            gadget.element.removeChild(gadget.element.firstChild);
          }
          gadget.element.appendChild(fragment);
          return gadget.declareGadget("gadget_officejs_form_view.html",
                                      {element: fragment, scope: 'form_view'})
            .push(function (form_view_gadget) {
              return form_view_gadget.render({
                doc: { title: form_definition.title,
                       format: window.Object.keys(gadget.state.upload)
                      .join(', ') },
                //url and form type should come in form defenition, which should
                //get those values via getFormInfo using dialog_category setting
                child_gadget_url: 'gadget_erp5_pt_form_dialog.html',
                form_type: 'dialog',
                form_definition: form_definition,
                view: "view"
              });
            });
        });
    });
}(window, document, rJS, RSVP, jIO));