/*jslint indent: 2, maxerr: 3, maxlen: 100, nomen: true */
/*global window, document, rJS, RSVP, Handlebars, $, loopEventListener,
  QueryFactory, SimpleQuery, ComplexQuery, Query, console*/
(function (window, document, rJS, RSVP, Handlebars, $, loopEventListener,
  QueryFactory, SimpleQuery, ComplexQuery, Query, console) {
  "use strict";
  var gadget_klass = rJS(window),
    filter_item_source = gadget_klass.__template_element
                         .getElementById("filter-item-template")
                         .innerHTML,
    filter_item_template = Handlebars.compile(filter_item_source),
    filter_source = gadget_klass.__template_element
                         .getElementById("filter-template")
                         .innerHTML,
    filter_template = Handlebars.compile(filter_source),

    options_source = gadget_klass.__template_element
                         .getElementById("options-template")
                         .innerHTML,
    options_template = Handlebars.compile(options_source);

  Handlebars.registerHelper('equal', function (left_value,
    right_value, options) {
    if (arguments.length < 3) {
      throw new Error("Handlebars Helper equal needs 2 parameters");
    }
    if (left_value !== right_value) {
      return options.inverse(this);
    }
    return options.fn(this);
  });

  //XXXXX
  //define input's type according to column's value
  //the way to determiner is not generic
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
        tmp = gadget.props.numeric;
      } else {
        tmp = gadget.props.other;
      }
    } else {
      tmp = gadget.props.default;
    }
    for (i = 0; i < tmp.length; i += 1) {
      option.push({
        "text": tmp[i][0],
        "value": tmp[i][1]
      });
    }
    return gadget.translateHtml(options_template({option: option}));
  }




  function createFilterItemTemplate(gadget, class_value, filter_item) {
    var column_list = gadget.props.search_column_list,
      option = [],
      tmp,
      operator_option = [],
      input_type = "text",
      i;

    if (filter_item) {
      if (isNumericComparison(filter_item.key)) {
        tmp = gadget.props.numeric;
        if (filter_item.key.indexOf("date") !== -1) {
          input_type = "date";
        } else {
          input_type = "number";
        }
      } else {
        tmp = gadget.props.other;
      }
    } else {
      tmp = gadget.props.default;
      filter_item = {};
    }

    for (i = 0; i < tmp.length; i += 1) {
      operator_option.push({
        "text": tmp[i][0],
        "value": tmp[i][1],
        "selected_option": filter_item.operator
      });
    }

    for (i = 0; i < column_list.length; i += 1) {
      option.push({
        "text": column_list[i][1],
        "value": column_list[i][0],
        "selected_option": filter_item.key || "searchable_text"
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


  function listenToSelect(gadget, class_value) {
    var list = [],
      i,
      filter_item_list =
        gadget.props.element.querySelectorAll("." + class_value);
    function createFunction(i) {
      var select_list = filter_item_list[i].querySelectorAll("select"),
        input = filter_item_list[i].querySelector("input");
      return loopEventListener(
        select_list[0],
        "change",
        false,
        function (event) {
          return new RSVP.Queue()
            .push(function () {
              return createOptionsTemplate(gadget, event.target.value);
            })
            .push(function (innerHTML) {
              select_list[1].innerHTML = innerHTML;
              $(select_list[1]).selectmenu('refresh');
              if (isNumericComparison(event.target.value)) {
                if (event.target.value.indexOf("date") !== -1) {
                  input.setAttribute("type", "date");
                } else {
                  input.setAttribute("type", "number");
                }
              } else {
                input.setAttribute("type", "text");
              }
            });
        }
      );
    }
    for (i = 0; i < filter_item_list.length; i += 1) {
      list.push(createFunction(i));
    }
    return RSVP.all(list);
  }




  rJS(window)
    /////////////////////////////////////////////////////////////////
    // ready
    /////////////////////////////////////////////////////////////////
    // Init local properties
    .ready(function (g) {
      g.props = {};
    })
    .ready(function (g) {
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
          g.props.numeric = [["Equals To", "="], ["Greater Than", ">"],
            ["Less Than", "<"], ["Not Greater Than", "<="],
            ["Not Less Than", ">="]];
          g.props.other = [["Exact Match", "exacte_match"],
            ["keyword", "keyword"]];
          g.props.default = [["Contain", "Contain"]];
        });
    })



    //////////////////////////////////////////////
    // acquired method
    //////////////////////////////////////////////
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("trigger", "trigger")
    //////////////////////////////////////////////
    // initialize the gadget content
    //////////////////////////////////////////////
    .declareMethod('render', function (options) {
      var gadget = this;
      gadget.props.search_column_list = options.search_column_list;
      gadget.props.begin_from = options.begin_from;

      gadget.props.extended_search = options.extended_search;

      return new RSVP.Queue()
        .push(function () {
          var tmp = filter_template();
          return gadget.translateHtml(tmp);
        })
        .push(function (translated_html) {
          var tmp = document.createElement("div");
          tmp.innerHTML = translated_html;
          gadget.props.element.querySelector(".container").appendChild(tmp);
        });
    })
    //////////////////////////////////////////////
    .declareService(function () {
      var gadget = this,
        i,
        list = [],
        or = gadget.props.element.querySelector(".or"),
        and = gadget.props.element.querySelector(".and"),
        container = gadget.props.element.querySelector(".filter_item_container"),
        query_list;
      if (gadget.props.extended_search) {
        //string to query
        try {
          query_list = QueryFactory.create(gadget.props.extended_search);
        } catch (error) {
          //XXXX hack to not crash interface
          //it catch all error, not only search criteria invalid error
          console.warn(error);
          return;
        }
        if (query_list.operator === "OR") {
          or.checked = true;
          and.checked = false;
          or.parentElement.children[0].setAttribute("class",
            "ui-btn ui-corner-all ui-btn-inherit ui-btn-icon-left ui-radio-on");
          and.parentElement.children[0].setAttribute("class",
            "ui-btn ui-corner-all ui-btn-inherit ui-btn-icon-left ui-radio-off");
        }

        query_list = query_list.query_list || [query_list];
        for (i = 0; i < query_list.length; i += 1) {
          list.push(createFilterItemTemplate(gadget, "auto", query_list[i]));
        }
        return RSVP.Queue()
          .push(function () {
            return RSVP.all(list);
          })
          .push(function (all_result) {
            var innerHTML = "",
              select_list;
            for (i = 0; i < all_result.length; i += 1) {
              innerHTML += all_result[i];
            }
            container.innerHTML = innerHTML;
            select_list = container.querySelectorAll("select");
            for (i = 0; i < select_list.length; i += 1) {
              $(select_list[i]).selectmenu();
            }
            return listenToSelect(gadget, "auto");
          });
      }
    })
    .declareService(function () {
      var gadget = this,
        container = gadget.props.element.querySelector(".filter_item_container");
      return loopEventListener(
        gadget.props.element.querySelector(".filter_editor"),
        "submit",
        false,
        function () {
          var focused = document.activeElement;
          if (focused.nodeName === "BUTTON") {
            container.removeChild(focused.parentElement.parentElement);
          }
        }
      );
    })
    .declareService(function () {
      var gadget = this;
      return loopEventListener(
        gadget.props.element.querySelector(".submit"),
        "submit",
        false,
        function () {
          var i,
            simple_operator,
            query,
            key,
            select_list,
            simple_query_list = [],
            complex_query,
            select,
            value,
            options = {},
            filter_item_list = gadget.props.element.querySelectorAll(".filter_item"),
            and = gadget.props.element.querySelector(".and");
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
              operator: and.checked ? "AND" : "OR",
              query_list: simple_query_list,
              type: "complex"
            });
            //query to string
            query = Query.objectToSearchText(complex_query);
          } else {
            query = "";
          }
          options.extended_search = query;
          options[gadget.props.begin_from] = undefined;
          return gadget.redirect(
            {
              command: 'store_and_change',
              options : options
            }
          );
        }
      );
    })
    .declareService(function () {
      var gadget = this,
        class_value = "add_after";
      return loopEventListener(
        gadget.props.element.querySelector(".plus"),
        "submit",
        false,
        function () {
          return new RSVP.Queue()
            .push(function () {
              return createFilterItemTemplate(gadget, class_value);
            })
            .push(function (template) {
              var tmp = document.createElement("div"),
                container = gadget.props.element.querySelector(".filter_item_container"),
                select_list,
                i;
              tmp.innerHTML = template;
              select_list = tmp.querySelectorAll("select");
              for (i = 0; i < select_list.length; i += 1) {
                $(select_list[i]).selectmenu();
              }
              container.appendChild(tmp.querySelector("div"));
              return listenToSelect(gadget, class_value);
            });
        }
      );
    })
    .declareService(function () {
      var gadget = this;
      return loopEventListener(
        gadget.props.element.querySelector(".delete"),
        "submit",
        false,
        function () {
          return gadget.trigger();
        }
      );
    });

}(window, document, rJS, RSVP, Handlebars, $, loopEventListener,
  QueryFactory, SimpleQuery, ComplexQuery, Query, console));