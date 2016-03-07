/*global window, rJS, RSVP, loopEventListener*/
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, loopEventListener) {
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
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("redirect", "redirect")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('triggerSubmit', function () {
      this.props.element.querySelector('button').click();
    })
    .declareMethod("render", function () {
      var page_gadget = this,
        data;
      return page_gadget.updateHeader({
        page_title: 'Connect to a Jabber server',
        submit_action: true
      })
        .push(function () {
          return page_gadget.jio_get("CONNECTION");
        })
        .push(function (result) {
          data = result;
          return page_gadget.getDeclaredGadget("erp5_form");
        })
        .push(function (form_gadget) {
          return form_gadget.render({
            erp5_document: {"_embedded": {"_view": {
              "server": {
                "description": "",
                "title": "Server URL",
                "default": data.server,
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "server",
                "hidden": 0,
                "type": "StringField"
              },
              "jid": {
                "description": "",
                "title": "Jabber ID",
                "default": data.jid,
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "jid",
                "hidden": 0,
                "type": "StringField"
              },
              "passwd": {
                "description": "",
                "title": "Password",
                "default": data.passwd,
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "passwd",
                "hidden": 0,
                "type": "PasswordField"
              }
            }}},
            form_definition: {
              group_list: [[
                "center",
                [["server"], ["jid"], ["passwd"]]
              ]]
            }
          });
        });
    })

    .declareService(function () {
      var form_gadget = this;

      function formSubmit() {
        return form_gadget.notifySubmitting()
          .push(function () {
            return form_gadget.getDeclaredGadget("erp5_form");
          })
          .push(function (erp5_form) {
            return erp5_form.getContent();
          })
          .push(function (content_dict) {
            return form_gadget.jio_put(
              'CONNECTION',
              content_dict
            );
          })
          .push(function () {
            return RSVP.all([
              form_gadget.notifySubmitted(),
              form_gadget.redirect({command: 'display', options: {page: 'contact'}})
            ]);
          })
          .push(undefined, function (error) {
            return form_gadget.notifySubmitted()
              .push(function () {
                form_gadget.props.element.querySelector('pre').textContent = error;
              });
          });
      }

      // Listen to form submit
      return loopEventListener(
        form_gadget.props.element.querySelector('form'),
        'submit',
        false,
        formSubmit
      );
    });

}(window, rJS, RSVP, loopEventListener));