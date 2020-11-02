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
              //converts the html content to a pdf file
              //and opens a file download window
              return html2pdf(html_data.innerHTML);
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
            })
            .push(undefined, function (error) {
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
    });

}(window, document, rJS, RSVP, console));