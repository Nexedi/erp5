/*global window, rJS, RSVP, AbortController, fetch */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  // JSON with every non-ASCII code point escaped, so it stays valid in an
  // HTTP header (ported from ai-agent-harness's js/util.js asciiJSON).
  function asciiJSON(value) {
    return JSON.stringify(value).replace(/[\u0080-￿]/g, function (c) {
      var code = c.charCodeAt(0).toString(16);
      while (code.length < 4) {
        code = "0" + code;
      }
      return "\\u" + code;
    });
  }

  rJS(window)
    .declareMethod('render', function (options) {
      this.proxy_server_url = (options && options.proxy_server_url) || '';
    })
    .declareMethod('getDefinition', function () {
      return {
        name: "http_request",
        description: "Fetch a URL - a web page, a JSON API, any public HTTP(S) resource. Relayed " +
          "through the configured forwarder (Server URL, in External Service) when one is set, purely " +
          "to get around the browser's own CORS restriction on the target; without one, this is a " +
          "plain, unproxied fetch, which only succeeds if the target itself allows cross-origin " +
          "requests. HTML is converted to readable text unless `raw` is requested. This is not a " +
          "general web browser - no JavaScript on the fetched page runs, and there is no rendering.",
        parameters: {
          type: "object",
          properties: {
            url: { type: "string" },
            method: { type: "string", enum: ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD"] },
            headers: { type: "object", description: "Extra request headers." },
            body: { type: "string" },
            raw: { type: "boolean", description: "Return the body verbatim instead of extracted text." },
            max_chars: { type: "integer", description: "Optional: truncate the returned text to this many " +
              "characters. If omitted, the full text is returned (and automatically summarized if it's too " +
              "large to send as-is)." }
          },
          required: ["url"]
        }
      };
    })
    .declareMethod('execute', function (args) {
      var gadget = this,
        controller = new AbortController(),
        target = args.url,
        method = (args.method || "GET").toUpperCase(),
        request_headers = args.headers || {},
        fetch_url,
        fetch_options,
        raw_promise;

      if (!target) {
        return "ERROR: missing url";
      }

      if (gadget.proxy_server_url) {
        fetch_url = gadget.proxy_server_url.replace(/\/+$/, '') + "/proxy";
        fetch_options = {
          method: "POST",
          headers: {
            "Content-Type": "application/octet-stream",
            "X-Target-URL": encodeURI(target),
            "X-Target-Method": method,
            "X-Target-Headers": asciiJSON(request_headers)
          },
          body: args.body,
          signal: controller.signal
        };
      } else {
        fetch_url = target;
        fetch_options = {
          method: method,
          headers: request_headers,
          body: args.body,
          signal: controller.signal
        };
      }

      raw_promise = new RSVP.Promise(function (resolve, reject) {
        fetch(fetch_url, fetch_options)
          .then(function (response) {
            var content_type = response.headers.get("content-type") || "",
              status = response.status;
            return response.text().then(function (text) {
              return {
                status: status,
                content_type: content_type,
                text: text
              };
            });
          })
          .then(resolve, function (error) {
            resolve({error: error && error.message ? error.message : String(error)});
          });
      }, function canceller() {
        controller.abort();
      });

      return new RSVP.Queue(raw_promise)
        .push(function (result) {
          var text, is_html;
          if (result.error) {
            return "ERROR: " + result.error;
          }
          text = result.text || "";

          is_html = /html/i.test(result.content_type || "") ||
            /<(!doctype\s+html|html|head)[\s>]/i.test(text.slice(0, 2000));
          is_html = true;
          if (!args.raw && is_html) {
            text = window.ChatToolCommon.htmlToText(text);
          }
          if (args.max_chars && text.length > args.max_chars) {
            text = text.slice(0, args.max_chars) + "\n... [truncated at " + args.max_chars + " chars]";
          }
          return "HTTP " + result.status + " " + (result.content_type || "") + "\n\n" + text;
        });
    });
}(window, rJS, RSVP));
