/*global window, rJS, RSVP, Handlebars, OPMLManage */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, Handlebars, OPMLManage) {
  "use strict";

  var gadget_klass = rJS(window),
    templater = gadget_klass.__template_element,
    notify_msg_template = Handlebars.compile(
      templater.getElementById("template-message-error").innerHTML
    ),
    opml_global = OPMLManage;

  gadget_klass
    /////////////////////////////
    // state
    /////////////////////////////
    .setState({
      message: "",
      redirect: false
    })
    /////////////////////////////
    // ready
    /////////////////////////////
    .ready(function (gadget) {
      return opml_global.init(gadget, notify_msg_template);
    })
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", 'notifySubmitted')

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .onEvent('submit', function () {
      var gadget = this,
        doc;
      return new RSVP.Queue()
        .push(function () {
          return  gadget.getDeclaredGadget('form_view');
        })
        .push(function (form_gadget) {
          return form_gadget.getContent();
        })
        .push(function (form_doc) {
          doc = form_doc;
          if (!opml_global.validateHttpUrl(form_doc.url)) {
            gadget.state.message
              .innerHTML = notify_msg_template({
                status: 'error',
                message: "'" + form_doc.url + "' is not a valid OPML URL"
              });
            return false;
          }
          if (!form_doc.username || !form_doc.password) {
            gadget.state.message
              .innerHTML = notify_msg_template({
                status: 'error',
                message: 'Username and password fields are required!'
              });
            return false;
          }
          if (doc.password !== gadget.state.password) {
            // password was modified, update on backend
            doc.new_password = doc.password;
            doc.password = gadget.state.password;
            doc.verify_password = 1;
          }
          return true;
        })
        .push(function (state) {
          if (state) {
            return gadget.notifySubmitting()
              .push(function () {
                doc.title = gadget.state.opml_title;
                return opml_global.saveOPML(doc,
                  doc.title === "" || doc.title === undefined || doc.verify_password === 1);
              })
              .push(function (status) {
                var msg = 'Document Updated';
                if (!status) {
                  msg = 'Document update failed';
                }
                return RSVP.all([
                  gadget.notifySubmitted(msg),
                  status
                ]);
              })
              .push(function (result_list) {
                if (result_list[1] && gadget.state.redirect) {
                  return gadget.redirect({
                    "command": "change",
                    "options": {"page": "ojsm_status_list"}
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
            "password": doc.password
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
                  ["my_active"], ["my_verify_password"],
                  ["my_new_password"]]
              ]]
            }
          });
        })
        .push(function () {
          return gadget.changeState({redirect: false})
            .push(function () {
              return RSVP.all([
                gadget.getUrlFor({command: 'history_previous'}),
                gadget.getUrlFor({command: 'selection_previous'}),
                gadget.getUrlFor({command: 'selection_next'}),
                gadget.getUrlFor({command: 'push_history', options: {
                  page: "ojsm_jump",
                  jio_key: gadget.state.opml_key,
                  title: gadget.state.opml_title,
                  jump_page: "ojsm_hosting_subscription_view",
                  view_title: "Related Hosting Subscription",
                  opml_key: gadget.state.opml_key
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
}(window, rJS, RSVP, Handlebars, OPMLManage));
