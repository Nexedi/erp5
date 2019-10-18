/*global document, window, rJS */
/*jslint nomen: true, indent: 2, maxerr: 10, maxlen: 90 */
(function (document, window, rJS) {
  "use strict";

  rJS(window)

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("redirect", "redirect")
    //.declareAcquiredMethod("getSetting", "getSetting")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("render", function (options) {
      var gadget = this;
      return gadget.redirect({
        'command': 'display_with_history',
        'options': {
          'page': 'form',
          'editable': 0,
          'jio_key': 'project_module',
          'view': 'view',
          'field_listbox_sort_list:json': [["title", "ascending"]],
          'field_listbox_column_list:json': ["title",
                                             "default_destination_section_title"],
          'extended_search': 'translated_validation_state_title:  "Started"'
        }
      });
    });

}(document, window, rJS));