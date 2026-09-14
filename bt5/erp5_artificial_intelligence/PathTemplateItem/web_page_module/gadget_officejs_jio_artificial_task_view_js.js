/*global window, rJS, RSVP, jIO */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, jIO) {
  "use strict";
  function readLLMSettings(gadget) {
    return gadget.getSettingList(["baseUrl", "apiKey", "model"])
      .push(function (setting_list) {
        return {
          baseUrl: setting_list[0] || '',
          apiKey: setting_list[1] || '',
          model: setting_list[2] || ''
        };
      });
  }

  function historyStorageKey(document_id) {
    return 'officejs_harness_ai.history.' + document_id;
  }

  function readHistory(document_id) {
    var history_list = [];
    try {
      history_list = JSON.parse(window.localStorage.getItem(historyStorageKey(document_id)) || '[]');
    } catch (ignore) {
      history_list = [];
    }
    return history_list;
  }

  function appendHistory(document_id, post) {
    var history_list = readHistory(document_id);
    history_list.push(post);
    window.localStorage.setItem(historyStorageKey(document_id), JSON.stringify(history_list));
    return post;
  }

  // postComment/storeTaskResult consumers only ever read evt.target.getResponseHeader
  // (used to detect a server-side redirect to a freshly created document, which never
  // happens here since we are already viewing an existing document) - stub it so the
  // fake "event" returned by the local versions of these methods behaves the same way.
  function fakeXhrEvent() {
    return {target: {getResponseHeader: function () { return null; }}};
  }

  rJS(window)
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("getSettingList", "getSettingList")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")

    .allowPublicAcquisition('getCommentPostList', function (argument_list) {
      var document_id = argument_list[0];
      return readHistory(document_id);
    })
    .allowPublicAcquisition('postComment', function (argument_list) {
      var document_id = argument_list[0],
        form_data = argument_list[1];
      appendHistory(document_id, {
        date: new Date().toISOString(),
        text: form_data.data || "",
        tool_message_list: "[]",
        response: false
      });
      return fakeXhrEvent();
    })
    .allowPublicAcquisition('requestProcessTask', function (argument_list) {
      var gadget = this,
        document_id = argument_list[0],
        body = argument_list[1];

      return readLLMSettings(gadget)
        .push(function (settings) {
          var payload;

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

          return gadget.jio_putAttachment(document_id,
            gadget.hateoas_url + document_id + "/ArtificialTask_proxyLLMRequest",
            JSON.stringify({
              target_url: settings.baseUrl.replace(/\/+$/, '') + "/chat/completions",
              authorization: "Bearer " + settings.apiKey,
              payload: payload
            }));
        })
        .push(function (evt) {
          return jIO.util.readBlobAsText(evt.target.response);
        })
        .push(function (text_evt) {
          var response = JSON.parse(text_evt.target.result);
          if (response.error) {
            throw new Error(typeof response.error === "string" ? response.error :
              (response.error.message || JSON.stringify(response.error)));
          }
          return response.choices[0].message;
        });
    })
    .allowPublicAcquisition('storeTaskResult', function (argument_list) {
      var document_id = argument_list[0],
        body = argument_list[1],
        message_list = body.message_list ? JSON.parse(body.message_list) : [],
        tool_message_list = message_list.filter(function (message) {
          return message.role === 'tool' || message.role === 'assistant';
        });
      appendHistory(document_id, {
        date: new Date().toISOString(),
        text: body.content || "",
        tool_message_list: JSON.stringify(tool_message_list),
        response: true
      });
      return fakeXhrEvent();
    })

    .declareMethod('render', function (options) {
      var gadget = this;
      gadget.options = options;
      return gadget.getSetting('hateoas_url')
        .push(function (hateoas_url) {
          gadget.hateoas_url = hateoas_url;
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
            'chat_state': gadget.state.doc.simulation_state,
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
          return gadget.updateHeader({
            page_title: gadget.state.doc.title
          });
        });
    });
}(window, rJS, RSVP, jIO));
