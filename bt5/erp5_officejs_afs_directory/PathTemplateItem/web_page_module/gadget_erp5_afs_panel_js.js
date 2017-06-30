/*jslint indent: 2, nomen: true, maxlen: 80*/
/*global window, Node, rJS, Handlebars, RSVP, loopEventListener */
(function (window, Node, rJS, Handlebars, RSVP, loopEventListener) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // some variables
  /////////////////////////////////////////////////////////////////
  var gadget_klass = rJS(window),
    source_header = gadget_klass.__template_element
                         .getElementById("panel-template-header").innerHTML,
    panel_template_header = Handlebars.compile(source_header),
    source_body = gadget_klass.__template_element
                         .getElementById("panel-template-body").innerHTML,
    panel_template_body = Handlebars.compile(source_body);

  /////////////////////////////////////////////////////////////////
  // some methods
  /////////////////////////////////////////////////////////////////
  function getUrlDict(param) {
    return {command: 'display', options: {page: param}};
  }

  gadget_klass

    /////////////////////////////////////////////////////////////////
    // state
    /////////////////////////////////////////////////////////////////
    .setState({
      visible: false,
      desktop: false
    })

    .onStateChange(function (modification_dict) {
      var gadget = this;

      if (modification_dict.hasOwnProperty("visible")) {
        if (gadget.state.visible) {
          if (!gadget.element.classList.contains('visible')) {
            gadget.element.classList.toggle('visible');
          }
        } else {
          if (gadget.element.classList.contains('visible')) {
            gadget.element.classList.remove('visible');
          }
        }
      }
    })

    //////////////////////////////////////////////
    // acquired methods
    //////////////////////////////////////////////
    .declareAcquiredMethod("getUrlFor", "getUrlFor")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('toggle', function () {
      return this.changeState({
        visible: !this.state.visible
      });
    })

    .declareMethod('close', function () {
      return this.changeState({
        visible: false
      });
    })

    .declareMethod('render', function () {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.getUrlFor(getUrlDict("afs_directory")),
            gadget.getUrlFor(getUrlDict("afs_publisher_statistic")),
            gadget.getUrlFor(getUrlDict("afs_publisher_list")),
            gadget.getUrlFor(getUrlDict("afs_software_list")),
            gadget.getUrlFor(getUrlDict("afs_success_case_list"))
          ]);
        })
        .push(function (result_list) {
          var content = panel_template_header();

          content += panel_template_body({
            "directory_href": result_list[0],
            "publisher_statistic_href": result_list[1],
            "publisher_href": result_list[2],
            "software_href": result_list[3],
            "success_case_href": result_list[4]
          });

          gadget.element.querySelector("div").innerHTML = content;
        });
    })

    /////////////////////////////////////////////////////////////////
    // declared jobs
    /////////////////////////////////////////////////////////////////
    .declareJob('listenResize', function () {

      // resize should be only trigger after the render method as displaying 
      // the panel rely on external gadget (for translation for example)
      var result,
        event,
        context = this;

      function extractSizeAndDispatch() {
        if (window.matchMedia("(min-width: 85em)").matches) {
          return context.changeState({desktop: true});
        }
        return context.changeState({desktop: false});
      }
      result = loopEventListener(window, 'resize', false,
                                 extractSizeAndDispatch);
      event = window.document.createEvent("Event");
      event.initEvent('resize', true, true);
      window.dispatchEvent(event);
      return result;
    })

    /////////////////////////////////////////////////////////////////
    // event handlers
    /////////////////////////////////////////////////////////////////
    .onEvent('click', function (evt) {
      if ((evt.target.nodeType === Node.ELEMENT_NODE) &&
          (evt.target.tagName === 'BUTTON')) {
        return this.toggle();
      }
    }, false, false)

    .onEvent('blur', function (evt) {

      // XXX Horrible hack to clear the search when focus is lost
      // This does not follow renderJS design, as a gadget should not touch
      // another gadget content
      if (evt.target.type === 'search') {
        evt.target.value = "";
      }
    }, true, false);

}(window, Node, rJS, Handlebars, RSVP, loopEventListener));
