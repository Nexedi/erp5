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

    .declareMethod('render', function () {
      var gadget = this;
      gadget.options = {
        'jio_key': 'artificial_task_module'
      };
      return gadget.getSetting('hateoas_url')
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
              'tool_list': [],
              'skill_list': [],
              'hateoas_url': gadget.hateoas_url,
              'request_options': {
                'document_id': gadget.options.jio_key,
                'post_url': gadget.hateoas_url + gadget.options.jio_key + "/ArtificialTaskModule_startNewArtificialTask"
              },
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
