/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  var CHARS_PER_TOKEN = 3.5,
    COMPACT_TOKEN_BUDGET = 80000,
    KEEP_RECENT_TOKEN_BUDGET = 28000,
    CONTEXT_RESERVE_TOKENS = 16384,
    PANIC_KEEP_RECENT_TOKEN_BUDGET = 8000,
    RATE_LIMIT_RETRY_DELAY_MS = 120000,
    MAX_LOOP_COUNT = 500,
    TURN_LIMIT_PROMPT = "Turn limit reached: you can not call tools anymore. Give your final answer " +
      "now, with what you found so far, and say clearly what you could not find or verify.",
    SUMMARY_CHUNK_CHARS = 100000,
    SUMMARY_PROMPT = "The text below is one chunk of a larger tool result that was too large to return " +
      "as-is. Summarize it concisely, but preserve exact facts, numbers, names, dates, code, and any " +
      "other concrete detail that may be needed later - this summary is the ONLY part of this chunk " +
      "that will remain visible; anything you omit is permanently lost to the rest of this conversation.",
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

  function isRateLimitError(e) {
    return Boolean(e && e.message && (/^LLM 429 /).test(e.message));
  }

  function isContextOverflowError(e) {
    return Boolean(e && e.message && (/^LLM 400 /).test(e.message) &&
      (/exceeds the available context size/i).test(e.message));
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
    return Math.ceil(JSON.stringify(message_list).length / CHARS_PER_TOKEN);
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

  // Summarizes the older part of message_list once it is estimated above
  // compact_token_budget, keeping roughly keep_recent_budget tokens as-is.
  function compactWithBudget(gadget, message_list, keep_recent_budget, compact_token_budget, last_usage_anchor) {
    var leading_system_count = 0,
      cut_index,
      recent_token_count = 0,
      leading_system_message_list,
      old_message_list,
      recent_message_list,
      previous_summary = null;
    if (estimateContextTokens(last_usage_anchor, message_list) < compact_token_budget) {
      return message_list;
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
      return message_list;
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
        return gadget.requestProcessTaskWithUsage(
          gadget,
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
        if (!result.content) {
          throw new Error("compactMessageList: empty summary");
        }
        // A summary cut off by the output token limit is incomplete -
        // keep the full history rather than lose its missing part.
        if (result.finish_reason === "length") {
          throw new Error("compactMessageList: summary truncated");
        }
        return leading_system_message_list.concat([{
          role: "user",
          content: CONTEXT_SUMMARY_PREFIX + result.content
        }], recent_message_list);
      })
      .push(undefined, function () {
        return message_list;
      });
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
      gadget.execution_plan = null;
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
          return gadget_chat_ui.render(Object.assign({}, options, {enable_cancel: true}));
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
      return this.compactMessageList.apply(this, argument_list);
    })
    .allowPublicAcquisition('summarizeToolOutput', function (argument_list) {
      return this.summarizeToolOutput.apply(argument_list[0], argument_list);
    })
    .declareMethod('requestProcessTaskWithUsage', function (gadget, document_id, request_options) {
      return gadget.requestProcessTask(document_id, request_options)
        .push(function (result) {
          var usage = result.usage;
          if (usage && gadget.usage_totals) {
            gadget.usage_totals.call_count += 1;
            gadget.usage_totals.prompt_tokens += usage.prompt_tokens || 0;
            gadget.usage_totals.completion_tokens += usage.completion_tokens || 0;
            gadget.usage_totals.total_tokens += usage.total_tokens || ((usage.prompt_tokens || 0) + (usage.completion_tokens || 0));
          }
          return result;
        });
    })
    .allowPublicAcquisition('requestProcessTaskWithUsage', function (argument_list) {
      return this.requestProcessTaskWithUsage.apply(argument_list[0], argument_list);
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
      // Shown in the tool call trace only: the answer itself goes back to the
      // model as its own message in the next requests.
      gadget.tool_message_list.push({
        role: "tool",
        name: "cancelled",
        content: "Cancelled by user"
      });

      return RSVP.all([
        gadget.gadget_chat_ui.showMessage({ content: content, tool_message_list: gadget.tool_message_list, execution_plan: execution_plan }),
        gadget.notifySubmitted({message: 'Cancelled', status: "success"}),
        gadget.gadget_chat_ui.resetEditor(),
        gadget.storeTaskResult(
          gadget.options.jio_key,
          {
            tool_message_list: JSON.stringify(gadget.tool_message_list),
            content: content,
            execution_plan: execution_plan ? JSON.stringify(execution_plan) : ""
          }
        )
      ]);
    })
    .declareMethod('compactMessageList', function (gadget, message_list, keep_recent_override, last_usage_anchor) {
      var agent = this;
      return new RSVP.Queue(agent.getModelContextWindow())
        .push(function (context_window) {
          var compact_token_budget = COMPACT_TOKEN_BUDGET,
            keep_recent_budget = KEEP_RECENT_TOKEN_BUDGET;
          // Compact once the context gets within CONTEXT_RESERVE_TOKENS of the
          // model's real context window (kept for the reply and tool
          // definitions), like ~/pi does. When the server does not report the
          // window size, keep the fixed budgets.
          if (context_window) {
            compact_token_budget = context_window - Math.min(CONTEXT_RESERVE_TOKENS, Math.floor(context_window / 4));
            keep_recent_budget = Math.min(KEEP_RECENT_TOKEN_BUDGET, Math.floor(compact_token_budget * 0.35));
          }
          // An explicit keep_recent_override (context overflow retry) always compacts.
          return compactWithBudget(
            gadget,
            message_list,
            keep_recent_override || keep_recent_budget,
            keep_recent_override ? 0 : compact_token_budget,
            last_usage_anchor
          );
        });
    })
    .declareMethod('summarizeToolOutput', function (gadget, content) {
      var text = typeof content === "string" ? content : JSON.stringify(content),
        chunk_list = [],
        start,
        queue = new RSVP.Queue(),
        summary_list = [];
      if (text.length <= SUMMARY_CHUNK_CHARS) {
        return text;
      }
      for (start = 0; start < text.length; start += SUMMARY_CHUNK_CHARS) {
        chunk_list.push(text.slice(start, start + SUMMARY_CHUNK_CHARS));
      }
      chunk_list.forEach(function (chunk, index) {
        queue
          .push(function () {
            if (gadget.tool_message_list) {
              gadget.tool_message_list.push({
                role: "tool",
                name: "summarize_tool_output",
                content: "Tool result too large to send as-is - summarizing part " + (index + 1) +
                  " of " + chunk_list.length + "..."
              });
            }
            return gadget.gadget_chat_ui && gadget.gadget_chat_ui.showMessage({
              tool_message_list: gadget.tool_message_list,
              execution_plan: gadget.execution_plan
            });
          })
          .push(function () {
            return gadget.requestProcessTaskWithUsage(
              gadget,
              gadget.jio_key,
              {
                message_list: JSON.stringify([
                  { role: "system", content: SUMMARY_PROMPT },
                  { role: "user", content: "Chunk " + (index + 1) + " of " + chunk_list.length + ":\n\n" + chunk }
                ]),
                tool_definition_list: JSON.stringify([]),
                is_background: "1"
              }
            );
          })
          .push(function (result) {
            var summary_text;
            summary_text = "[Summary of chunk " + (index + 1) + " of " + chunk_list.length +
              " of a truncated tool output]\n" + (result.content || "(empty summary)");
            summary_list.push(summary_text);
            if (gadget.tool_message_list) {
              gadget.tool_message_list.push({
                role: "tool",
                name: "summarize_tool_output_result",
                content: summary_text
              });
            }
            return gadget.gadget_chat_ui && gadget.gadget_chat_ui.showMessage({
              tool_message_list: gadget.tool_message_list,
              execution_plan: gadget.execution_plan
            });
          });
      });
      return queue.push(function () {
        return summary_list.join("\n\n");
      });
    })
    .declareMethod('showStreamingDelta', function (partial) {
      var gadget = this;
      gadget.streaming_text = partial.content;
      return gadget.gadget_chat_ui.showMessage({
        content: joinAnswerText(gadget.answer_text_list, partial.content),
        tool_message_list: gadget.tool_message_list || [],
        execution_plan: gadget.execution_plan
      });
    })
    .declareJob('processTask', function (max_loop_count) {
      var gadget = this,
        queue_loop = new RSVP.Queue();
      gadget.tool_message_list = [];
      // Text the model wrote in the turns that called tools: it stays shown
      // above the text of the next turns, and is part of the final answer.
      gadget.answer_text_list = [];
      gadget.streaming_text = "";
      gadget.processing_queue = queue_loop;
      gadget.last_usage_anchor = null;
      gadget.usage_totals = { call_count: 0, prompt_tokens: 0, completion_tokens: 0, total_tokens: 0 };

      function loop_call(loop_count, message_list, pending_tool_call_list, is_retry) {
        var has_tool_call = Boolean(
            pending_tool_call_list && pending_tool_call_list.length
          );

        function loopError(e) {
          var error_text = joinAnswerText(gadget.answer_text_list,
              "Error: " + (e && e.message ? e.message : String(e))),
            execution_plan = gadget.execution_plan;
          gadget.processing_queue = null;
          gadget.execution_plan = null;
          return RSVP.all([
            gadget.gadget_chat_ui.showMessage({ content: error_text, tool_message_list: gadget.tool_message_list, execution_plan: execution_plan }),
            gadget.notifySubmitted({message: 'Error', status: "error"}),
            gadget.gadget_chat_ui.resetEditor(),
            gadget.storeTaskResult(
              gadget.options.jio_key,
              {
                tool_message_list: JSON.stringify(gadget.tool_message_list),
                content: error_text,
                execution_plan: execution_plan ? JSON.stringify(execution_plan) : ""
              }
            )
          ]);
        }

        function completeTask(final_content) {
          var execution_plan = gadget.execution_plan,
            content = joinAnswerText(gadget.answer_text_list, final_content);
          gadget.processing_queue = null;
          gadget.execution_plan = null;
          gadget.tool_message_list.push({
            role: "tool",
            name: "usage_totals",
            content: "Task usage: " + gadget.usage_totals.call_count + " LLM call(s), " +
              gadget.usage_totals.prompt_tokens + " prompt + " + gadget.usage_totals.completion_tokens +
              " completion = " + gadget.usage_totals.total_tokens + " token(s) total."
          });
          return RSVP.all([
            gadget.gadget_chat_ui.showMessage({ content: content, tool_message_list: gadget.tool_message_list, execution_plan: execution_plan }),
            gadget.notifySubmitted({message: 'Completed', status: "success"}),
            gadget.gadget_chat_ui.resetEditor(),
            gadget.storeTaskResult(
              gadget.options.jio_key,
              {
                tool_message_list: JSON.stringify(gadget.tool_message_list),
                content: content,
                execution_plan: execution_plan ? JSON.stringify(execution_plan) : ""
              }
            )
          ]);
        }

        // At the limit, one last request without tools makes the model
        // report what it found, instead of losing all of its work.
        if (loop_count >= max_loop_count) {
          queue_loop
            .push(function () {
              var final_message_list = message_list;
              if (has_tool_call) {
                final_message_list = final_message_list.concat(pending_tool_call_list.map(function (tool_call) {
                  return {
                    role: "tool",
                    tool_call_id: tool_call.id,
                    name: tool_call.function.name,
                    content: "Not run: turn limit reached."
                  };
                }));
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
                  return gadget.compactMessageList(gadget, final_message_list.concat([
                    { role: "user", content: TURN_LIMIT_PROMPT }
                  ]), undefined, gadget.last_usage_anchor);
                });
            })
            .push(function (final_message_list) {
              return gadget.requestProcessTaskWithUsage(
                gadget,
                gadget.jio_key,
                {
                  message_list: JSON.stringify(final_message_list),
                  tool_definition_list: JSON.stringify([])
                }
              );
            })
            .push(function (result) {
              if (!result.content) {
                throw new Error("processTask: too many iterations");
              }
              return completeTask("[turn limit reached - partial answer]\n" + result.content);
            })
            .push(undefined, loopError);
          return;
        }

        if (has_tool_call) {
          queue_loop
            .push(function () {
              var i, tool_call;
              for (i = 0; i < pending_tool_call_list.length; i += 1) {
                tool_call = pending_tool_call_list[i];
                gadget.tool_message_list.push({
                  name: tool_call.function.name + " (call " + tool_call.id + ")",
                  content: 'args:' + (tool_call.function.arguments ? tool_call.function.arguments : ''),
                  'role': "tool"
                });
              }
              return gadget.gadget_chat_ui.showMessage({tool_message_list: gadget.tool_message_list, execution_plan: gadget.execution_plan });
            })
            .push(function () {
              return gadget.tool_manager.runToolCallList(pending_tool_call_list, message_list);
            })
            .push(function (client_tool_result_list) {
              var i, tool_call, client_tool_result;
              for (i = 0; i < pending_tool_call_list.length; i += 1) {
                tool_call = pending_tool_call_list[i];
                client_tool_result = client_tool_result_list[i];
                gadget.tool_message_list.push({
                  name: tool_call.function.name + " (result " + tool_call.id + ")",
                  content: 'result:' + client_tool_result.content,
                  sub_message_list: client_tool_result.message_list,
                  'role': "tool"
                });
                if (client_tool_result.execution_plan !== undefined) {
                  gadget.execution_plan = client_tool_result.execution_plan;
                }
                if (client_tool_result.usage_totals) {
                  gadget.usage_totals.call_count += client_tool_result.usage_totals.call_count;
                  gadget.usage_totals.prompt_tokens += client_tool_result.usage_totals.prompt_tokens;
                  gadget.usage_totals.completion_tokens += client_tool_result.usage_totals.completion_tokens;
                  gadget.usage_totals.total_tokens += client_tool_result.usage_totals.total_tokens;
                }
              }
              return gadget.gadget_chat_ui.showMessage({tool_message_list: gadget.tool_message_list, execution_plan: gadget.execution_plan })
                .push(function () {
                  return client_tool_result_list;
                });
            })
            .push(function (client_tool_result_list) {
              var summarize_queue = new RSVP.Queue(),
                summarized_content_list = [];
              client_tool_result_list.forEach(function (client_tool_result, i) {
                summarize_queue
                  .push(function () {
                    return gadget.summarizeToolOutput(gadget, client_tool_result.content);
                  })
                  .push(function (summarized_content) {
                    summarized_content_list[i] = summarized_content;
                  });
              });
              return summarize_queue.push(function () {
                var next_message_list = message_list, i, tool_call;
                for (i = 0; i < pending_tool_call_list.length; i += 1) {
                  tool_call = pending_tool_call_list[i];
                  next_message_list = next_message_list.concat([{
                    role: "tool",
                    tool_call_id: tool_call.id,
                    name: tool_call.function.name,
                    content: summarized_content_list[i]
                  }]);
                }
                return next_message_list;
              });
            })
            .push(function (next_message_list) {
              return loop_call(
                loop_count + 1,
                next_message_list,
                null,
                is_retry
              );
            })
            .push(undefined, loopError);
          return;
        }

        queue_loop
          .push(function () {
            return gadget.compactMessageList(gadget, message_list, undefined, gadget.last_usage_anchor);
          })
          .push(function (compacted_message_list) {
            var shrunk_by = message_list.length - compacted_message_list.length;
            if (gadget.last_usage_anchor) {
              gadget.last_usage_anchor.message_count = Math.max(0, gadget.last_usage_anchor.message_count - shrunk_by);
            }
            message_list = compacted_message_list;
            return gadget.tool_manager.getToolDefinitionList(message_list);
          })
          .push(function (tool_definition_list) {
            return gadget.requestProcessTaskWithUsage(
              gadget,
              gadget.jio_key,
              {
                message_list: JSON.stringify(message_list),
                tool_definition_list: JSON.stringify(tool_definition_list)
              }
            );
          })
          .push(function (result) {
            var assistant_message;
            gadget.streaming_text = "";
            if (result.usage && result.usage.prompt_tokens) {
              gadget.last_usage_anchor = { prompt_tokens: result.usage.prompt_tokens, message_count: message_list.length };
            }
            if (result.tool_calls && result.tool_calls.length) {
              gadget.tool_message_list.push({
                'role': 'assistant',
                'content': result.content,
                'reasoning': result.reasoning
              });
              if (result.content && result.content.trim()) {
                gadget.answer_text_list.push(result.content.trim());
              }
              assistant_message = {
                role: "assistant",
                content: result.content,
                tool_calls: result.tool_calls
              };
              // Send the reasoning back in the field the server used, so the
              // model still sees why it made the previous tool calls.
              if (result.reasoning && result.reasoning_field) {
                assistant_message[result.reasoning_field] = result.reasoning;
              }
              return gadget.gadget_chat_ui.showMessage({tool_message_list: gadget.tool_message_list, execution_plan: gadget.execution_plan })
                .push(function () {
                 return loop_call(
                   loop_count + 1,
                   message_list.concat([assistant_message]),
                  result.tool_calls,
                  is_retry
                );
              });
            }
            if (!result.content) {
              throw new Error("Empty response from LLM with no tool calls" +
                (result.finish_reason ? " (finish_reason: " + result.finish_reason + ")" : ""));
            }
            return completeTask(result.content);
          })
          .push(undefined, function (e) {
            if (!is_retry && isRateLimitError(e)) {
              gadget.tool_message_list.push({
                role: "tool",
                name: "rate_limit_retry",
                content: e.message + " - retrying once in " + (RATE_LIMIT_RETRY_DELAY_MS / 1000) + "s"
              });
              return gadget.gadget_chat_ui.showMessage({
                tool_message_list: gadget.tool_message_list,
                execution_plan: gadget.execution_plan
              })
                .push(function () {
                  return new RSVP.Queue(RSVP.delay(RATE_LIMIT_RETRY_DELAY_MS))
                    .push(function () {
                      return loop_call(loop_count, message_list, pending_tool_call_list, true);
                    });
                });
            }
            if (!is_retry && isContextOverflowError(e)) {
              gadget.tool_message_list.push({
                role: "tool",
                name: "context_overflow_retry",
                content: e.message + " - the proactive estimate missed this, compacting harder and retrying once"
              });
              return gadget.gadget_chat_ui.showMessage({
                tool_message_list: gadget.tool_message_list,
                execution_plan: gadget.execution_plan
              })
                .push(function () {
                  return gadget.compactMessageList(gadget, message_list, PANIC_KEEP_RECENT_TOKEN_BUDGET);
                })
                .push(function (compacted_message_list) {
                  if (compacted_message_list.length >= message_list.length) {
                    throw e;
                  }
                  return loop_call(loop_count, compacted_message_list, pending_tool_call_list, true);
                });
            }
            if (!is_retry && isEmptyResponseError(e)) {
              gadget.tool_message_list.push({
                role: "tool",
                name: "empty_response_retry",
                content: e.message + " - retrying once"
              });
              return gadget.gadget_chat_ui.showMessage({
                tool_message_list: gadget.tool_message_list,
                execution_plan: gadget.execution_plan
              })
                .push(function () {
                  return loop_call(loop_count, message_list, pending_tool_call_list, false);
                });
            }
            if (!is_retry && isNetworkError(e)) {
              gadget.tool_message_list.push({
                role: "tool",
                name: "network_error_retry",
                content: e.message + " - the connection to the LLM server dropped mid-request, retrying once"
              });
              return gadget.gadget_chat_ui.showMessage({
                tool_message_list: gadget.tool_message_list,
                execution_plan: gadget.execution_plan
              })
                .push(function () {
                  return loop_call(loop_count, message_list, pending_tool_call_list, false);
                });
            }
            return loopError(e);
          });
      }

      queue_loop
        .push(function () {
          return gadget.gadget_chat_ui.blockEditor();
        })
        .push(function () {
          return gadget.notifySubmitted({message: 'Processing', status: "success"});
        })
        .push(function () {
          return gadget.gadget_chat_ui.getMessageList();
        })
        .push(function (message_list) {
          return gadget.gadget_chat_ui.showMessage({})
            .push(function () {
              return message_list;
            });
        })
        .push(function (message_list) {
          return new RSVP.Queue(RSVP.all([
            gadget.tool_manager.getSystemPromptList(),
            gadget.skill_manager.formatSkillListForPrompt()
          ]))
            .push(function (result_list) {
              var system_message_list = result_list[0],
                skill_list_prompt = result_list[1];
              if (skill_list_prompt) {
                system_message_list.push({ role: "system", content: skill_list_prompt });
              }
              return loop_call(0, system_message_list.concat(message_list));
            });
        });
      return queue_loop;
    });
}(window, rJS, RSVP));
