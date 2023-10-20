/*jslint nomen: true, indent: 2, maxerr: 3 */
/*global window, rJS, Handlebars, document, RSVP */
(function (window, rJS, Handlebars, document, RSVP) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // Handlebars
  /////////////////////////////////////////////////////////////////
  // Precompile the templates while loading the first gadget instance
  var gadget_klass = rJS(window),
    template_element = gadget_klass.__template_element,

    header_title_template = Handlebars.compile(template_element
                                                 .getElementById("header-title-template")
                                                 .innerHTML),
    header_title_link_template = Handlebars.compile(template_element
                                                      .getElementById("header-title-link-template")
                                                      .innerHTML),
    sub_header_template = Handlebars.compile(template_element
                                               .getElementById("sub-header-template")
                                               .innerHTML),
    header_button_template = Handlebars.compile(template_element
                                                  .getElementById("header-button-template")
                                                  .innerHTML),
    header_link_template = Handlebars.compile(template_element
                                                .getElementById("header-link-template")
                                                .innerHTML),

    possible_left_button_list = [
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
      ['right_url', 'New', 'plus']
    ],
    possible_right_button_list = [
      ['save_action', 'Save', 'check', 'submit'],
      ['submit_action', 'Proceed', 'check', 'submit'],
      ['add_action', 'Add', 'check', 'submit'],
      ['filter_action', 'Filter', 'filter', 'submit'],
      ['refresh_action', 'Refresh', 'refresh', 'submit']
    ],
    possible_sub_header_list = [
      ['tab_url', 'Views', 'eye'],
      ['jump_url', 'Jump', 'plane'],
      ['delete_url', 'Delete', 'times'],
      ['import_url', 'Import', 'upload'],
      ['export_url', 'Export', 'share-square-o'],
      ['actions_url', 'Actions', 'cogs'],
      ['cut_url', 'Cut', 'scissors'],
      ['add_url', 'Add', 'plus'],
      ['previous_url', 'Previous', 'carat-l'],
      ['next_url', 'Next', 'carat-r'],
      ['edit_content', 'Content', 'file-text'],
      ['edit_properties', 'Properties', 'info'],
      ['change_password', 'Change Password', 'pencil-square-o'],
      ['resources_url', 'Resources', 'picture-o'],
      ['processes_url', 'Processes', 'list-alt'],
      ['gadget_url', 'Script', 'puzzle-piece']
    ];

  gadget_klass
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
    .ready(function () {
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

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('notifyLoaded', function () {
      return this.changeState({
        loaded: true
      });
    })
    .declareMethod('notifyLoading', function () {
      return this.changeState({
        loaded: false
      });
    })
    .declareMethod('notifySubmitted', function () {
      return this.changeState({
        submitted: true,
        // Change modify here, to allow user to redo some modification and being correctly notified
        modified: false
      });
    })
    .declareMethod('notifySubmitting', function () {
      return this.changeState({
        submitted: false
      });
    })
    .declareMethod('notifyError', function () {
      return this.changeState({
        loaded: true,
        submitted: true,
        error: true
      });
    })
    .declareMethod('notifyChange', function () {
      return this.changeState({
        modified: true
      });
    })
/*
    .declareMethod('notifyUpdate', function () {
      return this.render(this.stats.options);
    })
*/
    .declareMethod('render', function (options) {
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
      if (options.hasOwnProperty("page_icon")) {
        state.title_icon = options.page_icon;
      }
      for (i = 0; i < possible_main_link_list.length; i += 1) {
        if (options.hasOwnProperty(possible_main_link_list[i][0])) {
          state.title_icon = possible_main_link_list[i][2];
          state.title_url = options[possible_main_link_list[i][0]];
        }
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
          klass = "";
          if (!options[possible_right_link_list[i][0]]) {
            klass = "ui-disabled";
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

    .onStateChange(function (modification_dict) {
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
          modification_dict.hasOwnProperty('title_url')) {
        if (gadget.state.error) {
          default_title_icon = "exclamation";
        } else if (!gadget.state.loaded) {
          default_title_icon = "spinner";
        } else if (!gadget.state.submitted) {
          default_title_icon = "spinner";
        }
        // Updating globally the page title. Does not follow RenderJS philosophy, but, it is enough for now
        document.title = gadget.state.title_text;
        title_link = {
          title: gadget.state.title_text,
          icon: default_title_icon || gadget.state.title_icon,
          url: gadget.state.title_url
        };
        if (title_link.url === undefined) {
          promise_list.push(gadget.translateHtml(header_title_template(title_link)));
        } else {
          promise_list.push(gadget.translateHtml(header_title_link_template(title_link)));
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
          promise_list.push(gadget.translateHtml(header_link_template(right_link)));
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

      return new RSVP.Queue()
        .push(function () {
          return RSVP.all(promise_list);
        })
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
    .onEvent('submit', function (evt) {
      var name = evt.target[0].getAttribute("name");
      if (name === "panel") {
        return this.triggerPanel();
      }
      if (name === "submit") {
        return this.triggerSubmit();
      }
      throw new Error("Unsupported button " + name);
    });

}(window, rJS, Handlebars, document, RSVP));