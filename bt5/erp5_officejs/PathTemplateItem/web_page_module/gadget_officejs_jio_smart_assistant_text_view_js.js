/*global window, rJS, RSVP, URL,
  promiseEventListener, document*/
/*jslint indent:2, maxlen: 80, nomen: true */
(function (window, rJS, RSVP) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("updateDocument", "updateDocument")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("jio_get", "jio_get")


    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function (options) {
      var gadget = this,
        state = {
          title: options.doc.title,
          jio_key: options.jio_key
        };

      gadget.type = options.doc.type;

      return gadget.jio_get(options.jio_key)
        .push(function (content) {
          state.content = content;
          state.text = content.text_content;

          return RSVP.all([
            gadget.getUrlFor({command: 'history_previous'}),
            gadget.getUrlFor({command: 'selection_previous'}),
            gadget.getUrlFor({command: 'selection_next'}),
            gadget.changeState(state)
          ]);
        })
        .push(function (url_list) {
          return gadget.updateHeader({
            page_title: "Smart Assistant",
            save_action: true,
            selection_url: url_list[0],
            previous_url: url_list[1],
            next_url: url_list[2]
          });
        });
    })

    .onEvent('submit', function () {
      var gadget = this;

      return gadget.notifySubmitting()
        .push(function () {
          return gadget.getDeclaredGadget('form_view');
        })
        .push(function (form_gadget) {
          return form_gadget.getContent();
        })
        .push(function (result) {
          var reply = result.reply;
          return gadget.updateDocument({
            'text_content': gadget.state.content.text_content + "\n" + reply
          });
        })
        .push(function () {
          return gadget.notifySubmitted({
            "message": "Data Updated",
            "status": "success"
          });
        })
        .push(function () {
          return gadget.redirect({command: 'reload'});
        });
    })
    .declareMethod("triggerSubmit", function () {
      return this.element.querySelector('button[type="submit"]').click();
    })

    .onStateChange(function () {
      var gadget = this;

      return gadget.getDeclaredGadget('form_view')
        .push(function (form_gadget) {
          return form_gadget.render({
            erp5_document: {
              "_embedded": {
                "_view": {
                  "my_title": {
                    "description": "",
                    "title": "Title",
                    "default": gadget.state.title,
                    "css_class": "",
                    "required": 1,
                    "editable": 1,
                    "key": "title",
                    "hidden": 0,
                    "type": "StringField"
                  },
                  "my_text_content": {
                    "default": gadget.state.content.text_content,
                    "css_class": "",
                    "required": 0,
                    "editable": 0,
                    "key": "text_content",
                    "hidden": 0,
                    "title": 'History',
                    "type": "TextAreaField"
                  },
                  "my_reply": {
                    "default": "",
                    "title": "Reply",
                    "css_class": "",
                    "required": 0,
                    "editable": 1,
                    "key": "reply",
                    "hidden": 0,
                    "renderjs_extra": '{"editor": "fck_editor"}',
                    "type": "GadgetField",
                    "url": "gadget_editor.html",
                    "sandbox": "public"
                  }
                }
              },
              "_links": {
                "type": {
                  // form_list display portal_type in header
                  name: ""
                }
              }
            },
            form_definition: {
              group_list: [[
                "left",
                [["my_title"]]
              ], [
                "center",
                [["my_text_content"]]
              ], [
                "bottom",
                [["my_reply"]]
              ]]
            }
          });
        });
    });
}(window, rJS, RSVP));