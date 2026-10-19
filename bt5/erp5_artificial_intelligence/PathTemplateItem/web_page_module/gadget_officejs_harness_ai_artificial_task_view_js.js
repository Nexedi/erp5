/*global window, rJS, RSVP, SimpleQuery, ComplexQuery, AbortController, fetch, TextDecoder */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, SimpleQuery, ComplexQuery) {
  "use strict";

  function fakeXhrEvent() {
    return {target: {getResponseHeader: function () { return null; }}};
  }


  // JSON with every non-ASCII code point escaped, so it stays valid in an
  // HTTP header (ported from ai-agent-harness's js/util.js asciiJSON).
  function asciiJSON(value) {
    return JSON.stringify(value).replace(/[\u0080-\uffff]/g, function (c) {
      var code = c.charCodeAt(0).toString(16);
      while (code.length < 4) {
        code = "0" + code;
      }
      return "\\u" + code;
    });
  }


  function applyStreamChunk(json, state) {
    var choice = json.choices && json.choices[0], delta, content_grew = false;
    if (json.error) {
      state.error = json.error;
      return false;
    }
    if (json.model) {
      state.model = json.model;
    }
    if (json.usage) {
      state.usage = json.usage;
    }
    if (!choice) {
      return false;
    }
    delta = choice.delta || {};
    if (delta.content) {
      state.content += delta.content;
      content_grew = true;
    }
    if (delta.tool_calls) {
      delta.tool_calls.forEach(function (tc) {
        var index = tc.index || 0, entry = state.tool_call_map[index];
        if (!entry) {
          entry = {id: tc.id || "", type: tc.type || "function", "function": {name: "", arguments: ""}};
          state.tool_call_map[index] = entry;
          state.tool_call_order.push(index);
        }
        if (tc.id) {
          entry.id = tc.id;
        }
        if (tc["function"]) {
          if (tc["function"].name) {
            entry["function"].name += tc["function"].name;
          }
          if (tc["function"].arguments) {
            entry["function"].arguments += tc["function"].arguments;
          }
        }
      });
    }
    return content_grew;
  }

  function consumeOpenAIStream(response, on_delta) {
    var reader = response.body.getReader(),
      decoder = new TextDecoder(),
      buffer = "",
      state = {content: "", model: null, usage: null, error: null, tool_call_map: {}, tool_call_order: []};

    function handleFrame(frame) {
      var data_line, json;
      data_line = frame.split("\n").filter(function (line) {
        return line.indexOf("data:") === 0;
      })[0];
      if (!data_line) {
        return;
      }
      data_line = data_line.slice(5).trim();
      if (data_line === "" || data_line === "[DONE]") {
        return;
      }
      try {
        json = JSON.parse(data_line);
      } catch (ignore) {
        return;
      }
      if (applyStreamChunk(json, state) && on_delta) {
        on_delta({content: state.content});
      }
    }

    function pump() {
      return new RSVP.Queue(reader.read()).push(function (step) {
        var split;
        if (step.done) {
          if (buffer) {
            handleFrame(buffer);
          }
          return;
        }
        buffer += decoder.decode(step.value, {stream: true});
        split = buffer.indexOf("\n\n");
        while (split !== -1) {
          handleFrame(buffer.slice(0, split));
          buffer = buffer.slice(split + 2);
          split = buffer.indexOf("\n\n");
        }
        return pump();
      });
    }

    return new RSVP.Queue()
      .push(function () {
        return pump();
      })
      .push(function () {
        var tool_calls;
        if (state.error) {
          throw new Error(typeof state.error === "string" ? state.error :
            (state.error.message || JSON.stringify(state.error)));
        }
        tool_calls = state.tool_call_order.map(function (index) {
          return state.tool_call_map[index];
        });
        if (tool_calls.length) {
          return {content: state.content || "", tool_calls: tool_calls};
        }
        return {content: state.content, model: state.model, usage: state.usage};
      });
  }



  rJS(window)
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getSettingList", "getSettingList")
    .declareAcquiredMethod("setSettingList", "setSettingList")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("jio_post", "jio_post")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("jio_remove", "jio_remove")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")

    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")

    .allowPublicAcquisition('getCommentPostList', function (argument_list) {
      var gadget = this,
        document_id = argument_list[0],
        task_line_row_list;
      return gadget.jio_allDocs({
        query: new ComplexQuery({
          operator: "AND",
          type: "complex",
          query_list: [
            new SimpleQuery({key: "portal_type", type: "simple", value: "Artificial Task Line"}),
            new SimpleQuery({key: "parent_relative_url", type: "simple", value: document_id})
          ]
        }),
        select_list: ["text_content", "int_index", "response", "tool_message_list", "author_title", "date"],
        sort_on: [["int_index", "ascending"]]
      })
        .push(function (task_line_result) {
          task_line_row_list = task_line_result.data.rows || [];

          gadget.next_int_index = task_line_row_list.reduce(function (max_index, row) {
            return Math.max(max_index, row.value.int_index || 0);
          }, -1) + 1;

          if (!task_line_row_list.length) {
            return {data: {rows: []}};
          }
          return gadget.jio_allDocs({
            query: new ComplexQuery({
              operator: "AND",
              type: "complex",
              query_list: [
                new SimpleQuery({key: "portal_type", type: "simple", value: "Artificial Task Execution Plan"}),
                new ComplexQuery({
                  operator: "OR",
                  type: "complex",
                  query_list: task_line_row_list.map(function (row) {
                    return new SimpleQuery({key: "follow_up_relative_url", type: "simple", value: row.id});
                  })
                })
              ]
            }),
            select_list: ["follow_up_relative_url"]
          });
        })
        .push(function (plan_result) {
          var plan_id_by_task_line_id = {},
            own_plan_id_list = [];
          (plan_result.data.rows || []).forEach(function (row) {
            var task_line_id = row.value.follow_up_relative_url;
            plan_id_by_task_line_id[task_line_id] = row.id;
            own_plan_id_list.push(row.id);
          });
          if (!own_plan_id_list.length) {
            return {plan_id_by_task_line_id: plan_id_by_task_line_id, line_result: {data: {rows: []}}};
          }
          return gadget.jio_allDocs({
            query: new ComplexQuery({
              operator: "OR",
              type: "complex",
              query_list: own_plan_id_list.map(function (plan_id) {
                return new SimpleQuery({key: "parent_relative_url", type: "simple", value: plan_id});
              })
            }),
            select_list: ["parent_relative_url", "int_index", "text_content"],
            sort_on: [["int_index", "ascending"]]
          })
            .push(function (line_result) {
              return {plan_id_by_task_line_id: plan_id_by_task_line_id, line_result: line_result};
            });
        })
        .push(function (joined) {
          var plan_id_by_task_line_id = joined.plan_id_by_task_line_id,
            step_row_list_by_plan_id = {},
            plan_json_by_task_line_id = {};
          (joined.line_result.data.rows || []).forEach(function (row) {
            var plan_id = row.value.parent_relative_url;
            if (!step_row_list_by_plan_id[plan_id]) {
              step_row_list_by_plan_id[plan_id] = [];
            }
            step_row_list_by_plan_id[plan_id].push(row.value);
          });
          Object.keys(plan_id_by_task_line_id).forEach(function (task_line_id) {
            var plan_id = plan_id_by_task_line_id[task_line_id],
              step_row_list = step_row_list_by_plan_id[plan_id] || [],
              goal = "",
              step_list = step_row_list.map(function (step_row) {
                var step_data = {};
                try {
                  step_data = JSON.parse(step_row.text_content || "{}");
                } catch (ignore) {}
                if (step_data.goal) {
                  goal = step_data.goal;
                }
                return { title: step_data.title, status: step_data.status, note: step_data.note };
              });
            if (step_list.length) {
              plan_json_by_task_line_id[task_line_id] = JSON.stringify({ goal: goal, step_list: step_list });
            }
          });
          return task_line_row_list.map(function (row) {
            return {
              date: row.value.date || new Date().toISOString(),
              text: row.value.text_content,
              tool_message_list: row.value.tool_message_list || "[]",
              response: row.value.response || false,
              author_title: row.value.author_title || "",
              execution_plan: plan_json_by_task_line_id[row.id] || ""
            };
          });
        });
    })
    .allowPublicAcquisition('getDefinedToolList', function () {
      var gadget = this;
      return gadget.jio_allDocs({
        query: new SimpleQuery({key: "portal_type", type: "simple", value: "Web Script"}),
        select_list: ["reference", "text_content"]
      })
        .push(function (result) {
          return (result.data.rows || []).map(function (row) {
            var data = {};
            try {
              data = JSON.parse(row.value.text_content || "{}");
            } catch (ignore) {}
            return {
              name: row.value.reference,
              description: data.description || "",
              parameters: data.parameters,
              code: data.code,
              libraries: data.libraries
            };
          });
        });
    })
    .allowPublicAcquisition('storeDefinedTool', function (argument_list) {
      var gadget = this,
        spec = argument_list[0];
      return gadget.jio_post({
        portal_type: 'Web Script',
        reference: spec.name,
        title: spec.name,
        date: new Date().toISOString(),
        text_content: JSON.stringify({
          description: spec.description,
          parameters: spec.parameters,
          code: spec.code,
          libraries: spec.libraries
        })
      });
    })
    .allowPublicAcquisition('removeDefinedTool', function (argument_list) {
      var gadget = this,
        name = argument_list[0];
      return gadget.jio_allDocs({
        query: new ComplexQuery({
          operator: "AND",
          type: "complex",
          query_list: [
            new SimpleQuery({key: "portal_type", type: "simple", value: "Web Script"}),
            new SimpleQuery({key: "reference", type: "simple", value: name})
          ]
        }),
        select_list: []
      })
        .push(function (result) {
          return RSVP.all((result.data.rows || []).map(function (row) {
            return gadget.jio_remove(row.id);
          }));
        });
    })
    .allowPublicAcquisition('postComment', function (argument_list) {
      var gadget = this,
        document_id = argument_list[0],
        form_data_json = argument_list[1],
        int_index = gadget.next_int_index || 0;
      gadget.next_int_index = int_index + 1;
      return gadget.jio_post({
        portal_type: 'Artificial Task Line',
        parent_relative_url: document_id,
        text_content: form_data_json.data,
        int_index: int_index,
        response: false,
        author_title: "",
        date: new Date().toISOString()
      })
        .push(function () {
          return fakeXhrEvent();
        });
    })
    .allowPublicAcquisition('requestProcessTask', function (argument_list) {
      var gadget = this,
        body = argument_list[1],
        settings = gadget.llm_settings,
        controller = new AbortController(),
        target = settings.baseUrl ?
            settings.baseUrl.replace(/\/+$/, '') + "/" + (settings.endpoint || "chat/completions").replace(/^\/+/, '') :
            "",
        payload,
        fetch_url,
        fetch_options;

      if (!settings.apiKey || !settings.baseUrl) {
        throw new Error(
          "No LLM API key/base URL configured - open Setting from the panel first."
        );
      }

      if (body.compact_message_list !== undefined) {
        payload = {
          model: settings.model,
          stream: true,
          messages: [{
            role: "system",
            content: "Summarize the following conversation concisely, preserving " +
              "any information needed to continue the task."
          }].concat(JSON.parse(body.compact_message_list))
        };
      } else {
        payload = {
          model: settings.model,
          stream: true,
          messages: JSON.parse(body.message_list),
          tools: JSON.parse(body.tool_definition_list)
        };
      }

      if (settings.proxy_server_url) {
        fetch_url = settings.proxy_server_url.replace(/\/+$/, '') + "/proxy";
        fetch_options = {
          method: "POST",
          headers: {
            "Content-Type": "application/octet-stream",
            "X-Target-URL": encodeURI(target),
            "X-Target-Method": "POST",
            "X-Target-Headers": asciiJSON({
              "Content-Type": "application/json",
              "Authorization": "Bearer " + settings.apiKey
            })
          },
          body: JSON.stringify(payload),
          signal: controller.signal
        };
      } else {
        fetch_url = target;
        fetch_options = {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + settings.apiKey
          },
          body: JSON.stringify(payload),
          signal: controller.signal
        };
      }

      return new RSVP.Promise(function (resolve, reject) {
        fetch(fetch_url, fetch_options)
          .then(function (response) {
            if (!response.ok) {
              return response.text().then(function (text) {
                throw new Error("LLM " + response.status + " error: " + text.slice(0, 1000));
              });
            }
            return consumeOpenAIStream(
              response,
              (body.is_subagent || body.compact_message_list !== undefined) ? undefined :
                function onDelta(partial) {
                  return gadget.chat_gadget.showStreamingDelta(partial);
                }
            );
          })
          .then(resolve, reject);
      }, function canceller() {
        controller.abort();
      });
    })
    .allowPublicAcquisition('storeTaskResult', function (argument_list) {
      var gadget = this,
        document_id = argument_list[0],
        body = argument_list[1],
        int_index = gadget.next_int_index || 0,
        message_list = body.message_list ? JSON.parse(body.message_list) : [],
        tool_message_list =  message_list.slice(0, -1),
        trace = message_list[message_list.length - 1];
      gadget.next_int_index = int_index + 1;
      return gadget.jio_post({
        portal_type: 'Artificial Task Line',
        parent_relative_url: document_id,
        text_content: body.content,
        int_index: int_index,
        response: true,
        author_title: "Assistant",
        date: new Date().toISOString(),
        trace: trace,
        tool_message_list: JSON.stringify(tool_message_list)
      })
        .push(function (task_line_id) {
          var plan = body.execution_plan ? JSON.parse(body.execution_plan) : null;
          if (!plan || !plan.step_list || !plan.step_list.length) {
            return;
          }
          return gadget.jio_post({
            portal_type: 'Artificial Task Execution Plan',
            follow_up_relative_url: task_line_id,
            date: new Date().toISOString()
          })
            .push(function (plan_id) {
              return RSVP.all(plan.step_list.map(function (step, index) {
                return gadget.jio_post({
                  portal_type: 'Artificial Task Execution Plan Line',
                  parent_relative_url: plan_id,
                  int_index: index,
                  text_content: JSON.stringify({
                    goal: plan.goal,
                    title: step.title,
                    status: step.status,
                    note: step.note
                  })
                });
              }));
            });
        })
        .push(function () {
          if (gadget.state.doc.state === 'started') {
            gadget.state.doc.state = 'stopped';
            return gadget.jio_put(document_id, gadget.state.doc);
          }
        })
        .push(function () {
          return fakeXhrEvent();
        });
    })

    .declareMethod('render', function (options) {
      var gadget = this;
      gadget.options = options;
      return gadget.getSettingList(
        ["hateoas_url", "baseUrl", "apiKey", "model", "proxy_server_url", "endpoint", "mcp_server_list", "mcp_oauth_token_map"]
      )
        .push(function (setting_list) {
          gadget.hateoas_url = setting_list[0];
          gadget.mcp_oauth_token_map = setting_list[7] ? JSON.parse(setting_list[7]) : {};
          gadget.llm_settings = {
            baseUrl: setting_list[1] || '',
            apiKey: setting_list[2] || '',
            model: setting_list[3] || '',
            proxy_server_url: setting_list[4] || '',
            endpoint: setting_list[5] || 'chat/completions'
          };
          gadget.mcp_server_list = window.ChatMCP.parseServerListText(setting_list[6] || '').value || [];
          gadget.mcp_server_list.forEach(function (server_config) {
            var oauth_state = gadget.mcp_oauth_token_map[server_config.name];
            if (!server_config.token && oauth_state && oauth_state.access_token) {
              server_config.token = oauth_state.access_token;
            }
          });
        })
        .push(function () {
          return gadget.changeState({
            jio_key: options.jio_key,
            doc: options.doc
          });
        });
    })

    .allowPublicAcquisition('refreshMcpServerAuth', function (argument_list) {
      var gadget = this,
        server_config = argument_list[0],
        oauth_state = gadget.mcp_oauth_token_map[server_config.name];
      return new RSVP.Queue(window.ChatMCPOAuth.refresh(oauth_state))
        .push(function (refreshed) {
          if (!refreshed) {
            return null;
          }
          gadget.mcp_oauth_token_map[server_config.name] = refreshed;
          return gadget.setSettingList({
            mcp_oauth_token_map: JSON.stringify(gadget.mcp_oauth_token_map)
          })
            .push(function () {
              return refreshed;
            });
        });
    })
    .onStateChange(function () {
      var gadget = this;
      return gadget.getDeclaredGadget("gadget_chat")
        .push(function (chat_gadget) {
          gadget.chat_gadget = chat_gadget;
          return chat_gadget.render({
            'chat_state': gadget.state.doc.state,
            'hateoas_url': gadget.hateoas_url,
            'jio_key': gadget.state.jio_key,
            'mcp_server_list': gadget.mcp_server_list,
            'proxy_server_url': gadget.llm_settings.proxy_server_url,
            'editor_options': {
              editor: 'gadget_editor.html',
              options: {
                value: "",
                key: "comment",
                portal_type: "Artificial Task Line",
                editable: true,
                editor: 'codemirror',
                maximize: true
              }
            }
          });
        })
        .push(function () {
          return RSVP.all([
            gadget.getUrlFor({command: 'history_previous'}),
            gadget.getUrlFor({command: 'selection_previous'}),
            gadget.getUrlFor({command: 'selection_next'})
          ]);
        })
        .push(function (all_result) {
          return gadget.updateHeader({
            selection_url: all_result[0],
            previous_url: all_result[1],
            next_url: all_result[2],
            page_title: gadget.state.doc.title
          });
        });
    });
}(window, rJS, RSVP, SimpleQuery, ComplexQuery));
