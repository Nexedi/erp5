/*global window, rJS, RSVP, Handlebars, jIO, location */
/*jslint nomen: true, maxlen:80, indent:2*/
(function (rJS, jIO, Handlebars, RSVP, window) {
  "use strict";
  var gk = rJS(window),
    data_source = gk.__template_element.getElementById('getData').innerHTML,
    get_data_template = Handlebars.compile(data_source);
  function putMessageType(data, messagetype, string) {
    var i;
    if (data[string] && data[string].line_list) {
      for (i = 0; i < data[string].line_list.length; i += 1) {
        data[string].line_list[i].messagetype = messagetype;
      }
      return data[string].line_list;
    }
    return '';
  }

  rJS(window)
    .ready(function (g) {
      g.props = {};
    })
    .ready(function (g) {
      return g.getElement().push(function (element) {
        g.props.element = element;
      });
    })
    .declareService(function () {
      var form_gadget = this,
        html_content,
        basedir = location.pathname.split('/').slice(0, -1).join('/') + '/',
        queue = new RSVP.Queue();
      function getDataExamine() {
        queue
          .push(function () {
            return jIO.util.ajax(
              {
                "type": "POST",
                "url":  basedir + 'ActivityTool_getSqlStatisticList',
                "xhrFields": {
                  withCredentials: true
                }
              }
            );
          })
          .push(function (evt) {
            var data = JSON.parse(evt.target.response);
            html_content = get_data_template(
              {
                time: new Date().toTimeString(),
                messageList1: putMessageType(data, 'dict', 'SQLDict'),
                messageList2: putMessageType(data, 'queue', 'SQLQueue'),
                messagePri1 : putMessageType(data, 'dict', 'SQLDict2'),
                messagePri2 : putMessageType(data, 'queue', 'SQLQueue2')
              }
            );

            form_gadget.props.element.querySelector(".activity_watcher_gadget")
                            .innerHTML = html_content;
            return RSVP.delay(1000);
          })
          .push(function () {
            return getDataExamine();
          });
      }
      return queue.push(function () {
        return getDataExamine();
      });
    });
}(rJS, jIO, Handlebars, RSVP, window));