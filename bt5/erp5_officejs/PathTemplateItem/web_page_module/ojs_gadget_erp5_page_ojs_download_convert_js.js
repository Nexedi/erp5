/*global window, rJS, RSVP, jIO */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, jIO) {
  "use strict";

  var ATT_NAME = "data";


  function downloadFromBlob(gadget, blob, format) {
    var element = gadget.element,
      a = window.document.createElement("a"),
      url = window.URL.createObjectURL(blob),
      name = [
        gadget.state.doc.filename,
        format
      ].join('.');
    element.appendChild(a);
    a.style = "display: none";
    a.href = url;
    a.download = name;
    a.click();
    element.removeChild(a);
    window.URL.revokeObjectURL(url);
  }

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .allowPublicAcquisition('submitContent', function () {
      var gadget = this, format;

      return gadget.notifySubmitting()
        .push(function () {
          return gadget.getDeclaredGadget('form_view');
        })
        .push(function (form_gadget) {
          return form_gadget.getContent();
        })
        .push(function (result) {
          format = result.format;
          if (format === gadget.state.doc.mime_type) {
            return gadget.jio_getAttachment(gadget.state.jio_key, ATT_NAME);
          }
          return gadget.getDeclaredGadget('ojs_cloudooo')
            .push(function (ojs_cloudooo) {
              return ojs_cloudooo.getConvertedBlob({
                jio_key: gadget.state.jio_key,
                format: format,
                mime_type: gadget.state.doc.mime_type
              });
            });
        })
        .push(function (result) {
          if (window.Array.isArray(result)) {
            return gadget.redirect({
              'command': 'display',
              'options': {
                'page': 'ojs_sync',
                'auto_repair': true,
                'redirect': jIO.util.stringify({
                  'command': 'display',
                  'options': {
                    'page': 'ojs_download_convert',
                    'jio_key': gadget.state.jio_key
                  }
                })
              }
            });
          }
          return downloadFromBlob(gadget, result, format);
        })
        .push(function () {
          return gadget.notifySubmitted();
        }, function (error) {
          if (error instanceof jIO.util.jIOError) {
            return gadget.notifySubmitted({
              message: "Conversion Failed",
              status: "error"
            });
          }
          throw error;
        })
       .push(function () {
          return;
        });
    })

    .declareMethod("triggerSubmit", function () {
      return this.element.querySelector('button[type="submit"]').click();
    })

    .declareMethod("render", function (options) {
      var gadget = this;
      return gadget.jio_get(options.jio_key)
        .push(function (doc) {
          return gadget.changeState({
            jio_key: options.jio_key,
            doc: doc
          });
        });
    })

    .onStateChange(function () {
      var gadget = this,
        format = gadget.state.doc.mime_type,
        format_list = [format];
      return gadget.getSetting('conversion_dict', {})
        .push(function (conversion_dict) {
          var dict = window.JSON.parse(conversion_dict), i;
          if (dict.hasOwnProperty(format)) {
            for (i = 0; i < dict[format].length; i += 1) {
              if (window.Array.isArray(dict[format][i])) {
                format_list.push(dict[format][i][1]);
              } else {
                format_list.push(dict[format][i]);
              }
            }
          }
          return gadget.getDeclaredGadget('form_view');
        })
        .push(function (form_gadget) {
          return form_gadget.render({
            erp5_document: {
              "_embedded": {"_view": {
                "_actions": {"put": {}},
                "form_id": {},
                "dialog_id": {},
                "my_format": {
                  "title": "Format Avaible",
                  "required": 1,
                  "editable": 1,
                  "key": "format",
                  "value": gadget.state.doc.mime_type,
                  "items": format_list,
                  "type": "ListField"
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
              title: "Download",
              group_list: [[
                "center",
                [["my_format"]]
              ]]
            }
          });
        })
        .push(function () {
          return RSVP.all([
            gadget.getUrlFor({
              command: 'display',
              options: {'jio_key': gadget.state.jio_key}
            }),
            gadget.getUrlFor({command: 'selection_previous'}),
            gadget.getUrlFor({command: 'selection_next'})
          ]);
        })
        .push(function (url_list) {
          return gadget.updateHeader({
            page_title: "Download",
            selection_url: url_list[0],
            previous_url: url_list[1],
            next_url: url_list[2],
            save_action: true
          });
        });
    });
}(window, rJS, RSVP, jIO));