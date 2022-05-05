/*globals window, RSVP, rJS*/
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, RSVP, rJS) {
  "use strict";
  rJS(window)
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .allowPublicAcquisition('updateHeader', function () {
      return;
    })
   .allowPublicAcquisition("jio_allDocs", function (param_list) {
      var gadget = this;
      return gadget.jio_allDocs(param_list[0])
        .push(function (result) {
          var i, value, news, len = result.data.total_rows;
          for (i = 0; i < len; i += 1) {
            if (result.data.rows[i].value.hasOwnProperty("title")) {
              value = result.data.rows[i].id;
              result.data.rows[i].value['listbox_uid:list'] = {
                "key": "",
                "value": ""
              };
              result.data.rows[i].value.title = {
                field_gadget_param : {
                  css_class: "",
                  hidden: 0,
                  editable: true,
                  default: {jio_key: value},
                  key: 'success_case_in_listbox',
                  url: "gadget_erp5_eci_success_case_widget.html",
                  type: "GadgetField"
                }
              };
            }
          }
          return result;
        });
    })
   .declareMethod('triggerSubmit', function triggerSubmit() {
      return this.getDeclaredGadget('form_list')
        .push(function (g) {
          return g.triggerSubmit();
        });
    }, {mutex: 'changestate'})
    .allowPublicAcquisition('getUrlParameter', function (argument_list) {
      return this.getUrlParameter(argument_list)
        .push(function (result) {
          if ((result === undefined) &&
              (argument_list[0] === 'field_listbox_sort_list:json')) {
            return [['title', 'ascending']];
          }

          return result;
        });
    })

    .declareMethod("render", function () {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return gadget.jio_allDocs({
            select_list: [
              'selection_domain_category',
              'selection_domain_industry',
              'selection_domain_country',
              'selection_domain_publisher',
              'selection_domain_similar_solution',
              'selection_domain_publisher_country'
            ],
            query: 'portal_type:"success_case"'
          });
        })
        .push(function (result) {
          function getUniqueArray(data_list, property) {
            var value = data_list.map((obj) => obj.value[property])
              .reduce((cur, prev) => cur.concat(prev))
             .filter(Boolean);
            return Array.from(new Set(value)).sort();
          }

          var category = getUniqueArray(result.data.rows, 'selection_domain_category'),
              industry = getUniqueArray(result.data.rows, 'selection_domain_industry'),
              country = getUniqueArray(result.data.rows, 'selection_domain_country'),
              publisher = getUniqueArray(result.data.rows, 'selection_domain_publisher'),
              similar_solution = getUniqueArray(result.data.rows, 'selection_domain_similar_solution'),
              publisher_country = getUniqueArray(result.data.rows, 'selection_domain_publisher_country');


          gadget.domain_root_list = [
            ['category', 'Category'],
            ['industry', 'Industry'],
            ['country', 'Country'],
            ['publisher', 'Provider'],
            ['similar_solution', 'Similar solution'],
            ['publisher_country', 'Provider Country']
          ];
          gadget.domain_dict = {
            category: category.map(data => [data, data]),
            industry: industry.map(data => [data, data]),
            country: country.map(data => [data, data]),
            publisher: publisher.map(data => [data, data]),
            similar_solution: similar_solution.map(data => [data, data]),
            publisher_country: publisher_country.map(data => [data, data])
          };
          return RSVP.all([
            gadget.updateHeader({
              page_title: "Success case list",
              filter_action: true
            }),
            gadget.getDeclaredGadget("form_list")
          ]);
      })
      .push(function (result_list) {
        return result_list[1].render({
          erp5_document: {"_embedded": {"_view": {
            "listbox": {
              "column_list": [['title', 'Success cases']],
              "show_anchor": 0,
              "default_params": {},
              "editable": 1,
              "editable_column_list": [],
              "key": "field_listbox",
              "lines": 20,
              "list_method": "portal_catalog",
              "query": 'urn:jio:allDocs?query=portal_type:"success_case"',
              "portal_type": [],
              "search_column_list": [['modification_date', 'Updated Date']],
              "domain_root_list":  gadget.domain_root_list,
              "domain_dict": gadget.domain_dict,
              "sort_column_list": [['title', 'Success cases']],
              "title": "Success cases",
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
            ],
              ["hidden", ["listbox_modification_date"]]]
          }
        });
      });
    });
}(window, RSVP, rJS));