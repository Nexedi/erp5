/*jslint nomen: true, indent: 2, maxerr: 3, unparam: true */
/*global window, document, rJS, Handlebars, RSVP, Node, URL, loopEventListener, asBoolean , ensureArray*/
(function (window, document, rJS, Handlebars, RSVP, Node, URL, loopEventListener, asBoolean, ensureArray) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // temlates
  /////////////////////////////////////////////////////////////////
  // Precompile templates while loading the first gadget instance
  var gadget_klass = rJS(window),
    template_element = gadget_klass.__template_element,
    panel_template_body_list = Handlebars.compile(template_element
                         .getElementById("panel-template-body-list")
                         .innerHTML),
    panel_template_body_desktop = Handlebars.compile(template_element
                                  .getElementById("panel-template-body-desktop")
                                  .innerHTML);

  gadget_klass
    .setState({
      visible: false
    })
    //////////////////////////////////////////////
    // acquired method
    //////////////////////////////////////////////
    .declareAcquiredMethod("getUrlForList", "getUrlForList")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("translate", "translate")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('toggle', function toggle() {
      return this.changeState({
        visible: !this.state.visible
      });
    })
    .declareMethod('close', function close() {
      return this.changeState({
        visible: false
      });
    })

    .declareMethod('render', function render(options) {
      var erp5_document = options.erp5_document,
        view = options.view,
        visible = options.visible,
        context = this,
        workflow_list,
        view_list,
        action_list,
        i;

      if (visible === undefined) {
        visible = context.state.visible;
      }
      if (erp5_document !== undefined) {
        workflow_list = ensureArray(erp5_document._links.action_workflow);
        view_list = ensureArray(erp5_document._links.action_object_view);
        action_list = ensureArray(erp5_document._links.action_object_jio_action)
          .concat(ensureArray(erp5_document._links.action_object_jio_button))
          .concat(ensureArray(erp5_document._links.action_object_jio_fast_input));

        if (view === 'view') {
          for (i = 0; i < view_list.length; i += 1) {
            view_list[i].class_name = view_list[i].name === view ? 'active' : '';
          }
        } else {
          for (i = 0; i < workflow_list.length; i += 1) {
            workflow_list[i].class_name = workflow_list[i].href === view ? 'active' : '';
          }
          for (i = 0; i < view_list.length; i += 1) {
            view_list[i].class_name = view_list[i].href === view ? 'active' : '';
          }
          for (i = 0; i < action_list.length; i += 1) {
            action_list[i].class_name = action_list[i].href === view ? 'active' : '';
          }
        }
        // Prevent has much as possible to modify the DOM panel
        // stateChange prefer to compare strings
        workflow_list = JSON.stringify(workflow_list);
        view_list = JSON.stringify(view_list);
        action_list = JSON.stringify(action_list);
      }
      return context.getUrlParameter('editable')
        .push(function (editable) {
          return context.changeState({
            visible: visible,
            workflow_list: workflow_list,
            view_list: view_list,
            action_list: action_list,
            global: true,
            editable: asBoolean(options.editable) || asBoolean(editable) || false
          });
        });
    })

    .onStateChange(function onStateChange(modification_dict) {
      var context = this,
        gadget = this,
        queue = new RSVP.Queue();

      if (modification_dict.hasOwnProperty("visible")) {
        if (this.state.visible) {
          if (!this.element.classList.contains('visible')) {
            this.element.classList.toggle('visible');
          }
        } else {
          if (this.element.classList.contains('visible')) {
            this.element.classList.remove('visible');
          }
        }
      }

      if (modification_dict.hasOwnProperty("global")) {
        queue
          .push(function (my_translated_or_plain_html) {
            return context.getDeclaredGadget('erp5_searchfield');
          })
          .push(function (search_gadget) {
            return search_gadget.render({
              focus: false,
              extended_search: ''
            });
          });
      }

      if (modification_dict.hasOwnProperty("editable")) {
        queue
          // Update the global links
          .push(function () {
            return context.getUrlForList([
              {command: 'display', options: {page: "front"}},
              {command: 'display', options: {page: "history"}},
              {command: 'display', options: {page: "preference"}},
              {command: 'display', options: {page: "logout"}},
              {command: 'display_stored_state', options: {page: "search"}},
              {command: 'display', options: {page: "worklist"}},
              {command: 'display'}
            ]);
          })
          .push(function (result_list) {
            return context.translateHtml(
              panel_template_body_list({
                "module_href": result_list[0],
                "history_href": result_list[1],
                "preference_href": result_list[2],
                "logout_href": result_list[3],
                "search_href": result_list[4],
                "worklist_href": result_list[5],
                "front_href": result_list[6]
              })
            );
          })

          .push(function (result) {
            context.element.querySelector("ul").innerHTML = result;

            // Update the checkbox field value
            return RSVP.all([
              context.getDeclaredGadget("erp5_checkbox"),
              context.translate("Editable")
            ]);
          })
          .push(function (result_list) {
            var value = [],
              search_gadget = result_list[0],
              title = result_list[1];
            if (context.state.editable) {
              value = ['editable'];
            }
            return search_gadget.render({field_json: {
              editable: true,
              name: 'editable',
              key: 'editable',
              hidden: false,
              items: [[title, 'editable']],
              default: value
            }});
          });
      }

      if ((this.state.global === true) &&
          (modification_dict.hasOwnProperty("editable") ||
          modification_dict.hasOwnProperty("workflow_list") ||
          modification_dict.hasOwnProperty("action_list") ||
          modification_dict.hasOwnProperty("view_list"))) {
        if (this.state.view_list === undefined) {
          queue
            .push(function () {
              gadget.element.querySelector("dl").textContent = '';
            });
        } else {
          queue
            .push(function () {
              var i = 0,
                parameter_list = [],
                workflow_list = JSON.parse(gadget.state.workflow_list),
                view_list = JSON.parse(gadget.state.view_list),
                action_list = JSON.parse(gadget.state.action_list);

              for (i = 0; i < workflow_list.length; i += 1) {
                parameter_list.push({
                  command: 'change',
                  options: {
                    view: workflow_list[i].href,
                    page: undefined
                  }
                });
              }
              for (i = 0; i < view_list.length; i += 1) {
                parameter_list.push({
                  command: 'change',
                  options: {
                    view: view_list[i].href,
                    page: undefined
                  }
                });
              }
              for (i = 0; i < action_list.length; i += 1) {
                parameter_list.push({
                  command: 'change',
                  options: {
                    view: action_list[i].href,
                    page: undefined
                  }
                });
              }
              return gadget.getUrlForList(parameter_list);
            })
            .push(function (result_list) {
              var i,
                result_workflow_list = [],
                result_view_list = [],
                result_action_list = [],
                workflow_list = JSON.parse(gadget.state.workflow_list),
                view_list = JSON.parse(gadget.state.view_list),
                action_list = JSON.parse(gadget.state.action_list);

              for (i = 0; i < workflow_list.length; i += 1) {
                result_workflow_list.push({
                  title: workflow_list[i].title,
                  class_name: workflow_list[i].class_name,
                  href: result_list[i]
                });
              }
              for (i = 0; i < view_list.length; i += 1) {
                result_view_list.push({
                  title: view_list[i].title,
                  class_name: view_list[i].class_name,
                  href: result_list[i + workflow_list.length]
                });
              }
              for (i = 0; i < action_list.length; i += 1) {
                result_action_list.push({
                  title: action_list[i].title,
                  class_name: action_list[i].class_name,
                  href: result_list[i + workflow_list.length + view_list.length]
                });
              }
              return gadget.translateHtml(panel_template_body_desktop({
                workflow_list: result_workflow_list,
                view_list: result_view_list,
                action_list: result_action_list
              }));
            })
            .push(function (translated_html) {
              gadget.element.querySelector("dl").innerHTML = translated_html;
            });
        }
      }

      return queue;
    })

    /////////////////////////////////////////////////////////////////
    // declared services
    /////////////////////////////////////////////////////////////////
    .onEvent('click', function click(evt) {
      if ((evt.target.nodeType === Node.ELEMENT_NODE) &&
          (evt.target.tagName === 'BUTTON')) {
        return this.toggle();
      }
    }, false, false)

    .allowPublicAcquisition('notifyChange', function notifyChange(
      argument_list,
      scope
    ) {
      if (scope === 'erp5_checkbox') {
        var context = this;
        return context.getDeclaredGadget('erp5_checkbox')
          .push(function (gadget) {
            return gadget.getContent();
          })
          .push(function (result) {
            var options = {editable: undefined};
            if (result.editable.length === 1) {
              options.editable = true;
            }
            return context.redirect({command: 'change', options: options});
          });
      }
      // Typing a search query should not modify the header status
      return;
    }, {mutex: 'changestate'})
    .allowPublicAcquisition('notifyValid', function notifyValid() {
      // Typing a search query should not modify the header status
      return;
    })

    .onEvent('submit', function submit(event) {
      var gadget = this,
        search_gadget,
        redirect_options = {
          page: "search"
        };

      return gadget
        .getDeclaredGadget("erp5_searchfield")
        .push(function (declared_gadget) {
          search_gadget = declared_gadget;
          return search_gadget.getContent();
        })
        .push(function (data) {
          if (data.search) {
            redirect_options.extended_search = data.search;
          }
          // let the search gadget know its current state (value and focus)
          // in order to be able to zero it out in the next Promise
          // input gadget's state does not reflect immediate reality
          // so we need to manage its state from the parent
          return search_gadget.render({
            extended_search: data.search,
            focus: true
          });
        })
        .push(function () {
          // we want the search field in side panel to be empty and blured
          return search_gadget.render({
            extended_search: '',
            focus: false  // we don't want focus on the empty field for sure
          });
        })
        .push(function () {
          return gadget.redirect({command: 'store_and_display', options: redirect_options});
        });

    }, /*useCapture=*/false, /*preventDefault=*/true);

}(window, document, rJS, Handlebars, RSVP, Node, URL, loopEventListener, asBoolean, ensureArray));
