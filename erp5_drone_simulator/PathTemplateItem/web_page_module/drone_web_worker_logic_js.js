/*global GameManager, console*/
/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80 */

var runGame, game_manager_instance;
// game.js
(function () {
  "use strict";
  console.log('game logic');

  runGame = function (canvas, script, map, log) {
    console.log('runGame', canvas);
    if (!game_manager_instance) {
      game_manager_instance = new GameManager(canvas, script, map, 5);
    }
    return game_manager_instance.run();
  };

/*
  // Resize canvas on window resize
  window.addEventListener('resize', function () {
    engine.resize();
  });
*/
}(this));