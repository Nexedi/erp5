/*global window, rJS, RSVP, URI, location,
    loopEventListener, btoa */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS, RSVP) {
  "use strict";

  function setjIODAVConfiguration(gadget, options) {
    return gadget.getSetting("portal_type", "Web Page")
      .push(function (portal_type) {
        var configuration = {
          type: "replicate",
          // XXX This drop the signature lists...
          query: {
            query: 'portal_type:"' + portal_type + '" ',
            limit: [0, 100]
          },
          use_remote_post: false,
          conflict_handling: 2,
          check_local_modification: true,
          check_local_creation: true,
          check_local_deletion: true,
          check_remote_modification: true,
          check_remote_creation: true,
          check_remote_deletion: true,
          local_sub_storage: {
            type: "mapping",
            attachment: {
              'data': {
                get: {uri_template: 'enclosure'},
                put: {uri_template: 'enclosure'}
              }
            },
            sub_storage: {
              type: "query",
              sub_storage: {
                type: "uuid",
                sub_storage: {
                  type: "indexeddb",
                  database: "officejs-dav"
                }
              }
            }
          },
          remote_sub_storage: {
            type: "mapping",
            attachment: {
              'data': {
                get: {uri_template: 'enclosure'},
                put: {uri_template: 'enclosure'}
              }
            },
            sub_storage: {
              type: "query",
              sub_storage: {
                type: "drivetojiomapping",
                sub_storage: {
                  type: "mapping",
                  property: {
                    "portal_type": [
                      "switchPropertyValue",
                      {"PDF": "pdf", "Web Page": "txt"}
                    ]
                  },
                  sub_storage: {
                    type: "dav",
                    url: options.dav_url,
                    basic_login: btoa(options.username + ':' + options.password),
                    with_credentials: true
                  }
                }
              }
            }
          }
        };
        return gadget.setSetting('jio_storage_description', configuration);
      })
      .push(function () {
        return gadget.setSetting('jio_storage_name', "DAV");
      })
      .push(function () {
        return gadget.setGlobalSetting('dav_url', options.dav_url);
      })
      .push(function () {
        return gadget.setSetting('sync_reload', true);
      })
      .push(function () {
        return gadget.redirect({
          command: "display",
          options: {page: 'ojs_sync', auto_repair: 'true'}
        });
      });
  }

  rJS(window)

    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("reload", "reload")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("setSetting", "setSetting")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareMethod("getGlobalSetting", function (key) {
      var gadget = this;
      return gadget.getDeclaredGadget("global_setting_gadget")
        .push(function (global_setting_gadget) {
          return global_setting_gadget.getSetting(key);
        });
    })
    .declareMethod("setGlobalSetting", function (key, value) {
      var gadget = this;
      return gadget.getDeclaredGadget("global_setting_gadget")
        .push(function (global_setting_gadget) {
          return global_setting_gadget.setSetting(key, value);
        });
    })
    .declareMethod("render", function () {
      var gadget = this;
      return gadget.getUrlFor({command: 'display', options: {page: 'ojs_configurator'}})
        .push(function (url) {
          return gadget.updateHeader({
            page_title: "Connect To DAV Storage",
            back_url: url,
            panel_action: false,
            submit_action: true
          });
        });
    })

    /////////////////////////////////////////
    // Form submit
    /////////////////////////////////////////
    .onEvent('submit', function () {
      var gadget = this;
      return gadget.getDeclaredGadget('form_view')
        .push(function (form_gadget) {
          return form_gadget.getContent();
        })
        .push(function (content) {
          return setjIODAVConfiguration(gadget, content);
        });
    })

    .declareMethod("triggerSubmit", function () {
      return this.element.querySelector('button[type="submit"]').click();
    })

    .declareService(function () {
      var gadget = this;
      return gadget.declareGadget("gadget_officejs_setting.html", {
        "scope": "global_setting_gadget",
        "element": gadget.element.querySelector(".global_setting_gadget"),
        "sandbox": "iframe"
      })
        .push(function (global_setting_gadget) {
          return RSVP.all([
            global_setting_gadget.getSetting(
              "dav_url",
              "https://exemple.com"
            ),
            global_setting_gadget.getSetting(
              "username",
              ""
            )
          ]);
        })
        .push(function (options) {
          gadget.state.dav_url = options[0];
          gadget.state.username = options[1];
          return gadget.getDeclaredGadget('form_view');
        })
        .push(function (form_gadget) {
          return form_gadget.render({
            erp5_document: {"_embedded": {"_view": {
              "my_dav_url": {
                "description": "",
                "title": "Connection Url",
                "default": gadget.state.dav_url,
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "dav_url",
                "hidden": 0,
                "type": "StringField"
              },
              "my_username": {
                "description": "",
                "title": "Username",
                "default": gadget.state.username,
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "username",
                "hidden": 0,
                "type": "StringField"
              },
              "my_password": {
                "description": "",
                "title": "Password",
                "default": "",
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "password",
                "hidden": 0,
                "type": "PasswordField"
              }
            }},
              "_links": {
                "type": {
                  // form_list display portal_type in header
                  name: ""
                }
              }},
              form_definition: {
                group_list: [[
                  "top",
                  [["my_dav_url"], ["my_username"], ["my_password"]]
                ]]
              }
            });
        })
        .push(function () {
          return gadget.getDeclaredGadget('access');
        })
        .push(function (sub_gadget) {
          return sub_gadget.render("DAV");
        });
    });

}(window, rJS, RSVP));