/*global window, rJS, document, Node,
         QueryFactory, SimpleQuery, ComplexQuery, Query, domsugar*/
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, document, Node,
           QueryFactory, SimpleQuery, ComplexQuery, Query, domsugar) {
  "use strict";

  function convertQueryToSearchText(query) {
    return Query.objectToSearchText(query);
  }

  function convertFullTextQueryListToSearchText(full_text_query_list) {
    // jio objectToSearchText explicitely add all operators
    // replace it for now and drop operators if not needed
    var i,
      len = full_text_query_list.length,
      result_list = [];
    for (i = 0; i < len; i += 1) {
      if (full_text_query_list[i].value.indexOf(' ') === -1) {
        result_list.push(full_text_query_list[i].value);
      } else {
        result_list.push(convertQueryToSearchText(full_text_query_list[i]));
      }
    }
    return result_list.join(' ');
  }

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('render', function (options) {
      var state_dict = {
        extended_search: options.extended_search || "",
        enable_graphic: options.enable_graphic || false,
        graphic_type: options.graphic_type
      };
      return this.changeState(state_dict);
    })
    .declareAcquiredMethod("triggerListboxGraphicSelection",
                           "triggerListboxGraphicSelection")
    .onStateChange(function (modification_dict) {
      var gadget = this,
        i,
        len,
        button_container = gadget.element.querySelector('div.search_parsed_value'),
        button_graphic = gadget.element.querySelector(".graphic-button"),
        select_button_graphic = gadget.element.querySelector(".change-graphic-button"),
        graphic_css_class = "ui-screen-hidden",
        button,
        operator = 'AND',
        jio_query_list = [],
        query_text_list = [],
        full_text_query_list = [],
        jio_query,
        sub_jio_query,
        parsed_value = '',
        input_value = '',
        continue_full_text_query_search = true;

      if (gadget.state.extended_search) {
        console.log(modification_dict);
        if (modification_dict.enable_graphic &&
            modification_dict.graphic_type &&
              button_graphic) {
          button_graphic.classList.add(graphic_css_class);
          select_button_graphic.classList.remove(graphic_css_class);
        } else {
          button_graphic.classList.remove(graphic_css_class);
          select_button_graphic.classList.add(graphic_css_class);
        }

        // Parse the raw query
        try {
          jio_query = QueryFactory.create(gadget.state.extended_search);
        } catch (error) {
          // it catch all error, not only search criteria invalid error
          // Keep the value as is, to display it to the user
          input_value = gadget.state.extended_search;
        }

        if (jio_query instanceof SimpleQuery) {
          query_text_list.push(jio_query.value);
          jio_query_list.push(jio_query);
        } else if (jio_query instanceof ComplexQuery) {
          len = jio_query.query_list.length;
          operator = jio_query.operator;
          for (i = 0; i < len; i += 1) {
            sub_jio_query = jio_query.query_list[i];
            jio_query_list.push(sub_jio_query);
            if (sub_jio_query instanceof SimpleQuery) {
              query_text_list.push(sub_jio_query.value);
            } else {
              query_text_list.push('complex');
            }
          }
        }

        // If last queries are full text queries, keep them in the input field
        if (jio_query_list.length) {
          while (continue_full_text_query_search) {
            jio_query = jio_query_list[jio_query_list.length - 1];
            if ((operator === 'AND') && (jio_query instanceof SimpleQuery) && (!jio_query.key)) {
              // drop last array element
              full_text_query_list.unshift(jio_query_list[jio_query_list.length - 1]);
              jio_query_list = jio_query_list.slice(0, -1);
              query_text_list = query_text_list.slice(0, -1);
              if (!jio_query_list.length) {
                continue_full_text_query_search = false;
              }
            } else {
              continue_full_text_query_search = false;
            }
          }

          if (full_text_query_list.length) {
            input_value = convertFullTextQueryListToSearchText(full_text_query_list);
          }
          if (jio_query_list.length === 1) {
            parsed_value = convertQueryToSearchText(jio_query_list[0]);
          } else if (jio_query_list.length > 1) {
            parsed_value = convertQueryToSearchText(new ComplexQuery({
              operator: operator,
              query_list: jio_query_list,
              type: "complex"
            }));
          }
        }
      } else if (modification_dict.enable_graphic &&
                   button_graphic && !button_graphic.classList.contains(
                 graphic_css_class)) {
        button_graphic.classList.add(graphic_css_class);
        select_button_graphic.classList.remove(graphic_css_class);
      } else if (select_button_graphic &&
          modification_dict.enable_graphic &&
          !modification_dict.extended_search ){
        select_button_graphic.classList.remove(graphic_css_class);
      }
      console.log(modification_dict);
      button_container.innerHTML = '';
      len = query_text_list.length;
      for (i = 0; i < len; i += 1) {
        button_container.appendChild(
          domsugar("button", {
            "text": query_text_list[i],
            "value": i
          })
        );
      }
      button_container.appendChild(domsugar("input", {
        "type": "hidden",
        "value": parsed_value
      }));

      return gadget.getDeclaredGadget('input')
        .push(function (input_gadget) {
          return input_gadget.render({
            type: "search",
            value: input_value,
            name: "search",
            editable: true
          });
        });
    })

    .allowPublicAcquisition("notifyValid", function () {return; })

    .declareMethod('getContent', function () {
      var gadget = this;
      return this.getDeclaredGadget('input')
        .push(function (input_gadget) {
          return input_gadget.getContent();
        })
        .push(function (result) {
          var content_dict = {search: ''},
            jio_query_list = [],
            jio_query,
            operator = 'AND',
            hidden_input = gadget.element.querySelector('input');
          // Start from the original query
          if (hidden_input.value) {
            // Parse error is not supposed to happen, as hidden_input has been parsed already
            jio_query = QueryFactory.create(hidden_input.value);
            if (jio_query instanceof SimpleQuery) {
              jio_query_list.push(jio_query);
            } else if (jio_query instanceof ComplexQuery) {
              jio_query_list = jio_query.query_list;
              operator = jio_query.operator;
            }
          }

          if (result.search) {
            // User search query is always considered as an argument of an AND
            // complex query (this gadget does not allow to extend OR query)
            jio_query = undefined;
            // XXX trim from input gadget?
            try {
              jio_query = QueryFactory.create(result.search.trim());
            } catch (error) {
              // it catch all error, not only search criteria invalid error
              // Consider the string as a full text only in this case
              // to keep it displayed to the user
              jio_query = new SimpleQuery({value: result.search.trim()});
            }
            if ((jio_query_list.length === 0) && (jio_query instanceof ComplexQuery)) {
              jio_query_list = jio_query.query_list;
              operator = jio_query.operator;
            } else if (jio_query !== undefined) {
              // Keep user search as last argument
              // so that it is still editable after a refresh
              if (operator === 'AND') {
                jio_query_list.push(jio_query);
              } else {
                jio_query_list = [
                  new ComplexQuery({
                    operator: operator,
                    query_list: jio_query_list,
                    type: "complex"
                  }),
                  jio_query
                ];
                operator = 'AND';
              }
            }
          }

          if (jio_query_list.length === 1) {
            content_dict.search = convertQueryToSearchText(jio_query_list[0]);
          } else if (jio_query_list.length > 1) {
            content_dict.search = convertQueryToSearchText(new ComplexQuery({
              operator: operator,
              query_list: jio_query_list,
              type: "complex"
            }));
          }

          return content_dict;
        });
    }, {mutex: 'changestate'})

    .allowPublicAcquisition("notifyFocus", function notifyFocus() {
      // All html5 fields in ERP5JS triggers this method when focus
      // is triggered. This is usefull to display error text.
      // But, in the case of panel, we don't need to handle anything.
      return;
    })
    .allowPublicAcquisition("notifyBlur", function notifyFocus() {
      // All html5 fields in ERP5JS triggers this method when blur
      // is triggered now. This is usefull to display error text.
      // But, in the case of panel, we don't need to handle anything.
      return;
    })
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("triggerSubmit", "triggerSubmit")
    .onEvent('click', function (evt) {
      var gadget = this;
      if (evt.target.tagName === 'BUTTON') {
        if ((evt.target.nodeType === Node.ELEMENT_NODE) &&
            (evt.target.value)) {
          // Open the filter panel if one 'search' button is clicked
          evt.preventDefault();
          return this.triggerSubmit({focus_on: parseInt(evt.target.value, 10)});
        } else if (evt.target.classList.contains("graphic-button")) {
          return gadget.redirect({
            command: "store_and_change",
            options: {
              graphic_type: gadget.state.graphic_type
            }
          });
        } else if (evt.target.classList.contains("change-graphic-button")) {
          return gadget.triggerListboxGraphicSelection();
        }

      }
    }, false, false);

}(window, rJS, document, Node,
  QueryFactory, SimpleQuery, ComplexQuery, Query, domsugar));