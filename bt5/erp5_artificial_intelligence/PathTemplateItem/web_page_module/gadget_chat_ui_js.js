/*global window, rJS, RSVP, domsugar, marked, URI, jIO */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, marked) {
  "use strict";


  marked.setOptions({breaks: true});
  // Message and tool result text is untrusted (eg. an http_request result is a
  // whole fetched web page): show raw HTML as text instead of injecting it into
  // the page, where a <base href> would re-point every relative URL (worker,
  // gadgets) and <script>/<img onerror> would run in this origin.
  // Only links and images to these URL schemes are rendered: a link like
  // [x](javascript:...) in an untrusted text would run in this origin when
  // clicked. Other URLs, relative ones included, are shown as text.
  function isSafeUrl(url) {
    // Browsers ignore control characters and spaces in a URL scheme.
    var scheme = /^([a-z][a-z0-9+.\-]*):/.exec((url || "").replace(/[\u0000-\u0020]/g, "").toLowerCase());
    return Boolean(scheme) && ["http", "https", "mailto"].indexOf(scheme[1]) !== -1;
  }

  marked.use({
    renderer: {
      html: function (token) {
        return token.text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
      },
      // Returning false keeps marked's own rendering.
      link: function (token) {
        return isSafeUrl(token.href) ? false : this.parser.parseInline(token.tokens);
      },
      image: function (token) {
        return isSafeUrl(token.href) ? false :
            (token.text || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
      }
    }
  });

  var COMMENT_POLL_INTERVAL = 3000,
    ATTACHMENT_TEXT_MAX_LENGTH = 5 * 1024 * 1024,
    ATTACHMENT_IMAGE_MAX_BYTES = 5 * 1024 * 1024;

  // An attachment link is a "data:<mime>[;base64],<payload>" URI.
  function parseDataUri(data_uri) {
    var match = /^data:([^;,]*)(?:;[^,]*)?,([\s\S]*)$/.exec(data_uri || "");
    return match ? { mime: match[1], base64: match[2] } : null;
  }

  function isImageMimeType(mime) {
    return (/^image\//).test(mime || "");
  }

  function isTextMimeType(mime) {
    return (/^text\//).test(mime || "") ||
      (/^application\/(json|xml|javascript|x-sh)$/).test(mime || "");
  }

  function base64ByteLength(base64) {
    var padding = (/={1,2}$/.exec(base64 || "") || [""])[0].length;
    return Math.floor((base64 || "").length * 3 / 4) - padding;
  }

  function decodeBase64ToText(base64) {
    var binary = window.atob(base64), bytes = new Uint8Array(binary.length), i;
    for (i = 0; i < binary.length; i += 1) {
      bytes[i] = binary.charCodeAt(i);
    }
    return new window.TextDecoder("utf-8", { fatal: false }).decode(bytes);
  }

  function getAttachmentContentPart(attachment_name, data_uri) {
    var parsed = parseDataUri(data_uri), text, truncated;
    if (!parsed) {
      return null;
    }
    if (isImageMimeType(parsed.mime)) {
      if (base64ByteLength(parsed.base64) > ATTACHMENT_IMAGE_MAX_BYTES) {
        return { type: "text", skipped: true, text: "[Attachment: " + attachment_name +
          " - image too large to send (" +
          Math.round(base64ByteLength(parsed.base64) / 1024) + "KB), skipped]" };
      }
      return { type: "image_url", image_url: { url: data_uri } };
    }
    if (isTextMimeType(parsed.mime)) {
      text = decodeBase64ToText(parsed.base64);
      truncated = text.length > ATTACHMENT_TEXT_MAX_LENGTH;
      return { type: "text", text: "[Attachment: " + attachment_name + "]\n" +
        text.slice(0, ATTACHMENT_TEXT_MAX_LENGTH) + (truncated ? "\n[... truncated ...]" : "") };
    }
    if (parsed.mime === "application/pdf") {
      return { type: "text", skipped: true, text: "[Attachment: " + attachment_name +
        " - a PDF, not sent inline. Call the pdf_to_text tool with file_name=\"" + attachment_name +
        "\" to read its text content]" };
    }
    return { type: "text", skipped: true, text: "[Attachment: " + attachment_name + " (" +
      (parsed.mime || "unknown type") + ") - not shown, unsupported type]" };
  }

  // The LLM message of a post (as getCommentPostList returns it), or null for
  // an answer cancelled before the model wrote anything.
  function postToMessage(post) {
    var content = post.text || "",
      attachment_part = post.attachment_link ?
          getAttachmentContentPart(post.attachment_name, post.attachment_link) : null;
    if (post.response) {
      return content.trim() ? { role: "assistant", content: content } : null;
    }
    return {
      role: "user",
      content: attachment_part ?
          (attachment_part.type === "image_url" ?
              [{ type: "text", text: content }, attachment_part] :
              content + "\n\n" + attachment_part.text) :
          content
    };
  }


  function traceToMessageList(trace) {
    var message_list = [];
    trace.forEach(function (entry, index) {
      var next_index = index + 1;
      if (entry.role !== "assistant" || !entry.tool_calls || !entry.tool_calls.length) {
        return;
      }
      while (next_index < trace.length && trace[next_index].role !== "assistant") {
        next_index += 1;
      }
      message_list.push({
        role: "assistant",
        content: "",
        tool_calls: entry.tool_calls
      });
      entry.tool_calls.forEach(function (tool_call) {
        var result = trace.slice(index + 1, next_index).filter(function (message) {
          return message.role === "tool" && message.tool_call_id === tool_call.id;
        })[0];
        message_list.push({
          role: "tool",
          tool_call_id: tool_call.id,
          name: tool_call["function"].name,
          // Without a stored result (the task was cancelled or failed while
          // it ran, or it was not run at the turn limit), servers reject the
          // tool call: say it was not run.
          content: result ? result.content :
              "Not run: the task stopped before this tool call returned a result."
        });
      });
    });
    return message_list;
  }


  function postListToHistory(post_list, summarized_before_int_index) {
    var history = { message_list: [], cut_list: [] },
      kept_list = post_list.filter(function (post) {
        return (post.int_index || 0) >= summarized_before_int_index;
      });
    kept_list.forEach(function (post, index) {
      var message = postToMessage(post);
      if (post.response) {
        history.message_list = history.message_list.concat(
          traceToMessageList(JSON.parse(post.tool_message_list || "[]"))
        );
      } else if (index === 0 || kept_list[index - 1].response) {
        history.cut_list.push({ index: history.message_list.length, int_index: post.int_index || 0 });
      }
      if (message) {
        history.message_list.push(message);
      }
    });
    return history;
  }

  function formatPost(post) {
    var date = new Date(post.date);
    post.date_formatted = date.toLocaleString();
    post.date_relative = date.toLocaleString();
    return post;
  }

  // The reasoning of an answer, in a "Thinking" block above its text.
  function getReasoningDom(reasoning, is_open) {
    return domsugar("details", is_open ? { open: "open", "class": "post-answer-reasoning" } :
        { "class": "post-answer-reasoning" }, [
      domsugar("summary", ["Thinking"]),
      domsugar("div", { "class": "post-answer-reasoning-content" }, [reasoning])
    ]);
  }

  function getPostDom(post) {
    var content_element = post.response ?
        domsugar("div", [
        domsugar("div", { "class": "post-markdown", html: marked.parse(post.text) })
      ]) :
        domsugar("div", [domsugar("pre", [post.text])]),
        dom_list = [
        content_element
      ],
      attachment_children;
    if (post.attachment_link) {
      attachment_children = [
        domsugar("a", { href: post.attachment_link, download: post.attachment_name }, [post.attachment_name])
      ];
      dom_list.push(domsugar("div", { "class": "post-attachment" }, attachment_children));
    }
    dom_list.push(domsugar("time", { datetime: post.date, title: post.date }, [
      (post.response && post.author_title) ? (post.author_title + " · " + post.date_formatted) : post.date_formatted
    ]));
    // post-has-text: an answer with a text, counted by onLoop as shown.
    return domsugar("li", {
      "class": post.response ?
          ((post.text || "").trim() ? "post-answer post-has-text" : "post-answer") :
          "post-question"
    }, dom_list);
  }

  function getTypingIndicatorDom() {
    return domsugar("span", { "class": "chat-typing-indicator" }, [
      domsugar("span"),
      domsugar("span"),
      domsugar("span")
    ]);
  }

  function formatSeconds(duration_ms) {
    return (duration_ms / 1000).toFixed(1) + "s";
  }

  // How long the LLM request of an answer took, and its tokens, eg.
  // "LLM request: 7.3s (first token after 5.1s), 3012 prompt (2800 from the
  // cache) + 45 completion tokens, 18 tokens/s".
  function getTimingText(timing, usage) {
    var text = "LLM request: " + formatSeconds(timing.duration_ms),
      generation_ms;
    if (timing.first_token_ms !== null && timing.first_token_ms !== undefined) {
      text += " (first token after " + formatSeconds(timing.first_token_ms) + ")";
    }
    if (usage && usage.total_tokens) {
      text += ", " + usage.prompt_tokens + " prompt" +
        (usage.cached_tokens ? " (" + usage.cached_tokens + " from the cache)" : "") +
        " + " + usage.completion_tokens + " completion tokens";
      generation_ms = timing.duration_ms - (timing.first_token_ms || 0);
      if (usage.completion_tokens && generation_ms > 0) {
        text += ", " + Math.round(usage.completion_tokens * 1000 / generation_ms) + " tokens/s";
      }
    }
    return text;
  }

  function getAssistantMessageDiv(assistant_message) {
    var dom_list = [
      domsugar("strong", ["Assistant"]),
      domsugar("br")
    ];
    if (assistant_message.timing) {
      dom_list.push(domsugar("div", { "class": "post-tool-timing" },
        [getTimingText(assistant_message.timing, assistant_message.usage)]));
    }
    if (assistant_message.reasoning) {
      dom_list.push(domsugar("details", { "class": "post-assistant-reasoning" }, [
        domsugar("summary", ["Thinking"]),
        domsugar("pre", { "class": "post-tool-content" }, [assistant_message.reasoning])
      ]));
    }
    dom_list.push(domsugar("div", { "class": "post-tool-content" }, [assistant_message.content || ""]));
    (assistant_message.tool_calls || []).forEach(function (tool_call) {
      var tool_function = tool_call["function"] || {};
      dom_list.push(domsugar("div", {
        "class": "post-tool-call post-tool-call-running",
        "data-tool-call-id": tool_call.id || ""
      }, [
        domsugar("strong", ["Tool call: " + tool_function.name + (tool_call.id ? " (" + tool_call.id + ")" : "")]),
        domsugar("pre", { "class": "post-tool-content" }, [tool_function.arguments || ""])
      ]));
    });
    return domsugar("div", { "class": "post-tool-entry post-assistant-entry" }, dom_list);
  }

  function getSubMessageDiv(sub_message) {
    var label = sub_message.role === "tool" ?
        ("Tool: " + sub_message.name) :
        (sub_message.role === "assistant" ? "Assistant" : "Task");
    return domsugar("div", { "class": "post-tool-entry post-tool-sub-entry" }, [
      domsugar("strong", [label]),
      domsugar("br"),
      domsugar("div", { "class": "post-markdown post-tool-content", html: marked.parse(sub_message.content || "") })
    ]);
  }

  // A tool result has the tool_call_id of its call; a tool message without
  // it is a note of the agent (retry, compaction, usage...).
  function getToolCallDiv(tool_message) {
    var dom_list = [
      domsugar("strong", ["Tool: " + tool_message.name +
        (tool_message.tool_call_id ? " (result " + tool_message.tool_call_id + ")" : "") +
        (tool_message.duration_ms !== undefined ? " - " + formatSeconds(tool_message.duration_ms) : "")]),
      domsugar("br"),
      domsugar("div", { "class": "post-markdown post-tool-content", html: marked.parse(tool_message.content || "") })
    ];
    if (tool_message.sub_message_list && tool_message.sub_message_list.length) {
      dom_list.push(domsugar("details", { "class": "post-tool-sub-list" }, [
        domsugar("summary", ["Sub-agent trace (" + tool_message.sub_message_list.length + ")"])
      ].concat(tool_message.sub_message_list.map(getSubMessageDiv))));
    }
    return domsugar("div", { "class": "post-tool-entry" }, dom_list);
  }

  function getAgentMessageDiv(agent_message) {
    return agent_message.role === "assistant" ?
      getAssistantMessageDiv(agent_message) :
      getToolCallDiv(agent_message);
  }

  function getToolCallSummaryText(count) {
    return "Tool calls (" + count + ")";
  }

  var EXECUTION_PLAN_STATUS_ICON = {
    pending: "☐",
    in_progress: "⟳",
    done: "☑",
    failed: "✗",
    skipped: "⊘"
  };

  function getExecutionPlanStepListDom(step_list) {
    return domsugar("ol", { "class": "execution-plan-step-list" }, step_list.map(function (step) {
      var li_children = [
        domsugar("span", { "class": "execution-plan-step-status" }, [EXECUTION_PLAN_STATUS_ICON[step.status] || EXECUTION_PLAN_STATUS_ICON.pending]),
        domsugar("span", { "class": "execution-plan-step-title" }, [step.title])
      ];
      if (step.note) {
        li_children.push(domsugar("div", { "class": "execution-plan-step-note" }, [step.note]));
      }
      return domsugar("li", { "class": "execution-plan-step execution-plan-step-" + step.status }, li_children);
    }));
  }

  function getExecutionPlanDom(plan) {
    if (!plan || !plan.step_list || !plan.step_list.length) {
      return null;
    }
    return domsugar("div", { "class": "execution-plan" }, [
      domsugar("strong", { "class": "execution-plan-goal" }, ["Plan: " + (plan.goal || "")]),
      getExecutionPlanStepListDom(plan.step_list)
    ]);
  }

  // The error that stopped a task, from the "error" entry of its trace:
  // shown under the answer, as it is not part of the answer text.
  function getErrorDom(tool_message_list) {
    var i;
    for (i = tool_message_list.length - 1; i >= 0; i -= 1) {
      if (tool_message_list[i].name === "error") {
        return domsugar("div", { "class": "post-error" }, [tool_message_list[i].content || ""]);
      }
    }
    return null;
  }

  function appendPlanAndToolDom(post_dom, post) {
    var tool_message_list = JSON.parse(post.tool_message_list || "[]"),
      plan_dom = getExecutionPlanDom(post.execution_plan ? JSON.parse(post.execution_plan) : null),
      error_dom = getErrorDom(tool_message_list),
      tool_call_dom = getToolCallDom(tool_message_list, false);
    if (plan_dom) {
      post_dom.appendChild(plan_dom);
    }
    if (error_dom) {
      post_dom.appendChild(error_dom);
    }
    if (tool_call_dom) {
      post_dom.appendChild(tool_call_dom);
    }
    return post_dom;
  }

  // Live refresh of the in-progress message bubble's plan while a turn is
  // still running (before it has its own stored snapshot) - mirrors how the
  // tool-call list is appended to incrementally in showMessage below.
  function refreshMessageExecutionPlan(message_element, plan) {
    var old_plan_element = message_element.querySelector('.execution-plan'),
      new_plan_dom = getExecutionPlanDom(plan),
      reference_node;
    if (old_plan_element) {
      old_plan_element.parentNode.removeChild(old_plan_element);
    }
    if (new_plan_dom) {
      reference_node = message_element.querySelector('.post-tool') || message_element.querySelector('time');
      message_element.insertBefore(new_plan_dom, reference_node || null);
    }
  }

  // A tool call shows it is running until its result is in the trace, or
  // until the request is finished (is_finished).
  function refreshToolCallState(element, tool_message_list, is_finished) {
    var done_dict = {};
    tool_message_list.forEach(function (tool_message) {
      if (tool_message.tool_call_id) {
        done_dict[tool_message.tool_call_id] = true;
      }
    });
    Array.prototype.forEach.call(element.querySelectorAll('.post-tool-call-running'), function (call_element) {
      if (is_finished || done_dict.hasOwnProperty(call_element.getAttribute('data-tool-call-id'))) {
        call_element.classList.remove('post-tool-call-running');
      }
    });
  }

  // details_open: the trace of the answer being written, open until the
  // request is finished.
  function getToolCallDom(tool_message_list, details_open) {
    var details_attr, tool_call_dom;
    if (!tool_message_list || !tool_message_list.length) {
      return;
    }
    details_attr = details_open ? { open: "open", "class": "post-tool-pending" } : {};
    tool_call_dom = domsugar("li", { "class": "post-tool" }, [
      domsugar("details", details_attr, [
        domsugar("summary", [getToolCallSummaryText(tool_message_list.length)])
      ].concat(tool_message_list.map(getAgentMessageDiv)))
    ]);
    refreshToolCallState(tool_call_dom, tool_message_list, !details_open);
    return tool_call_dom;
  }


  function renderMessage(message_element, message, rendered_tool_message_count) {
    var tool_message_list = message.tool_message_list || [],
      details_element,
      error_dom,
      reasoning_element,
      markdown_element,
      i;
    markdown_element = message_element.querySelector(".post-markdown");
    if (message.hasOwnProperty('content') && message.content) {
      markdown_element.innerHTML = marked.parse(message.content || "");
      if (message.content.trim()) {
        message_element.classList.add("post-has-text");
      }
      if (message.streaming) {
        markdown_element.appendChild(getTypingIndicatorDom());
      }
    } else {
      // Still working: keep the text already shown, the model goes on
      // writing below it.
      if (!markdown_element.querySelector('.chat-typing-indicator')) {
        markdown_element.appendChild(getTypingIndicatorDom());
      }
    }
    if (tool_message_list.length) {
      details_element = message_element.querySelector('.post-tool > details');
      if (!details_element) {
        message_element.appendChild(getToolCallDom(tool_message_list, true));
      } else {
        for (i = rendered_tool_message_count; i < tool_message_list.length; i += 1) {
          details_element.appendChild(getAgentMessageDiv(tool_message_list[i]));
        }
        if (tool_message_list.length !== rendered_tool_message_count) {
          details_element.querySelector('summary').textContent =
            getToolCallSummaryText(tool_message_list.length);
        }
        details_element.open = true;
        details_element.classList.add('post-tool-pending');
        refreshToolCallState(details_element, tool_message_list, false);
      }
    }
    // message.reasoning: "" removes the block, it stays open while the
    // answer is streamed.
    if (message.hasOwnProperty('reasoning')) {
      reasoning_element = message_element.querySelector('.post-answer-reasoning');
      if (!message.reasoning) {
        if (reasoning_element) {
          reasoning_element.parentNode.removeChild(reasoning_element);
        }
      } else if (reasoning_element) {
        reasoning_element.querySelector('.post-answer-reasoning-content').textContent = message.reasoning;
        reasoning_element.open = Boolean(message.streaming);
      } else {
        message_element.appendChild(getReasoningDom(message.reasoning, message.streaming));
      }
    }
    if (!message_element.querySelector('.post-error')) {
      error_dom = getErrorDom(tool_message_list);
      if (error_dom) {
        message_element.appendChild(error_dom);
      }
    }
    if (message.hasOwnProperty('execution_plan')) {
      refreshMessageExecutionPlan(message_element, message.execution_plan);
    }
    return Math.max(rendered_tool_message_count, tool_message_list.length);
  }

  rJS(window)
    .declareAcquiredMethod("translate", "translate")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("notifyCommentPosted", "notifyCommentPosted")
    .declareAcquiredMethod("notifyCancelRequested", "notifyCancelRequested")
    .declareAcquiredMethod("getCommentPostList", "getCommentPostList")
    .declareAcquiredMethod("postComment", "postComment")

    .declareMethod('render', function (options) {
      var gadget = this;
      gadget.options = options;
      return gadget.declareGadget(options.editor_options.editor, {
        element: gadget.element.querySelector('.chat-editor'),
        scope: "editor",
        sandbox: "public"
      })
      .push(function () {
        return gadget.translate("Post Comment");
      })
      .push(function (translation) {
        gadget.element.querySelector("[data-i18n='[value]Post Comment']").value = translation;
        return gadget.changeState({
          'editor_state': 'initialise',
          'allow_submit': true,
          'render_comment': true
        });
      });
    })
    .allowPublicAcquisition('notifySubmit', function notifySubmit(e) {
      return this.submitPostComment(e);
    })
    .onStateChange(function (modification_dict) {
      var gadget = this,
        queue = new RSVP.Queue();
      if (modification_dict.hasOwnProperty("allow_submit") ||
          modification_dict.hasOwnProperty("editor_state")) {
        var submitButton = gadget.element.querySelector("input[type=submit]"),
          cancelButton = gadget.element.querySelector("#cancel_button");
        if (gadget.state.allow_submit) {
          submitButton.disabled = false;
          submitButton.classList.remove("ui-disabled");
        } else {
          submitButton.disabled = true;
          submitButton.classList.add("ui-disabled");
        }
        // The editor stays 'pending' while the agent runs, even when posts
        // can be queued meanwhile (enable_queue).
        cancelButton.style.display = (gadget.options.enable_cancel &&
          (!gadget.state.allow_submit || gadget.state.editor_state === 'pending')) ? "inline-block" : "none";
      }
      if (modification_dict.hasOwnProperty("editor_state")) {
        if (modification_dict.editor_state == 'initialise') {
          queue
            .push(function () {
              return gadget.getDeclaredGadget("editor");
            })
            .push(function (editor) {
              return editor.render(gadget.options.editor_options.options);
            });
        }
      }
      if (modification_dict.hasOwnProperty("render_comment") && modification_dict.render_comment) {
        queue
          .push(function () {
            return gadget.getCommentPostList(gadget.options.jio_key);
          })
          .push(
            function (post_list) {
              return post_list.map(formatPost).map(function (post) {
                return appendPlanAndToolDom(getPostDom(post), post);
              });
            })
          .push(function (dom_list) {
            var all_dom_list = [], post_list_element, i;
            for (i = 0; i < dom_list.length; i += 1) {
              all_dom_list = all_dom_list.concat(dom_list[i]);
            }
            post_list_element = gadget.element.querySelector("#post_list");
            domsugar(post_list_element, all_dom_list);
          });
      }
      return queue;
    })
    .onLoop(function () {
      var gadget = this;
      if (gadget.options.disable_comment_poll) {
        return;
      }
      return gadget.getCommentPostList(gadget.options.jio_key)
        .push(function (post_list) {
          // The stored posts after the ones already shown: questions, and
          // answers with a text (not the one being written).
          var rendered_count = gadget.element.querySelectorAll(
              "#post_list li.post-question:not(.post-queued), #post_list li.post-answer.post-has-text"
            ).length;
          return post_list.slice(rendered_count).reduce(function (sub_queue, post) {
            return sub_queue.push(function () {
              return gadget.appendPost(post);
            });
          }, new RSVP.Queue());
        });
    }, COMMENT_POLL_INTERVAL)

    // we send post message and also tool call trace
    .declareMethod('getMessageList', function (summarized_before_int_index) {
      return this.getCommentPostList(this.options.jio_key)
        .push(function (post_list) {
          return postListToHistory(post_list, summarized_before_int_index || 0);
        });
    })
    .declareMethod('appendPost', function (post) {
      var gadget = this,
        post_list_element = gadget.element.querySelector("#post_list"),
        dom = appendPlanAndToolDom(getPostDom(formatPost(post)), post);
      post_list_element.appendChild(dom);
    })
    // Starts the answer, at the end of the page, and the processing.
    .declareMethod('startProcessing', function () {
      var gadget = this;
      return gadget.showMessage({})
        .push(function () {
          return gadget.changeState({
            // With enable_queue, the user can keep posting while the agent
            // runs: the posts are queued (see submitPostComment).
            allow_submit: Boolean(gadget.options.enable_queue),
            editor_state: 'pending'
          });
        });
    })
    // Ends the answer being written: the next showMessage starts a new one.
    .declareMethod('finishAnswer', function () {
      var gadget = this,
        message_element = gadget.new_message_element,
        typing_indicator,
        details_element;
      if (gadget.streaming_frame) {
        window.cancelAnimationFrame(gadget.streaming_frame);
        gadget.streaming_frame = null;
      }
      if (message_element) {
        // An answer with tool calls only still looks in progress: it is not
        // anymore.
        typing_indicator = message_element.querySelector('.post-markdown .chat-typing-indicator');
        if (typing_indicator) {
          typing_indicator.parentNode.removeChild(typing_indicator);
        }
        details_element = message_element.querySelector('.post-tool > details');
        if (details_element) {
          details_element.open = false;
          details_element.classList.remove('post-tool-pending');
          refreshToolCallState(details_element, [], true);
        }
      }
      gadget.new_message_element = null;
      gadget.rendered_tool_message_count = 0;
    })
    // Ends the processing: the posts queued meanwhile are stored, below the
    // answer, and their LLM messages returned.
    .declareMethod('stopProcessing', function () {
      var gadget = this;
      return gadget.finishAnswer()
        .push(function () {
          return gadget.flushQueuedPostList();
        })
        .push(function (queued_message_list) {
          return gadget.changeState({
            allow_submit: true,
            // With enable_queue, the user may be writing the next post when
            // the agent ends: 'ready' keeps that draft, 'initialise' would
            // render the editor again, empty.
            editor_state: gadget.options.enable_queue ? 'ready' : 'initialise'
          })
            .push(function () {
              return queued_message_list;
            });
        });
    })
    // Ends the processing cancelled by the user: the posts queued meanwhile
    // are dropped, without storing them.
    .declareMethod('cancelProcessing', function () {
      var gadget = this;
      (gadget.queued_post_list || []).forEach(function (queued_post) {
        // A post already stored by a flush is not queued anymore: it stays.
        if (queued_post.element.classList.contains("post-queued") &&
            queued_post.element.parentNode) {
          queued_post.element.parentNode.removeChild(queued_post.element);
        }
      });
      gadget.queued_post_list = [];
      return gadget.finishAnswer()
        .push(function () {
          return gadget.changeState({
            allow_submit: true,
            // Like in stopProcessing: 'ready' keeps the draft.
            editor_state: gadget.options.enable_queue ? 'ready' : 'initialise'
          });
        });
    })
    // Stores the queued posts, in the order they were posted, and returns
    // their LLM messages.
    .declareMethod('flushQueuedPostList', function () {
      var gadget = this,
        message_list = [];
      function flushNext() {
        var queued_post = (gadget.queued_post_list || [])[0];
        if (!queued_post) {
          return message_list;
        }
        return gadget.postComment(gadget.options.jio_key, queued_post.form_data_json)
          .push(function () {
            gadget.queued_post_list.shift();
            queued_post.element.classList.remove("post-queued");
            // Stored before the answer being written, which is stored once
            // the agent ends: show it above, in the order of the stored
            // lines. From stopProcessing, the posts stay below the answer.
            if (gadget.new_message_element && gadget.new_message_element.parentNode &&
                (gadget.new_message_element.compareDocumentPosition(queued_post.element) &
                  window.Node.DOCUMENT_POSITION_FOLLOWING)) {
              gadget.new_message_element.parentNode.insertBefore(queued_post.element, gadget.new_message_element);
            }
            message_list.push(postToMessage(queued_post.post));
            return flushNext();
          });
      }
      return flushNext();
    })
    .declareMethod('showMessage', function (message) {
      var gadget = this,
        time_element;
      if (!gadget.new_message_element) {
        gadget.new_message_element = getPostDom(formatPost({
          date: new Date().toISOString(),
          text: "",
          response: true,
          author_title: message.author_title || "Assistant"
        }));
        gadget.rendered_tool_message_count = 0;
        gadget.element.querySelector("#post_list").appendChild(gadget.new_message_element);
      } else if (message.author_title) {
        time_element = gadget.new_message_element.querySelector("time");
        time_element.textContent = message.author_title + " · " +
          new Date(time_element.getAttribute("datetime")).toLocaleString();
      }
      if (message.streaming) {
        gadget.streaming_message = message;
        if (!gadget.streaming_frame) {
          gadget.streaming_frame = window.requestAnimationFrame(function () {
            gadget.streaming_frame = null;
            gadget.rendered_tool_message_count = renderMessage(gadget.new_message_element,
              gadget.streaming_message, gadget.rendered_tool_message_count);
          });
        }
        return;
      }
      if (gadget.streaming_frame) {
        window.cancelAnimationFrame(gadget.streaming_frame);
        gadget.streaming_frame = null;
        // The last streamed text is not shown yet: show it before this
        // message, which may have no content and keep the text shown.
        gadget.rendered_tool_message_count = renderMessage(gadget.new_message_element,
          gadget.streaming_message, gadget.rendered_tool_message_count);
      }
      gadget.rendered_tool_message_count = renderMessage(gadget.new_message_element,
        message, gadget.rendered_tool_message_count);
    })
    .declareJob('submitPostComment', function () {
      var gadget = this,
        queue = null;

      return gadget.getDeclaredGadget("editor")
        .push(function (e) {
          return e.getContent();
        })
        .push(function (content) {
          // Posted while the agent runs: the editor stays 'pending' until the
          // agent ends (stopProcessing).
          var is_queued = gadget.state.editor_state === 'pending';
          if (content.comment === '') {
            return gadget.translate("Post content can not be empty!")
              .push(function (translated_message) {
                return gadget.notifySubmitted({message: translated_message});
              });
          }
          queue = gadget.changeState(is_queued ? {allow_submit: false} : {
            allow_submit: false,
            editor_state: 'posting'
          })
            .push(function () {
              var choose_file_html_element = gadget.element.querySelector('#attachment'),
                file_blob = choose_file_html_element.files[0],
                comment_text = content.comment,
                form_data_json = {},
                post;
              form_data_json.data = comment_text || "";
              form_data_json.file = "";
              choose_file_html_element.value = "";

              post = {
                date: new Date().toISOString(),
                text: comment_text,
                response: false,
                author_title: ""
              };

              return new RSVP.Queue()
                .push(function () {
                  if (file_blob) {
                    return jIO.util.readBlobAsDataURL(file_blob);
                  }
                })
                .push(function (data_url_evt) {
                  var queued_element;
                  if (data_url_evt) {
                    form_data_json.file = {
                      url: data_url_evt.target.result,
                      file_name: file_blob.name
                    };
                    post.attachment_link = data_url_evt.target.result;
                    post.attachment_name = file_blob.name;
                  }
                  if (is_queued) {
                    // The agent is running: the post waits below the answer
                    // being written until the agent takes it, before its
                    // next LLM request or once it has answered.
                    return new RSVP.Queue(gadget.new_message_element ? null : gadget.showMessage({}))
                      .push(function () {
                        queued_element = getPostDom(formatPost(post));
                        queued_element.classList.add("post-queued");
                        gadget.element.querySelector("#post_list").appendChild(queued_element);
                        gadget.queued_post_list = (gadget.queued_post_list || []).concat([{
                          element: queued_element,
                          form_data_json: form_data_json,
                          post: post
                        }]);
                      });
                  }
                  return gadget.appendPost(post);
                })
                .push(function () {
                  if (is_queued) {
                    return;
                  }
                  return gadget.postComment(
                    gadget.options.jio_key,
                    form_data_json
                  );
                })
                .push(function (evt) {
                  var location,
                    uri,
                    redirect_jio_key;
                  if (is_queued) {
                    // Clear the editor without leaving the 'pending' state.
                    return gadget.getDeclaredGadget("editor")
                      .push(function (editor) {
                        return editor.render(gadget.options.editor_options.options);
                      })
                      .push(function () {
                        return gadget.changeState({allow_submit: true});
                      });
                  }
                  location = evt.target.getResponseHeader("X-Location");
                  gadget.new_message_element = null;
                  if (location) {
                    uri = new URI(location);
                    redirect_jio_key = uri.segment(2);
                  }
                  if (redirect_jio_key && (gadget.options.jio_key != redirect_jio_key)) {
                    return gadget.redirect({
                      command: 'display',
                      options: {
                        "jio_key": redirect_jio_key
                      }
                    });
                  }
                  return gadget.changeState({
                    editor_state: 'initialise',
                    allow_submit: true
                  })
                    .push(function () {
                      return gadget.notifyCommentPosted();
                    });
                });
            }, function (e) {
                return RSVP.all([
                  gadget.changeState(is_queued ? {allow_submit: true} : {
                    allow_submit: true,
                    editor_state: 'initialise'
                  }),
                  gadget.notifySubmitted({message: "Error:" + e, status: "error"})
                ]);
              });
          return queue;
        });
    })
    .onEvent('submit', function () {
      return this.submitPostComment();
    })
    .onEvent('click', function (evt) {
      if (!evt.target || evt.target.id !== 'cancel_button') {
        return;
      }
      return this.notifyCancelRequested();
    }, false, false);
}(window, rJS, RSVP, marked));
