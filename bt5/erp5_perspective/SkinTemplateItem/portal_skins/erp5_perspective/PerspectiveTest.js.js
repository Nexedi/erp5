/*global window, document, rJS, worker, console, RSVP, fetch */
/*jslint indent: 2*/
(function (window, rJS, RSVP) {
  "use strict";



  function getStockTimelineData() {
    return new RSVP.Queue()
      .push(function () {
        return fetch("test.csv");
      })
    
      .push(function (resp) {
        return resp.text();
      });
  }





  rJS(window)
    .declareMethod("getData", function () {
      return getStockTimelineData();
    });


}(window, rJS, RSVP));