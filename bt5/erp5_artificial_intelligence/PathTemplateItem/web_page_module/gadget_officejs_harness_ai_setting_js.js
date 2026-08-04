/*global window, rJS, RSVP, fetch, Option */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  function currentVersion() {
    var version = window.location.href.replace(window.location.hash, ""),
      index = version.indexOf(window.location.host) + window.location.host.length;
    return version.substr(index);
  }

  // JSON with every non-ASCII code point escaped, so it stays valid in an
  // HTTP header - same helper as gadget_officejs_harness_ai_artificial_task_view_js.js's
  // asciiJSON, duplicated here since this file has no dependency on that one.
  function asciiJSON(value) {
    var escape_non_ascii = /[\u0080-\uffff]/g;
    return JSON.stringify(value).replace(escape_non_ascii, function (c) {
      var code = c.charCodeAt(0).toString(16);
      while (code.length < 4) {
        code = "0" + code;
      }
      return "\\u" + code;
    });
  }

  rJS(window)
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("getSettingList", "getSettingList")
    .declareAcquiredMethod("setSetting", "setSetting")
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
      var gadget = this,
        form_gadget;
      return gadget.getDeclaredGadget('form_view')
        .push(function (result) {
          form_gadget = result;
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
          return form_gadget.getContent();
        })
        .push(function (content) {
          if (content === null) {
            return null;
          }
          return gadget.setSettingList({
            jio_storage_description: {
              type: "query",
              sub_storage: {
                type: "uuid",
                sub_storage: {
                  type: "indexeddb",
                  database: "local_default"
                }
              }
            },
            jio_storage_name: 'LOCAL',
            sync_reload: true,
            migration_version: currentVersion(),
            baseUrl: content.base_url || "",
            apiKey: content.api_key || "",
            model: content.model || "",
            endpoint: content.endpoint || "chat/completions"
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
        });
    })

    .declareMethod("triggerSubmit", function () {
      return this.element.querySelector('button[type="submit"]').click();
    }, {mutex: 'render'})
    .allowPublicAcquisition('notifySubmit', function notifySubmit() {
      return this.triggerSubmit();
    })

    .declareMethod('updateModelListField', function () {
      var gadget = this,
        select = gadget.element.querySelector('#model'),
        base_url_field = gadget.element.querySelector('#base_url'),
        api_key_field = gadget.element.querySelector('#api_key'),
        base_url = base_url_field ? base_url_field.value : "",
        api_key = api_key_field ? api_key_field.value : "",
        current_value,
        i;

      if (!select || !base_url || !api_key) {
        return;
      }

      current_value = select.value;
      for (i = select.options.length - 1; i >= 0; i -= 1) {
        select.remove(i);
      }

      return new RSVP.Queue()
        .push(function () {
          var target = base_url.replace(/\/+$/, "") + "/models";
          if (gadget.state.proxy_server_url) {
            return fetch(gadget.state.proxy_server_url.replace(/\/+$/, "") + "/proxy", {
              method: "POST",
              headers: {
                "Content-Type": "application/octet-stream",
                "X-Target-URL": encodeURI(target),
                "X-Target-Method": "GET",
                "X-Target-Headers": asciiJSON({Authorization: "Bearer " + api_key})
              }
            });
          }
          return fetch(target, {
            headers: {Authorization: "Bearer " + api_key}
          });
        })
        .push(function (response) {
          if (!response.ok) {
            throw new Error("Failed to fetch model list: " + response.status);
          }
          return response.json();
        })
        .push(function (json) {
          var model_list = (json && json.data) || [],
            found = false;

          for (i = 0; i < model_list.length; i += 1) {
            select.options[i] = new Option(model_list[i].id, model_list[i].id);
            if (model_list[i].id === current_value) {
              found = true;
            }
          }
          if (current_value) {
            select.value = current_value;
          }
        })
        .push(undefined, function () {
          if (current_value) {
            select.options[0] = new Option(current_value, current_value);
            select.value = current_value;
          }
        });
    })

    .onEvent('change', function (evt) {
      var gadget = this;
      if (evt.target.id === "base_url" || evt.target.id === "api_key") {
        return gadget.updateModelListField();
      }
    }, false, false)

    .declareService(function () {
      var gadget = this;
      return gadget.getSettingList(["baseUrl", "apiKey", "model", "proxy_server_url", "endpoint"])
        .push(function (setting_list) {
          gadget.state.baseUrl = setting_list[0] || "";
          gadget.state.apiKey = setting_list[1] || "";
          gadget.state.model = setting_list[2] || "";
          gadget.state.proxy_server_url = setting_list[3] || "";
          gadget.state.endpoint = setting_list[4] || "chat/completions";
        })
        .push(function () {
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
                "description": "Populated automatically once Base URL and API Key are filled in.",
                "title": "Model",
                "default": gadget.state.model,
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "model",
                "hidden": 0,
                "type": "ListField",
                "items": gadget.state.model ? [[gadget.state.model, gadget.state.model]] : []
              },
              "my_endpoint": {
                "description": "Path appended to Base URL to reach the chat-completions call, e.g. " +
                  "\"chat/completions\" against a Base URL of https://api.example.com/v1 calls " +
                  "https://api.example.com/v1/chat/completions. Change this if a provider uses a " +
                  "different path for the same OpenAI-compatible wire format.",
                "title": "Endpoint",
                "default": gadget.state.endpoint,
                "css_class": "",
                "required": 0,
                "editable": 1,
                "key": "endpoint",
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
                [["my_base_url"], ["my_api_key"], ["my_model"], ["my_endpoint"]]
              ]]
            }
          });
        })
        .push(function () {
          if (gadget.state.baseUrl && gadget.state.apiKey) {
            return gadget.updateModelListField();
          }
        });
    });

}(window, rJS, RSVP));
