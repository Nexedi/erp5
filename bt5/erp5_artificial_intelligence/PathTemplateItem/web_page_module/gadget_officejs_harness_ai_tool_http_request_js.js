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

  var HTTP_TEXT_WINDOW_CHARS = 8000,
    // Appended to failures, so the model moves on instead of retrying the
    // same URL, which returns the same failure.
    NO_RETRY_HINT = "Retrying the same URL will not help: use other sources, or report this " +
      "source as not verified.";

  function normalizeUrl(url) {
    try {
      url = decodeURI(url);
    } catch (ignore) {
      // keep the URL as it is
    }
    return url.replace(/\/+$/, "");
  }

  // Note after the body of an HTTP error status of the target.
  function statusHint(status) {
    if (status < 400) {
      return "";
    }
    if (status === 408 || status === 429 || (status >= 500 && status !== 501)) {
      return "\n\n[HTTP " + status + ": the site failed to answer. It may work later, but do not " +
        "retry it right away: use other sources first.]";
    }
    return "\n\n[HTTP " + status + ": this URL does not work. " + NO_RETRY_HINT + "]";
  }

  rJS(window)
    .declareMethod('render', function (options) {
      this.proxy_server_url = (options && options.proxy_server_url) || '';
    })
    .declareMethod('getDefinition', function () {
      return {
        name: "http_request",
        description: "Fetch a public URL: a web page or a JSON API. HTML is converted to " +
          "readable text, with each link written as \"text (absolute URL)\". The JavaScript of " +
          "the page does not run, so pages built by JavaScript (many search engines and web " +
          "portals) come back nearly empty. Requests carry no cookies or login. PDF and other " +
          "binary files can not be read.\n" +
          "Fetch only a URL given by the user, a link found in a page you fetched, or the home page " +
          "or documented API of a site you know. Do not build URLs yourself: no guessed paths, no " +
          "made-up query parameters (search=, keyword=, _format=json, ...), no search engine result " +
          "pages. If 2 or 3 fetches for the same source fail or do not give what you need, stop " +
          "trying that source: use the results you have, and report what you could not find or " +
          "verify.",
        parameters: {
          type: "object",
          properties: {
            url: { type: "string" },
            method: { type: "string", "enum": ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD"],
              description: "Default GET." },
            headers: { type: "object", description: "Extra request headers." },
            body: { type: "string", description: "Request body, eg. JSON text for a POST." },
            raw: { type: "boolean", description: "Return the body as it is, not converted to text." },
            min_chars: { type: "integer", description: "One call returns at most " +
              HTTP_TEXT_WINDOW_CHARS + " chars of the text: start from this char offset to read " +
              "further (default 0)." },
            max_chars: { type: "integer", description: "Stop at this char offset (default and " +
              "maximum: min_chars + " + HTTP_TEXT_WINDOW_CHARS + ")." },
            pattern: { type: "string", description: "Search the whole text instead of reading it: " +
              "a case-insensitive regular expression (eg. \"deadline|closing date\", or a link " +
              "text to find its URL). Returns each match with its char offset and " +
              window.ChatToolCommon.TEXT_SEARCH_CONTEXT_CHARS + " chars of context on each side, at " +
              "most " + window.ChatToolCommon.TEXT_SEARCH_MAX_MATCHES + " matches. min_chars and " +
              "max_chars are ignored." }
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

      // Requests never carry this site's cookies (credentials "omit"): the
      // model must not act on the site as the logged-in user.
      if (gadget.proxy_server_url) {
        fetch_url = gadget.proxy_server_url.replace(/\/+$/, '') + "/proxy";
        fetch_options = {
          method: "POST",
          credentials: "omit",
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
          credentials: "omit",
          headers: request_headers,
          body: args.body,
          signal: controller.signal
        };
      }

      raw_promise = new RSVP.Promise(function (resolve, reject) {
        fetch(fetch_url, fetch_options)
          .then(function (response) {
            var content_type = response.headers.get("content-type") || "",
              status = response.status,
              // Through the forwarder, response.url is the forwarder itself:
              // it reports the URL that answered in X-Final-URL instead.
              final_url = gadget.proxy_server_url ? response.headers.get("X-Final-URL") : response.url,
              is_proxy_error = Boolean(gadget.proxy_server_url && response.headers.get("X-Proxy-Error"));
            return response.text().then(function (text) {
              return {
                status: status,
                content_type: content_type,
                text: text,
                final_url: final_url,
                is_proxy_error: is_proxy_error
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
          var text, is_html, proxy_error, header;
          if (result.error) {
            return "ERROR: could not fetch " + target + ": " + result.error +
              (gadget.proxy_server_url ? "" : " (network error, or the site does not allow requests " +
                "from a browser page and no forwarder Server URL is set)") + ". " + NO_RETRY_HINT;
          }
          if (result.is_proxy_error) {
            try {
              proxy_error = JSON.parse(result.text).error;
            } catch (ignore) {
              proxy_error = result.text;
            }
            // A DNS failure reads like a network hiccup, but the domain does
            // not exist: say so, the model tends to retry it otherwise.
            if (/^cannot resolve /.test(proxy_error)) {
              return "ERROR: the domain " + proxy_error.replace(/^cannot resolve ([^:]+):[\s\S]*$/, "$1") +
                " does not exist (DNS lookup failed), so " + target + " is a wrong address, not a site " +
                "that is down for now. Do not retry it: find the right address of this source, or report " +
                "it as not verified.";
            }
            return "ERROR: could not fetch " + target + ": " + proxy_error + ". " + NO_RETRY_HINT;
          }
          text = result.text || "";
          header = "HTTP " + result.status + " " + (result.content_type || "");
          if (result.final_url && normalizeUrl(result.final_url) !== normalizeUrl(target)) {
            header += "\nRedirected to: " + result.final_url;
          }

          is_html = /html/i.test(result.content_type || "") ||
            /<(!doctype\s+html|html|head)[\s>]/i.test(text.slice(0, 2000));
          if (!args.raw && is_html) {
            text = window.ChatToolCommon.htmlToText(text, result.final_url || target);
          }
          text = args.pattern ? window.ChatToolCommon.searchText(text, args.pattern) :
              window.ChatToolCommon.readTextWindow(text, args.min_chars, args.max_chars, undefined,
                HTTP_TEXT_WINDOW_CHARS);
          return header + "\n\n" + text + statusHint(result.status);
        });
    });
}(window, rJS, RSVP));
