/*global window, rJS, RSVP, jIO */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, jIO) {
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
        .push(function (form_gadget) {
          return RSVP.all([
            form_gadget.getContent(),
            gadget.getSetting('portal_type'),
            gadget.getSetting('content_type'),
            gadget.getSetting('file_extension')
          ]);
        })
        .push(function (result) {
          var file_name, from, jio_key, data, to;
          if (result[0].file !== undefined) {
            file_name = result[0].file.file_name;
            from = file_name.split('.').pop();
            data = jIO.util.dataURItoBlob(result[0].file.url);
            if (gadget.state.upload.hasOwnProperty(from)) {
              to = gadget.state.upload[from];
              return gadget.jio_post({
                title: file_name,
                portal_type: result[1],
                content_type: result[2],
                filename: file_name,
                mime_type: from
              })
                .push(function (doc_id) {
                  jio_key = doc_id;
                  return gadget.jio_putAttachment(jio_key, ATT_NAME, data);
                })
                .push(function () {
                  if (result[3] === from) {
                    return;
                  }
                  return gadget.getDeclaredGadget('ojs_cloudooo')
                    .push(function (ojs_cloudooo) {
                      return ojs_cloudooo.putCloudoooConvertOperation({
                        status: "convert",
                        from: from,
                        to: to,
                        id: jio_key,
                        name: ATT_NAME
                      });
                    });
                })
                .push(function () {
                  return gadget.redirect({
                    'command': 'display',
                    'options': {
                      'page': 'ojs_sync',
                      'auto_repair': true,
                      'redirect': jIO.util.stringify({
                        'command': 'display',
                        'options': {'jio_key': jio_key}
                      })
                    }
                  });
                });
            }
            return gadget.notifySubmitted({
              message: "Can not convert, use format : " +
                window.Object.keys(gadget.state.upload).join(', '),
              status: "error"
            })
              .push(function () {
                return;
              });
          }
          return gadget.notifySubmitted({
            message: "File is required",
            status: "error"
          })
            .push(function () {
              return;
            });
        });
    })

    .declareMethod("triggerSubmit", function () {
      return this.element.querySelector('button[type="submit"]').click();
    })

    .declareMethod("render", function () {
      var gadget = this;
      return gadget.getSetting('upload_dict')
        .push(function (upload_dict) {
          return gadget.changeState({
            upload: window.JSON.parse(upload_dict)
          });
        });
    })

    .onStateChange(function () {
      var gadget = this;
      return gadget.getDeclaredGadget('form_view')
        .push(function (form_gadget) {
          return form_gadget.render({
            erp5_document: {
              "_embedded": {"_view": {
                "_actions": {"put": {}},
                "form_id": {},
                "dialog_id": {},
                "my_file": {
                  "description": "",
                  "title": "File",
                  "default": "",
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "file",
                  "hidden": 0,
                  "type": "FileField"
                },
                "your_format": {
                  "title": "Format Avaible",
                  "required": 0,
                  "editable": 0,
                  "default": window.Object.keys(gadget.state.upload).join(', '),
                  "type": "StringField"
                }
              }},
              "_links": {
                "type": {
                  // form_list display portal_type in header
                  name: ""
                }
              }
            },
            form_definition: {
              title: "Upload",
              group_list: [[
                "center",
                [["my_file"], ["your_format"]]
              ]]
            }
          });
        })
        .push(function () {
          return RSVP.all([
            gadget.getUrlFor({command: 'display'})
          ]);
        })
        .push(function (url_list) {
          return gadget.updateHeader({
            page_title: "Upload File",
            selection_url: url_list[0]
          });
        });
    });
}(window, rJS, RSVP, jIO));