/*jslint nomen: true, indent: 2, maxerr: 3, unparam: true */
/*global window, document, rJS, RSVP, Node, asBoolean , ensureArray,
         mergeGlobalActionWithRawActionList, domsugar*/
(function (window, document, rJS, RSVP, Node, asBoolean, ensureArray,
           mergeGlobalActionWithRawActionList, domsugar) {
  "use strict";

  function appendDt(fragment, dt_title, dt_icon,
                    action_list, href_list, index) {
    var element_list = [
      domsugar('dt', {
        text: dt_title,
        'class': 'ui-btn-icon-left ui-icon-' + dt_icon
      })
    ],
      i;
    for (i = 0; i < action_list.length; i += 1) {
      element_list.push(domsugar('dd', {'class': 'document-listview'}, [
        domsugar('a', {
          href: href_list[index + i],
          text: action_list[i].title,
          'class': action_list[i].class_name || null
        })
      ]));
    }
    fragment.appendChild(domsugar(null, element_list));
  }

  rJS(window)
    .setState({
      visible: false
    })
    //////////////////////////////////////////////
    // acquired method
    //////////////////////////////////////////////
    .declareAcquiredMethod("getUrlForList", "getUrlForList")
    .declareAcquiredMethod("getTranslationList", "getTranslationList")
    .declareAcquiredMethod("getTranslationDict", "getTranslationDict")
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
        jio_key = options.jio_key,
        view = options.view,
        jump_view = options.jump_view,
        visible = options.visible,
        extra_menu_list = options.extra_menu_list,
        display_workflow_list,
        context = this,
        workflow_list,
        group_mapping,
        view_list,
        action_list,
        clone_list,
        jump_list;

      if (visible === undefined) {
        visible = context.state.visible;
      }

      if (options.display_workflow_list === undefined) {
        display_workflow_list = true;
      } else {
        display_workflow_list = asBoolean(options.display_workflow_list);
      }

      if ((erp5_document !== undefined) && (jio_key !== undefined)) {
        group_mapping = mergeGlobalActionWithRawActionList(jio_key,
          view, jump_view,
          erp5_document._links, [
            "action_workflow",
            "action_object_view", [
              "action_object_jio_action",
              "action_object_jio_button",
              "action_object_jio_fast_input"
            ],
            "action_object_clone_action",
            "action_object_jio_jump"
          ], {
            "action_object_jio_action": "display_dialog_with_history",
            "action_object_clone_action": "display_dialog_with_history"
          }, {
            "action_object_clone_action": true
          });

        workflow_list = JSON.stringify(group_mapping.action_workflow);
        view_list = JSON.stringify(group_mapping.action_object_view);
        action_list = JSON.stringify(group_mapping.action_object_jio_action);
        clone_list = JSON.stringify(group_mapping.action_object_clone_action);
        jump_list = JSON.stringify(group_mapping.action_object_jio_jump);
      }

      if (extra_menu_list !== undefined) {
        extra_menu_list = JSON.stringify(extra_menu_list);
      }

      return context.getUrlParameter('editable')
        .push(function (editable) {
          return context.changeState({
            visible: visible,
            display_workflow_list: display_workflow_list,
            workflow_list: workflow_list,
            view_list: view_list,
            action_list: action_list,
            clone_list: clone_list,
            jump_list: jump_list,
            global: true,
            jio_key: jio_key,
            view: view,
            jump_view: jump_view,
            editable: asBoolean(options.editable) || asBoolean(editable) || false,
            extra_menu_list: extra_menu_list
          });
        });
    })
    .onStateChange(function onStateChange(modification_dict) {
      var i,
        gadget = this,
        workflow_list,
        view_list,
        action_list,
        clone_list,
        jump_list,
        dl_fragment,
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
      if (modification_dict.hasOwnProperty("editable")) {
        queue
          // Update the global links
          .push(function () {
            return RSVP.hash({
              url_list: gadget.getUrlForList([
                {command: 'display', options: {page: "ui_flight_comparison_script_page"}},
                {command: 'display', options: {page: "ui_flight_comparison_log_page"}}
              ]),
              translation_list: gadget.getTranslationList([
                'Editable',
                'Edit & Run Script',
                'Run Logs'
              ])
            });
          })
          .push(function (result_dict) {
            var editable_value = [],
              element_list = [],
              icon_and_key_list = [
                'edit', null,
                'puzzle-piece', null
              ];

            for (i = 0; i < result_dict.url_list.length; i += 1) {
              element_list.push(domsugar('li', [
                domsugar('a', {
                  href: result_dict.url_list[i],
                  'class': 'ui-btn-icon-left ui-icon-' + icon_and_key_list[2 * i],
                  accesskey: icon_and_key_list[2 * i + 1],
                  text: result_dict.translation_list[i + 1]
                })
              ]));
            }

            domsugar(gadget.element.querySelector("ul"),
                     [domsugar(null, element_list)]);
          });
      }

      if ((this.state.global === true) &&
          (modification_dict.hasOwnProperty("editable") ||
          modification_dict.hasOwnProperty("view") ||
          modification_dict.hasOwnProperty("jump_view") ||
          modification_dict.hasOwnProperty("workflow_list") ||
          modification_dict.hasOwnProperty("action_list") ||
          modification_dict.hasOwnProperty("clone_list") ||
          modification_dict.hasOwnProperty("jump_list") ||
          modification_dict.hasOwnProperty("jio_key") ||
          modification_dict.hasOwnProperty("view_list") ||
          modification_dict.hasOwnProperty("extra_menu_list"))) {

        dl_fragment = document.createDocumentFragment();
        gadget.element.querySelector("dl").textContent = '';
        if (this.state.view_list !== undefined) {
          queue
            .push(function () {
              var parameter_list = [];

              view_list = JSON.parse(gadget.state.view_list);
              action_list = JSON.parse(gadget.state.action_list);
              clone_list = JSON.parse(gadget.state.clone_list);
              jump_list = JSON.parse(gadget.state.jump_list);
              workflow_list = JSON.parse(gadget.state.workflow_list);

              parameter_list = view_list.concat(workflow_list).concat(
                action_list
              ).concat(clone_list).concat(jump_list).map(function (options) {
                return options.url_kw;
              });
              return RSVP.hash({
                url_list: gadget.getUrlForList(parameter_list),
                translation_dict: gadget.getTranslationDict([
                  'Views', 'Workflows', 'Actions', 'Jumps'
                ])
              });
            })
            .push(function (result_dict) {
              appendDt(dl_fragment, result_dict.translation_dict.Views, 'eye',
                       view_list, result_dict.url_list, 0);
              if (gadget.state.display_workflow_list) {
                // show Workflows only on document
                appendDt(dl_fragment, result_dict.translation_dict.Workflows, 'random',
                  workflow_list, result_dict.url_list, view_list.length);
              }
              appendDt(dl_fragment, result_dict.translation_dict.Actions, 'cogs',
                       action_list.concat(clone_list), result_dict.url_list,
                       view_list.length + workflow_list.length);
              appendDt(dl_fragment, result_dict.translation_dict.Jumps, 'plane',
                       jump_list, result_dict.url_list,
                       view_list.length + workflow_list.length +
                       action_list.length + clone_list.length);
            });
        }
        if (gadget.state.hasOwnProperty("extra_menu_list") &&
            gadget.state.extra_menu_list) {
          queue
            .push(function () {
              return gadget.getTranslationList(['Global']);
            })
            .push(function (translation_list) {
              var extra_menu_list = JSON.parse(gadget.state.extra_menu_list);
              extra_menu_list.forEach(function (menu) {
                appendDt(dl_fragment, menu.title, menu.icon,
                       menu.entry_list, menu.href_list, 0);
              });
            });
        }
      }
      queue
        .push(function () {
          if (dl_fragment) {
            domsugar(gadget.element.querySelector("dl"), [dl_fragment]);
          }
        });
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
    }, false, false);
}(window, document, rJS, RSVP, Node, asBoolean, ensureArray,
  mergeGlobalActionWithRawActionList, domsugar));