/*jslint nomen: true, indent: 2, maxerr: 3, unparam: true */
/*global window, document, rJS, RSVP, Node, domsugar */
(function (window, document, rJS, RSVP, Node, domsugar) {
  "use strict";

  rJS(window)
    .setState({
      visible: false
    })
    .declareAcquiredMethod("getUrlForList", "getUrlForList")
    .declareAcquiredMethod("getTranslationList", "getTranslationList")
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
      var visible = options.visible,
        context = this;

      if (visible === undefined) {
        visible = context.state.visible;
      }
      return context.getUrlParameter('editable')
        .push(function (editable) {
          return context.changeState({
            visible: visible,
            global: true,
            editable: editable
          });
        });
    })
    .onStateChange(function onStateChange(modification_dict) {
      var i,
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

      if (modification_dict.hasOwnProperty("editable")) {
        queue
          .push(function () {
            return RSVP.hash({
              url_list: gadget.getUrlForList([
                {command: 'display', options: {page: "ojs_harness_ai_homepage"}},
                {command: 'display'},
                {command: 'display', options: {page: "ojs_harness_ai_setting"}}
              ]),
              translation_list: gadget.getTranslationList([
                'New Artificial Task',
                'Artificial Task Module',
                'Setting'
              ])
            });
          })
          .push(function (result_dict) {
            var element_list = [],
              icon_and_key_list = [
                'home', null,
                'clipboard', null,
                'sliders', 's'
              ];

            for (i = 0; i < result_dict.url_list.length; i += 1) {
              element_list.push(domsugar('li', [
                domsugar('a', {
                  href: result_dict.url_list[i],
                  'class': 'ui-btn-icon-left ui-icon-' + icon_and_key_list[2 * i],
                  accesskey: icon_and_key_list[2 * i + 1],
                  text: result_dict.translation_list[i]
                })
              ]));
            }
            domsugar(gadget.element.querySelector("ul"),
                     [domsugar(null, element_list)]);
          });
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

    .allowPublicAcquisition("notifyFocus", function notifyFocus() {
      return;
    })
    .allowPublicAcquisition("notifyBlur", function notifyFocus() {
      return;
    })
    .allowPublicAcquisition('notifyChange', function notifyChange() {
      return;
    }, {mutex: 'changestate'})
    .allowPublicAcquisition('notifyValid', function notifyValid() {
      return;
    });

}(window, document, rJS, RSVP, Node, domsugar));
