/*global window, fetch, RSVP, TextDecoder */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, RSVP) {
  "use strict";

  var MCP_PROTOCOL_VERSION = "2025-06-18",
    MAX_TOOL_NAME_LEN = 64,
    NAME_SAFE_RE = /[^a-zA-Z0-9_-]/g,
    json_rpc_id_counter = 0;

  function sanitizeNamePart(value) {
    return String(value).replace(NAME_SAFE_RE, "_");
  }

  // Builds a collision-free, OpenAI-function-name-safe public tool name, e.g.
  // "mcp__erp5__erp5_search". used_name_set is scoped to one server's own
  // tool list (collisions ACROSS servers can't happen: the server name is
  // baked into the prefix), so it only has to dedupe a single misbehaving
  // server that reports the same tool name twice.
  function uniqueNamespacedName(server_name, tool_name, used_name_set) {
    var base = ("mcp__" + sanitizeNamePart(server_name) + "__" + sanitizeNamePart(tool_name)).slice(0, MAX_TOOL_NAME_LEN),
      candidate = base,
      suffix = 2;
    while (used_name_set.hasOwnProperty(candidate)) {
      candidate = base.slice(0, MAX_TOOL_NAME_LEN - String(suffix).length - 1) + "_" + suffix;
      suffix += 1;
    }
    used_name_set[candidate] = true;
    return candidate;
  }

  function nextId() {
    json_rpc_id_counter += 1;
    return json_rpc_id_counter;
  }

  function requestHeaders(server_config, session) {
    var headers = {
      "Content-Type": "application/json",
      "Accept": "application/json, text/event-stream"
    };
    if (session && session.protocol_version) {
      headers["MCP-Protocol-Version"] = session.protocol_version;
    }
    if (session && session.session_id) {
      headers["Mcp-Session-Id"] = session.session_id;
    }
    if (server_config.token) {
      headers.Authorization = "Bearer " + server_config.token;
    }
    return headers;
  }

  function unwrapJsonRpcMessage(message) {
    if (message && message.error) {
      throw new Error("MCP error " + message.error.code + ": " + message.error.message);
    }
    return message ? message.result : undefined;
  }

  // Manual Server-Sent-Events framing over a POST response body - EventSource
  // cannot be used here since it can only issue GET requests, never POST.
  // Reads chunks until it finds the "data:" record whose JSON-RPC "id"
  // matches this request, then cancels the stream (does not wait for it to
  // close) rather than draining it fully.
  function readSseForJsonRpcResponse(response, expected_id) {
    var reader = response.body.getReader(),
      decoder = new TextDecoder("utf-8"),
      buffer = "";

    function processBuffer() {
      var records = buffer.split("\n\n"), i, record, data_line_list, data_text, message;
      buffer = records.pop();
      for (i = 0; i < records.length; i += 1) {
        record = records[i];
        data_line_list = record.split("\n").filter(function (line) { return line.indexOf("data:") === 0; });
        if (!data_line_list.length) {
          continue;
        }
        data_text = data_line_list.map(function (line) {
          return line.slice(5).replace(/^ /, "");
        }).join("\n");
        try {
          message = JSON.parse(data_text);
        } catch (ignore) {
          continue;
        }
        if (message && message.id === expected_id) {
          return message;
        }
      }
      return null;
    }

    function pump() {
      return new RSVP.Queue(reader.read())
        .push(function (chunk) {
          var found;
          if (chunk.value) {
            buffer += decoder.decode(chunk.value, { stream: !chunk.done });
          }
          found = processBuffer();
          if (found) {
            reader.cancel();
            return unwrapJsonRpcMessage(found);
          }
          if (chunk.done) {
            throw new Error("MCP: SSE stream ended without a response for request id " + expected_id);
          }
          return pump();
        });
    }

    return pump();
  }

  function parseRpcResponse(response, expected_id) {
    var content_type = response.headers.get("Content-Type") || "";
    if (!response.ok) {
      return new RSVP.Queue(response.text())
        .push(function (text) {
          throw new Error("HTTP " + response.status + (text ? ": " + text.slice(0, 300) : ""));
        });
    }
    if (content_type.indexOf("text/event-stream") !== -1) {
      return readSseForJsonRpcResponse(response, expected_id);
    }
    return new RSVP.Queue(response.json())
      .push(function (message) {
        return unwrapJsonRpcMessage(message);
      });
  }

  // Low-level POST of one JSON-RPC request. Resolves {result, response} (the
  // raw response is kept so initializeSession can read the Mcp-Session-Id
  // response header - that information does not exist anywhere in the
  // JSON-RPC payload itself).
  function rpcCallRaw(server_config, method, params, session) {
    var id = nextId();
    return new RSVP.Queue(fetch(server_config.url, {
      method: "POST",
      headers: requestHeaders(server_config, session),
      body: JSON.stringify({ jsonrpc: "2.0", id: id, method: method, params: params || {} })
    }))
      .push(function (response) {
        return parseRpcResponse(response, id)
          .push(function (result) {
            return { result: result, response: response };
          });
      });
  }

  function rpcCall(server_config, method, params, session) {
    return rpcCallRaw(server_config, method, params, session)
      .push(function (envelope) {
        return envelope.result;
      });
  }

  // notifications/initialized has no "id" (it is a JSON-RPC notification, not
  // a request) - the server is expected to answer 202 Accepted with an empty
  // body, never a JSON-RPC response to parse.
  function rpcNotify(server_config, method, params, session) {
    return new RSVP.Queue(fetch(server_config.url, {
      method: "POST",
      headers: requestHeaders(server_config, session),
      body: JSON.stringify({ jsonrpc: "2.0", method: method, params: params || {} })
    }))
      .push(function (response) {
        if (!response.ok && response.status !== 202) {
          throw new Error("MCP notify \"" + method + "\" failed: HTTP " + response.status);
        }
      });
  }

  function initializeSession(server_config) {
    var session = { session_id: null, protocol_version: MCP_PROTOCOL_VERSION };
    return rpcCallRaw(server_config, "initialize", {
      protocolVersion: MCP_PROTOCOL_VERSION,
      capabilities: {},
      clientInfo: { name: "erp5-officejs-harness-agent", version: "1.0" }
    }, null)
      .push(function (envelope) {
        session.session_id = envelope.response.headers.get("Mcp-Session-Id") || null;
        if (envelope.result && envelope.result.protocolVersion) {
          session.protocol_version = envelope.result.protocolVersion;
        }
        return rpcNotify(server_config, "notifications/initialized", {}, session);
      })
      .push(function () {
        return session;
      });
  }

  function listAllTools(server_config, session, cursor, accumulated) {
    accumulated = accumulated || [];
    return rpcCall(server_config, "tools/list", cursor ? { cursor: cursor } : {}, session)
      .push(function (result) {
        var tool_list = accumulated.concat((result && result.tools) || []);
        if (result && result.nextCursor) {
          return listAllTools(server_config, session, result.nextCursor, tool_list);
        }
        return tool_list;
      });
  }

  function isSessionLostError(error) {
    return Boolean(error && /HTTP 404/.test(error.message));
  }

  function isAuthExpiredError(error) {
    return Boolean(error && /HTTP 401/.test(error.message));
  }

  // Runs fn() once; on an HTTP 401, asks onAuthExpired for a fresh access
  // token (a no-op/never-connected server just returns a falsy value) before
  // retrying exactly once. Applies uniformly to discovery (initialize can
  // itself 401 if the stored token already expired) and to individual tool
  // calls. Never used for anything except auth: any other error, or a
  // second 401 after a successful refresh, propagates as-is.
  function withAuthRetry(server_config, onAuthExpired, fn) {
    return fn()
      .push(undefined, function (error) {
        if (!onAuthExpired || !isAuthExpiredError(error)) {
          throw error;
        }
        return onAuthExpired(server_config)
          .push(function (refreshed) {
            if (!refreshed || !refreshed.access_token) {
              throw error;
            }
            server_config.token = refreshed.access_token;
            return fn();
          });
      });
  }

  function discoverServerTools(server_config, onAuthExpired) {
    return withAuthRetry(server_config, onAuthExpired, function () {
      return initializeSession(server_config)
        .push(function (session) {
          return listAllTools(server_config, session)
            .push(function (raw_tool_list) {
              return { session: session, raw_tool_list: raw_tool_list };
            });
        });
    });
  }

  function callTool(server_config, session, raw_tool_name, args) {
    return rpcCall(server_config, "tools/call", { name: raw_tool_name, arguments: args || {} }, session)
      .push(function (result) {
        var text_part_list = ((result && result.content) || [])
          .filter(function (part) { return part.type === "text"; })
          .map(function (part) { return part.text; });
        if (result && result.isError) {
          throw new Error(text_part_list.join("\n") || "tool reported an error with no message");
        }
        return text_part_list.length ? text_part_list.join("\n") : JSON.stringify((result && result.content) || result);
      });
  }

  // discovery.session is mutated in place on a successful re-handshake so
  // later calls to the same tool (closed over the same `discovery` object)
  // reuse the fresh session too, instead of re-initializing every time.
  // Session-loss (404) and auth-expiry (401) are independent retry paths:
  // either, or both in sequence, can fire for a single call before it's
  // finally reported as failed.
  function callToolWithRetry(server_config, discovery, raw_tool_name, args, onAuthExpired) {
    return withAuthRetry(server_config, onAuthExpired, function () {
      return callTool(server_config, discovery.session, raw_tool_name, args)
        .push(undefined, function (error) {
          if (!isSessionLostError(error)) {
            throw error;
          }
          return initializeSession(server_config)
            .push(function (new_session) {
              discovery.session = new_session;
              return callTool(server_config, new_session, raw_tool_name, args);
            });
        });
    })
      .push(function (text) {
        return text;
      }, function (error) {
        return "ERROR: MCP tool call failed: " + (error && error.message ? error.message : String(error));
      });
  }

  function wrapServerTools(server_config, discovery, onAuthExpired) {
    var used_name_set = {};
    return discovery.raw_tool_list.map(function (raw_tool) {
      var public_name = uniqueNamespacedName(server_config.name, raw_tool.name, used_name_set);
      return {
        definition: {
          name: public_name,
          description: "[MCP: " + server_config.name + "] " + (raw_tool.description || raw_tool.name),
          parameters: raw_tool.inputSchema || { type: "object", properties: {} }
        },
        execute: function (args) {
          return callToolWithRetry(server_config, discovery, raw_tool.name, args, onAuthExpired);
        }
      };
    });
  }

  // Never rejects: an unreachable/misbehaving server contributes zero tools
  // (reported via onServerError) rather than breaking discovery for every
  // other configured server, or for the local sandbox tools this is merged
  // with in gadget_chat_tools_js.js. onAuthExpired is optional - a server
  // authenticated with a plain static token (no OAuth) simply never
  // triggers it (a 401 there just fails discovery for that server normally).
  function buildToolList(mcp_server_list, element, onServerError, onAuthExpired) {
    if (!mcp_server_list || !mcp_server_list.length) {
      return RSVP.resolve([]);
    }
    return new RSVP.Queue(RSVP.all(mcp_server_list.map(function (server_config) {
      return discoverServerTools(server_config, onAuthExpired)
        .push(function (discovery) {
          return wrapServerTools(server_config, discovery, onAuthExpired);
        })
        .push(undefined, function (error) {
          if (onServerError) {
            onServerError(server_config, error);
          }
          return [];
        });
    })))
      .push(function (tool_list_list) {
        return tool_list_list.reduce(function (flat, tool_list) { return flat.concat(tool_list); }, []);
      });
  }

  // Discovery-only probe (initialize + tools/list, no tools/call) used by the
  // settings page to report per-server connectivity without needing to build
  // (and namespace) an actual tool list.
  function probeServer(server_config, onAuthExpired) {
    return discoverServerTools(server_config, onAuthExpired)
      .push(function (discovery) {
        return { ok: true, tool_count: discovery.raw_tool_list.length };
      }, function (error) {
        return { ok: false, error: error && error.message ? error.message : String(error) };
      });
  }

  // One MCP server URL per line (blank lines ignored, exact duplicates
  // dropped) - the URL itself doubles as the server's "name" (the tool
  // namespace prefix, and its key in the OAuth token map), so there's
  // nothing else to fill in. A static bearer token, if one is ever needed
  // for a server with no OAuth support, can still be embedded directly in
  // the URL (e.g. as a query parameter) since the whole line becomes both
  // `url` and `name` verbatim. Shared by the Settings page (validates on
  // submit) and the officejs task view (parses the saved setting) so both
  // agree on exactly the same format.
  function parseServerListText(text) {
    var raw_line_list, i, line, seen = {}, value = [];
    if (!text || !text.trim()) {
      return { ok: true, value: [] };
    }
    raw_line_list = text.split("\n");
    for (i = 0; i < raw_line_list.length; i += 1) {
      line = raw_line_list[i].trim();
      if (!line) {
        continue;
      }
      if (!/^https?:\/\//i.test(line)) {
        return { ok: false, error: "Line " + (i + 1) + " (\"" + line + "\") must be a full http:// or https:// URL." };
      }
      if (!seen.hasOwnProperty(line)) {
        seen[line] = true;
        value.push({ name: line, url: line });
      }
    }
    return { ok: true, value: value };
  }

  window.ChatMCP = {
    buildToolList: buildToolList,
    probeServer: probeServer,
    parseServerListText: parseServerListText
  };
}(window, RSVP));
