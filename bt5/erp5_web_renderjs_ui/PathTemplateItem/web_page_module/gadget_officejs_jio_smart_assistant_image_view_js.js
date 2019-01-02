/*global window, rJS, RSVP, jIO, URL, Blob, promiseEventListener, document*/
/*jslint indent:2, maxlen: 80, nomen: true */
(function (window, jIO, rJS, RSVP, URL) {
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
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
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


      return gadget.jio_getAttachment(options.jio_key, "data")
        .push(function (blob_image) {
          state.image = URL.createObjectURL(blob_image);
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
          var blob_image,
            queue;
          if (result.image_) {
            title = result.image_.file_name;
            blob_image = jIO.util.dataURItoBlob(result.image_.url);
            queue = gadget.jio_putAttachment(gadget.state.jio_key,
                                             'data', blob_image);
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
                  "my_image": {
                    "description": "",
                    "title": "Change it",
                    "default": "",
                    "css_class": "",
                    "required": 1,
                    "editable": 1,
                    "key": "image_",
                    "hidden": 0,
                    "accept": "image/*",
                    "capture": "camera",
                    "type": "FileField"
                  },
                  "my_image_preview": {
                    "description": "",
                    "title": "Actually",
                    "default": gadget.state.image,
                    "css_class": "",
                    "height" : "10",
                    "required": 1,
                    "editable": 1,
                    "key": "image_preview",
                    "hidden": 0,
                    "type": "ImageField"
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
                [["my_title"], ["my_image"], ["my_image_preview"]]
              ]]
            }
          });
        });
    });
}(window, jIO, rJS, RSVP, URL));