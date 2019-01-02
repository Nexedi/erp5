/*global window, rJS*/
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS) {
  "use strict";

  rJS(window)

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("redirect", "redirect")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('render', function () {
      var gadget = this;
      return gadget.jio_get("CONNECTION")
        .push(function (data) {
          return gadget.changeState({
            server: data.server,
            jid: data.jid,
            passwd: data.passwd
          });
        });
    })

    .onStateChange(function () {
      var gadget = this;

      return gadget.updateHeader({
        page_title: 'Connect to a Jabber server'
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
                "default": gadget.state.server,
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
                "default": gadget.state.jid,
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
                "default": gadget.state.passwd,
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
                "left",
                [["server"], ["jid"], ["passwd"]]
              ]]
            }
          });
        });
    })

    .allowPublicAcquisition("submitContent", function submitContent(param_list) {
      var gadget = this,
        content_dict = param_list[0];
      return gadget.jio_put(
        'CONNECTION',
        content_dict
      )
        .push(function () {
          return gadget.redirect({
            command: 'display_stored_state',
            options: {page: "jabberclient_contact"}
          });
        });
    });

}(window, rJS));