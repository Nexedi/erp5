/*global window, rJS, RSVP */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // handle acquisition
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("translate", "translate")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("setSetting", "setSetting")
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    .declareAcquiredMethod("reload", "reload")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .allowPublicAcquisition("notifyChange", function (argument_list) {
      return;
    })
    .declareMethod("render", function () {
      var gadget = this,
        user = "Who are you?";
      return gadget.updateHeader({
        page_title: 'Preferences',
        save_action: true
      })
        .push(function () {
          return gadget.getDeclaredGadget("erp5_form");
        })
        .push(function (erp5_form) {
          gadget.state.erp5_form = erp5_form;
          return gadget.getSetting('me');
        })
        .push(function (me) {
          if (me !== undefined) {
           return gadget.jio_allDocs({
             query: 'portal_type: Person' ,
             select_list: ['first_name', 'last_name'],
             limit: [0, 1]
            })
             .push(function (result) {
               if (result.data.rows.length) {
                 user = result.data.rows[0].value.first_name + " " + result.data.rows[0].value.last_name;
               } else {
                 user = 'unknown';
               }
             });
          }
        })
        .push(function () {
          return RSVP.all([
            gadget.getSetting("language_map"),
            gadget.getSetting("selected_language"),
            gadget.getSetting("default_selected_language"),
            gadget.translate("User"),
            gadget.translate("Language")
            
          ]);
        })
        .push(function (results) {
          var selected_language = results[1] || results[2],
            key,
            list_item = [],
            options = JSON.parse(results[0]);
          gadget.state.old_selected_lang = selected_language;
          for (key in options) {
            if (options.hasOwnProperty(key)) {
              list_item.push([options[key], key]);
            }
          }
          return gadget.state.erp5_form.render({
            erp5_document: {"_embedded": {"_view": {
              'User': {
                "default": user,
                "editable": 0,
                "key": "field_user",
                "title": results[3],
                "type": "StringField"
              },
              'Language': {
                "default": selected_language,
                "editable": 1,
                "items": list_item,
                "key": "field_language",
                "title": results[4],
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
        });
    })
    .declareMethod('triggerSubmit', function () {
      this.element.querySelector('button').click();
    })
    .onEvent('submit', function () {
      var gadget = this,
        selected_lang;
      
      return gadget.state.erp5_form.getContent()
        .push(function (data) {
          selected_lang = data.field_language;
          return gadget.setSetting("selected_language", selected_lang);
        })
        .push(function () {
          if (gadget.state.old_selected_lang !== selected_lang) {
            return gadget.reload();
          }
        });
    });
}(window, rJS, RSVP));
