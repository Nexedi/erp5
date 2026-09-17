/*global window, rJS */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS) {
  "use strict";

  rJS(window)
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("jio_post", "jio_post")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")

    .allowPublicAcquisition('getCommentPostList', function () {
      return [];
    })
    .allowPublicAcquisition('postComment', function (argument_list) {
      var gadget = this,
        form_data_json = argument_list[1],
        artificial_task_id;
      return gadget.jio_post({
        portal_type: 'Artificial Task',
        parent_relative_url: 'artificial_task_module',
        state: 'planned',
        title: form_data_json.data
      })
        .push(function (new_id) {
          artificial_task_id = new_id;
          return gadget.jio_post({
            portal_type: 'Artificial Task Line',
            parent_relative_url: artificial_task_id,
            text_content: form_data_json.data,
            int_index: 0
          });
        })
        .push(function () {
          return {target: {getResponseHeader: function (name) {
            return name === "X-Location" ? ("x/y/" + artificial_task_id) : null;
          }}};
        });
    })

    .declareMethod('render', function () {
      var gadget = this;
      gadget.options = {'jio_key': 'artificial_task_module'};
      return gadget.getSetting('hateoas_url')
        .push(function (hateoas_url) {
          gadget.hateoas_url = hateoas_url;
        })
        .push(function () {
          return gadget.changeState({id: 'artificial_task_module'});
        });
    })
    .onStateChange(function () {
      var gadget = this;
      return gadget.getDeclaredGadget("gadget_chat")
        .push(function (chat) {
          return chat.render({
            'hateoas_url': gadget.hateoas_url,
            'jio_key': gadget.options.jio_key,
            'editor_options': {
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
}(window, rJS));
