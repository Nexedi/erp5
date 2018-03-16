/*global window, rJS, jIO, Handlebars, Blob*/
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
    .declareAcquiredMethod("getUrlFor", "getUrlFor")



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
      var text;
      var content;
      var global_id;
      var form;
      //var id_list = [0, 0, 0];
      var portal_type, parent_relative_url;
    
      if (!gadget.state.content) {
        gadget.state.content = {
          upload: "",
          image: ""
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
      gadget.send();
    })


    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .onEvent('submit', function () {
      var gadget = this;
    
      gadget.send();
    })
    .declareService(function () {
      var gadget = this;
      gadget.element.querySelector(".main_button").innerHTML =
        handlebars_template({
          show_update_button: false
        });
    })
  
    
  
    .declareMethod("render", function (option) {
      var gadget = this;
      
      if (option.jio_key)
        gadget.notifySubmitted({
          "message": "Data created",
          "status": "success"
        });
    
      gadget.jio_allDocs();
      
      return gadget.getDeclaredGadget('form_view')
        .push(function (form_gadget) {
          return form_gadget.render({
            erp5_document: {"_embedded": {"_view": {
              "upload": {
                "show_anchor": 0,
                "default_params": {},
                "editable": 1,
                "editable_column_list": [],
                "key": "upload",
                "lines": 5,
                "list_method": "portal_catalog",
                "query": "urn:jio:allDocs?query=portal_type%3A%22Test%20Result%22",
                "portal_type": ["Test Result"],
                "title": " ",
                "type": "FileField"
              },
              "image": {
                "editable": 1,
                "key": "image",
                "capture": "camera",
                "title": " ",
                "accept": "image/*",
                "type": "FileField"
              },
              "audio": {
                "editable": 1,
                "required": 1,
                "key": "",
                "default": {"target": "ojs_message_audio", "target_type": "audio"},
                "title": " ",
                "url": "gadget_erp5_page_ojs_link_field.html",
                "type": "GadgetField"
              },
              "text_button": {
                "editable": 1,
                "required": 1,
                "key": "",
                "title": " ",
                "default": {"target": "message_text", "target_type": "text_button"},
                "url": "gadget_erp5_page_ojs_link_field.html",
                "type": "GadgetField"
              }
            }},
              "_links": {
                "type": {
                  // form_list display portal_type in header
                  name: ""
                }
              }},
              form_definition: {
                group_list: [[
                  "left",
                  [["upload"], ["image"]]
                ], [
                  "right",
                  [["audio"], ["text_button"]]
                ]]
              }
            });
        })
        .push(function () {
          return RSVP.all([
            gadget.getSetting('document_title_plural'),
            gadget.getUrlFor({command: 'display', options: {page: "ojs_message_document_list"}})
          ]);
        })
        .push(function (list_url) {
          return gadget.updateHeader({
            page_title: list_url[0],
            selection_url: list_url[1],
            page_icon: "exchange"
          });
        });

    });

}(window, rJS, jIO, RSVP, document));