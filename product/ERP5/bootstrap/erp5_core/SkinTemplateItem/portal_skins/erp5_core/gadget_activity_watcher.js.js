/*global window, rJS, RSVP, domsugar, jIO, console */
/*jslint nomen: true, maxlen:80, indent:2*/
(function (rJS, jIO, domsugar, RSVP, window) {
  "use strict";

  function putMessageType(data, messagetype, string, array) {
    var i;
    if (data[string] && data[string].line_list) {
      for (i = 0; i < data[string].line_list.length; i += 1) {
        array.push(domsugar('tr', [
          domsugar('td', {text: messagetype}),
          domsugar('td', {text: data[string].line_list[i].count}),
          domsugar('td', {text: data[string].line_list[i].method_id}),
          domsugar('td', {text: data[string].line_list[i].node}),
          domsugar('td', {text: data[string].line_list[i].min_pri}),
          domsugar('td', {text: data[string].line_list[i].max_pri})
        ]));
      }
    }
  }

  function putMessageType2(data, messagetype, string, array) {
    var i;
    if (data[string] && data[string].line_list) {
      for (i = 0; i < data[string].line_list.length; i += 1) {
        array.push(domsugar('tr', [
          domsugar('td', {text: messagetype}),
          domsugar('td', {text: data[string].line_list[i].pri}),
          domsugar('td', {text: data[string].line_list[i].min}),
          domsugar('td', {text: data[string].line_list[i].avg}),
          domsugar('td', {text: data[string].line_list[i].max})
        ]));
      }
    }
  }

  rJS(window)
    .declareMethod('render', function (options) {
      console.log(options);
      return this.changeState(options);
    })

    .onLoop(function () {
      var form_gadget = this;
      if (!form_gadget.state.read_activity_list_url) {
        // renderjs has not yet been called
        // gadget doesn't know which URL to call
        return undefined;
      }
      return new RSVP.Queue()
        .push(function () {
          return jIO.util.ajax(
            {
              "type": "GET",
              "url": form_gadget.state.read_activity_list_url,
              "xhrFields": {
                withCredentials: true
              }
            }
          );
        })
        .push(function (evt) {
          var data = JSON.parse(evt.target.response),
            tbody1_content_list = [],
            tbody2_content_list = [];
          putMessageType(data, 'dict', 'SQLDict', tbody1_content_list);
          putMessageType(data, 'queue', 'SQLQueue', tbody1_content_list);
          putMessageType2(data, 'dict', 'SQLDict2', tbody2_content_list);
          putMessageType2(data, 'queue', 'SQLQueue2', tbody2_content_list);
          domsugar(form_gadget.element.querySelector(".activity_watcher_gadget"), [
            'Date : ',
            new Date().toTimeString(),

            domsugar('table', [
              domsugar('thead', [domsugar('tr', [
                domsugar('th', {text: 'Type'}),
                domsugar('th', {text: 'Count'}),
                domsugar('th', {text: 'Method Id'}),
                domsugar('th', {text: 'Processing Node'}),
                domsugar('th', {text: 'Min pri'}),
                domsugar('th', {text: 'Max pri'})
              ])]),
              domsugar('tbody', tbody1_content_list)
            ]),

            domsugar('table', [
              domsugar('thead', [domsugar('tr', [
                domsugar('th', {text: 'Type'}),
                domsugar('th', {text: 'Priority'}),
                domsugar('th', {text: 'Min'}),
                domsugar('th', {text: 'Avg'}),
                domsugar('th', {text: 'Max'})
              ])]),
              domsugar('tbody', tbody2_content_list)
            ])
          ]);

        }, function (error) {
          //Exception is raised if network is lost for some reasons,
          //in this case, try patiently until network is back.
          console.warn("Unable to fetch activities from ERP5", error);
          form_gadget.element.querySelector(".activity_watcher_gadget")
                     .textContent = "Unable to fetch activities from ERP5";
        });

    }, 1000);
}(rJS, jIO, domsugar, RSVP, window));