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
            //TODO set title here
            header_options.jump_url = url;
            header_options.save_action = true;
            return header_options;
          });
      case "software_instance":
        return {};
      case "promise":
        return {};
      default:
        return {};
      }
    });

}(document, window, rJS, RSVP));