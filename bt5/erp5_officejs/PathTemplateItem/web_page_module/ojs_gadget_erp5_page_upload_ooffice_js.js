/*global window, rJS, RSVP, jIO */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, jIO) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("jio_post", "jio_post")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("redirect", "redirect")
    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .allowPublicAcquisition('jio_putAttachment', function () {
      var gadget = this,
        file_name,
        jio_key,
        data,
        destination_mime_type = 'docy',
        source_mime_type = 'docx';

      return gadget.notifySubmitting()
        .push(function () {
          return gadget.getDeclaredGadget('form_view');
        })
        .push(function (form_gadget) {
          return RSVP.all([
            form_gadget.getContent(),
            gadget.getSetting('portal_type')
          ]);
        })
        .push(function (result) {
          file_name = result[0].file.file_name.split(source_mime_type)[0];
          data = jIO.util.dataURItoBlob(result[0].file.url);
          return gadget.jio_post({
            title: file_name,
            portal_type: result[1],
            content_type: "application/x-asc-text",
            filename: file_name
          });
        })
        .push(function (doc_id) {
          jio_key = doc_id;
          return gadget.jio_putAttachment(jio_key, "data?docx", data);
        })
        .push(function () {
          return gadget.redirect({command: 'display', options: {jio_key: jio_key}});
        });
    })

    .declareMethod("triggerSubmit", function () {
      return this.element.querySelector('button[type="submit"]').click();
    })

    .declareMethod("render", function (options) {
      var gadget = this;
      return gadget.getDeclaredGadget('form_view')
        .push(function (form_gadget) {
          var editable = gadget.state.content_editable;
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
                  "title": "Format",
                  "default": "docx",
                  "editable": 0
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
          })
          .push(function () {
            return RSVP.all([
              gadget.getUrlFor({command: 'history_previous'}),
              gadget.getUrlFor({command: 'selection_previous'}),
              gadget.getUrlFor({command: 'selection_next'})
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
    });
}(window, rJS, RSVP, jIO));