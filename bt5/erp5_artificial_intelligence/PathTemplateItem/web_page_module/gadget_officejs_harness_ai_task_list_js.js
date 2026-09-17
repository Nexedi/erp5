/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  rJS(window)
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("getSettingList", "getSettingList")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("updateHeader", "updateHeader")

    .declareMethod("render", function () {
      var gadget = this,
        current_version,
        index;

      current_version = window.location.href.replace(window.location.hash, "");
      index = current_version.indexOf(window.location.host) +
        window.location.host.length;
      current_version = current_version.substr(index);

      return new RSVP.Queue()
        .push(function () {
          return gadget.getSettingList(["migration_version", "app_configurator"]);
        })
        .push(function (setting_list) {
          var configurator = setting_list[1] || 'ojs_configurator';
          if (setting_list[0] !== current_version) {
            //if app version has changed, force storage selection
            return gadget.redirect({
              'command': 'display',
              'options': {
                'page': configurator,
                'auto_repair': true
              }
            });
          }
        })
        .push(function () {
          return RSVP.all([
            gadget.getDeclaredGadget('form_list'),
            gadget.getSetting("portal_type")
          ]);
        })
        .push(function (result) {
          var column_list = [
            ['title', 'Title'],
            ['state', 'State'],
            ['modification_date', 'Modification Date']
          ];
          return result[0].render({
            erp5_document: {
              "_embedded": {"_view": {
                "listbox": {
                  "column_list": column_list,
                  "show_anchor": 0,
                  "default_params": {},
                  "editable": 1,
                  "editable_column_list": [],
                  "key": "field_listbox",
                  "lines": 30,
                  "list_method": "portal_catalog",
                  "query": "urn:jio:allDocs?query=portal_type%3A%22" + result[1] + "%22",
                  "portal_type": [],
                  "search_column_list": column_list,
                  "sort_column_list": column_list,
                  "sort": [['modification_date', 'descending']],
                  "title": "Artificial Tasks",
                  "type": "ListBox"
                }
              }},
              "_links": { "type": { name: "" } }
            },
            form_definition: { group_list: [["bottom", [["listbox"]]]] }
          });
        })
        .push(function () {
          return gadget.updateHeader({
            page_title: "Artificial Task Module"
          });
        });
    });
}(window, rJS, RSVP));
