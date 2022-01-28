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
          'Confirm'
        ]),
        erp5_form: gadget.getDeclaredGadget("erp5_form"),
        url_dict: gadget.getUrlForDict({
          // Back url
          back: {command: 'history_previous'}
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
              front_url: result_dict.url_dict.back
            }),

            result_dict.erp5_form.render({
              erp5_document: {"_embedded": {"_view": {
              }},
                "_links": {
                  "type": {
                    // form_list display portal_type in header
                    name: ""
                  }
                }
                },
              form_definition: {
                group_list: []
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