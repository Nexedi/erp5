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


// tricky polyfill
/*
console.log("using tricky polyfill");
var document = {
    fullscreen: false,
    mozPointerLockElement: false,
    addEventListener: (e, func) => {},
    createElement: (dom) => {
        return {
            onwheel: () => {}
        }
    }
}

var window = {
    AudioContext: undefined,
    addEventListener: (e, func) => {},
    setTimeout: (func, time) => {
        setTimeout(func, time)
    }
}

var HTMLElement = () => {}*/

// game.js
(function (worker) {
  console.log('worker loading');
  var offscreen_canvas;
  worker.onmessage = function (evt) {
    //console.log('Worker: Message received from main script', evt.data);
    var type = evt.data.type;
    if (type === 'start') {
      console.log('Worker: Message received from main script', evt.data);
      offscreen_canvas = evt.data.canvas;
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
          return runGame(evt.data.canvas, evt.data.script,
                         evt.data.game_parameters_json, evt.data.log);
        })
        .push(function () {
          return worker.postMessage({'type': 'started'});
        });
    }
    if (type === 'update') {
      return new RSVP.Queue()
        .push(function () {
          return updateGame();
        })
        .push(function () {
          return worker.postMessage({'type': 'updated'});
        });
    }
    if (type === 'mousewheel') {
      console.log("[TODO] mousewheel event in WW!!");
      //offscreen_canvas.trigger("mousewheel");
      return eventGame();
      return;
    }
    throw new Error('Unsupported message ' + JSON.stringify(evt.data));
    //self.postMessage('nutnut', evt);
  };
  worker.postMessage({
    'type': 'loaded'
  });
  //throw new Error('argh');
}(this));