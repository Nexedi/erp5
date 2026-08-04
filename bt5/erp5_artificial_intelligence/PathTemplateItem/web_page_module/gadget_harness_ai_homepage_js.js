/*global window, rJS, RSVP, FormData, URI, jIO */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")

    .allowPublicAcquisition('getCommentPostList', function () {
      return [];
    })
    .allowPublicAcquisition('postComment', function (argument_list) {
      var gadget = this,
        document_id = argument_list[0],
        form_data_json = argument_list[1];
      return gadget.jio_putAttachment(
        document_id,
        gadget.hateoas_url + document_id + "/ArtificialTaskModule_startNewArtificialTask",
        form_data_json
      );
    })

    .declareMethod('render', function () {
      var gadget = this;
      gadget.options = {
        'jio_key': 'artificial_task_module'
      };
      return gadget.jio_getAttachment(
        'portal_workflow',
        'links'
      ).push(function () {
        return gadget.getSetting('hateoas_url');
      })
        .push(function (hateoas_url) {
          gadget.hateoas_url = hateoas_url;
        })
        .push(function () {
          var state_dict = {
            id: 'artificial_task_module'
          };
          return gadget.changeState(state_dict);
        });
    })
    .onStateChange(function () {
      var gadget = this;
      return gadget.getDeclaredGadget("gadget_chat")
        .push(function (chat) {
          return chat.render({
              'hateoas_url': gadget.hateoas_url,
              'jio_key': gadget.options.jio_key,
              'editor_options' : {
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
        });
    });
}(window, rJS, RSVP));
