/*global window, rJS, UriTemplate, domsugar, RSVP */
/*jslint indent: 2, maxerr: 3, nomen: true */
(function (window, rJS, UriTemplate, domsugar, RSVP) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // handle acquisition
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("getUrlForDict", "getUrlForDict")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("getTranslationDict", "getTranslationDict")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function () {
      var gadget = this;

      return new RSVP.Queue(RSVP.hash({
        translation: gadget.getTranslationDict([
          'Confirm',
          'User'
        ]),
        me: gadget.getSetting('me')
          .push(function (me) {
            if (me !== undefined) {
              return gadget.jio_allDocs({
                query: 'relative_url:"' + me + '"',
                select_list: ['title']
              });
            }
          })
          .push(function (result) {
            var user;
            // Calculate user name
            if (result === undefined) {
              user = "Who are you?";
            } else {
              user = result.data.rows[0].value.title;
            }
            return user;
          }),
        erp5_form: gadget.getDeclaredGadget("erp5_form"),
        url_dict: gadget.getUrlForDict({
          // Back url
          back: {command: 'display'},
          // Change language
          change_language: {command: 'display', options: {page: 'language'}}
        })
      }))
        .push(function (result_dict) {
          domsugar(gadget.element.querySelector('.dialog_button_container'), [
            domsugar('input', {name: 'action_update',
                               type: 'submit',
                               value: result_dict.translation.Confirm})
          ]);
          return RSVP.all([
            gadget.updateHeader({
              page_title: 'Logout',
              page_icon: 'power-off',
              front_url: result_dict.url_dict.back,
              language_url: result_dict.url_dict.change_language
            }),

            result_dict.erp5_form.render({
              erp5_document: {"_embedded": {"_view": {
                'User': {
                  "default": result_dict.me,
                  "editable": 0,
                  "key": "field_user",
                  "title": result_dict.translation.User,
                  "type": "StringField"
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
                  [["User"]]
                ]]
              }
            })

          ]);
        });
    })

    .onEvent('submit', function () {
      var gadget = this,
        logout_url_template;

      return gadget.jio_getAttachment('acl_users', 'links')
        .push(function (links) {
          logout_url_template = links._links.logout.href;
          return gadget.getUrlFor({
            command: 'display',
            absolute_url: true,
            options: {}
          });
        })
        .push(function (came_from) {
          return gadget.redirect({
            command: 'raw',
            options: {
              url: UriTemplate.parse(logout_url_template).expand({came_from: came_from})
            }
          });
        });
    })
    .declareMethod("triggerSubmit", function () {
      return;
    });
}(window, rJS, UriTemplate, domsugar, RSVP));