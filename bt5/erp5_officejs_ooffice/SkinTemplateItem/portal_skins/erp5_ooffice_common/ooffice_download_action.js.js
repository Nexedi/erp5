/*global window, rJS, document, RSVP, jIO */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, document, RSVP, jIO) {
  "use strict";

  function downloadFromBlob(gadget, parent_options, blob, format) {
    var element = gadget.element,
      a = window.document.createElement("a"),
      url = window.URL.createObjectURL(blob),
      name_list;
    if (parent_options.download_format) {
      return gadget.jio_get(parent_options.jio_key)
        .push(function (jio_document) {
          name_list = jio_document.filename.split('.');
          name_list[name_list.length - 1] = format;
          element.appendChild(a);
          a.style = "display: none";
          a.href = url;
          a.download = name_list.join('.');
          a.click();
          element.removeChild(a);
          window.URL.revokeObjectURL(url);
        });
    }
    name_list = parent_options.doc.filename.split('.');
    name_list[name_list.length - 1] = format;
    element.appendChild(a);
    a.style = "display: none";
    a.href = url;
    a.download = name_list.join('.');
    a.click();
    element.removeChild(a);
    window.URL.revokeObjectURL(url);
  }

  function downloadFromFormat(gadget, parent_options, format) {
    var action_options = parent_options.action_options,
      fragment = document.createElement('div'), jio_key;
    if (!action_options) {
      action_options = parent_options;
    }
    jio_key = action_options.jio_key;
    gadget.element.appendChild(fragment);
    return gadget.declareGadget("gadget_ojs_cloudooo.html",
                                {element: fragment, scope: 'ojs_cloudooo'})
      .push(function (ojs_cloudooo) {
        action_options.download_format = format;
        return ojs_cloudooo.getConvertedBlob({
          jio_key: jio_key,
          format: format,
          redirect: jIO.util.stringify({
            'command': 'display',
            'options': action_options
          })
        });
      })
      .push(function (result) {
        return downloadFromBlob(gadget, parent_options, result, format);
      });
  }

  rJS(window)

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_post", "jio_post")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("preRenderDocument", function (parent_options) {
      var gadget = this, format_list, conversion_dict, doc;
      return gadget.getSetting('conversion_dict')
        .push(function (result) {
          conversion_dict = result;
          return gadget.getSetting('file_extension');
        })
        .push(function (format) {
          format_list = window.JSON.parse(conversion_dict)[format];
          format_list.push(format);
          doc = { title: parent_options.form_definition.title,
                  action: true,
                  format: format_list };
          if (parent_options.download_format) {
            return downloadFromFormat(gadget, parent_options, parent_options.download_format);
          }
        })
        .push(function () {
          return doc;
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
      }, gadget = this;
      return downloadFromFormat(gadget, parent_options, content_dict.format)
        .push(function () {
          return return_submit_dict;
        }, function (error) {
          if (error instanceof jIO.util.jIOError) {
            return_submit_dict.notify.message = "Conversion Failed";
            return_submit_dict.notify.status = "error";
            return return_submit_dict;
          }
          throw error;
        });
    });

}(window, rJS, document, RSVP, jIO));