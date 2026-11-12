/*global window, rJS, RSVP, SimpleQuery, ComplexQuery, AbortController, fetch, TextDecoder */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, SimpleQuery, ComplexQuery) {
  "use strict";

  // Fields in which OpenAI-compatible servers stream the model reasoning
  // (llama.cpp and vLLM use reasoning_content). Some servers send the same
  // text in two of them, so only the first field seen is kept.
  var REASONING_FIELD_LIST = ["reasoning_content", "reasoning", "reasoning_text"];

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
    var choice = json.choices && json.choices[0], delta, grew = false, i, field;
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
    if (choice.finish_reason) {
      state.finish_reason = choice.finish_reason;
    }
    delta = choice.delta || {};
    for (i = 0; i < REASONING_FIELD_LIST.length; i += 1) {
      field = REASONING_FIELD_LIST[i];
      if (typeof delta[field] === "string" && delta[field] &&
          (state.reasoning_field === null || state.reasoning_field === field)) {
        state.reasoning_field = field;
        state.reasoning += delta[field];
        grew = true;
      }
    }
    if (delta.content) {
      state.content += delta.content;
      grew = true;
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
    return grew;
  }

  // start_time: when the request was sent, to time the response: the
  // result has timing {duration_ms, first_token_ms}, and its usage has
  // duration_ms too, for the totals of the task.
  function consumeOpenAIStream(response, on_delta, start_time) {
    var reader = response.body.getReader(),
      decoder = new TextDecoder(),
      buffer = "",
      state = {content: "", reasoning: "", reasoning_field: null, model: null, usage: null, finish_reason: null,
        done: false, first_token_time: null,
        error: null, tool_call_map: {}, tool_call_order: []};

    // A frame may hold several "data:" lines: per the SSE spec they are one
    // value joined by "\n".
    function handleFrame(frame) {
      var data_line_list, data_line, json;
      data_line_list = frame.split("\n").filter(function (line) {
        return line.indexOf("data:") === 0;
      });
      if (!data_line_list.length) {
        return;
      }
      data_line = data_line_list.map(function (line) {
        return line.slice(line.charAt(5) === " " ? 6 : 5);
      }).join("\n").trim();
      if (data_line === "[DONE]") {
        state.done = true;
        return;
      }
      if (data_line === "") {
        return;
      }
      try {
        json = JSON.parse(data_line);
      } catch (ignore) {
        return;
      }
      if (state.first_token_time === null && json.choices && json.choices.length) {
        state.first_token_time = Date.now();
      }
      if (applyStreamChunk(json, state) && on_delta) {
        on_delta({content: state.content, reasoning: state.reasoning});
      }
    }

    function pump() {
      return new RSVP.Queue(reader.read()).push(function (step) {
        var split;
        if (step.done) {
          if (buffer) {
            handleFrame(buffer.replace(/\r/g, "\n"));
          }
          return;
        }
        // Servers may frame events with "\r\n": normalize before splitting.
        // A lone "\r" at the end may be the first half of a "\r\n" split
        // across two reads, so it waits for the next one.
        buffer = (buffer + decoder.decode(step.value, {stream: true})).replace(/\r\n|\r(?!$)/g, "\n");
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
        var tool_calls, message, timing, usage;
        if (state.error) {
          throw new Error(typeof state.error === "string" ? state.error :
            (state.error.message || JSON.stringify(state.error)));
        }
        // A forwarder relays the stream until its end of file: if the LLM
        // server connection breaks, the stream just ends, without
        // finish_reason nor [DONE]. Its content is then incomplete.
        if (!state.done && !state.finish_reason) {
          throw new Error("LLM stream ended before the end of the response: the connection was lost");
        }
        tool_calls = state.tool_call_order.map(function (index) {
          return state.tool_call_map[index];
        });
        timing = {
          duration_ms: Date.now() - start_time,
          first_token_ms: state.first_token_time === null ? null : state.first_token_time - start_time
        };
        // The usage reported by the server (0 if it did not), in the shape
        // of the usage totals the callers add up (ChatToolCommon.addUsageTotals).
        // cached_tokens: the prompt tokens read from the prompt cache of the
        // server (prompt_tokens_details.cached_tokens of OpenAI, vLLM,
        // llama.cpp and OpenRouter, prompt_cache_hit_tokens of DeepSeek).
        usage = state.usage || {};
        usage = {
          call_count: 1,
          prompt_tokens: usage.prompt_tokens || 0,
          completion_tokens: usage.completion_tokens || 0,
          total_tokens: usage.total_tokens || ((usage.prompt_tokens || 0) + (usage.completion_tokens || 0)),
          cached_tokens: (usage.prompt_tokens_details && usage.prompt_tokens_details.cached_tokens) ||
            usage.prompt_cache_hit_tokens || 0,
          duration_ms: timing.duration_ms
        };
        if (tool_calls.length) {
          // The assistant message to append to the conversation before the
          // tool results. The reasoning is sent back in the field the server
          // used, so the model still sees why it made these calls.
          message = {role: "assistant", content: state.content || "", tool_calls: tool_calls};
          if (state.reasoning && state.reasoning_field) {
            message[state.reasoning_field] = state.reasoning;
          }
          return {content: state.content || "", tool_calls: tool_calls, message: message, usage: usage,
            finish_reason: state.finish_reason, reasoning: state.reasoning, reasoning_field: state.reasoning_field,
            timing: timing};
        }
        return {content: state.content, model: state.model, usage: usage, finish_reason: state.finish_reason,
          reasoning: state.reasoning, reasoning_field: state.reasoning_field, timing: timing};
      });
  }



  // The row of the Artificial Task Compaction of the task, or null.
  function findTaskCompactionRow(gadget, document_id) {
    return gadget.jio_allDocs({
      query: new ComplexQuery({
        operator: "AND",
        type: "complex",
        query_list: [
          new SimpleQuery({key: "portal_type", type: "simple", value: "Artificial Task Compaction"}),
          new SimpleQuery({key: "parent_relative_url", type: "simple", value: document_id})
        ]
      }),
      select_list: ["text_content", "int_index"],
      limit: [0, 1]
    })
      .push(function (result) {
        return (result.data.rows || [])[0] || null;
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
        document_id = argument_list[0];
      // The local storage (indexeddb) can not run a query: jIO reads all its
      // documents for each allDocs. So the lines, their attachments and their
      // execution plans are read with one allDocs, and joined here.
      return gadget.jio_allDocs({
        query: new ComplexQuery({
          operator: "OR",
          type: "complex",
          query_list: [
            "Artificial Task Line",
            "Document",
            "Artificial Task Execution Plan",
            "Artificial Task Execution Plan Line"
          ].map(function (portal_type) {
            return new SimpleQuery({key: "portal_type", type: "simple", value: portal_type});
          })
        }),
        select_list: ["portal_type", "parent_relative_url", "follow_up_relative_url", "text_content",
          "int_index", "response", "tool_message_list", "author_title", "date", "url", "file_name"]
      })
        .push(function (result) {
          var row_list = result.data.rows || [],
            task_line_row_list = [],
            is_task_line_id = {},
            attachment_by_task_line_id = {},
            plan_id_by_task_line_id = {},
            step_row_list_by_plan_id = {},
            plan_json_by_task_line_id = {};
          row_list.forEach(function (row) {
            if (row.value.portal_type === "Artificial Task Line" &&
                row.value.parent_relative_url === document_id) {
              task_line_row_list.push(row);
              is_task_line_id[row.id] = true;
            }
          });
          task_line_row_list.sort(function (a, b) {
            return (a.value.int_index || 0) - (b.value.int_index || 0);
          });
          gadget.next_int_index = task_line_row_list.reduce(function (max_index, row) {
            return Math.max(max_index, row.value.int_index || 0);
          }, -1) + 1;

          row_list.forEach(function (row) {
            var task_line_id = row.value.follow_up_relative_url;
            if (!is_task_line_id.hasOwnProperty(task_line_id)) {
              return;
            }
            if (row.value.portal_type === "Document") {
              attachment_by_task_line_id[task_line_id] = {
                link: row.value.url,
                name: row.value.file_name || row.id
              };
            } else if (row.value.portal_type === "Artificial Task Execution Plan") {
              plan_id_by_task_line_id[task_line_id] = row.id;
              step_row_list_by_plan_id[row.id] = [];
            }
          });
          row_list.forEach(function (row) {
            if (row.value.portal_type === "Artificial Task Execution Plan Line" &&
                step_row_list_by_plan_id.hasOwnProperty(row.value.parent_relative_url)) {
              step_row_list_by_plan_id[row.value.parent_relative_url].push(row.value);
            }
          });

          Object.keys(plan_id_by_task_line_id).forEach(function (task_line_id) {
            var goal = "",
              step_list = step_row_list_by_plan_id[plan_id_by_task_line_id[task_line_id]]
                .sort(function (a, b) {
                  return (a.int_index || 0) - (b.int_index || 0);
                })
                .map(function (step_row) {
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
            var attachment = attachment_by_task_line_id[row.id];
            return {
              int_index: row.value.int_index || 0,
              date: row.value.date || new Date().toISOString(),
              text: row.value.text_content,
              tool_message_list: row.value.tool_message_list || "[]",
              response: row.value.response || false,
              author_title: row.value.author_title || "",
              execution_plan: plan_json_by_task_line_id[row.id] || "",
              attachment_link: attachment ? attachment.link : null,
              attachment_name: attachment ? attachment.name : null
            };
          });
        });
    })
    // The summary of the older posts of the task, stored by
    // storeTaskCompaction: {summary, summarized_before_int_index}, or null. The
    // posts before summarized_before_int_index are replaced by the summary.
    .allowPublicAcquisition('getTaskCompaction', function (argument_list) {
      return findTaskCompactionRow(this, argument_list[0])
        .push(function (row) {
          if (!row || !row.value.text_content) {
            return null;
          }
          return {
            summary: row.value.text_content,
            summarized_before_int_index: row.value.int_index || 0
          };
        });
    })
    // One summary per task: updated if the task has one, created otherwise.
    .allowPublicAcquisition('storeTaskCompaction', function (argument_list) {
      var gadget = this,
        document_id = argument_list[0],
        compaction = argument_list[1],
        doc = {
          portal_type: 'Artificial Task Compaction',
          parent_relative_url: document_id,
          text_content: compaction.summary,
          int_index: compaction.summarized_before_int_index,
          date: new Date().toISOString()
        };
      return findTaskCompactionRow(gadget, document_id)
        .push(function (row) {
          if (row) {
            return gadget.jio_put(row.id, doc);
          }
          return gadget.jio_post(doc);
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
        file = form_data_json.file,
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
        .push(function (task_line_id) {
          if (file && file.url) {
            return gadget.jio_post({
              portal_type: 'Document',
              parent_relative_url: 'document_module',
              title: file.file_name,
              url: file.url,
              file_name: file.file_name,
              follow_up_relative_url: task_line_id,
              date: new Date().toISOString()
            });
          }
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
        tool_definition_list,
        // When the request is sent, to time it.
        start_time,
        fetch_url,
        fetch_options;

      if (!settings.apiKey || !settings.baseUrl) {
        throw new Error(
          "No LLM API key/base URL configured - open Setting from the panel first."
        );
      }

      payload = {
        model: settings.model,
        stream: true,
        stream_options: {include_usage: true},
        messages: JSON.parse(body.message_list)
      };
      tool_definition_list = JSON.parse(body.tool_definition_list);
      // if thinking is enabled
      if (settings.thinking) {
        payload.chat_template_kwargs = {enable_thinking: true, preserve_thinking: true};
      }
      if (tool_definition_list.length) {
        payload.tools = tool_definition_list;
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
        start_time = Date.now();
        fetch(fetch_url, fetch_options)
          .then(function (response) {
            if (!response.ok) {
              return response.text().then(function (text) {
                var error = new Error("LLM " + response.status + " error: " + text.slice(0, 1000)),
                  retry_after_ms = response.headers.get("retry-after-ms"),
                  retry_after = response.headers.get("retry-after");
                // Kept on the error so the agent can wait as long as the
                // server asks before retrying a 429 or 5xx.
                error.status = response.status;
                if (retry_after_ms && !isNaN(Number(retry_after_ms))) {
                  error.retry_after_ms = Number(retry_after_ms);
                } else if (retry_after) {
                  error.retry_after_ms = !isNaN(Number(retry_after)) ? Number(retry_after) * 1000 :
                      Math.max(0, Date.parse(retry_after) - Date.now()) || undefined;
                }
                throw error;
              });
            }
            return consumeOpenAIStream(
              response,
              body.is_background ? undefined :
                function onDelta(partial) {
                  return gadget.agent_gadget.showStreamingDelta(partial);
                },
              start_time
            );
          })
          .then(resolve, reject);
      }, function canceller() {
        controller.abort();
      });
    })
    .allowPublicAcquisition('getModelContextWindow', function () {
      var gadget = this,
        settings = gadget.llm_settings,
        target,
        headers;
      // Fetched once per render: undefined = not fetched yet, null = unknown.
      if (gadget.model_context_window !== undefined) {
        return gadget.model_context_window;
      }
      if (!settings.apiKey || !settings.baseUrl || !settings.model) {
        return null;
      }
      target = settings.baseUrl.replace(/\/+$/, '') + "/models";
      headers = {"Authorization": "Bearer " + settings.apiKey};
      return new RSVP.Queue()
        .push(function () {
          if (settings.proxy_server_url) {
            return fetch(settings.proxy_server_url.replace(/\/+$/, '') + "/proxy", {
              method: "POST",
              headers: {
                "Content-Type": "application/octet-stream",
                "X-Target-URL": encodeURI(target),
                "X-Target-Method": "GET",
                "X-Target-Headers": asciiJSON(headers)
              }
            });
          }
          return fetch(target, {headers: headers});
        })
        .push(function (response) {
          if (!response.ok) {
            return null;
          }
          return response.json();
        })
        .push(function (json) {
          var model_list = (json && json.data) || [],
            model_info,
            value,
            i;
          for (i = 0; i < model_list.length; i += 1) {
            if (model_list[i].id === settings.model) {
              model_info = model_list[i];
              value = parseInt(model_info.context_length || model_info.context_window ||
                model_info.max_model_len || model_info.max_context_length ||
                (model_info.top_provider && model_info.top_provider.context_length), 10);
              return value > 0 ? value : null;
            }
          }
          return null;
        })
        .push(undefined, function () {
          return null;
        })
        .push(function (context_window) {
          gadget.model_context_window = context_window;
          return context_window;
        });
    })
    .allowPublicAcquisition('storeTaskResult', function (argument_list) {
      var gadget = this,
        document_id = argument_list[0],
        body = argument_list[1],
        int_index = gadget.next_int_index || 0;
      gadget.next_int_index = int_index + 1;
      return gadget.jio_post({
        portal_type: 'Artificial Task Line',
        parent_relative_url: document_id,
        text_content: body.content,
        int_index: int_index,
        response: true,
        author_title: "Assistant",
        date: new Date().toISOString(),
        tool_message_list: body.tool_message_list || "[]"
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
        ["hateoas_url", "baseUrl", "apiKey", "model", "proxy_server_url", "endpoint", "mcp_server_list", "mcp_oauth_token_map",
          "thinking"]
      )
        .push(function (setting_list) {
          gadget.hateoas_url = setting_list[0];
          gadget.mcp_oauth_token_map = setting_list[7] ? JSON.parse(setting_list[7]) : {};
          gadget.llm_settings = {
            baseUrl: setting_list[1] || '',
            apiKey: setting_list[2] || '',
            model: setting_list[3] || '',
            proxy_server_url: setting_list[4] || '',
            endpoint: setting_list[5] || 'chat/completions',
            thinking: Boolean(setting_list[8])
          };
          gadget.model_context_window = undefined;
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
      return gadget.getDeclaredGadget("gadget_agent")
        .push(function (agent_gadget) {
          gadget.agent_gadget = agent_gadget;
          return agent_gadget.render({
            'chat_state': gadget.state.doc.state,
            'hateoas_url': gadget.hateoas_url,
            'jio_key': gadget.state.jio_key,
            'mcp_server_list': gadget.mcp_server_list,
            'proxy_server_url': gadget.llm_settings.proxy_server_url,
            'disable_comment_poll': true,
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
