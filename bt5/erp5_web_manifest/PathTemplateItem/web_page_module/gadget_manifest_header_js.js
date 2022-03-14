/*jslint nomen: true, indent: 2, maxerr: 3 */
/*global window, rJS, Handlebars, document, RSVP */
(function (window, rJS, Handlebars, document, loopEventListener, RSVP) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // Handlebars
  /////////////////////////////////////////////////////////////////
  // Precompile the templates while loading the first gadget instance
  var gadget_klass = rJS(window),

    header_title_source = gadget_klass.__template_element
                         .getElementById("header-title-template")
                         .innerHTML,
    header_title_template = Handlebars.compile(header_title_source),

    header_title_link_source = gadget_klass.__template_element
                         .getElementById("header-title-link-template")
                         .innerHTML,
    header_title_link_template = Handlebars.compile(header_title_link_source),

    sub_header_source = gadget_klass.__template_element
                         .getElementById("sub-header-template")
                         .innerHTML,
    sub_header_template = Handlebars.compile(sub_header_source),

    header_button_source = gadget_klass.__template_element
                         .getElementById("header-button-template")
                         .innerHTML,
    header_button_template = Handlebars.compile(header_button_source),
    header_link_source = gadget_klass.__template_element
                         .getElementById("header-link-template")
                         .innerHTML,
    header_link_template = Handlebars.compile(header_link_source);

  gadget_klass
    /////////////////////////////////////////////////////////////////
    // ready
    /////////////////////////////////////////////////////////////////
    // Init local properties
    .ready(function (g) {
      g.props = {};
      g.stats = {
        loaded: false,
        modified: false,
        submitted: true,
        error: false,
        options: {}
      };
    })

    // Assign the element to a variable
    .ready(function (g) {
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
          g.props.sub_header_element = element.querySelector(".ui-subheader");
          g.props.sub_header_ul = g.props.sub_header_element.querySelector("ul");
          g.props.left_link = element.querySelector(".ui-btn-left > div");
          g.props.right_link = element.querySelector(".ui-btn-right > div");
          g.props.title_element = element.querySelector("h1");
        });
    })

    .ready(function (g) {
      return g.render(g.stats.options);
    })

    //////////////////////////////////////////////
    // acquired methods
    //////////////////////////////////////////////
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("whoWantToDisplayThis", "whoWantToDisplayThis")
    .declareAcquiredMethod("triggerSubmit", "triggerSubmit")
    .declareAcquiredMethod("triggerPanel", "triggerPanel")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('notifyError', function () {
      this.stats.loaded = true;
      this.stats.submitted = true;
      this.stats.error = true;
      var gadget = this;
      return this.render(this.stats.options)
        .push(function () {
          gadget.stats.error = false;
        });
    })
    .declareMethod('notifyUpdate', function () {
      return this.render(this.stats.options);
    })
    .declareMethod('notifyLoading', function () {
      if (this.stats.loaded) {
        this.stats.loaded = false;
        return this.render(this.stats.options);
      }
    })
    .declareMethod('notifyLoaded', function () {
      if (!this.stats.loaded) {
        this.stats.loaded = true;
        return this.render(this.stats.options);
      }
    })
    .declareMethod('notifyChange', function () {
      if (!this.stats.modified) {
        this.stats.modified = true;
        return this.render(this.stats.options);
      }
    })
    .declareMethod('notifySubmitting', function () {
      if (this.stats.submitted) {
        this.stats.submitted = false;
        return this.render(this.stats.options);
      }
    })
    .declareMethod('notifySubmitted', function () {
      if (!this.stats.submitted) {
        this.stats.submitted = true;
        // Change modify here, to allow user to redo some modification and being correctly notified
        this.stats.modified = false;
        return this.render(this.stats.options);
      }
    })
    .declareMethod('render', function (options) {
      var gadget = this,
        possible_left_link_list = [
          // ['menu_url', 'Menu', 'bars'],
          ['selection_url', 'Back', 'arrow-left'],
          ['view_url', 'View', 'check'],
          ['cancel_url', 'Cancel', 'times'],
          ['back_url', 'Back', 'arrow-left']
        ],
        possible_left_button_list = [
          ['panel_action', 'Menu', 'bars', 'panel']
        ],
        possible_right_link_list = [
          ['edit_url', 'Edit', 'pencil']
        ],
        possible_right_button_list = [
          ['save_action', 'Save', 'check', 'submit'],
          ['submit_action', 'Proceed', 'check', 'submit']
        ],
        possible_sub_header_list = [
          ['tab_url', 'Tabs', 'eye'],
          ['jump_url', 'Jump', 'plane'],
          ['delete_url', 'Delete', 'times'],
          ['export_url', 'Export', 'share-square-o'],
          ['actions_url', 'Actions', 'cogs'],
          ['cut_url', 'Cut', 'scissors'],
          ['add_url', 'Add', 'plus'],
          ['previous_url', 'Previous', 'carat-l'],
          ['next_url', 'Next', 'carat-r']
        ],
        i,
        klass,
        count = 0,
        //left_link = {
        //  title: "Menu",
        //  icon: "bars",
        //  url: "#leftpanel",
          // class: "ui-disabled"
        // },
        left_link,
        left_button,
        right_link,
        right_button,
        default_right_text,
        default_right_icon = "",
        title_link = {},
        sub_header_list = [],
        alphabet = "abcdefghijklmnopqrstuvwxyz",
        promise_list = [];

      gadget.stats.options = options;
      // Handle main title
      if (options.hasOwnProperty("page_title")) {
        title_link.title = options.page_title;
        // Updating globally the page title. Does not follow RenderJS philosophy, but, it is enough for now
        document.title = title_link.title;
      }
      if (options.hasOwnProperty("breadcrumb_url")) {
        title_link.url = options.breadcrumb_url;
        promise_list.push(gadget.translateHtml(header_title_link_template(title_link)));
      } else {
        promise_list.push(gadget.translateHtml(header_title_template(title_link)));
      }

      // Handle left link
      for (i = 0; i < possible_left_link_list.length; i += 1) {
        if (options.hasOwnProperty(possible_left_link_list[i][0])) {
          klass = "";
          if (!options[possible_left_link_list[i][0]]) {
            klass = "ui-disabled";
          }
          left_link = {
            title: possible_left_link_list[i][1],
            icon: possible_left_link_list[i][2],
            url: options[possible_left_link_list[i][0]],
            class: klass
          };
        }
      }
      for (i = 0; i < possible_left_button_list.length; i += 1) {
        if (options.hasOwnProperty(possible_left_button_list[i][0])) {
          left_button = {
            title: possible_left_button_list[i][1],
            icon: possible_left_button_list[i][2],
            name: possible_left_button_list[i][3]
          };
        }
      }
      if (left_button !== undefined) {
        promise_list.push(gadget.translateHtml(header_button_template(left_button)));
      } else if (left_link === undefined) {
        promise_list.push(gadget.translateHtml(""));
      } else {
        promise_list.push(gadget.translateHtml(header_link_template(left_link)));
      }

      // Handle right link
      if (gadget.stats.error) {
        default_right_icon = "exclamation";
      } else if (!gadget.stats.loaded) {
        default_right_icon = "spinner";
        // Show default loading information
        right_link = {
          title: "Loading",
          icon: default_right_icon,
          url: "",
          class: "ui-disabled ui-icon-spin"
        };
      } else if (!gadget.stats.submitted) {
        default_right_icon = "spinner";
      } else if (gadget.stats.modified) {
        default_right_text = "Save";
        default_right_icon = "warning";
      }
      for (i = 0; i < possible_right_link_list.length; i += 1) {
        if (options.hasOwnProperty(possible_right_link_list[i][0])) {
          klass = "";
          if (!options[possible_right_link_list[i][0]]) {
            klass = "ui-disabled";
          }
          right_link = {
            title: possible_right_link_list[i][1],
            icon: default_right_icon || possible_right_link_list[i][2],
            url: options[possible_right_link_list[i][0]],
            class: klass
          };
        }
      }
      for (i = 0; i < possible_right_button_list.length; i += 1) {
        if (options.hasOwnProperty(possible_right_button_list[i][0])) {
          right_button = {
            title: default_right_text || possible_right_button_list[i][1],
            icon: default_right_icon || possible_right_button_list[i][2],
            name: possible_right_button_list[i][3]
          };
          if (gadget.stats.error) {
            right_button.class = "ui-disabled";
          }
        }
      }
      if (right_button !== undefined) {
        promise_list.push(gadget.translateHtml(header_button_template(right_button)));
      } else if (right_link !== undefined) {
        promise_list.push(gadget.translateHtml(header_link_template(right_link)));
      } else {
        promise_list.push(gadget.translateHtml(""));
      }

      // Handle sub header
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
            class: klass,
            block: alphabet.charAt(count)
          });
          count += 1;
        }
      }

      if (sub_header_list.length !== 0) {
        sub_header_list[0].class += " ui-first-child";
        sub_header_list[sub_header_list.length - 1].class += " ui-last-child";
      }
      // gadget.props.sub_header_ul.textContent = JSON.stringify(options);
      //gadget.props.sub_header_ul.innerHTML = sub_header_template({
      //  sub_header_list: sub_header_list
      //});

      promise_list.push(gadget.translateHtml(sub_header_template({
        sub_header_list: sub_header_list
      })));

      return new RSVP.Queue()
        .push(function () {
          return RSVP.all(promise_list);
        })
        .push(function (my_translated_html_list) {
          gadget.props.title_element.innerHTML = my_translated_html_list[0];
          gadget.props.left_link.innerHTML = my_translated_html_list[1];
          gadget.props.right_link.innerHTML = my_translated_html_list[2];
          gadget.props.sub_header_ul.innerHTML = my_translated_html_list[3];
        });
    })

    //////////////////////////////////////////////
    // handle button click
    //////////////////////////////////////////////
    .declareService(function () {
      var form_gadget = this;

      function formSubmit(evt) {
        var button = evt.target[0],
          name = button.getAttribute("name");
        if (name === "panel") {
          return form_gadget.triggerPanel();
        }
        if (name === "submit") {
          return form_gadget.triggerSubmit();
        }
        throw new Error("Unsupported button " + name);
      }

      // Listen to form submit
      return loopEventListener(
        form_gadget.props.element,
        'submit',
        false,
        formSubmit
      );
    });

}(window, rJS, Handlebars, document, rJS.loopEventListener, RSVP));