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
      "tool_spawn_subagent",
      "tool_read_tool_output"
    ],
    // Result of the tool calls of a response cut by the max output tokens:
    // their arguments may be incomplete (a cut string can still parse), so
    // none of them is run.
    TRUNCATED_TOOL_CALL_RESULT = "Not run: the response hit the max output tokens, so the arguments of " +
      "this call may be incomplete. Re-issue the tool call with complete arguments, splitting large " +
      "content over several calls if needed.",
    TURN_LIMIT_TOOL_CALL_RESULT = "Not run: turn limit reached.",
    TOOL_CALL_REPEAT_LIMIT = 3,
    // Only the tool calls of the last TOOL_CALL_REPEAT_WINDOW assistant
    // turns are counted.
    TOOL_CALL_REPEAT_WINDOW = 12,
    // Is it really a good idea ?
    // If it happends, it means probably that the tool is bad defined
    // at HIDE_LIMIT the tool is dropped from the tool list sent to the LLM,
    // at STOP_LIMIT the agent loop stops instead of calling the LLM again.
    TOOL_CALL_REPEAT_HIDE_LIMIT = 4,
    // Written in the tool result that removes a tool: finding it in the
    // message_list keeps that tool removed for the rest of the task.
    TOOL_DISABLED_NOTICE = "This tool is now disabled for the rest of this task.",
    TOOL_CALL_REPEAT_STOP_LIMIT = 5,
    TOOL_CALL_REPEAT_SYSTEM_PROMPT = "If a tool call with the exact same name and arguments fails or does " +
      "not help, do not call it again with the exact same arguments - it will not produce a different " +
      "result. Try different arguments, a different tool, or report the issue and move on instead.";

  function findClientTool(name, tool_list) {
    var i;
    for (i = 0; i < tool_list.length; i += 1) {
      if (tool_list[i].definition.name === name) {
        return tool_list[i];
      }
    }
    return null;
  }

  // Escape the raw control characters some models write inside JSON
  // strings (eg. a real newline in a "code" argument), which JSON.parse
  // rejects. Characters outside strings are whitespace and kept as is.
  function repairJson(text) {
    var result = "", in_string = false, i, c;
    for (i = 0; i < text.length; i += 1) {
      c = text.charAt(i);
      if (in_string && c === "\\") {
        result += c + text.charAt(i + 1);
        i += 1;
      } else if (c === "\"") {
        in_string = !in_string;
        result += c;
      } else if (in_string && c < " ") {
        result += c === "\n" ? "\\n" : c === "\r" ? "\\r" : c === "\t" ? "\\t" :
            "\\u" + ("000" + c.charCodeAt(0).toString(16)).slice(-4);
      } else {
        result += c;
      }
    }
    return result;
  }

  // Arguments of a tool call, or null if they are not a JSON object even
  // after repair. The tool is then not run, and the model is told why.
  function parseToolCallArguments(text) {
    var args;
    if (!text || !text.trim()) {
      return {};
    }
    try {
      args = JSON.parse(text);
    } catch (ignore) {
      try {
        args = JSON.parse(repairJson(text));
      } catch (ignore2) {
        return null;
      }
    }
    return (args && typeof args === "object" && !Array.isArray(args)) ? args : null;
  }

  function runClientToolCall(tool_call, tool_list) {
    var tool = findClientTool(tool_call.function.name, tool_list),
      args = parseToolCallArguments(tool_call.function.arguments),
      result;
    if (args === null) {
      return {
        tool_call_id: tool_call.id,
        name: tool_call.function.name,
        content: "Error: the arguments of this \"" + tool_call.function.name + "\" call are not a valid " +
          "JSON object, so the tool was not run. Received: " +
          (tool_call.function.arguments.length > 500 ?
              tool_call.function.arguments.slice(0, 500) + "..." : tool_call.function.arguments) +
          "\nRe-issue the call with valid JSON arguments."
      };
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


  // How many times each tool call (same name, same arguments) appears in
  // the last TOOL_CALL_REPEAT_WINDOW assistant turns of message_list, keyed
  // by the JSON of its name and arguments.
  function countToolCalls(message_list) {
    var count_dict = {}, turn_count = 0, i, j, message, key;
    for (i = message_list.length - 1; i >= 0 && turn_count < TOOL_CALL_REPEAT_WINDOW; i -= 1) {
      message = message_list[i];
      if (message.role === "assistant" && message.tool_calls && message.tool_calls.length) {
        turn_count += 1;
        for (j = 0; j < message.tool_calls.length; j += 1) {
          key = JSON.stringify([message.tool_calls[j].function.name, message.tool_calls[j].function.arguments]);
          if (!count_dict.hasOwnProperty(key)) {
            count_dict[key] = { name: message.tool_calls[j].function.name, count: 0 };
          }
          count_dict[key].count += 1;
        }
      }
    }
    return count_dict;
  }

  function isRepeatAllowedTool(tool_call, tool_list) {
    var tool = findClientTool(tool_call.function.name, tool_list);
    return Boolean(tool && tool.definition && tool.definition.allow_repeat);
  }

  // Names of the tools whose result, anywhere in message_list, says that
  // they are disabled.
  function getDisabledToolNameList(message_list) {
    var name_list = [], i, message;
    for (i = 0; i < message_list.length; i += 1) {
      message = message_list[i];
      if (message.role === "tool" && message.name && typeof message.content === "string" &&
          message.content.indexOf(TOOL_DISABLED_NOTICE) !== -1 && name_list.indexOf(message.name) === -1) {
        name_list.push(message.name);
      }
    }
    return name_list;
  }

  function runOneClientToolCall(tool_call, message_list, tool_list) {
    var repeat_count;
    if (isRepeatAllowedTool(tool_call, tool_list)) {
      return runClientToolCall(tool_call, tool_list);
    }
    repeat_count = (countToolCalls(message_list)[
      JSON.stringify([tool_call.function.name, tool_call.function.arguments])
    ] || { count: 0 }).count;
    if (repeat_count >= TOOL_CALL_REPEAT_LIMIT) {
      return {
        tool_call_id: tool_call.id,
        name: tool_call.function.name,
        content: "You already called this exact tool with these exact same arguments (" +
          (tool_call.function.arguments.length > 300 ?
              tool_call.function.arguments.slice(0, 300) + "..." : tool_call.function.arguments) + ") " +
          (repeat_count - 1) + " time(s) in the last " + TOOL_CALL_REPEAT_WINDOW + " turns, and it did not help - repeating it again will not " +
          "produce a different result. Stop retrying this exact call: try different arguments, a " +
          "different tool, or report the failure and move on." +
          (repeat_count >= TOOL_CALL_REPEAT_HIDE_LIMIT ?
              " " + TOOL_DISABLED_NOTICE :
              " If you call it again with these same arguments, this tool will be disabled for the " +
              "rest of this task.")
      };
    }
    if (getDisabledToolNameList(message_list).indexOf(tool_call.function.name) !== -1) {
      return {
        tool_call_id: tool_call.id,
        name: tool_call.function.name,
        content: "Not run: it was called again and again with the same arguments before. " +
          TOOL_DISABLED_NOTICE + " Use another tool, or the results you already have."
      };
    }
    return runClientToolCall(tool_call, tool_list);
  }

  function runClientToolCallList(tool_call_list, message_list, tool_list, excluded_tool_name_list) {
    var queue, result_list;

    // Tools hidden from this caller (eg. spawn_subagent for a sub-agent)
    // are not run even if the model calls them anyway.
    if (excluded_tool_name_list && excluded_tool_name_list.length) {
      tool_list = tool_list.filter(function (tool) {
        return excluded_tool_name_list.indexOf(tool.definition.name) === -1;
      });
    }

    if (!tool_call_list.some(function (tool_call) {
        var tool = findClientTool(tool_call.function.name, tool_list);
        return Boolean(tool && tool.definition && tool.definition.executionMode === "sequential");
      })) {
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


  function getNotRunToolResultList(tool_call_list, content) {
    return tool_call_list.map(function (tool_call) {
      return {
        tool_call_id: tool_call.id,
        name: tool_call["function"].name,
        content: content
      };
    });
  }

  function getToolDefinitionList(tool_list, message_list, excluded_tool_name_list) {
    var count_dict = countToolCalls(message_list),
      hidden_tool_name_list = getDisabledToolNameList(message_list).concat(excluded_tool_name_list || []);
    Object.keys(count_dict).forEach(function (key) {
      var name = count_dict[key].name,
        count = count_dict[key].count;
      if (isRepeatAllowedTool({ "function": { name: name } }, tool_list)) {
        return;
      }
      if (count >= TOOL_CALL_REPEAT_STOP_LIMIT) {
        throw new Error("Stopped: the model kept calling \"" + name +
          "\" with the same arguments " + count + " times in the last " + TOOL_CALL_REPEAT_WINDOW +
          " turns after being told to stop.");
      }
      if (count >= TOOL_CALL_REPEAT_HIDE_LIMIT) {
        hidden_tool_name_list.push(name);
      }
    });
    return tool_list.filter(function (tool) {
      return hidden_tool_name_list.indexOf(tool.definition.name) === -1;
    }).map(function (tool) {
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
    // System prompts about using the tools, added by the agent to its own.
    .declareMethod('getToolPromptList', function () {
      return [
        { role: "system", content: TOOL_CALL_REPEAT_SYSTEM_PROMPT }
      ];
    })
    .declareMethod('getToolDefinitionList', function (message_list, excluded_tool_name_list) {
      return getToolDefinitionList(this.tool_list, message_list, excluded_tool_name_list);
    })
    .allowPublicAcquisition('getToolDefinitionList', function (argument_list) {
      return getToolDefinitionList(this.tool_list, argument_list[0], argument_list[1]);
    })
    // Run the tool calls of an LLM response. option_dict:
    // - finish_reason: of that response; if "length", none is run
    // - turn_limit_reached: none is run
    // - excluded_tool_name_list: tools that must not be run
    // Returns {message_list, result_list}: the "tool" messages to append to
    // the conversation, and the results with their extra data for the
    // caller (message_list of a sub-agent, execution_plan, usage_totals).
    .declareMethod('runToolCallList', function (tool_call_list, message_list, option_dict) {
      var gadget = this;
      option_dict = option_dict || {};
      return new RSVP.Queue()
        .push(function () {
          if (option_dict.turn_limit_reached) {
            return getNotRunToolResultList(tool_call_list, TURN_LIMIT_TOOL_CALL_RESULT);
          }
          if (option_dict.finish_reason === "length") {
            return getNotRunToolResultList(tool_call_list, TRUNCATED_TOOL_CALL_RESULT);
          }
          return runClientToolCallList(tool_call_list, message_list, gadget.tool_list,
            option_dict.excluded_tool_name_list);
        })
        .push(function (result_list) {
          // A too large content is cut by read_tool_output, which keeps the
          // full text for the model to read the rest.
          return new RSVP.Queue(gadget.getDeclaredGadget("tool_read_tool_output"))
            .push(function (read_tool_output) {
              return RSVP.all(result_list.map(function (tool_result) {
                return read_tool_output.limitToolOutput(tool_result.content);
              }));
            })
            .push(function (content_list) {
              result_list.forEach(function (tool_result, i) {
                tool_result.content = content_list[i];
              });
              return result_list;
            });
        })
        .push(function (result_list) {
          return {
            message_list: result_list.map(function (tool_result) {
              return {
                role: "tool",
                tool_call_id: tool_result.tool_call_id,
                name: tool_result.name,
                content: tool_result.content
              };
            }),
            result_list: result_list
          };
        });
    })
    .allowPublicAcquisition('runToolCallList', function (argument_list) {
      return this.runToolCallList(argument_list[0], argument_list[1], argument_list[2]);
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
