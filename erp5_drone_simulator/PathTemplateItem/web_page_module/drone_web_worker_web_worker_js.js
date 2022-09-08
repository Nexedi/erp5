/*global window, rJS, jIO, RSVP, domsugar, console,
         requestAnimationFrame, cancelAnimationFrame,
         Worker, importScripts,
         DroneGameManager*/
/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80 */

// game.js
(function (worker) {
  "use strict";
  var window = {};
  console.log('worker loading');
  worker.onmessage = function (evt) {
    //console.log('Worker: Message received from main script', evt.data);
    var type = evt.data.type;
    if (type === 'start') {
      console.log('Worker: Message received from main script', evt.data);

      importScripts('babylon.js',
                    'GameManager.js',
                    'DroneManager.js',
                    'MapManager.js',
                    'ObstacleManager.js',
                    'DroneAaileFixeAPI.js',
                    'DroneLogAPI.js',
                    'DroneAPI.js',
                    evt.data.logic_url);
      runGame(evt.data.canvas, evt.data.script, evt.data.map, evt.data.log);
      return worker.postMessage({'type': 'started'});
    }
    if (type === 'update') {
      var i;
      for (i = 0; i < 100000000; i += 1) {
        1+1;
      }
      return worker.postMessage({'type': 'updated'});
    }
    throw new Error('Unsupported message ' + JSON.stringify(evt.data));
    //self.postMessage('nutnut', evt);
  };
  worker.postMessage({
    'type': 'loaded'
  });
  //throw new Error('argh');
}(this));