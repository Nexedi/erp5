/*globals window, RSVP, rJS*/
/*jslint indent: 2, nomen: true, maxlen: 180*/
(function (window, RSVP, rJS) {
  "use strict";
  rJS(window)
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
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
                field_gadget_param: {
                  css_class: "",
                  hidden: 0,
                  default: {
                    jio_key: value,
                    index: i,
                    query: 'urn:jio:allDocs?query=' + 'portal_type:' + '"publisher"'
                  },
                  editable: true,
                  key: 'provider_in_listbox',
                  url: "gadget_erp5_eci_provider_widget.html",
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
    }, {
      mutex: 'changestate'
    })
    .allowPublicAcquisition('getUrlParameter', function (argument_list) {
      return this.getUrlParameter(argument_list)
        .push(function (result) {
          if ((result === undefined) &&
            (argument_list[0] === 'field_listbox_sort_list:json')) {
            return [
              ['title', 'ascending']
            ];
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
              'selection_domain_type',
              'selection_domain_country',
              'selection_domain_category'
            ],
            query: 'portal_type:"publisher"'
          });
        })
        .push(function (result) {
          function getUniqueArray(data_list, property) {
            var value = data_list.map((obj) => obj.value[property])
              .reduce((cur, prev) => cur.concat(prev))
              .filter(Boolean);
            return Array.from(new Set(value)).sort();
          }

          var country = getUniqueArray(result.data.rows, 'selection_domain_country'),
            type = getUniqueArray(result.data.rows, 'selection_domain_type'),
            category = getUniqueArray(result.data.rows, 'selection_domain_category');


          gadget.domain_root_list = [
            ['type', 'Type'],
            ['country', 'Country'],
            ['category', 'Category']
          ];
          gadget.domain_dict = {
            type: type.map(data => [data, data]),
            country: country.map(data => [data, data]),
            category: category.map(data => [data, data])
          };
          return RSVP.all([
            gadget.updateHeader({
              page_title: "Provider List",
              filter_action: true
            }),
            gadget.getDeclaredGadget("form_list")
          ]);
        })
        .push(function(result_list) {
          var form_gadget = result_list[1];

          return form_gadget.render({
            erp5_document: {
              "_embedded": {
                "_view": {
                  "listbox": {
                    "column_list": [
                      ['title', 'Providers']
                    ],
                    "show_anchor": 0,
                    "default_params": {},
                    "editable": true,
                    "key": "field_listbox",
                    "lines": 20,
                    "list_method": "portal_catalog",
                    "query": 'urn:jio:allDocs?query=' + 'portal_type:' + '"publisher"',
                    "portal_type": [],
                    "search_column_list": [
                      ['modification_date', 'Updated Date'],
                      ['staff_quantity', 'Staff'],
                      ['price', 'Turnover']
                    ],
                    "sort_column_list": [],
                    "domain_root_list": gadget.domain_root_list,
                    "domain_dict": gadget.domain_dict,
                    "sort_on": ["title", "ascending"],
                    "title": "Providers",
                    "type": "ListBox"
                  }
                }
              },
              "_links": {
                "type": {
                  name: ""
                }
              }
            },
            form_definition: {
              group_list: [
                [
                  "bottom",
                  [
                    ["listbox"]
                  ]
                ],
                [
                  "hidden",
                  ["listbox_modification_date"]
                ]
              ]
            }
          });
        });
    });
}(window, RSVP, rJS));