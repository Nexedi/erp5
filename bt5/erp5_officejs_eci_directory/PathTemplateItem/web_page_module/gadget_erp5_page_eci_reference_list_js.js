/*globals window, RSVP, rJS, QueryFactory*/
/*jslint indent: 2, nomen: true, maxlen: 180*/
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
      var gadget = this,
        i,
        query_list = [],
        selection_domain_reference_industry,
        selection_domain_reference_country,
        search = QueryFactory.create(param_list[0].query.trim());
      if (search.operator === "AND") {
        for (i = 0; i < search.query_list.length; i += 1) {
          if (search.query_list[i].key === 'selection_domain_reference_country') {
            selection_domain_reference_country = search.query_list[i];
          } else if (search.query_list[i].key === 'selection_domain_reference_industry') {
            selection_domain_reference_industry = search.query_list[i];
          } else {
            query_list.push(search.query_list[i]);
          }
        }
      }
      // search country combine with reference
      if (selection_domain_reference_country && selection_domain_reference_industry) {
        var new_criteria;
        new_criteria = new SimpleQuery({
          key: 'selection_domain_reference_industry_country_set',
          operator: '=',
          type: "simple",
          value: [selection_domain_reference_industry.value, selection_domain_reference_country.value]
        });
        query_list.push(new_criteria);
      } else {
        if (selection_domain_reference_country) {
          query_list.push(selection_domain_reference_country);
        }
        if (selection_domain_reference_industry) {
          query_list.push(selection_domain_reference_industry);
        }
      }
      search.query_list = query_list;
      param_list[0].query = Query.objectToSearchText(search);
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
                  editable: true,
                  hidden: 0,
                  default: {
                    jio_key: value
                  },
                  key: 'success_case_in_listbox',
                  url: "gadget_erp5_eci_reference_widget.html",
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
              'selection_domain_reference_industry',
              'selection_domain_reference_country',
              'selection_domain_publisher',
              'selection_domain_similar_solution',
              'selection_domain_country',
              'selection_domain_category'
            ],
            query: 'portal_type:"solution"'
          });
        })
        .push(function (result) {
          function getUniqueArray(data_list, property) {
            var value = data_list.map((obj) => obj.value[property])
              .reduce((cur, prev) => cur.concat(prev))
             .filter(Boolean);
            return Array.from(new Set(value)).sort();
          }
          var industry = getUniqueArray(result.data.rows, 'selection_domain_reference_industry'),
              country = getUniqueArray(result.data.rows, 'selection_domain_reference_country'),
              publisher = getUniqueArray(result.data.rows, 'selection_domain_publisher'),
              similar_solution = getUniqueArray(result.data.rows, 'selection_domain_similar_solution'),
              solution_country = getUniqueArray(result.data.rows, 'selection_domain_country'),
              category = getUniqueArray(result.data.rows, 'selection_domain_category');


          gadget.domain_root_list = [
            ['reference_industry', 'Industry'],
            ['reference_country', 'Country'],
            ['publisher', 'Provider'],
            ['similar_solution', 'Similar solution'],
            ['country', 'Provider Country'],
            ['category', 'Category']
          ];
          gadget.domain_dict = {
            reference_industry: industry.map(data => [data, data]),
            reference_country: country.map(data => [data, data]),
            publisher: publisher.map(data => [data, data]),
            similar_solution: similar_solution.map(data => [data, data]),
            country: solution_country.map(data => [data, data]),
            category: category.map(data => [data, data])
          };
          return RSVP.all([
            gadget.updateHeader({
              page_title: "Reference list",
              filter_action: true
            }),
            gadget.getDeclaredGadget("form_list")
          ]);
      })
      .push(function (result_list) {
        return result_list[1].render({
          erp5_document: {"_embedded": {"_view": {
            "listbox": {
              "column_list": [['title', 'References']],
              "show_anchor": 0,
              "default_params": {},
              "editable": 1,
              "editable_column_list": [],
              "key": "field_listbox",
              "lines": 20,
              "list_method": "portal_catalog",
              "query": 'urn:jio:allDocs?query=portal_type:"solution" AND has_reference: "true"',
              "portal_type": [],
              "search_column_list": [['modification_date', 'Updated Date']],
              "domain_root_list":  gadget.domain_root_list,
              "domain_dict": gadget.domain_dict,
              "sort_column_list": [['title', 'References']],
              "title": "References",
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