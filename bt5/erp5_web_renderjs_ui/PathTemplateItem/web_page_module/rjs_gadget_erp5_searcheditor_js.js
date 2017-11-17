/*jslint indent: 2, maxerr: 3, maxlen: 100, nomen: true */
/*global window, document, rJS, RSVP, Handlebars,
  QueryFactory, SimpleQuery, ComplexQuery, Query, console*/
(function (window, document, rJS, RSVP, Handlebars,
  QueryFactory, SimpleQuery, ComplexQuery, Query, console) {
  "use strict";
  var gadget_klass = rJS(window),
    template_element = gadget_klass.__template_element,

    filter_item_template = Handlebars.compile(template_element
                         .getElementById("filter-item-template")
                         .innerHTML),
    filter_template = Handlebars.compile(template_element
                         .getElementById("filter-template")
                         .innerHTML),
    options_template = Handlebars.compile(template_element
                         .getElementById("options-template")
                         .innerHTML),
    NUMERIC = [
      ["Equals To", "="], ["Greater Than", ">"],
      ["Less Than", "<"], ["Not Greater Than", "<="],
      ["Not Less Than", ">="]
    ],
    OTHER = [
      ["Exact Match", "exacte_match"],
      ["keyword", "keyword"]
    ],
    DEFAULT = [["Contain", "Contain"]];

  Handlebars.registerHelper('equal', function (left_value, right_value, options) {
    if (arguments.length < 3) {
      throw new Error("Handlebars Helper equal needs 2 parameters");
    }
    if (left_value !== right_value) {
      return options.inverse(this);
    }
    return options.fn(this);
  });

  // XXX
  // define input's type according to column's value
  // the way to determiner is not generic
  function isNumericComparison(value) {
    return value.indexOf('date') !== -1 ||
      value.indexOf('quantity') !== -1 ||
      value.indexOf('price') !== -1;
  }

  function createOptionsTemplate(gadget, value) {
    var option = [],
      tmp,
      i;
    if (value !== "searchable_text") {
      if (isNumericComparison(value)) {
        tmp = NUMERIC;
      } else {
        tmp = OTHER;
      }
    } else {
      tmp = DEFAULT;
    }
    for (i = 0; i < tmp.length; i += 1) {
      option.push({
        text: tmp[i][0],
        value: tmp[i][1]
      });
    }
    return gadget.translateHtml(options_template({option: option}));
  }

  function createFilterItemTemplate(gadget, class_value, filter_item) {
    var column_list = gadget.state.search_column_list,
      option = [],
      tmp,
      operator_option = [],
      input_type = "search",
      i;

    if (filter_item) {
      if (isNumericComparison(filter_item.key)) {
        tmp = NUMERIC;
        if (filter_item.key.indexOf("date") !== -1) {
          input_type = "date";
        } else {
          input_type = "number";
        }
      } else {
        tmp = OTHER;
      }
    } else {
      tmp = DEFAULT;
      filter_item = {};
    }

    for (i = 0; i < tmp.length; i += 1) {
      operator_option.push({
        text: tmp[i][0],
        value: tmp[i][1],
        selected_option: filter_item.operator
      });
    }

    for (i = 0; i < column_list.length; i += 1) {
      option.push({
        text: column_list[i][1],
        value: column_list[i][0],
        selected_option: filter_item.key || "searchable_text"
      });
    }
    return gadget.translateHtml(filter_item_template({
      option: option,
      operator_option: operator_option,
      class_value: class_value,
      input_value: filter_item.value,
      input_type: input_type
    }));
  }

  gadget_klass
    //////////////////////////////////////////////
    // acquired method
    //////////////////////////////////////////////
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("trigger", "trigger")

    //////////////////////////////////////////////
    // initialize the gadget content
    //////////////////////////////////////////////
    .onStateChange(function () {
      var gadget = this,
        container = gadget.element.querySelector(".container"),
        div = document.createElement("div"),
        operator_select,
        filter_item_container,
        query_list = [],
        promise_list = [],
        i;

      return gadget.translateHtml(filter_template())
        .push(function (translated_html) {
          div.innerHTML = translated_html;

          operator_select = div.querySelector("select");
          filter_item_container = div.querySelector(".filter_item_container");

          if (gadget.state.extended_search) {
            // string to query
            try {
              query_list = QueryFactory.create(gadget.state.extended_search);
            } catch (error) {
              // XXX hack to not crash interface
              // it catch all error, not only search criteria invalid error
              console.warn(error);
              return [];
            }
            if (query_list.operator === "OR") {
              operator_select.querySelectorAll("option")[1].selected = "selected";
            }

            query_list = query_list.query_list || [query_list];
            for (i = 0; i < query_list.length; i += 1) {
              promise_list.push(createFilterItemTemplate(gadget, "auto", query_list[i]));
            }
          } else if (gadget.state.search_column_list.length > 0) {
            // No search query was provided
            // Add an empty search parameter for the first searchable column
            promise_list.push(
              createFilterItemTemplate(
                gadget,
                "auto",
                new SimpleQuery({
                  key: gadget.state.search_column_list[0][1],
                  operator: "",
                  type: "simple",
                  value: ''
                })
              )
            );
          }
          return RSVP.all(promise_list);
        })
        .push(function (result_list) {
          var subdiv;
          for (i = 0; i < result_list.length; i += 1) {
            subdiv = document.createElement("div");
            subdiv.innerHTML = result_list[i];
            filter_item_container.appendChild(subdiv);
          }

          while (container.firstChild) {
            container.removeChild(container.firstChild);
          }

          container.appendChild(div);
          return gadget.focusOnLastInput();
        });
    })

    .declareJob('focusOnLastInput', function () {
      var input_list = this.element.querySelectorAll('input');
      if (input_list.length) {
        input_list[input_list.length - 1].focus();
      }
    })

    .declareMethod('render', function (options) {
      return this.changeState({
        search_column_list: options.search_column_list,
        begin_from: options.begin_from,
        extended_search: options.extended_search
      });
    })

    .onEvent('submit', function () {
      var i,
        gadget = this,
        simple_operator,
        query,
        key,
        select_list,
        simple_query_list = [],
        complex_query,
        select,
        value,
        options = {},
        filter_item_list = gadget.element.querySelectorAll(".filter_item"),
        operator_select = gadget.element.querySelector("select"),
        operator = operator_select[operator_select.selectedIndex].value;
      for (i = 0; i < filter_item_list.length; i += 1) {
        select_list = filter_item_list[i].querySelectorAll("select");
        value = filter_item_list[i].querySelector("input").value;
        simple_operator = "";
        select = select_list[1][select_list[1].selectedIndex].value;
        if (select === "keyword") {
          value = "%" + value + "%";
        } else if (["", ">", "<", "<=", ">="].indexOf(select) !== -1) {
          simple_operator = select;
        }

        if (select_list[0][select_list[0].selectedIndex].value === "searchable_text") {
          key = "";
        } else {
          key = select_list[0][select_list[0].selectedIndex].value;
        }

        simple_query_list.push(new SimpleQuery(
          {
            key: key,
            operator: simple_operator,
            type: "simple",
            value: value
          }
        ));
      }

      if (simple_query_list.length > 0) {
        complex_query = new ComplexQuery({
          operator: operator,
          query_list: simple_query_list,
          type: "complex"
        });
        //query to string
        query = Query.objectToSearchText(complex_query);
      } else {
        query = "";
      }
      options.extended_search = query;
      options[gadget.state.begin_from] = undefined;
      return gadget.redirect({
        command: 'store_and_change',
        options : options
      });

    })

    .onEvent('click', function (evt) {
      var gadget = this;

      if (evt.target.classList.contains('close')) {
        evt.preventDefault();
        return this.trigger();
      }

      if (evt.target.classList.contains('plus')) {
        evt.preventDefault();
        return createFilterItemTemplate(gadget, 'auto')
          .push(function (template) {
            var tmp = document.createElement("div"),
              container = gadget.element.querySelector(".filter_item_container");
            tmp.innerHTML = template;
            container.appendChild(tmp);
          });
      }

      if (evt.target.classList.contains('ui-icon-minus')) {
        evt.preventDefault();
        evt.target.parentElement.parentElement.removeChild(evt.target.parentElement);
      }
    }, false, false)

    .onEvent('change', function (evt) {
      var gadget = this;
      if (evt.target.classList.contains('column')) {
        evt.preventDefault();
        return createOptionsTemplate(gadget, evt.target.value)
          .push(function (innerHTML) {
            evt.target.parentElement.querySelectorAll('select')[1].innerHTML = innerHTML;
            if (isNumericComparison(evt.target.value)) {
              if (evt.target.value.indexOf("date") !== -1) {
                evt.target.parentElement.querySelector('input').setAttribute("type", "date");
              } else {
                evt.target.parentElement.querySelector('input').setAttribute("type", "number");
              }
            } else {
              evt.target.parentElement.querySelector('input').setAttribute("type", "text");
            }
          });
      }
    }, false, false);

}(window, document, rJS, RSVP, Handlebars,
  QueryFactory, SimpleQuery, ComplexQuery, Query, console));