/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  var COMPACT_THRESHOLD = 5000,
    KEEP_RECENT = 2000,
    MAX_TOOL_OUTPUT_LINES = 20000,
    SUBAGENT_DEFAULT_MAX_LOOP_COUNT = 2000,
    SUBAGENT_MAX_LOOP_COUNT_CAP = 5000,
    RATE_LIMIT_RETRY_DELAY_MS = 120000,
    SUBAGENT_EXCLUDED_TOOL_NAME_LIST = ["spawn_subagent", "set_execution_plan", "update_execution_plan_step"];

  function isRateLimitError(e) {
    return Boolean(e && e.message && (/^LLM 429 /).test(e.message));
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
        return tool.execute(args);
      })
      .push(function (result) {

        var message_list = result && typeof result === "object" ? result.message_list : undefined,
          content = message_list ? result.content : result;
        return {
          tool_call_id: tool_call.id,
          name: tool_call.function.name,
          content: typeof content === "string" ? content : JSON.stringify(content),
          message_list: message_list
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

  function rehydrateDynamicTools(tool_list, spec_list) {
    var j, spec;
    for (j = 0; j < spec_list.length; j += 1) {
      spec = spec_list[j];
      if (!findClientTool(spec.name, tool_list)) {
        tool_list.registerDynamicTool(tool_list.createDynamicJsTool(spec));
      }
    }
  }

  rJS(window)
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    .declareAcquiredMethod("requestProcessTask", "requestProcessTask")
    .declareAcquiredMethod("requestHttp", "requestHttp")
    .declareAcquiredMethod("storeTaskResult", "storeTaskResult")
    .declareAcquiredMethod("refreshMcpServerAuth", "refreshMcpServerAuth")
    .declareAcquiredMethod("getDefinedToolList", "getDefinedToolList")
    .declareAcquiredMethod("storeDefinedTool", "storeDefinedTool")
    .declareAcquiredMethod("removeDefinedTool", "removeDefinedTool")
    .declareAcquiredMethod("getCommentPostList", "getCommentPostList")

    .declareMethod('runSubagentTask', function (task, max_turns) {
      var gadget = this,
        queue_loop = new RSVP.Queue(),
        document_id = gadget.options.jio_key,
        max_loop_count = Math.min(Math.max(Number(max_turns) || SUBAGENT_DEFAULT_MAX_LOOP_COUNT, 1), SUBAGENT_MAX_LOOP_COUNT_CAP);

      function subagentToolDefinitionList() {
        return toolDefinitionList(gadget.tool_list.filter(function (tool) {
          return SUBAGENT_EXCLUDED_TOOL_NAME_LIST.indexOf(tool.definition.name) === -1;
        }));
      }

      function subagentLoopCall(loop_count, message_list, pending_tool_call_list) {
        var has_tool_call = Boolean(pending_tool_call_list && pending_tool_call_list.length);

        function subagentError(e) {
          return {
            content: "Error running sub-agent: " + JSON.stringify(e, Object.getOwnPropertyNames(e)),
            message_list: message_list
          };
        }
        console.log('**************subagentLoopCall ' + loop_count);
        if (loop_count >= max_loop_count) {
          return new RSVP.Queue().push(function () {
            return {
              content: "[subagent stopped: exceeded " + max_loop_count + " turns without a final answer]",
              message_list: message_list
            };
          });
        }

        if (has_tool_call) {
          queue_loop
            .push(function () {
              return RSVP.all(pending_tool_call_list.map(function (tool_call) {
                return runClientToolCall(tool_call, gadget.tool_list);
              }));
            })
            .push(function (client_tool_result_list) {
              var next_message_list = message_list, i, tool_call, client_tool_result;
              for (i = 0; i < pending_tool_call_list.length; i += 1) {
                tool_call = pending_tool_call_list[i];
                client_tool_result = client_tool_result_list[i];
                next_message_list = next_message_list.concat([{
                  role: "tool",
                  tool_call_id: tool_call.id,
                  name: tool_call.function.name,
                  content: truncateToolOutput('args:' + (tool_call.function.arguments ? tool_call.function.arguments : '') + '\n' + 'result:' + client_tool_result.content)
                }]);
              }
              return subagentLoopCall(
                loop_count + 1,
                next_message_list,
                null
              );
            })
            .push(undefined, subagentError);
          return;
        }

        queue_loop
          .push(function () {
            return gadget.requestProcessTask(
              document_id,
              {
                message_list: JSON.stringify(message_list),
                tool_definition_list: JSON.stringify(subagentToolDefinitionList()),
                is_subagent: "1"
              }
            );
          })
          .push(function (result) {
            if (result.tool_calls && result.tool_calls.length) {
              return subagentLoopCall(
                loop_count + 1,
                message_list.concat([{
                  role: "assistant",
                  content: result.content,
                  tool_calls: result.tool_calls
                }]),
                result.tool_calls
              );
            }
            return {
              content: result.content,
              message_list: message_list.concat([{ role: "assistant", content: result.content }])
            };
          })
          .push(undefined, subagentError);
      }

      subagentLoopCall(0, [{ role: "user", content: task }]);
      return queue_loop;
    })

    .declareMethod('render', function (options) {
      var gadget = this;
      gadget.options = options;
      gadget.execution_plan = null;
      return new RSVP.Queue(gadget.getCommentPostList(options.jio_key))
        .push(function (post_list) {
          // The current working plan is simply whatever the most recent
          var i;
          for (i = post_list.length - 1; i >= 0; i -= 1) {
            if (post_list[i].execution_plan) {
              gadget.execution_plan = JSON.parse(post_list[i].execution_plan);
              break;
            }
          }
          return window.ChatTools.createToolList(
            gadget.element,
            options.mcp_server_list,
            function onMcpServerError(server_config, error) {
              if (window.console && window.console.warn) {
                window.console.warn(
                  "MCP server \"" + (server_config && server_config.name) + "\" unavailable: " +
                    (error && error.message ? error.message : error)
                );
              }
            },
            function (server_config) {
              return gadget.refreshMcpServerAuth(server_config);
            },
            function (args) {
              return gadget.requestHttp(args);
            },
            function (spec) {
              return gadget.storeDefinedTool(spec);
            },
            function (name) {
              return gadget.removeDefinedTool(name);
            },
            function (action) {
              return gadget.updateExecutionPlan(action);
            }
          );
        })
        .push(function (tool_list) {
          gadget.tool_list = tool_list;
          gadget.tool_list.push({
            definition: {
              name: "spawn_subagent",
              description: "Delegate a self-contained sub-task to a fresh, independent instance of this " +
                "same agent - same tools (everything except spawn_subagent itself, to prevent runaway " +
                "recursion), but its own separate conversation that starts empty (it has NO access to this " +
                "conversation's history - give it a full, self-contained task description). Runs to " +
                "completion (its own multi-turn tool-calling loop) before this call returns; only its final " +
                "answer comes back - none of its intermediate searches/reads/retries appear in this " +
                "conversation. USE THIS WHEN: a piece of the current task is large or noisy enough to " +
                "isolate (e.g. \"research X and summarize\", \"go create and populate these 5 documents, " +
                "report back what was done\"). DO NOT USE THIS for a trivial one-tool-call task - just call " +
                "that tool directly.",
              parameters: {
                type: "object",
                properties: {
                  task: {
                    type: "string",
                    description: "Full, self-contained description of what the sub-agent should do."
                  },
                  max_turns: {
                    type: "integer",
                    description: "Cap on the sub-agent's own turn count (default 20, max 50)."
                  }
                },
                required: ["task"]
              }
            },
            execute: function (args) {
              return gadget.runSubagentTask(args.task, args.max_turns);
            }
          });
          return gadget.getDefinedToolList();
        })
        .push(function (spec_list) {
          rehydrateDynamicTools(gadget.tool_list, spec_list);
          return gadget.getDeclaredGadget("gadget_chat_ui");
        })
        .push(function (gadget_chat_ui) {
          gadget.gadget_chat_ui = gadget_chat_ui;
          return gadget_chat_ui.render(Object.assign({}, options, {enable_cancel: true}));
        })
        .push(function () {
          if (options.chat_state === 'started') {
            return gadget.processTask(200000);
          }
        });
    })
    .declareMethod('updateExecutionPlan', function (action) {
      var gadget = this,
        plan = gadget.execution_plan,
        step;
      if (action.command === "set") {
        plan = {
          goal: action.goal || "",
          step_list: (action.step_list || []).map(function (step_spec) {
            return { title: step_spec.title, status: "pending", note: "" };
          })
        };
      } else if (action.command === "update_step") {
        step = plan && plan.step_list[action.index];
        if (!step) {
          return null;
        }
        step.status = action.status;
        step.note = action.note || "";
      }
      gadget.execution_plan = plan;
      return plan;
    })
    .allowPublicAcquisition('notifyCommentPosted', function () {
      return this.processTask(200000);
    })
    .allowPublicAcquisition('notifyCancelRequested', function () {
      return this.cancelProcessing();
    })
    .declareMethod('cancelProcessing', function () {
      var gadget = this,
        queue_loop = gadget.processing_queue,
        message_list = gadget.current_message_list || [],
        pending_tool_call_list = gadget.current_pending_tool_call_list || [],
        initial_message_length = gadget.current_initial_message_length || 0;
      if (!queue_loop) {
        return;
      }
      gadget.processing_queue = null;
      queue_loop.cancel("Cancelled by user");

      pending_tool_call_list.forEach(function (tool_call) {
        message_list = message_list.concat([{
          role: "tool",
          tool_call_id: tool_call.id,
          name: tool_call.function.name,
          content: "Cancelled by user"
        }]);
      });

      return RSVP.all([
        gadget.gadget_chat_ui.showMessage({ content: "Cancelled by user", tool_message_list: gadget.tool_message_list, execution_plan: gadget.execution_plan }),
        gadget.notifySubmitted({message: 'Cancelled', status: "success"}),
        gadget.gadget_chat_ui.resetEditor(),
        gadget.storeTaskResult(
          gadget.options.jio_key,
          {
            message_list: JSON.stringify(
              message_list.slice(initial_message_length).concat([{content: "Cancelled by user"}])
            ),
            content: "Cancelled by user",
            execution_plan: gadget.execution_plan ? JSON.stringify(gadget.execution_plan) : ""
          }
        )
      ]);
    })
    .declareMethod('compactMessageList', function (message_list) {
      var gadget = this,
        leading_system_count = 0,
        cut_index,
        leading_system_message_list,
        old_message_list,
        recent_message_list;
      if (message_list.length < COMPACT_THRESHOLD) {
        return message_list;
      }
      while (leading_system_count < message_list.length &&
          message_list[leading_system_count].role === "system") {
        leading_system_count += 1;
      }

      cut_index = Math.max(message_list.length - KEEP_RECENT, leading_system_count);
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

      return gadget.requestProcessTask(
        gadget.options.jio_key,
        { compact_message_list: JSON.stringify(old_message_list) }
      )
        .push(function (result) {
          if (!result.content) {
            throw new Error("compactMessageList: empty summary");
          }
          return leading_system_message_list.concat([{
            role: "user", //XXXXX this change all message role to user
            content: "[context summary]\n" + result.content
          }], recent_message_list);
        })
        .push(undefined, function () {
          return message_list;
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
    .declareJob('processTask', function (max_loop_count, skill_list) {
      var gadget = this,
        queue_loop = new RSVP.Queue();
      gadget.tool_message_list = [];
      gadget.processing_queue = queue_loop;
      gadget.current_message_list = [];
      gadget.current_pending_tool_call_list = null;
      gadget.current_initial_message_length = 0;

      function loop_call(loop_count, message_list, pending_tool_call_list, is_rate_limit_retry) {
        var has_tool_call = Boolean(
            pending_tool_call_list && pending_tool_call_list.length
          );
        gadget.current_message_list = message_list;
        gadget.current_pending_tool_call_list = pending_tool_call_list;

        function loopError(e) {
          var error_text = "Error: " + (e && e.message ? e.message : String(e));
          gadget.processing_queue = null;
          return RSVP.all([
            gadget.gadget_chat_ui.showMessage({ content: error_text, tool_message_list: gadget.tool_message_list, execution_plan: gadget.execution_plan }),
            gadget.notifySubmitted({message: 'Error', status: "error"}),
            gadget.gadget_chat_ui.resetEditor(),
            gadget.storeTaskResult(
              gadget.options.jio_key,
              {
                message_list: JSON.stringify([]),
                content: "[" + error_text + "]",
                execution_plan: gadget.execution_plan ? JSON.stringify(gadget.execution_plan) : ""
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
              return RSVP.all(pending_tool_call_list.map(function (tool_call) {
                return runClientToolCall(tool_call, gadget.tool_list);
              }));
            })
            .push(function (client_tool_result_list) {
              var next_message_list = message_list, i, tool_call, client_tool_result, result_content;
              for (i = 0; i < pending_tool_call_list.length; i += 1) {
                tool_call = pending_tool_call_list[i];
                client_tool_result = client_tool_result_list[i];
                result_content = 'args:' + (tool_call.function.arguments ? tool_call.function.arguments : '') + '\n' + 'result:' + client_tool_result.content;
                next_message_list = next_message_list.concat([{
                  role: "tool",
                  tool_call_id: tool_call.id,
                  name: tool_call.function.name,
                  content: truncateToolOutput(result_content),
                  sub_message_list: client_tool_result.message_list
                }]);
                gadget.tool_message_list.push({
                  name: tool_call.function.name,
                  content: result_content,
                  sub_message_list: client_tool_result.message_list,
                  'role': 'tole'
                });
              }
              return RSVP.all([
                next_message_list,
                gadget.gadget_chat_ui.showMessage({tool_message_list: gadget.tool_message_list, execution_plan: gadget.execution_plan })
              ]);
            })
            .push(function (resulit_list) {
              return loop_call(
                loop_count + 1,
                resulit_list[0],
                null
              );
            })
            .push(undefined, loopError);
          return;
        }

        queue_loop
          .push(function () {
            return gadget.requestProcessTask(
              gadget.options.jio_key,
              {
                message_list: JSON.stringify(message_list),
                tool_definition_list: JSON.stringify(toolDefinitionList(gadget.tool_list)),
                initial_message_length: gadget.current_initial_message_length
              }
            );
          })
          .push(function (result) {
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
                  result.tool_calls
                );
              });
            }
            gadget.processing_queue = null;
            return RSVP.all([
              gadget.gadget_chat_ui.showMessage({ content: result.content , tool_message_list: gadget.tool_message_list, execution_plan: gadget.execution_plan }),
              gadget.notifySubmitted({message: 'Completed', status: "success"}),
              gadget.gadget_chat_ui.resetEditor(),
              gadget.storeTaskResult(
                gadget.options.jio_key,
                {
                  message_list: JSON.stringify(message_list.slice(gadget.current_initial_message_length).concat([result])),
                  content: result.content,
                  execution_plan: gadget.execution_plan ? JSON.stringify(gadget.execution_plan) : ""
                }
              )
            ]);
          })
          .push(undefined, function (e) {
            // A 429 is transient (rate limit, not a real failure) - worth
            // one automatic retry of this same turn after a long wait,

            if (!is_rate_limit_retry && isRateLimitError(e)) {
              if (window.console && window.console.warn) {
                window.console.warn(e.message + " - retrying once in " + (RATE_LIMIT_RETRY_DELAY_MS / 1000) + "s");
              }
              return new RSVP.Queue(RSVP.delay(RATE_LIMIT_RETRY_DELAY_MS))
                .push(function () {
                  return loop_call(loop_count, message_list, pending_tool_call_list, true);
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
          return RSVP.all([
            gadget.gadget_chat_ui.showMessage({ execution_plan: gadget.execution_plan }),
            gadget.compactMessageList(message_list)
          ]);
        })
        .push(function (result_list) {
          // XXXXXX seems bad to do locally
          var message_list = result_list[1],
            last_comment = message_list[message_list.length - 1].content,
            skill_list = window.ChatSkills.matchSkillList(last_comment),
            skill_message_list = (skill_list || []).map(function (skill) {
              return { role: "system", content: skill.instructions };
            });
          message_list = skill_message_list.concat(message_list);
          gadget.current_initial_message_length = message_list.length;
          return loop_call(0, message_list);
        });
      return queue_loop;
    });
}(window, rJS, RSVP));
