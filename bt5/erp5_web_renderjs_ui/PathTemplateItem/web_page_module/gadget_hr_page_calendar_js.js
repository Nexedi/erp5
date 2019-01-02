/*global window, rJS, RSVP, Handlebars, calculatePageTitle */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, loopEventListener) {
  "use strict";

  var gadget_klass = rJS(window);
  gadget_klass
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("redirect", "redirect")
    .allowPublicAcquisition("changeUrl", function (options) {
       return this.redirect({
            jio_key: options[0].jio_key,
            page: "view"
          });
     })
    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function (options) {
    })
    .declareService(function () {
      var gadget = this,
        iframe,
        events = [];
      return gadget.declareGadget('gadget_officejs_calendar.html', {
        element: gadget.element.querySelector('.container'),
        sandbox: 'iframe'
      })
      .push(function (calendar) {
        iframe = gadget.element.querySelector('iframe');
        iframe.setAttribute(
            'style',
            'width:100%; border: 0 none; height: 600px'
          );
        return gadget.jio_allDocs({
          query: '(portal_type: "Travel Request Record" AND simulation_state:("draft","sent","stopped")) ' +
                'OR (portal_type: "Leave Request Record" AND simulation_state:("draft","sent","stopped"))',
          select_list: ['title', 'start_date', 'stop_date'],
          limit: [0, 12345678]
        })
        .push(function (result) {
          var i;
          for (i = 0; i < result.data.total_rows; i += 1) {
            events.push({
              title: result.data.rows[i].value.title,
              start: result.data.rows[i].value.start_date,
              end: result.data.rows[i].value.stop_date,
              url: result.data.rows[i].id
            });
          }
          return calendar.render({events: events});
        });
      });
    });
}(window, rJS, RSVP, loopEventListener));