/*global window, rJS, jIO, RSVP, domsugar, console,
         requestAnimationFrame, cancelAnimationFrame,
         Worker,
         DroneGameManager*/
/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80 */

// game.js
(function (RSVP, requestAnimationFrame, cancelAnimationFrame) {
  "use strict";
  console.log('game');

  //////////////////////////////////////////
  // Webworker
  //////////////////////////////////////////
  function handleWorker(url, callback) {
    var worker;

    function canceller() {
      worker.terminate();
    }

    function resolver(resolve, reject) {
      worker = new Worker(url);

      function handleError(error) {
        canceller();
        reject(error);
      }

      worker.onerror = handleError;
      var result;
      try {
        result = callback(worker);
      } catch (e) {
        return handleError(e);
      }

      new RSVP.Queue(result)
        .push(function (value) {
          canceller();
          console.log('resolve handle worker', value);
          resolve(value);
        }, handleError);
    }
    return new RSVP.Promise(resolver, canceller);
  }

  //////////////////////////////////////////
  // promiseAnimationFrame
  //////////////////////////////////////////
  function promiseAnimationFrame() {
    var request_id;

    function canceller() {
      cancelAnimationFrame(request_id);
    }

    function resolver(resolve) {
      request_id = requestAnimationFrame(resolve);
    }
    return new RSVP.Promise(resolver, canceller);
  }

  //////////////////////////////////////////
  // DroneGameManager
  //////////////////////////////////////////
  function DroneGameManager() {
    if (!(this instanceof DroneGameManager)) {
      return new DroneGameManager();
    }
  }

  DroneGameManager.prototype = {
    constructor: DroneGameManager,
    pause: function pauseGameManager() {
      console.log('pausing', this.loop_promise);
      if (!this.hasOwnProperty('loop_promise')) {
        throw new Error('Can not pause the game if not started');
      }
      if (this.hasOwnProperty('pause_defer')) {
        throw new Error('Can not pause the game if already paused');
      }
      this.pause_defer = RSVP.defer();
      var pause_defer = this.pause_defer;
      this.loop_promise
        .push(function () {
          return pause_defer.promise;
        });
    },
    unpause: function continueGameManager() {
      if (!this.hasOwnProperty('loop_promise')) {
        throw new Error('Can not unpause the game if not started');
      }
      if (!this.hasOwnProperty('pause_defer')) {
        throw new Error('Can not unpause the game if not paused');
      }
      this.pause_defer.resolve('unpause');
      var pause_defer = this.pause_defer;
      delete this.pause_defer;
    },
    quit: function stopGameManager() {
      if (!this.hasOwnProperty('loop_promise')) {
        throw new Error('Can not quit the game if not started');
      }
      this.loop_promise.cancel('Stopping game manager');
      console.log('stopping game manager');
      delete this.loop_promise;
      delete this.pause_defer;
    },
    play: function startGameManager(options) {
      if (this.hasOwnProperty('loop_promise')) {
        throw new Error('Can not start the game if already started');
      }

      this.loop_promise = new RSVP.Queue();
      var loop_promise = this.loop_promise,
        context = this;
      this.pause();

      return RSVP.Queue(RSVP.any([
        loop_promise,
        handleWorker('gadget_erp5_page_game_worker.js', function (worker) {

          var message_error_handler_defer = RSVP.defer(),
            update_defer = null;

          function step() {
            context.loop_promise
              .push(function () {
                console.log('loop step');
                worker.postMessage({
                  type: 'update'
                });
                update_defer = RSVP.defer();
                return RSVP.all([
                  promiseAnimationFrame(),
                  update_defer.promise
                ]);
              })
              .push(function () {
                step();
              });
          }

          console.log('got worker ', worker, options);

          worker.onmessage = function (evt) {
            //console.log('Message received from worker', evt.data);
            var type = evt.data.type;
            if (type === 'loaded') {
              console.log('loaded');
              return worker.postMessage({
                type: 'load_game',
                logic_url: options.logic_url
              });
            }
            if (type === 'load_game_done') {
              console.log('load_game_done');
              context.unpause();
              return step();
            }
            if (type === 'update_done') {
              return update_defer.resolve('update_done');
            }
            message_error_handler_defer.reject(
              new Error('Unsupported message ' + JSON.stringify(evt.data))
            );
          };
          // Always quit the game when the worker callback usage is over
          // to prevent trying to call pause
          //context.quit();
          return message_error_handler_defer.promise;
        })
      ]))
        .push(undefined, function (error) {
          // As the loop_promise will be cancelled at some point when calling
          // quit, we will get a CancellationError as result.
          // This is expected, and play must be successfully resolved
          if (!(error instanceof RSVP.CancellationError)) {
            throw error;
          }
        });
    }
  };

  window.DroneGameManager = DroneGameManager;
}(RSVP, requestAnimationFrame, cancelAnimationFrame));

// droneaailefixe.js
(function () {
  "use strict";
  console.log('droneaailefixe');
}());

// page gadget.js
(function (window, rJS, domsugar, DroneGameManager) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")

    .declareMethod('render', function renderHeader() {
      var gadget = this,
        // XXX hardcoded
        parameter_gamelogic = 'gadget_erp5_page_game_logic.js';

      gadget.runGame({
        logic_url: parameter_gamelogic
      });
      domsugar(gadget.element, {text: 'couscous'});

      return gadget.updateHeader({
        page_title: 'Game',
        page_icon: 'puzzle-piece'
      });
    })

    .declareJob('runGame', function runGame(options) {
      var gadget = this,
        game_manager = DroneGameManager();
      return game_manager.play(options);
    /*
      return RSVP.any([
        RSVP.Queue(game_manager.play(options))
          .push(function (result) {
            console.log('play finished', result);
          }),

        RSVP.Queue(RSVP.delay(1000))
          .push(function () {
            game_manager.pause();
            return RSVP.delay(1000);
          })
          .push(function () {
            game_manager.unpause();
            return RSVP.delay(1000);
          })
          .push(function () {
            game_manager.quit();
          })
      ]);
  */
    });

}(window, rJS, domsugar, DroneGameManager));