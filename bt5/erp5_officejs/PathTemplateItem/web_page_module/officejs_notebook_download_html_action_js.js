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

  function removeScripts(head_inner_html) {
    var div = document.createElement('div'), script_list, i;
    div.innerHTML = head_inner_html;
    script_list = div.getElementsByTagName('script');
    i = script_list.length;
    while (i > 0) {
      i -= 1;
      script_list[i].parentNode.removeChild(script_list[i]);
    }
    return div.innerHTML;
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
      /*jslint unparam: true*/
      var gadget = this,
        notebook_html,
        return_submit_dict = {};
      return_submit_dict.redirect = {
        command: 'display',
        options: {
          jio_key: parent_options.action_options.jio_key,
          editable: true
        }
      };
      return parent_options.gadget.getDeclaredGadget("fg")
        .push(function (form_gadget) {
          return form_gadget.getContent();
        })
        .push(function (content_dict) {
          if (Object.keys(content_dict).length === 0) {
            return_submit_dict.notify = {
              message: "Wait until the notebook is fully executed",
              status: "error"
            };
            delete return_submit_dict.redirect;
            return return_submit_dict;
          }
          notebook_html = removeScripts(content_dict.text_content);
          return new RSVP.Queue()
            .push(function () {
              return downloadHTML(gadget, notebook_html,
                                  parent_options.doc.title);
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
  /*jslint unparam: false*/

}(window, document, rJS, RSVP, Blob, console));