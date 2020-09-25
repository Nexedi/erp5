/*global window, rJS, RSVP, Blob */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, Blob) {
  "use strict";

  function downloadFromTextContent(gadget, text_content, title) {
    var element = gadget.element,
      a = window.document.createElement("a"),
      url = window.URL.createObjectURL(new Blob([text_content], {type: 'text/plain'})),
      name_list = [title, "txt"];
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
      return { title: parent_options.form_definition.title,
               skip_action_form: true };
    })

    .declareMethod('handleSubmit', function (content_dict, parent_options) {
      var gadget = this,
        return_submit_dict = {};
      return gadget.jio_get(parent_options.action_options.jio_key)
        .push(function (document) {
          return downloadFromTextContent(gadget, document.text_content, document.title);
        })
        .push(function (jio_key) {
          return_submit_dict.redirect = {
            command: 'display',
            options: {
              jio_key: parent_options.action_options.jio_key,
              editable: true
            }
          };
          return return_submit_dict;
        }, function (error) {
          return_submit_dict.notify = {
            message: "Failure downloading document",
            status: "error"
          };
          return return_submit_dict;
        });
    });

}(window, rJS, RSVP, Blob));