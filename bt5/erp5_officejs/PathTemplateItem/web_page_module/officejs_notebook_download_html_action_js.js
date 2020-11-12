/*global window, document, rJS, RSVP, Blob, console */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, document, rJS, RSVP, Blob, console) {
  "use strict";

  function downloadHTML(gadget, html_content, title) {
    var element = gadget.element,
      a = window.document.createElement("a"),
      url = window.URL.createObjectURL(new Blob([html_content], {type: 'text/plain'})),
      name_list = [title, "html"];
    element.appendChild(a);
    a.style = "display: none";
    a.href = url;
    a.download = name_list.join('.');
    a.click();
    element.removeChild(a);
    window.URL.revokeObjectURL(url);
  }

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
            delete return_submit_dict.redirect;
            return return_submit_dict;
          }
          return new RSVP.Queue()
            .push(function () {
              //remove notebook source as it may cause style issues
              html_data.querySelector('[id="jsmd-source"]').remove();
              return downloadHTML(gadget, html_data.innerHTML, parent_options.doc.title);
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
              return_submit_dict.redirect = {
                command: 'display',
                options: {
                  jio_key: parent_options.action_options.jio_key,
                  editable: true
                }
              };
              return return_submit_dict;
            });
        });
    });

}(window, document, rJS, RSVP, Blob, console));