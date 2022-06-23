/*global window, rJS, RSVP, GameManager, loopEventListener, console, document, Blob*/
/*jslint nomen: true, maxlen:80, indent:2*/
(function (window, rJS, RSVP, GameManager, console, document, Blob) {
  "use strict";

  var deferred = RSVP.defer();

  rJS(window)
    .declareMethod('render', function (options) {
      return this.changeState({
        content: options.value,
        key: options.key
      });
    })
    .declareMethod('getContent', function (options) {
      return deferred.promise;
    })

    .declareJob('runGame', function runGame() {
      var value = this.state.content ? JSON.parse(this.state.content) : null,
        gadget = this;
      if (value.autorun) {
        return (new GameManager(value.script, value.map,
                                value.simulation_speed)).run()
        .push(function (result) {
          if (GameManager.getLog() !== '') {
            var blob = new Blob([GameManager.getLog()], {type: 'text/plain'}),
              a = document.createElement('a');

            a.download = 'drone_log.txt';
            a.href = window.URL.createObjectURL(blob);
            a.dataset.downloadurl =  ['text/plain', a.download,
                                      a.href].join(':');
            a.textContent = 'LOG';
            document.querySelector('.actionBar').appendChild(a);
          }
          deferred.resolve(result);
        });
      }
    })

    .onStateChange(function (modification_dict) {
      if (modification_dict.hasOwnProperty('content')) {
        return this.runGame();
      }
    });
}(window, rJS, RSVP, GameManager, console, document, Blob));
