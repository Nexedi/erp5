/*jslint indent: 2, nomen: true */
/*global window, rJS, jIO, URL, RSVP*/
(function (window, rJS, jIO, URL, RSVP) {
  "use strict";

  function check(gadget, storage, format) {
    var output_message = "output_message not set - there was an error";
    return new RSVP.Queue()
      .push(function () {
        return RSVP.all([
          storage.getAttachment('test', 'data'),
          jIO.util.ajax({
            type: "GET",
            url: new URL('./test_ooo_' + gadget.param.type + '.' + format, window.location.href),
            dataType: "blob"
          })
        ]);
      })
      .push(function (result) {
        return RSVP.all([
          jIO.util.readBlobAsText(result[0]),
          jIO.util.readBlobAsText(result[1].target.response)
        ]);
      }, function (error) {
        output_message = 'ERROR converting document: ' + error.message;
      })
      .push(function (result) {
        var div = window.document.createElement('div');
        if (result && result[0].target.response == result[1].target.response) {
          output_message = 'Converted ' + format + ' OK';
        }
        div.textContent = output_message;
        gadget.element.appendChild(div);
      });
  }

  rJS(window)
    .declareService(function () {
      var storage = jIO.createJIO({
        type: "indexeddb",
        database: "local_default"
      }),
        gadget = this,
        element_list =
          gadget.element.querySelectorAll("[data-renderjs-configuration]"),
        len = element_list.length,
        i,
        queue = new RSVP.Queue(),
        format_list;
      gadget.param = {};
      for (i = 0; i < len; i += 1) {
        gadget.param[element_list[i].getAttribute('data-renderjs-configuration')] =
          element_list[i].textContent;
      }
      format_list = JSON.parse(gadget.param.format_list);
      len = format_list.length;
      for (i = 0; i < len; i += 1) {
        queue.push(check(gadget, storage, format_list[i]));
      }
      return queue;
    });
}(window, rJS, jIO, URL, RSVP));
