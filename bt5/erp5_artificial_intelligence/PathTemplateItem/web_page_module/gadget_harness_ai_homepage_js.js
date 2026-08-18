/*global window, rJS, RSVP, FormData, URI, jIO, domsugar */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  rJS(window)
    .declareAcquiredMethod("translate", "translate")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    .declareAcquiredMethod("redirect", "redirect")

    .declareMethod('render', function (options) {
      var gadget = this;
      return gadget.declareGadget('gadget_editor.html',  {
        element: gadget.element.querySelector('.chat-editor'),
        scope: "editor",
        sandbox: "public"
      })
      .push(function (editor) {
        return RSVP.all([
          gadget.getSetting('hateoas_url'),
          gadget.translate("Post Comment")
        ]);
      })
      .push(function (result_list) {
        gadget.hateoas_url = result_list[0];
        gadget.element.querySelector("[data-i18n='[value]Post Comment']").value = result_list[1];
        return gadget.changeState({
          'editor_state': 'initialise',
          'allow_submit': true
        });
      });
    })
    .allowPublicAcquisition('notifySubmit', function notifySubmit(e) {
      return this.submitPostComment(e);
    })
    .onStateChange(function (modification_dict) {
      var gadget = this,
        queue = new RSVP.Queue();
      if (modification_dict.hasOwnProperty("allow_submit")) {
        var submitButton = gadget.element.querySelector("input[type=submit]");
        if (modification_dict.allow_submit) {
          submitButton.disabled = false;
          submitButton.classList.remove("ui-disabled");
        } else {
          submitButton.disabled = true;
          submitButton.classList.add("ui-disabled");
        }
      }
      if (modification_dict.hasOwnProperty("editor_state")) {
        if (modification_dict.editor_state == 'initialise') {
          queue
            .push(function () {
              return gadget.getDeclaredGadget("editor");
            })
            .push(function (editor) {
              return editor.render({
                value: "",
                key: "comment",
                editable: true,
                editor: 'codemirror',
                maximize: true
              });
            });
        }
      }
      return queue;
    })
    .declareJob('submitPostComment', function () {
      var gadget = this,
        queue = null;

      return gadget.getDeclaredGadget("editor")
        .push(function (e) {
          return e.getContent();
        })
        .push(function (content) {
          if (content.comment === '') {
            return gadget.translate("Post content can not be empty!")
                .push(function (translated_message) {
                  return gadget.notifySubmitted({message: translated_message});
                });
          }
          queue = new RSVP.Queue()
            .push(function () {
              return gadget.changeState({
                allow_submit: false,
                editor_state: 'posting'
              });
            })
            .push(function () {
              var choose_file_html_element = gadget.element.querySelector('#attachment'),
                file_blob = choose_file_html_element.files[0],
                url = gadget.hateoas_url + "artificial_task_module/ArtificialTaskModule_startNewArtificialTask",
                comment_text = content.comment,
                form_data_json = {},
                post;
              form_data_json.data = comment_text || "";
              form_data_json.file = "";
              choose_file_html_element.value = "";

              post = {
                date: new Date().toISOString(),
                text: comment_text,
                response: false
              };

              return new RSVP.Queue()
                .push(function () {
                  if (file_blob) {
                    return jIO.util.readBlobAsDataURL(file_blob);
                  }
                })
                .push(function (data_url_evt) {
                  if (data_url_evt) {
                    form_data_json.file = {
                      url: data_url_evt.target.result,
                      file_name: file_blob.name
                    };
                  }
                  return gadget.jio_putAttachment(
                    'artificial_task_module',
                    url,
                    form_data_json
                  );
                })
                .push(function (evt) {
                  var uri = new URI(
                    evt.target.getResponseHeader("X-Location")
                  ),
                    redirect_jio_key = uri.segment(2);
                  return gadget.redirect({
                    command: 'display',
                    options: {
                      "jio_key": redirect_jio_key,
                      "process_task": true
                    }
                  });
                });
            }, function (e) {
                return RSVP.all([
                  gadget.changeState({
                    allow_submit: true,
                    editor_state: 'initialise'
                  }),
                  gadget.notifySubmitted({message: "Error:" + e, status: "error"})
                ]);
              });
          return queue;
        });
    })
    .onEvent('submit', function () {
      return this.submitPostComment();
    });
}(window, rJS, RSVP));
