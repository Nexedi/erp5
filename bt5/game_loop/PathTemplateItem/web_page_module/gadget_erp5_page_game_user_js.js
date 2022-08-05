/*global me, console*/
/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80 */

(function (me, console) {
  // Every script is evaluated per drone
  "use strict";

  ////////////////////////////////////////
  // Game functions
  ////////////////////////////////////////
  me.onGetMsg = function (msg) {
    console.log('drone onGetMsg', msg);
  };

  me.onStart = function () {
    console.log('drone onStart');
  };

  me.onUpdate = function onUpdate() {
    console.log('drone onUpdate', new Date());
    /*
    var i;
    for (i = 0; i < 100000000000; i += 1) {
      ;
    }
    */
  };

  console.log('user script loaded');
}(me, console));
