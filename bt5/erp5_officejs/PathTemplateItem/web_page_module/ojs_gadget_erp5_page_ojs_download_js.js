/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, jIO, rJS, RSVP, Blob, DOMParser) {

  "use strict";

  function downloadJsPdf(gadget, html) {
    var doc = new jsPDF();
    var specialElementHandlers = {};

    doc.fromHTML(html.lastChild.innerHTML, 15, 15, {
      'width': 170,
      'elementHandlers': specialElementHandlers
    });
    doc.save('sample-content.pdf');
  }

//////////////////////////////////////////////////////
  
  function downloadTxt(gadget) {
    var element = gadget.element,
      a = window.document.createElement("a"),
      url = window.URL.createObjectURL(new Blob([gadget.state.doc.text_content], {type: 'text/plain'})),
      name_list = [gadget.state.doc.title, "txt"];
    element.appendChild(a);
    a.style = "display: none";
    a.href = url;
    a.download = name_list.join('.');
    a.click();
    element.removeChild(a);
    window.URL.revokeObjectURL(url);
  }
//////
  function downloadFromBlob(gadget, blob, format) {
    var element = gadget.element,
      a = window.document.createElement("a"),
      url = window.URL.createObjectURL(blob),
      name_list = gadget.state.doc.filename.split('.');
    name_list[name_list.length - 1] = format;
    element.appendChild(a);
    a.style = "display: none";
    a.href = url;
    a.download = name_list.join('.');
    a.click();
    element.removeChild(a);
    window.URL.revokeObjectURL(url);
  }

  function downloadFromFormat(gadget, format) {
    return gadget.getDeclaredGadget('ojs_cloudooo')
      .push(function (ojs_cloudooo) {
        return ojs_cloudooo.getConvertedBlob({
          jio_key: gadget.state.jio_key,
          format: format,
          redirect: jIO.util.stringify({
            'command': 'display',
            'options': {
              'page': 'ojs_download',
              'jio_key': gadget.state.jio_key,
              'download_format': format
            }
          })
        });
      })
      .push(function (result) {
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
      });
  }
//////
  function addFileName(gadget, format) {
    return new RSVP.Queue()
    .push(function () {
      var doc = gadget.state.doc;
      var name_list = [doc.title, "html"];
      doc.filename = name_list.join('.');
      return doc;
    })
    .push(function (doc) {
      gadget.jio_put(gadget.state.jio_key, doc);
    })
    .push(function () {
      downloadFromFormat(gadget, format);
    });

  }
  rJS(window)
  
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("removeSetting", "removeSetting")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")
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
          return form_gadget.getContent();
        })
        .push(function (result) {
          if (result.format == "txt") { downloadTxt(gadget); }
          else {
            return new RSVP.Queue()
            .push(function () {
              addFileName(gadget, result.format);
            });
          }
        });
    })

    .declareMethod("triggerSubmit", function () {
      return this.element.querySelector('button[type="submit"]').click();
    })
  
    .declareMethod("render", function (options) {

      var gadget = this;
      return new RSVP.Queue()
      .push(function () {
        return RSVP.all([
          gadget.jio_get(options.jio_key),
          gadget.getSetting("file_extension", "")
        ]);
      })
      .push(function (result) {
        return gadget.changeState({
          jio_key: options.jio_key,
          doc: result[0],
          format: result[1],
          download_format: options.download_format,
          editable: options.editable
        });
      });
    })

    .onStateChange(function () {
      var gadget = this, format_list;
      return gadget.getSetting('conversion_dict', {})
        .push(function (conversion_dict) {
          format_list = window.JSON.parse(conversion_dict)[gadget.state.format];
          format_list.push(gadget.state.format);
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
                  "value": gadget.state.format,
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
            next_url: url_list[2]
          });
        })
        .push(function () {
          if (gadget.state.download_format) {
            return downloadFromFormat(gadget, gadget.state.download_format);
          }
        });
    });

}(window, jIO, rJS, RSVP, Blob, DOMParser));
