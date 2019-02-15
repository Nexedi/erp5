/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS, RSVP) {
  "use strict";
//"https://softinst89769.host.vifib.net/erp5/portal_skins/erp5_http_proxy/ERP5Site_getHTTPResource?url="
  function setjIOLinshareConfiguration(gadget, options) {
    return new RSVP.Queue()
      .push(function () {
        return RSVP.all([
          gadget.getSetting("portal_type"),
          gadget.getSetting("erp5_attachment_synchro", true)
        ]);
      })
      .push(function (setting) {
        var configuration = {},
          attachment_synchro = setting[1] !== "",
          linshare_json = {
            type: "linshare",
            url: options.url
          };
        if (options.username || options.password) {
          linshare_json.access_token = window.btoa(
            options.username + ':' + options.password
          );
        }
        configuration = {
          type: "replicate",
          query: {
            query: 'portal_type:"' + setting[0] + '" ',
            limit: [0, 200],
            sort_on: [["modification_date", "descending"]]
          },
          use_remote_post: false,
          conflict_handling: 1,
          debug: true,
          check_local_attachment_modification: attachment_synchro,
          check_local_attachment_creation: attachment_synchro,
          check_remote_attachment_modification: attachment_synchro,
          check_remote_attachment_creation: attachment_synchro,
          check_remote_attachment_deletion: attachment_synchro,
          check_local_modification: true,
          check_local_creation: true,
          check_local_deletion: false,
          check_remote_modification: true,
          check_remote_creation: true,
          check_remote_deletion: true,
          signature_sub_storage: {
            type: "query",
            sub_storage: {
              type: "uuid",
              sub_storage: {
                type: "indexeddb",
                database: "ojs_linshare_hash"
              }
            }
          },
          local_sub_storage: {
            type: "query",
            schema: {"modification_date": {type: "string", format: "date-time"}},
            sub_storage: {
              type: "uuid",
              sub_storage: {
                type: "indexeddb",
                database: "ojs_linshare"
              }
            }
          },
          remote_sub_storage: {
            type: "saferepair",
            sub_storage: {
              type: "mapping",
              attachment_list: ["data"],
              attachment: {
                'data': {
                  get: {uri_template: 'enclosure'},
                  put: {uri_template: 'enclosure'}
                }
              },
              sub_storage: {
                type: "query",
                sub_storage: linshare_json
              }
            }
          }
        };
        return gadget.setSetting('jio_storage_description', configuration);
      })
      .push(function () {
        return gadget.setSetting('jio_storage_name', options.name);
      })
      .push(function () {
        return gadget.setSetting('sync_reload', true);
      })
      .push(function () {
        return gadget.setSetting('linshare_url', options.url);
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
    .declareMethod("render", function (options) {
      var gadget = this;
      if (options.url) {
        return gadget.changeState({
          url: options.url || "",
          username: options.username || ""
        });
      }
      return gadget.getSetting('linshare_storage', "")
        .push(function (url) {
          return gadget.changeState({
            url: url
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
          return setjIOLinshareConfiguration(gadget, content);
        });
    })

    .declareMethod("triggerSubmit", function () {
      return this.element.querySelector('button[type="submit"]').click();
    })

    .onStateChange(function () {
      var gadget = this;
      return gadget.getDeclaredGadget('form_view')
        .push(function (form_gadget) {
          return form_gadget.render({
            erp5_document: {"_embedded": {"_view": {
              "my_url": {
                "description": "",
                "title": "Connection Url",
                "default": gadget.state.url,
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "url",
                "hidden": 0,
                "type": "StringField"
              },
              "my_username": {
                "description": "",
                "title": "Username",
                "default": gadget.state.username || "",
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
                  [["my_url"], ["my_username"], ["my_password"]]
                ]]
              }
            });
        })
        .push(function () {
          return gadget.getUrlFor({
            command: 'display',
            options: {page: 'ojs_configurator'}
          });
        })
        .push(function (url) {
          return gadget.updateHeader({
            page_title: "Connect To Linshare",
            back_url: url,
            panel_action: false,
            submit_action: true
          });
        });
    });

}(window, rJS, RSVP));