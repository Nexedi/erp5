/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  var STATIC_TOOL_SCOPE_LIST = [
      "tool_execute_javascript",
      "tool_run_wasm",
      "tool_library_inspect",
      "tool_http_request",
      "tool_pdf_to_text",
      "tool_load_skill",
      "tool_execution_plan",
      "tool_define_tool",
      "tool_list_defined_tools",
      "tool_undefine_tool",
      "tool_spawn_subagent"
    ],
    TOOL_CALL_REPEAT_LIMIT = 2,
    // Escalation when the LLM ignores the TOOL_CALL_REPEAT_LIMIT notice:
    // at HIDE_LIMIT the tool is dropped from the tool list sent to the LLM,
    // at STOP_LIMIT the agent loop stops instead of calling the LLM again.
    TOOL_CALL_REPEAT_HIDE_LIMIT = 3,
    TOOL_CALL_REPEAT_STOP_LIMIT = 4,
    TOOL_CALL_REPEAT_SYSTEM_PROMPT = "If a tool call with the exact same name and arguments fails or does " +
      "not help, do not call it again with the exact same arguments - it will not produce a different " +
      "result. Try different arguments, a different tool, or report the issue and move on instead.",
    ENVIRONMENT_SYSTEM_PROMPT = "This agent runs entirely inside a web browser tab, not on a server or a " +
      "local machine. There is no local filesystem, no shell, and no OS process to invoke - paths like " +
      "\"/home/...\" and commands like \"ls\", \"cat\" or \"pip install\" do not exist here, and any " +
      "attempt to use them will fail. The only capabilities available are the tools explicitly provided " +
      "in this conversation: a sandboxed JavaScript/WASM execution environment (itself with no " +
      "filesystem or network access), http_request for making network calls, execution_plan for " +
      "tracking a checklist, define_tool/list_defined_tools/undefine_tool for creating new callable " +
      "tools out of JS code, spawn_subagent for delegating sub-tasks, and whatever MCP tools are " +
      "configured. Do not assume access to anything beyond these.";

  function toolDefinitionList(tool_list) {
    return tool_list.map(function (tool) {
      return {
        type: "function",
        "function": {
          name: tool.definition.name,
          description: tool.definition.description,
          parameters: tool.definition.parameters
        }
      };
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
        content: result
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
          usage_totals = is_structured_result ? result.usage_totals : undefined,
          content = is_structured_result ? result.content : result,
          content_text = typeof content === "string" ? content : JSON.stringify(content);
        return {
          tool_call_id: tool_call.id,
          name: tool_call.function.name,
          content: content_text,
          message_list: message_list,
          execution_plan: execution_plan,
          usage_totals: usage_totals
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

  function countPriorIdenticalToolCalls(message_list, tool_call) {
    var count = 0, i, message, j, tc;
    for (i = 0; i < message_list.length; i += 1) {
      message = message_list[i];
      if (message.role === "assistant" && message.tool_calls) {
        for (j = 0; j < message.tool_calls.length; j += 1) {
          tc = message.tool_calls[j];
          if (tc.function.name === tool_call.function.name && tc.function.arguments === tool_call.function.arguments) {
            count += 1;
          }
        }
      }
    }
    return count;
  }

  function isRepeatAllowedTool(tool_call, tool_list) {
    var tool = findClientTool(tool_call.function.name, tool_list);
    return Boolean(tool && tool.definition && tool.definition.allow_repeat);
  }

  function runOneClientToolCall(tool_call, message_list, tool_list) {
    var repeat_count;
    if (isRepeatAllowedTool(tool_call, tool_list)) {
      return runClientToolCall(tool_call, tool_list);
    }
    repeat_count = countPriorIdenticalToolCalls(message_list, tool_call);
    if (repeat_count >= TOOL_CALL_REPEAT_LIMIT) {
      return {
        tool_call_id: tool_call.id,
        name: tool_call.function.name,
        content: "You already called this exact tool with these exact same arguments " + repeat_count +
          " time(s) before in this conversation, and it did not help - repeating it again will not " +
          "produce a different result. Stop retrying this exact call: try different arguments, a " +
          "different tool, or report the failure and move on." +
          (repeat_count >= TOOL_CALL_REPEAT_HIDE_LIMIT ?
              " This tool is now disabled for the rest of this task." : "")
      };
    }
    return runClientToolCall(tool_call, tool_list);
  }

  // Derived from message_list on every LLM request, so it needs no extra
  // state and works the same for the main agent loop and sub-agents.
  function getRepeatEscalation(message_list, tool_list) {
    var count_dict = {},
      hidden_tool_name_list = [],
      stop_reason = null,
      i,
      j,
      message,
      tool_call,
      key,
      count;
    for (i = 0; i < message_list.length; i += 1) {
      message = message_list[i];
      if (message.role === "assistant" && message.tool_calls) {
        for (j = 0; j < message.tool_calls.length; j += 1) {
          tool_call = message.tool_calls[j];
          if (!isRepeatAllowedTool(tool_call, tool_list)) {
            key = JSON.stringify([tool_call.function.name, tool_call.function.arguments]);
            count = (count_dict[key] || 0) + 1;
            count_dict[key] = count;
            if (count >= TOOL_CALL_REPEAT_HIDE_LIMIT &&
                hidden_tool_name_list.indexOf(tool_call.function.name) === -1) {
              hidden_tool_name_list.push(tool_call.function.name);
            }
            if (count >= TOOL_CALL_REPEAT_STOP_LIMIT && !stop_reason) {
              stop_reason = "Stopped: the model kept calling \"" + tool_call.function.name +
                "\" with the same arguments " + count + " times after being told to stop.";
            }
          }
        }
      }
    }
    return {
      hidden_tool_name_list: hidden_tool_name_list,
      stop_reason: stop_reason
    };
  }

  function filterHiddenTools(tool_list, hidden_tool_name_list) {
    return tool_list.filter(function (tool) {
      return hidden_tool_name_list.indexOf(tool.definition.name) === -1;
    });
  }

  function isSequentialToolCall(tool_call, tool_list) {
    var tool = findClientTool(tool_call.function.name, tool_list);
    return Boolean(tool && tool.definition && tool.definition.executionMode === "sequential");
  }

  function runClientToolCallList(tool_call_list, message_list, tool_list) {
    var queue, result_list;

    if (!tool_call_list.some(function (tool_call) { return isSequentialToolCall(tool_call, tool_list); })) {
      return RSVP.all(tool_call_list.map(function (tool_call) {
        return runOneClientToolCall(tool_call, message_list, tool_list);
      }));
    }

    // At least one call in this round targets a tool that mutates shared
    // gadget state (e.g. execution_plan, define_tool/undefine_tool) - run
    // the whole round one at a time instead of in parallel, so two such
    // calls in the same round can never race each other.
    queue = new RSVP.Queue();
    result_list = [];
    tool_call_list.forEach(function (tool_call, i) {
      queue
        .push(function () {
          return runOneClientToolCall(tool_call, message_list, tool_list);
        })
        .push(function (result) {
          result_list[i] = result;
        });
    });
    return queue.push(function () {
      return result_list;
    });
  }

  function getSystemPromptList() {
    return [
      { role: "system", content: ENVIRONMENT_SYSTEM_PROMPT },
      { role: "system", content: TOOL_CALL_REPEAT_SYSTEM_PROMPT }
    ];
  }

  // Tool definitions for the next LLM request. Tools the LLM keeps calling
  // with the same arguments are hidden, and once it still insists the whole
  // request is refused, so a looping agent stops instead of spinning forever.
  function getToolDefinitionList(tool_list, message_list, excluded_tool_name_list) {
    var escalation = getRepeatEscalation(message_list, tool_list);
    if (escalation.stop_reason) {
      throw new Error(escalation.stop_reason);
    }
    return toolDefinitionList(filterHiddenTools(
      tool_list,
      escalation.hidden_tool_name_list.concat(excluded_tool_name_list || [])
    ));
  }

  rJS(window)
    .declareAcquiredMethod("refreshMcpServerAuth", "refreshMcpServerAuth")
    .declareAcquiredMethod("getDefinedToolList", "getDefinedToolList")
    .declareAcquiredMethod("storeDefinedTool", "storeDefinedTool")

    .declareMethod('render', function (options) {
      var gadget = this;
      gadget.options = options;
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
            return !findClientTool(spec.name, gadget.tool_list);
          }).map(function (spec) {
            return gadget.createDynamicToolEntry(spec);
          }));
        })
        .push(function (entry_list) {
          entry_list.forEach(function (entry) {
            gadget.tool_list.push(entry);
          });
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
    .declareMethod('getSystemPromptList', function () {
      return getSystemPromptList();
    })
    .allowPublicAcquisition('getSystemPromptList', function () {
      return getSystemPromptList();
    })
    .declareMethod('getToolDefinitionList', function (message_list, excluded_tool_name_list) {
      return getToolDefinitionList(this.tool_list, message_list, excluded_tool_name_list);
    })
    .allowPublicAcquisition('getToolDefinitionList', function (argument_list) {
      return getToolDefinitionList(this.tool_list, argument_list[0], argument_list[1]);
    })
    .declareMethod('runToolCallList', function (tool_call_list, message_list) {
      return runClientToolCallList(tool_call_list, message_list, this.tool_list);
    })
    .allowPublicAcquisition('runToolCallList', function (argument_list) {
      return runClientToolCallList(argument_list[0], argument_list[1], this.tool_list);
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
    });
}(window, rJS, RSVP));
