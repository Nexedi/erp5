/*jslint nomen: true, indent: 2, maxerr: 3 */
/*global window, rJS, document, RSVP */
(function (window, rJS, document, RSVP) {
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
    header_button_template = function (data) {
      // <form><button name='{{name}}' data-i18n="{{title}}" type='submit' class='ui-icon-{{icon}} ui-btn-icon-left {{class}}'>{{title}}</button></form>
      var form_element = document.createElement('form'),
        button_element = document.createElement('button');

      button_element.setAttribute('name', data.name);
      button_element.setAttribute('data-i18n', data.title);
      button_element.setAttribute('type', 'submit');
      button_element.setAttribute('class', 'ui-icon-' + data.icon + ' ui-btn-icon-left ' + data.class);
      form_element.appendChild(button_element);
      return form_element.outerHTML;
    },
    sub_header_template = function (data) {
      // {{#each sub_header_list}}
      // <li><a href="{{url}}" data-i18n="{{title}}" class="ui-btn-icon-top ui-icon-{{icon}} {{class}}">{{title}}</a></li>
      // {{/each}}
      var fragment = document.createElement('div'),
        li_element,
        a_element,
        i;
      for (i = 0; i < data.sub_header_list.length; i += 1) {
        li_element = document.createElement('li');
        a_element = document.createElement('a');
        a_element.setAttribute('href', data.sub_header_list[i].url);
        a_element.setAttribute('data-i18n', data.sub_header_list[i].title);
        a_element.setAttribute('class', 'ui-btn-icon-top ui-icon-' + data.sub_header_list[i].icon + ' ' + data.sub_header_list[i].class);
        li_element.appendChild(a_element);
        fragment.appendChild(li_element);
      }
      return fragment.innerHTML;
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
    /////////////////////////////////////////////////////////////////
    // ready
    /////////////////////////////////////////////////////////////////
    // Init local properties
    .ready(function ready() {
      this.props = {
        element_list: [
          this.element.querySelector("h1"),
          this.element.querySelector(".ui-btn-left > div"),
          this.element.querySelector(".ui-btn-right > div"),
          this.element.querySelector(".ui-subheader").querySelector("ul")
        ]
      };
    })

    //////////////////////////////////////////////
    // acquired methods
    //////////////////////////////////////////////
    .declareAcquiredMethod("translateHtml", "translateHtml")
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
        title_button_icon: undefined,
        title_button_name: undefined,
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
        title_button,
        promise_list = [],
        tmp_element;
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
        title_link = {
          title: gadget.state.title_text,
          icon: default_title_icon || gadget.state.title_icon,
          url: gadget.state.title_url
        };
        if (gadget.state.title_button_name) {
          title_button = {
            title: gadget.state.title_text,
            icon: default_title_icon || gadget.state.title_button_icon,
            name: gadget.state.title_button_name
          };
          promise_list.push(gadget.translateHtml(header_button_template(title_button)));
        } else if (title_link.url === undefined) {
          // <span data-i18n="{{title}}" class="ui-btn-icon-left ui-icon-{{icon}}" >{{title}}</span>
          tmp_element = document.createElement('span');
          tmp_element.setAttribute('data-i18n', title_link.title);
          tmp_element.setAttribute('class', 'ui-btn-icon-left ui-icon-' + title_link.icon);
          promise_list.push(gadget.translateHtml(tmp_element.outerHTML));
        } else {
          // <a data-i18n="{{title}}" class="ui-btn-icon-left ui-icon-{{icon}}" href="{{url}}"  accesskey="u">{{title}}</a>
          tmp_element = document.createElement('a');
          tmp_element.setAttribute('data-i18n', title_link.title);
          tmp_element.setAttribute('class', 'ui-btn-icon-left ui-icon-' + title_link.icon);
          tmp_element.setAttribute('href', title_link.url);
          tmp_element.setAttribute('accesskey', 'u');
          promise_list.push(gadget.translateHtml(tmp_element.outerHTML));
        }
      } else {
        promise_list.push(null);
      }

      // Left button
      if (modification_dict.hasOwnProperty('left_button_title') ||
          modification_dict.hasOwnProperty('left_button_icon') ||
          modification_dict.hasOwnProperty('left_button_name')) {
        if (gadget.state.left_button_title === undefined) {
          promise_list.push("");
        } else {
          promise_list.push(gadget.translateHtml(header_button_template({
            title: gadget.state.left_button_title,
            icon: gadget.state.left_button_icon,
            name: gadget.state.left_button_name
          })));
        }
      } else {
        promise_list.push(null);
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
          promise_list.push(gadget.translateHtml(header_button_template(right_button)));
        } else if (right_link !== undefined) {
          // <a data-i18n="{{title}}" href="{{url}}" class="ui-icon-{{icon}} ui-btn-icon-left {{class}}">{{title}}</a>
          tmp_element = document.createElement('a');
          tmp_element.setAttribute('data-i18n', right_link.title);
          tmp_element.setAttribute('class', 'ui-icon-' + right_link.icon + ' ui-btn-icon-left ' + right_link.class);
          tmp_element.setAttribute('href', right_link.url);
          promise_list.push(gadget.translateHtml(tmp_element.outerHTML));
        } else {
          promise_list.push("");
        }
      } else {
        promise_list.push(null);
      }

      // Handle sub header
      if (modification_dict.hasOwnProperty('sub_header_list')) {
        promise_list.push(gadget.translateHtml(sub_header_template({
          sub_header_list: gadget.state.sub_header_list
        })));
      } else {
        promise_list.push(null);
      }

      return new RSVP.Queue(RSVP.all(promise_list))
        .push(function (result_list) {
          var j;
          for (j = 0; j < result_list.length; j += 1) {
            if (result_list[j] !== null) {
              gadget.props.element_list[j].innerHTML = result_list[j];
            }
          }
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

}(window, rJS, document, RSVP));