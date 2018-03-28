/*global window, rJS, RSVP*/
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";
  var gadget_klass = rJS(window);

  gadget_klass
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .setState({
      active_tab: '',
      options_json: ''
    })
    .declareMethod('triggerSubmit', function (param_list) {
      return this.state.active_tab_gadget.triggerSubmit(param_list);
    })
    .allowPublicAcquisition("updateHeader", function () {
      return;
    })
    .declareMethod("render", function (options) {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.getUrlFor({command: 'display', options: {page: 'home', tab: 'rss_reader'}}),
            gadget.getUrlFor({command: 'display', options: {page: 'home', tab: 'links'}}),
            gadget.getUrlFor({command: 'display', options: {page: 'home', tab: 'language'}})
          ]);
        })
        .push(function (result_list) {
          var active_tab = options.tab || 'rss_reader',
            header_dict = {
              language_url : result_list[2],
              page_title : 'Home',
              page_icon : 'home',
              rss_reader_url: result_list[0],
              links_url: result_list[1],
              extra_class: {}
            };
          header_dict.extra_class[active_tab + '_url'] = 'ui-active-tab';
          return RSVP.all([
            gadget.updateHeader(header_dict),
            gadget.changeState({
              active_tab: active_tab,
              options_json: JSON.stringify(options)
            })
          ]);
        });
    })
    .onStateChange(function (modification_dict) {
      var gadget = this;
      if (modification_dict.hasOwnProperty('active_tab')) {
        while (gadget.element.firstChild) {
          gadget.element.removeChild(gadget.element.firstChild);
        }
        return gadget.declareGadget("gadget_erp5_page_" + modification_dict.active_tab + ".html",
                                   {element: gadget.element})
          .push(function (active_tab_gadget) {
            gadget.state.active_tab_gadget = active_tab_gadget;
            return active_tab_gadget.render(JSON.parse(modification_dict.options_json));
          });
      }
      if (modification_dict.hasOwnProperty('options_json')) {
        return gadget.state.active_tab_gadget.render(JSON.parse(modification_dict.options_json));
      }
    });

}(window, rJS, RSVP));