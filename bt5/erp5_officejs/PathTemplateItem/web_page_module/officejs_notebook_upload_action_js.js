/*global window, rJS, RSVP, jIO, DOMParser */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, jIO, DOMParser) {
  "use strict";

  rJS(window)

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////

    .declareAcquiredMethod("jio_post", "jio_post")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("getSettingList", "getSettingList")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod('preRenderDocument', function (parent_options) {
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
      var gadget = this,
        return_submit_dict = {},
        document = parent_options.doc,
        all_attachments,
        promise_list = [],
        parent_jio_key = parent_options.action_options.jio_key,
        property,
        jio_key;
      delete content_dict.dialog_method;
      for (property in content_dict) {
        if (content_dict.hasOwnProperty(property)) {
          document[property] = content_dict[property];
        }
      }
      return gadget.getSettingList(['portal_type',
                                    'content_type',
                                    'upload_dict',
                                    'parent_relative_url'])
        .push(function (result_list) {
          var file_name_list, data, filename, queue, filetype;
          if (document.file !== undefined) {
            file_name_list = document.file.file_name.split('.');
            filetype = file_name_list.pop();
            if (filetype in window.JSON.parse(result_list[2])) {
              filename = file_name_list.join('.');
              data = jIO.util.dataURItoBlob(document.file.url);
              return new RSVP.Queue()
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
                  }
                  return gadget.jio_post({
                    title: filename,
                    portal_type: result_list[0],
                    content_type: result_list[1],
                    parent_relative_url: result_list[3],
                    text_content: data_content
                  });
                })
                .push(function (jio_key) {
                  return_submit_dict.redirect = {
                    command: 'display',
                    options: {
                      jio_key: jio_key,
                      editable: true
                    }
                  };
                  return return_submit_dict;
                }, function (error) {
                  if (error instanceof jIO.util.jIOError) {
                    return_submit_dict.notify = {
                      message: "Failure uploading document",
                      status: "error"
                    };
                    return return_submit_dict;
                  }
                  throw error;
                });
            }
            return_submit_dict.notify.message = "Wrong format, use format : " +
                window.Object.keys(window.JSON.parse(result_list[2])).join(', ');
            return_submit_dict.notify.status = "error";
            return return_submit_dict;
          }
          return_submit_dict.notify.message = "File is required";
          return_submit_dict.notify.status = "error";
          return return_submit_dict;
        });
    });

}(window, rJS, RSVP, jIO, DOMParser));