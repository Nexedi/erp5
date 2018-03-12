/*global window, rJS, jIO, Handlebars*/
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, jIO, RSVP, document) {
  "use strict";
  var gadget_klass = rJS(window),
    dialog_button = gadget_klass.__template_element
                         .getElementById("handlebars-template")
                         .innerHTML,
      handlebars_template = Handlebars.compile(dialog_button);

  gadget_klass
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("jio_post", "jio_post")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("reload", "reload")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("updateDocument", "updateDocument")
    .declareAcquiredMethod("notifyChange", "notifyChange")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")



    .allowPublicAcquisition('updateHeader', function () {
      return;
    })
    .allowPublicAcquisition('getUrlParameter', function (argument_list) {
      return this.getUrlParameter(argument_list)
        .push(function (result) {
          if ((result === undefined) && (
              (argument_list[0] === 'field_listbox_test_result_sort_list:json') ||
                (argument_list[0] === 'field_listbox_bug_sort_list:json') ||
                (argument_list[0] === 'field_listbox_task_report_sort_list:json')
            )) {
            return [['modification_date', 'descending']];
          }
          return result;
        });
    })
  
    .declareMethod("send", function () {
      var gadget = this;
      var blob_upload = new Blob();
      var blob_image = new Blob();
      var blob_audio = new Blob();
      var text;
      var content;
      var global_id;
      var form;
      //var id_list = [0, 0, 0];
      var portal_type, parent_relative_url;
    
      if (!gadget.state.content) {
        gadget.state.content = {
          upload: "",
          image: "",
          text: ""
        };
      }
     else {
        if (!gadget.state.content.upload)
          gadget.state.content.upload = "";
        if (!gadget.state.content.image)
          gadget.state.content.image = "";
      }
      
      return gadget.notifySubmitting()
        .push(function () {
          return gadget.getDeclaredGadget('form_view');
        })
        .push(function (form_gadget) {
          return form_gadget.getContent();
        })
        .push(function (result) {
          if (result.upload && result.upload.url != gadget.state.content.upload.url)
            blob_upload = jIO.util.dataURItoBlob(result.upload.url);
          if (result.image && result.image.url != gadget.state.content.image.url)
            blob_image = jIO.util.dataURItoBlob(result.image.url);
          if (gadget.state.audio)
            blob_audio = gadget.state.audio;
        
          content = result;
        
          return RSVP.all([
            gadget.getSetting('portal_type'),
            gadget.getSetting('parent_relative_url')
          ]);
        })
        
        .push(function (result) {
          portal_type = result[0].split(',');
          parent_relative_url = result[1].split(',');
        
        
          if (content.upload && content.upload.url != gadget.state.content.upload.url) {
            return gadget.jio_post({
              "title": content.upload.file_name,
              portal_type: portal_type[3],
              parent_relative_url: parent_relative_url[3]
            });
          }
        })
    
        .push(function (id_upload) {
          if (id_upload) {
            global_id = id_upload;
            gadget.jio_putAttachment(id_upload, 'data', blob_upload);
          }
        })
    
        .push(function () {
          if (content.image && content.image.url != gadget.state.content.image.url) {
            return gadget.jio_post({
              "title": content.image.file_name,
              portal_type: portal_type[1],
              parent_relative_url: parent_relative_url[1]
            });
          }
        })
        
        .push(function (id_image) {
          if (id_image) {
            global_id = id_image;
            gadget.jio_putAttachment(id_image, 'data', blob_image);
          }
        })
        
        .push(function () {
          if (gadget.state.audio) {
            var date = new Date();
            var title = date.getFullYear() + "_" + date.getMonth() + "_" + date.getDate() + "_" + date.getHours() + ":" + date.getMinutes() + ":" + date.getSeconds();
            return gadget.jio_post({
              "title": "record_" + title,
              portal_type: portal_type[2],
              parent_relative_url: parent_relative_url[2]
            });
          }
        })
        
        .push(function (id_audio) {
          if (id_audio) {
            global_id = id_audio;
            gadget.jio_putAttachment(id_audio, 'data', blob_audio);
          }

          if (content.text !== "" && content.text != gadget.state.content.text)
            return gadget.jio_post({
              "title": content.text.split(' ').slice(0, 4).join('_'),
            //  "links": id_list,
              portal_type: portal_type[0],
              parent_relative_url: parent_relative_url[0]
            });
        })
        .push(function (id_text) {
          if (id_text) {
            global_id = id_text;
            return RSVP.all([
           //   gadget.jio_putAttachment(id, 'upload', blob_upload),
           //   gadget.jio_putAttachment(id, 'image', blob_image),
           //   gadget.jio_putAttachment(id, 'audio', blob_audio),
              gadget.jio_putAttachment(id_text, 'data', content.text)
            ]);  
          }
        }) 
        .push(function () {
          gadget.state.content = content;
          gadget.state.audio = null;
          
          gadget.notifySubmitted({
            "message": "Data created",
            "status": "success"
          });
          //return gadget.reload();
            /*
            command: 'display',
            options: {
             "page": "ojs_document_list",
              editable: true
            }});*/
        });
    })
  
    .allowPublicAcquisition('notifyChange', function () {
      var gadget = this;
      var textarea = document.querySelector("textarea[id='text']").parentNode.parentNode;
      if (document.activeElement.getAttribute("id") != "text" && textarea.style.display === '') {
        document.querySelector("textarea[id='text']").value = '';
        gadget.send();
      }
      
    })
  
  
  
    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .onEvent('submit', function () {
      var gadget = this;
    
      var textarea = document.querySelector("textarea[id='text']").parentNode.parentNode;
      var button = document.querySelector("label[for='text_button']");
      document.querySelector("button[id='submit']").remove();
      document.querySelector("textarea[id='text']").value = '';

      button.style.background = "";
      textarea.style.display = "";
    
    
      gadget.send();
    })

      .declareService(function () {
        var gadget = this;
        var record;
        var stop = false;
    
    
        var button = document.querySelectorAll("label[for='audio']")[0];
        var mousedown = loopEventListener(button, "mousedown", false,
          function (event) {
          
            if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {

              navigator.mediaDevices.getUserMedia({ audio: true }).then(function (stream) {
                  record = new MediaRecorder(stream);
                  record.start();
                  var chunks = [];
                
                  if (stop)
                    record.stop();

                  record.onstop = function (e) {
                    stop = false;
                    
                    stream.getTracks().forEach(function (track) { track.stop(); });
                    
                    button.style.background = "";
                    
                    var blob = new Blob(chunks, { 'type' : 'audio/ogg; codecs=opus' });
                    
                    if (blob.size > 2000) {

                      gadget.state.audio = blob;

                      document.querySelector("textarea[id='text']").value = '';
                      gadget.send();
                    }
                  };

                  record.ondataavailable = function (e) {
                    chunks.push(e.data);
                  };
                });
            }
            
            button.style.background = "red";
          });
    
        var mouseup = loopEventListener(button, "mouseup", false,
          function (event) {
            if (record && record.state == "recording")
              record.stop();
            else
              stop = true;
            button.style.background = "";
          });
    
        var touchstart = loopEventListener(button, "touchstart", false,
          function (event) {
            if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {

              navigator.mediaDevices.getUserMedia({ audio: true }).then(function (stream) {
                  record = new MediaRecorder(stream);
                  record.start();
                  var chunks = [];
                
                  if (stop)
                    record.stop();

                  record.onstop = function (e) {
                    stop = false;
                    
                    stream.getTracks().forEach(function (track) { track.stop(); });
                    
                    button.style.background = "";
                    
                    var blob = new Blob(chunks, { 'type' : 'audio/ogg; codecs=opus' });
                    
                    if (blob.size > 2000) {

                      gadget.state.audio = blob;

                      document.querySelector("textarea[id='text']").value = '';
                      gadget.send();
                    }
                  };

                  record.ondataavailable = function (e) {
                    chunks.push(e.data);
                  };
                });
            }
          
            button.style.background = "red";
          });
    
        var touchend = loopEventListener(button, "touchend", false,
          function (event) {
            if (record && record.state == "recording")
              record.stop();
            else
              stop = true;
          });
    
        return RSVP.all([mousedown, mouseup, touchstart, touchend]);
    
      })
/*    
    .declareService(function () {
      var gadget = this;
      var button = document.querySelectorAll("input[type='file']")[0];
      return loopEventListener(button, "change", false,
        function (event) {
          if (button.files.length !== 0)
            button.parentNode.parentNode.previousElementSibling.style.backgroundColor = "#37A419";
          else
            button.parentNode.parentNode.previousElementSibling.style.backgroundColor = "";
            
        });
    }, false)
  
    .declareService(function () {
      var gadget = this;
      var button = document.querySelectorAll("input[type='file']")[1];
      return loopEventListener(button, "change", false,
        function (event) {
          if (button.files.length !== 0)
            button.parentNode.parentNode.previousElementSibling.style.backgroundColor = "#37A419";
          else
            button.parentNode.parentNode.previousElementSibling.style.backgroundColor = "";
            
        });
    }, false)
  /*
    .declareService(function () {
      var gadget = this;
      var button = document.querySelectorAll("input[type='file']")[2];
      return loopEventListener(button, "change", false,
        function (event) {
          if (button.files.length !== 0)
            button.parentNode.parentNode.previousElementSibling.style.backgroundColor = "#37A419";
          else
            button.parentNode.parentNode.previousElementSibling.style.backgroundColor = "";
            
        });
    }, false) 
    */
  
    .declareService(function () {
      var gadget = this;
      var text_label = document.querySelector("label[for='text_button']");
      return loopEventListener(text_label, "click", false,
        function (event) {
          var textarea = document.querySelector("textarea[id='text']").parentNode.parentNode;
          var button = document.querySelector("label[for='text_button']");
          if (textarea.style.display != "block") {
            if (document.querySelector("button[class='success']"))
              document.querySelector("button[class='success']").click();
            
            button.style.background = "#37A419";

            textarea.style.display = "block";
            document.querySelector("textarea[id='text']").focus();
            
            var button_send = document.createElement("button");
            button_send.setAttribute('type', 'submit');
            button_send.setAttribute('id', 'submit');
            button_send.innerHTML = "Send";

            textarea.appendChild(button_send);
            
            
          }
          else {
            document.querySelector("button[id='submit']").remove();
            
            button.style.background = "";
            textarea.style.display = "";
          }
     
            
        });
    }, false)

  
    .declareService(function () {
      var gadget = this;
      gadget.element.querySelector(".main_button").innerHTML =
        handlebars_template({
          show_update_button: false
        });
    })
  
    
  
    .declareMethod("render", function () {
      var gadget = this;
      gadget.jio_allDocs();
      
      return gadget.updateHeader({
        page_title: 'Claudie'
        //save_action: true
      })
        .push(function () {
          return gadget.getDeclaredGadget('form_view');
        })
        .push(function (form_gadget) {
          return form_gadget.render({
            erp5_document: {"_embedded": {"_view": {
                /*"my_title": {
                    "description": "",
                    "title": "Title",
                    "default": "Untitled Document",
                    "css_class": "",
                    "required": 1,
                    "editable": 1,
                    "key": "title",
                    "hidden": 0,
                    "type": "StringField"
                  },*/

               "upload": {
                /*"column_list": [
                  ['title', 'Title'],
                  ['string_index', 'Result']
                ],*/
                "show_anchor": 0,
                "default_params": {},
                "editable": 1,
                "editable_column_list": [],
                "key": "upload",
                "lines": 5,
                "list_method": "portal_catalog",
                "query": "urn:jio:allDocs?query=portal_type%3A%22Test%20Result%22",
                "portal_type": ["Test Result"],
               // "search_column_list": [],
               // "sort_column_list": [],
                "title": " ",
                "type": "FileField"
              },
              "image": {
               /* "column_list": [
                  ['title', 'Title'],
                  ['translated_simulation_state_title', 'State']
                ],*/
               // "show_anchor": 0,
               // "default_params": {},
                "editable": 1,
              //  "editable_column_list": [],
                "key": "image",
              //  "lines": 5,
              //  "list_method": "portal_catalog",
              //  "query": "urn:jio:allDocs?query=portal_type%3A%22Bug%22",
              //  "portal_type": ["Test Result"],
              //  "search_column_list": [],
              //  "sort_column_list": [],
                "capture": "camera",
                "title": " ",
                "accept": "image/*",
                "capture": "camera",
                "type": "FileField"
              },
              "audio": {
                "column_list": [
                  ['title', 'Title'],
                  ['translated_simulation_state_title', 'State']
                ],
                "show_anchor": 0,
                "default_params": {},
                "editable": 1,
                "editable_column_list": [],
                "key": "audio",
                "lines": 5,
                "list_method": "portal_catalog",
                "query": "urn:jio:allDocs?query=portal_type%3A%22Task%20Report%22",
                "portal_type": ["Task Report"],
                "search_column_list": [],
                "sort_column_list": [],
                "title": " ",
                "accept": "audio/*",
                "capture": "microphone",
                "type": "StringField"
              },
              "text_button": {
                "column_list": [
                  ['title', 'Title'],
                  ['translated_simulation_state_title', 'State']
                ],
                "show_anchor": 0,
                "default_params": {},
                "editable": 1,
                "editable_column_list": [],
                "key": "text_button",
                "lines": 5,
                "list_method": "portal_catalog",
                "query": "urn:jio:allDocs?query=portal_type%3A%22Task%20Report%22",
                "portal_type": ["Task Report"],
                "search_column_list": [],
                "sort_column_list": [],
                "title": " ",
                "type": "TextAreaField"
              },
              
              "text": {
                "column_list": [
                  ['title', 'Title'],
                  ['translated_simulation_state_title', 'State']
                ],
                "show_anchor": 0,
                "default_params": {},
                "editable": 1,
                "editable_column_list": [],
                "key": "text",
                "lines": 5,
                "list_method": "portal_catalog",
                "query": "urn:jio:allDocs?query=portal_type%3A%22Task%20Report%22",
                "portal_type": ["Task Report"],
                "search_column_list": [],
                "sort_column_list": [],
                "title": " ",
                "type": "TextAreaField"
              }
            }},
              "_links": {
                "type": {
                  // form_list display portal_type in header
                  name: ""
                }
              }},
              form_definition: {
                //pt: "form_dialog",
                //title: "Upload image",
               // update_action: "",
              //  action: "triggerSubmit",
                group_list: [[
                  "left",
                  [["upload"], ["image"]]
                ], [
                  "right",
                  [["audio"], ["text_button"]]
                ], [
                  "bottom",
                  [["text"]]
                ]]
              }
            });
        });
    /*
        .push(function () {
          return RSVP.all([
            gadget.getSetting('portal_type'),
            gadget.getSetting('parent_relative_url')
          ]);
        })
        .push(function (result) {
          var ext = "img",
            ret = {
            title: "Untitled Document",
            portal_type: result[0],
            parent_relative_url: result[1],
            content_type: undefined
          };
          if (ext) {
            ret.filename = "default." + ext;
          }
          return gadget.jio_post(ret);
        })
        .push(function (id) {
          return gadget.redirect({
            command: 'display',
            options: {
              jio_key: id,
              editable: true
            }
          });
        });*/

    });

}(window, rJS, jIO, RSVP, document));