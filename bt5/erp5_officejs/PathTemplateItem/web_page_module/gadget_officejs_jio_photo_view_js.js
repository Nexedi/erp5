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
    .declareAcquiredMethod("redirect", "redirect")

    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("jio_post", "jio_post")


    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function (options) {
     // console.log("################");
      var gadget = this;
      gadget.type = options.doc.type;
      
      var state = {
        title: options.doc.title,
        jio_key: options.jio_key
      };

      return gadget.jio_getAttachment(options.jio_key, "data")
        .push(function (blob_image) {
          return jIO.util.readBlobAsDataURL(blob_image);
        })
        
        .push(function (data_image) {
          state.image = data_image.target.result;
        })
    
        .push(function () {
          gadget.changeState(state);
          return gadget.updateHeader({
            page_title: 'Claudie',
            save_action: true
          });
        });
    })
  
    .onEvent('submit', function () {
      var gadget = this;
      var text;
      var title;
      var global_id;
    
      return gadget.notifySubmitting()
        .push(function () {
          return gadget.getDeclaredGadget('form_view');
        })
        .push(function (form_gadget) {
          return form_gadget.getContent();
        })
        .push(function (result) {
          title = result.title;
          var blob_image = new Blob();
        
          if (result.image)
            blob_image = jIO.util.dataURItoBlob(result.image_.url);
            
          return gadget.jio_putAttachment(gadget.state.jio_key, 'data', blob_image);
        })
    
        .push(function () {
          return gadget.updateDocument({
            
            title: title
          });
        })
    
        .push(function () {
          return gadget.redirect({
            command: 'display',
            options: {
              jio_key: gadget.state.jio_key,
              editable: true
            }
          });
        });
    })
          
    /*      return RSVP.all([
            gadget.getSetting('portal_type'),
            gadget.getSetting('parent_relative_url')
          ]);
        })
        .push(function () {
          var id = gadget.state.jio_key;
          var command = [];
          if (content.upload)
            command.push(gadget.jio_putAttachment(id, 'upload', blob_upload));
          if (content.image)
            command.push(gadget.jio_putAttachment(id, 'image', blob_image));
          if (content.audio)
            command.push(gadget.jio_putAttachment(id, 'audio', blob_audio));
          if (content.text)
            command.push(gadget.jio_putAttachment(id, 'text', content.text));
          return RSVP.all(
            command
          );
        })
        .push(function () {
          var upload_name = gadget.state.upload_name;
          if (content.upload)
            upload_name = content.upload.file_name;
        
          return gadget.updateDocument({
            
            title: content.title,
            links: id_list
          });
        })
        .push(function () {
          return gadget.redirect({
            command: 'display',
            options: {
              jio_key: gadget.state.jio_key,
              editable: true
            }
          });
            
            command: 'display',
            options: {
             "page": "ojs_document_list",
              editable: true
            }});
        });
    })*/

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
        })
    
        .push(function () {
          if (gadget.state.audio) {
            var audio = document.createElement("audio");
            audio.setAttribute('controls', 'controls');
            audio.src = URL.createObjectURL(gadget.state.audio);
            
            var audio_field = document.querySelector("input[id='audio']");
            var form = audio_field.parentNode;
            //form.removeChild(audio_field);
            form.appendChild(audio);

            
          }
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
            page_title: "test",
            save_action: true,
            selection_url: url_list[0],
            previous_url: url_list[1],
            next_url: url_list[2]
          });
        }).push(undefined, function (err) { console.log(err); });
    });
}(window, jIO, rJS, RSVP, URL, document, promiseEventListener));