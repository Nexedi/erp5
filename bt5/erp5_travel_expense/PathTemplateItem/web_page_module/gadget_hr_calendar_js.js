/*global window, rJS, RSVP, Handlebars, calculatePageTitle */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // Handlebars
  /////////////////////////////////////////////////////////////////
  // Precompile the templates while loading the first gadget instance
  var gadget_klass = rJS(window);
  gadget_klass
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("changeUrl", "changeUrl")
    .declareAcquiredMethod("getSetting", "getSetting")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function (options) {
      var gadget = this,
        data = {
          fr: {
            listDay: 'Jour',
            listWeek:'Semaine'},
          en: {
            listDay: 'Day',
            listWeek:'Week'
          }
        },
        calendar_options = {
          header: {
            left: 'prev,next today',
            center: 'title',
            right: 'listDay,listWeek,month'
          },
          height: "auto",
          aspectRatio: 0.7,
          contentHeight: "auto",
          // customize the button names,
          // otherwise they'd all just say "list"
          views: {
           listDay: { buttonText: 'listDay' },
           listWeek: { buttonText: 'listWeek' }
          },
          eventClick: function(event) {
            if (event.url) {
             //xxx should return false to prevent url change
             //https://fullcalendar.io/docs/mouse/eventClick/
              gadget.changeUrl({jio_key: event.url});
              return false;
            }
          },
          defaultView: 'month',
          navLinks: true, // can click day/week names to navigate views
          editable: true,
          eventLimit: true, // allow "more" link when too many events
          events: options.events
     };
     return gadget.getSetting('selected_language')
      .push(function (lang) {
        calendar_options.locale = lang;
        calendar_options.buttonText = data[lang] || data.en;
        $('#calendar').fullCalendar(calendar_options);
       });
  });
}(window, rJS, RSVP));