/*global window, rJS, jIO, FormData*/
/*jslint indent:2, maxlen: 80, nomen: true */
(function (window, rJS, jIO, FormData) {
  "use strict";
  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("redirect", "redirect")

    .declareService(function handleWebShareFile() {
      var gadget = this,
        data = new FormData();
      data.append('file', 'test');
      return new RSVP.Queue()
        .push(function () {
          return jIO.util.ajax({
            type: 'POST',
            url: 'testpostData',
            dataType: "blob",
            processData: false,
            contentType: false,
            data: data
          });
        })
        .push(function () {
          return gadget.redirect({
            command: 'display',
            options: {page: "ojs_smart_assistant_upload_shared_file"}
          });
        });
    });
}(window, rJS, jIO, FormData));