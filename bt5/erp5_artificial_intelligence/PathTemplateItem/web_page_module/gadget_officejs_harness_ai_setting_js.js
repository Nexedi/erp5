/*global window, rJS, RSVP, fetch, Option */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  // Fetch the list of models the configured OpenAI-compatible endpoint
  // currently serves (GET <base_url>/models with the api key as a Bearer
  // token, same convention as e.g. https://api.openai.com/v1/models) and
  // replace the model <select>'s options with it directly in the DOM -
  // same idiom as gadget_supportrequest_fast_view_dialog_js.js's
  // updateResourceListField, since this generic form gadget has no
  // programmatic "update item list" method of its own.
  function updateModelListField(gadget) {
    var select = gadget.element.querySelector('#model'),
      base_url_field = gadget.element.querySelector('#base_url'),
      api_key_field = gadget.element.querySelector('#api_key'),
      base_url = base_url_field ? base_url_field.value : "",
      api_key = api_key_field ? api_key_field.value : "";

    if (!select || !base_url || !api_key) {
      return RSVP.resolve();
    }

    return new RSVP.Queue()
      .push(function () {
        return fetch(base_url.replace(/\/+$/, "") + "/models", {
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
          current_value = select.value,
          found = false,
          i;

        for (i = select.options.length - 1; i >= 0; i -= 1) {
          select.remove(i);
        }
        for (i = 0; i < model_list.length; i += 1) {
          select.options[i] = new Option(model_list[i].id, model_list[i].id);
          if (model_list[i].id === current_value) {
            found = true;
          }
        }
        if (current_value && !found) {
          // Keep whatever model was previously saved as an extra option
          // even if this provider does not list it, rather than silently
          // dropping it.
          select.options[select.options.length] = new Option(current_value, current_value);
        }
        if (current_value) {
          select.value = current_value;
        }
      })
      .push(undefined, function () {
        // Bad URL, bad key, CORS, offline, ... - leave the model select
        // as-is (e.g. still showing the previously saved value) rather
        // than blocking the rest of the settings form on this.
        return null;
      });
  }

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

    /////////////////////////////////////////
    // Populate the Model select once Base URL and API Key look filled in
    /////////////////////////////////////////
    .declareJob('deferUpdateModelListField', function () {
      return updateModelListField(this);
    })

    .onEvent('change', function (evt) {
      var gadget = this;
      if (evt.target.id === "base_url" || evt.target.id === "api_key") {
        gadget.deferUpdateModelListField();
      }
    }, false, false)

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
        })
        .push(function () {
          if (gadget.state.baseUrl && gadget.state.apiKey) {
            return gadget.deferUpdateModelListField();
          }
        });
    });

}(window, rJS, RSVP));
