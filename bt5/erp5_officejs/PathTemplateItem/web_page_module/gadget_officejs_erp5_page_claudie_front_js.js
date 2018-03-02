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
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("updateDocument", "updateDocument")



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
    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
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
        .push(function (result) {
          //console.log(content.data.file_name);
          var upload_name = "";
          if (content.upload)
            upload_name = content.upload.file_name;
          return gadget.jio_post({
            "title": content.title,
            "upload": upload_name,
            portal_type: result[0],
            parent_relative_url: result[1]
          });
        })
        .push(function (id) {
          global_id = id;
          return RSVP.all([
            gadget.jio_putAttachment(id, 'upload', blob_upload),
            gadget.jio_putAttachment(id, 'image', blob_image),
            gadget.jio_putAttachment(id, 'audio', blob_audio),
            gadget.jio_putAttachment(id, 'text', content.text)
          ]);
        })
        .push(function () {
          return gadget.redirect({
            command: 'display',
            options: {
              jio_key: global_id,
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
                "my_title": {
                    "description": "",
                    "title": "Title",
                    "default": "Untitled Document",
                    "css_class": "",
                    "required": 1,
                    "editable": 1,
                    "key": "title",
                    "hidden": 0,
                    "type": "StringField"
                  },

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
                "title": "Upload",
                "type": "FileField"
              },
              "image": {
                "column_list": [
                  ['title', 'Title'],
                  ['translated_simulation_state_title', 'State']
                ],
                "show_anchor": 0,
                "default_params": {},
                "editable": 1,
                "editable_column_list": [],
                "key": "image",
                "lines": 5,
                "list_method": "portal_catalog",
                "query": "urn:jio:allDocs?query=portal_type%3A%22Bug%22",
                "portal_type": ["Test Result"],
                "search_column_list": [],
                "sort_column_list": [],
                "title": "Image",
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
                "title": "Audio",
                "type": "FileField"
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
                "title": "Note",
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
                group_list: [
                  [
                    "left",
                    [["my_title"], ["upload"], ["image"], ["audio"], ["text"]]
                  ]
                ]
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