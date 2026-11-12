/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  var CHARS_PER_TOKEN = 3.5,
    COMPACT_TOKEN_BUDGET = 80000,
    KEEP_RECENT_TOKEN_BUDGET = 28000,
    CONTEXT_RESERVE_TOKENS = 16384,
    // An image costs about this many characters of context, whatever the
    // size of its base64 data URI.
    IMAGE_ESTIMATE_CHARS = 4800,
    MAX_LOOP_COUNT = 500,
    ENVIRONMENT_SYSTEM_PROMPT = "This agent runs inside a web browser tab, not on a server or a local " +
      "machine. There is no filesystem, no shell and no OS process: paths like \"/home/...\" and " +
      "commands like \"ls\" or \"pip install\" do not exist here. You can act only through the tools " +
      "given in this conversation. The history of this conversation keeps the tool calls of your " +
      "earlier answers and their results. When it gets long, its oldest part is replaced by a summary.",
    TURN_LIMIT_PROMPT = "Turn limit reached: you can not call tools anymore. Give your final answer " +
      "now, with what you found so far, and say clearly what you could not find or verify.",
    CONTEXT_SUMMARY_PREFIX = "[context summary]\n",
    SUMMARY_FORMAT = "## Goal\n[What is the user trying to accomplish?]\n\n" +
      "## Constraints & Preferences\n- [Any constraints or requirements mentioned by the user, or \"(none)\"]\n\n" +
      "## Progress\n### Done\n- [Completed steps]\n\n### In Progress\n- [Current work]\n\n### Blocked\n- [Issues preventing progress, if any]\n\n" +
      "## Key Decisions\n- [Decision]: [Brief rationale]\n\n" +
      "## Next Steps\n1. [Ordered list of what should happen next]\n\n" +
      "## Critical Context\n- [Any data, identifiers, or exact values needed to continue, or \"(none)\"]\n\n" +
      "Keep each section concise. Preserve exact names, numbers, and error messages. Answer with the " +
      "summary only.",
    SUMMARIZATION_PROMPT = "Summarize the conversation given in <conversation> tags into a structured " +
      "checkpoint, that another instance of this agent will use to continue the task. Use this EXACT " +
      "format:\n\n" + SUMMARY_FORMAT,
    // Used when an earlier compaction already produced a summary: merge the
    // new messages into it instead of summarizing the summary again, which
    // would lose a little more detail at every compaction.
    UPDATE_SUMMARIZATION_PROMPT = "Update the summary given in <previous-summary> tags with the NEW " +
      "conversation messages given in <conversation> tags: keep all that is still relevant, move " +
      "finished work to Done, and add the new progress, decisions and context. Use this EXACT " +
      "format:\n\n" + SUMMARY_FORMAT;

  // Whether the message is the summary of the older messages, put by
  // compactMessageList.
  function isSummaryMessage(message) {
    return Boolean(message && message.role === "user" && typeof message.content === "string" &&
      message.content.indexOf(CONTEXT_SUMMARY_PREFIX) === 0);
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
          truncateForSummary(messageContentToText(message.content), 2000);
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
    .declareAcquiredMethod("getTaskCompaction", "getTaskCompaction")
    .declareAcquiredMethod("storeTaskCompaction", "storeTaskCompaction")

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
        role: "note",
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
    .declareMethod('compactMessageList', function (message_list, keep_recent_override, last_usage_anchor,
                                                   cut_index_list) {
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
            first_old_index,
            before_cut_index,
            after_cut_index,
            index,
            i,
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
          if (cut_index_list) {
            // message_list = [system, question 1, its 79 tool calls,
            // results and answer, question 2 (index 81), ...] with
            // cut_index_list = [1, 81, 83, 84, 85] and cut_index = 45 (in
            // the tool calls of the first turn): 1 is first_old_index, so
            // nothing is before the cut, and the cut moves to 81. Messages 1
            // to 80 (the whole first turn) are summarized, and the messages
            // from question 2 are kept.
            first_old_index = leading_system_count;
            if (isSummaryMessage(message_list[leading_system_count])) {
              first_old_index += 1;
            }
            before_cut_index = null;
            after_cut_index = null;
            for (i = 0; i < cut_index_list.length; i += 1) {
              index = cut_index_list[i];
              if (index > first_old_index) {
                if (index <= cut_index) {
                  before_cut_index = index;
                } else if (after_cut_index === null) {
                  after_cut_index = index;
                }
              }
            }
            cut_index = before_cut_index || after_cut_index || leading_system_count;
          }
          leading_system_message_list = message_list.slice(0, leading_system_count);
          old_message_list = message_list.slice(leading_system_count, cut_index);
          recent_message_list = message_list.slice(cut_index);

          if (old_message_list.length && isSummaryMessage(old_message_list[0])) {
            previous_summary = old_message_list[0].content.slice(CONTEXT_SUMMARY_PREFIX.length);
            old_message_list = old_message_list.slice(1);
          }
          if (!old_message_list.length) {
            return { message_list: message_list, usage_totals: summary_usage_totals };
          }

          if (gadget.tool_message_list) {
            gadget.tool_message_list.push({
              role: "note",
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
                usage_totals: summary_usage_totals,
                summary: result.content,
                cut_index: cut_index
              };
            })
            .push(undefined, function (e) {
              // Keep going with the full history, but say so: the next request
              // may then overflow the context.
              if (gadget.tool_message_list) {
                gadget.tool_message_list.push({
                  role: "note",
                  name: "compact_history",
                  content: "Summarizing the older messages failed (" + (e && e.message ? e.message : String(e)) +
                    ") - continuing with the full history."
                });
              }
              return { message_list: message_list, usage_totals: summary_usage_totals };
            });
        });
    })
    // load&compact&save summary if needed
    .declareMethod('loadHistory', function () {
      var gadget = this;
      return new RSVP.Queue(RSVP.all([
        gadget.getTaskCompaction(gadget.jio_key),
        gadget.getSystemPromptList()
      ]))
        .push(function (result_list) {
          var compaction = result_list[0],
            head_message_list = result_list[1].concat(compaction ? [{
              role: "user",
              content: CONTEXT_SUMMARY_PREFIX + compaction.summary
            }] : []);
          return gadget.gadget_chat_ui.getMessageList(compaction ? compaction.summarized_before_int_index : 0)
            .push(function (history) {
              return [head_message_list, history];
            });
        })
        .push(function (result_list) {
          var head_message_list = result_list[0],
            history = result_list[1];
          return gadget.compactMessageList(head_message_list.concat(history.message_list), undefined, null,
            history.cut_list.map(function (cut) {
              return cut.index + head_message_list.length;
            }))
            .push(function (compacted) {
              var loaded = { message_list: compacted.message_list, usage_totals: compacted.usage_totals };
              if (compacted.summary === undefined) {
                return loaded;
              }
              return gadget.storeTaskCompaction(gadget.jio_key, {
                summary: compacted.summary,
                summarized_before_int_index: history.cut_list.filter(function (cut) {
                  return cut.index === compacted.cut_index - head_message_list.length;
                })[0].int_index
              })
                .push(function () {
                  return loaded;
                });
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
          // One system message only: some servers reject several, or a
          // system message after the first one, or keep only the first.
          var content_list = [ENVIRONMENT_SYSTEM_PROMPT].concat(result_list[0].map(function (message) {
            return message.content;
          }));
          if (result_list[1]) {
            content_list.push(result_list[1]);
          }
          return [{ role: "system", content: content_list.join("\n\n") }];
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
          role: "note",
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
          role: "note",
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
                role: "note",
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
              // Its "note" messages are notes of the agent (retries,
              // compaction, usage...), not sent to the model.
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
            var retry_name = window.ChatToolCommon.getRetryName(e),
              retry_reason = retry_name === "network_error_retry" ?
                  " (the connection to the LLM server failed)" : "",
              retry_count,
              delay;
            // Counted by kind of error.
            retry_count_dict = retry_count_dict || {};
            retry_count = retry_count_dict[retry_name] || 0;
            if (!window.ChatToolCommon.isRetryAllowed(retry_name, retry_count)) {
              return loopError(e);
            }
            retry_count_dict[retry_name] = retry_count + 1;
            if (retry_name === "context_overflow_retry") {
              gadget.tool_message_list.push({
                role: "note",
                name: retry_name,
                content: e.message + " - the proactive estimate missed this, compacting harder and retrying"
              });
              return gadget.gadget_chat_ui.showMessage({
                tool_message_list: gadget.tool_message_list,
                execution_plan: gadget.execution_plan
              })
                .push(function () {
                  return gadget.compactMessageList(message_list, window.ChatToolCommon.PANIC_KEEP_RECENT_TOKEN_BUDGET);
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
            delay = window.ChatToolCommon.getRetryDelay(e, retry_count);
            gadget.tool_message_list.push({
              role: "note",
              name: retry_name,
              content: e.message + retry_reason + " - retry " + (retry_count + 1) +
                (retry_name === "network_error_retry" ? "" : " of " + window.ChatToolCommon.MAX_RETRY_COUNT) +
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
            gadget.tool_message_list.push({ role: "note", name: "mcp_unavailable", content: content });
          });
        })
        .push(function () {
          return gadget.notifySubmitted({message: 'Processing', status: "success"});
        })
        .push(function () {
          return gadget.loadHistory();
        })
        .push(function (loaded) {
          window.ChatToolCommon.addUsageTotals(usage_totals, loaded.usage_totals);
          return loop_call(0, loaded.message_list);
        });
      return queue_loop;
    });
}(window, rJS, RSVP));
