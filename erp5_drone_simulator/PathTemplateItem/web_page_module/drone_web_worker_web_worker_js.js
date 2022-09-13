/*global window, rJS, jIO, RSVP, domsugar, console,
         requestAnimationFrame, cancelAnimationFrame,
         Worker, importScripts,
         DroneGameManager*/
/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80 */
// game.js

var document = {
  addEventListener: function () {},
  createElement: function () {}
};

(function (worker) {
  importScripts('babylon.js', 'babylon.gui.js');
}(this));

var window = {
  addEventListener: function () {}
};

// game.js
(function (worker) {
  console.log('worker loading');
  worker.onmessage = function (evt) {
    //console.log('Worker: Message received from main script', evt.data);
    var type = evt.data.type;
    if (type === 'start') {
      console.log('Worker: Message received from main script', evt.data);
      //override createElement as it is needed by babylon to create a canvas
      document.createElement = function (type) {
        if (type === 'canvas') {
          return evt.data.canvas;
        }
      }
      //TODO evt.data.logic_url should contain the list of scripts
      importScripts(
                    'rsvp.js',
                    'GameManager.js',
                    'DroneManager.js',
                    'MapManager.js',
                    'ObstacleManager.js',
                    'DroneAaileFixeAPI.js',
                    'DroneLogAPI.js',
                    'DroneAPI.js',
                    evt.data.logic_url);
      RSVP = window.RSVP;
      window = undefined;
      return new RSVP.Queue()
        .push(function () {
          return runGame(evt.data.canvas, evt.data.script, evt.data.map, evt.data.log);
        })
        .push(function () {
          return worker.postMessage({'type': 'started'});
        });
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