/*global document, window, rJS */
/*jslint nomen: true, indent: 2, maxerr: 10, maxlen: 90 */
(function (document, window, rJS) {
  "use strict";

  rJS(window)

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("getSetting", "getSetting")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("render", function (options) {
      var gadget = this;
      return gadget.getSetting("hateoas_url")
        .push(function (hateoas_url) {
          return gadget.redirect({
            'command': 'display_stored_state',
            'options': {
              'page': 'form',
              'editable': 0,
              'jio_key': 'project_module',
              'view': hateoas_url +
              '/ERP5Document_getHateoas?mode=traverse&relative_url=' +
              'project_module&view=ProjectModule_viewProjectManagementList',
              'field_listbox_sort_list:json': [["title", "ascending"]],
              'field_listbox_column_list:json': ["title",
                                                 "default_destination_section_title"],
              'extended_search': 'selection_domain_state_project_domain:  "started"'
            }
          });
        });
    });

}(document, window, rJS));