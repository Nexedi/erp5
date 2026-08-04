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
    TEXT_SEARCH_CONTEXT_CHARS = 150;

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

  function htmlToText(html) {
    var body_match = /<body[^>]*>([\s\S]*)<\/body>/i.exec(html);
    if (body_match) {
      html = body_match[1];
    }
    return html
      .replace(/<script[\s\S]*?<\/script>/gi, " ")
      .replace(/<style[\s\S]*?<\/style>/gi, " ")
      .replace(/<!--[\s\S]*?-->/g, " ")
      .replace(/<\/(p|div|li|tr|h[1-6]|section|article)>/gi, "\n")
      .replace(/<br\s*\/?>/gi, "\n")
      .replace(/<[^>]+>/g, " ")
      .replace(/&nbsp;/g, " ")
      .replace(/&amp;/g, "&")
      .replace(/&lt;/g, "<")
      .replace(/&gt;/g, ">")
      .replace(/&quot;/g, "\"")
      .replace(/&#(\d+);/g, function (match, code) { return String.fromCharCode(+code); })
      .replace(/&#x([0-9a-f]+);/gi, function (match, hex) { return String.fromCharCode(parseInt(hex, 16)); })
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
      end;
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
          match_list.push("[char " + match.index + locate(match.index, match.index + 1) + "] ..." +
            text.slice(start, end).replace(/\s+/g, " ") + "...");
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
          " Use min_chars=" + end + " to continue, or pattern to search the whole text." :
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
    addUsageTotals: addUsageTotals
  };
}(window, document));
