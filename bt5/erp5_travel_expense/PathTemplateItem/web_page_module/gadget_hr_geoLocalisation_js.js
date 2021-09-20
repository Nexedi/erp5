/*jslint nomen: true, indent: 2, maxerr: 3 */
/*global window, rJS, Handlebars, RSVP*/
(function (window, rJS, RSVP) {
  "use strict";
  var gadget_klass = rJS(window);
  gadget_klass
    .declareAcquiredMethod("allDocs", "jio_allDocs")
    .declareAcquiredMethod("post", "jio_post")
    .declareAcquiredMethod("remove", "jio_remove")
    .declareMethod('getGeoLocation', function (options) {
      var gadget = this;
      gadget.geoLocation = {coords: {latitude: "", longitude: ""}};
       alertify.log('searching GPS');
       return new RSVP.Queue()
         .push(function () {
           return geoLocationPromise();
         })
        .push(function(result) {
          gadget.geoLocation = result;
          alertify.success('GPS found');
          return gadget.geoLocation;
        }, function(err) {
          alertify.error("GPS Localization Stopped");
          console.log(err);
          gadget.geoLocation =  {coords: {latitude: "", longitude: ""}};
          return gadget.geoLocation;
        });
    })
    .declareMethod('createGeoLocationRecord', function () {
      var gadget = this;
      if (gadget.geoLocation.coords.latitude === "") {
        return;
      }
      return gadget.allDocs({
        query: 'portal_type: Person' ,
        select_list: ['first_name', 'last_name'],
        limit: [0, 1]
        })
        .push(function (result) {
           gadget.author = result.data.rows[0].value.first_name + ' ' + result.data.rows[0].value.last_name;
           return gadget.allDocs({
             query: 'portal_type: "Localisation Record" AND source_title: "' + gadget.author + '"',
             limit: [0, 123456]
           });
        })
        .push(function (result) {
          var i,
            remove_list = [];
          for (i = 0; i < result.data.total_rows; i += 1) {
            remove_list.push(gadget.remove(result.data.rows[i].id));
          }
          return RSVP.all(remove_list);
        })
        .push(function () {
          return gadget.post({
            parent_relative_url: "record_module",
            portal_type: "Localisation Record",
            longitude: gadget.geoLocation.coords.longitude,
            latitude: gadget.geoLocation.coords.latitude,
            source_title: gadget.author,
            simulation_state: 'draft',
            modification_date:new Date().toISOString().slice(0, 10).replace(/-/g, "/")
          });
        });
    });
}(window, rJS, RSVP));
