/*global window, rJS, RSVP, loopEventListener,
  document */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, jIO, RSVP, Blob) {
  "use strict";

  var content_type = {
    Spreadsheet: 'application/x-asc-spreadsheet',
    Presentation: 'application/x-asc-presentation',
    Text: 'application/x-asc-text'
  };

  var file_ext = {
    Spreadsheet: 'xlsy',
    Presentation: 'ppty',
    Text: 'docy'
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
      var gadget = this, doc_id;
      return gadget.changeState({
        title: 'Untitled Document'
      });
    })

  .declareMethod('storeData', function (content) {
    var blob = jIO.util.dataURItoBlob(content.data.url),
      gadget = this,
      postVar = {
        title: "Untitled Document",
        portal_type: gadget.portal_type,
        parent_relative_url: gadget.parent_relative_url,
        content_type: content_type[gadget.portal_type] || undefined
      };

    postVar.title = content.data.file_name || postVar.title;
    postVar.length = blob.size;
    return RSVP.Queue()
      .push(function () {
        return gadget.jio_post(postVar);
      }).push(function (id) {
        return gadget.jio_putAttachment(id, 'enclosure', blob);
      });
  })
  .declareMethod('triggerSubmit', function () {
    var gadget = this;
    return gadget.notifySubmitting().push(function () {
      return gadget.getDeclaredGadget('form_view');
    }).push(function (form_gadget) {
      return form_gadget.getContent();
    }).push(function (content) {
      return RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.getSetting('portal_type'),
            gadget.getSetting('parent_relative_url')
          ]);
        }).push(function (result) {
          var promiseArray = [];
          gadget.portal_type = result[0];
          gadget.parent_relative_url = result[1];

          for (var key in content) {
            if (content.hasOwnProperty(key)) {
              promiseArray.push(
                (function (data, gadget) {
                  var blob = jIO.util.dataURItoBlob(data.url),
                    postVar = {
                      title: "Untitled Document",
                      portal_type: gadget.portal_type,
                      parent_relative_url: gadget.parent_relative_url,
                      content_type: content_type[gadget.portal_type] || undefined
                    };

                  postVar.title = data.file_name || postVar.title;
                  postVar.length = blob.size;
                  return RSVP.Queue()
                    .push(function () {
                      return gadget.jio_post(postVar);
                    }).push(function (id) {
                      return gadget.jio_putAttachment(id, 'enclosure', blob);
                    });
                })(content[key], gadget)
              );
            }
          }
          return RSVP.all(promiseArray);
        });
    }).push(function () {
      return RSVP.all([
        gadget.notifySubmitted({message: 'Data Updated', status: 'success'}),
        gadget.redirect({
          command: 'display',
          options: {
            page: 'ojs_document_list',
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
        return gadget.updateHeader({
          save_action: true
        });
      });
  });
}(window, rJS, jIO, RSVP, Blob));
