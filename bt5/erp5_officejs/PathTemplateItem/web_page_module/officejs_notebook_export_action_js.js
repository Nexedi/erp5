/*global window, document, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, document, rJS, RSVP) {
  "use strict";

  rJS(window)

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////

    .declareAcquiredMethod("jio_get", "jio_get")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod('preRenderDocument', function (parent_options) {
      return this.jio_get(parent_options.jio_key);
    })

    .declareMethod('handleSubmit', function (content_dict, parent_options) {
      var gadget = this, html_data,
        parent_gadget = parent_options.gadget,
        return_submit_dict = {};
      return parent_gadget.getDeclaredGadget("fg")
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
          var print_preview_window,
              pagedjs_style = document.createElement('link'),
              pagedjs_script = document.createElement('script'),
              html_data = result.element
            .querySelector('[data-gadget-scope="editor"]').firstChild
            .contentDocument.body.firstChild.contentDocument.firstChild;
          pagedjs_style.setAttribute('type', 'text/css');
          pagedjs_style.setAttribute('href', 'interface.css');
          pagedjs_script.setAttribute('src', 'paged.polyfill.js');
          pagedjs_script.setAttribute('id', 'paged-js-source');
          print_preview_window = window.open('', '', 'height=400,width=800');
          print_preview_window.document.write(html_data.innerHTML);
          print_preview_window.document.head.appendChild(pagedjs_style);
          print_preview_window.document.head.appendChild(pagedjs_script);
          print_preview_window.document.close();
          print_preview_window.print();
        })
        .push(function () {
          return_submit_dict.redirect = {
            command: 'display',
            options: {
              jio_key: parent_options.jio_key,
              editable: true
            }
          };
          return return_submit_dict;
        }, function (error) {
          console.log("ERROR:", error);
          return_submit_dict.notify = {
            message: "Failure exporting document",
            status: "error"
          };
          return_submit_dict.redirect = {
            command: 'display',
            options: {
              jio_key: parent_options.jio_key,
              editable: true
            }
          };
          return return_submit_dict;
        });
    });

}(window, document, rJS, RSVP));