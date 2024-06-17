/*global window, rJS, RSVP, Handlebars */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, Rusha) {
  "use strict";

  var rusha = new Rusha();

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", 'notifySubmitted')

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .onEvent('submit', function () {
      var gadget = this,
        doc,
        opml_gadget;
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
          if (doc.password !== gadget.state.password) {
            // password was modified, update on backend
            doc.new_password = doc.password;
            doc.confirm_new_password = doc.new_password;
            doc.password = gadget.state.password;
            doc.verify_password = 1;
          } else {
            doc.verify_password = (doc.verify_password === "on") ? 1 : 0;
          }
          return opml_gadget.checkOPMLForm(doc);
        })
        .push(function (state) {
          if (state) {
            return gadget.notifySubmitting()
              .push(function () {
                var verify_opml = doc.title === "" || doc.title === undefined ||
                    doc.verify_password === 1;
                if (gadget.state.active === false && doc.active === "on") {
                  verify_opml = true;
                }
                doc.title = gadget.state.opml_title;
                return opml_gadget.saveOPML(doc, verify_opml);
              })
              .push(function (state) {
                var msg = {message: 'Document Updated', status: 'success'};
                if (!state.status) {
                  msg = {message: 'Document update failed', status: "error"};
                }
                return RSVP.all([
                  gadget.notifySubmitted(msg),
                  state
                ]);
              })
              .push(function (result) {
                if (result[1].status) {
                  return gadget.changeState({
                    "password": doc.password
                  });
                }
              });
          }
        });
    })

    .declareMethod("triggerSubmit", function () {
      return this.element.querySelector('button[type="submit"]').click();
    })

    .declareMethod("render", function (options) {
      var gadget = this,
        doc = options.doc;
      return RSVP.Queue()
        .push(function () {
          return gadget.changeState({
            "opml_title": doc.title || "",
            "opml_key": options.jio_key,
            "password": doc.password,
            "active": doc.active
          });
        })
        .push(function () {
          return RSVP.all([
            gadget.getDeclaredGadget('form_view')
          ]);
        })
        .push(function (result) {
          return result[0].render({
            erp5_document: {
              "_embedded": {"_view": {
                "my_title": {
                  "description": "The name of OPML",
                  "title": "Title",
                  "default": doc.title || "",
                  "css_class": "",
                  "required": 0,
                  "editable": 0,
                  "key": "title",
                  "hidden": doc.title === undefined ? 1 : 0,
                  "type": "StringField"
                },
                "my_url": {
                  "description": "",
                  "title": "OPML URL",
                  "default": doc.url || options.url || "",
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
                  "default": doc.username || "",
                  "css_class": "",
                  "required": 1,
                  "editable": 0,
                  "key": "username",
                  "hidden": 0,
                  "type": "StringField"
                },
                "my_password": {
                  "description": "Password for access private URLs",
                  "title": "Password",
                  "default": doc.password || "",
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "password",
                  "hidden": 0,
                  "type": "PasswordField"
                },
                "my_requested_state": {
                  "description": "Instance tree state",
                  "title": "Requested State",
                  "default": doc.state || (doc.active ? "Started" : "Stopped"),
                  "css_class": "",
                  "required": 1,
                  "editable": 0,
                  "key": "state",
                  "hidden": 0,
                  "type": "StringField"
                },
                "my_active": {
                  "description": "Sync this opml or not",
                  "title": "Active (Enable Sync)",
                  "default": doc.active || doc.active === undefined ? 1 : 0,
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
                  "hidden": 1,
                  "type": "PasswordField"
                },
                "my_verify_password": {
                  "description": "Check if this OPML is valid, and also verify that password match",
                  "title": "Verify OPML & Password",
                  "default": 0,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "verify_password",
                  "hidden": 0,
                  "type": "CheckBoxField"
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
                [["my_title"], ["my_url"], ["my_username"], ["my_password"],
                  ["my_requested_state"], ["my_active"], ["my_verify_password"],
                  ["my_new_password"]]
              ]]
            }
          });
        })
        .push(function () {
          return new RSVP.Queue()
            .push(function () {
              var hosting_key = rusha.digestFromString(gadget.state.opml_key);
              return RSVP.all([
                gadget.getUrlFor({command: 'history_previous'}),
                gadget.getUrlFor({command: 'selection_previous'}),
                gadget.getUrlFor({command: 'selection_next'}),
                gadget.getUrlFor({command: 'push_history', options: {
                  page: "ojsm_jump",
                  jio_key: hosting_key,
                  title: gadget.state.opml_title,
                  view_title: "Related Instance Tree"
                }}),
                gadget.getUrlFor({command: 'change', options: {
                  page: 'ojsm_opml_delete',
                  jio_key: gadget.state.opml_key,
                  return_url: 'settings_configurator'
                }})
              ]);
            })
            .push(function (url_list) {
              return gadget.updateHeader({
                page_title: options.doc.title || "OPML View",
                selection_url: url_list[0],
                previous_url: url_list[1],
                next_url: url_list[2],
                jump_url: url_list[3],
                delete_url: url_list[4],
                save_action: true
              });
            });
        });
    });
}(window, rJS, RSVP, Rusha));
