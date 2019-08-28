/*global window, rJS, document, RSVP, jIO */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, document, RSVP, jIO) {
  "use strict";

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
      return this.getSetting('upload_dict')
        .push(function (upload_dict) {
          var upload = window.JSON.parse(upload_dict),
            doc = { title: parent_options.form_definition.title,
                    action: true,
                    format: window.Object.keys(upload).join(', ') };
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
      return RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.getSetting('portal_type'),
            gadget.getSetting('content_type'),
            gadget.getSetting('file_extension'),
            gadget.getSetting('parent_relative_url'),
            gadget.getSetting('upload_dict')
          ]);
        })
        .push(function (result) {
          var upload = window.JSON.parse(result[4]),
            ATT_NAME = "data", file_name_list, from, jio_key, data, to, att_name = ATT_NAME, filename;
          if (content_dict.file !== undefined) {
            file_name_list = content_dict.file.file_name.split('.');
            from = file_name_list.pop();
            file_name_list.push(result[2]);
            filename = file_name_list.join('.');
            data = jIO.util.dataURItoBlob(content_dict.file.url);
            if (upload.hasOwnProperty(from)) {
              if (result[2] !== from) {
                att_name = from;
              }
              to = upload[from];
              return gadget.jio_post({
                title: filename,
                portal_type: result[0],
                content_type: result[1],
                filename: filename,
                parent_relative_url: result[3]
              })
                .push(function (doc_id) {
                  jio_key = doc_id;
                  return gadget.jio_putAttachment(jio_key, att_name, data);
                })
                .push(function () {
                  if (result[2] === from) {
                    return_submit_dict.notify.message = "Data Updated";
                    return_submit_dict.notify.status = "success";
                    return_submit_dict.redirect.options = {
                      jio_key: jio_key,
                      editable: true
                    };
                    return return_submit_dict;
                  }
                  var fragment = document.createElement('div');
                  gadget.element.appendChild(fragment);
                  return gadget.declareGadget("gadget_ojs_cloudooo.html",
                                              {element: fragment, scope: 'ojs_cloudooo'})
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
                  return_submit_dict.notify.message = "Data Updated";
                  return_submit_dict.notify.status = "success";
                  return_submit_dict.redirect.options = {
                    'command': 'display',
                    'options': {
                      'jio_key': jio_key
                    }
                  };
                  return return_submit_dict;
                });
            }
            return_submit_dict.notify.message = "Can not convert, use format : " +
                  window.Object.keys(upload).join(', ');
            return_submit_dict.notify.status = "error";
            return return_submit_dict;
          }
          return_submit_dict.notify.message = "File is required";
          return_submit_dict.notify.status = "error";
          return return_submit_dict;
        });
    });

}(window, rJS, document, RSVP, jIO));