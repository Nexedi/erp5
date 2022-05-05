/*jslint nomen: true, indent: 2, maxerr: 3 */
/*global window, rJS, Handlebars, RSVP*/
(function (window, rJS, RSVP, L) {
  "use strict";
  var gadget_klass = rJS(window);
  gadget_klass
    .declareMethod('render', function (data_list) {
      var gadget = this,
        i,
        group,
        popup_string,
        marker,
        mymap = L.map('mapid'),
        marker_list = [],
        myIcon = L.icon({
         iconUrl: 'image_module/marker-icon',
         iconSize: [35, 50],
         iconAnchor:  [23, 47],
         popupAnchor: [-3, -44],
         shadowUrl: 'image_module/marker-shadow',
         shadowSize: [65, 50],
         shadowAnchor: [23, 47]
      });
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
     }).addTo(mymap);
      for (i = 0; i < data_list.length; i += 1) {
        try {
           if (data_list[i].href) {
             popup_string = '<a href='+ data_list[i].href + '>' + data_list[i].title + '</a>'
           } else {
             popup_string = data_list[i].title;
           }
           marker = new L.marker([data_list[i].coordinate_list[0], data_list[i].coordinate_list[1]], {icon: myIcon});
           marker.addTo(mymap)
           .bindPopup(popup_string, {autoClose:true, closeOnClick: false, maxWidth : 150});
           marker_list.push(marker);
        } catch(error) {
          console.log(error);
          console.log(data_list[i]);
        }
      }
      if (marker_list.length > 1) {
        group = new L.featureGroup(marker_list);
        mymap.fitBounds(group.getBounds());
      } else {
        if (marker_list.length == 1) {
          mymap.setView([marker_list[0]._latlng.lat, marker_list[0]._latlng.lng], 9);
        } else {
          mymap.setView([48.85749, 2.35107], 13);
        }
      }
    });
}(window, rJS, RSVP, L));
