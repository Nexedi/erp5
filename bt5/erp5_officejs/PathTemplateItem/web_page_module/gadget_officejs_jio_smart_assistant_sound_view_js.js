/*global window, rJS, RSVP, jIO, URL, Blob*/
/*jslint indent:2, maxlen: 80, nomen: true */
(function (window, jIO, rJS, RSVP) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("updateDocument", "updateDocument")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", 'notifySubmitted')
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")


    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function (options) {
      var gadget = this,
        state = {
          title: options.doc.title,
          jio_key: options.jio_key
        };

      gadget.type = options.doc.type;

      return RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.getUrlFor({command: 'history_previous'}),
            gadget.getUrlFor({command: 'selection_previous'}),
            gadget.getUrlFor({command: 'selection_next'}),
            gadget.changeState(state)
          ]);
        })
        .push(function (url_list) {
          return gadget.updateHeader({
            page_title: "Smart Assistant",
            save_action: true,
            selection_url: url_list[0],
            previous_url: url_list[1],
            next_url: url_list[2]
          });
        });
    })

    .onEvent('submit', function () {
      var gadget = this,
        title;

      return gadget.notifySubmitting()
        .push(function () {
          return gadget.getDeclaredGadget('form_view');
        })
        .push(function (form_gadget) {
          return form_gadget.getContent();
        })
        .push(function (result) {
          var blob_audio,
            queue;
          if (result.audio_) {
            title = result.audio_.file_name;
            blob_audio = jIO.util.dataURItoBlob(result.audio_.url);
            queue = gadget.jio_putAttachment(gadget.state.jio_key,
                                             'data', blob_audio);
          } else {
            title = result.title;
            queue = new RSVP.Queue();
          }
          queue.push(function () {
            return gadget.updateDocument({title: title});
          });
          return queue;
        })
        .push(function () {
          return gadget.notifySubmitted({
            "message": "Data updated",
            "status": "success"
          });
        })
        .push(function () {
          return gadget.redirect({command: 'reload'});
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
                    "default": gadget.state.title,
                    "css_class": "",
                    "required": 1,
                    "editable": 1,
                    "key": "title",
                    "hidden": 0,
                    "type": "StringField"
                  },
                  "my_actual_audio": {
                    "default": gadget.state.jio_key,
                    "css_class": "",
                    "required": 1,
                    "editable": 0,
                    "key": "player_content",
                    "hidden": 0,
                    "title": "Listen actual content",
                    "type": "GadgetField",
                    "renderjs_extra": '{"name": "data"}',
                    "url": "gadget_custom_player.html",
                    "sandbox": "public"
                  },
                  "my_audio": {
                    "description": "",
                    "title": "Audio",
                    "default": "",
                    "css_class": "",
                    "required": 1,
                    "editable": 1,
                    "key": "audio_",
                    "hidden": 0,
                    "accept": "audio/*",
                    "capture": "microphone",
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
                [["my_title"], ["my_actual_audio"], ["my_audio"]]
              ]]
            }
          });
        });
    });
}(window, jIO, rJS, RSVP));