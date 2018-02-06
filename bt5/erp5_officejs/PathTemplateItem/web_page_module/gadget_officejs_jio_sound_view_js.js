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

    .allowPublicAcquisition('getAttachment', function (params) {
      return this.jioInstance.getAttachment(params[0], params[0], {"start": params[1].start, "end": params[1].end});
    })

    .declareMethod("render", function (options) {
      var gadget = this,
        queue;
      if (options.doc.type && options.doc.type === 'mp3') {
        queue = gadget.declareGadget('gadget_officejs_jio_sound_controller.html', {element: gadget.element.querySelector('.controller')});
      } else {
        queue = gadget.declareGadget('gadget_officejs_jio_sound_controller_fallback.html', {element: gadget.element.querySelector('.controller')});
      }
      queue
       .push(function (soundController) {
        gadget.id = options.doc.id;
        gadget.title = options.doc.title;
        gadget.length = options.doc.length;
        gadget.duration = options.doc.duration;
        gadget.type = options.doc.type;
        return soundController.configurePlayer(gadget.id, gadget.length, gadget.duration);
      }).push(function () {
        return gadget.changeState({
          jio_key: options.jio_key,
          doc: options.doc
        });
      });
      return queue;
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
          if (gadget.title === "Untitled Document") {
            gadget.title = content.title;
            return gadget.jioInstance.post({
              "title": gadget.title
            });
          } else {
            gadget.title = content.title;
            return gadget.jioInstance.put(
              gadget.id, {
                "title": gadget.title
              });
          }
        })
        .push(function (id) {
          var data = gadget.element.querySelector('#data').files[0];
          if (data) {
            var result = data.slice();
            var arrName = data.name.split('.');
            gadget.type = arrName[arrName.length - 1];
            gadget.id = id;
            gadget.title = data.name;
            gadget.length = data.size;
            return RSVP.all([
              gadget.calculateDuration(result),
              gadget.jioInstance.putAttachment(gadget.id, gadget.id, result)
            ]);
          }
        })
        .push(function () {
          var subGadget;
          document.getElementById('field-content').style.display = "none";
          if (gadget.type && gadget.type === 'mp3') {
            subGadget = gadget.declareGadget('gadget_officejs_jio_sound_controller.html', {element: gadget.element.querySelector('.controller')});
          } else {
            subGadget = gadget.declareGadget('gadget_officejs_jio_sound_controller_fallback.html', {element: gadget.element.querySelector('.controller')});
          }
          return subGadget
            .push(function (soundController) {
              return soundController.configurePlayer(gadget.id, gadget.length, gadget.duration);
            })
            .push(function () {
              return gadget.updateDocument({
                id: gadget.id,
                title: gadget.title,
                length: gadget.length,
                duration: gadget.duration,
                type: gadget.type
              });
            });
        })
        .push(function () {
          document.location.reload();
          return gadget.notifySubmitted({message: 'Data Updated', status: 'success'});
        }).push(undefined, function (err) {
          console.log(err);
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
                [["my_title"]]
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
