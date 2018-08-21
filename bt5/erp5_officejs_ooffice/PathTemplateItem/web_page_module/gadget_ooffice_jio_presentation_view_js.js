/*global window, rJS, RSVP, jIO, Blob */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, jIO, Blob) {
  "use strict";

  var ATT_NAME = "data";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("updateDocument", "updateDocument")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", 'notifySubmitted')
    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("render", function (options) {
      var gadget = this;
      return gadget.getSetting('file_extension', "")
        .push(function (result) {
          return gadget.changeState({
            jio_key: options.jio_key,
            doc: options.doc,
            mime_type: result,
            content_editable: options.doc.content_type === undefined ||
                options.doc.content_type.indexOf("application/x-asc") === 0
          });
        });
    })

    .onEvent('submit', function () {
      var gadget = this, data, name_list;
      return gadget.notifySubmitting()
        .push(function () {
          return gadget.getDeclaredGadget('form_view');
        })
        .push(function (form_gadget) {
          return form_gadget.getContent();
        })
        .push(function (content) {
          data = content.text_content;
          delete content.text_content;
          name_list = gadget.state.doc.filename.split('.');
          if (name_list.pop() !== gadget.state.mime_type) {
            name_list.push(gadget.state.mime_type);
            content.filename = name_list.join('.');
          }
          return gadget.updateDocument(content);
        })
        .push(function () {
          if (gadget.state.content_editable) {
            return gadget.jio_putAttachment(
              gadget.state.jio_key,
              "data",
              jIO.util.dataURItoBlob(data)
            )
              .push(function () {
                return gadget.getDeclaredGadget("ojs_cloudooo");
              })
              .push(function (cloudooo) {
                return cloudooo.putAllCloudoooConvertionOperation({
                  format: gadget.state.mime_type,
                  jio_key: gadget.state.jio_key
                });
              });
          }
        })
        .push(function () {
          return gadget.notifySubmitted({message: 'Data Updated', status: 'success'});
        });
    })

    .declareMethod("triggerSubmit", function () {
      return this.element.querySelector('button[type="submit"]').click();
    })

    .onStateChange(function () {
      var gadget = this,
        data,
        editable = gadget.state.content_editable ? 1 : 0;
      return new RSVP.Queue()
        .push(function () {
          if (!editable) {
            return gadget.jio_getAttachment(gadget.state.jio_key, "data");
          }
          return gadget.getDeclaredGadget("ojs_cloudooo")
            .push(function (ojs_cloudooo) {
              return ojs_cloudooo.getConvertedBlob({
                jio_key: gadget.state.jio_key,
                format: gadget.state.mime_type,
                filename: gadget.state.doc.filename
              });
            });
        })
        .push(undefined, function (error) {
          if (error instanceof jIO.util.jIOError && error.status_code === 404) {
            return new Blob();
          }
          throw error;
        })
        .push(function (blob) {
          if (editable) {
            return jIO.util.readBlobAsDataURL(blob);
          }
          return jIO.util.readBlobAsText(blob);
        })
        .push(function (evt) {
          data = evt.target.result;
          return gadget.getDeclaredGadget('form_view');
        })
        .push(function (form_gadget) {
          return form_gadget.render({
            erp5_document: {
              "_embedded": {"_view": {
                "my_title": {
                  "description": "",
                  "title": "Title",
                  "default": gadget.state.doc.title,
                  "css_class": "",
                  "required": 1,
                  "editable": editable,
                  "key": "title",
                  "hidden": 0,
                  "type": "StringField"
                },
                "my_reference": {
                  "description": "",
                  "title": "Reference",
                  "default": gadget.state.doc.reference,
                  "css_class": "",
                  "required": 0,
                  "editable": editable,
                  "key": "reference",
                  "hidden": 0,
                  "type": "StringField"
                },
                "my_version": {
                  "description": "",
                  "title": "Version",
                  "default": gadget.state.doc.version,
                  "css_class": "",
                  "required": 0,
                  "editable": editable,
                  "key": "version",
                  "hidden": 0,
                  "type": "StringField"
                },
                "my_language": {
                  "description": "",
                  "title": "Language",
                  "default": gadget.state.doc.language,
                  "css_class": "",
                  "required": 0,
                  "editable": editable,
                  "key": "language",
                  "hidden": 0,
                  "type": "StringField"
                },
                "my_description": {
                  "description": "",
                  "title": "Description",
                  "default": gadget.state.doc.description,
                  "css_class": "",
                  "required": 0,
                  "editable": editable,
                  "key": "description",
                  "hidden": 0,
                  "type": "TextAreaField"
                },
                "my_content": {
                  "default": data,
                  "css_class": "",
                  "required": 0,
                  "editable": editable,
                  "key": "text_content",
                  "hidden": 0,
                  "type": editable ? "GadgetField" : "EditorField",
                  "renderjs_extra": '{"editor": "onlyoffice",' +
                    '"maximize": true}',
                  "url": "gadget_editor.html",
                  "sandbox": "public"
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
                [["my_title"], ["my_reference"]]
              ], [
                "right",
                [["my_version"], ["my_language"]]
              ], [
                "center",
                [["my_description"]]
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
            gadget.getUrlFor({command: 'selection_next'}),
            gadget.getUrlFor({
              command: 'change',
              options: {'page': "ojs_download_convert"}
            })
          ]);
        })
        .push(function (url_list) {
          return gadget.updateHeader({
            page_title: gadget.state.doc.title,
            selection_url: url_list[0],
            previous_url: url_list[1],
            next_url: url_list[2],
            save_action: editable,
            download_url: url_list[3]
          });
        });
    });
}(window, rJS, RSVP, jIO, Blob));