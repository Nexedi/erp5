/*global window, rJS, RSVP, jIO, MediaSource,
  loopEventListener
*/
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS) {
  "use strict";

  rJS(window)
    .setState({ play: false, mute: false, auto_play: false })

    //////////////////////////////////////////////
    // Acquire Method
    //////////////////////////////////////////////
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("redirect", "redirect")

    /////////////////////////////////////////////
    // Declare Method
    ////////////////////////////////////////////
    .allowPublicAcquisition('updateCurrentTime', function (time) {
      this.element.querySelector('.current_time').textContent = new Date(time * 1000).toISOString().substr(11, 8);
      this.element.querySelector('progress').value = time;
    })

    .allowPublicAcquisition('updateTotalTime', function (time) {
      this.element.querySelector('.total_time').textContent = new Date(time * 1000).toISOString().substr(11, 8);
      this.element.querySelector('progress').max = time;
    })

    .allowPublicAcquisition('onEnd', function () {
      if (this.state.auto_play) {
        return this.redirect({ command: 'selection_next' });  
      }
      return this.changeState({ play: false, mute: false });
    })

    .declareMethod('togglePlayPause', function () {
      var gadget = this,
        play_button = gadget.element.querySelector('.play-btn');

      if (gadget.state.play) {
        play_button.classList.add('ui-icon-pause');
        play_button.classList.remove('ui-icon-play');
      } else {
        play_button.classList.add('ui-icon-play');
        play_button.classList.remove('ui-icon-pause');
      }
      return gadget.getDeclaredGadget('controller')
        .push(function (controller) {
          return controller.handlePlayPause(gadget.state.play);
        });
    })

    .declareMethod('toggleSound', function () {
      var gadget = this,
        volume_button = gadget.element.querySelector('.vol-btn');

      if (gadget.state.mute) {
        volume_button.classList.remove('ui-icon-volume-up');
        volume_button.classList.add('ui-icon-volume-off');
      } else {
        volume_button.classList.remove('ui-icon-volume-off');
        volume_button.classList.add('ui-icon-volume-up');
      }
      return gadget.getDeclaredGadget('controller')
        .push(function (controller) {
          return controller.handleSound(gadget.state.mute);
        });
    })

    .declareMethod('render', function (params) {
      var gadget = this;
      return gadget.jio_get(params.value)
        .push(function (doc) {
          var name_array = doc.title.split('.'),
            type = name_array[name_array.length - 1];
          if (type === 'mp3' && MediaSource.isTypeSupported('audio/mpeg')) {
            return gadget.declareGadget('gadget_custom_player_controller.html', {
              element: gadget.element.querySelector('.controller'),
              scope: 'controller'
            });
          }
          return gadget.declareGadget('gadget_custom_player_controller_fallback.html', {
            element: gadget.element.querySelector('.controller'),
            scope: 'controller'
          });
        })
        .push(function (controller) {
          return controller.render({
            id: params.value,
            name: params.name
          });
        })
        .push(function () {
          if (params.auto_play) {
            return gadget.changeState({ play: true, auto_play: true });  
          }
        });
    })

    .onStateChange(function (modification_dict) {
      if (modification_dict.hasOwnProperty('play')) {
        return this.togglePlayPause(modification_dict.play);
      }
      if (modification_dict.hasOwnProperty('mute')) {
        return this.toggleSound(modification_dict.mute);
      }
    })

    .declareService(function () {
      var gadget = this;
      return loopEventListener(
        gadget.element.querySelector('.play-btn'),
        'click',
        false,
        function () {
          return gadget.changeState({ play: !gadget.state.play });
        },
        true
      );
    })

    .declareService(function () {
      var gadget = this;
      return loopEventListener(
        gadget.element.querySelector('.vol-btn'),
        'click',
        false,
        function () {
          return gadget.changeState({ mute: !gadget.state.mute });
        },
        true
      );
    });
}(window, rJS));