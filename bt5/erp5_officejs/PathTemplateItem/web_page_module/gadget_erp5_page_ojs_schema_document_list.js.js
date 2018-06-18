/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("getSetting", "getSetting")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .allowPublicAcquisition("jio_allDocs", function (param_list) {
      var gadget = this;
      return gadget.jio_allDocs(param_list[0])
        .push(function (result) {
          var i, date, len = result.data.total_rows;
          for (i = 0; i < len; i += 1) {
            if (result.data.rows[i].value.hasOwnProperty("modification_date")) {
              date = new Date(result.data.rows[i].value.modification_date);
              result.data.rows[i].value.modification_date = {
                field_gadget_param: {
                  allow_empty_time: 0,
                  ampm_time_style: 0,
                  css_class: "date_field",
                  date_only: 0,
                  description: "The Date",
                  editable: 0,
                  hidden: 0,
                  hidden_day_is_last_day: 0,
                  "default": date.toUTCString(),
                  key: "modification_date",
                  required: 0,
                  timezone_style: 0,
                  title: "Modification Date",
                  type: "DateTimeField"
                }
              };
              result.data.rows[i].value["listbox_uid:list"] = {
                key: "listbox_uid:list",
                value: 2713
              };
            }
          }
          return result;
        });
    })

    .allowPublicAcquisition('notifySubmit', function () {
      return this.triggerSubmit();
    })

    .declareMethod("triggerSubmit", function () {
      var argument_list = arguments;
      return this.getDeclaredGadget('form_list')
        .push(function (gadget) {
          return gadget.triggerSubmit.apply(gadget, argument_list);
        });
    })

    .declareMethod("render", function (options) {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          var portal_type = options.portal_type || gadget.getSetting("portal_type");
          return RSVP.all([
            gadget.getDeclaredGadget('form_list'),
            portal_type
          ]);
        })
        .push(function (result) {
          var column_list = [
            ['title', 'Title'],
            ['reference', 'Reference'],
            ['language', 'Language'],
            ['description', 'Description'],
            ['version', 'Version'],
            ['modification_date', 'Modification Date']
          ],
            query = 'portal_type:"' + result[1] + '"';
          if (options.schema) {
            query += ' AND schema:"' + options.schema + '"';
          }
          query = encodeURIComponent(query);
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
                  "query": "urn:jio:allDocs?query=" + query,
                  "portal_type": [],
                  "search_column_list": column_list,
                  "sort_column_list": column_list,
                  "sort": [['modification_date', 'descending']],
                  "title": options.schema_title || "Schemas",
                  "type": "ListBox"
                }
              }},
              "_links": {
                "type": {
                  // form_list display portal_type in header
                  name: ""
                }
              }
            },
            form_definition: {
              group_list: [[
                "bottom",
                [["listbox"]]
              ]]
            }
          });
        })
        .push(function () {
          var tasks;
          if (options.portal_type === "JSON Document") {
            tasks = [
              gadget.getUrlFor({command: "index", options: {
                  page: "ojs_add_json_document",
                  schema: options.schema
                }}),
              gadget.getSetting('document_title_plural')
            ];
          } else {
            tasks = [
              gadget.getUrlFor({command: "index", options: {"page": "ojs_multi_upload"}}),
              gadget.getSetting('document_title_plural')
            ];
          }
          return RSVP.all(tasks);
        })
        .push(function (result) {
          return gadget.updateHeader({
            page_title: options.schema_title || result[1],
            filter_action: true,
            add_url: result[0]
          });
        });
    });
}(window, rJS, RSVP));