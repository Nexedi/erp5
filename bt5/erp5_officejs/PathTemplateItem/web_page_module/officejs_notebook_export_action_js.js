/*global window, document, rJS, RSVP, console */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, document, rJS, RSVP, console) {
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
      return this.jio_get(parent_options.jio_key)
        .push(function (doc) {
          //add pagination cells at the end of the notebook
          doc.text_content += '\n%% resource\n' +
            'paged.polyfill.js\n' +
            'interface.css';
          return doc;
        });
    })

    .declareMethod('handleSubmit', function (content_dict, parent_options) {
      var gadget = this, notebook_html, notebook_editor_iframe,
        parent_gadget = parent_options.gadget, print_preview_window,
        return_submit_dict = {};
      return_submit_dict.redirect = {
        command: 'display',
        options: {
          jio_key: parent_options.action_options.jio_key,
          editable: true
        }
      };
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
          notebook_editor_iframe = result.element
            .querySelector('[data-gadget-scope="editor"]').firstChild
            .contentDocument.body.firstChild;
          if (notebook_editor_iframe.tagName !== "IFRAME") {
            return_submit_dict.notify = {
              message: "Wait until the notebook is fully executed",
              status: "error"
            };
            delete return_submit_dict.redirect;
            return return_submit_dict;
          }
          notebook_html = notebook_editor_iframe.contentDocument.firstChild;
          return new RSVP.Queue()
            .push(function () {
              //remove notebook source as it may cause style issues
              notebook_html.querySelector('[id="jsmd-source"]').remove();
              print_preview_window = window.open('', '', 'height=400,width=800');
              print_preview_window.document.write(notebook_html.innerHTML);
              print_preview_window.document.title = parent_options.doc.title;
              print_preview_window.onafterprint = function () {
                print_preview_window.close();
              };
              return print_preview_window.document.close();
            })
            .push(function () {
              print_preview_window.print();
            })
            .push(function () {
              return return_submit_dict;
            })
            .push(undefined, function (error) {
              console.log("ERROR:", error);
              return_submit_dict.notify = {
                message: "Failure exporting document",
                status: "error"
              };
              return return_submit_dict;
            });
        });
    });

}(window, document, rJS, RSVP, console));