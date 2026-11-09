/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  var CHARS_PER_TOKEN = 3.5,
    COMPACT_TOKEN_BUDGET = 80000,
    KEEP_RECENT_TOKEN_BUDGET = 28000,
    CONTEXT_RESERVE_TOKENS = 16384,
    PANIC_KEEP_RECENT_TOKEN_BUDGET = 8000,
    // Transient LLM errors (context overflow, rate limit, 5xx, empty
    // response) are retried MAX_RETRY_COUNT times in a row, each kind counted
    // apart, see getRetryDelay. Network errors,
    // frequent in a browser (sleep, wifi, ...), are retried until it works.
    MAX_RETRY_COUNT = 3,
    MAX_RETRY_DELAY = 60000,
    // An image costs about this many characters of context, whatever the
    // size of its base64 data URI.
    IMAGE_ESTIMATE_CHARS = 4800,
    // Error messages of the servers (in a 4xx response) when the prompt is
    // larger than the context window.
    CONTEXT_OVERFLOW_PATTERN = /context[_ ]length|context (?:size|window)|prompt (?:is )?too long|too many tokens|token limit exceeded/i,
    // Errors sent inside the stream, which have no HTTP status, that may
    // succeed later.
    RETRYABLE_ERROR_PATTERN = /overloaded|rate.?limit|too many requests|unavailable|server.?error|internal.?error|provider returned error/i,
    NON_RETRYABLE_ERROR_PATTERN = /insufficient_quota|quota exceeded|billing/i,
    MAX_LOOP_COUNT = 500,
    ENVIRONMENT_SYSTEM_PROMPT = "This agent runs entirely inside a web browser tab, not on a server or a " +
      "local machine. There is no local filesystem, no shell, and no OS process to invoke - paths like " +
      "\"/home/...\" and commands like \"ls\", \"cat\" or \"pip install\" do not exist here, and any " +
      "attempt to use them will fail. The only capabilities available are the tools explicitly provided " +
      "in this conversation: a sandboxed JavaScript/WASM execution environment (itself with no " +
      "filesystem or network access), http_request for making network calls, " +
      "define_tool for creating (and listing, removing) new callable tools out of JS code, " +
      "spawn_subagent for delegating sub-tasks, read_tool_output for reading a tool output that was " +
      "too large to return whole, whatever MCP tools are configured, and - only when the " +
      "user asks for it - execution_plan for a checklist. Do not assume access to anything beyond these. " +
      "The history of this conversation has only the posts of the user and the text of your answers: " +
      "the tool calls of your earlier answers and their results are not repeated in it. The text of an " +
      "earlier answer is a faithful record of what its tools returned - do not take it for made up. " +
      "When a tool returns values the user may ask about later (ids, numbers, URLs), write them in " +
      "your answer, since its text is all that the next turns keep.",
    TURN_LIMIT_PROMPT = "Turn limit reached: you can not call tools anymore. Give your final answer " +
      "now, with what you found so far, and say clearly what you could not find or verify.",
    CONTEXT_SUMMARY_PREFIX = "[context summary]\n",
    SUMMARY_TOOL_RESULT_MAX_CHARS = 2000,
    SUMMARY_FORMAT = "## Goal\n[What is the user trying to accomplish?]\n\n" +
      "## Constraints & Preferences\n- [Any constraints or requirements mentioned by the user, or \"(none)\"]\n\n" +
      "## Progress\n### Done\n- [Completed steps]\n\n### In Progress\n- [Current work]\n\n### Blocked\n- [Issues preventing progress, if any]\n\n" +
      "## Key Decisions\n- [Decision]: [Brief rationale]\n\n" +
      "## Next Steps\n1. [Ordered list of what should happen next]\n\n" +
      "## Critical Context\n- [Any data, identifiers, or exact values needed to continue, or \"(none)\"]\n\n" +
      "Keep each section concise. Preserve exact names, numbers, and error messages.",
    SUMMARIZATION_PROMPT = "The text above is a conversation to summarize. Create a structured context " +
      "checkpoint that another instance of this agent will use to continue the task. Use this EXACT format:\n\n" +
      SUMMARY_FORMAT,
    // Used when an earlier compaction already produced a summary: merge the
    // new messages into it instead of summarizing the summary again, which
    // would lose a little more detail at every compaction.
    UPDATE_SUMMARIZATION_PROMPT = "The text above contains NEW conversation messages to incorporate into " +
      "the existing summary provided in <previous-summary> tags. Update that summary: keep everything " +
      "from it that is still relevant, move finished work to Done, and add new progress, decisions and " +
      "context. Use this EXACT format:\n\n" + SUMMARY_FORMAT;

  function isContextOverflowError(e) {
    if (!e || !e.status) {
      return false;
    }
    return e.status === 413 || (e.status >= 400 && e.status < 500 && e.status !== 429 &&
      CONTEXT_OVERFLOW_PATTERN.test(e.message));
  }

  // Rate limits and server side failures that may succeed later, but not
  // an exhausted quota or billing problem.
  function isTransientServerError(e) {
    if (!e || !e.message || NON_RETRYABLE_ERROR_PATTERN.test(e.message)) {
      return false;
    }
    return e.status === 429 || e.status >= 500 || (!e.status && RETRYABLE_ERROR_PATTERN.test(e.message));
  }

  // What the server asked with Retry-After (at most 2 minutes), otherwise
  // 2s doubled at each attempt, at most MAX_RETRY_DELAY.
  function getRetryDelay(e, retry_count) {
    if (e && e.retry_after_ms > 0) {
      return Math.min(e.retry_after_ms, 120000);
    }
    return Math.min(2000 * Math.pow(2, retry_count), MAX_RETRY_DELAY);
  }

  function isEmptyResponseError(e) {
    return Boolean(e && e.message && (/^Empty response from LLM/).test(e.message));
  }

  function isNetworkError(e) {
    return Boolean(e && e.message &&
      (/failed to fetch|network\s*error|load failed|connection was lost/i).test(e.message));
  }

  function truncateForSummary(text, max_chars) {
    if (text.length <= max_chars) {
      return text;
    }
    return text.slice(0, max_chars) + "\n[... " + (text.length - max_chars) + " more characters truncated]";
  }

  function estimateTokensForMessages(message_list) {
    var image_count = 0,
      text = JSON.stringify(message_list, function (key, value) {
        // A base64 image counts as IMAGE_ESTIMATE_CHARS, not as its length.
        if (value && value.type === "image_url" && value.image_url) {
          image_count += 1;
          return null;
        }
        return value;
      });
    return Math.ceil((text.length + image_count * IMAGE_ESTIMATE_CHARS) / CHARS_PER_TOKEN);
  }

  function messageContentToText(content) {
    if (typeof content === "string" || !content) {
      return content || "";
    }
    return content.map(function (part) {
      return part.type === "text" ? part.text : "[image attachment]";
    }).join("\n");
  }

  function serializeMessageListForSummary(message_list) {
    return message_list.map(function (message) {
      if (message.role === "assistant" && message.tool_calls && message.tool_calls.length) {
        return "Assistant: " + messageContentToText(message.content) + "\n" + message.tool_calls.map(function (tool_call) {
          return "  calls " + tool_call.function.name + "(" + (tool_call.function.arguments || "") + ")";
        }).join("\n");
      }
      if (message.role === "tool") {
        return "Tool result [" + message.name + "]: " +
          truncateForSummary(messageContentToText(message.content), SUMMARY_TOOL_RESULT_MAX_CHARS);
      }
      return message.role + ": " + messageContentToText(message.content);
    }).join("\n\n");
  }

  function estimateContextTokens(last_usage_anchor, message_list) {
    if (last_usage_anchor && last_usage_anchor.message_count <= message_list.length) {
      return last_usage_anchor.prompt_tokens + estimateTokensForMessages(message_list.slice(last_usage_anchor.message_count));
    }
    return estimateTokensForMessages(message_list);
  }

  function joinAnswerText(answer_text_list, current_text) {
    return (answer_text_list || []).concat(current_text ? [current_text] : []).join("\n\n");
  }

  rJS(window)
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    .declareAcquiredMethod("requestProcessTask", "requestProcessTask")
    .declareAcquiredMethod("storeTaskResult", "storeTaskResult")
    .declareAcquiredMethod("getModelContextWindow", "getModelContextWindow")

    .declareMethod('render', function (options) {
      var gadget = this;
      gadget.options = options;
      gadget.jio_key = options.jio_key;
      return new RSVP.Queue(RSVP.all([
          gadget.getDeclaredGadget('tool_manager'),
          gadget.getDeclaredGadget('skill_manager')
        ]))
        .push(function (manager_list) {
          gadget.tool_manager = manager_list[0];
          gadget.skill_manager = manager_list[1];
          return RSVP.all([
            gadget.tool_manager.render(options),
            gadget.skill_manager.render(options)
          ]);
        })
        .push(function () {
          return gadget.getDeclaredGadget("gadget_chat_ui");
        })
        .push(function (gadget_chat_ui) {
          gadget.gadget_chat_ui = gadget_chat_ui;
          return gadget_chat_ui.render(Object.assign({}, options, {enable_cancel: true, enable_queue: true}));
        })
        .push(function () {
          if (options.chat_state === 'started') {
            return gadget.processTask(MAX_LOOP_COUNT);
          }
        });
    })
    .allowPublicAcquisition('getSkillByName', function (argument_list) {
      return this.skill_manager.getSkillByName(argument_list[0]);
    })
    .allowPublicAcquisition('compactMessageList', function (argument_list) {
      return this.compactMessageList.apply(argument_list[0], [argument_list[1], argument_list[2], argument_list[3]])
    })
    .allowPublicAcquisition('notifyCommentPosted', function () {
      return this.processTask(MAX_LOOP_COUNT);
    })
    .allowPublicAcquisition('notifyCancelRequested', function () {
      return this.cancelProcessing();
    })
    .declareMethod('cancelProcessing', function () {
      var gadget = this,
        queue_loop = gadget.processing_queue,
        execution_plan,
        content;
      if (!queue_loop) {
        return;
      }
      gadget.processing_queue = null;
      queue_loop.cancel("Cancelled by user");

      execution_plan = gadget.execution_plan;
      gadget.execution_plan = null;
      // Keep what the model already wrote, including the turn it was
      // streaming when the user cancelled.
      content = joinAnswerText(gadget.answer_text_list, gadget.streaming_text);
      // Only show in the tool call trace only
      gadget.tool_message_list.push({
        role: "tool",
        name: "cancelled",
        content: "Cancelled by user"
      });

      return new RSVP.Queue(RSVP.all([
        gadget.gadget_chat_ui.showMessage({ content: content, reasoning: "", tool_message_list: gadget.tool_message_list, execution_plan: execution_plan }),
        gadget.storeTaskResult(
          gadget.options.jio_key,
          {
            tool_message_list: JSON.stringify(gadget.tool_message_list),
            content: content,
            execution_plan: execution_plan ? JSON.stringify(execution_plan) : ""
          }
        )
      ]))
        .push(function () {
          return gadget.gadget_chat_ui.cancelProcessing();
        })
        .push(function () {
          return gadget.notifySubmitted({message: 'Cancelled', status: "success"});
        });
    })
    .declareMethod('compactMessageList', function (message_list, keep_recent_override, last_usage_anchor) {
      var gadget = this;
      return gadget.getModelContextWindow()
        .push(function (context_window) {
          var compact_token_budget = COMPACT_TOKEN_BUDGET,
            keep_recent_budget = KEEP_RECENT_TOKEN_BUDGET,
            summary_usage_totals = window.ChatToolCommon.createUsageTotals(),
            leading_system_count = 0,
            cut_index,
            recent_token_count = 0,
            leading_system_message_list,
            old_message_list,
            recent_message_list,
            previous_summary = null;
          if (context_window) {
            compact_token_budget = context_window - Math.min(CONTEXT_RESERVE_TOKENS, Math.floor(context_window / 4));
            keep_recent_budget = Math.min(KEEP_RECENT_TOKEN_BUDGET, Math.floor(compact_token_budget * 0.35));
          }
          if (keep_recent_override) {
            keep_recent_budget = keep_recent_override;
            compact_token_budget = 0;
          }
          if (estimateContextTokens(last_usage_anchor, message_list) < compact_token_budget) {
            return { message_list: message_list, usage_totals: summary_usage_totals };
          }
          while (leading_system_count < message_list.length &&
              message_list[leading_system_count].role === "system") {
            leading_system_count += 1;
          }

          cut_index = message_list.length;
          while (cut_index > leading_system_count && recent_token_count < keep_recent_budget) {
            cut_index -= 1;
            recent_token_count += estimateTokensForMessages([message_list[cut_index]]);
          }
          while (cut_index > leading_system_count &&
              message_list[cut_index].role === "tool") {
            cut_index -= 1;
          }
          leading_system_message_list = message_list.slice(0, leading_system_count);
          old_message_list = message_list.slice(leading_system_count, cut_index);
          recent_message_list = message_list.slice(cut_index);

          if (old_message_list.length && old_message_list[0].role === "user" &&
              typeof old_message_list[0].content === "string" &&
              old_message_list[0].content.indexOf(CONTEXT_SUMMARY_PREFIX) === 0) {
            previous_summary = old_message_list[0].content.slice(CONTEXT_SUMMARY_PREFIX.length);
            old_message_list = old_message_list.slice(1);
          }
          if (!old_message_list.length) {
            return { message_list: message_list, usage_totals: summary_usage_totals };
          }

          if (gadget.tool_message_list) {
            gadget.tool_message_list.push({
              role: "tool",
              name: "compact_history",
              content: "Conversation getting long - summarizing " + old_message_list.length +
                " older message(s) to free up context..."
            });
          }
          return new RSVP.Queue()
            .push(function () {
              return gadget.gadget_chat_ui && gadget.gadget_chat_ui.showMessage({
                tool_message_list: gadget.tool_message_list,
                execution_plan: gadget.execution_plan
              });
            })
            .push(function () {
              return gadget.requestProcessTask(
                gadget.jio_key,
                {
                  message_list: JSON.stringify([
                    { role: "system", content: previous_summary !== null ? UPDATE_SUMMARIZATION_PROMPT : SUMMARIZATION_PROMPT },
                    { role: "user", content: (previous_summary !== null ?
                        "<previous-summary>\n" + previous_summary + "\n</previous-summary>\n\n" : "") +
                      "<conversation>\n" + serializeMessageListForSummary(old_message_list) + "\n</conversation>" }
                  ]),
                  tool_definition_list: JSON.stringify([]),
                  is_background: "1"
                }
              );
            })
            .push(function (result) {
              if (result.usage) {
                summary_usage_totals = result.usage;
              }
              if (!result.content) {
                throw new Error("compactMessageList: empty summary");
              }

              if (result.finish_reason === "length") {
                throw new Error("compactMessageList: summary truncated");
              }
              return {
                message_list: leading_system_message_list.concat([{
                  role: "user",
                  content: CONTEXT_SUMMARY_PREFIX + result.content
                }], recent_message_list),
                usage_totals: summary_usage_totals
              };
            })
            .push(undefined, function (e) {
              // Keep going with the full history, but say so: the next request
              // may then overflow the context.
              if (gadget.tool_message_list) {
                gadget.tool_message_list.push({
                  role: "tool",
                  name: "compact_history",
                  content: "Summarizing the older messages failed (" + (e && e.message ? e.message : String(e)) +
                    ") - continuing with the full history."
                });
              }
              return { message_list: message_list, usage_totals: summary_usage_totals };
            });
        });
    })
    .declareMethod('getSystemPromptList', function () {
      var gadget = this;
      return new RSVP.Queue(RSVP.all([
        gadget.tool_manager.getToolPromptList(),
        gadget.skill_manager.formatSkillListForPrompt()
      ]))
        .push(function (result_list) {
          var system_message_list = [{ role: "system", content: ENVIRONMENT_SYSTEM_PROMPT }].concat(result_list[0]);
          if (result_list[1]) {
            system_message_list.push({ role: "system", content: result_list[1] });
          }
          return system_message_list;
        });
    })
    .allowPublicAcquisition('getSystemPromptList', function () {
      return this.getSystemPromptList();
    })
    .declareMethod('showStreamingDelta', function (partial) {
      var gadget = this;
      gadget.streaming_text = partial.content;
      return gadget.gadget_chat_ui.showMessage({
        content: joinAnswerText(gadget.answer_text_list, partial.content),
        reasoning: partial.reasoning,
        streaming: true,
        tool_message_list: gadget.tool_message_list || [],
        execution_plan: gadget.execution_plan
      });
    })
    .declareJob('processTask', function (max_loop_count) {
      var gadget = this,
        queue_loop = new RSVP.Queue(),
        // Usage of this task: its LLM calls, compactions, tool output
        // summaries and sub-agents.
        usage_totals = window.ChatToolCommon.createUsageTotals(),
        // The prompt_tokens reported by the server for the first
        // message_count messages of the last request, to estimate the
        // context size more precisely than from the characters only.
        last_usage_anchor = null;
      gadget.tool_message_list = [];
      // use for all the llm answer
      gadget.answer_text_list = [];
      gadget.streaming_text = "";
      gadget.processing_queue = queue_loop;

      function loopError(e) {
        var content = joinAnswerText(gadget.answer_text_list, ""),
          execution_plan = gadget.execution_plan,
          message = e && e.message ? e.message : String(e),
          stack = e && e.stack ? String(e.stack) : "";
        gadget.processing_queue = null;
        gadget.execution_plan = null;
        // only put inside the trace, to not send back to llm
        gadget.tool_message_list.push({
          role: "tool",
          name: "error",
          content: "Error: " + (stack.indexOf(message) !== -1 ? stack :
              message + (stack ? "\n\n" + stack : ""))
        });
        return new RSVP.Queue(RSVP.all([
          gadget.gadget_chat_ui.showMessage({ content: content, reasoning: "", tool_message_list: gadget.tool_message_list, execution_plan: execution_plan }),
          gadget.storeTaskResult(
            gadget.options.jio_key,
            {
              tool_message_list: JSON.stringify(gadget.tool_message_list),
              content: content,
              execution_plan: execution_plan ? JSON.stringify(execution_plan) : ""
            }
          )
        ]))
          .push(function () {
            // Unlike on cancel, the queued posts are kept, but not sent.
            return gadget.gadget_chat_ui.stopProcessing();
          })
          .push(function () {
            // Only once the processing is stopped, like on cancel.
            return gadget.notifySubmitted({message: 'Error', status: "error"});
          });
      }

      // reasoning: the reasoning of the final answer, kept in the trace like
      // the one of the turns with tool calls.
      function completeTask(final_content, reasoning) {
        var execution_plan = gadget.execution_plan,
          content = joinAnswerText(gadget.answer_text_list, final_content);
        if (reasoning) {
          gadget.tool_message_list.push({
            role: "assistant",
            content: "",
            reasoning: reasoning
          });
        }
        gadget.tool_message_list.push({
          role: "tool",
          name: "usage_totals",
          content: "Task usage: " + usage_totals.call_count + " LLM call(s), " +
            usage_totals.prompt_tokens + " prompt + " + usage_totals.completion_tokens +
            " completion = " + usage_totals.total_tokens + " token(s) total."
        });
        return new RSVP.Queue(RSVP.all([
          gadget.gadget_chat_ui.showMessage({ content: content, reasoning: "", tool_message_list: gadget.tool_message_list, execution_plan: execution_plan }),
          gadget.storeTaskResult(
            gadget.options.jio_key,
            {
              tool_message_list: JSON.stringify(gadget.tool_message_list),
              content: content,
              execution_plan: execution_plan ? JSON.stringify(execution_plan) : ""
            }
          )
        ]))
          .push(function () {
            return gadget.gadget_chat_ui.stopProcessing();
          })
          .push(function (queued_message_list) {
            gadget.execution_plan = null;
            if (queued_message_list.length) {
              return gadget.processTask(max_loop_count);
            }
            return gadget.notifySubmitted({message: 'Completed', status: "success"});
          });
      }

      function loop_call(loop_count, message_list, pending_result, retry_count_dict) {
        var has_tool_call = Boolean(
            pending_result && pending_result.tool_calls && pending_result.tool_calls.length
          );

        // report what it found, instead of losing all of its work.
        if (loop_count >= max_loop_count) {
          queue_loop
            .push(function () {
              if (has_tool_call) {
                return gadget.tool_manager.runToolCallList(pending_result.tool_calls, message_list, {
                  turn_limit_reached: true
                });
              }
            })
            .push(function (tool_round) {
              if (tool_round) {
                message_list = message_list.concat(tool_round.message_list);
              }
              gadget.tool_message_list.push({
                role: "tool",
                name: "turn_limit",
                content: "Turn limit of " + max_loop_count + " reached - asking the model for a final answer without tools"
              });
              return gadget.gadget_chat_ui.showMessage({
                tool_message_list: gadget.tool_message_list,
                execution_plan: gadget.execution_plan
              })
                .push(function () {
                  return gadget.compactMessageList(message_list.concat([
                    { role: "user", content: TURN_LIMIT_PROMPT }
                  ]), undefined, last_usage_anchor);
                });
            })
            .push(function (compacted) {
              window.ChatToolCommon.addUsageTotals(usage_totals, compacted.usage_totals);
              return gadget.requestProcessTask(
                gadget.jio_key,
                {
                  message_list: JSON.stringify(compacted.message_list),
                  tool_definition_list: JSON.stringify([])
                }
              );
            })
            .push(function (result) {
              window.ChatToolCommon.addUsageTotals(usage_totals, result.usage);
              if (!result.content) {
                throw new Error("processTask: too many iterations");
              }
              return completeTask("[turn limit reached - partial answer]\n" + result.content, result.reasoning);
            })
            .push(undefined, loopError);
          return;
        }

        if (has_tool_call) {
          queue_loop
            .push(function () {
              return gadget.tool_manager.runToolCallList(pending_result.tool_calls, message_list, {
                finish_reason: pending_result.finish_reason
              });
            })
            .push(function (tool_round) {
              var i, client_tool_result;
              for (i = 0; i < tool_round.result_list.length; i += 1) {
                client_tool_result = tool_round.result_list[i];
                // The tool message sent to the model, with the trace of a
                // sub-agent for the page.
                gadget.tool_message_list.push({
                  role: "tool",
                  tool_call_id: client_tool_result.tool_call_id,
                  name: client_tool_result.name,
                  content: client_tool_result.content,
                  sub_message_list: client_tool_result.message_list
                });
                if (client_tool_result.execution_plan !== undefined) {
                  gadget.execution_plan = client_tool_result.execution_plan;
                }
                window.ChatToolCommon.addUsageTotals(usage_totals, client_tool_result.usage_totals);
              }
              return gadget.gadget_chat_ui.showMessage({tool_message_list: gadget.tool_message_list, execution_plan: gadget.execution_plan })
                .push(function () {
                  return loop_call(
                    loop_count + 1,
                    message_list.concat(tool_round.message_list),
                    null,
                    {}
                  );
                });
            })
            .push(undefined, loopError);
          return;
        }

        queue_loop
          .push(function () {
            return gadget.gadget_chat_ui.flushQueuedPostList();
          })
          .push(function (queued_message_list) {
            message_list = message_list.concat(queued_message_list);
            return gadget.compactMessageList(message_list, undefined, last_usage_anchor);
          })
          .push(function (compacted) {
            window.ChatToolCommon.addUsageTotals(usage_totals, compacted.usage_totals);
            // The anchor counted the messages that were just summarized.
            if (compacted.message_list !== message_list) {
              last_usage_anchor = null;
            }
            message_list = compacted.message_list;
            return gadget.tool_manager.getToolDefinitionList(message_list);
          })
          .push(function (tool_definition_list) {
            return gadget.requestProcessTask(
              gadget.jio_key,
              {
                message_list: JSON.stringify(message_list),
                tool_definition_list: JSON.stringify(tool_definition_list)
              }
            );
          })
          .push(function (result) {
            window.ChatToolCommon.addUsageTotals(usage_totals, result.usage);
            gadget.streaming_text = "";
            if (result.usage && result.usage.prompt_tokens) {
              last_usage_anchor = { prompt_tokens: result.usage.prompt_tokens, message_count: message_list.length };
            }
            if (result.tool_calls && result.tool_calls.length) {
              // The trace holds the messages of the model, like the one of
              // the server side harness (ArtificialTask_runHarnessAgent):
              // the tool calls with their arguments, then their results.
              // Its tool messages without tool_call_id are notes of the
              // agent (retries, compaction, usage...), not sent to the model.
              gadget.tool_message_list.push({
                role: "assistant",
                content: result.content,
                tool_calls: result.tool_calls,
                reasoning: result.reasoning
              });
              if (result.content && result.content.trim()) {
                gadget.answer_text_list.push(result.content.trim());
              }
              // The reasoning of this turn is now in the trace, with its
              // tool calls.
              return gadget.gadget_chat_ui.showMessage({reasoning: "", tool_message_list: gadget.tool_message_list, execution_plan: gadget.execution_plan })
                .push(function () {
                  return loop_call(
                    loop_count + 1,
                    message_list.concat([result.message]),
                    result,
                    {}
                  );
                });
            }
            if (!result.content) {
              throw new Error("Empty response from LLM with no tool calls" +
                (result.finish_reason ? " (finish_reason: " + result.finish_reason + ")" : ""));
            }
            return completeTask(result.content, result.reasoning);
          })
          .push(undefined, function (e) {
            var retry_name,
              retry_reason = "",
              retry_count,
              delay;
            if (isContextOverflowError(e)) {
              retry_name = "context_overflow_retry";
            } else if (isTransientServerError(e)) {
              retry_name = "rate_limit_retry";
            } else if (isEmptyResponseError(e)) {
              retry_name = "empty_response_retry";
            } else if (isNetworkError(e)) {
              retry_name = "network_error_retry";
              retry_reason = " (the connection to the LLM server failed)";
            } else {
              return loopError(e);
            }
            // Counted by kind of error: network errors are not limited.
            retry_count_dict = retry_count_dict || {};
            retry_count = retry_count_dict[retry_name] || 0;
            if (retry_name !== "network_error_retry" && retry_count >= MAX_RETRY_COUNT) {
              return loopError(e);
            }
            retry_count_dict[retry_name] = retry_count + 1;
            if (retry_name === "context_overflow_retry") {
              gadget.tool_message_list.push({
                role: "tool",
                name: retry_name,
                content: e.message + " - the proactive estimate missed this, compacting harder and retrying"
              });
              return gadget.gadget_chat_ui.showMessage({
                tool_message_list: gadget.tool_message_list,
                execution_plan: gadget.execution_plan
              })
                .push(function () {
                  return gadget.compactMessageList(message_list, PANIC_KEEP_RECENT_TOKEN_BUDGET);
                })
                .push(function (compacted) {
                  window.ChatToolCommon.addUsageTotals(usage_totals, compacted.usage_totals);
                  // Nothing left to compact: retrying would fail the same way.
                  if (compacted.message_list.length >= message_list.length) {
                    throw e;
                  }
                  last_usage_anchor = null;
                  return loop_call(loop_count, compacted.message_list, pending_result, retry_count_dict);
                });
            }
            delay = getRetryDelay(e, retry_count);
            gadget.tool_message_list.push({
              role: "tool",
              name: retry_name,
              content: e.message + retry_reason + " - retry " + (retry_count + 1) +
                (retry_name === "network_error_retry" ? "" : " of " + MAX_RETRY_COUNT) +
                " in " + Math.round(delay / 1000) + "s"
            });
            return gadget.gadget_chat_ui.showMessage({
              tool_message_list: gadget.tool_message_list,
              execution_plan: gadget.execution_plan
            })
              .push(function () {
                return RSVP.delay(delay);
              })
              .push(function () {
                return loop_call(loop_count, message_list, pending_result, retry_count_dict);
              });
          });
      }

      queue_loop
        .push(function () {
          return gadget.gadget_chat_ui.startProcessing();
        })
        .push(function () {
          return gadget.tool_manager.getMcpUnavailableList();
        })
        .push(function (mcp_unavailable_list) {
          // Shown in the trace, so that the user knows why MCP tools are
          // missing.
          mcp_unavailable_list.forEach(function (content) {
            gadget.tool_message_list.push({ role: "tool", name: "mcp_unavailable", content: content });
          });
        })
        .push(function () {
          return gadget.notifySubmitted({message: 'Processing', status: "success"});
        })
        .push(function () {
          return gadget.gadget_chat_ui.getMessageList();
        })
        .push(function (message_list) {
          return gadget.getSystemPromptList()
            .push(function (system_message_list) {
              return loop_call(0, system_message_list.concat(message_list));
            });
        });
      return queue_loop;
    });
}(window, rJS, RSVP));
