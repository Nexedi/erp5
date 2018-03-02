/*global window, rJS, RSVP, jIO, URL,
  promiseEventListener, document*/
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, jIO, rJS, RSVP, URL, document, promiseEventListener) {
  "use strict";

  rJS(window)
  .declareAcquiredMethod("jio_get", "jio_get")
  .declareMethod('render', function (params) {
    //console.log(params.value.id);
    var doc = this.jio_get(params.value.id);
    
    console.log(doc);
    //this.element.querySelector("img").setAttribute("src", "Flower.jpg");
  
  });
}(window, jIO, rJS, RSVP, URL, document, promiseEventListener));