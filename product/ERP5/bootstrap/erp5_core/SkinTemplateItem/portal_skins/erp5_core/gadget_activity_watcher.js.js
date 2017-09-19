/*global window, rJS, RSVP, Handlebars, jIO, location, console */
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
    .onLoop(function () {
      var form_gadget = this,
        basedir = location.pathname.split('/').slice(0, -1).join('/') + '/';
      return new RSVP.Queue()
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
          form_gadget.element.querySelector(".activity_watcher_gadget")
                             .innerHTML = get_data_template(
            {
              time: new Date().toTimeString(),
              messageList1: putMessageType(data, 'dict', 'SQLDict'),
              messageList2: putMessageType(data, 'queue', 'SQLQueue'),
              messagePri1 : putMessageType(data, 'dict', 'SQLDict2'),
              messagePri2 : putMessageType(data, 'queue', 'SQLQueue2')
            }
          );

        }, function (error) {
          //Exception is raised if network is lost for some reasons,
          //in this case, try patiently until network is back.
          console.warn("Unable to fetch activities from ERP5", error);
          form_gadget.element.querySelector(".activity_watcher_gadget")
                     .textContent = "Unable to fetch activities from ERP5";
        });

    }, 1000);
}(rJS, jIO, Handlebars, RSVP, window));