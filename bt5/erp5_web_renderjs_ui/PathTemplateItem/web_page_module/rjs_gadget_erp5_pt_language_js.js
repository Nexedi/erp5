/*global window, rJS, RSVP, Handlebars */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, Handlebars) {
  "use strict";
  var gadget_klass = rJS(window),
    dialog_button_source = gadget_klass.__template_element
                         .getElementById("dialog-button-template")
                         .innerHTML,
    dialog_button_template = Handlebars.compile(dialog_button_source);

  gadget_klass
    .declareAcquiredMethod("translate", "translate")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("setSetting", "setSetting")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
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
        user = "Who are you?",
        header_dict = {
          page_title: 'Language'
        };

      return gadget.getUrlFor({command: 'history_previous'})
        .push(function (result) {
          header_dict.front_url = result;
          return RSVP.all([
            gadget.updateHeader(header_dict),
            gadget.getSetting('me')
          ]);
        })
        .push(function (result_list) {
          var me = result_list[0];
          if (me !== undefined) {
            return gadget.jio_allDocs({
              query: 'relative_url:"' + me + '"',
              select_list: ['title']
            })
              .push(function (result) {
                user = result.data.rows[0].value.title;
              });
          }
        })
        .push(function () {
          return gadget.jio_getAttachment(
            'portal_preferences',
            'links'
          );
        })
        .push(function (result) {
          return RSVP.all([
            gadget.getDeclaredGadget("erp5_form"),
            gadget.jio_getAttachment('portal_preferences', result._links.action_preferences.href),
            gadget.getSetting("language_map"),
            gadget.getSetting("selected_language"),
            gadget.getSetting("default_selected_language"),
            gadget.translate("Language"),
            gadget.translate("User")
          ]);
        })
        .push(function (result_list) {
          var selected_language = result_list[3] || result_list[4],
            key,
            list_item = [],
            options = JSON.parse(result_list[2]);
          gadget.state.erp5_form = result_list[0];
          gadget.state.old_selected_lang = selected_language;
          for (key in options) {
            if (options.hasOwnProperty(key)) {
              if (!result_list[1].preferred_user_interface_language_list ||
                  result_list[1].preferred_user_interface_language_list.indexOf(key) !== -1) {
                list_item.push([options[key], key]);
              }
            }
          }
          return gadget.state.erp5_form.render({
            erp5_document: {"_embedded": {"_view": {
              'User': {
                "default": user,
                "editable": 0,
                "key": "field_user",
                "title": result_list[6],
                "type": "StringField"
              },
              'Language': {
                "default": selected_language,
                "editable": 1,
                "items": list_item,
                "key": "field_language",
                "title": result_list[5],
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
          });
        })
        .push(function () {
          return gadget.translateHtml(dialog_button_template());
        })
        .push(function (result) {
          gadget.element.querySelector('.dialog_button_container')
                                   .innerHTML = result;
        });
    })
    .onEvent('submit', function () {
      var gadget = this,
        selected_lang;
      return gadget.notifySubmitting()
        .push(function () {
          return gadget.state.erp5_form.getContent();
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
    });
}(window, rJS, RSVP, Handlebars));
