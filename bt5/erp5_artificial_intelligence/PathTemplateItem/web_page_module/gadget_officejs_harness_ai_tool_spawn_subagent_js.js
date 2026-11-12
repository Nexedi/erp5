/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  var SUBAGENT_MAX_LOOP_COUNT_CAP = 30,
    SUBAGENT_TURN_LIMIT_PROMPT = "Turn limit reached: you can not call tools anymore. Give your final " +
      "answer now, with what you found so far, in the form asked in the task.",
    SUBAGENT_EXCLUDED_TOOL_NAME_LIST = ["spawn_subagent", "execution_plan"],
    // Appended to the task, so every report has the same shape for the
    // parent agent to check.
    SUBAGENT_REPORT_FORMAT_PROMPT = "When you are done, answer in this form:\n" +
      "Findings: the answer to the task, short and concrete.\n" +
      "Verified sources: each source you actually read, with its URL or document name.\n" +
      "Not verified: what you could not find, read or confirm, and why (eg. a site that does not " +
      "exist or does not answer). Do not guess to fill the gaps.";

  rJS(window)
    .declareAcquiredMethod("requestProcessTask", "requestProcessTask")
    // Used by compactMessageList, which runs with this gadget as its context.
    .declareAcquiredMethod("getModelContextWindow", "getModelContextWindow")
    .declareAcquiredMethod("getSystemPromptList", "getSystemPromptList")
    .declareAcquiredMethod("getToolDefinitionList", "getToolDefinitionList")
    .declareAcquiredMethod("runToolCallList", "runToolCallList")
    .declareAcquiredMethod("compactMessageList", "compactMessageList")
    .declareMethod('render', function (options) {
      this.jio_key = options.jio_key;
    })
    .declareMethod('getDefinition', function () {
      return {
        name: "spawn_subagent",
        description: "Delegate a self-contained sub-task to a new instance of this agent, which has " +
          "the same tools except spawn_subagent and execution_plan. It does not see this " +
          "conversation: the task must give everything it needs. Only its report comes " +
          "back: its findings, the sources it read, and what it could not verify; check " +
          "them before you rely on them. Use it only for independent research that would " +
          "fill this conversation with many reads, and that can run next to others (eg. " +
          "the open calls of program X, and those of program Y). Do not use it for a few " +
          "direct tool calls, or to read a long page or PDF: search it with `pattern` " +
          "instead. In the task, give only facts you verified: never invent a URL, a name " +
          "or a date. Launch at most a few at once: each one is a separate conversation " +
          "with the LLM.",
        parameters: {
          type: "object",
          properties: {
            task: { type: "string", description: "Full, self-contained description of the sub-task, with only verified facts." },
            max_turns: { type: "integer", description: "Maximum number of steps: each LLM request and each round of tool calls counts " +
              "as one (default and maximum " + SUBAGENT_MAX_LOOP_COUNT_CAP + ")." }
          },
          required: ["task"]
        }
      };
    })
    .declareMethod('execute', function (args) {
      var gadget = this,
        queue_loop = new RSVP.Queue(),
        document_id = gadget.jio_key,
        max_loop_count = Math.min(Math.max(Number(args.max_turns) || SUBAGENT_MAX_LOOP_COUNT_CAP, 1), SUBAGENT_MAX_LOOP_COUNT_CAP),
        last_usage_anchor,
        // Local to this execute: several sub-agents can run at the same time
        // on this same gadget, each one counts its own usage.
        usage_totals = window.ChatToolCommon.createUsageTotals();

      function subagentError(message_list, e) {
        return {
          content: "Error running sub-agent: " + JSON.stringify(e, Object.getOwnPropertyNames(e)),
          message_list: message_list,
          usage_totals: usage_totals
        };
      }

      function subagentFinalAnswer(message_list, pending_result) {
        var final_message_list = message_list,
          stopped_content = "[subagent stopped: exceeded " + max_loop_count + " turns without a final answer]";
        return new RSVP.Queue()
          .push(function () {
            if (pending_result) {
              return gadget.runToolCallList(pending_result.tool_calls, message_list, {
                turn_limit_reached: true
              });
            }
          })
          .push(function (tool_round) {
            if (tool_round) {
              final_message_list = final_message_list.concat(tool_round.message_list);
            }
            final_message_list = final_message_list.concat([{ role: "user", content: SUBAGENT_TURN_LIMIT_PROMPT }]);
            return gadget.compactMessageList(gadget, final_message_list, undefined, last_usage_anchor);
          })
          .push(function (compacted) {
            window.ChatToolCommon.addUsageTotals(usage_totals, compacted.usage_totals);
            final_message_list = compacted.message_list;
            return gadget.requestProcessTask(
              document_id,
              {
                message_list: JSON.stringify(final_message_list),
                tool_definition_list: JSON.stringify([]),
                is_background: "1"
              }
            );
          })
          .push(function (result) {
            window.ChatToolCommon.addUsageTotals(usage_totals, result.usage);
            return {
              content: result.content ?
                  "[subagent reached its turn limit - partial answer]\n" + result.content : stopped_content,
              message_list: final_message_list.concat([{ role: "assistant", content: result.content }]),
              usage_totals: usage_totals
            };
          }, function () {
            return {
              content: stopped_content,
              message_list: message_list,
              usage_totals: usage_totals
            };
          });
      }

      // retry_count_dict: how many times in a row the LLM request failed,
      // by kind of error (see ChatToolCommon.getRetryName).
      function subagentLoopCall(loop_count, message_list, pending_result, retry_count_dict) {

        var has_tool_call = Boolean(pending_result && pending_result.tool_calls && pending_result.tool_calls.length);

        if (loop_count >= max_loop_count) {
          return subagentFinalAnswer(message_list, pending_result);
        }

        if (has_tool_call) {
          queue_loop
            .push(function () {
              return gadget.runToolCallList(pending_result.tool_calls, message_list, {
                finish_reason: pending_result.finish_reason,
                excluded_tool_name_list: SUBAGENT_EXCLUDED_TOOL_NAME_LIST
              });
            })
            .push(function (tool_round) {
              return subagentLoopCall(
                loop_count + 1,
                message_list.concat(tool_round.message_list),
                null
              );
            })
            .push(undefined, function (e) {
              return subagentError(message_list, e);
            });
          return;
        }

        queue_loop
          .push(function () {
            return gadget.compactMessageList(gadget, message_list, undefined, last_usage_anchor);
          })
          .push(function (compacted) {
            window.ChatToolCommon.addUsageTotals(usage_totals, compacted.usage_totals);
            // The anchor counted the messages that were just summarized.
            if (compacted.message_list !== message_list) {
              last_usage_anchor = null;
            }
            message_list = compacted.message_list;
            return gadget.getToolDefinitionList(message_list, SUBAGENT_EXCLUDED_TOOL_NAME_LIST);
          })
          .push(function (tool_definition_list) {
            return gadget.requestProcessTask(
              document_id,
              {
                message_list: JSON.stringify(message_list),
                tool_definition_list: JSON.stringify(tool_definition_list),
                is_background: "1"
              }
            );
          })
          .push(function (result) {
            window.ChatToolCommon.addUsageTotals(usage_totals, result.usage);
            if (result.usage && result.usage.prompt_tokens) {
              last_usage_anchor = { prompt_tokens: result.usage.prompt_tokens, message_count: message_list.length };
            }
            if (result.tool_calls && result.tool_calls.length) {
              return subagentLoopCall(
                loop_count + 1,
                message_list.concat([result.message]),
                result
              );
            }
            if (!result.content) {
              throw new Error("Empty response from LLM with no tool calls" +
                (result.finish_reason ? " (finish_reason: " + result.finish_reason + ")" : ""));
            }
            return {
              content: result.content,
              message_list: message_list.concat([{ role: "assistant", content: result.content }]),
              usage_totals: usage_totals
            };
          })
          .push(undefined, function (e) {
            var retry_name = window.ChatToolCommon.getRetryName(e),
              retry_count;
            retry_count_dict = retry_count_dict || {};
            retry_count = retry_count_dict[retry_name] || 0;
            if (!window.ChatToolCommon.isRetryAllowed(retry_name, retry_count)) {
              return subagentError(message_list, e);
            }
            retry_count_dict[retry_name] = retry_count + 1;
            if (retry_name === "context_overflow_retry") {
              return gadget.compactMessageList(gadget, message_list,
                window.ChatToolCommon.PANIC_KEEP_RECENT_TOKEN_BUDGET)
                .push(function (compacted) {
                  window.ChatToolCommon.addUsageTotals(usage_totals, compacted.usage_totals);
                  // Nothing left to compact: retrying would fail the same way.
                  if (compacted.message_list.length >= message_list.length) {
                    return subagentError(message_list, e);
                  }
                  last_usage_anchor = null;
                  return subagentLoopCall(loop_count, compacted.message_list, null, retry_count_dict);
                });
            }
            return new RSVP.Queue()
              .push(function () {
                return RSVP.delay(window.ChatToolCommon.getRetryDelay(e, retry_count));
              })
              .push(function () {
                return subagentLoopCall(loop_count, message_list, null, retry_count_dict);
              });
          });
      }

      queue_loop
        .push(function () {
          return gadget.getSystemPromptList();
        })
        .push(function (system_message_list) {
          subagentLoopCall(0, system_message_list.concat([
            { role: "user", content: args.task + "\n\n" + SUBAGENT_REPORT_FORMAT_PROMPT }
          ]));
        });

      return queue_loop;
    });
}(window, rJS, RSVP));
