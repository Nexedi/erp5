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
    .declareAcquiredMethod("jio_post", "jio_post")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("getSettingList", "getSettingList")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod('preRenderDocument', function (parent_options) {
      return { title: parent_options.form_definition.title };
    })

    .declareMethod('handleSubmit', function (content_dict, parent_options) {
      //must return a dict with:
      //notify: options_dict for notifySubmitted
      //redirect: options_dict for redirect
      var return_submit_dict = {
        notify: {
          message: "",
          status: ""
        },
        redirect: {
          command: 'display',
          options: {}
        }
      }, gadget = this;
      return gadget.jio_get(parent_options.action_options.jio_key)
        .push(function (document) {
          return downloadFromTextContent(gadget, document.text_content, document.title);
        })
        .push(function (jio_key) {
          return_submit_dict.notify.message = "File downloaded";
          return_submit_dict.notify.status = "success";
          return_submit_dict.redirect.options = {
            jio_key: jio_key,
            editable: true
          };
          return return_submit_dict;
        }, function (error) {
          return_submit_dict.notify.message = "Failure downloading document";
          return_submit_dict.notify.status = "error";
          return return_submit_dict;
        });
    });

}(window, rJS, RSVP, Blob));