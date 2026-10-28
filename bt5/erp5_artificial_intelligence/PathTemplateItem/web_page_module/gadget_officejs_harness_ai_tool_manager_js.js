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
    ];

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
            return !window.ChatToolCommon.findClientTool(spec.name, gadget.tool_list);
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
    .declareMethod('getToolList', function () {
      return this.tool_list;
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
    });
}(window, rJS, RSVP));
