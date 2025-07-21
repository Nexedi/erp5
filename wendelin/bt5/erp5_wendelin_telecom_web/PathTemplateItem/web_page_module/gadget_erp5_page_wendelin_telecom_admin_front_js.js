/*global window, rJS*/
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")


    .allowPublicAcquisition('updateHeader', function () {
      return;
    })
    .allowPublicAcquisition('getUrlParameter', function (argument_list) {
      return this.getUrlParameter(argument_list)
        .push(function (result) {
          if ((result === undefined) && (
              (argument_list[0] === 'field_listbox_project_sort_list:json') ||
                (argument_list[0] === 'field_listbox_movement_sort_list:json') ||
                (argument_list[0] === 'field_listbox_ors_sort_list:json')
            )) {
            return [['modification_date', 'descending']];
          }
          return result;
        });
    })
    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function () {
      var gadget = this;

      return gadget.updateHeader({
        page_title: 'Wendelin Telecom'
      })
        .push(function () {
          return gadget.getDeclaredGadget('form_view');
        })
        .push(function (form_gadget) {
          return form_gadget.render({
            erp5_document: {"_embedded": {"_view": {
              "listbox_project": {
                "column_list": [
                  ['title', 'Title'],
                  ['portal_type', 'Portal Type'],
                  ['translated_validation_state_title', 'State']
                ],
                "show_anchor": 0,
                "default_params": {},
                "editable": 1,
                "editable_column_list": [],
                "key": "field_listbox_project",
                "lines": 10,
                "list_method": "portal_catalog",
                "query": "urn:jio:allDocs?query=portal_type%3A%28%22Project%22%29",
                "portal_type": ["Project"],
                "search_column_list": [],
                "sort_column_list": [],
                "title": "Latest Client Projects",
                "type": "ListBox"
              },
              "listbox_ors": {
                "column_list": [
                  ['title', 'Title'],
                  ['portal_type', 'Portal Type'],
                  ['translated_validation_state_title', 'State']
                ],
                "show_anchor": 0,
                "default_params": {},
                "editable": 1,
                "editable_column_list": [],
                "key": "field_listbox_ors",
                "lines": 10,
                "list_method": "portal_catalog",
                "query": "urn:jio:allDocs?query=portal_type%3A%22Data%20Acquisition%20Unit%22",
                "portal_type": ["Data Acquisition Unit"],
                "search_column_list": [],
                "sort_column_list": [],
                "title": "Latest Open Radio Stations",
                "type": "ListBox"
              },
              "listbox_movement": {
                "column_list": [
                  ['title', 'Title'],
                  ['portal_type', 'Portal Type'],
                  ['translated_simulation_state_title', 'State']
                ],
                "show_anchor": 0,
                "default_params": {},
                "editable": 1,
                "editable_column_list": [],
                "key": "field_listbox_movement",
                "lines": 10,
                "list_method": "portal_catalog",
                "query": "urn:jio:allDocs?query=portal_type%3A%28%22Data%20Ingestion%22%20OR%20%20%22Data%20Analysis%22%29",
                "portal_type": ["Data Ingestion", "Data Analysis"],
                "search_column_list": [],
                "sort_column_list": [],
                "title": "Latest Ingestions and Analyses",
                "type": "ListBox"
              }
            }},
              "_links": {
                "type": {
                  // form_list display portal_type in header
                  name: ""
                }
              }},
            form_definition: {
              group_list: [
                [
                  "bottom",
                  [["listbox_project"], ["listbox_ors"], ["listbox_movement"]]
                ]
              ]
            }
          });
        });

    });

}(window, rJS));