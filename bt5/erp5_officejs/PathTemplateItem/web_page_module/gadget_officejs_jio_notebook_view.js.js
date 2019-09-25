/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, document, rJS, RSVP, promiseEventListener, Blob, DOMParser) {

  "use strict";
  
  var ATT_NAME = "data";
  
  
  function ExportContent(gadget) {
    var html = (new DOMParser()).parseFromString('<html><head><head><body><p></p></body></html>', 'text/html').documentElement;
    html.querySelector('p').innerHTML = gadget.state.doc.text_content;
    if (!gadget.state.editable) {
      html = document.querySelector('[data-gadget-scope="editor"]').firstChild.contentDocument.body.firstChild.contentDocument.firstChild;
    }
    html.firstChild.innerHTML = "";
    return new RSVP.Queue()
      .push(function () {
          return gadget.jio_putAttachment(
              gadget.state.jio_key,
              "data",
              new Blob([html.outerHTML], {type: 'text/html'})
          )
          .push(function () {
            return gadget.jio_putAttachment(
              gadget.state.jio_key,
              "options",
              JSON.stringify({
                encoding: ["utf8", "string"],
                page_size: ["A4", "string"],
                zoom : [1, "double"],
                dpi : ["300", "string"],
                header_center : ["document Title", "string"]
              })
            );
          });
        })
        .push(function () {
          return gadget.getDeclaredGadget("ojs_cloudooo");
        })
        .push(function (cloudooo) {
          return gadget.jio_getAttachment(gadget.state.jio_key, "options", {"format": "json"})
          .push(function (options) {
            return cloudooo.putAllCloudoooConvertionOperation({
              format: "html",
              jio_key: gadget.state.jio_key,
              conversion_kw : options
            });
          });
        });
  }

  rJS(window)
  
  .allowPublicAcquisition('triggerEditable', function (options) {
    var gadget = this;
    return new RSVP.Queue()
    .push(function () {
      return gadget.getDeclaredGadget('form_view');
    })
    .push(function (form_gadget) {
      return form_gadget.getContent();
    })
    .push(function (content) {
      for (var key in gadget.state.doc) {
        if (!(key in content)) {content[key] = gadget.state.doc[key]; }
      }
      return gadget.changeState({
          doc: content,
          editable: options[0].editable
        });
    });
  })

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("updateDocument", "updateDocument")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", 'notifySubmitted')

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
  
  .declareService(function () {
    var gadget = this,
        props = gadget.__sub_gadget_dict.form_view,
        div = props.element.querySelector("div");
    return new RSVP.Queue()
    .push(function () {
      return promiseEventListener(div, "load", true);
    })
    .push(function (my_event) {
      document.querySelector('[data-i18n="Export"]').addEventListener("click", function () { ExportContent(gadget); }, false);
    });
  })
  
    .declareMethod("render", function (options) {

      var gadget = this;
      return new RSVP.Queue()
      .push(function () {
        return gadget.changeState({
          jio_key: options.jio_key,
          doc: options.doc,
          editable: options.editable
        });
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
          return gadget.updateDocument(content);
        })
        .push(function () {
          return gadget.notifySubmitted({message: 'Data Updated', status: 'success'});
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
              "_embedded": {"_view": {
                "my_title": {
                  "description": "",
                  "title": "Title",
                  "default": gadget.state.doc.title,
                  "css_class": "",
                  "required": 1,
                  "editable": gadget.state.editable,
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
                  "editable": gadget.state.editable,
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
                  "editable": gadget.state.editable,
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
                  "editable": gadget.state.editable,
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
                  "editable": gadget.state.editable,
                  "key": "description",
                  "hidden": 0,
                  "type": "TextAreaField"
                },
                "my_content": {
                  "default": gadget.state.doc.text_content,
                  "css_class": "",
                  "required": 0,
                  "editable": gadget.state.editable,
                  "key": "text_content",
                  "hidden": 0,
                  "type": "GadgetField",
                  "url": "gadget_editor.html",
                  "sandbox": "public",
                  "renderjs_extra": '{"editor": "jsmd_editor", "maximize": true}'
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
              options: {'page': "ojs_download"}
            })
          ]);
        })
        .push(function (url_list) {
          return gadget.updateHeader({
            page_title: gadget.state.doc.title,
            save_action: true,
            selection_url: url_list[0],
            previous_url: url_list[1],
            next_url: url_list[2],
            export_url: url_list[3]
          });
        });
    });
}(window, document, rJS, RSVP, promiseEventListener, Blob, DOMParser));
