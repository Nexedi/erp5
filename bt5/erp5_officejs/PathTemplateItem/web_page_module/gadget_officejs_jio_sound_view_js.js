/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, jIO, rJS, RSVP, MediaSource, URL, document, promiseEventListener) {
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

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("render", function (options) {
      var gadget = this;
      return this.getDeclaredGadget('sound_controller')
        .push(function (soundController) {
          return soundController.configurePlayer(options.doc.id, options.doc.title, options.doc.length, options.doc.duration);
        }).push(function () {
          return gadget.changeState({
            jio_key: options.jio_key,
            doc: options.doc
          });
        });
    })
    .allowPublicAcquisition('getAttachment', function (params) {
      return this.jioInstance.getAttachment(params[0], params[1], {"start": params[2].start, "end": params[2].end});
    })
    .declareMethod('calculateDuration', function (blob) {
      // Create a temporary audio element and assign the data to calculate the time information.
      var gadget = this;
      var audioElement = document.createElement('audio');
      audioElement.src = URL.createObjectURL(blob);
      return RSVP.Queue()
        .push(function () {
          return promiseEventListener(
            audioElement,
            'loadedmetadata',
            false
          );
        })
        .push(function () {
          return gadget.duration = audioElement.duration;
        });
    })
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
          gadget.title = content.title.file_name;
          gadget.result = jIO.util.dataURItoBlob(content.title.url);
          return gadget.calculateDuration(gadget.result);
        })
        .push(function () {
          gadget.length = gadget.result.size;
          return gadget.jioInstance.post({
            "title": gadget.title
          })
          .push(undefined, function (error) {
            throw error;
          });
        })
        .push(function (id) {
          gadget.id = id;
          return gadget.jioInstance.putAttachment(gadget.id, gadget.title, gadget.result);
        })
        .push(function () {
          return gadget.getDeclaredGadget('sound_controller').push(function (soundController) {
            return soundController.configurePlayer(gadget.id, gadget.title, gadget.length, gadget.duration);
          }).push(function () {
            return gadget.updateDocument({
              id: gadget.id,
              title: gadget.title,
              length: gadget.length,
              duration: gadget.duration
            });
          });
        })
        .push(function () {
          document.location.reload();
          return gadget.notifySubmitted({message: 'Data Updated', status: 'success'});
        });
    })

    .declareMethod("triggerSubmit", function () {
      return this.element.querySelector('button[type="submit"]').click();
    })
    .ready(function () {
      this.jioInstance = jIO.createJIO({
        "type": "uuid",
        "sub_storage": {
          "type": "indexeddb",
          "database": "musicPlayer"
        }
      });
    })

    .onStateChange(function () {
      var gadget = this;
      return gadget.getDeclaredGadget('form_view')
        .push(function (form_gadget) {
          return form_gadget.render({
            erp5_document: {
              "_embedded": {"_view": {
                "my_title": {
                  "description": "",
                  "title": "Upload",
                  "default": gadget.state.doc.title,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "title",
                  "hidden": 0,
                  "type": "FileField"
                },
                "my_id": {
                  "description": "",
                  "title": "Upload",
                  "default": gadget.state.doc.id,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "title",
                  "hidden": 1,
                  "type": "StringField"
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
              group_list: [[
                "left",
                [["my_title", "my_id"]]
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
}(window, jIO, rJS, RSVP, MediaSource, URL, document, promiseEventListener));
