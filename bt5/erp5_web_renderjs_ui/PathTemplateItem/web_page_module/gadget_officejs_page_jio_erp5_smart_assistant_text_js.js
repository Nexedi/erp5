/*global document, window, rJS, RSVP */
/*jslint indent:2, maxlen: 80, nomen: true */
(function (document, window, rJS, RSVP) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("jio_post", "jio_post")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    .declareAcquiredMethod("getSetting", "getSetting")



    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .allowPublicAcquisition('notifySubmit', function () {
      return this.triggerSubmit();
    })

    .onEvent('submit', function () {
      var gadget = this,
        content;

      return gadget.notifySubmitting()
        .push(function () {
          return gadget.getDeclaredGadget('form_view');
        })
        .push(function (form_gadget) {
          return form_gadget.getContent();
        })
        .push(function (result) {

          content = result;
          return RSVP.all([
            gadget.getSetting('portal_type'),
            gadget.getSetting('parent_relative_url')
          ]);
        })
        .push(function (result) {
          var portal_type = result[0].split(',')[0],
            parent_relative_url = result[1].split(',')[0],
            text_html,
            title;

          if (content.text_content !== "") {
            text_html = document.createElement("div");
            text_html.innerHTML = content.text_content;
            title = text_html.textContent.split(' ').slice(0, 4).join('_');

            return gadget.jio_post({
              "title": title,
              "text_content": content.text_content,
              portal_type: portal_type,
              parent_relative_url: parent_relative_url
            })
              .push(function () {
                return gadget.notifySubmitted({"message": "Data created",
                                               "status": "success"});
              });
          }
        })
        .push(function () {
          return gadget.redirect({command: 'display',
                                  options: {page: 'ojs_smart_assistant_home'}});
        });
    })

    .declareMethod("triggerSubmit", function () {
      return this.element.querySelector('button[type="submit"]').click();
    })

    .declareMethod("render", function () {
      var gadget = this;
      return gadget.getDeclaredGadget('form_view')
        .push(function (form_gadget) {
          return form_gadget.render({
            erp5_document: {
              "_embedded": {"_view": {
                "my_content": {
                  "default": "",
                  "css_class": "",
                  "required": 0,
                  "editable": 1,
                  "key": "text_content",
                  "hidden": 0,
                  "renderjs_extra": '{"editor": "fck_editor",' +
                    '"maximize": "auto"}',
                  "type": "GadgetField",
                  "url": "gadget_editor.html",
                  "sandbox": "public"
                }
              }},
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
                [["my_title"], ["my_reference"]]
              ], [
                "right",
                [["my_version"], ["my_language"]]
              ], [
                "center",
                [["my_description"]]
              ], [
                "bottom",
                [["my_content"]]
              ]]
            }
          });
        })
        .push(function () {
          return RSVP.all([
            gadget.getUrlFor({command: 'display',
                              options: {page: 'ojs_smart_assistant_home'}}),
            gadget.getUrlFor({command: 'selection_previous'}),
            gadget.getUrlFor({command: 'selection_next'})
          ]);
        })
        .push(function (url_list) {
          return gadget.updateHeader({
            page_title: "Text editor",
            save_action: true,
            selection_url: url_list[0]
          });
        });
    });
}(document, window, rJS, RSVP));
