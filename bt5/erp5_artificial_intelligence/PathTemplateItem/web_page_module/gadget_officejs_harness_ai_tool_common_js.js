/*global window, Worker, RSVP, setTimeout, clearTimeout */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window) {
  "use strict";

  var SANDBOX_WORKER_URL = "gadget_officejs_harness_ai_sandbox_worker.js",
    SANDBOX_DEFAULT_TIMEOUT_MS = 10000,
    SANDBOX_MAX_TIMEOUT_MS = 120000,
    MAX_TOOL_OUTPUT_LINES = 20000;

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

  function truncateToolOutput(content) {
    var text = typeof content === "string" ? content : JSON.stringify(content),
      lines = text.split("\n"),
      kept;
    if (lines.length <= MAX_TOOL_OUTPUT_LINES) {
      return text;
    }
    kept = lines.slice(-MAX_TOOL_OUTPUT_LINES).join("\n");
    return "[output truncated: showing last " + MAX_TOOL_OUTPUT_LINES + " of " +
      lines.length + " lines - full output is visible in the tool call panel]\n" + kept;
  }

  function toolDefinitionList(tool_list) {
    return tool_list.map(function (tool) {
      return { type: "function", "function": tool.definition };
    });
  }

  function findClientTool(name, tool_list) {
    var i;
    for (i = 0; i < tool_list.length; i += 1) {
      if (tool_list[i].definition.name === name) {
        return tool_list[i];
      }
    }
    return null;
  }

  function runClientToolCall(tool_call, tool_list) {
    var tool = findClientTool(tool_call.function.name, tool_list),
      args = {},
      result;
    try {
      args = tool_call.function.arguments ?
        JSON.parse(tool_call.function.arguments) : {};
    } catch (ignore) {
      args = {};
    }
    if (!tool) {
      result = "Error: no such client tool \"" + tool_call.function.name + "\"";
      return {
        tool_call_id: tool_call.id,
        name: tool_call.function.name,
        content: typeof result === "string" ? result : JSON.stringify(result)
      };
    }
    return new RSVP.Queue()
      .push(function () {
        return tool.gadget ? tool.gadget.execute(args) : tool.execute(args);
      })
      .push(function (result) {

        var is_structured_result = Boolean(result && typeof result === "object" && result.hasOwnProperty("content")),
          message_list = is_structured_result ? result.message_list : undefined,
          execution_plan = is_structured_result ? result.execution_plan : undefined,
          content = is_structured_result ? result.content : result;
        return {
          tool_call_id: tool_call.id,
          name: tool_call.function.name,
          content: typeof content === "string" ? content : JSON.stringify(content),
          message_list: message_list,
          execution_plan: execution_plan
        };
      }, function (e) {
      result = "Error running tool \"" + tool_call.function.name + "\": " + JSON.stringify(e, Object.getOwnPropertyNames(e));
      return {
        tool_call_id: tool_call.id,
        name: tool_call.function.name,
        content: result
      };
    });
  }

  window.ChatToolCommon = {
    truncate: truncate,
    htmlToText: htmlToText,
    runSandboxJob: runSandboxJob,
    renderPlanText: renderPlanText,
    runJsCode: runJsCode,
    truncateToolOutput: truncateToolOutput,
    toolDefinitionList: toolDefinitionList,
    findClientTool: findClientTool,
    runClientToolCall: runClientToolCall
  };
}(window));
