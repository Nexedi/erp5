/*global window, rJS, jIO, Handlebars, RSVP, Blob*/
/*jslint indent:2, maxlen: 80, nomen: true */
(function (window, rJS, jIO, RSVP) {
  "use strict";

  rJS(window)

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("jio_post", "jio_post")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("notifyChange", "notifyChange")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")



    .allowPublicAcquisition('updateHeader', function () {
      return;
    })

    .declareMethod("send", function (scope) {
      var gadget = this,
        blob,
        name,
        portal_type = gadget.props.portal_type,
        parent_relative_url = gadget.props.parent_relative_url;

      return RSVP.Queue()
        .push(function () {
          return gadget.getDeclaredGadget(scope);
        })
        .push(function (form) {
          return form.getContent();
        })
        .push(function (result) {
          if (scope === "form_view_upload_audio" && result.upload) {
            blob = jIO.util.dataURItoBlob(result.upload.url);
            portal_type = portal_type[3];
            parent_relative_url = parent_relative_url[3];
            name = result.upload.file_name;
          } else if (scope === "form_view_image_text" && result.image) {
            blob = jIO.util.dataURItoBlob(result.image.url);
            portal_type = portal_type[1];
            parent_relative_url = parent_relative_url[1];
            name = result.image.file_name;
          }
          if (blob) {
            return gadget.notifySubmitting()
              .push(function () {
                return gadget.jio_post({
                  "title": name,
                  portal_type: portal_type,
                  parent_relative_url: parent_relative_url
                });
              })
              .push(function (id) {
                return gadget.jio_putAttachment(id, 'data', blob);
              })
              .push(function () {
                return gadget.notifySubmitted({
                  "message": "Data created",
                  "status": "success"
                });
              });
          }
        });
    })
    .allowPublicAcquisition('notifyChange', function (result, scope) {
      /*jslint unparam: true*/
      if (result[0] === "change") {
        return this.send(scope);
      }
    })


    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .ready(function (g) {
      return RSVP.Queue()
        .push(function () {
          return RSVP.all([
            g.getSetting('portal_type'),
            g.getSetting('parent_relative_url')
          ]);
        })
        .push(function (result) {
          g.props = {
            portal_type: result[0].split(','),
            parent_relative_url: result[1].split(',')
          };
        });
    })
    .declareMethod("render", function () {
      var gadget = this;
      return gadget.getSetting('jio_storage_name')
        .push(function (result) {
          if (!result) {
            return gadget.redirect({command: 'display',
                                    options: {page: 'ojs_configurator'}});
          }
        })
        .push(function () {
          return RSVP.all([
            gadget.getDeclaredGadget('form_view_upload_audio'),
            gadget.getDeclaredGadget('form_view_image_text')
          ]);
        })
        .push(function (result) {
          return RSVP.all([
            result[0].render({
              erp5_document: {"_embedded": {"_view": {
                "upload": {
                  "editable": 1,
                  "key": "upload",
                  "css_class":
                    "ui-view-only-label ui-label-circle ui-label-icon-files-o",
                  "title": " ",
                  "type": "FileField"
                },
                "audio": {
                  "editable": 1,
                  "required": 1,
                  "key": "",
                  "css_class": "invisible ui-a-circle ui-a-icon-microphone",
                  "default": {"target": "ojs_smart_assistant_audio",
                              "target_type": "audio"},
                  "title": " ",
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
                  [["upload"]]
                ], [
                  "right",
                  [["audio"]]
                ]]
              }
            }),

            result[1].render({
              erp5_document: {"_embedded": {"_view": {
                "image": {
                  "editable": 1,
                  "key": "image",
                  "css_class":
                    "ui-view-only-label ui-label-circle ui-label-icon-camera",
                  "capture": "camera",
                  "title": " ",
                  "accept": "image/*",
                  "type": "FileField"
                },
                "text": {
                  "editable": 1,
                  "required": 1,
                  "key": "",
                  "css_class":
                    "invisible ui-a-circle ui-a-icon-pencil-square-o",
                  "title": " ",
                  "default": {"target": "smart_assistant_text",
                              "target_type": "text"},
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
                  [["image"]]
                ], [
                  "right",
                  [["text"]]
                ]]
              }
            })
          ]);
        })
        .push(function () {
          return RSVP.all([
            gadget.getSetting('document_title_plural'),
            gadget.getUrlFor({command: 'display',
                              options:
                              {page: "ojs_smart_assistant_document_list"}
                             })
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

}(window, rJS, jIO, RSVP));