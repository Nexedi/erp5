/*global window, rJS, jIO, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80 */
(function (window, rJS, jIO, RSVP) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("getUrlForList", "getUrlForList")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .allowPublicAcquisition('updateHeader', function () {
      return;
    })
    .allowPublicAcquisition('getUrlForList', function (argument_list) {
      var i,
        options_list = argument_list[0],
        result_list = [];
      for (i = 0; i < options_list.length; i += 1) {
        if (options_list[i].command === 'index') {
          result_list.push({
            command: 'display_stored_state',
            options: {jio_key: options_list[i].options.jio_key}
          });
        } else {
          result_list.push(options_list[i]);
        }
      }
      return this.getUrlForList.apply(this, [result_list]);
    })

    .allowPublicAcquisition('jio_allDocs', function (argument_list) {
      // ERP5 does not support filtering/sorting on translated properties
      // Fetch the list of all modules from ERP5
      // and filter/sort it manually after
      var allDocs_options = argument_list[0],
        select_list = ['translated_title',
                       'business_application_translated_title', 'uid', 'id',
                       'title', '__id'],
        new_allDocs_options = {
          limit: allDocs_options.limit,
          query:
            '(parent_uid:"0" AND meta_type:"ERP5 Folder" AND id:"%_module")',
          select_list: select_list,
          sort_on: []
        },
        context = this;
      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            context.jio_allDocs(new_allDocs_options),
            context.getUrlParameter('extended_search')
          ]);
        })
        .push(function (result_list) {
          var data_rows = [],
            i,
            len = result_list[0].data.total_rows,
            query = result_list[1] || "";
          for (i = 0; i < len; i += 1) {
            // queries do not accept null value
            result_list[0].data.rows[i].value
                                       .business_application_translated_title =
              result_list[0].data.rows[i].value
                            .business_application_translated_title || '';
            result_list[0].data.rows[i].value.id =
              result_list[0].data.rows[i].id;
            data_rows.push(result_list[0].data.rows[i].value);
          }
          return jIO.QueryFactory.create(query)
            .exec(data_rows, {query: query, select_list: select_list,
                              sort_on: allDocs_options.sort_on});
        })
        .push(function (document_list) {
          var len = document_list.length,
            i,
            result = [];
          for (i = 0; i < len; i += 1) {
            result.push({id: document_list[i].id, value: document_list[i]});
          }
          return {data: {rows: result, total_rows: len}};
        });
    })

    .declareMethod("triggerSubmit", function () {
      var argument_list = arguments;
      return this.getDeclaredGadget('form_list')
        .push(function (gadget) {
          return gadget.triggerSubmit.apply(gadget, argument_list);
        });
    })
    .declareMethod("render", function () {
      var gadget = this,
        header_dict = {
          page_title: 'Modules',
          page_icon: 'puzzle-piece',
          filter_action: true
        };

      return gadget.getUrlFor({command: 'display'})
        .push(function (front_url) {
          header_dict.front_url = front_url;
          return gadget.updateHeader(header_dict);
        })
        .push(function () {
          return gadget.getDeclaredGadget('form_list');
        })
        .push(function (form_gadget) {
          var column_list = [
            ['translated_title', 'Title'],
            ['business_application_translated_title', 'Domain']
          ];
          return form_gadget.render({
            erp5_document: {"_embedded": {"_view": {
              "listbox": {
                "column_list": column_list,
                "show_anchor": 0,
                "default_params": {},
                "editable": 1,
                "editable_column_list": [],
                "key": "field_listbox",
                "lines": 1000,
                "list_method": "portal_catalog",
                "query": "urn:jio:allDocs?query=parent_uid%3A%220%22%20AND" +
                         "%20meta_type%3A%22ERP5%20Folder%22%20AND" +
                         "%20id%3A%22%25_module%22",
                "portal_type": [],
                "search_column_list": column_list,
                "sort_column_list": column_list,
                "sort": [["translated_title", "ASC"]],
                "title": "Modules",
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
              group_list: [[
                "bottom",
                [["listbox"]]
              ]]
            }
          });
        });
    });
}(window, rJS, jIO, RSVP));