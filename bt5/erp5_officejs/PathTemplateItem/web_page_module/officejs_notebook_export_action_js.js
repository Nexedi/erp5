/*global window, rJS, RSVP, Blob */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, Blob) {
  "use strict";

  rJS(window)

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////

    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod('preRenderDocument', function (parent_options) {
      return this.jio_get(parent_options.jio_key);
    })

    .declareMethod('handleSubmit', function (content_dict, parent_options) {
      var gadget = this, data,
        jio_key = parent_options.action_options.jio_key,
        parent_gadget = parent_options.gadget,
        return_submit_dict = {};
      return gadget.jio_get(jio_key)
        .push(function (document) {
          return parent_gadget.getDeclaredGadget("fg");
        })
        .push(function (subgadget) {
          return subgadget.getDeclaredGadget("erp5_pt_gadget");
        })
        .push(function (subgadget) {
          return subgadget.getDeclaredGadget("erp5_form");
        })
        .push(function (erp5_form_gadget) {
          return erp5_form_gadget.getDeclaredGadget("text_content");
        })
        .push(function (result) {
          data = result.element
            .querySelector('[data-gadget-scope="editor"]').firstChild
            .contentDocument.body.firstChild.contentDocument.firstChild;
          return gadget.getDeclaredGadget("ojs_cloudooo");
        })
        .push(function (cloudooo_gadget) {
          return RSVP.all([
            cloudooo_gadget.putCloudoooConvertOperation({
              "status": "converted",
              "from": "txt",
              "to": "html",
              "id": jio_key,
              "name": "data"
            }),
            cloudooo_gadget.putCloudoooConvertOperation({
              "status": "convert",
              "from": "html",
              "to": "pdf",
              "id": jio_key,
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
            jio_key,
            'html',
            new Blob([data], {type: 'text/html'})
          );
        })
        .push(function () {
          return_submit_dict.redirect = {
            command: 'display',
            options: {
              jio_key: jio_key,
              page: 'ojs_download_convert'
            }
          };
          return return_submit_dict;
        }, function (error) {
          return_submit_dict.notify = {
            message: "Failure exporting document",
            status: "error"
          };
          return_submit_dict.redirect = {
            command: 'display',
            options: {
              jio_key: jio_key,
              editable: true
            }
          };
          return return_submit_dict;
        });
    });

}(window, rJS, RSVP, Blob));