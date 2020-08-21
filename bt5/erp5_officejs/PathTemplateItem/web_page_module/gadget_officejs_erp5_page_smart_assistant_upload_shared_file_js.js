/*global window, rJS, jIO, Handlebars, RSVP, Blob*/
/*jslint indent:2, maxlen: 80, nomen: true */
(function (window, rJS, jIO, RSVP) {
  "use strict";
  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_post", "jio_post")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")

    .declareService(function handleWebShareFile() {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return jIO.util.ajax({
            type: 'GET',
            url: 'getSharedData',
            dataType: "blob"
          });
        })
        .push(function (resx) {
          // Condition: when there's uploaded data
          if (resx.target.response.size) {
            return gadget.notifySubmitting()
              .push(function () {
                return gadget.jio_post({
                  "title": Date(), //get date as title
                  portal_type: "Smart Assistant File",
                  parent_relative_url: "smart_assistant_file_module",
                  validation_state: 'draft'
                });
              })
              .push(function (id) {
                return gadget.jio_putAttachment(
                  id,
                  'data',
                  resx.target.response
                );
              })
              .push(function () {
                return gadget.notifySubmitted({
                  "message": "Data created",
                  "status": "success"
                });
              })
              .push(function () {
                return gadget.redirect({
                  command: 'display',
                  options: {page: "ojs_smart_assistant_document_list"}
                });
              });
          }
          // Condition: if there's no data
          return gadget.notifySubmitted({
            "message": "No data found",
            "status": "failed"
          })
            .push(function () {
              return gadget.redirect({
                command: 'display',
                options: {page: "ojs_smart_assistant_home"}
              });
            });
        });
    });
}(window, rJS, jIO, RSVP));