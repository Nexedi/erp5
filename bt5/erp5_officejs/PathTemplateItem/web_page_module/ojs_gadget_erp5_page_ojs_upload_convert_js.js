/*global window, rJS, RSVP, jIO, JSON */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, jIO, JSON) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    .declareAcquiredMethod("jio_post", "jio_post")
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
          var file_name_list, file_name, from, jio_key, data, to,
              att_id;
          if (result[0].file !== undefined) {
            file_name_list = result[0].file.file_name.split('.');
            from = file_name_list.pop();
            if (gadget.state.upload.hasOwnProperty(from)) {
              to = gadget.state.upload[from];
              att_id = "data?from=" + from + "&to=" + to;
            } else if (from === result[3]) {
              att_id = "data";
            } else {
              return gadget.notifySubmitted({
                message: "Can convert, avaible format : " +
                    gadget.state.upload,
                status: "error"
              });
            }
            file_name = file_name_list.join('.');
            data = jIO.util.dataURItoBlob(result[0].file.url);
            return gadget.jio_post({
              title: file_name,
              portal_type: result[1],
              content_type: result[2],
              filename: file_name
            })
              .push(function (doc_id) {
                jio_key = doc_id;
                return gadget.jio_putAttachment(jio_key, "data?from=" + from + '?to=' + gadget.state.upload_extension, data);
              })
              .push(function () {
                return jio_key;
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
      var gadget = this;
      return gadget.getSetting('upload_dict')
        .push(function (upload_dict) {
          return gadget.changeState({
            upload: upload_dict
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
            gadget.getUrlFor({command: 'history_previous'})
          ]);
        })
        .push(function (url_list) {
          return gadget.updateHeader({
            page_title: "Upload File",
            selection_url: url_list[0],
            previous_url: url_list[1],
            next_url: url_list[2]
          });
        });
    });
}(window, rJS, RSVP, jIO, JSON));