/*global window, rJS, RSVP, SimpleQuery, ComplexQuery, AbortController, fetch */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, SimpleQuery, ComplexQuery) {
  "use strict";
  // postComment/storeTaskResult consumers only ever read evt.target.getResponseHeader
  // (used to detect a server-side redirect to a freshly created document, which never
  // happens here since we are already viewing an existing document) - stub it so the
  // fake "event" returned by the local versions of these methods behaves the same way.
  function fakeXhrEvent() {
    return {target: {getResponseHeader: function () { return null; }}};
  }

  rJS(window)
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getSettingList", "getSettingList")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("jio_post", "jio_post")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")

    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")

    .allowPublicAcquisition('getCommentPostList', function (argument_list) {
      var gadget = this,
        document_id = argument_list[0];
      return gadget.jio_allDocs({
        query: new ComplexQuery({
          operator: "AND",
          type: "complex",
          query_list: [
            new SimpleQuery({key: "portal_type", type: "simple", value: "Artificial Task Line"}),
            new SimpleQuery({key: "parent_relative_url", type: "simple", value: document_id})
          ]
        }),
        select_list: ["text_content", "int_index", "response", "tool_message_list"],
        sort_on: [["int_index", "ascending"]]
      })
        .push(function (result) {
          var rows = result.data.rows || [];
          gadget.next_int_index = rows.reduce(function (max_index, row) {
            return Math.max(max_index, row.value.int_index || 0);
          }, -1) + 1;
          return rows.map(function (row) {
            return {
              date: new Date().toISOString(),
              text: row.value.text_content,
              tool_message_list: row.value.tool_message_list || "[]",
              response: row.value.response || false
            };
          });
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
        response: false
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
        payload;

      if (!settings.apiKey || !settings.baseUrl) {
        throw new Error(
          "No LLM API key/base URL configured - open Setting from the panel first."
        );
      }

      if (body.compact_message_list !== undefined) {
        payload = {
          model: settings.model,
          messages: [{
            role: "system",
            content: "Summarize the following conversation concisely, preserving " +
              "any information needed to continue the task."
          }].concat(JSON.parse(body.compact_message_list))
        };
      } else {
        payload = {
          model: settings.model,
          messages: JSON.parse(body.message_list),
          tools: JSON.parse(body.tool_definition_list)
        };
      }

      return new RSVP.Queue(new RSVP.Promise(function (resolve, reject) {
        fetch(settings.baseUrl.replace(/\/+$/, '') + "/chat/completions", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + settings.apiKey
          },
          body: JSON.stringify(payload),
          signal: controller.signal
        }).then(resolve, reject);
      }, function canceller() {
        controller.abort();
      }))
        .push(function (response) {
          if (!response.ok) {
            return response.text().then(function (text) {
              throw new Error("LLM " + response.status + " error: " + text.slice(0, 1000));
            });
          }
          return response.json();
        })
        .push(function (response) {
          var message;
          if (response.error) {
            throw new Error(typeof response.error === "string" ? response.error :
              (response.error.message || JSON.stringify(response.error)));
          }
          message = response.choices[0].message;
          if (message.tool_calls) {
            return {
              content: message.content || "",
              tool_calls: message.tool_calls
            };
          }
          response.content = message.content;
          return response;
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
        trace: trace,
        tool_message_list: JSON.stringify(tool_message_list)
      })
        .push(function () {
          if (gadget.state.doc.state === 'planned') {
            gadget.state.doc.state = 'completed';
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
      return gadget.getSettingList(["hateoas_url", "baseUrl", "apiKey", "model"])
        .push(function (setting_list) {
          gadget.hateoas_url = setting_list[0];
          gadget.llm_settings = {
            baseUrl: setting_list[1] || '',
            apiKey: setting_list[2] || '',
            model: setting_list[3] || ''
          };
          return gadget.changeState({
            jio_key: options.jio_key,
            doc: options.doc
          });
        });
    })
    .onStateChange(function () {
      var gadget = this;
      return gadget.getDeclaredGadget("gadget_chat")
        .push(function (chat_gadget) {
          return chat_gadget.render({
            'chat_state': gadget.state.doc.state,
            'hateoas_url': gadget.hateoas_url,
            'jio_key': gadget.state.jio_key,
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
