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
        return_submit_dict = {},
        pdfReactor = new PDFreactor("https://cloud.pdfreactor.com/service/rest");
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
            //PAGED.JS
            /*.push(function () {
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
            })*/
            //HTML2PDF
            .push(function () {
              //var element = document.getElementById('printable_id');
              console.log("html_data", html_data);
              console.log("html_data.head", html_data.head);
              return html2pdf(html_data.innerHTML);
            })
            .push(function () {
              return {};
            })
            //PDFREACTOR
            /*.push(function () {
              return pdfReactor.convert({
                document: "<html>" + html_data.innerHTML + "</html>"
              });
            })
            .push(function (result) {
              var download_pdf = document.createElement('a');
              download_pdf.href = "data:application/pdf;base64," + result.document;
              download_pdf.download = "my_pdf.pdf";
              download_pdf.click();
              return_submit_dict.redirect = {
                command: 'display',
                options: {
                  jio_key: parent_options.jio_key,
                  editable: true
                }
              };
              return return_submit_dict;
            })*/
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
        /*.push(undefined, function (error) {
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
        });*/
    });

}(window, document, rJS, RSVP, console));