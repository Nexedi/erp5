/*global window, document, rJS, worker, console, RSVP, fetch */
/*jslint indent: 2*/
(function (window, rJS, RSVP) {
  "use strict";



  function getStockTimelineData() {
    return new RSVP.Queue()
      .push(function () {
      console.log("herlo");


        return "heelloooo";
      })
    /*
      .push(function (resp) {
        return resp.arrayBuffer();
      });
*/
  }





  rJS(window)
    .declareMethod("getData", function () {
    console.log("jkhjhkjkh");
      return getStockTimelineData();
    });


}(window, rJS, RSVP));