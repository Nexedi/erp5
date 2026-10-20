/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  var COMPACT_THRESHOLD = 5000,
    KEEP_RECENT = 2000,
    RATE_LIMIT_RETRY_DELAY_MS = 120000,
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
            return gadget.processTask(200000);
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
        initial_message_length = gadget.current_initial_message_length || 0,
        execution_plan;
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

      execution_plan = gadget.execution_plan;
      gadget.execution_plan = null;

      return RSVP.all([
        gadget.gadget_chat_ui.showMessage({ content: "Cancelled by user", tool_message_list: gadget.tool_message_list, execution_plan: execution_plan }),
        gadget.notifySubmitted({message: 'Cancelled', status: "success"}),
        gadget.gadget_chat_ui.resetEditor(),
        gadget.storeTaskResult(
          gadget.options.jio_key,
          {
            message_list: JSON.stringify(
              message_list.slice(initial_message_length).concat([{content: "Cancelled by user"}])
            ),
            content: "Cancelled by user",
            execution_plan: execution_plan ? JSON.stringify(execution_plan) : ""
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
                message_list: JSON.stringify([]),
                content: "[" + error_text + "]",
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
              return RSVP.all(pending_tool_call_list.map(function (tool_call) {
                return window.ChatToolCommon.runClientToolCall(tool_call, gadget.tool_list);
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
                  content: client_tool_result.content
                }]);
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
              return RSVP.all([
                next_message_list,
                gadget.gadget_chat_ui.showMessage({tool_message_list: gadget.tool_message_list, execution_plan: gadget.execution_plan })
              ]);
            })
            .push(function (resulit_list) {
              return loop_call(
                loop_count + 1,
                resulit_list[0],
                null,
                is_rate_limit_retry
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
                tool_definition_list: JSON.stringify(window.ChatToolCommon.toolDefinitionList(gadget.tool_list))
              }
            );
          })
          .push(function (result) {
            var execution_plan;
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
                  is_rate_limit_retry
                );
              });
            }
            execution_plan = gadget.execution_plan;
            gadget.processing_queue = null;
            gadget.execution_plan = null;
            return RSVP.all([
              gadget.gadget_chat_ui.showMessage({ content: result.content , tool_message_list: gadget.tool_message_list, execution_plan: execution_plan }),
              gadget.notifySubmitted({message: 'Completed', status: "success"}),
              gadget.gadget_chat_ui.resetEditor(),
              gadget.storeTaskResult(
                gadget.options.jio_key,
                {
                  message_list: JSON.stringify(message_list.slice(gadget.current_initial_message_length).concat([result])),
                  content: result.content,
                  execution_plan: execution_plan ? JSON.stringify(execution_plan) : ""
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
            gadget.gadget_chat_ui.showMessage({}),
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
