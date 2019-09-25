/*global window, rJS, RSVP, jIO, DOMParser, Blob */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, jIO, DOMParser, Blob) {
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
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("getSetting", "getSetting")
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
            gadget.getSetting('upload_dict'),
            gadget.getSetting('parent_relative_url')
          ]);
        })
        .push(function (result) {
          var file_name_list, data, filename, queue, filetype, jio_key;
          if (result[0].file !== undefined) {
            file_name_list = result[0].file.file_name.split('.');
            filetype = file_name_list.pop();
            if (filetype in window.JSON.parse(result[3])) {
              filename = file_name_list.join('.');
              data = jIO.util.dataURItoBlob(result[0].file.url);
              queue = new RSVP.Queue()
                .push(function () {
                  return jIO.util.readBlobAsText(data);
                })
                .push(function (evt) {
                  return evt.target.result;
                })
                .push(function (data_content) {
                  if (filetype === 'html') {
                    // In case the filetype is html, try looking for an elemnt
                    // with id `jsmd`, because iodide notebook saves the jsmd
                    // data in it.
                    var parser, htmlDoc;
                    parser = new DOMParser();
                    htmlDoc = parser.parseFromString(data_content, "text/html");
                    data_content = htmlDoc.getElementById('jsmd').textContent;
                    filetype = "txt";
                  }
                  return gadget.jio_post({
                    title: filename,
                    portal_type: result[1],
                    content_type: result[2],
                    parent_relative_url: result[4],
                    text_content: data_content,
                    filename: "default." + filetype
                  })
                  .push(function (result) {
                    jio_key = result;
                    return gadget.jio_putAttachment(
                      jio_key,
                      "data",
                      new Blob([data_content], {type: result[2]})
                    );
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
              return queue;
            }
            return gadget.notifySubmitted({
              message: "Wrong format, use format : " +
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
}(window, rJS, RSVP, jIO, DOMParser, Blob));