/*global window, document, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

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
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")


    .declareMethod("render", function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return gadget.getSettingList(["migration_version", "app_configurator",  "proxy_server_url", "mcp_server_list", "mcp_oauth_token_map"]);
        })
        .push(function (setting_list) {
          var configurator = setting_list[1] || 'ojs_configurator';
          if (setting_list[0] !== currentVersion()) {
            return gadget.redirect({
              'command': 'display',
              'options': {
                'page': configurator,
                'auto_repair': true
              }
            });
          }
          return gadget.getUrlFor({command: "display"})
            .push(function (url) {
              return gadget.updateHeader({
                page_title: "External Service",
                back_url: url,
                panel_action: false,
                submit_action: true
              });
            })
            .push(function () {
              return gadget.changeState({
                'proxy_server_url': setting_list[2],
                'mcp_server_list': setting_list[3],
                'mcp_oauth_token_map': JSON.parse(setting_list[4] || '{}')
              });
            });
        });
    }, {mutex: 'render'})
    .onStateChange(function (modification_dict) {
      var gadget = this;
      return gadget.renderView();
    })
    .onEvent('submit', function () {
      var gadget = this,
        form_gadget;
      return gadget.notifySubmitting()
        .push(function () {
          return gadget.getDeclaredGadget('form_view');
        })
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
            proxy_server_url: content.server_url || "",
            mcp_server_list: content.mcp_server_list || ""
          })
            .push(function () {
              return gadget.notifySubmitted({message: "Saved", status: "success"});
            })
            .push(function () {
              return gadget.changeState({
                'proxy_server_url': content.server_url || '',
                'mcp_server_list': content.mcp_server_list || ""
              });
            });
        });
    })

    .declareMethod("triggerSubmit", function () {
      return this.element.querySelector('button[type="submit"]').click();
    }, {mutex: 'render'})
    .allowPublicAcquisition('notifySubmit', function notifySubmit() {
      return this.triggerSubmit();
    })

    .declareMethod('renderMcpConnectionList', function () {
      var gadget = this,
        container = gadget.element.querySelector('#mcp_connection_list');
      if (!container) {
        return;
      }
      return gadget.getSetting('mcp_server_list')
        .push(function (mcp_server_list) {
          var server_list = window.ChatMCP.parseServerListText(mcp_server_list || "").value || [];
          container.textContent = "";
          if (!server_list.length) {
            container.textContent = "No MCP servers configured yet - add one above and click Save.";
            return;
          }
          server_list.forEach(function (server_config) {
            var oauth_state = gadget.state.mcp_oauth_token_map[server_config.name],
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
        });
    })

    .declareJob('renderView', function () {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return window.ChatMCPOAuth.resumeIfPending();
        })
        .push(function (resumed) {
          if (!resumed) {
            return null;
          }
          gadget.state.mcp_oauth_token_map[resumed.server_name] = resumed.oauth_state;
          return gadget.setSetting('mcp_oauth_token_map', JSON.stringify(gadget.state.mcp_oauth_token_map))
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
              "my_server_url": {
                "description": "Optional. A local forwarder used to reach " +
                  "Base URL instead of calling it directly from the browser - avoids CORS/direct-" +
                  "access requirements and is needed for streaming to work across most providers. " +
                  "The forwarder's own origin must already be allowed by this app's Content-" +
                  "Security-Policy connect-src, same constraint Base URL (in Setting) is already " +
                  "subject to - otherwise the browser blocks the request. Leave empty to call Base " +
                  "URL directly.",
                "title": "Proxy Server URL",
                "default": gadget.state.proxy_server_url,
                "css_class": "",
                "required": 0,
                "editable": 1,
                "key": "server_url",
                "hidden": 0,
                "type": "StringField"
              },
              "my_mcp_server_list": {
                "description": "Optional. One MCP server URL per line (Streamable HTTP transport), " +
                  "e.g.:\nhttps://example.com/mcp\nhttps://other-example.com/mcp\n" +
                  "Each server is identified by its URL alone - no separate name to fill in. If a " +
                  "server needs sign-in, save this first, then use the Connect button that appears " +
                  "for it below. A self-hosted server's origin must already be allowed by this app's " +
                  "Content-Security-Policy connect-src, same constraint Base URL (in Setting) is " +
                  "already subject to - otherwise the browser blocks the request. Leave empty for none.",
                "title": "MCP Servers (one URL per line)",
                "default": gadget.state.mcp_server_list,
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
                [["my_server_url"], ["my_mcp_server_list"]]
              ]]
            }
          });
        })
        .push(function () {
          return gadget.renderMcpConnectionList();
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
      server_config = (window.ChatMCP.parseServerListText(gadget.state.mcp_server_list).value || [])
        .filter(function (s) { return s.name === server_name; })[0];
      if (!server_config) {
        return;
      }
      evt.target.disabled = true;
      return window.ChatMCPOAuth.connect(server_config)
        .push(undefined, function (error) {
          return gadget.notifySubmitted({
            message: "Could not connect to \"" + server_name + "\": " + (error && error.message ? error.message : error),
            status: "error"
          });
        })
        .push(function () {
          evt.target.disabled = false;
          return gadget.renderMcpConnectionList();
        });
    }, false, false);

}(window, rJS, RSVP));
