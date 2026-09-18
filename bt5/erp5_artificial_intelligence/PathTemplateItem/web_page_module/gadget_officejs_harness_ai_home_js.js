/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  rJS(window)
    .declareAcquiredMethod("getSettingList", "getSettingList")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("jio_post", "jio_post")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("redirect", "redirect")
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
      var gadget = this,
        current_version,
        index;
      gadget.options = {'jio_key': 'artificial_task_module'};

      current_version = window.location.href.replace(window.location.hash, "");
      index = current_version.indexOf(window.location.host) +
        window.location.host.length;
      current_version = current_version.substr(index);

      return new RSVP.Queue()
        .push(function () {
          return gadget.getSettingList(["migration_version", "app_configurator", "hateoas_url"]);
        })
        .push(function (setting_list) {
          var configurator = setting_list[1] || 'ojs_configurator';
          if (setting_list[0] !== current_version) {
            return gadget.redirect({
              'command': 'display',
              'options': {
                'page': configurator,
                'auto_repair': true
              }
            });
          }
          gadget.hateoas_url = setting_list[2];
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
}(window, rJS, RSVP));
