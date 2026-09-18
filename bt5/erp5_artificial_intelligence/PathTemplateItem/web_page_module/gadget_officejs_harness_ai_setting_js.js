/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  function currentVersion() {
    var version = window.location.href.replace(window.location.hash, ""),
      index = version.indexOf(window.location.host) + window.location.host.length;
    return version.substr(index);
  }

  // Same setSettingList payload as storage_list.local.setConfiguration in
  // gadget_officejs_page_jio_configurator_js.js - this app never goes through
  // that generic wizard (fixed app_configurator router setting pointing here
  // instead), so this page is responsible for setting up the same "Local is
  // Enough" jio storage itself, plus our own LLM settings, in one
  // setSettingList call.
  function setLLMConfiguration(gadget, content) {
    var jio_storage_description = {
      type: "query",
      sub_storage: {
        type: "uuid",
        sub_storage: {
          type: "indexeddb",
          database: "local_default"
        }
      }
    };
    return gadget.setSettingList({
      jio_storage_description: jio_storage_description,
      jio_storage_name: 'LOCAL',
      sync_reload: true,
      baseUrl: content.base_url || "",
      apiKey: content.api_key || "",
      model: content.model || "",
      migration_version: currentVersion()
    })
      .push(function () {
        return gadget.redirect({command: "display", options: {
          page: 'ojs_sync',
          auto_repair: 'true',
          redirect: JSON.stringify({
            command: 'display',
            options: {
              page: "ojs_harness_ai_homepage"
            }
          })
        }});
      });
  }

  rJS(window)
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("getSettingList", "getSettingList")
    .declareAcquiredMethod("setSettingList", "setSettingList")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("translate", "translate")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")

    .declareMethod("render", function () {
      var gadget = this;
      return gadget.getUrlFor({command: "display"})
        .push(function (url) {
          return gadget.updateHeader({
            page_title: "Setting",
            back_url: url,
            panel_action: false,
            submit_action: true
          });
        });
    }, {mutex: 'render'})

    /////////////////////////////////////////
    // Form submit
    /////////////////////////////////////////
    .onEvent('submit', function () {
      var gadget = this;
      return gadget.getDeclaredGadget('form_view')
        .push(function (form_gadget) {
          return form_gadget.checkValidity();
        })
        .push(function (is_valid) {
          if (!is_valid) {
            return gadget.translate("Please fill all required fields to submit")
              .push(function (message) {
                return gadget.notifySubmitted({
                  message: message,
                  status: "error"
                });
              })
              .push(function () {
                return null;
              });
          }
          return gadget.getDeclaredGadget('form_view')
            .push(function (form_gadget) {
              return form_gadget.getContent();
            });
        })
        .push(function (content) {
          if (content === null) {
            return;
          }
          return setLLMConfiguration(gadget, content);
        });
    })

    .declareMethod("triggerSubmit", function () {
      return this.element.querySelector('button[type="submit"]').click();
    }, {mutex: 'render'})

    .declareService(function () {
      var gadget = this;
      return gadget.getSettingList(["baseUrl", "apiKey", "model"])
        .push(function (setting_list) {
          gadget.state.baseUrl = setting_list[0] || "";
          gadget.state.apiKey = setting_list[1] || "";
          gadget.state.model = setting_list[2] || "";
          return gadget.getDeclaredGadget('form_view');
        })
        .push(function (form_gadget) {
          return form_gadget.render({
            erp5_document: {"_embedded": {"_view": {
              "my_base_url": {
                "description": "OpenAI-compatible endpoint, e.g. https://api.example.com/v1",
                "title": "Base URL",
                "default": gadget.state.baseUrl,
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "base_url",
                "hidden": 0,
                "type": "StringField"
              },
              "my_api_key": {
                "description": "Stored only in this browser, never sent to the server.",
                "title": "API Key",
                "default": gadget.state.apiKey,
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "api_key",
                "hidden": 0,
                "type": "PasswordField"
              },
              "my_model": {
                "description": "",
                "title": "Model",
                "default": gadget.state.model,
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "model",
                "hidden": 0,
                "type": "StringField"
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
                [["my_base_url"], ["my_api_key"], ["my_model"]]
              ]]
            }
          });
        });
    });

}(window, rJS, RSVP));
