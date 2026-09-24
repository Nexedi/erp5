/*global window, document, fetch, RSVP, crypto, TextEncoder, URL, URLSearchParams */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, document, RSVP) {
  "use strict";

  var CALLBACK_PAGE = "gadget_officejs_harness_ai_mcp_oauth_callback.html",
    CLIENT_NAME = "ERP5 OfficeJS Harness Agent",
    POPUP_FEATURES = "width=480,height=640",
    EXPIRY_SAFETY_MARGIN_MS = 30000;

  function callbackUrl() {
    return new URL(CALLBACK_PAGE, document.baseURI).href;
  }

  function base64UrlEncode(buffer) {
    var bytes = buffer instanceof ArrayBuffer ? new Uint8Array(buffer) : buffer,
      binary = "",
      i;
    for (i = 0; i < bytes.length; i += 1) {
      binary += String.fromCharCode(bytes[i]);
    }
    return window.btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
  }

  function randomUrlSafeString(byte_length) {
    var bytes = new Uint8Array(byte_length);
    crypto.getRandomValues(bytes);
    return base64UrlEncode(bytes);
  }

  function sha256Base64Url(text) {
    return new RSVP.Queue(crypto.subtle.digest("SHA-256", new TextEncoder().encode(text)))
      .push(function (digest) {
        return base64UrlEncode(digest);
      });
  }

  function fetchJSON(url, options) {
    return new RSVP.Queue(fetch(url, options))
      .push(function (response) {
        if (!response.ok) {
          return new RSVP.Queue(response.text())
            .push(function (text) {
              throw new Error("HTTP " + response.status + (text ? ": " + text.slice(0, 300) : ""));
            });
        }
        return response.json();
      });
  }

  // RFC 9728 protected-resource metadata first (points at the authorization
  // server), falling back to treating the MCP server's own origin as the
  // authorization server directly - the common single-tenant setup, and what
  // erp5-mcp-hateoas's remote mode does (issuer_url === resource_server_url).
  function discoverMetadata(server_config) {
    var mcp_origin = new URL(server_config.url).origin;
    return fetchJSON(mcp_origin + "/.well-known/oauth-protected-resource")
      .push(function (resource_metadata) {
        var auth_server = (resource_metadata.authorization_servers || [])[0] || mcp_origin;
        return fetchJSON(auth_server.replace(/\/+$/, "") + "/.well-known/oauth-authorization-server");
      }, function () {
        return fetchJSON(mcp_origin + "/.well-known/oauth-authorization-server");
      });
  }

  // Dynamic Client Registration (RFC 7591) - a public client (no secret),
  // PKCE-only, matching what erp5-mcp-hateoas's remote mode expects
  // (ClientRegistrationOptions(enabled=True), token_endpoint_auth_method "none").
  function registerClient(auth_metadata) {
    return fetchJSON(auth_metadata.registration_endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        client_name: CLIENT_NAME,
        redirect_uris: [callbackUrl()],
        grant_types: ["authorization_code", "refresh_token"],
        response_types: ["code"],
        token_endpoint_auth_method: "none"
      })
    })
      .push(function (registration) {
        return registration.client_id;
      });
  }

  // Opens the sign-in page in a popup (never an iframe - the erp5 instance's
  // own CSP frame-src wouldn't allow embedding a foreign MCP server's login
  // page anyway) and waits for gadget_officejs_harness_ai_mcp_oauth_callback_html.html to
  // postMessage the resulting code back once the popup lands there.
  function openAuthorizePopupAndWaitForCode(authorize_url, expected_state) {
    return new RSVP.Promise(function (resolve, reject) {
      var popup = window.open(authorize_url, "erp5_mcp_oauth", POPUP_FEATURES),
        poll_timer,
        cleaned = false;

      function cleanup() {
        if (cleaned) {
          return;
        }
        cleaned = true;
        window.removeEventListener("message", onMessage);
        clearInterval(poll_timer);
        try {
          popup.close();
        } catch (ignore) {
          return;
        }
      }

      function onMessage(event) {
        if (event.origin !== window.location.origin || !event.data || event.data.source !== "erp5-mcp-oauth") {
          return;
        }
        cleanup();
        if (event.data.error) {
          reject(new Error("Authorization failed: " + event.data.error));
        } else if (event.data.state !== expected_state) {
          reject(new Error("Authorization state mismatch - aborting for safety."));
        } else {
          resolve(event.data.code);
        }
      }

      if (!popup) {
        reject(new Error("Popup blocked - allow popups for this site and try again."));
        return;
      }
      window.addEventListener("message", onMessage);
      poll_timer = setInterval(function () {
        if (popup.closed) {
          cleanup();
          reject(new Error("Sign-in window was closed before completing."));
        }
      }, 500);
    });
  }

  function exchangeCodeForToken(auth_metadata, client_id, code, code_verifier) {
    var body = new URLSearchParams();
    body.set("grant_type", "authorization_code");
    body.set("code", code);
    body.set("redirect_uri", callbackUrl());
    body.set("client_id", client_id);
    body.set("code_verifier", code_verifier);
    return fetchJSON(auth_metadata.token_endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: body.toString()
    });
  }

  function tokenResponseToState(auth_metadata, client_id, token_response) {
    return {
      client_id: client_id,
      authorization_endpoint: auth_metadata.authorization_endpoint,
      token_endpoint: auth_metadata.token_endpoint,
      registration_endpoint: auth_metadata.registration_endpoint,
      access_token: token_response.access_token,
      refresh_token: token_response.refresh_token,
      expires_at: Date.now() + (Number(token_response.expires_in || 0) * 1000)
    };
  }

  // Full interactive sign-in: discover -> register (or reuse a still-valid
  // registration from existing_state, same token_endpoint) -> PKCE -> popup
  // authorize -> exchange. Only ever called from an explicit user action
  // (the Settings page's "Connect" button), never automatically mid-chat.
  function connect(server_config, existing_state) {
    var code_verifier = randomUrlSafeString(32),
      state = randomUrlSafeString(16),
      auth_metadata;
    return discoverMetadata(server_config)
      .push(function (metadata) {
        auth_metadata = metadata;
        if (existing_state && existing_state.client_id && existing_state.token_endpoint === metadata.token_endpoint) {
          return existing_state.client_id;
        }
        return registerClient(metadata);
      })
      .push(function (client_id) {
        return sha256Base64Url(code_verifier)
          .push(function (code_challenge) {
            var authorize_url = auth_metadata.authorization_endpoint +
              "?" + new URLSearchParams({
                response_type: "code",
                client_id: client_id,
                redirect_uri: callbackUrl(),
                state: state,
                code_challenge: code_challenge,
                code_challenge_method: "S256"
              }).toString();
            return new RSVP.Queue(openAuthorizePopupAndWaitForCode(authorize_url, state))
              .push(function (code) {
                return exchangeCodeForToken(auth_metadata, client_id, code, code_verifier);
              })
              .push(function (token_response) {
                return tokenResponseToState(auth_metadata, client_id, token_response);
              });
          });
      });
  }

  // Silent refresh using a stored refresh_token - no popup, no user
  // interaction. Never rejects: returns null if there is nothing to refresh
  // with (or the refresh itself fails), so callers can treat "can't silently
  // refresh" the same as "never connected" and ask the user to reconnect.
  function refresh(oauth_state) {
    var body;
    if (!oauth_state || !oauth_state.refresh_token) {
      return RSVP.resolve(null);
    }
    body = new URLSearchParams();
    body.set("grant_type", "refresh_token");
    body.set("refresh_token", oauth_state.refresh_token);
    body.set("client_id", oauth_state.client_id);
    return fetchJSON(oauth_state.token_endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: body.toString()
    })
      .push(function (token_response) {
        return {
          client_id: oauth_state.client_id,
          authorization_endpoint: oauth_state.authorization_endpoint,
          token_endpoint: oauth_state.token_endpoint,
          registration_endpoint: oauth_state.registration_endpoint,
          access_token: token_response.access_token,
          refresh_token: token_response.refresh_token || oauth_state.refresh_token,
          expires_at: Date.now() + (Number(token_response.expires_in || 0) * 1000)
        };
      }, function () {
        return null;
      });
  }

  function isExpired(oauth_state) {
    return !oauth_state || !oauth_state.expires_at || oauth_state.expires_at <= (Date.now() + EXPIRY_SAFETY_MARGIN_MS);
  }

  window.ChatMCPOAuth = {
    connect: connect,
    refresh: refresh,
    isExpired: isExpired
  };
}(window, document, RSVP));
