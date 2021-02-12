/*global window, rJS, RSVP, jIO, MediaSource
*/
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, loopEventListener) {
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
      return gadget.getDeclaredGadget(gadget.params.scope)
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
      return gadget.getDeclaredGadget(gadget.params.scope)
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
            gadget.params.scope = 'controller';
            if (gadget.params.controller) {
              return gadget.getDeclaredGadget('controller');
            }
            gadget.params.controller = true;
            return gadget.declareGadget('gadget_custom_player_controller.html', {
              element: gadget.element.querySelector('.controller'),
              scope: 'controller'
            });
          }
          gadget.params.scope = 'controller_fallback';
          if (gadget.params.contoller_fallback) {
            return gadget.getDeclaredGadget('controller_fallback');
          }
          gadget.params.controller_fallback = true;
          return gadget.declareGadget('gadget_custom_player_controller_fallback.html', {
            element: gadget.element.querySelector('.controller'),
            scope: 'controller_fallback'
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
            return gadget.changeState({ play: true, auto_play: true});  
          }
        }).push(function() {
          return RSVP.all([
            gadget.togglePlayPause(gadget.state.play),
            gadget.toggleSound(gadget.state.mute)
          ]);
        });
    })
    
    .ready(function () {
      this.params = {
        controller: false,
        controller_fallback: false
      };
    })
    
    .declareService(function () {
      var gadget = this,
       progress_bar = gadget.element.querySelector('progress');
      return loopEventListener(
        progress_bar,
        'click',
        false,
        function (event) {
          return gadget.getDeclaredGadget(gadget.params.scope)
          .push(function (controller) {
            var percentage = event.offsetX / progress_bar.offsetWidth;
            return controller.updateAudioElementCurrentTime(percentage * progress_bar.max, progress_bar.max)
              .push(function () {
                return gadget.togglePlayPause(gadget.state.play);
              });
          });
        },
        true
      );
    })

    .declareService(function () {
      var gadget = this;
      return loopEventListener(
        gadget.element.querySelector('.play-btn'),
        'click',
        false,
        function () {
          return gadget.changeState({ play: !gadget.state.play })
            .push(function () {
              return gadget.togglePlayPause(gadget.state.play);
            });
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
          return gadget.changeState({ mute: !gadget.state.mute })
            .push(function () {
              return gadget.toggleSound(gadget.state.mute);
            });
        },
        true
      );
    });
}(window, rJS, rJS.loopEventListener));