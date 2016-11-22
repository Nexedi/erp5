/*jslint nomen: true, indent: 2, maxerr: 3 */
/*global window, rJS, Handlebars, RSVP, Node */
(function (window, rJS, Handlebars, RSVP, Node) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // temlates
  /////////////////////////////////////////////////////////////////
  // Precompile templates while loading the first gadget instance
  var gadget_klass = rJS(window),
    template_element = gadget_klass.__template_element,
    panel_template_header = Handlebars.compile(template_element
                         .getElementById("panel-template-header")
                         .innerHTML),
    panel_template_body = Handlebars.compile(template_element
                         .getElementById("panel-template-body")
                         .innerHTML);

  gadget_klass
    //////////////////////////////////////////////
    // acquired method
    //////////////////////////////////////////////
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("translateHtml", "translateHtml")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('toggle', function () {
      this.element.classList.toggle('visible');
    })
    .declareMethod('close', function () {
      if (this.element.classList.contains('visible')) {
        this.element.classList.remove('visible');
      }
    })

    .declareMethod('render', function () {
      var g = this;
      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            g.getUrlFor({command: 'display', options: {page: "front"}}),
            g.getUrlFor({command: 'display', options: {page: "history"}}),
            g.getUrlFor({command: 'display', options: {page: "preference"}}),
            g.getUrlFor({command: 'display', options: {page: "logout"}}),
            g.getUrlFor({command: 'display', options: {page: "search"}}),
            g.getUrlFor({command: 'display', options: {page: "worklist"}})
          ]);
        })
        .push(function (all_result) {
          // XXX: Customize panel header!
          return g.translateHtml(
            panel_template_header() +
            panel_template_body({
              "module_href": all_result[0],
              "history_href": all_result[1],
              "preference_href": all_result[2],
              // "language_list": language_list,
              "logout_href": all_result[3],
              "search_href": all_result[4],
              "worklist_href": all_result[5]
            })
          );
        })
        .push(function (my_translated_or_plain_html) {
          g.element.querySelector("div").innerHTML = my_translated_or_plain_html;
        });
    })

    /////////////////////////////////////////////////////////////////
    // declared services
    /////////////////////////////////////////////////////////////////
    .onEvent('click', function (evt) {
      if ((evt.target.nodeType === Node.ELEMENT_NODE) &&
          (evt.target.tagName === 'BUTTON')) {
        return this.toggle();
      }
    }, false, false);

}(window, rJS, Handlebars, RSVP, Node));
