/*jslint nomen: true, indent: 2, maxerr: 3 */
/*global window, rJS, Handlebars, jQuery, RSVP */
(function (window, rJS, Handlebars, $, RSVP, loopEventListener) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // temlates
  /////////////////////////////////////////////////////////////////
  // Precompile templates while loading the first gadget instance
  var gadget_klass = rJS(window),
    source_header = gadget_klass.__template_element
                         .getElementById("panel-template-header")
                         .innerHTML,
    panel_template_header = Handlebars.compile(source_header),
    source_body = gadget_klass.__template_element
                         .getElementById("panel-template-body")
                         .innerHTML,
    panel_template_body = Handlebars.compile(source_body);

  gadget_klass

    /////////////////////////////////////////////////////////////////
    // ready
    /////////////////////////////////////////////////////////////////
    // Init local properties
    .ready(function (g) {
      g.props = {};
    })

    //////////////////////////////////////////////
    // acquired method
    //////////////////////////////////////////////
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("changeLanguage", "changeLanguage")
    .declareAcquiredMethod("getLanguageList", "getLanguageList")
    .declareAcquiredMethod(
      "whoWantToDisplayThisFrontPage",
      "whoWantToDisplayThisFrontPage"
    )

    // Assign the element to a variable
    .ready(function (g) {
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
          g.props.jelement = $(element.querySelector("div"));
        });
    })

    .ready(function (g) {
      g.props.jelement.panel({
        display: "overlay",
        position: "left",
        theme: "d"
        // animate: false
      });
    })

    .ready(function (g) {
      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            g.whoWantToDisplayThisFrontPage("front"),
            g.whoWantToDisplayThisFrontPage("history"),
            g.getLanguageList()
          ]);
        })
        .push(function (all_result) {
          var raw_language_list = JSON.parse(all_result[2]),
            len = raw_language_list.length,
            i,
            i_len,
            language_list,
            tmp;

          // XXX: Customize panel header!
          tmp = panel_template_header();

          // languages
          if (len > 0) {
            language_list = [];
            for (i = 0, i_len = len; i < i_len; i += 1) {
              language_list.push({"count": i, "lang": language_list[i]});
            }
          }

          tmp += panel_template_body({
            "module_href": all_result[0],
            "history_href": all_result[1],
            "language_list": language_list
          });
          return tmp;
        })
        .push(function (my_translated_or_plain_html) {
          g.props.jelement.html(my_translated_or_plain_html);
          g.props.jelement.trigger("create");
        });
    })

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('toggle', function () {
      this.props.jelement.panel("toggle");
    })

    .declareMethod('render', function () {
      var panel_gadget = this;

      if (panel_gadget.props.set_search === true) {
        return panel_gadget;
      }

      return new RSVP.Queue()
        .push(function () {
          return panel_gadget.declareGadget("gadget_erp5_searchfield.html", {
            "scope": "search"
          });
        })
        .push(function (my_search_gadget) {
          var parent_node, search_option_dict = {};

          panel_gadget.props.set_search = true;

          // XXX disable for now
          search_option_dict.disabled = true;
          search_option_dict.theme = "d";
          search_option_dict.extended_search = "";
          parent_node = panel_gadget.__element.querySelector(".ui-content");

          parent_node.insertBefore(
            my_search_gadget.__element,
            parent_node.firstChild
          );
          return my_search_gadget.render(search_option_dict);
        })
        .push(function () {
          return panel_gadget;
        });
    })

    /////////////////////////////////////////////////////////////////
    // declared services
    /////////////////////////////////////////////////////////////////
    .declareService(function () {
      var panel_gadget,
        form_list,
        event_list,
        handler,
        i,
        len;

      function translate(my_event) {
        return panel_gadget.changeLanguage(my_event.target.lang.value);
      }

      function formSubmit() {
        panel_gadget.toggle();
      }

      panel_gadget = this;
      form_list = panel_gadget.props.element.querySelectorAll('form');
      event_list = [];
      handler = [formSubmit];

      // XXX: not robust - Will break when search field is active
      for (i = 0, len = form_list.length; i < len; i += 1) {
        event_list[i] = loopEventListener(
          form_list[i],
          'submit',
          false,
          handler[i] || translate
        );
      }

      return new RSVP.Queue()
        .push(function () {
          return RSVP.all(event_list);
        });
    });

}(window, rJS, Handlebars, jQuery, RSVP, rJS.loopEventListener));
