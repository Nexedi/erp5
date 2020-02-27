/*jslint indent: 2, maxerr: 3, maxlen: 100, nomen: true */
/*global window, document, rJS, domsugar,
  QueryFactory, SimpleQuery, ComplexQuery, Query*/
(function (window, document, rJS, domsugar,
  QueryFactory, SimpleQuery, ComplexQuery, Query) {
  "use strict";
  var NUMERIC = [
      ["Equal to", "="], ["Greater than", ">"],
      ["Less than", "<"], ["Less than or Equal to", "<="],
      ["Greater than or Equal to", ">="]
    ],
    OTHER = [
      ["Equal to", "exact_match"],
      ["Equal to (at least one)", "at_least_one_exact_match"],
      ["Contains", "keyword"]
    ],
    DOMAIN = [
      ["Equal to", "exact_match"]
    ],
    DEFAULT = [["Contains", "contain"]],
    PREFIX_COLUMN = 'COLUMN_',
    PREFIX_RAW = 'RAW',
    PREFIX_DOMAIN = 'DOMAIN_',
    PREFIX_TEXT = 'TEXT';

  // XXX
  // define input's type according to column's value
  // the way to determiner is not generic
  function isNumericComparison(value) {
    return value.indexOf('date') !== -1 ||
      value.indexOf('quantity') !== -1 ||
      value.indexOf('price') !== -1;
  }
  function getComparisonOptionList(value) {
    if (value.indexOf(PREFIX_COLUMN) === 0) {
      if (isNumericComparison(value)) {
        return NUMERIC;
      }
      return OTHER;
    }
    if (value.indexOf(PREFIX_DOMAIN) === 0) {
      return DOMAIN;
    }
    return DEFAULT;
  }

  function makeFilterItemInput(param) {
    var input = document.createElement("input");
    input.type = param.type;
    input.value = param.value;
    return input;
  }
  function appendInputToFilterItem(item_element) {
    item_element.appendChild(makeFilterItemInput({
      type: "search",
      value: ""
    }));
  }
  function getFilterItemElementFromEvent(event, gadget_element) {
    var element = event.target;
    while (!element.classList.contains("filter_item")) {
      element = element.parentElement;
      if (!element || element === gadget_element) { return null; }
    }
    return element;
  }

  function updateFilterDOM(gadget) {
    var item_list = gadget.element.querySelectorAll(".filter_item"),
      input_list = null,
      i = 0,
      j = 0;
    for (i = 0; i < item_list.length; i += 1) {
      if ("at_least_one_exact_match" ===
          item_list[i].querySelectorAll("select")[1].value) {
        // remove empty inputs except last one and focused one
        input_list = item_list[i].querySelectorAll("input");
        for (j = input_list.length - 2; j >= 0; j -= 1) {
          if (!input_list[j].value &&
              input_list[j] !== document.activeElement) {
            input_list[j].remove();
          }
        }
        // remove last input if the one before the last is empty
        input_list = item_list[i].querySelectorAll("input");
        if (input_list.length >= 2 &&
            !input_list[input_list.length - 1].value &&
            !input_list[input_list.length - 2].value) {
          input_list[input_list.length - 1].remove();
        }
        // append input if last one is not empty
        input_list = item_list[i].querySelectorAll("input");
        if (input_list[input_list.length - 1].value) {
          appendInputToFilterItem(item_list[i]);
        }
        // put field required if there is no filled input
        input_list = item_list[i].querySelectorAll("input");
        if (input_list.length === 1) {
          input_list[0].required = true;
        }
      } else {
        // keep first input only
        input_list = item_list[i].querySelectorAll("input");
        for (j = input_list.length - 1; j > 0; j -= 1) {
          input_list[j].remove();
        }
      }
    }
  }

  function detectAtleastoneexactmatchComplexQuery(query) {
    var i = 0, key = "", operator = "", difference_count = 0, value_list = [];
    if (query.type !== "complex" || query.operator !== "OR") { return null; }
    for (i = 0; i < query.query_list.length; i += 1) {
      if (difference_count === 1) {
        if (key      !== (query.query_list[i].key      || "") ||
            operator !== (query.query_list[i].operator || "")) {
          return null;
        }
      } else if (difference_count === 0) {
        key = query.query_list[i].key || "";
        operator = query.query_list[i].operator || "";
        difference_count = 1;
      }
    }
    return {key: key, operator: operator, value_list: value_list};
  }

  function generateFilterItemTemplate(options) {
    var column_option_list = options.option.map(function (option) {
      return domsugar('option', {
        selected: !!option.selected,
        value: option.value,
        text: option.text
      });
    }),
      operator_option_list = options.operator_option.map(function (option) {
        return domsugar('option', {
          selected: !!option.selected,
          value: option.value,
          text: option.text
        });
      }),
      div_dom_list = [
        domsugar('select', {class: 'column'}, column_option_list),
        domsugar('select', operator_option_list)
      ];

    if (options.domain_option) {
      div_dom_list.push(domsugar(
        'select',
        {required: true},
        options.domain_option.map(function (option) {
          return domsugar('option', {
            selected: !!option.selected,
            value: option.value || undefined,
            text: option.text
          });
        })
      ));

    } else if (options.input_list) {
      div_dom_list.push.apply(div_dom_list, options.input_list.map(function (option) {
        return domsugar('input', {
          required: !!option.required,
          value: option.value,
          type: option.type
        });
      }));

    } else {
      div_dom_list.push(domsugar('input', {
        type: options.input_type,
        value: options.input_value,
        required: true
      }));
    }

    return domsugar('div', [
      domsugar('button', {class: 'ui-icon ui-icon-minus'}),
      domsugar('div', {class: 'filter_item'}, div_dom_list)
    ]);
  }

  function createFilterItemTemplate(gadget, query_dict, translation_dict, column_translation_dict) {
    var operator_default_list = DEFAULT,
      operator_option_list = [],
      column_option_list = [],
      input_list = [],
      input_type = "search",
      i,
      is_selected,
      query_detail_dict,
      domain_list,
      domain_option_list;

    query_detail_dict = detectAtleastoneexactmatchComplexQuery(query_dict);
    if (query_detail_dict) {
      operator_default_list = getComparisonOptionList(query_detail_dict.key);
      if (operator_default_list !== OTHER) {
        query_dict = query_dict.query_list[0] || {
          type: "simple",
          key: query_detail_dict.key,
          value: query_detail_dict.value_list[0] || ""
        };
        query_detail_dict = null;
      }
    } else {
      operator_default_list = getComparisonOptionList(query_dict.key);
    }
    if (query_detail_dict) {

      is_selected = false;
      for (i = 0; i < gadget.state.search_column_list.length; i += 1) {
        is_selected = is_selected ||
          (query_detail_dict.key === gadget.state.search_column_list[i][0]);
        column_option_list.push({
          text: column_translation_dict[gadget.state.search_column_list[i][1]] ||
                gadget.state.search_column_list[i][1],
          value: gadget.state.search_column_list[i][0],
          selected: (query_detail_dict.key === gadget.state.search_column_list[i][0])
        });
      }
      if (!is_selected) {
        throw new Error('SearchEditor: no key found for: ' + query_detail_dict.key);
      }
      is_selected = false;
      for (i = 0; i < operator_default_list.length; i += 1) {
        is_selected = is_selected ||
          ("at_least_one_exact_match" === operator_default_list[i][1]);
        operator_option_list.push({
          text: translation_dict[operator_default_list[i][0]],
          value: operator_default_list[i][1],
          selected: ("at_least_one_exact_match" === operator_default_list[i][1])
        });
      }
      if (!is_selected) {
        throw new Error('SearchEditor: no operator found for: at_least_one_exact_match');
      }

      for (i = 0; i < query_dict.query_list.length; i += 1) {
        input_list.push({
          type: "search",
          value: query_dict.query_list[i].value,
          required: ""
        });
      }
      input_list.push({
        type: "search",
        value: "",
        required: ""
      });
      return generateFilterItemTemplate({
        option: column_option_list,
        operator_option: operator_option_list,
        input_list: input_list,
        domain_option: domain_option_list
      });
    }


    if (operator_default_list === NUMERIC) {
      if (query_dict.key.indexOf("date") !== -1) {
        input_type = "date";
      } else {
        input_type = "number";
      }
    } else if (operator_default_list === DOMAIN) {
      is_selected = false;
      input_type = "select";
      domain_option_list = [];
      domain_list = gadget.state.domain_dict[query_dict.key.slice(PREFIX_DOMAIN.length)];
      for (i = 0; i < domain_list.length; i += 1) {
        domain_option_list.push({
          text: domain_list[i][0],
          value: domain_list[i][1],
          selected: (query_dict.value === domain_list[i][1])
        });
        is_selected = is_selected || (query_dict.value === domain_list[i][1]);
      }
      if (!is_selected) {
        domain_option_list.push({
          text: '??? ' + query_dict.value,
          value: query_dict.value,
          selected: true
        });
      }
    }

    if (!query_dict.operator) {
      // Set the default operator depending of the type of the column
      query_dict.operator = operator_default_list[0][1];
    }
    is_selected = false;
    for (i = 0; i < operator_default_list.length; i += 1) {
      is_selected = is_selected || (query_dict.operator === operator_default_list[i][1]);
      operator_option_list.push({
        text: translation_dict[operator_default_list[i][0]],
        value: operator_default_list[i][1],
        selected: (query_dict.operator === operator_default_list[i][1])
      });
    }
    if (!is_selected) {
      // Do not lose the query operator even if it is not handled by the UI
      // Do not try to change it to another value, as it means losing user data
      if (query_dict.key.indexOf(PREFIX_COLUMN) === 0) {
        query_dict.key = query_dict.key.slice(PREFIX_COLUMN.length);
      } else if (query_dict.key.indexOf(PREFIX_DOMAIN) === 0) {
        query_dict.key = query_dict.key.slice(PREFIX_DOMAIN.length);
      } else {
        query_dict.key = '';
      }
      query_dict.value = Query.objectToSearchText(new SimpleQuery({
        key: query_dict.key,
        operator: query_dict.operator,
        type: "simple",
        value: query_dict.value
      }));
      query_dict.operator = DEFAULT[0][1];
      query_dict.key = PREFIX_RAW;
      operator_option_list = [{
        text: translation_dict[DEFAULT[0][0]],
        value: DEFAULT[0][1],
        selected: true
      }];
    }

    is_selected = false;
    for (i = 0; i < gadget.state.search_column_list.length; i += 1) {
      is_selected = is_selected || (query_dict.key === gadget.state.search_column_list[i][0]);
      column_option_list.push({
        text: column_translation_dict[gadget.state.search_column_list[i][1]] ||
              gadget.state.search_column_list[i][1],
        value: gadget.state.search_column_list[i][0],
        selected: (query_dict.key === gadget.state.search_column_list[i][0])
      });
    }
    if (!is_selected) {
      throw new Error('SearchEditor: no key found for: ' + query_dict.key);
    }

    return generateFilterItemTemplate({
      option: column_option_list,
      operator_option: operator_option_list,
      input_value: query_dict.value,
      input_type: input_type,
      domain_option: domain_option_list
    });
  }

  function getValueListFromElementList(element_list) {
    var i = 0, value_list = [];
    for (i = 0; i < element_list.length; i += 1) {
      if (element_list[i].value) {
        value_list.push(element_list[i].value);
      }
    }
    return value_list;
  }

  function makeComplexQueryFromValueList(key, value_list, operator, logical_operator) {
    var query_list = [],
      complex = {type: "complex", operator: logical_operator, query_list: query_list},
      i = 0;
    for (i = 0; i < value_list.length; i += 1) {
      query_list.push({
        type: "simple",
        key: key,
        operator: operator,
        value: value_list[i]
      });
    }
    return complex;
  }

  function getQueryStateFromDOM(gadget) {
    var operator_select = gadget.element.querySelector("select"),
      state = {
        query_list: [],
        operator: operator_select[operator_select.selectedIndex].value
      },
      i,
      filter_item_list = gadget.element.querySelectorAll(".filter_item"),
      select_list,
      key,
      operator,
      value;

    for (i = 0; i < filter_item_list.length; i += 1) {
      select_list = filter_item_list[i].querySelectorAll("select");
      key = select_list[0][select_list[0].selectedIndex].value;
      operator = select_list[1][select_list[1].selectedIndex].value;
      if (select_list.length === 3) {
        value = select_list[2][select_list[2].selectedIndex].value;
      } else {
        if (operator === "at_least_one_exact_match") {
          value = getValueListFromElementList(
            filter_item_list[i].querySelectorAll("input")
          );
          if (value.length > 1) {
            state.query_list.push(makeComplexQueryFromValueList(key, value, "", "OR"));
            /*jslint continue: true */
            continue;
          }
          /*jslint continue: false */
        }
        value = filter_item_list[i].querySelector("input").value;
      }
      state.query_list.push({
        type: "simple",
        value: value,
        operator: operator,
        key: key
      });
    }

    return state;
  }

  function queryRemovePrefixInDeep(query) {
    var i = 0;
    if (query.type === "simple") {
      if (query.key.indexOf(PREFIX_COLUMN) === 0) {
        query.key = query.key.slice(PREFIX_COLUMN.length);
      } else if (query.key.indexOf(PREFIX_DOMAIN) === 0) {
        query.key = query.key.slice(PREFIX_DOMAIN.length);
      } else {
        query.key = '';
      }
    } else {
      for (i = 0; i < query.query_list.length; i += 1) {
        queryRemovePrefixInDeep(query.query_list[i]);
      }
    }
  }

  function querySetKeyInDeep(query, key) {
    var i = 0;
    if (query.type === "complex") {
      for (i = 0; i < query.query_list.length; i += 1) {
        querySetKeyInDeep(query.query_list[i], key);
      }
    } else {
      query.key = key;
    }
  }

  function getElementIndex(node) {
    var index = -1;
    while (node) {
      node = node.previousElementSibling;
      index += 1;
    }
    return index;
  }

  rJS(window)
    //////////////////////////////////////////////
    // acquired method
    //////////////////////////////////////////////
    .declareAcquiredMethod("getTranslationList", "getTranslationList")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("trigger", "trigger")

    //////////////////////////////////////////////
    // initialize the gadget content
    //////////////////////////////////////////////
    .declareMethod('render', function render(options) {
      var operator = 'AND',
        query_list = [],
        i,
        jio_query,
        len,
        sub_jio_query,
        sub_jio_query_dict,
        sub_jio_query_detail_dict,
        search_column_list = [],
        search_column_dict = {},
        search_domain_dict = {},
        additional_search_column_list = [],
        additional_search_column_dict = {};

      function addAdditionalSearchColumn(key, prefixed_key, title) {
        if (additional_search_column_dict.hasOwnProperty(key)) { return false; }
        additional_search_column_dict[key] = true;
        additional_search_column_list.push([prefixed_key, title]);
        return true;
      }

      len = options.search_column_list.length;
      for (i = 0; i < len; i += 1) {
        search_column_dict[options.search_column_list[i][0]] = true;
        search_column_list.push([
          PREFIX_COLUMN + options.search_column_list[i][0],
          options.search_column_list[i][1]
        ]);
      }

      len = options.domain_list ? options.domain_list.length : 0;
      for (i = 0; i < len; i += 1) {
        search_domain_dict[options.domain_list[i][0]] = true;
        search_column_list.push([
          PREFIX_DOMAIN + options.domain_list[i][0],
          options.domain_list[i][1]
        ]);
      }
      // Translated later
      search_column_list.push([PREFIX_TEXT, "Searchable Text"]);
      search_column_list.push([PREFIX_RAW, "Search Expression"]);

      // When the raw query is modified, reset the full gadget
      if (options.extended_search) {
        // Parse the raw query
        try {
          jio_query = QueryFactory.create(options.extended_search);
        } catch (error) {
          // it catch all error, not only search criteria invalid error
          query_list.push({
            key: PREFIX_RAW,
            value: options.extended_search
          });
        }

        if (jio_query instanceof SimpleQuery) {
          if (jio_query.key) {
            if (search_column_dict.hasOwnProperty(jio_query.key)) {
              query_list.push({
                key: PREFIX_COLUMN + jio_query.key,
                value: jio_query.value,
                operator: jio_query.operator
              });
            } else if (search_domain_dict.hasOwnProperty(jio_query.key)) {
              query_list.push({
                key: PREFIX_DOMAIN + jio_query.key,
                value: jio_query.value,
                operator: jio_query.operator
              });
            } else {
              addAdditionalSearchColumn(
                jio_query.key,
                PREFIX_COLUMN + jio_query.key,
                jio_query.key
              );
              query_list.push({
                key: PREFIX_COLUMN + jio_query.key,
                value: jio_query.value,
                operator: jio_query.operator
              });
            }
          } else {
            query_list.push({
              key: PREFIX_TEXT,
              value: jio_query.value
            });
          }

        } else if (jio_query instanceof ComplexQuery) {
          operator = jio_query.operator;
          sub_jio_query_dict = jio_query.toJSON();
          sub_jio_query_detail_dict =
            detectAtleastoneexactmatchComplexQuery(sub_jio_query_dict);
          if (sub_jio_query_detail_dict &&
              search_column_dict.hasOwnProperty(sub_jio_query_detail_dict.key)) {
            querySetKeyInDeep(sub_jio_query_dict, PREFIX_COLUMN + sub_jio_query_detail_dict.key);
            query_list.push(sub_jio_query_dict);
            operator = "AND";
            jio_query = {query_list: []};  // This line acts like a "go to end of this function"
          }

          len = jio_query.query_list.length;
          for (i = 0; i < len; i += 1) {
            sub_jio_query = jio_query.query_list[i];
            if (sub_jio_query instanceof SimpleQuery) {
              if (sub_jio_query.key) {
                if (search_column_dict.hasOwnProperty(sub_jio_query.key)) {
                  query_list.push({
                    key: PREFIX_COLUMN + sub_jio_query.key,
                    value: sub_jio_query.value,
                    operator: sub_jio_query.operator
                  });
                } else if (search_domain_dict.hasOwnProperty(sub_jio_query.key)) {
                  query_list.push({
                    key: PREFIX_DOMAIN + sub_jio_query.key,
                    value: sub_jio_query.value,
                    operator: sub_jio_query.operator
                  });
                } else {
                  addAdditionalSearchColumn(
                    sub_jio_query.key,
                    PREFIX_COLUMN + sub_jio_query.key,
                    sub_jio_query.key
                  );
                  query_list.push({
                    key: PREFIX_COLUMN + sub_jio_query.key,
                    value: sub_jio_query.value,
                    operator: sub_jio_query.operator
                  });
                }
              } else {
                query_list.push({
                  key: PREFIX_TEXT,
                  value: sub_jio_query.value
                });
              }
            } else {
              sub_jio_query_dict = sub_jio_query.toJSON();
              sub_jio_query_detail_dict =
                detectAtleastoneexactmatchComplexQuery(sub_jio_query_dict);
              if (sub_jio_query_detail_dict) {
                addAdditionalSearchColumn(
                  sub_jio_query_detail_dict.key,
                  PREFIX_COLUMN + sub_jio_query_detail_dict.key,
                  sub_jio_query_detail_dict.key
                );
                querySetKeyInDeep(
                  sub_jio_query_dict,
                  PREFIX_COLUMN + sub_jio_query_detail_dict.key
                );
                query_list.push(sub_jio_query_dict);
              } else {
                query_list.push({
                  key: PREFIX_RAW,
                  value: Query.objectToSearchText(sub_jio_query)
                });
              }
            }
          }
        }
      } else {
        query_list.push({
          key: search_column_list[0][0],
          value: ''
        });
      }

      return this.changeState({
        search_column_list: search_column_list.concat(additional_search_column_list),
        additional_search_column_list: additional_search_column_list,
        begin_from_key: options.begin_from,
        // [{key: 'title', value: 'Foo', operator: 'like'}]
        query_list: query_list,
        domain_dict: options.domain_dict,
        // and/or
        operator: operator,
        focus_on: options.focus_on,
        update_filter_dom: 0
      });
    })

    .onStateChange(function onStateChange(modification_dict) {
      var gadget = this;

      if (modification_dict.update_filter_dom !== undefined &&
          Object.keys(modification_dict).length === 1) {
        updateFilterDOM(this);
        return;
      }

      return gadget.getTranslationList([
        'Submit',
        'Filter Editor',
        'Close',
        'Add Criteria',
        'Reset',
        'All criterions (AND)',
        'At least one (OR)',
        'Contains',
        'Equal to',
        'Equal to (at least one)',
        'Greater than',
        'Less than',
        'Less than or Equal to',
        'Greater than or Equal to',
        'Searchable Text',
        'Search Expression'
      ])
        .push(function (translation_list) {
          var filter_dom_list =
              gadget.state.query_list.map(
                function (query) {
                  return createFilterItemTemplate(
                    gadget,
                    query,
                    {
                      'Contains': translation_list[7],
                      'Equal to': translation_list[8],
                      'Equal to (at least one)': translation_list[9],
                      'Greater than': translation_list[10],
                      'Less than': translation_list[11],
                      'Less than or Equal to': translation_list[12],
                      'Greater than or Equal to': translation_list[13]
                    },
                    {
                      'Searchable Text': translation_list[14],
                      'Search Expression': translation_list[15]
                    }
                  );
                }
              );

          domsugar(gadget.element.querySelector(".container"), [
            domsugar('div', [
              domsugar('div', {'data-role': 'header', 'class': 'ui-header'}, [
                domsugar('div', {class: 'ui-btn-right'}, [
                  domsugar('div', {class: 'ui-controlgroup-controls'}, [
                    domsugar('button', {
                      type: 'submit',
                      class: 'ui-btn-icon-left ui-icon-check',
                      text: translation_list[0]
                    })
                  ])
                ]),
                domsugar('h1', {text: translation_list[1]}),
                domsugar('div', {class: 'ui-btn-left'}, [
                  domsugar('div', {class: 'ui-controlgroup-controls'}, [
                    domsugar('button', {
                      type: 'submit',
                      class: 'close ui-btn-icon-left ui-icon-times',
                      text: translation_list[2]
                    })
                  ])
                ])
              ]),
              domsugar('section', [
                domsugar('fieldset', [
                  domsugar('select', {name: 'heard_about'}, [
                    domsugar('option', {
                      value: 'AND',
                      text: translation_list[5],
                      selected: (gadget.state.operator === "AND")
                    }),
                    domsugar('option', {
                      value: 'OR',
                      text: translation_list[6],
                      selected: (gadget.state.operator === "OR")
                    })
                  ])
                ]),
                domsugar('div', {class: 'filter_item_container'},
                         filter_dom_list),
                domsugar('button', {
                  class: 'plus ui-icon-plus ui-btn-icon-left',
                  text: translation_list[3]
                }),
                domsugar('button', {
                  class: 'trash ui-icon-trash-o ui-btn-icon-left',
                  text: translation_list[4]
                })
                // domsugar('div', {class: 'domain_item_container'},
                //          domain_dom_list),
              ])
            ])
          ]);
          return gadget.focusOnLastInput(gadget.state.focus_on);
        });
    })

    .declareJob('updateFilterDOM', function updateFilterDOM() {
      return this.changeState({update_filter_dom: this.state.update_filter_dom + 1});
    })

    .declareJob('focusOnLastInput', function focusOnLastInput(index) {
      var input_list = this.element.querySelectorAll('input');
      if (index === undefined) {
        index = input_list.length - 1;
      }
      if (input_list.length) {
        input_list[index].focus();
      }
    })

    .onEvent('submit', function submit() {
      var new_state = getQueryStateFromDOM(this),
        operator = new_state.operator,
        query_list = new_state.query_list,
        query,
        len = query_list.length,
        i,
        jio_query_list = [],
        options = {};

      for (i = 0; i < len; i += 1) {
        query = query_list[i];
        if (query.type === "complex") {
          queryRemovePrefixInDeep(query);
          jio_query_list.push(new ComplexQuery(query));
        } else {
          if (query.operator === 'keyword') {
            query.value = '%' + query.value + '%';
            query.operator = '';
          } else if (["", ">", "<", "<=", ">="].indexOf(query.operator) === -1) {
            query.operator = '';
          }

          if (query.key === PREFIX_RAW) {
            try {
              jio_query_list.push(QueryFactory.create(query.value));
            } catch (ignore) {
              // If the value can not be parsed by jio, drop it
            }
          } else {
            queryRemovePrefixInDeep(query);

            jio_query_list.push(new SimpleQuery({
              key: query.key,
              operator: query.operator,
              type: "simple",
              value: query.value
            }));

          }
        }
      }

      if (jio_query_list.length > 0) {
        options.extended_search = Query.objectToSearchText(new ComplexQuery({
          operator: operator,
          query_list: jio_query_list,
          type: "complex"
        }));
      } else {
        options.extended_search = '';
      }
      options[this.state.begin_from_key] = undefined;
      return this.redirect({
        command: 'store_and_change',
        options : options
      }, true);

    })

    .onEvent('click', function click(evt) {
      var new_state;

      if (evt.target.classList.contains('trash')) {
        evt.preventDefault();
        new_state = getQueryStateFromDOM(this);
        new_state.query_list = [];
        return this.changeState(new_state);
      }

      if (evt.target.classList.contains('close')) {
        evt.preventDefault();
        return this.trigger();
      }

      if (evt.target.classList.contains('plus')) {
        evt.preventDefault();
        new_state = getQueryStateFromDOM(this);
        // XXX Duplicated code
        // XXX XXX Should select the first column which doesn't have a value
        new_state.query_list.push({
          key: this.state.search_column_list[0][0],
          value: ''
          // operator: 'exact_match'
        });
        return this.changeState(new_state);
      }

      if (evt.target.classList.contains('ui-icon-minus')) {
        evt.preventDefault();
        evt.target.parentElement.parentElement.removeChild(evt.target.parentElement);
      }
    }, false, false)

    .onEvent('input', function input(evt) {
      var filter_item_element = getFilterItemElementFromEvent(evt, this.element);
      if (filter_item_element) {
        if (filter_item_element.querySelectorAll("select")[1].value ===
              "at_least_one_exact_match") {
          // This "if" exists only for performance reason,
          // in order to run updateFilterDOM only if necessary.
          this.updateFilterDOM();
        }
      }
    }, false, false)

    .onEvent('change', function change(evt) {
      this.updateFilterDOM();
      if (evt.target.classList.contains('column')) {
        // Reset the operator when user change the column/key
        evt.preventDefault();
        var new_state = getQueryStateFromDOM(this),
          index = getElementIndex(evt.target.parentElement.parentElement);
        if (new_state.query_list[index].type !== "complex") {
          delete new_state.query_list[index].operator;
        }
        return this.changeState(new_state);
      }
    }, false, false);

}(window, document, rJS, domsugar,
  QueryFactory, SimpleQuery, ComplexQuery, Query));