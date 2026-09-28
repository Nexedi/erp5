/*global window, document, rJS, RSVP, fetch, Option */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  function renderMcpConnectionList(gadget) {
    var container = gadget.element.querySelector('#mcp_connection_list'),
      server_list = window.ChatMCP.parseServerListText(gadget.state.mcpServerList).value || [];
    if (!container) {
      return;
    }
    container.textContent = "";
    if (!server_list.length) {
      container.textContent = "No MCP servers configured yet - add one above and click Save.";
      return;
    }
    server_list.forEach(function (server_config) {
      var oauth_state = gadget.state.mcpOAuthTokenMap[server_config.name],
        row = document.createElement("div"),
        name_strong = document.createElement("strong"),
        status_span = document.createElement("span"),
        button = document.createElement("button"),
        status_text;
      if (!oauth_state) {
        status_text = "Not connected";
      } else if (window.ChatMCPOAuth.isExpired(oauth_state)) {
        status_text = "Connection expired";
      } else {
        status_text = "Connected";
      }
      row.className = "mcp-connection-row";
      name_strong.textContent = server_config.name;
      status_span.className = "mcp-connection-status";
      status_span.textContent = " - " + status_text + " ";
      button.type = "button";
      button.className = "mcp-connect-button ui-btn";
      button.setAttribute("data-server-name", server_config.name);
      button.textContent = oauth_state ? "Reconnect" : "Connect";
      row.appendChild(name_strong);
      row.appendChild(status_span);
      row.appendChild(button);
      container.appendChild(row);
    });
  }

  function currentVersion() {
    var version = window.location.href.replace(window.location.hash, ""),
      index = version.indexOf(window.location.host) + window.location.host.length;
    return version.substr(index);
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
          var validation;
          if (content === null) {
            return null;
          }
          validation = window.ChatMCP.parseServerListText(content.mcp_server_list);
          if (!validation.ok) {
            return gadget.notifySubmitted({ message: validation.error, status: "error" });
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
            mcpServerList: content.mcp_server_list || ""
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
    })

    .onEvent('change', function (evt) {
      var gadget = this;
      if (evt.target.id === "base_url" || evt.target.id === "api_key") {
        return gadget.updateModelListField();
      }
    }, false, false)

    .declareService(function () {
      var gadget = this;
      return gadget.getSettingList(["baseUrl", "apiKey", "model", "mcpServerList"])
        .push(function (setting_list) {
          gadget.state.baseUrl = setting_list[0] || "";
          gadget.state.apiKey = setting_list[1] || "";
          gadget.state.model = setting_list[2] || "";
          gadget.state.mcpServerList = setting_list[3] || "";
        })
        .push(function () {
          return gadget.getSetting('mcpOAuthTokenMap');
        })
        .push(function (mcp_oauth_token_map_json) {
          if (!mcp_oauth_token_map_json) {
            gadget.state.mcpOAuthTokenMap = {}
          } else {
            gadget.state.mcpOAuthTokenMap = JSON.parse(mcp_oauth_token_map_json);
          }
          return window.ChatMCPOAuth.resumeIfPending();
        })
        .push(function (resumed) {
          if (!resumed) {
            return null;
          }
          gadget.state.mcpOAuthTokenMap[resumed.server_name] = resumed.oauth_state;
          return gadget.setSetting('mcpOAuthTokenMap', JSON.stringify(gadget.state.mcpOAuthTokenMap))
            .push(function () {
              return gadget.notifySubmitted({
                message: "Connected to \"" + resumed.server_name + "\".",
                status: "success"
              });
            });
        }, function (error) {
          return gadget.notifySubmitted({
            message: "Could not connect: " + (error && error.message ? error.message : error),
            status: "error"
          });
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
              "my_mcp_server_list": {
                "description": "Optional. One MCP server URL per line (Streamable HTTP transport), " +
                  "e.g.:\nhttps://example.com/mcp\nhttps://other-example.com/mcp\n" +
                  "Each server is identified by its URL alone - no separate name to fill in. If a " +
                  "server needs sign-in, save this first, then use the Connect button that appears " +
                  "for it below. A self-hosted server's origin must already be allowed by this app's " +
                  "Content-Security-Policy connect-src, same constraint the Base URL above is already " +
                  "subject to - otherwise the browser blocks the request. Leave empty for none.",
                "title": "MCP Servers (one URL per line)",
                "default": gadget.state.mcpServerList,
                "css_class": "",
                "required": 0,
                "editable": 1,
                "key": "mcp_server_list",
                "hidden": 0,
                "type": "TextAreaField"
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
                [["my_base_url"], ["my_api_key"], ["my_model"], ["my_mcp_server_list"]]
              ]]
            }
          });
        })
        .push(function () {
          renderMcpConnectionList(gadget);
          if (gadget.state.baseUrl && gadget.state.apiKey) {
            return gadget.updateModelListField();
          }
        });
    })

    /////////////////////////////////////////
    // MCP server "Connect"/"Reconnect" buttons (plain hand-built DOM inside
    // #mcp_connection_list, not part of the generic form_view gadget)
    /////////////////////////////////////////
    .onEvent('click', function (evt) {
      var gadget = this,
        server_name,
        server_config;
      if (!evt.target.classList || !evt.target.classList.contains('mcp-connect-button')) {
        return;
      }
      server_name = evt.target.getAttribute('data-server-name');
      server_config = (window.ChatMCP.parseServerListText(gadget.state.mcpServerList).value || [])
        .filter(function (s) { return s.name === server_name; })[0];
      if (!server_config) {
        return;
      }
      evt.target.disabled = true;
      return window.ChatMCPOAuth.connect(server_config, gadget.state.mcpOAuthTokenMap[server_name])
        .push(undefined, function (error) {
          return gadget.notifySubmitted({
            message: "Could not connect to \"" + server_name + "\": " + (error && error.message ? error.message : error),
            status: "error"
          });
        })
        .push(function () {
          evt.target.disabled = false;
          renderMcpConnectionList(gadget);
        });
    }, false, false);

}(window, rJS, RSVP));
