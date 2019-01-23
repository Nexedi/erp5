/*jslint indent: 2, maxerr: 3, nomen: true */
/*global window, document, rJS, RSVP, Handlebars*/
(function (window, document, rJS, RSVP, Handlebars) {
  "use strict";

  var gadget_klass = rJS(window),
    template_element = gadget_klass.__template_element,
    sort_item_template = Handlebars.compile(template_element
                         .getElementById("sort-item-template")
                         .innerHTML),
    sort_template = Handlebars.compile(template_element
                         .getElementById("sort-template")
                         .innerHTML);

  Handlebars.registerHelper('equal', function (left_value, right_value, options) {
    if (arguments.length < 3) {
      throw new Error("Handlebars Helper equal needs 2 parameters");
    }
    if (left_value !== right_value) {
      return options.inverse(this);
    }
    return options.fn(this);
  });


  function createSortItemTemplate(gadget, sort_value) {
    var sort_column_list = gadget.state.sort_column_list,
      sort_value_list = sort_value || [],
      option_list = [],
      is_selected = false,
      i;

    for (i = 0; i < sort_column_list.length; i += 1) {
      is_selected = is_selected || (sort_value_list[0] === sort_column_list[i][0]);
      option_list.push({
        text: sort_column_list[i][1],
        value: sort_column_list[i][0],
        selected: sort_value_list[0] === sort_column_list[i][0]
      });
    }
    if (!is_selected && (sort_value !== undefined)) {
      option_list.push({
        text: sort_value_list[0],
        value: sort_value_list[0],
        selected: true
      });
    }

    return gadget.translateHtml(sort_item_template({
      option: option_list,
      operator: sort_value_list[1]
    }));
  }

  /* Valid sort item is a tuple of (column-name, ordering) */
  function isValidSortItem(sort_item) {
    return sort_item.length === 2 &&
           (sort_item[1] === 'ascending' || sort_item[1] === 'descending');
  }

  gadget_klass
    //////////////////////////////////////////////
    // acquired method
    //////////////////////////////////////////////
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("trigger", "trigger")

    .onStateChange(function onStateChange() {
      var gadget = this,
        div = document.createElement("div"),
        container = gadget.element.querySelector(".container");

      return gadget.translateHtml(sort_template())
        .push(function (translated_html) {

          div.innerHTML = translated_html;

          return RSVP.all(gadget.state.sort_list
            .filter(isValidSortItem)
            .map(function (sort_item) {
              return createSortItemTemplate(gadget, sort_item);
            })
            );
        })
        .push(function (result_list) {
          var i,
            subdiv,
            filter_item_container = div.querySelector('.sort_item_container');

          for (i = 0; i < result_list.length; i += 1) {
            subdiv = document.createElement("div");
            subdiv.innerHTML = result_list[i];
            filter_item_container.appendChild(subdiv);
          }

          while (container.firstChild) {
            container.removeChild(container.firstChild);
          }
          container.appendChild(div);
        });
    })

    .declareMethod('render', function render(options) {
      return this.changeState({
        sort_column_list: options.sort_column_list || [],
        key: options.key,
        sort_list: options.sort_list
      });
    })

    .onEvent('click', function click(evt) {
      var gadget = this,
        container;

      if (evt.target.classList.contains('trash')) {
        evt.preventDefault();
        container = gadget.element.querySelector(".sort_item_container");
        while (container.firstChild) {
          container.removeChild(container.firstChild);
        }
      }

      if (evt.target.classList.contains('close')) {
        evt.preventDefault();
        return this.trigger();
      }

      if (evt.target.classList.contains('plus')) {
        evt.preventDefault();
        return createSortItemTemplate(gadget)
          .push(function (template) {
            var tmp = document.createElement("div");
            container = gadget.element.querySelector(".sort_item_container");
            tmp.innerHTML = template;
            container.appendChild(tmp);
          });
      }

      if (evt.target.classList.contains('ui-icon-minus')) {
        evt.preventDefault();
        evt.target.parentElement.parentElement.removeChild(evt.target.parentElement);
      }

    }, false, false)

    .onEvent('submit', function submit() {
      var gadget = this,
        sort_list = gadget.element.querySelectorAll(".sort_item"),
        sort_query = [],
        select_list,
        sort_item,
        options = {},
        i;

      for (i = 0; i < sort_list.length; i += 1) {
        sort_item = sort_list[i];
        select_list = sort_item.querySelectorAll("select");
        sort_query[i] = [select_list[0][select_list[0].selectedIndex].value,
          select_list[1][select_list[1].selectedIndex].value];
      }
      if (i === 0) {
        options[gadget.state.key] = undefined;
      } else {
        options[gadget.state.key] = sort_query;
      }
      return gadget.redirect({
        command: 'store_and_change',
        options: options
      }, true);
    });

}(window, document, rJS, RSVP, Handlebars));