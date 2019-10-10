/*global window, document, jIO, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, document, jIO, rJS, RSVP, Blob) {

  "use strict";

  rJS(window)

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
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
            doc: result
          });
        });
    })

    .onEvent('submit', function (event) {
      var gadget = this, html, content, cloudooo;
      return gadget.notifySubmitting()
        .push(function () {
          return gadget.getDeclaredGadget('form_view');
        })
        .push(function (form_gadget) {
          return RSVP.all([
            form_gadget.getContent(),
            gadget.getDeclaredGadget("ojs_cloudooo"),
            form_gadget.getDeclaredGadget("text_content")
          ]);
        })
        .push(function (result_list) {
          content = result_list[0];
          cloudooo = result_list[1];
          html = result_list[2].element
            .querySelector('[data-gadget-scope="editor"]').firstChild
            .contentDocument.body.firstChild.contentDocument.firstChild;
          html.firstChild.innerHTML = "";
          return RSVP.all([
            cloudooo.putCloudoooConvertOperation({
              "status": "converted",
              "from": "txt",
              "to": "html",
              "id": gadget.state.jio_key,
              "name": "data"
            }),
            cloudooo.putCloudoooConvertOperation({
              "status": "convert",
              "from": "html",
              "to": "pdf",
              "id": gadget.state.jio_key,
              "name": "html",
              "to_name": "pdf",
              "conversion_kw": {
                "encoding": ["utf8", "string"],
                "page_size": ["A4", "string"],
                "zoom" : [1, "double"],
                "dpi" : ["300", "string"],
                "header_center" : ["document Title", "string"]
              }
            })
          ]);
        })
        .push(function () {
          return gadget.jio_putAttachment(
            gadget.state.jio_key,
            'html',
            new Blob([html.outerHTML], {type: 'text/html'})
          );
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
      var gadget = this, data;
      return gadget.jio_getAttachment(gadget.state.jio_key, "data")
        .push(undefined, function (error) {
          if (error instanceof jIO.util.jIOError && error.status_code === 404) {
            return new Blob();
          }
          throw error;
        })
        .push(function (blob) {
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
                "my_content": {
                  "default": data,
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
        .push(function () {
          return RSVP.all([
            gadget.getUrlFor({
              command: 'display',
              options: {'jio_key': gadget.state.jio_key}
            }),
            gadget.getUrlFor({command: 'selection_previous'}),
            gadget.getUrlFor({command: 'selection_next'})
          ]);
        })
        .push(function (url_list) {
          return gadget.updateHeader({
            page_title: "Export",
            submit_action: true,
            selection_url: url_list[0],
            previous_url: url_list[1],
            next_url: url_list[2]
          });
        });
    });
}(window, document, jIO, rJS, RSVP, Blob));
