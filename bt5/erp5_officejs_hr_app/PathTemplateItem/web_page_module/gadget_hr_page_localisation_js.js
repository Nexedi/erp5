/*jslint nomen: true, indent: 2, maxerr: 3 */
/*global window, rJS, Handlebars, RSVP*/
(function (window, rJS, RSVP, L) {
  "use strict";
  var gadget_klass = rJS(window);
  gadget_klass
    .declareAcquiredMethod("allDocs", "jio_allDocs")
    .declareMethod('render', function () {
      var gadget = this;
      return gadget.allDocs({
        query: 'portal_type: "Localisation Record"',
        select_list: ['longitude', 'latitude', 'source_title', 'creation_date'],
        limit: [0, 12345678]
      })
      .push(function (result) {
        gadget.geo_doc = result.data;
      });
    })
    .declareService(function () {
      var gadget = this,
        i,
        group,
        marker,
        mymap = L.map('mapid'),
        marker_list = [],
        myIcon = L.icon({
         iconUrl: 'image_module/marker-icon?format=png',
         iconSize: [35, 50],
         iconAnchor:  [23, 47],
         popupAnchor: [-3, -44],
         shadowUrl: 'image_module/marker-shadow?format=png',
         shadowSize: [65, 50],
         shadowAnchor: [23, 47]
      });
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
     }).addTo(mymap);
      for (i = 0; i < gadget.geo_doc.total_rows; i += 1) {
         marker = new L.marker([gadget.geo_doc.rows[i].value.latitude, gadget.geo_doc.rows[i].value.longitude], {icon: myIcon});
         marker.addTo(mymap)
         .bindPopup(gadget.geo_doc.rows[i].value.creation_date + ":" + gadget.geo_doc.rows[i].value.source_title, {autoClose:false, closeOnClick: false, maxWidth : 150});
         marker_list.push(marker);
      }
      if (marker_list.length) {
        group = new L.featureGroup(marker_list);
        mymap.fitBounds(group.getBounds());
        for (i = 0; i < marker_list.length; i += 1) {
          marker_list[i].openPopup();
        }
      } else {
        mymap.setView([48.85749, 2.35107], 13);
      }
    });
}(window, rJS, RSVP, L));
