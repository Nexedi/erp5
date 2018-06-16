/*global window, rJS, RSVP, loopEventListener,
  jIO, document */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, jIO, RSVP) {
  "use strict";

  var content_type = {
    Spreadsheet: 'application/x-asc-spreadsheet',
    Presentation: 'application/x-asc-presentation',
    Text: 'application/x-asc-text'
  };

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("jio_post", "jio_post")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function () {
      var gadget = this;
      return gadget.changeState({
        title: 'Untitled Document'
      });
    })

    .declareMethod('putIntoDB', function (data, portal_type, parent_relative_url) {
      var gadget = this,
        blob = jIO.util.dataURItoBlob(data.url),
        post_variables = {
          title: "Untitled Document",
          portal_type: portal_type,
          parent_relative_url: parent_relative_url,
          content_type: content_type[portal_type] || undefined
        };

      post_variables.title = data.file_name || post_variables.title;
      if (data.file_name) {
        post_variables.reference = data.file_name;
      }
      return gadget.jio_post(post_variables)
        .push(function (id) {
          return gadget.jio_putAttachment(id, 'data', blob);
        })
        .push(undefined, function (error) {
          if (error.target && error.target.error.name === 'NotReadableError') {
            return gadget.notifySubmitted({message: error.target.error.message, status: 'fail'});
          }
          throw error;
        });
    })

    .declareMethod('triggerSubmit', function () {
      var gadget = this;
      return gadget.notifySubmitting()
        .push(function () {
          return gadget.getDeclaredGadget('form_view');
        })
        .push(function (form_gadget) {
          return form_gadget.getContent();
        })
        .push(function (content) {
          return new RSVP.Queue()
            .push(function () {
              return RSVP.all([
                gadget.getSetting('portal_type'),
                gadget.getSetting('parent_relative_url')
              ]);
            })
            .push(function (result) {
              var promiseArray = [],
                data_array = content.data,
                i,
                portal_type = result[0],
                parent_relative_url = result[1];

              for (i = 0; i < data_array.length; i += 1) {
                promiseArray.push(gadget.putIntoDB(data_array[i], portal_type, parent_relative_url));
              }
              return RSVP.all(promiseArray);
            });
        })
        .push(function () {
          return RSVP.all([
            gadget.notifySubmitted({message: 'Data Updated', status: 'success'}),
            gadget.redirect({
              command: 'display',
              options: {
                page: 'ojs_media_player_document_list',
                editable: 'true'
              }
            })
          ]);
        });
    })

    .onStateChange(function () {
      var gadget = this;
      return gadget.getDeclaredGadget('form_view')
        .push(function (form_gadget) {
          return form_gadget.render({
            erp5_document: {
              "_embedded": {
                "_view": {
                  "my_file": {
                    "description": "",
                    "title": "Upload",
                    "default": "",
                    "css_class": "",
                    "required": 1,
                    "editable": 1,
                    "key": "data",
                    "hidden": 0,
                    "multiple": "true",
                    "accept": "audio/*",
                    "type": "FileField"
                  }
                }
              },
              "_links": {
                "type": {
                  // form_list display portal_type in header
                  name: ""
                }
              }
            },
            form_definition: {
              group_list: [[
                "left",
                [["my_file"]]
              ]]
            }
          });
        })
        .push(function () {
          return gadget.getUrlFor({command: "change", options: {"page": "ojs_media_player_document_list"}});
        })
        .push(function (result) {
          return gadget.updateHeader({
            page_title: 'Document(s)',
            selection_url: result,
            save_action: true
          });
        });
    });
}(window, rJS, jIO, RSVP));
