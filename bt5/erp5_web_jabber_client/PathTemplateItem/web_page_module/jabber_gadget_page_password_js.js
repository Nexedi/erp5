/*global window, rJS, RSVP, loopEventListener*/
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, loopEventListener) {
  "use strict";

  function validatePassword(password1, password2) {
    return (password1 === password2);
  }

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
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("redirect", "redirect")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('triggerSubmit', function () {
      this.props.element.querySelector('button').click();
    })
    .declareMethod("render", function () {
      var page_gadget = this;
      return page_gadget.updateHeader({
        page_title: 'Reset Password',
        submit_action: true
      })
        .push(function () {
          // Ensure user is connected...
          return page_gadget.jio_allDocs();
        })
        .push(function () {
          return page_gadget.getDeclaredGadget("erp5_form");
        })
        .push(function (form_gadget) {
          return form_gadget.render({
            erp5_document: {"_embedded": {"_view": {
              "server": {
                "description": "",
                "title": "Server URL",
                "default": "nexedi.com",
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "server",
                "hidden": 0,
                "type": "StringField"
              },
              "new_passwd": {
                "description": "",
                "title": "New Password",
                "default": "",
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "new_passwd",
                "hidden": 0,
                "type": "PasswordField"
              },
              "repeat_passwd": {
                "description": "",
                "title": "Repeat Password",
                "default": "",
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "repeat_passwd",
                "hidden": 0,
                "type": "PasswordField"
              }
            }}},
            form_definition: {
              group_list: [[
                "center",
                [["server"], ["new_passwd"], ["repeat_passwd"]]
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
            if (validatePassword(content_dict.new_passwd, content_dict.repeat_passwd)) {
              return form_gadget.jio_put(
                'PASSWORD',
                content_dict
              );
            }
            // XXX Uses field validation instead...
            throw new Error('Password does not match.');
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
                throw error;
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