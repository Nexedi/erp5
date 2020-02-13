/*global window, rJS, RSVP, domsugar */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, domsugar) {
  "use strict";

  rJS(window)
    .declareAcquiredMethod("getTranslationList", "getTranslationList")
    .declareAcquiredMethod("getSettingList", "getSettingList")
    .declareAcquiredMethod("setSetting", "setSetting")
    .declareAcquiredMethod("getUrlForList", "getUrlForList")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("updateHeader", "updateHeader")


    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function () {
      var gadget = this,
        first_result_list;

      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.getUrlForList([{command: 'display'}]),
            gadget.getSettingList(['me', 'language_map', 'selected_language',
                                   'default_selected_language']),
            gadget.getDeclaredGadget("erp5_form"),
            gadget.getTranslationList(['Language', 'User', 'Update'])
          ]);
        })
        .push(function (result_list) {
          first_result_list = result_list;
          var me = result_list[1][0];
          if (me !== undefined) {
            return gadget.jio_allDocs({
              query: 'relative_url:"' + me + '"',
              select_list: ['title']
            });
          }
        })
        .push(function (result) {
          var user,
            selected_language = first_result_list[1][2] ||
                                first_result_list[1][3],
            key,
            list_item = [],
            options = JSON.parse(first_result_list[1][1]);
          gadget.state.old_selected_lang = selected_language;

          // Calculate user name
          if (result === undefined) {
            user = "Who are you?";
          } else {
            user = result.data.rows[0].value.title;
          }

          // Calculate possible language list
          for (key in options) {
            if (options.hasOwnProperty(key)) {
              list_item.push([options[key], key]);
            }
          }

          domsugar(gadget.element.querySelector('.dialog_button_container'), [
            domsugar('input', {name: 'action_update',
                               type: 'submit',
                               value: first_result_list[3][2]})
          ]);

          return RSVP.all([
            gadget.updateHeader({
              page_title: 'Language',
              page_icon: 'flag',
              front_url: first_result_list[0][0]
            }),

            first_result_list[2].render({
              erp5_document: {"_embedded": {"_view": {
                'User': {
                  "default": user,
                  "editable": 0,
                  "key": "field_user",
                  "title": first_result_list[3][1],
                  "type": "StringField"
                },
                'Language': {
                  "default": selected_language,
                  "editable": 1,
                  "items": list_item,
                  "key": "field_language",
                  "title": first_result_list[3][0],
                  "type": "ListField"
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
                  [["User"], ["Language"]]
                ]]
              }
            })

          ]);
        });

    })

    .onEvent('submit', function () {
      var gadget = this,
        selected_lang;
      return gadget.notifySubmitting()
        .push(function () {
          return gadget.getDeclaredGadget("erp5_form");
        })
        .push(function (erp5_form) {
          return erp5_form.getContent();
        })
        .push(function (data) {
          selected_lang = data.field_language;
          return gadget.setSetting("selected_language", selected_lang);
        })
        .push(function () {
          if (gadget.state.old_selected_lang !== selected_lang) {
            return gadget.redirect({
              command: 'change_language',
              options: {
                language: selected_lang
              }
            });
          }
          return gadget.notifySubmitted();
        });
    })
    .declareMethod("triggerSubmit", function () {
      return;
    });
}(window, rJS, RSVP, domsugar));
