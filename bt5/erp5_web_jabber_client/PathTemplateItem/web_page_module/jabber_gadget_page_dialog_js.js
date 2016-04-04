/*global window, document, rJS, RSVP, loopEventListener*/
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, document, rJS, RSVP, loopEventListener) {
  "use strict";

  function scroll() {
    RSVP.Queue()
      .push(function () {
        return RSVP.delay(0);
      })
      .push(function () {
        window.scrollTo(0, document.body.scrollHeight || document.documentElement.scrollHeight);
      });
  }

  // MESSAGE_FRESHNESS 30 minutes
  var MESSAGE_FRESHNESS = 1800000;

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // ready
    /////////////////////////////////////////////////////////////////
    // Init local properties
    .ready(function (g) {
      g.props = {};
    })

    // Assign the element to a variable
    .ready(function (g) {
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
        });
    })

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    .declareAcquiredMethod("refresh", "refresh")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function (options) {
      var gadget = this,
        ul = document.createElement("ul");
      ul.setAttribute("data-role", "listview");
      gadget.props.jid = options.jid;
      return gadget.updateHeader({
        page_title: options.jid
      })
        .push(function () {
          return gadget.jio_getAttachment(options.jid, "enclosure", {format: 'text'});
        })
        .push(function (text) {
          var line_list = text.split('\n'),
            line,
            tmp_line,
            i,
            index,
            displayed_text = '',
            is_incoming = true,
            is_handled,
            previous_message_date,
            is_old,
            message_date,
            message_is_incoming;

          function appendText(txt, incoming) {
            var li, pre;
            if (txt) {
              li = document.createElement("li");
              if (incoming) {
                li.setAttribute("style", "padding-right: 5em;");
              } else {
                li.setAttribute("style", "text-align: right; padding-left: 5em;");
              }
              pre = document.createElement("pre");
              pre.setAttribute("style", "white-space: pre-wrap;");
              pre.textContent = txt;
              li.appendChild(pre);
              ul.appendChild(li);
            }
          }

          function appendDate(date) {
            var li,
              i_element;
            li = document.createElement("li");
            li.setAttribute("style", "text-align: center; padding-left: 5em; padding: 0;");
            i_element = document.createElement("i");
            i_element.setAttribute("style", "white-space: pre-wrap; padding: 0.5em 0 0.5em 0; display: block;");
            i_element.textContent = date.toLocaleString();
            li.appendChild(i_element);
            ul.appendChild(li);
          }

          for (i = 0; i < line_list.length - 1; i += 1) {
            line = line_list[i];
            is_handled = false;
            is_old = false;
            if (line.indexOf('[') === 0) {
              index = line.indexOf('] ');
              if (index !== -1) {
                // Check message freshness
                message_date = new Date(line.substring(1, index));
                if (previous_message_date === undefined) {
                  previous_message_date = new Date(message_date - MESSAGE_FRESHNESS - 2);
                }
                if (message_date - previous_message_date > MESSAGE_FRESHNESS) {
                  is_old = true;
                }
                // Check direction
                tmp_line = line.substring(index + 2);
                if (tmp_line.indexOf('> ') === 0) {
                  message_is_incoming = false;
                } else if (tmp_line.indexOf('< ') === 0) {
                  message_is_incoming = true;
                }
                line = tmp_line.substring(2);
                if (message_is_incoming !== is_incoming || is_old) {
                  appendText(displayed_text, is_incoming);
                  is_incoming = message_is_incoming;
                  is_handled = true;
                  displayed_text = line + '\n';
                }
                if (is_old) {
                  appendDate(message_date);
                }
              }
            }
            previous_message_date = message_date;

            if (!is_handled) {
              displayed_text += line + '\n';
            }
          }
          appendText(displayed_text, is_incoming);

          gadget.props.element.querySelector(".discussion-content").innerHTML = "";
          gadget.props.element.querySelector(".discussion-content").appendChild(ul);
          scroll();
        });
    })

    .declareService(function () {
      var form_gadget = this;

      function formSubmit(submit_event) {
        return form_gadget.notifySubmitting()
          .push(function () {
            var text = submit_event.target[0].value;
            submit_event.target[0].value = "";
            return form_gadget.jio_putAttachment(
              form_gadget.props.jid,
              'MESSAGE',
              text
            );
          })
          .push(function () {
            return form_gadget.refresh();
          })
          .push(function () {
            return form_gadget.notifySubmitted();
          })
          .push(undefined, function (error) {
            return form_gadget.notifySubmitted()
              .push(function () {
                throw error;
              });
          });
      }

      // Listen to form submit
      return loopEventListener(
        form_gadget.props.element.querySelector('form'),
        'submit',
        false,
        formSubmit
      );
    })

    .declareService(function () {
      scroll();
    });

}(window, document, rJS, RSVP, loopEventListener));