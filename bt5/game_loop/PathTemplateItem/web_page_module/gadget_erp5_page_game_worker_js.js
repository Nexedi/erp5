/*global window, rJS, jIO, RSVP, domsugar, console,
         requestAnimationFrame, cancelAnimationFrame,
         Worker, importScripts,
         DroneGameManager*/
/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80 */

// game.js
(function (worker) {
  "use strict";
  console.log('worker loading');
  worker.onmessage = function (evt) {
    //console.log('Worker: Message received from main script', evt.data);
    var type = evt.data.type;
    if (type === 'load_game') {
      importScripts(evt.data.logic_url);
      return worker.postMessage({'type': 'load_game_done'});
    }
    if (type === 'update') {
      var i;
      for (i = 0; i < 100000000; i += 1) {
        1+1;
      }
      return worker.postMessage({'type': 'update_done'});
    }
    throw new Error('Unsupported message ' + JSON.stringify(evt.data));
    //self.postMessage('nutnut', evt);
  };
  worker.postMessage({
    'type': 'loaded'
  });
  //throw new Error('argh');
}(this));