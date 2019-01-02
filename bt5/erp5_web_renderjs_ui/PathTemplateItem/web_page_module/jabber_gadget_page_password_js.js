/*global window, rJS*/
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS) {
  "use strict";

  function validatePassword(password1, password2) {
    return (password1 === password2);
  }

  rJS(window)

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('render', function () {
      return this.changeState({
        first_render: true
      });
    })

    .onStateChange(function () {
      var gadget = this;
      return gadget.getUrlFor({
        command: 'display_stored_state',
        options: {page: 'jabberclient_contact'}
      })
        .push(function (url) {
          return gadget.updateHeader({
            page_title: 'Reset Password',
            page_icon: 'power-off',
            cancel_url: url
          });
        })
        .push(function () {
          return gadget.getDeclaredGadget("form_dialog");
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
                "left",
                [["server"], ["new_passwd"], ["repeat_passwd"]]
              ]]
            }
          });
        });
    })

    .allowPublicAcquisition("submitContent", function submitContent(param_list) {
      var gadget = this,
        content_dict = param_list[0];
      if (validatePassword(content_dict.new_passwd, content_dict.repeat_passwd)) {
        return gadget.jio_put(
          'PASSWORD',
          content_dict
        )
          .push(function () {
            return gadget.redirect({
              command: 'display_stored_state',
              options: {page: 'jabberclient_contact'}
            });
          });
      }
      return gadget.notifySubmitted({
        'message': "Passwords do not match.",
        'status': 'error'
      });
    });

}(window, rJS));