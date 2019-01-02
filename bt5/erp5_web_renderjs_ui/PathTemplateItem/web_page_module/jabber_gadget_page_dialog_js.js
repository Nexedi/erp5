/*global window, document, rJS, RSVP*/
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, document, rJS, RSVP) {
  "use strict";

  // 30 minutes
  var MESSAGE_FRESHNESS = 1800000;

  function calculateMessageList(text) {
    var message_list = [],
      line_list = text.split('\n'),
      line_count = line_list.length,
      line,
      tmp_line,
      i,
      index,
      displayed_text = '',
      is_incoming = true,
      is_handled,
      is_old,
      message_date,
      previous_message_date,
      message_is_incoming;

    function appendMessage(displayed_text, incoming, date) {
      if (displayed_text) {
        message_list.push({
          text: displayed_text,
          incoming: incoming,
          message_date: date
        });
      }
    }

    for (i = 0; i < line_count - 1; i += 1) {
      line = line_list[i];

      is_handled = false;
      is_old = false;
      if (line.indexOf('[') === 0) {
        index = line.indexOf('] ');
        if (index !== -1) {
          // Check message freshness
          // If we receive one multiline message, then the lines after the first
          // would not start with the date. So this would return Invalid Date
          message_date = new Date(line.substring(1, index));
          // Check direction and cut the date from the start of the line. 
          // This should be done only if it is a unique line or the first
          // line of a multi-line message. Other lines will retain direction
          // of the first
          if (isNaN(message_date) === false) {
            if (previous_message_date === undefined) {
              previous_message_date = new Date(message_date - MESSAGE_FRESHNESS - 2);
            }
            if (message_date - previous_message_date > MESSAGE_FRESHNESS) {
              is_old = true;
            }
            tmp_line = line.substring(index + 2);
            if (tmp_line.indexOf('> ') === 0) {
              message_is_incoming = false;
            } else if (tmp_line.indexOf('< ') === 0) {
              message_is_incoming = true;
            }
            line = tmp_line.substring(2);
          }
          if (message_is_incoming !== is_incoming || is_old) {
            appendMessage(displayed_text, is_incoming, previous_message_date);
            is_incoming = message_is_incoming;
            is_handled = true;
            displayed_text = line + '\n';
          }
        }
      }
      previous_message_date = message_date;

      if (!is_handled) {
        displayed_text += line + '\n';
      }
    }
    appendMessage(displayed_text, is_incoming, message_date);
    return message_list;
  }

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    .declareAcquiredMethod("refresh", "refresh")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")

    .declareJob('scroll', function () {
      window.scrollTo(0, this.element.scrollHeight ||
                         document.body.scrollHeight ||
                         document.documentElement.scrollHeight);
    })

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('render', function (options) {
      var gadget = this;
      return gadget.jio_getAttachment(options.jio_key, "enclosure", {format: 'text'})
        .push(function (text) {
          return gadget.changeState({
            jio_key: options.jio_key,
            text: text,
            refresh: options.refresh || 1
          });
        });
    })

    .onStateChange(function (modification_dict) {
      var gadget = this,
        queue = new RSVP.Queue();

      if (modification_dict.hasOwnProperty('jio_key')) {
        queue
          .push(function () {
            return RSVP.all([
              gadget.getUrlFor({command: 'display_stored_state',
                                options: {page: 'jabberclient_contact'}}),
              gadget.getUrlFor({command: 'change',
                                options: {page: 'jabberclient_attachment'}}),
              gadget.getUrlFor({command: 'selection_previous'}),
              gadget.getUrlFor({command: 'selection_next'})
            ]);
          })
          .push(function (all_result) {
            return gadget.updateHeader({
              selection_url: all_result[0],
              previous_url: all_result[2],
              next_url: all_result[3],
              page_title: gadget.state.jio_key,
              actions_url: all_result[1]
            });
          });
      }
      if (modification_dict.hasOwnProperty('refresh')) {
        queue
          .push(function () {
            return gadget.getDeclaredGadget('input_form');
          })
          .push(function (form_gadget) {
            var field_dict = {};
            field_dict.your_message = {
              "description": "",
              "title": "Message",
              "default": "",
              "css_class": "",
              "required": 1,
              "editable": 1,
              "key": "your_message",
              "hidden": 0,
              "type": "StringField"
            };

            return form_gadget.render({
              erp5_document: {"_embedded": {"_view": field_dict}},
              form_definition: {
                group_list: [
                  ["bottom", [["your_message"]]]
                ]
              }
            });
          });
      }

      if (modification_dict.hasOwnProperty('text')) {
        queue
          .push(function () {
            return gadget.getDeclaredGadget('discussion_form');
          })
          .push(function (form_gadget) {
            var text = gadget.state.text,
              message_list = calculateMessageList(text),
              field_list = [],
              field_dict = {},
              i,
              now = (new Date()).toDateString();

            function appendField(message) {
              var field_id,
                field_title,
                current_field;
              field_id = message.message_date.toLocaleString();
              if (message.incoming) {
                field_title = '< ';
              } else {
                field_title = '> ';
              }
              if (now === message.message_date.toDateString()) {
                field_title += message.message_date.toLocaleTimeString();
              } else {
                field_title += message.message_date.toLocaleDateString();
              }
              field_list.push([field_id]);
              current_field = {
                "description": "",
                "title": field_title,
                "default": message.text,
                "css_class": "",
                "required": 0,
                "editable": 0,
                "key": field_id,
                "hidden": 0,
                "type": "TextAreaField"
              };
              field_dict[field_id] = current_field;
            }

            for (i = 0; i < message_list.length; i += 1) {
              appendField(message_list[i]);
            }

            return form_gadget.render({
              erp5_document: {"_embedded": {"_view": field_dict}},
              form_definition: {
                group_list: [
                  ["center", field_list]
                ]
              }
            });
          });
      }

      if (modification_dict.hasOwnProperty('jio_key') ||
          modification_dict.hasOwnProperty('refresh')) {
        // Only scroll when displaying a new user discussion
        // This allow to read discussion history without being annoyed by scroll
        queue
          .push(function () {
            return gadget.scroll();
          });
      }
      return queue;
    })

    .onEvent('submit', function () {
      var page_gadget = this;
      return page_gadget.notifySubmitting()
        .push(function () {
          return page_gadget.getDeclaredGadget('input_form');
        })
        .push(function (input_form_gadget) {
          return input_form_gadget.getContent();
        })
        .push(function (content) {
          return page_gadget.jio_putAttachment(
            page_gadget.state.jio_key,
            'MESSAGE',
            content.your_message
          );
        })
        .push(function () {
          return page_gadget.notifySubmitted();
        })
        .push(function () {
          return page_gadget.render({
            jio_key: page_gadget.state.jio_key,
            refresh: new Date().getTime()
          });
        });
    });

}(window, document, rJS, RSVP));