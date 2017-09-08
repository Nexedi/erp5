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
      ['filter_action', 'Filter', 'filter', 'submit']
    ],
    possible_sub_header_list = [
      ['tab_url', 'Views', 'eye'],
      ['jump_url', 'Jump', 'plane'],
      ['delete_url', 'Delete', 'times'],
      ['export_url', 'Export', 'share-square-o'],
      ['actions_url', 'Actions', 'cogs'],
      ['cut_url', 'Cut', 'scissors'],
      ['add_url', 'Add', 'plus'],
      ['previous_url', 'Previous', 'carat-l'],
      ['next_url', 'Next', 'carat-r'],
      ['edit_content', 'Content', 'file-text'],
      ['edit_properties', 'Properties', 'info']
    ];

  gadget_klass
    .setState({
      loaded: false,
      modified: false,
      submitted: true,
      error: false,
      // links compose from "text", "icon", "url" and optionally "class"
      // buttons compose from "title", "icon", "name"
      main_link: {},
      left_button: {},
      // right button and right link are exclusive!
      right_button: {},
      right_link: {}
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
    .declareMethod('render', function (options) {
      var gadget = this,
        state = {
          "error": options.error || false
        },
        klass,
        sub_header_list = [],
        i;

      if (options.hasOwnProperty("page_title")) {
        // if a new page title is specified then we are displaying different
        // view so we force-reload all menu buttons
        state.main_link = {};
        state.right_link = {};
        state.right_button = {};
        state.left_button = {};
      }

      // Main title
      if (options.hasOwnProperty("page_title") || options.hasOwnProperty("page_icon")) {
        state.main_link = {
          "title": options.page_title || gadget.state.main_link.title,
          "icon": options.page_icon || gadget.state.main_link.icon,
          "url": ''
        };
        for (i = 0; i < possible_main_link_list.length; i += 1) {
          if (options.hasOwnProperty(possible_main_link_list[i][0])) {
            state.main_link.icon = possible_main_link_list[i][2];
            state.main_link.url = options[possible_main_link_list[i][0]];
          }
        }
      }

      // Left button
      for (i = 0; i < possible_left_button_list.length; i += 1) {
        if (options.hasOwnProperty(possible_left_button_list[i][0])) {
          state.left_button = {
            "title": possible_left_button_list[i][1],
            "icon": possible_left_button_list[i][2],
            "name": possible_left_button_list[i][3]
          };
        }
      }

      // Handle right link
      for (i = 0; i < possible_right_link_list.length; i += 1) {
        if (options.hasOwnProperty(possible_right_link_list[i][0])) {
          state.right_link = {
            "title": possible_right_link_list[i][1],
            "icon": possible_right_link_list[i][2],
            "url": options[possible_right_link_list[i][0]],
            "class": ""
          };
          if (!options[possible_right_link_list[i][0]]) {
            state.right_link["class"] = "ui-disabled";
          }
          state.right_button = {}; // because right link and button are exclusive
        }
      }
      for (i = 0; i < possible_right_button_list.length; i += 1) {
        if (options.hasOwnProperty(possible_right_button_list[i][0])) {
          state.right_button = {
            "title": possible_right_button_list[i][1],
            "icon": possible_right_button_list[i][2],
            "name": possible_right_button_list[i][3]
          };
          state.right_link = {}; // because right link and button are exclusive
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
            "title": possible_sub_header_list[i][1],
            "icon": possible_sub_header_list[i][2],
            "url": options[possible_sub_header_list[i][0]],
            "class": klass
          });
        }
      }
      state.sub_header_list = sub_header_list;

      return this.changeState(state);
    })

    .onStateChange(function (modification_dict) {
      var gadget = this,
        default_title_icon = "",
        default_right_icon = "",
        main_link,
        promise_list = [];

      // insert "title" HTML text promise into promise_list[0]
      if (modification_dict.hasOwnProperty('error') ||
          modification_dict.hasOwnProperty('loaded') ||
          modification_dict.hasOwnProperty('submitted') ||
          modification_dict.hasOwnProperty('main_link')) {
        if (gadget.state.error) {
          default_title_icon = "exclamation";
        } else if (!gadget.state.loaded) {
          default_title_icon = "spinner";
        } else if (!gadget.state.submitted) {
          default_title_icon = "spinner";
        }
        // Updating globally the page title. Does not follow RenderJS philosophy, but, it is enough for now
        document.title = gadget.state.main_link.title;
        // Update icon in case an action in process (keep the original in state.title_icon)
        main_link = {
          "title": gadget.state.main_link.title,
          "icon": default_title_icon || gadget.state.main_link.icon,
          "url": gadget.state.main_link.url
        };

        if (main_link.url) {
          promise_list.push(gadget.translateHtml(header_title_link_template(main_link)));
        } else {
          promise_list.push(gadget.translateHtml(header_title_template(main_link)));
        }
      } else {
        promise_list.push(null);
      }

      // insert "left button" HTML text promise into promise_list[1]
      if (modification_dict.hasOwnProperty('left_button')) {
        if (gadget.state.left_button.title === undefined) {
          promise_list.push("");
        } else {
          promise_list.push(
            gadget.translateHtml(
              header_button_template(gadget.state.left_button)
            )
          );
        }
      } else {
        promise_list.push(null);
      }

      // insert "left link" HTML text promise into promise_list[2]
      if (modification_dict.hasOwnProperty('loaded') ||
          modification_dict.hasOwnProperty('submitted') ||
          modification_dict.hasOwnProperty('modified') ||
          modification_dict.hasOwnProperty('right_link') ||
          modification_dict.hasOwnProperty('right_button')) {
        // find the right right icon
        if (gadget.state.modified) {
          default_right_icon = "warning";
        }
        if (gadget.state.error || !gadget.state.loaded || !gadget.state.submitted) {
          default_right_icon = "ui-disabled";
        }
        // render the right right thing
        if (gadget.state.right_button.title) {
          promise_list.push(gadget.translateHtml(header_button_template({
            "title": gadget.state.right_button.title,
            "icon": default_right_icon || gadget.state.right_button.icon,
            "name": gadget.state.right_button.name
          })));
        } else if (gadget.state.right_link.title) {
          promise_list.push(gadget.translateHtml(header_link_template(gadget.state.right_link)));
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