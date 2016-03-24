/*jslint indent: 2, maxerr: 3, nomen: true */
/*global window, document, rJS, RSVP, Handlebars, $, loopEventListener*/
(function (window, document, rJS, RSVP, Handlebars, $, loopEventListener) {
  "use strict";
  var gadget_klass = rJS(window),
    sort_item_source = gadget_klass.__template_element
                         .getElementById("sort-item-template")
                         .innerHTML,
    sort_item_template = Handlebars.compile(sort_item_source),
    sort_source = gadget_klass.__template_element
                         .getElementById("sort-template")
                         .innerHTML,
    sort_template = Handlebars.compile(sort_source);

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
    var sort_column_list = gadget.props.sort_column_list,
      sort_value_list = sort_value || [],
      option_list = [],
      i;


    for (i = 0; i < sort_column_list.length; i += 1) {
      option_list.push({
        "text": sort_column_list[i][1],
        "value": sort_column_list[i][0],
        "selected_option": sort_value_list[0]
      });
    }

    return gadget.translateHtml(sort_item_template({
      option: option_list,
      operator: sort_value_list[1]
    }));
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
      gadget.props.sort_column_list = options.sort_column_list || [];
      gadget.props.key = options.key;
      gadget.props.sort_list = options.sort_list;

      return new RSVP.Queue()
        .push(function () {
          var tmp = sort_template();
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
        list = [];
      return new RSVP.Queue()
        .push(function () {
          for (i = 0; i < gadget.props.sort_list.length; i += 1) {
            if (gadget.props.sort_list[i]) {
              list.push(createSortItemTemplate(gadget, gadget.props.sort_list[i]));
            }
          }
          return RSVP.all(list);
        })
        .push(function (all_result) {
          var innerHTML = "",
            select_list;
          for (i = 0; i < all_result.length; i += 1) {
            innerHTML += all_result[i];
          }
          gadget.props.element.querySelector(".sort_item_container").innerHTML = innerHTML;
          select_list = gadget.props.element.querySelector(".sort_item_container").querySelectorAll("select");
          for (i = 0; i < select_list.length; i += 1) {
            $(select_list[i]).selectmenu();
          }
        });
    })
    .declareService(function () {
      var gadget = this,
        container = gadget.props.element.querySelector(".sort_item_container");
      return loopEventListener(
        gadget.props.element.querySelector(".sort_editor"),
        "submit",
        false,
        function () {
          var focused = document.activeElement;
          container.removeChild(focused.parentElement);
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
          var sort_list = gadget.props.element.querySelectorAll(".sort_item"),
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
            options[gadget.props.key] = undefined;
          } else {
            options[gadget.props.key] = sort_query;
          }
          return gadget.redirect({
            command: 'store_and_change',
            options: options
          });
        }
      );
    })
    .declareService(function () {
      var gadget = this;
      return loopEventListener(
        gadget.props.element.querySelector(".plus"),
        "submit",
        false,
        function () {
          return new RSVP.Queue()
            .push(function () {
              return createSortItemTemplate(gadget);
            })
            .push(function (template) {
              var tmp = document.createElement("div"),
                container = gadget.props.element.querySelector(".sort_item_container"),
                select_list,
                i;
              tmp.innerHTML = template;
              select_list = tmp.querySelectorAll("select");
              for (i = 0; i < select_list.length; i += 1) {
                $(select_list[i]).selectmenu();
              }
              container.appendChild(tmp.querySelector("div"));
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

}(window, document, rJS, RSVP, Handlebars, $, loopEventListener));