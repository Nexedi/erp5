/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
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
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", 'notifySubmitted')
    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .allowPublicAcquisition('jio_putAttachment', function () {
      var gadget = this,
        file_name,
        jio_key,
        data,
        conversion_gadget,
        destination_mime_type = 'docy',
        source_mime_type = 'docx';

      return gadget.notifySubmitting()
        .push(function () {
          return RSVP.all([
            gadget.getDeclaredGadget('form_view'),
            gadget.getDeclaredGadget('conversion')
          ]);
        })
        .push(function (result) {
          conversion_gadget = result[1];
          return result[0].getContent();
        })
        .push(function (content) {
          file_name = content.file.file_name.split(source_mime_type)[0];
          return RSVP.all([
            conversion_gadget.convert(content.file.url.split('base64,')[1], source_mime_type, destination_mime_type),
            gadget.getSetting('portal_type')
          ]);
        })
        .push(function (result) {
          return RSVP.all([
            gadget.jio_post({title: file_name, portal_type: result[1], content_type: "application/x-asc-text", filename: file_name}),
            conversion_gadget.b64toBlob(result[0], "application/zip")
          ]);
        })
        .push(function (result) {
          jio_key = result[0];
          return gadget.jio_putAttachment(jio_key, 'data', result[1]);
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