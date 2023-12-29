/*global document, window, rJS, RSVP, Rusha */
/*jslint nomen: true, indent: 2, maxerr: 10, maxlen: 80 */
(function (document, window, rJS, RSVP, Rusha) {
  "use strict";

  var rusha = new Rusha();

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("getUrlForList", "getUrlForList")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("getOptions", function (portal_type_dict, page_options, header_options) {
      var gadget = this;
      switch (portal_type_dict.view) {
      case "instance_tree":
        return new RSVP.Queue()
          .push(function () {
            return gadget.jio_get(page_options.jio_key);
          })
          .push(function (instance_tree) {
            return gadget.getUrlFor({command: 'store_and_change', options: {
              page: "ojsm_jump",
              jio_key: instance_tree.opml_url,
              title: instance_tree.title,
              view_title: "Related OPML",
              search_page: "ojs_local_controller",
              portal_type: "Promise Module"
            }});
          })
          .push(function (url) {
            header_options.jump_url = url;
            header_options.save_action = true;
            return header_options;
          });
      case "software_instance":
        var promise_list = [];
        return new RSVP.Queue()
          .push(function () {
            promise_list.push({ command: 'change', options: page_options.view_action_dict.view_list.monitoring_resources_view });
            promise_list.push({ command: 'change', options: page_options.view_action_dict.view_list.monitoring_processes_view });
            promise_list.push({command: 'history_previous'});
            return gadget.getUrlForList(promise_list);
          })
          .push(function (url_list) {
            header_options.refresh_action = true;
            if (page_options.doc._links !== undefined) {
              header_options.resources_url = url_list[0];
              header_options.processes_url = url_list[1];
              if (header_options.hasOwnProperty('actions_url'))
                delete header_options.actions_url;
              if (header_options.hasOwnProperty('tab_url'))
                delete header_options.tab_url;
            }
            if (page_options.form_definition.title == "Processes") {
              header_options.selection_url = url_list[2];
              delete header_options.processes_url;
              delete header_options.refresh_action;
              delete header_options.previous_url;
              delete header_options.next_url;
            }
            if (page_options.form_definition.title == "Resources") {
              header_options.selection_url = url_list[2];
              delete header_options.resources_url;
              delete header_options.refresh_action;
              delete header_options.previous_url;
              delete header_options.next_url;
            }
            return header_options;
          });
      case "promise":
        header_options.refresh_action = true;
        return header_options;
      case "opml":
        return new RSVP.Queue()
          .push(function () {
            var hosting_key = rusha.digestFromString(page_options.jio_key);
            return RSVP.all([
              gadget.getUrlFor({command: 'push_history', options: {
                page: "ojsm_jump",
                jio_key: hosting_key,
                title: page_options.opml_title,
                view_title: "Related Instance Tree"
              }}),
              gadget.getUrlFor({command: 'change', options: {
                page: 'ojsm_opml_delete',
                jio_key: page_options.jio_key,
                return_url: 'settings_configurator'
              }})
            ]);
          })
          .push(function (url_list) {
            header_options.jump_url = url_list[0];
            header_options.delete_url = url_list[1];
            header_options.save_action = true;
            return header_options;
          });
      default:
        return header_options;
      }
    });

}(document, window, rJS, RSVP, Rusha));