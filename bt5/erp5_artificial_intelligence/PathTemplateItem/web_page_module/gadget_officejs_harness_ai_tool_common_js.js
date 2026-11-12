/*global window, document, Worker, URL, RSVP, setTimeout, clearTimeout */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, document) {
  "use strict";


  var SANDBOX_WORKER_URL = new URL(
      "gadget_officejs_harness_ai_sandbox_worker.js",
      (document.currentScript && document.currentScript.src) || document.baseURI
    ).href,
    SANDBOX_DEFAULT_TIMEOUT_MS = 10000,
    SANDBOX_MAX_TIMEOUT_MS = 120000,
    // Long tool results (PDF text, fetched pages) are read in windows of at
    // most TEXT_WINDOW_CHARS, or searched with a regular expression.
    TEXT_WINDOW_CHARS = 30000,
    TEXT_SEARCH_MAX_MATCHES = 40,
    TEXT_SEARCH_CONTEXT_CHARS = 150,
    // A longer match (eg. of a greedy pattern) is cut, so that a search
    // never returns most of the text.
    TEXT_SEARCH_MATCH_MAX_CHARS = 300,
    // Failed LLM requests of the agent loop and of spawn_subagent: transient
    // errors (context overflow, rate limit, 5xx, empty response) are retried
    // MAX_RETRY_COUNT times in a row, each kind counted apart. Network
    // errors, frequent in a browser (sleep, wifi, ...), are retried until it
    // works.
    MAX_RETRY_COUNT = 3,
    MAX_RETRY_DELAY = 60000,
    // After a context overflow, the history is compacted to keep only this
    // many recent tokens.
    PANIC_KEEP_RECENT_TOKEN_BUDGET = 8000,
    // Error messages of the servers (in a 4xx response) when the prompt is
    // larger than the context window.
    CONTEXT_OVERFLOW_PATTERN = /context[_ ]length|context (?:size|window)|prompt (?:is )?too long|too many tokens|token limit exceeded/i,
    // Errors sent inside the stream, which have no HTTP status, that may
    // succeed later.
    RETRYABLE_ERROR_PATTERN = /overloaded|rate.?limit|too many requests|unavailable|server.?error|internal.?error|provider returned error/i,
    NON_RETRYABLE_ERROR_PATTERN = /insufficient_quota|quota exceeded|billing/i,
    // The request or its response stream failed: "Failed to fetch" and
    // "network error" (Chrome), "NetworkError ..." and "Error in input
    // stream" (Firefox, the stream cut midway), "Load failed" (Safari).
    NETWORK_ERROR_PATTERN = /failed to fetch|network\s*error|load failed|connection was lost|error in input stream/i;

  // The kind of retry of a failed LLM request, or null if the error is not
  // transient: "context_overflow_retry", "rate_limit_retry" (also server
  // errors, but not an exhausted quota or billing problem),
  // "empty_response_retry" or "network_error_retry".
  function getRetryName(e) {
    var message = (e && e.message) || "";
    if (e && e.status && (e.status === 413 || (e.status >= 400 && e.status < 500 && e.status !== 429 &&
        CONTEXT_OVERFLOW_PATTERN.test(message)))) {
      return "context_overflow_retry";
    }
    if (message && !NON_RETRYABLE_ERROR_PATTERN.test(message) && (e.status === 429 || e.status >= 500 ||
        (!e.status && RETRYABLE_ERROR_PATTERN.test(message)))) {
      return "rate_limit_retry";
    }
    if ((/^Empty response from LLM/).test(message)) {
      return "empty_response_retry";
    }
    if (NETWORK_ERROR_PATTERN.test(message)) {
      return "network_error_retry";
    }
    return null;
  }

  // Whether a request that failed retry_count times in a row with this kind
  // of error is retried once more.
  function isRetryAllowed(retry_name, retry_count) {
    return Boolean(retry_name) && (retry_name === "network_error_retry" || retry_count < MAX_RETRY_COUNT);
  }

  // What the server asked with Retry-After (at most 2 minutes), otherwise
  // 2s doubled at each attempt, at most MAX_RETRY_DELAY.
  function getRetryDelay(e, retry_count) {
    if (e && e.retry_after_ms > 0) {
      return Math.min(e.retry_after_ms, 120000);
    }
    return Math.min(2000 * Math.pow(2, retry_count), MAX_RETRY_DELAY);
  }

  // Usage counting of the agent loop and of spawn_subagent: each LLM call,
  // compaction and sub-agent returns its usage_totals, which the caller adds
  // to its own.
  function createUsageTotals() {
    return { call_count: 0, prompt_tokens: 0, completion_tokens: 0, total_tokens: 0 };
  }

  function addUsageTotals(usage_totals, added_usage_totals) {
    if (added_usage_totals) {
      usage_totals.call_count += added_usage_totals.call_count;
      usage_totals.prompt_tokens += added_usage_totals.prompt_tokens;
      usage_totals.completion_tokens += added_usage_totals.completion_tokens;
      usage_totals.total_tokens += added_usage_totals.total_tokens;
    }
    return usage_totals;
  }

  function decodeHtmlEntities(text) {
    return text
      .replace(/&nbsp;/g, " ")
      .replace(/&lt;/g, "<")
      .replace(/&gt;/g, ">")
      .replace(/&quot;/g, "\"")
      .replace(/&#(\d+);/g, function (match, code) { return String.fromCharCode(+code); })
      .replace(/&#x([0-9a-f]+);/gi, function (match, hex) { return String.fromCharCode(parseInt(hex, 16)); })
      .replace(/&amp;/g, "&");
  }

  // The absolute URL of a link of a page, or "" for a link that does not
  // lead to another page (an anchor in the page, javascript:, mailto:, ...).
  function getLinkUrl(href, base_url) {
    var url;
    href = decodeHtmlEntities(href).trim();
    if (!href || href.charAt(0) === "#") {
      return "";
    }
    try {
      url = new URL(href, base_url || undefined);
    } catch (ignore) {
      return "";
    }
    if (url.protocol !== "http:" && url.protocol !== "https:") {
      return "";
    }
    url.hash = "";
    return url.href;
  }

  // The readable text of an HTML page. Its links are kept as
  // "text (absolute URL)", resolved against base_url (the URL of the page),
  // so that the model can follow them instead of guessing URLs.
  function htmlToText(html, base_url) {
    var body_match = /<body[^>]*>([\s\S]*)<\/body>/i.exec(html),
      base_match = /<base\b[^>]*\bhref\s*=\s*["']?([^"'\s>]+)/i.exec(html);
    if (base_match) {
      base_url = getLinkUrl(base_match[1], base_url) || base_url;
    }
    if (body_match) {
      html = body_match[1];
    }
    return decodeHtmlEntities(html
      .replace(/<script[\s\S]*?<\/script>/gi, " ")
      .replace(/<style[\s\S]*?<\/style>/gi, " ")
      .replace(/<!--[\s\S]*?-->/g, " ")
      .replace(/<a\b[^>]*?\bhref\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'>]+))[^>]*>([\s\S]*?)<\/a\s*>/gi,
        function (match, href_double, href_single, href_bare, inner_html) {
          var url = getLinkUrl(href_double || href_single || href_bare || "", base_url),
            text = inner_html.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();
          if (!url) {
            return " " + text + " ";
          }
          if (!text || text === url || text + "/" === url) {
            return " " + url + " ";
          }
          return " " + text + " (" + url + ") ";
        })
      .replace(/<\/(p|div|li|tr|h[1-6]|section|article)>/gi, "\n")
      .replace(/<br\s*\/?>/gi, "\n")
      .replace(/<[^>]+>/g, " "))
      .replace(/[ \t]+/g, " ")
      .replace(/\n\s*\n\s*\n+/g, "\n\n")
      .replace(/^\s+|\s+$/g, "");
  }


  function runSandboxJob(kind, payload, timeout_ms) {
    var budget = Math.min(Math.max(Number(timeout_ms) || SANDBOX_DEFAULT_TIMEOUT_MS, 100), SANDBOX_MAX_TIMEOUT_MS),
      settled = false,
      worker,
      timer;

    function cleanup() {
      settled = true;
      clearTimeout(timer);
      worker.terminate();
    }

    return new RSVP.Promise(function (resolve) {
      worker = new Worker(SANDBOX_WORKER_URL);
      function finish(value) {
        if (settled) { return; }
        cleanup();
        resolve(value);
      }
      timer = setTimeout(function () {
        finish({ ok: false, error: "execution exceeded " + budget + " ms and was terminated" });
      }, budget);
      worker.onmessage = function (event) {
        var data = event.data;
        // A loaded library (eg. pdf.js, when it detects it is itself
        // running inside a Worker rather than a real main thread) can post
        // its own, unrelated messages on this same channel - only react to
        // a reply that actually matches the job this handler is waiting on.
        if (!data || data.id !== "run_wasm") {
          return;
        }
        finish(data.ok ? data.result : { ok: false, error: data.error, stack: data.stack });
      };
      worker.onerror = function (event) {
        finish({
          ok: false,
          error: "worker error: " + (event.message || "unknown") +
            (event.filename ? " at " + event.filename + ":" + event.lineno + ":" + event.colno : "")
        });
      };
      worker.postMessage({ id: "run_wasm", kind: kind, payload: payload });
    }, function canceller() {
      if (settled) { return; }
      cleanup();
    });
  }

  function runJsCode(code, args, libraries) {
    return new RSVP.Queue(runSandboxJob("js", { code: code, args: args, libraries: libraries }))
      .push(function (result) {
        var parts = [];
        if (result.logs && result.logs.length) {
          parts.push("console:\n" + result.logs.join("\n"));
        }
        if (result.ok) {
          parts.push("result:\n" + (result.resultText || "(undefined)"));
        } else {
          parts.push("ERROR: " + result.error + (result.stack ? "\n" + result.stack : ""));
        }
        return parts.join("\n\n");
      });
  }

  function noLocation() {
    return "";
  }

  // Every match of the case-insensitive `pattern` with its char offset and
  // TEXT_SEARCH_CONTEXT_CHARS of context on each side. locate(start, end)
  // adds a location (eg. a page number) to each offset.
  function searchText(text, pattern, locate) {
    var regexp,
      match,
      match_list = [],
      match_count = 0,
      last_end = -1,
      start,
      end,
      match_text;
    locate = locate || noLocation;
    try {
      regexp = new RegExp(pattern, "gi");
    } catch (e) {
      return "ERROR: invalid pattern: " + e.message;
    }
    match = regexp.exec(text);
    while (match !== null) {
      if (match[0].length === 0) {
        regexp.lastIndex += 1;
      } else {
        match_count += 1;
        if (match.index >= last_end && match_list.length < TEXT_SEARCH_MAX_MATCHES) {
          start = Math.max(0, match.index - TEXT_SEARCH_CONTEXT_CHARS);
          end = Math.min(text.length, match.index + match[0].length + TEXT_SEARCH_CONTEXT_CHARS);
          last_end = end;
          match_text = match[0].length <= TEXT_SEARCH_MATCH_MAX_CHARS ? match[0] :
              match[0].slice(0, TEXT_SEARCH_MATCH_MAX_CHARS) + " [... " +
              (match[0].length - TEXT_SEARCH_MATCH_MAX_CHARS) + " more chars of this " +
              match[0].length + "-char match: read it with min_chars=" + match.index + " ...] ";
          match_list.push("[char " + match.index + locate(match.index, match.index + 1) + "] ..." +
            (text.slice(start, match.index) + match_text +
              text.slice(match.index + match[0].length, end)).replace(/\s+/g, " ") + "...");
        }
      }
      match = regexp.exec(text);
    }
    if (!match_count) {
      return "No match for /" + pattern + "/i in " + text.length + " chars.";
    }
    return match_count + " match(es) for /" + pattern + "/i in " + text.length + " chars" +
      (match_list.length < match_count ? ", showing " + match_list.length +
        " (overlapping ones and those beyond the first " + TEXT_SEARCH_MAX_MATCHES + " are left out)" : "") +
      ":\n\n" + match_list.join("\n\n") +
      "\n\n[To read around a match, call again with min_chars a little before its char offset.]";
  }

  // The [min_chars, max_chars) window of `text`, at most window_chars
  // (default TEXT_WINDOW_CHARS) long, followed by how to read further when
  // it is not the whole text.
  function readTextWindow(text, min_chars, max_chars, locate, window_chars) {
    var start = Math.min(Math.max(0, Number(min_chars) || 0), text.length),
      end = Math.max(start, Math.min(Number(max_chars) || Infinity, start + (window_chars || TEXT_WINDOW_CHARS),
        text.length));
    locate = locate || noLocation;
    if (start === 0 && end === text.length) {
      return text;
    }
    return text.slice(start, end) + "\n\n[Showing chars " + start + "-" + end + " of " + text.length +
      locate(start, end) + "." + (end < text.length ?
          " To find something, search the whole text with pattern; to read the next part, use " +
            "min_chars=" + end + "." :
          " End of the text.") + "]";
  }

  window.ChatToolCommon = {
    TEXT_WINDOW_CHARS: TEXT_WINDOW_CHARS,
    TEXT_SEARCH_MAX_MATCHES: TEXT_SEARCH_MAX_MATCHES,
    TEXT_SEARCH_CONTEXT_CHARS: TEXT_SEARCH_CONTEXT_CHARS,
    searchText: searchText,
    readTextWindow: readTextWindow,
    htmlToText: htmlToText,
    runSandboxJob: runSandboxJob,
    runJsCode: runJsCode,
    createUsageTotals: createUsageTotals,
    addUsageTotals: addUsageTotals,
    MAX_RETRY_COUNT: MAX_RETRY_COUNT,
    PANIC_KEEP_RECENT_TOKEN_BUDGET: PANIC_KEEP_RECENT_TOKEN_BUDGET,
    getRetryName: getRetryName,
    isRetryAllowed: isRetryAllowed,
    getRetryDelay: getRetryDelay
  };
}(window, document));
