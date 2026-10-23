/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  var CHARS_PER_TOKEN = 3.5,
    COMPACT_TOKEN_BUDGET = 80000,
    KEEP_RECENT_TOKEN_BUDGET = 28000,
    PANIC_KEEP_RECENT_TOKEN_BUDGET = 8000,
    RATE_LIMIT_RETRY_DELAY_MS = 120000,
    MAX_LOOP_COUNT = 200000,
    SUMMARY_CHUNK_CHARS = 100000,
    SUMMARY_PROMPT = "The text below is one chunk of a larger tool result that was too large to return " +
      "as-is. Summarize it concisely, but preserve exact facts, numbers, names, dates, code, and any " +
      "other concrete detail that may be needed later - this summary is the ONLY part of this chunk " +
      "that will remain visible; anything you omit is permanently lost to the rest of this conversation.",
    STATIC_TOOL_SCOPE_LIST = [
      "tool_execute_javascript",
      "tool_run_wasm",
      "tool_library_inspect",
      "tool_http_request",
      "tool_execution_plan",
      "tool_define_tool",
      "tool_list_defined_tools",
      "tool_undefine_tool",
      "tool_spawn_subagent"
    ];

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

  var SUMMARIZATION_PROMPT = "The text above is a conversation to summarize. Create a structured context " +
    "checkpoint that another instance of this agent will use to continue the task. Use this EXACT format:\n\n" +
    "## Goal\n[What is the user trying to accomplish?]\n\n" +
    "## Constraints & Preferences\n- [Any constraints or requirements mentioned by the user, or \"(none)\"]\n\n" +
    "## Progress\n### Done\n- [Completed steps]\n\n### In Progress\n- [Current work]\n\n### Blocked\n- [Issues preventing progress, if any]\n\n" +
    "## Key Decisions\n- [Decision]: [Brief rationale]\n\n" +
    "## Next Steps\n1. [Ordered list of what should happen next]\n\n" +
    "## Critical Context\n- [Any data, identifiers, or exact values needed to continue, or \"(none)\"]\n\n" +
    "Keep each section concise. Preserve exact names, numbers, and error messages.";

  function estimateTokensForMessages(message_list) {
    return Math.ceil(JSON.stringify(message_list).length / CHARS_PER_TOKEN);
  }

  function serializeMessageListForSummary(message_list) {
    return message_list.map(function (message) {
      if (message.role === "assistant" && message.tool_calls && message.tool_calls.length) {
        return "Assistant: " + (message.content || "") + "\n" + message.tool_calls.map(function (tool_call) {
          return "  calls " + tool_call.function.name + "(" + (tool_call.function.arguments || "") + ")";
        }).join("\n");
      }
      if (message.role === "tool") {
        return "Tool result [" + message.name + "]: " + message.content;
      }
      return message.role + ": " + message.content;
    }).join("\n\n");
  }

  function estimateContextTokens(last_usage_anchor, message_list) {
    if (last_usage_anchor && last_usage_anchor.message_count <= message_list.length) {
      return last_usage_anchor.prompt_tokens + estimateTokensForMessages(message_list.slice(last_usage_anchor.message_count));
    }
    return estimateTokensForMessages(message_list);
  }

  function addUsageToTotals(gadget, usage) {
    if (!usage) {
      return;
    }
    gadget.usage_totals.call_count += 1;
    gadget.usage_totals.prompt_tokens += usage.prompt_tokens || 0;
    gadget.usage_totals.completion_tokens += usage.completion_tokens || 0;
    gadget.usage_totals.total_tokens += usage.total_tokens || ((usage.prompt_tokens || 0) + (usage.completion_tokens || 0));
  }

  rJS(window)
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    .declareAcquiredMethod("requestProcessTask", "requestProcessTask")
    .declareAcquiredMethod("storeTaskResult", "storeTaskResult")
    .declareAcquiredMethod("refreshMcpServerAuth", "refreshMcpServerAuth")
    .declareAcquiredMethod("getDefinedToolList", "getDefinedToolList")
    .declareAcquiredMethod("storeDefinedTool", "storeDefinedTool")

    .declareMethod('render', function (options) {
      var gadget = this;
      gadget.options = options;
      gadget.execution_plan = null;
      return new RSVP.Queue(RSVP.all(STATIC_TOOL_SCOPE_LIST.map(function (scope) {
          return gadget.getDeclaredGadget(scope);
        })))
        .push(function (tool_gadget_list) {
          return new RSVP.Queue(RSVP.all(tool_gadget_list.map(function (tool_gadget) {
              return tool_gadget.render(options);
            })))
            .push(function () {
              return new RSVP.Queue(RSVP.all(tool_gadget_list.map(function (tool_gadget) {
                  return tool_gadget.getDefinition();
                })))
                .push(function (definition_list) {
                  return tool_gadget_list.map(function (tool_gadget, i) {
                    return { gadget: tool_gadget, definition: definition_list[i] };
                  });
                });
            });
        })
        .push(function (static_tool_list) {
          gadget.tool_list = static_tool_list;
          if (!options.mcp_server_list || !options.mcp_server_list.length) {
            return;
          }
          return new RSVP.Queue(window.ChatMCP.buildToolList(
              options.mcp_server_list,
              function onMcpAuthExpired(server_config) {
                return gadget.refreshMcpServerAuth(server_config);
              }
            ))
            .push(function (mcp_tool_list) {
              gadget.tool_list = gadget.tool_list.concat(mcp_tool_list);
            });
        })
        .push(function () {
          return gadget.getDefinedToolList();
        })
        .push(function (spec_list) {
          return RSVP.all(spec_list.filter(function (spec) {
            return !window.ChatToolCommon.findClientTool(spec.name, gadget.tool_list);
          }).map(function (spec) {
            return gadget.createDynamicToolEntry(spec);
          }));
        })
        .push(function (entry_list) {
          entry_list.forEach(function (entry) {
            gadget.tool_list.push(entry);
          });
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
    .declareMethod('createDynamicToolEntry', function (spec) {
      var gadget = this,
        scope = "tool_dynamic_" + spec.name;
      return gadget.declareGadget("gadget_officejs_harness_ai_tool_dynamic.html", { scope: scope })
        .push(function (tool_gadget) {
          return tool_gadget.setDefinition(spec)
            .push(function () {
              return tool_gadget.render(gadget.options);
            })
            .push(function () {
              return {
                gadget: tool_gadget,
                definition: { name: spec.name, description: spec.description, parameters: spec.parameters || { type: "object", properties: {} } },
                dynamic: true,
                spec: spec,
                scope: scope
              };
            });
        });
    })
    .allowPublicAcquisition('getToolList', function () {
      return this.tool_list;
    })
    .allowPublicAcquisition('compactMessageList', function (argument_list) {
      return this.compactMessageList(argument_list[0], argument_list[1], argument_list[2]);
    })
    .allowPublicAcquisition('summarizeToolOutput', function (argument_list) {
      return this.summarizeToolOutput(argument_list[0]);
    })
    .allowPublicAcquisition('addUsageToTotals', function (argument_list) {
      addUsageToTotals(this, argument_list[0]);
    })
    .allowPublicAcquisition('isToolNameTaken', function (argument_list) {
      var name = argument_list[0];
      return this.tool_list.some(function (tool) { return tool.definition.name === name; });
    })
    .allowPublicAcquisition('persistAndRegisterDynamicTool', function (argument_list) {
      var gadget = this,
        spec = argument_list[0];
      return gadget.storeDefinedTool(spec)
        .push(function () {
          return gadget.createDynamicToolEntry(spec);
        })
        .push(function (entry) {
          gadget.tool_list.push(entry);
        });
    })
    .allowPublicAcquisition('listDynamicToolSpecs', function () {
      return this.tool_list.filter(function (tool) {
        return tool.dynamic;
      }).map(function (tool) {
        return tool.spec;
      });
    })
    .allowPublicAcquisition('undefineDynamicTool', function (argument_list) {
      var gadget = this,
        name = argument_list[0],
        i;
      for (i = 0; i < gadget.tool_list.length; i += 1) {
        if (gadget.tool_list[i].definition.name === name) {
          if (!gadget.tool_list[i].dynamic) {
            return "not_dynamic";
          }
          gadget.dropGadget(gadget.tool_list[i].scope);
          gadget.tool_list.splice(i, 1);
          return "removed";
        }
      }
      return "not_found";
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
        execution_plan;
      if (!queue_loop) {
        return;
      }
      gadget.processing_queue = null;
      queue_loop.cancel("Cancelled by user");

      execution_plan = gadget.execution_plan;
      gadget.execution_plan = null;

      return RSVP.all([
        gadget.gadget_chat_ui.showMessage({ content: "Cancelled by user", tool_message_list: gadget.tool_message_list, execution_plan: execution_plan }),
        gadget.notifySubmitted({message: 'Cancelled', status: "success"}),
        gadget.gadget_chat_ui.resetEditor(),
        gadget.storeTaskResult(
          gadget.options.jio_key,
          {
            tool_message_list: JSON.stringify(gadget.tool_message_list),
            content: "Cancelled by user",
            execution_plan: execution_plan ? JSON.stringify(execution_plan) : ""
          }
        )
      ]);
    })
    .declareMethod('compactMessageList', function (message_list, keep_recent_override, last_usage_anchor) {
      var gadget = this,
        keep_recent_budget = keep_recent_override || KEEP_RECENT_TOKEN_BUDGET,
        leading_system_count = 0,
        cut_index,
        recent_token_count = 0,
        leading_system_message_list,
        old_message_list,
        recent_message_list;
      if (!keep_recent_override && estimateContextTokens(last_usage_anchor, message_list) < COMPACT_TOKEN_BUDGET) {
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

      if (!old_message_list.length) {
        return message_list;
      }

      gadget.tool_message_list.push({
        role: "tool",
        name: "compact_history",
        content: "Conversation getting long - summarizing " + old_message_list.length +
          " older message(s) to free up context..."
      });
      return gadget.gadget_chat_ui.showMessage({
        tool_message_list: gadget.tool_message_list,
        execution_plan: gadget.execution_plan
      })
        .push(function () {
          return gadget.requestProcessTask(
            gadget.options.jio_key,
            {
              message_list: JSON.stringify([
                { role: "system", content: SUMMARIZATION_PROMPT },
                { role: "user", content: "<conversation>\n" + serializeMessageListForSummary(old_message_list) + "\n</conversation>" }
              ]),
              tool_definition_list: JSON.stringify([]),
              is_background: "1"
            }
          );
        })
        .push(function (result) {
          addUsageToTotals(gadget, result.usage);
          if (!result.content) {
            throw new Error("compactMessageList: empty summary");
          }
          return leading_system_message_list.concat([{
            role: "user",
            content: "[context summary]\n" + result.content
          }], recent_message_list);
        })
        .push(undefined, function () {
          return message_list;
        });
    })
    .declareMethod('summarizeToolOutput', function (content) {
      var gadget = this,
        text = typeof content === "string" ? content : JSON.stringify(content),
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
            gadget.tool_message_list.push({
              role: "tool",
              name: "summarize_tool_output",
              content: "Tool result too large to send as-is - summarizing part " + (index + 1) +
                " of " + chunk_list.length + "..."
            });
            return gadget.gadget_chat_ui.showMessage({
              tool_message_list: gadget.tool_message_list,
              execution_plan: gadget.execution_plan
            });
          })
          .push(function () {
            return gadget.requestProcessTask(
              gadget.options.jio_key,
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
            addUsageToTotals(gadget, result.usage);
            summary_text = "[Summary of chunk " + (index + 1) + " of " + chunk_list.length +
              " of a truncated tool output]\n" + (result.content || "(empty summary)");
            summary_list.push(summary_text);
            gadget.tool_message_list.push({
              role: "tool",
              name: "summarize_tool_output_result",
              content: summary_text
            });
            return gadget.gadget_chat_ui.showMessage({
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
      return gadget.gadget_chat_ui.showMessage({
        content: partial.content,
        tool_message_list: gadget.tool_message_list || [],
        execution_plan: gadget.execution_plan
      });
    })
    .declareJob('processTask', function (max_loop_count) {
      var gadget = this,
        queue_loop = new RSVP.Queue();
      gadget.tool_message_list = [];
      gadget.processing_queue = queue_loop;
      gadget.last_usage_anchor = null;
      gadget.usage_totals = { call_count: 0, prompt_tokens: 0, completion_tokens: 0, total_tokens: 0 };

      function loop_call(loop_count, message_list, pending_tool_call_list, is_retry) {
        var has_tool_call = Boolean(
            pending_tool_call_list && pending_tool_call_list.length
          );

        function loopError(e) {
          var error_text = "Error: " + (e && e.message ? e.message : String(e)),
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

        if (loop_count >= max_loop_count) {
          throw new Error("processTask: too many iterations");
        }

        if (has_tool_call) {
          queue_loop
            .push(function () {
              return window.ChatToolCommon.runClientToolCallList(pending_tool_call_list, message_list, gadget.tool_list);
            })
            .push(function (client_tool_result_list) {
              var i, tool_call, client_tool_result;
              for (i = 0; i < pending_tool_call_list.length; i += 1) {
                tool_call = pending_tool_call_list[i];
                client_tool_result = client_tool_result_list[i];
                gadget.tool_message_list.push({
                  name: tool_call.function.name,
                  content: 'args:' + (tool_call.function.arguments ? tool_call.function.arguments : '') + '\n' + 'result:' + client_tool_result.content,
                  sub_message_list: client_tool_result.message_list,
                  'role': "tool"
                });
                if (client_tool_result.execution_plan !== undefined) {
                  gadget.execution_plan = client_tool_result.execution_plan;
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
                    return gadget.summarizeToolOutput(client_tool_result.content);
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
            return gadget.compactMessageList(message_list, undefined, gadget.last_usage_anchor);
          })
          .push(function (compacted_message_list) {
            var shrunk_by = message_list.length - compacted_message_list.length;
            if (gadget.last_usage_anchor) {
              gadget.last_usage_anchor.message_count = Math.max(0, gadget.last_usage_anchor.message_count - shrunk_by);
            }
            message_list = compacted_message_list;
            return gadget.requestProcessTask(
              gadget.options.jio_key,
              {
                message_list: JSON.stringify(message_list),
                tool_definition_list: JSON.stringify(window.ChatToolCommon.toolDefinitionList(gadget.tool_list))
              }
            );
          })
          .push(function (result) {
            var execution_plan;
            addUsageToTotals(gadget, result.usage);
            if (result.usage && result.usage.prompt_tokens) {
              gadget.last_usage_anchor = { prompt_tokens: result.usage.prompt_tokens, message_count: message_list.length };
            }
            if (result.tool_calls && result.tool_calls.length) {
              gadget.tool_message_list.push({
                'role': 'assistant',
                'content': result.content
              })
              return gadget.gadget_chat_ui.showMessage({tool_message_list: gadget.tool_message_list, execution_plan: gadget.execution_plan })
                .push(function () {
                 return loop_call(
                   loop_count + 1,
                   message_list.concat([{
                    role: "assistant",
                    content: result.content,
                    tool_calls: result.tool_calls
                  }]),
                  result.tool_calls,
                  is_retry
                );
              });
            }
            if (!result.content) {
              throw new Error("Empty response from LLM with no tool calls" +
                (result.finish_reason ? " (finish_reason: " + result.finish_reason + ")" : ""));
            }
            execution_plan = gadget.execution_plan;
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
              gadget.gadget_chat_ui.showMessage({ content: result.content , tool_message_list: gadget.tool_message_list, execution_plan: execution_plan }),
              gadget.notifySubmitted({message: 'Completed', status: "success"}),
              gadget.gadget_chat_ui.resetEditor(),
              gadget.storeTaskResult(
                gadget.options.jio_key,
                {
                  tool_message_list: JSON.stringify(gadget.tool_message_list),
                  content: result.content,
                  execution_plan: execution_plan ? JSON.stringify(execution_plan) : ""
                }
              )
            ]);
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
                  return gadget.compactMessageList(message_list, PANIC_KEEP_RECENT_TOKEN_BUDGET);
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
          var skill_message_list = window.ChatSkills.SKILL_LIST.map(function (skill) {
            return { role: "system", content: skill.instructions };
          });
          message_list = [
            { role: "system", content: window.ChatToolCommon.ENVIRONMENT_SYSTEM_PROMPT },
            { role: "system", content: window.ChatToolCommon.TOOL_CALL_REPEAT_SYSTEM_PROMPT }
          ].concat(skill_message_list, message_list);
          return loop_call(0, message_list);
        });
      return queue_loop;
    });
}(window, rJS, RSVP));
