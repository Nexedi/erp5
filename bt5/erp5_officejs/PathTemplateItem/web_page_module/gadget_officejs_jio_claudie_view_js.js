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
      console.log("################");
      var gadget = this;
      gadget.type = options.doc.type;
      
      var state = {
        title: options.doc.title,
        upload_name: options.doc.upload
      };
/*      
      return gadget.jio_get(options.jio_key)
        .push(function (data) {

          state.doc = options.doc;
          state.text = data.text;
          state.audio = data.audio;
          if (data.image) {
            return jIO.util.readBlobAsDataURL(data.image);
          }
        })
        .push(function (image) {
          if (image){
            state.image = image.target.result;
          }
          else{
            state.image = null;
          }
          gadget.changeState(state);
        });
    })
  */  
    
      return gadget.jio_getAttachment(options.jio_key, "upload")
        .push(function (blob) {
          state.upload = blob;
          
          return gadget.jio_getAttachment(options.jio_key, "image");
        })
        .push(function (blob) {
          return jIO.util.readBlobAsDataURL(blob);
        })
        .push(function (data) {
          state.jio_key = options.jio_key;
          state.image = data.target.result;
          
          return gadget.jio_getAttachment(options.jio_key, "text");
        })
        .push(function (blob_text) {
          return jIO.util.readBlobAsText(blob_text);
        })    
    
        .push(function (text) {
          state.text = text.target.result;
          
          return gadget.jio_getAttachment(options.jio_key, "audio");
        })
        //.push(function (blob) {
        //  return jIO.util.readBlobAsDataURL(blob);
        //})
        .push(function (blob) {
          state.audio = blob;
          
          gadget.changeState(state);
        })
        .push(function () {
          return gadget.updateHeader({
            page_title: 'Claudie',
            save_action: true
          });
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
      var blob_upload = new Blob();
      var blob_image = new Blob();
      var blob_audio = new Blob();
      var text;
      var content;
      var global_id;
      return gadget.notifySubmitting()
        .push(function () {
          return gadget.getDeclaredGadget('form_view');
        })
        .push(function (form_gadget) {
          return form_gadget.getContent();
        })
        .push(function (result) {
          if (result.upload)
            blob_upload = jIO.util.dataURItoBlob(result.upload.url);
          if (result.image) 
            blob_image = jIO.util.dataURItoBlob(result.image.url);
          if (result.audio) 
            blob_audio = jIO.util.dataURItoBlob(result.audio.url);
          
          content = result;
          return RSVP.all([
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
            upload: upload_name
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
            /*
            command: 'display',
            options: {
             "page": "ojs_document_list",
              editable: true
            }});*/
        });
    })

    .declareMethod("triggerSubmit", function () {
      return this.element.querySelector('button[type="submit"]').click();
    })

    .onStateChange(function () {
      var gadget = this;
      //this.element.querySelector("audio").src = gadget.state.audio;

      /*if (gadget.state.audio){
        this.element.querySelector("audio").src = URL.createObjectURL(gadget.state.audio);
      }*/
       // console.log("############");
      //var audio = document.getElementById("audio");

      //audio.src = gadget.state.audio;

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
                  "my_upload": {
                    "description": "",
                    "title": "Upload",
                    "default": "",
                    "css_class": "",
                    "required": 1,
                    "editable": 1,
                    "key": "upload",
                    "hidden": 0,
                    //"accept": "audio/*",
                    "type": "FileField"
                  },
                  "my_image": {
                    "description": "",
                    "title": "Image",
                    "default": "",
                    "css_class": "",
                    "required": 1,
                    "editable": 1,
                    "key": "image",
                    "hidden": 0,
                    //"accept": "audio/*",
                    "type": "FileField"
                  },
                  "my_audio": {
                    "description": "",
                    "title": "Audio",
                    "default": "",
                    "css_class": "",
                    "required": 1,
                    "editable": 1,
                    "key": "audio",
                    "hidden": 0,
                    "type": "FileField"
                  },
                  "my_text": {
                    "description": "",
                    "title": "Text",
                    "default": gadget.state.text,
                    "css_class": "",
                    "height" : "100",
                    "required": 1,
                    "editable": 1,
                    "key": "text",
                    "hidden": 0,
                    "type": "TextAreaField"
                  },
                  "my_image_preview": {
                    "description": "",
                    "title": "Image",
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
                [["my_title"], ["my_upload"], ["my_image"], ["my_audio"], ["my_text"]]
              ], [
                "bottom",
                [["my_image_preview"]]
              ]]
            }
          });
        })
        .push(function (form) {
          if (gadget.state.upload.size !== 0) {
            var a = document.createElement("a");
            a.setAttribute('href', URL.createObjectURL(gadget.state.upload));
            a.setAttribute('download', gadget.state.upload_name);
            a.innerHTML = gadget.state.upload_name;
            //audio.src = URL.createObjectURL(gadget.state.audio);
            
            var upload_field = document.querySelector("input[id='upload']");
            var form = upload_field.parentNode;
            //form.removeChild(audio_field);
            //form.insertBefore(a,upload_field);
            form.appendChild(a);

            
          }
      })

        .push(function () {
          if (gadget.state.audio.size !== 0) {
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