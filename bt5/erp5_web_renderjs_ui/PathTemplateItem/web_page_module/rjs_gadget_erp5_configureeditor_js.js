/*jslint indent: 2, maxerr: 3, nomen: true */
/*global window, document, rJS, RSVP, Handlebars*/
(function (window, document, rJS, RSVP, Handlebars) {
  "use strict";

  var gadget_klass = rJS(window),
    template_element = gadget_klass.__template_element,
    column_item_template = Handlebars.compile(template_element
                         .getElementById("column-item-template")
                         .innerHTML),
    column_template = Handlebars.compile(template_element
                         .getElementById("column-template")
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


  function createColumnItemTemplate(gadget, column_value, displayable_column_list) {
    var column_value_list = column_value || [],
      option_list = [],
      i;

    for (i = 0; i < displayable_column_list.length; i += 1) {
      option_list.push({
        text: displayable_column_list[i][1],
        value: displayable_column_list[i][0],
        selected_option: column_value_list[0]
      });
    }

    return gadget.translateHtml(column_item_template({
      option: option_list
    }));
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

      return gadget.translateHtml(column_template())
        .push(function (translated_html) {

          div.innerHTML = translated_html;

          return RSVP.all(gadget.state.column_list
            .map(function (column_item) {
              return createColumnItemTemplate(gadget, column_item, gadget.state.displayable_column_list);
            })
            );
        })
        .push(function (result_list) {
          var i,
            subdiv,
            filter_item_container = div.querySelector('.column_item_container');

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
        column_list: options.column_list,
        displayable_column_list: options.displayable_column_list,
        key: options.key
      });
    })

    .onEvent('click', function click(evt) {
      var gadget = this,
        container;

      if (evt.target.classList.contains('trash')) {
        evt.preventDefault();
        container = gadget.element.querySelector(".column_item_container");
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
        return createColumnItemTemplate(gadget, undefined, gadget.state.displayable_column_list)
          .push(function (template) {
            var tmp = document.createElement("div");
            container = gadget.element.querySelector(".column_item_container");
            tmp.innerHTML = template;
            container.appendChild(tmp);
          });
      }

      if (evt.target.classList.contains('ui-icon-minus')) {
        evt.preventDefault();
        evt.target.parentElement.parentElement.removeChild(evt.target.parentElement);
      }

    }, false, false)

    .onEvent('submit', function submit(evt) {
      var gadget = this,
        options = {},
        form = evt.target,
        i,
        field,
        column_list = [];
      for (i = 0; i < form.elements.length; i += 1) {
        field = form.elements[i];
        if (field.nodeName.toUpperCase() === 'SELECT') {
          column_list.push(field.value);
        }
      }
      if (column_list.length === 0) {
        options[gadget.state.key] = undefined;
      } else {
        // Remove duplicated elements (same column should not be displayed twice)
        column_list = column_list.filter(function (el, i, a) {
          return i === a.indexOf(el);
        });

        options[gadget.state.key] = column_list;
      }

      return gadget.redirect({
        command: 'store_and_change',
        options: options
      }, true);
    });

}(window, document, rJS, RSVP, Handlebars));