/*global window, document, rJS, RSVP, fetch, Option */
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

  // Same defensive-degrade rule as window.ChatMCP.parseServerListText
  // elsewhere in this feature: a hand-edited/corrupted stored value degrades
  // to "no OAuth connections" rather than breaking the settings page.
  function parseMcpOAuthTokenMap(json_text) {
    var parsed;
    if (!json_text) {
      return {};
    }
    try {
      parsed = JSON.parse(json_text);
    } catch (ignore) {
      return {};
    }
    return (parsed && typeof parsed === "object" && !Array.isArray(parsed)) ? parsed : {};
  }

  // Renders one row per currently-saved MCP server (name + connection status
  // + a Connect/Reconnect button) into the static #mcp_connection_list
  // container in the page template - this is plain hand-built DOM, not part
  // of the generic form_view gadget, since that only renders declarative
  // field types and has no notion of a per-row action button.
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

  // Same setSettingList payload as storage_list.local.setConfiguration in
  // gadget_officejs_page_jio_configurator_js.js - this app never goes through
  // that generic wizard (fixed app_configurator router setting pointing here
  // instead), so this page is responsible for setting up the same "Local is
  // Enough" jio storage itself, plus our own LLM settings, in one
  // setSettingList call.
  //
  // base_url/api_key/model/mcp_server_list themselves are stored on an
  // Artificial Agent jio document (not directly as flat settings keys) -
  // only its id travels through settings. Creating/updating that document
  // requires the app's own jio storage (jio_storage_description above) to
  // already be live, which only happens on the *next* full page load (see
  // rjs_gadget_erp5_launcher_js.js's .ready(), which calls createJio once
  // per load using whatever jio_storage_description was saved before this
  // load started) - so on someone's very first ever save there is no
  // Artificial Agent document yet to write to. In that one case, fall back
  // to storing the raw fields directly as a transient bridge; .declareService
  // below finishes the migration to an Artificial Agent id the next time
  // this page loads, once the jio storage from this save is actually live.
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
      },
      agent_data = {
        portal_type: 'Artificial Agent',
        base_url: content.base_url || "",
        api_key: content.api_key || "",
        model: content.model || "",
        mcp_server_list: content.mcp_server_list || ""
      };
    return new RSVP.Queue()
      .push(function () {
        if (gadget.state.agentId) {
          return gadget.jio_put(gadget.state.agentId, agent_data)
            .push(function () {
              return gadget.state.agentId;
            });
        }
        return gadget.jio_post(agent_data);
      })
      .push(function (agent_id) {
        return gadget.setSettingList({
          jio_storage_description: jio_storage_description,
          jio_storage_name: 'LOCAL',
          sync_reload: true,
          agentId: agent_id,
          baseUrl: "",
          apiKey: "",
          model: "",
          mcpServerList: "",
          migration_version: currentVersion()
        });
      }, function () {
        // jio storage not bootstrapped yet (very first ever save) - keep
        // the raw fields as a transient bridge, see comment above.
        return gadget.setSettingList({
          jio_storage_description: jio_storage_description,
          jio_storage_name: 'LOCAL',
          sync_reload: true,
          baseUrl: content.base_url || "",
          apiKey: content.api_key || "",
          model: content.model || "",
          mcpServerList: content.mcp_server_list || "",
          migration_version: currentVersion()
        });
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
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_post", "jio_post")
    .declareAcquiredMethod("jio_put", "jio_put")
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
          var validation;
          if (content === null) {
            return null;
          }
          validation = window.ChatMCP.parseServerListText(content.mcp_server_list);
          if (!validation.ok) {
            return gadget.notifySubmitted({ message: validation.error, status: "error" })
              .push(function () { return null; });
          }
          return setLLMConfiguration(gadget, content)
            .push(function (save_result) {
              gadget.state.mcpServerList = content.mcp_server_list || "";
              renderMcpConnectionList(gadget);
              if (!validation.value.length) {
                return save_result;
              }
              // Purely informational: probing MCP servers never blocks or
              // reverts the save that already happened above - a server can
              // be legitimately unreachable right now (VPN not connected
              // yet, still starting up, ...) without that being a config error.
              return new RSVP.Queue(RSVP.all(validation.value.map(function (server_config) {
                return window.ChatMCP.probeServer(server_config);
              })))
                .push(function (probe_result_list) {
                  var failed_list = probe_result_list
                    .map(function (probe, i) { return { name: validation.value[i].name, probe: probe }; })
                    .filter(function (x) { return !x.probe.ok; });
                  if (failed_list.length) {
                    return gadget.notifySubmitted({
                      message: "Saved, but could not reach: " +
                        failed_list.map(function (x) { return x.name + " (" + x.probe.error + ")"; }).join(", "),
                      status: "error"
                    });
                  }
                })
                .push(undefined, function () { return null; })
                .push(function () { return save_result; });
            });
        });
    })

    .declareMethod("triggerSubmit", function () {
      return this.element.querySelector('button[type="submit"]').click();
    }, {mutex: 'render'})
    .allowPublicAcquisition('notifySubmit', function notifySubmit() {
      return this.triggerSubmit();
    })

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
      return gadget.getSettingList(["agentId", "baseUrl", "apiKey", "model", "mcpServerList", "mcpOAuthTokenMap"])
        .push(function (setting_list) {
          gadget.state.agentId = setting_list[0] || "";
          gadget.state.mcpOAuthTokenMap = parseMcpOAuthTokenMap(setting_list[5]);

          if (gadget.state.agentId) {
            return gadget.jio_get(gadget.state.agentId)
              .push(function (doc) {
                gadget.state.baseUrl = doc.base_url || "";
                gadget.state.apiKey = doc.api_key || "";
                gadget.state.model = doc.model || "";
                gadget.state.mcpServerList = doc.mcp_server_list || "";
              }, function (error) {
                if (error.status_code !== 404) {
                  throw error;
                }
                gadget.state.baseUrl = "";
                gadget.state.apiKey = "";
                gadget.state.model = "";
                gadget.state.mcpServerList = "";
              });
          }

          // Not migrated to an Artificial Agent document yet - use the raw
          // bridge fields (see setLLMConfiguration), and opportunistically
          // finish the migration now that this is a fresh page load, so the
          // jio storage bootstrapped by rjs_gadget_erp5_launcher_js.js's
          // .ready() is actually live.
          gadget.state.baseUrl = setting_list[1] || "";
          gadget.state.apiKey = setting_list[2] || "";
          gadget.state.model = setting_list[3] || "";
          gadget.state.mcpServerList = setting_list[4] || "";
          if (!gadget.state.baseUrl && !gadget.state.apiKey &&
              !gadget.state.model && !gadget.state.mcpServerList) {
            return;
          }
          return gadget.jio_post({
            portal_type: 'Artificial Agent',
            base_url: gadget.state.baseUrl,
            api_key: gadget.state.apiKey,
            model: gadget.state.model,
            mcp_server_list: gadget.state.mcpServerList
          })
            .push(function (agent_id) {
              gadget.state.agentId = agent_id;
              return gadget.setSettingList({
                agentId: agent_id,
                baseUrl: "",
                apiKey: "",
                model: "",
                mcpServerList: ""
              });
            }, function () {
              // Storage still not ready - keep using the raw fields, retry
              // migration on the next page load.
              return null;
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
            return gadget.deferUpdateModelListField();
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
        .push(function (oauth_state) {
          gadget.state.mcpOAuthTokenMap[server_name] = oauth_state;
          return gadget.setSettingList({ mcpOAuthTokenMap: JSON.stringify(gadget.state.mcpOAuthTokenMap) });
        })
        .push(function () {
          return gadget.notifySubmitted({ message: "Connected to \"" + server_name + "\".", status: "success" });
        })
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
