/*global window, rJS, RSVP, jIO, URL,
  promiseEventListener, document*/
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, jIO, rJS, RSVP, URL, document, promiseEventListener) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("updateDocument", "updateDocument")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", 'notifySubmitted')
    .declareAcquiredMethod("reload", "reload")
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function (options) {
      var gadget = this;
      gadget.type = options.doc.type;
      return gadget.changeState({
        jio_key: options.jio_key,
        doc: options.doc
      });
    })
/*
    .declareMethod('calculateDuration', function (data) {
      // Create a temporary audio element and assign the data to
      // calculate the time duration.
      var gadget = this,
        audioElement = document.createElement('audio');
      audioElement.src = URL.createObjectURL(data);
      return RSVP.Queue()
        .push(function () {
          return promiseEventListener(
            audioElement,
            'loadedmetadata',
            false
          );
        })
        .push(function () {
          gadget.duration = audioElement.duration;
        });
    })
*/
    .onEvent('submit', function () {
      var gadget = this;
      return gadget.notifySubmitting()
        .push(function () {
          return gadget.getDeclaredGadget('form_view');
        })
        .push(function (form_gadget) {
          return form_gadget.getContent();
        })
        .push(function (content) {
          var blob = jIO.util.dataURItoBlob(content.data.url);
          return RSVP.Queue()
            .push(function () {
              gadget.title = content.data.file_name;
              return gadget.jio_get(gadget.state.jio_key);
              // Create a new document if not present in IDB.
              /*if (gadget.title === "Untitled Document") {
                gadget.title = content.title;
                return gadget.jio_post({
                  "title": gadget.title
                });
              }
              // Update the document if already present in IDB.
              gadget.title = content.title;
              return gadget.jio_put(
                gadget.id,
                {
                  "title": gadget.title
                }
              );
              */
            }).push(function (doc) {
              var property;
              for (property in content) {
                if (content.hasOwnProperty(property) && property !== 'data') {
                  doc[property] = content[property];
                }
              }
              doc.length = blob.size;
              return gadget.jio_put(gadget.state.jio_key, doc);
            }).push(function () {
              return gadget.jio_putAttachment(gadget.state.jio_key, 'enclosure', blob);
            });
            /*.push(function (doc) {
              // Extract information from data, if uploaded.
              if (content.data) {
                var arrName = content.data.file_name.split('.');
                gadget.type = arrName[arrName.length - 1];
                gadget.id = id;
                gadget.title = content.data.file_name;
                var blob = jIO.util.dataURItoBlob(content.data.url);
                gadget.length = blob.size;
                // Calculate the duration of audio file.
                //return gadget.calculateDuration(blob).push(function () {
                  // Insert audio data in attachment table.
                return gadget.jio_putAttachment(gadget.id, gadget.id, blob);
                //});
              }
            });*/
        })
        .push(function () {
          return gadget.updateDocument({
            title: gadget.title
          });
        })
        .push(function () {
          //gadget.reload();
          return gadget.notifySubmitted({message: 'Data Updated', status: 'success'});
        });
    })

    .declareMethod("triggerSubmit", function () {
      return this.element.querySelector('button[type="submit"]').click();
    })

    .onStateChange(function () {
      var gadget = this;
      return gadget.getDeclaredGadget('form_view')
        .push(function (form_gadget) {
          return form_gadget.render({
            erp5_document: {
              "_embedded": {
                "_view": {
                  "my_title": {
                    "description": "",
                    "title": "Title",
                    "default": gadget.state.doc.title,
                    "css_class": "",
                    "required": 1,
                    "editable": 1,
                    "key": "title",
                    "hidden": 0,
                    "type": "StringField"
                  },
                  "my_file": {
                    "description": "",
                    "title": "Upload",
                    "default": "",
                    "css_class": "",
                    "required": 1,
                    "editable": 1,
                    "key": "data",
                    "hidden": 0,
                    "accept": "audio/*",
                    "type": "FileField"
                  },
                  "my_content": {
                    "default": {
                      id: gadget.state.jio_key
                    },
                    "css_class": "",
                    "required": 1,
                    "editable": 1,
                    "key": "player_content",
                    "hidden": 0,
                    "type": "GadgetField",
                    "url": "gadget_custom_player.html",
                    "sandbox": "public"
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
                [["my_title"], ["my_file"]]
              ], [
                "bottom",
                [["my_content"]]
              ]]
            }
          });
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
            page_title: gadget.state.doc.title,
            save_action: true,
            selection_url: url_list[0],
            previous_url: url_list[1],
            next_url: url_list[2]
          });
        });
    });
}(window, jIO, rJS, RSVP, URL, document, promiseEventListener));
