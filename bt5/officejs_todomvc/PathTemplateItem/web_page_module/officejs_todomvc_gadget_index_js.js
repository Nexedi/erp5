/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80*/
/*global window, document, navigator, rJS, Handlebars*/
(function (window, document, navigator, rJS, Handlebars) {
  "use strict";


  /* Constants */

  var ENTER_KEY = 13,
    ESCAPE_KEY = 27,


  /* Global Variables */

    handlebars_template;


  /* Initialization */

  rJS(window)

    .setState({
      update: false,
      clear_input: false,
      editing_jio_id: "",
      query: ""
    })

    .declareService(function () {
      var gadget = this,
        div = document.createElement("div");
      gadget.element.appendChild(div);
      handlebars_template = Handlebars.compile(
        document.head.querySelector(".handlebars-template").innerHTML
      );
      // Normally, router gadgets are declared in the HTML of the root gadget
      // because one app only needs one router, and it is not dynamic at all.
      // However, this is declared in JavaScript purely to serve as an example.
      return gadget.declareGadget("officejs_todomvc_gadget_router.html", {
        scope: "router",
        sandbox: "public",
        element: div
      })
        .push(function () {
          if (navigator.serviceWorker) {
            return navigator.serviceWorker.register(
              "officejs_todomvc_serviceworker.js"
            );
          }
        })
        .push(function () {
          return gadget.changeState({update: true});
        });
    })


    /* Acquisition */

    .allowPublicAcquisition("setQuery", function (param_list) {
      var gadget = this;
      gadget.changeState({query: param_list[0]});
    })


    /* Rendering */

    .onStateChange(function (modification_dict) {
      var gadget = this,
        model_gadget,
        todo_count_dict;
      return gadget.getDeclaredGadget("model")
        .push(function (subgadget) {
          model_gadget = subgadget;
          return model_gadget.getTodoCountDict();
        })
        .push(function (count_dict) {
          todo_count_dict = count_dict;
          return model_gadget.getTodoList(gadget.state.query);
        })
        .push(function (todo_list) {
          var plural = todo_list.length === 1 ? " item" : " items",
            focus_query = ".new-todo",
            edit_value = "",
            post_value = "",
            i;
          if (gadget.state.editing_jio_id) {
            focus_query = "li[data-jio-id='"
              + gadget.state.editing_jio_id + "'] .edit";
          }
          if (!modification_dict.hasOwnProperty("clear_input")
              && gadget.element.querySelector(".new-todo")) {
            post_value = gadget.element.querySelector(".new-todo").value;
          }

          for (i = 0; i < todo_list.length; i += 1) {
            if (todo_list[i].id === gadget.state.editing_jio_id) {
              todo_list[i].editing = true;
              edit_value = todo_list[i].title;
            } else {
              todo_list[i].editing = false;
            }
          }

          gadget.element.querySelector(".handlebars-anchor").innerHTML =
            handlebars_template({
              todo_list: todo_list,
              todo_exists: todo_count_dict.total >= 1,
              todo_count: todo_count_dict.active.toString() + plural,
              all_completed: todo_count_dict.active === 0
            });

          gadget.element.querySelector(focus_query).focus();
          if (edit_value) {
            gadget.element.querySelector(focus_query).value = edit_value;
          }
          if (post_value) {
            gadget.element.querySelector(".new-todo").value = post_value;
          }
          gadget.state.update = false;
          gadget.state.clear_input = false;
        });
    })


    /* Event Listeners */

    .onEvent("submit", function (event) {
      var gadget = this,
        item = event.target.elements[0].value.trim();
      if (item) {
        return gadget.getDeclaredGadget("model")
          .push(function (model_gadget) {
            return model_gadget.postTodo(item);
          })
          .push(function () {
            return gadget.changeState({clear_input: true});
          });
      }
    }, false, true)

    .onEvent("click", function (event) {
      var gadget = this,
        todo_item = event.target.parentElement.parentElement,
        jio_id = todo_item.getAttribute("data-jio-id");
      return gadget.getDeclaredGadget("model")
        .push(function (model_gadget) {
          switch (event.target.className) {
          case "toggle":
            return model_gadget.setOneTodoStatus(
              jio_id,
              !todo_item.classList.contains("completed")
            );
          case "toggle-all":
            return model_gadget.setAllTodoStatus(event.target.checked);
          case "toggle-label":
            return model_gadget.setAllTodoStatus(
              !gadget.element.querySelector(".toggle-all").checked
            );
          case "destroy":
            return model_gadget.removeOneTodo(jio_id);
          case "clear-completed":
            return model_gadget.removeAllCompletedTodo();
          default:
            if (gadget.state.editing_jio_id
                && event.target.className !== "edit") {
              return "clicking outside of the input box cancels editing";
            }
            return "default";
          }
        })
        .push(function (path) {
          if (path !== "default") {
            return gadget.changeState({update: true, editing_jio_id: ""});
          }
        });
    }, false, false)

    .onEvent("dblclick", function (event) {
      var gadget = this;
      if (event.target.className === "todo-label") {
        return gadget.changeState({
          editing_jio_id: event.target.parentElement
            .parentElement.getAttribute("data-jio-id")
        });
      }
    }, false, false)

    .onEvent("keydown", function (event) {
      var gadget = this, item;
      if (event.target.className === "edit") {
        if (event.keyCode === ESCAPE_KEY) {
          return gadget.changeState({update: true, editing_jio_id: ""});
        }
        item = event.target.value.trim();
        if (event.keyCode === ENTER_KEY && item) {
          return gadget.getDeclaredGadget("model")
            .push(function (model_gadget) {
              return model_gadget.changeTodoTitle(
                event.target.parentElement.getAttribute("data-jio-id"),
                item
              );
            })
            .push(function () {
              return gadget.changeState({update: true, editing_jio_id: ""});
            });
        }
      }
    }, false, false);

}(window, document, navigator, rJS, Handlebars));