/*global document, window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 10, maxlen: 80 */
(function (document, window, rJS, RSVP) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")

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
            //TODO migrate
            gadget.getUrlFor({command: 'store_and_change', options: {
              page: "ojsm_jump",
              jio_key: instance_tree.opml_url,
              title: instance_tree.title,
              view_title: "Related OPML",
              search_page: "ojsm_status_list"
            }});
          })
          .push(function (url) {
            header_options.jump_url = url;
            header_options.save_action = true;
            return header_options;
          });
      case "software_instance":
        header_options.refresh_action = true;
        if (page_options.doc._links !== undefined) {
          //TODO get view/action urls
          header_options.resources_url = "a";
          header_options.processes_url = "b";
          if (header_options.hasOwnProperty('actions_url'))
            delete header_options.actions_url;
          if (header_options.hasOwnProperty('tab_url'))
            delete header_options.tab_url;
        }
        return header_options;
      case "promise":
        header_options.refresh_action = true;
        return header_options;
      default:
        return header_options;
      }
    });

}(document, window, rJS, RSVP));