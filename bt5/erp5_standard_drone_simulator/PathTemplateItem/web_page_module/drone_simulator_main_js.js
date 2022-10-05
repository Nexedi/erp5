/*global window, rJS, jIO, RSVP, domsugar, console,
         requestAnimationFrame, cancelAnimationFrame,
         Worker,
         DroneGameManager*/
/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80 */

// game.js
(function (RSVP, requestAnimationFrame, cancelAnimationFrame) {
  "use strict";

	// Events props to send to worker
	var mouseEventFields = new Set(['altKey', 'bubbles', 'button', 'buttons',
		'cancelBubble', 'cancelable', 'clientX', 'clientY', 'composed', 'ctrlKey',
		'defaultPrevented', 'detail', 'eventPhase', 'fromElement', 'isTrusted',
		'layerX', 'layerY', 'metaKey', 'movementX', 'movementY', 'offsetX', 'pageX',
		'offsetY', 'pageY', 'relatedTarget', 'returnValue', 'screenX', 'screenY',
		'shiftKey', 'timeStamp', 'type', 'which', 'x', 'wheelDelta', 'wheelDeltaX',
		'wheelDeltaY', 'y', 'deltaX', 'deltaY', 'deltaZ', 'deltaMode'
	]);

  var game_result;

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
    result: function resultGameManager() {
      return game_result;
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
        handleWorker('gadget_erp5_page_drone_simulator_web_worker.js', function (worker) {

          var message_error_handler_defer = RSVP.defer(),
            update_defer = null;

          worker.onmessage = workerToMain;
          // Always quit the game when the worker callback usage is over
          // to prevent trying to call pause
          return message_error_handler_defer.promise;

          function workerToMain(evt) {
            switch (evt.data.type) {
              case 'loaded':
                return worker.postMessage({
                  type: 'start',
                  logic_url_list: options.logic_url_list,
                  canvas: options.canvas,
                  width: options.width,
                  height: options.height,
                  script: options.script,
                  game_parameters: options.game_parameters,
                  log: options.log
                }, [options.canvas]);
                break;
              case 'started':
                console.log('GAME: started');
                context.unpause();
                return step();
                break;
              case 'updated':
                return update_defer.resolve('updated');
                break;
              case 'finished':
                console.log('GAME: finished');
                game_result = evt.data.result;
                return context.quit();
                break;
              case 'event':
                bindEvent(evt.data);
                break;
              case 'canvasMethod':
                options.canvas_original[evt.data.method](...evt.data.args);
                break;
              case 'canvasStyle':
                options.canvas_original.style[evt.data.name] = evt.data.value;
                break;
              case 'error':
                message_error_handler_defer.reject(evt.data.error);
                break;
              default:
                message_error_handler_defer.reject(
                  new Error('Unsupported message ' + JSON.stringify(evt.data))
                );
            }
          };

          function step() {
            context.loop_promise
              .push(function () {
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

          function bindEvent(data) {
            let target;
            switch (data.targetName) {
              case 'window':
                target = window;
                break;
              case 'canvas':
                target = options.canvas_original;
                break;
              case 'document':
                target = document;
                break;
            }
            if (!target) {
              console.error('Unknown target: ' + data.targetName);
              return;
            }
            target.addEventListener(data.eventName, function (e) {
              // We can`t pass original event to the worker
              const eventClone = cloneEvent(e);
              if (eventClone.type === "pointerout") {
                return;
              }
              worker.postMessage({
                type: 'event',
                targetName: data.targetName,
                eventName: data.eventName,
                eventClone: eventClone,
              });
            }, data.opt);
          }

          function cloneEvent(event) {
            event.preventDefault();
            const eventClone = {};
            for (let field of mouseEventFields) {
              eventClone[field] = event[field];
            }
            return eventClone;
          }
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