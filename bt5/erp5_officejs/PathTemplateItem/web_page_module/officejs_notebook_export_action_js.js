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
      return this.jio_get(parent_options.jio_key);
    })

    .declareMethod('handleSubmit', function (content_dict, parent_options) {
      var gadget = this, html_data,
        parent_gadget = parent_options.gadget,
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
          var html_data = result.element
              .querySelector('[data-gadget-scope="editor"]').firstChild
              .contentDocument.body.firstChild.contentDocument.firstChild,
            notebook_execution_done = html_data
              .querySelector('[id="jsmd_eval_done"]');
          if (!notebook_execution_done) {
            return_submit_dict.notify = {
              message: "Wait until the notebook is fully executed",
              status: "error"
            };
            return return_submit_dict;
          }
          return new RSVP.Queue()
            .push(function () {
              //remove pagination script as it may cause style issues
              html_data.querySelector('[id="paged-js-source"]').remove();
              var print_preview_window = window.open('', '', 'height=400,width=800');
              print_preview_window.document.write(html_data.innerHTML);
              print_preview_window.document.title = parent_options.doc.title;
              print_preview_window.onafterprint = function () {
                print_preview_window.close();
              };
              setTimeout(() => {
                print_preview_window.document.close();
                print_preview_window.print();
              }, 3000);
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