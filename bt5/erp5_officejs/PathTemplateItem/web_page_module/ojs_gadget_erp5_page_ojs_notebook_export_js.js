/*global window, document, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, document, rJS, RSVP, Blob) {

  "use strict";

  rJS(window)

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", 'notifySubmitted')
    .declareAcquiredMethod("redirect", 'redirect')

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("render", function (options) {

      var gadget = this;
      return gadget.jio_get(options.jio_key)
        .push(function (result) {
          return gadget.changeState({
            jio_key: options.jio_key,
            doc: result,
            editable: options.editable
          });
        });
    })

    .onEvent('submit', function (event) {
      var gadget = this, data, html;
      return gadget.notifySubmitting()
        .push(function () {
          return gadget.getDeclaredGadget('form_view');
        })
        .push(function (form_gadget) {
          return form_gadget.getContent();
        })
        .push(function (content) {
          html = document.querySelector('[data-gadget-scope="editor"]').firstChild.contentDocument.body.firstChild.contentDocument.firstChild;
          html.firstChild.innerHTML = "";
          return gadget.jio_putAttachment(
            gadget.state.jio_key,
            "data",
            new Blob([html.outerHTML], {type: 'text/html'})
          )
            .push(function () {
              return gadget.getDeclaredGadget("ojs_cloudooo");
            })
            .push(function (cloudooo) {
              return cloudooo.putAllCloudoooConvertionOperation({
                format: "html",
                jio_key: gadget.state.jio_key,
                conversion_kw: {encoding: ["utf8", "string"],
                                page_size: ["A4", "string"],
                                zoom : [1, "double"],
                                dpi : ["300", "string"],
                                header_center : ["document Title", "string"]
                               }
              });
            });
        })
        .push(function () {
          return gadget.notifySubmitted();
        })
        .push(function () {
          return gadget.redirect({
            'command': 'display',
            'options': {
              'page': 'ojs_download_convert',
              'jio_key': gadget.state.jio_key
            }
          });
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
                "my_content": {
                  "default": gadget.state.doc.text_content,
                  "css_class": "",
                  "required": 0,
                  "editable": 0,
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
                []
              ], [
                "right",
                []
              ], [
                "center",
                []
              ], [
                "bottom",
                [["my_content"]]
              ]]
            }
          });
        })
        .push(function (url_list) {
          return gadget.updateHeader({
            page_title: "Export",
            submit_action: true
          });
        });
    });
}(window, document, rJS, RSVP, Blob));
