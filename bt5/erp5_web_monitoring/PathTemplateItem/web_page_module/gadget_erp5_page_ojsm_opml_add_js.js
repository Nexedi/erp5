/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  rJS(window)

    .setState({auto_sync: true, check_pwd: true})
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", 'notifySubmitted')

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .onEvent('click', function (event) {
      var gadget = this;

      if (event.target.id === "saveOPMLNoPwd") {
        return gadget.changeState({check_pwd: false})
          .push(function () {
            return gadget.element.querySelector('button[type="submit"]').click();
          });
      }
    }, false, false)
    .onEvent('submit', function () {
      var gadget = this,
        opml_gadget,
        doc;
      return new RSVP.Queue()
        .push(function () {
          return gadget.getDeclaredGadget('opml_gadget');
        })
        .push(function (g) {
          opml_gadget = g;
          return gadget.getDeclaredGadget('form_view');
        })
        .push(function (form_gadget) {
          return form_gadget.getContent();
        })
        .push(function (form_doc) {
          doc = form_doc;
          return opml_gadget.checkOPMLForm(doc);
        })
        .push(function (state) {
          if (state) {
            return gadget.notifySubmitting()
              .push(function () {
                doc.title = "";
                return opml_gadget.saveOPML(doc, gadget.state.check_pwd);
              })
              .push(function (state) {
                var msg = {message: 'OPML document added', status: 'success'};
                if (!state) {
                  msg = {message: 'Failed to add OPML document', status: "error"};
                }
                return RSVP.all([
                  gadget.notifySubmitted(msg),
                  state
                ]);
              })
              .push(function (result_list) {
                if (result_list[1].status) {
                  var redirect_options = {
                    "command": "display",
                    "options": {page: "ojs_local_controller",
                                portal_type: "Promise Module"}
                  };
                  if (gadget.state.auto_sync) {
                    return gadget.getDeclaredGadget('sync_gadget')
                      .push(function (sync_gadget) {
                        // start synchronization now
                        return sync_gadget.register({now: true});
                      })
                      .push(function () {
                        return gadget.redirect(redirect_options);
                      });
                  }
                  return gadget.redirect(redirect_options);
                }
                if (result_list[1].can_force) {
                  gadget.element.getElementsByClassName("btn-nopasswd")[0]
                    .style.display = "";
                }
              });
          }
        });
    })

    .declareMethod("triggerSubmit", function () {
      return this.element.querySelector('button[type="submit"]').click();
    })

    .declareMethod("render", function (options) {
      var gadget = this, auto_sync = !options.intra;
      return RSVP.Queue()
        .push(function () {
          var button_no_pwd = gadget.element.getElementsByClassName("btn-nopasswd");

          button_no_pwd[0].style.display = "none";
          return RSVP.all([
            gadget.getDeclaredGadget('form_view'),
            gadget.getSetting('portal_type')
          ]);
        })
        .push(function (result) {
          return result[0].render({
            erp5_document: {
              "_embedded": {"_view": {
                "my_url": {
                  "description": "",
                  "title": "OPML URL",
                  "default": options.url || "",
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "url",
                  "hidden": 0,
                  "type": "StringField"
                },
                "my_username": {
                  "description": "Username for access private URLs",
                  "title": "Username",
                  "default": options.username || "",
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "username",
                  "hidden": 0,
                  "type": "StringField"
                },
                "my_password": {
                  "description": "Password for access private URLs",
                  "title": "Password",
                  "default": options.password || "",
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "password",
                  "hidden": 0,
                  "type": "PasswordField"
                },
                "my_slapos_master_url": {
                  "description": "Slapos master URL",
                  "title": "Slapos master URL",
                  "default": options.slapos_master_url || "not-provided",
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "slapos_master_url",
                  "hidden": 0,
                  "type": "StringField"
                },
                "my_portal_type": {
                  "description": "The name of a document in ERP5",
                  "title": "Portal Type",
                  "default": result[1],
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "portal_type",
                  "hidden": 1,
                  "type": "StringField"
                },
                "my_active": {
                  "description": "Sync this opml or not",
                  "title": "Active (Enable Sync)",
                  "default": 1,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "active",
                  "hidden": 0,
                  "type": "CheckBoxField"
                },
                "my_new_password": {
                  "description": "Change current OPML password",
                  "title": "New Password",
                  "default": "",
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "new_password",
                  "hidden": (options.chg_passwd || '' === true) ? 0 : 1,
                  "type": "PasswordField"
                },
                "my_confirm_new_password": {
                  "description": "Confirm new OPML password",
                  "title": "Confirm New Password",
                  "default": "",
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "confirm_new_password",
                  "hidden": (options.chg_passwd || '' === true) ? 0 : 1,
                  "type": "PasswordField"
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
                [["my_url"], ["my_username"], ["my_password"],
                  ["my_slapos_master_url"], ["my_portal_type"], ["my_active"],
                  ["my_new_password"], ["my_confirm_new_password"]]
              ]]
            }
          });
        })
        .push(function () {
          return gadget.getSetting("opml_add_auto_sync", "on");
        })
        .push(function (auto_sync) {
          return gadget.changeState({auto_sync: auto_sync === "on"});
        })
        .push(function () {
          var new_options;

          if (options.chg_passwd === 'true') {
            return undefined;
          }
          new_options = JSON.parse(JSON.stringify(options));
          new_options.chg_passwd = 'true';
          return gadget.getUrlFor({command: "change", options: new_options});
        })
        .push(function (chg_pwd_url) {
          return gadget.updateHeader({
            page_title: "Add OPML",
            save_action: true,
            change_password: chg_pwd_url
          });
        })
        .push(function () {
          return gadget.checkSynchronize(auto_sync);
        });
    })
    .declareJob("checkSynchronize", function (auto_sync) {
      if (auto_sync) {
        return this.element.querySelector('button[type="submit"]').click();
      }
    });
}(window, rJS, RSVP));
