/*global window, Worker, RSVP, setTimeout, clearTimeout */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window) {
  "use strict";

  var SANDBOX_WORKER_URL = "gadget_officejs_harness_ai_sandbox_worker.js",
    SANDBOX_DEFAULT_TIMEOUT_MS = 10000,
    SANDBOX_MAX_TIMEOUT_MS = 120000;

  function truncate(text, max_len) {
    if (typeof text !== "string") {
      text = String(text);
    }
    return text.length > max_len ? text.slice(0, max_len) + "\n... [truncated at " + max_len + " chars]" : text;
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
        finish(data.ok ? data.result : { ok: false, error: data.error });
      };
      worker.onerror = function (event) {
        finish({ ok: false, error: "worker error: " + (event.message || "unknown") });
      };
      worker.postMessage({ id: "run_wasm", kind: kind, payload: payload });
    }, function canceller() {
      if (settled) { return; }
      cleanup();
    });
  }

  function renderPlanText(plan) {
    if (!plan) {
      return "(no execution plan set)";
    }
    return "Goal: " + plan.goal + "\n" + plan.step_list.map(function (step, i) {
      return i + ". [" + step.status + "] " + step.title + (step.note ? " - " + step.note : "");
    }).join("\n");
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

  window.ChatToolCommon = {
    truncate: truncate,
    htmlToText: htmlToText,
    runSandboxJob: runSandboxJob,
    renderPlanText: renderPlanText,
    runJsCode: runJsCode
  };
}(window));
