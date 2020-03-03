/*jslint nomen: true, indent: 2, maxerr: 3 */
/*global window, rJS, document, RSVP, domsugar */
(function (window, rJS, document, RSVP, domsugar) {
  "use strict";

  var possible_left_button_list = [
      ['panel_action', 'Menu', 'bars', 'panel']
    ],
    possible_main_link_list = [
      // ['menu_url', 'Menu', 'bars'],
      ['front_url', 'Front', 'arrow-up'],
      ['selection_url', 'Previous', 'arrow-up'],
      ['cancel_url', 'Cancel', 'times'],
      ['back_url', 'Back', 'times']
    ],
    possible_right_link_list = [
      ['edit_url', 'Editable', 'pencil'],
      ['view_url', 'Viewable', 'eye'],
      ['right_url', 'New', 'plus'],
      ['language_url', 'Language', 'flag']
    ],
    possible_right_button_list = [
      ['save_action', 'Save', 'check', 'submit'],
      ['submit_action', 'Proceed', 'check', 'submit'],
      ['add_action', 'Add', 'check', 'submit'],
      ['filter_action', 'Filter', 'filter', 'submit']
    ],
    possible_sub_header_list = [
      ['tab_url', 'Views', 'eye'],
      ['jump_url', 'Jump', 'plane'],
      ['actions_url', 'Actions', 'cogs'],
      ['add_url', 'Add', 'plus'],
      ['export_url', 'Export', 'share-square-o'],
      ['delete_url', 'Delete', 'times'],
      ['cut_url', 'Cut', 'scissors'],
      ['fast_input_url', 'Fast Input', 'magic'],
      ['previous_url', 'Previous', 'carat-l'],
      ['next_url', 'Next', 'carat-r'],
      ['upload_url', 'Upload', 'upload'],
      ['download_url', 'Download', 'download']
    ],
    promiseHeaderButton = function (gadget, data) {
      return gadget.translate(data.title)
        .push(function (result) {
          return domsugar('form', [
            domsugar('button', {
              name: data.name,
              text: result,
              type: 'submit',
              'class': 'ui-icon-' + data.icon + ' ui-btn-icon-left ' +
                       data.class
            })
          ]);
        });
    },

    promiseSubHeader = function (gadget, data) {
      // {{#each sub_header_list}}
      // <li><a href="{{url}}" data-i18n="{{title}}" class="ui-btn-icon-top ui-icon-{{icon}} {{class}}">{{title}}</a></li>
      // {{/each}}
      var i,
        translation_list = [];

      for (i = 0; i < data.sub_header_list.length; i += 1) {
        translation_list.push(data.sub_header_list[i].title);
      }
      return gadget.getTranslationList(translation_list)
        .push(function (result_list) {
          var dom_list = [];
          for (i = 0; i < data.sub_header_list.length; i += 1) {
            dom_list.push(domsugar('li', [
              domsugar('a', {
                text: result_list[i],
                href: data.sub_header_list[i].url,
                'class': 'ui-btn-icon-top ui-icon-' +
                         data.sub_header_list[i].icon + ' ' +
                         data.sub_header_list[i].class
              })
            ]));
          }
          return domsugar(null, dom_list);
        });
    };

  rJS(window)
    .setState({
      loaded: false,
      modified: false,
      submitted: true,
      error: false,
      title_text: '',
      title_icon: undefined,
      title_url: undefined
    })

    //////////////////////////////////////////////
    // acquired methods
    //////////////////////////////////////////////
    .declareAcquiredMethod("translate", "translate")
    .declareAcquiredMethod("getTranslationList", "getTranslationList")
    .declareAcquiredMethod("triggerSubmit", "triggerSubmit")
    .declareAcquiredMethod("triggerPanel", "triggerPanel")
    .declareAcquiredMethod("triggerMaximize", "triggerMaximize")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('notifyLoaded', function notifyLoaded() {
      return this.changeState({
        loaded: true
      });
    })
    .declareMethod('notifyLoading', function notifyLoading() {
      return this.changeState({
        loaded: false
      });
    })
    .declareMethod('notifySubmitted', function notifySubmitted() {
      return this.changeState({
        submitted: true,
        // Change modify here, to allow user to redo some modification and being correctly notified
        modified: false
      });
    })
    .declareMethod('notifySubmitting', function notifySubmitting() {
      return this.changeState({
        submitted: false
      });
    })
    .declareMethod('notifyError', function notifyError() {
      return this.changeState({
        loaded: true,
        submitted: true,
        error: true
      });
    })
    .declareMethod('notifyChange', function notifyChange() {
      return this.changeState({
        modified: true
      });
    })
    .declareMethod('setButtonTitle', function setButtonTitle(options) {
      return this.changeState({
        title_button_icon: options.icon,
        title_button_name: options.action
      });
    })
/*
    .declareMethod('notifyUpdate', function () {
      return this.render(this.stats.options);
    })
*/
    .declareMethod('render', function render(options) {
      var state = {
        error: false,
        title_text: '',
        title_icon: undefined,
        title_url: undefined,
        left_button_title: undefined,
        left_button_icon: undefined,
        left_button_name: undefined,
        right_link_title: undefined,
        right_link_icon: undefined,
        right_link_url: undefined,
        right_link_class: undefined,
        right_button_title: undefined,
        right_button_icon: undefined,
        right_button_name: undefined
      },
        klass,
        sub_header_list = [],
        i;

      // Main title
      if (options.hasOwnProperty("page_title")) {
        state.title_text = options.page_title;
      }
      for (i = 0; i < possible_main_link_list.length; i += 1) {
        if (options.hasOwnProperty(possible_main_link_list[i][0])) {
          state.title_icon = possible_main_link_list[i][2];
          state.title_url = options[possible_main_link_list[i][0]];
        }
      }
      // Surcharge icon if the page want it
      if (options.hasOwnProperty("page_icon")) {
        state.title_icon = options.page_icon;
      }

      // Left button
      for (i = 0; i < possible_left_button_list.length; i += 1) {
        if (options.hasOwnProperty(possible_left_button_list[i][0])) {
          state.left_button_title = possible_left_button_list[i][1];
          state.left_button_icon = possible_left_button_list[i][2];
          state.left_button_name = possible_left_button_list[i][3];
        }
      }

      // Handle right link
      for (i = 0; i < possible_right_link_list.length; i += 1) {
        if (options.hasOwnProperty(possible_right_link_list[i][0])) {
          if (options.extra_class &&
              options.extra_class.hasOwnProperty(possible_right_link_list[i][0])) {
            klass = options.extra_class[possible_right_link_list[i][0]];
          } else {
            klass = "";
          }
          if (!options[possible_right_link_list[i][0]]) {
            klass += " ui-disabled";
          }
          state.right_link_title = possible_right_link_list[i][1];
          state.right_link_icon = possible_right_link_list[i][2];
          state.right_link_url = options[possible_right_link_list[i][0]];
          state.right_link_class = klass;
        }
      }
      for (i = 0; i < possible_right_button_list.length; i += 1) {
        if (options.hasOwnProperty(possible_right_button_list[i][0])) {
          state.right_button_title = possible_right_button_list[i][1];
          state.right_button_icon = possible_right_button_list[i][2];
          state.right_button_name = possible_right_button_list[i][3];
        }
      }

      // Sub header
      for (i = 0; i < possible_sub_header_list.length; i += 1) {
        if (options.hasOwnProperty(possible_sub_header_list[i][0])) {
          klass = "";
          if (!options[possible_sub_header_list[i][0]]) {
            klass = "ui-disabled";
          }
          sub_header_list.push({
            title: possible_sub_header_list[i][1],
            icon: possible_sub_header_list[i][2],
            url: options[possible_sub_header_list[i][0]],
            class: klass
          });
        }
      }
      state.sub_header_list = sub_header_list;

      return this.changeState(state);
    })

    .onStateChange(function onStateChange(modification_dict) {
      var gadget = this,
        right_link,
        right_button,
        default_title_icon = "",
        default_right_icon = "",
        title_link,
        promise_list = [];
      // Main title
      if (modification_dict.hasOwnProperty('error') ||
          modification_dict.hasOwnProperty('loaded') ||
          modification_dict.hasOwnProperty('submitted') ||
          modification_dict.hasOwnProperty('title_text') ||
          modification_dict.hasOwnProperty('title_icon') ||
          modification_dict.hasOwnProperty('title_url') ||
          modification_dict.hasOwnProperty('title_button_name')) {
        if (gadget.state.error) {
          default_title_icon = "exclamation";
        } else if (!gadget.state.loaded) {
          default_title_icon = "spinner";
        } else if (!gadget.state.submitted) {
          default_title_icon = "spinner";
        }
        // Updating globally the page title. Does not follow RenderJS philosophy, but, it is enough for now
        if (modification_dict.hasOwnProperty('title_text')) {
          // Be careful, this is CPU costly
          document.title = gadget.state.title_text;
        }

        // H1
        title_link = {
          title: gadget.state.title_text,
          icon: default_title_icon || gadget.state.title_icon,
          url: gadget.state.title_url
        };
        if (gadget.state.title_button_name) {
          promise_list.push(promiseHeaderButton(gadget, {
            title: gadget.state.title_text,
            icon: default_title_icon || gadget.state.title_button_icon,
            name: gadget.state.title_button_name
          }));
        } else if (title_link.url === undefined) {
          // <span data-i18n="{{title}}" class="ui-btn-icon-left ui-icon-{{icon}}" >{{title}}</span>
          promise_list.push(
            gadget.translate(title_link.title)
              .push(function (result) {
                return domsugar('span', {
                  'class': 'ui-btn-icon-left ui-icon-' + title_link.icon,
                  text: result
                });
              })
          );
        } else {
          // <a data-i18n="{{title}}" class="ui-btn-icon-left ui-icon-{{icon}}" href="{{url}}"  accesskey="u">{{title}}</a>
          promise_list.push(
            gadget.translate(title_link.title)
              .push(function (result) {
                return domsugar('a', {
                  'class': 'ui-btn-icon-left ui-icon-' + title_link.icon,
                  'href': title_link.url,
                  'accesskey': 'u',
                  text: result
                });
              })
          );
        }
      } else {
        promise_list.push(gadget.element.querySelector("h1"));
      }

      // Left button
      if (modification_dict.hasOwnProperty('left_button_title') ||
          modification_dict.hasOwnProperty('left_button_icon') ||
          modification_dict.hasOwnProperty('left_button_name')) {
        if (gadget.state.left_button_title === undefined) {
          promise_list.push("");
        } else {
          promise_list.push(promiseHeaderButton(gadget, {
            title: gadget.state.left_button_title,
            icon: gadget.state.left_button_icon,
            name: gadget.state.left_button_name
          }));
        }
      } else {
        promise_list.push(gadget.element.querySelector(".ui-btn-left > div"));
      }

      // Handle right link
      if (modification_dict.hasOwnProperty('loaded') ||
          modification_dict.hasOwnProperty('submitted') ||
          modification_dict.hasOwnProperty('modified') ||
          modification_dict.hasOwnProperty('right_link_title') ||
          modification_dict.hasOwnProperty('right_link_icon') ||
          modification_dict.hasOwnProperty('right_link_url') ||
          modification_dict.hasOwnProperty('right_link_class') ||
          modification_dict.hasOwnProperty('right_button_title') ||
          modification_dict.hasOwnProperty('right_button_icon')) {
        if (gadget.state.modified) {
          default_right_icon = "warning";
        }
        if (gadget.state.right_link_title !== undefined) {
          right_link = {
            title: gadget.state.right_link_title,
            icon: gadget.state.right_link_icon,
            url: gadget.state.right_link_url,
            class: gadget.state.right_link_class
          };
        }
        if (gadget.state.right_button_title !== undefined) {
          right_button = {
            title: gadget.state.right_button_title,
            icon: default_right_icon || gadget.state.right_button_icon,
            name: gadget.state.right_button_name
          };
          if (gadget.state.error || !gadget.state.loaded || !gadget.state.submitted) {
            right_button.class = "ui-disabled";
          }
        }

        if (right_button !== undefined) {
          promise_list.push(promiseHeaderButton(gadget, right_button));
        } else if (right_link !== undefined) {
          // <a data-i18n="{{title}}" href="{{url}}" class="ui-icon-{{icon}} ui-btn-icon-left {{class}}">{{title}}</a>
          promise_list.push(
            gadget.translate(right_link.title)
              .push(function (result) {
                return domsugar('a', {
                  text: result,
                  'class': 'ui-icon-' + right_link.icon + ' ui-btn-icon-left ' +
                           right_link.class,
                  href: right_link.url
                });
              })
          );
        } else {
          promise_list.push("");
        }
      } else {
        promise_list.push(gadget.element.querySelector(".ui-btn-right > div"));
      }

      // Handle sub header
      if (modification_dict.hasOwnProperty('sub_header_list')) {
        promise_list.push(promiseSubHeader(gadget, {
          sub_header_list: gadget.state.sub_header_list
        }));
      } else {
        promise_list.push(gadget.element.querySelector(".ui-subheader")
                                        .querySelector("ul"));
      }

      return new RSVP.Queue(RSVP.all(promise_list))
        .push(function (result_list) {
          domsugar(gadget.element, [
            domsugar('div', {'data-role': 'header', class: 'ui-header'}, [

              // Left button
              domsugar('div', {class: 'ui-btn-left'}, [
                domsugar('div', {class: 'ui-controlgroup-controls'}, [
                  result_list[1]
                ])
              ]),

              // H1
              domsugar('h1', [result_list[0]]),

              // Right button
              domsugar('div', {class: 'ui-btn-right'}, [
                domsugar('div', {class: 'ui-controlgroup-controls'}, [
                  result_list[2]
                ])
              ]),

              // Subheader
              domsugar('div', {class: 'ui-subheader'}, [
                domsugar('ul', [result_list[3]])
              ])
            ])
          ]);
        });
    })

    //////////////////////////////////////////////
    // handle button submit
    //////////////////////////////////////////////
    .onEvent('submit', function submit(evt) {
      var name = evt.target[0].getAttribute("name");
      if (name === "panel") {
        return this.triggerPanel();
      }
      if (name === "submit") {
        return this.triggerSubmit();
      }
      if (name === "maximize") {
        return this.triggerMaximize();
      }
      throw new Error("Unsupported button " + name);
    });

}(window, rJS, document, RSVP, domsugar));