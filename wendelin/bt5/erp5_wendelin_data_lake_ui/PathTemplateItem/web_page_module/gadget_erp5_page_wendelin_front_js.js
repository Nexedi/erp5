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
              (argument_list[0] === 'field_listbox_storage_sort_list:json') ||
                (argument_list[0] === 'field_listbox_movement_sort_list:json') ||
                (argument_list[0] === 'field_listbox_transformation_sort_list:json') || 
                (argument_list[0] === 'field_listbox_sensor_sort_list:json') ||
                (argument_list[0] === 'field_listbox_notebook_sort_list:json') 
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
        page_title: 'Wendelin'
      })
        .push(function () {
          return gadget.getDeclaredGadget('form_view');
        })
        .push(function (form_gadget) {
          return form_gadget.render({
            erp5_document: {"_embedded": {"_view": {
              "listbox_storage": {
                "column_list": [
                  ['title', 'Title'],
                  ['portal_type', 'Portal Type'],
                  ['translated_validation_state_title', 'State']
                ],
                "show_anchor": 0,
                "default_params": {},
                "editable": 1,
                "editable_column_list": [],
                "key": "field_listbox_storage",
                "lines": 5,
                "list_method": "portal_catalog",
                "query": "urn:jio:allDocs?query=portal_type%3A%28%22Data%20Stream%22%20OR%20%20%22Data%20Array%22%29",
                "portal_type": ["Data Stream", "Data Array"],
                "search_column_list": [],
                "sort_column_list": [],
                "title": "Latest Streams and Arrays",
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
                "lines": 5,
                "list_method": "portal_catalog",
                "query": "urn:jio:allDocs?query=portal_type%3A%28%22Data%20Ingestion%22%20OR%20%20%22Data%20Analysis%22%29",
                "portal_type": ["Data Ingestion", "Data Analysis"],
                "search_column_list": [],
                "sort_column_list": [],
                "title": "Latest Ingestions and Analyses",
                "type": "ListBox"
              },
              "listbox_transformation": {
                "column_list": [
                  ['title', 'Title'],
                  ['portal_type', 'Portal Type'],
                  ['translated_validation_state_title', 'State']
                ],
                "show_anchor": 0,
                "default_params": {},
                "editable": 1,
                "editable_column_list": [],
                "key": "field_listbox_transformation",
                "lines": 5,
                "list_method": "portal_catalog",
                "query": "urn:jio:allDocs?query=portal_type%3A%22Data%20Transformation%22",
                "portal_type": ["Data Transformation"],
                "search_column_list": [],
                "sort_column_list": [],
                "title": "Latest Transformations",
                "type": "ListBox"
              },
              "listbox_sensor": {
                "column_list": [
                  ['title', 'Title'],
                  ['portal_type', 'Portal Type'],
                  ['translated_validation_state_title', 'State']
                ],
                "show_anchor": 0,
                "default_params": {},
                "editable": 1,
                "editable_column_list": [],
                "key": "field_listbox_sensor",
                "lines": 5,
                "list_method": "portal_catalog",
                "query": "urn:jio:allDocs?query=portal_type%3A%22Data%20Acquisition%20Unit%22",
                "portal_type": ["Data Acquisition"],
                "search_column_list": [],
                "sort_column_list": [],
                "title": "Latest Sensors",
                "type": "ListBox"
              },
              "listbox_notebook": {
                "column_list": [
                  ['title', 'Title'],
                  ['portal_type', 'Portal Type'],
                  ['translated_validation_state_title', 'State']
                ],
                "show_anchor": 0,
                "default_params": {},
                "editable": 1,
                "editable_column_list": [],
                "key": "field_listbox_notebook",
                "lines": 5,
                "list_method": "portal_catalog",
                "query": "urn:jio:allDocs?query=portal_type%3A%22Notebook%22",
                "portal_type": ["Notebook"],
                "search_column_list": [],
                "sort_column_list": [],
                "title": "Latest Notebooks",
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
                  [["listbox_notebook"],["listbox_storage"], ["listbox_movement"], ["listbox_transformation"], ["listbox_sensor"]]
                ]
              ]
            }
          });
        });

    });

}(window, rJS));