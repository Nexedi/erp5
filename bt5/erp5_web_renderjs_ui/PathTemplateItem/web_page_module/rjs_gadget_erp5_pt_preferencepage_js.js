/*global window, document, rJS, RSVP, loopEventListener */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS, loopEventListener) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // ready
    /////////////////////////////////////////////////////////////////
    // Init local properties
    .ready(function (g) {
      g.props = {};
    })

    // Assign the element to a variable
    .ready(function (g) {
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
        });
    })

    /////////////////////////////////////////////////////////////////
    // handle acquisition
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    .declareAcquiredMethod("replace", "replace")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function () {
      var gadget = this,
        user = "Who are you?";

      return gadget.updateHeader({
        page_title: 'Preference',
        save_action: true
      })
        .push(function () {
          return gadget.getDeclaredGadget("erp5_form");
        })
        .push(function (erp5_form) {
          gadget.props.erp5_form = erp5_form;
          return gadget.getSetting('me');
        })
        .push(function (me) {
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
          return RSVP.all([
            gadget.getSetting("website_url_set"),
            gadget.getSetting("language_map"),
            gadget.getSetting("selected_language")
          ]);
        })
        .push(function (results) {
          var selected_language = results[2],
            key,
            list_item = [],
            options = JSON.parse(results[1]);
          gadget.props.website_url_set = JSON.parse(results[0]);
          gadget.props.old_selected_lang = selected_language;
          for (key in options) {
            if (options.hasOwnProperty(key)) {
              list_item.push([options[key], key]);
            }
          }
          return gadget.props.erp5_form.render({
            erp5_document: {"_embedded": {"_view": {
              'User': {
                "default": user,
                "editable": 0,
                "key": "field_user",
                "title": "User",
                "type": "StringField"
              },
              'Language': {
                "default": selected_language,
                "editable": 1,
                "items": list_item,
                "key": "field_language",
                "title": "Language",
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
      this.props.element.querySelector('button').click();
    })
    .declareService(function () {
      var gadget = this;

      function formSubmit() {
        return gadget.notifySubmitting()
          .push(function () {
            return gadget.props.erp5_form.getContent();
          })
          .push(function (data) {
            var param_list =  window.location.toString().split('#')[1],
              new_url;
            if (gadget.props.old_selected_lang !== data.field_language) {
              new_url =  gadget.props.website_url_set[data.field_language] + '#' + param_list;
              return gadget.replace(new_url);
            }
          })
          .push(function () {
            return gadget.notifySubmitted();
          });
      }

      // Listen to form submit
      return loopEventListener(
        gadget.props.element,
        'submit',
        false,
        formSubmit
      );
    });
}(window, rJS, loopEventListener));