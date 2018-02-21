/*global window, rJS, RSVP, jIO, MediaSource,
  loopEventListener
*/
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  function toHHMMSS(sec) {
    var sec_num = parseInt(sec, 10),
      hours = Math.floor(sec_num / 3600),
      minutes = Math.floor((sec_num - (hours * 3600)) / 60),
      seconds = sec_num - (hours * 3600) - (minutes * 60);

    if (hours   < 10) { hours   = "0" + hours; }
    if (minutes < 10) { minutes = "0" + minutes; }
    if (seconds < 10) { seconds = "0" + seconds; }
    return hours + ':' + minutes + ':' + seconds;
  }

  rJS(window)
    .declareAcquiredMethod("jio_get", "jio_get")
    /////////////////////////////////////////////
    // Declare Method
    ////////////////////////////////////////////
    .allowPublicAcquisition('updateCurrentTime', function (time) {
      this.customPlayer.querySelector('.current_time').innerHTML = toHHMMSS(time);
    })

    .allowPublicAcquisition('updateTotalTime', function (time) {
      this.customPlayer.querySelector('.total_time').innerHTML = toHHMMSS(time);
    })

    .declareMethod('togglePlayPause', function () {
      if (this.play) {
        this.play = false;
        this.customPlayer.querySelector('.play-btn').classList.add('ui-icon-play');
        this.customPlayer.querySelector('.play-btn').classList.remove('ui-icon-pause');
      } else {
        this.play = true;
        this.customPlayer.querySelector('.play-btn').classList.add('ui-icon-pause');
        this.customPlayer.querySelector('.play-btn').classList.remove('ui-icon-play');
      }
      return this.controller.handlePlayPause.call(this.controller);
    })

    .declareMethod('toggleSound', function () {
      if (this.muted) {
        this.muted = false;
        this.customPlayer.querySelector('.vol-btn').classList.remove('ui-icon-volume-off');
        this.customPlayer.querySelector('.vol-btn').classList.add('ui-icon-volume-up');
      } else {
        this.muted = true;
        this.customPlayer.querySelector('.vol-btn').classList.remove('ui-icon-volume-up');
        this.customPlayer.querySelector('.vol-btn').classList.add('ui-icon-volume-off');
      }
      return this.controller.handleSound.call(this.controller);
    })
    .declareMethod('getContent', function (params) {
      return {};
    })

    .declareMethod('render', function (params) {
      var gadget = this;
      this.play = false;
      this.muted = false;
      this.id = params.value.id;
      this.customPlayer = this.element.querySelector('.audioplayer');
      return this.jio_get(this.id).push(function (doc) {
        var nameArr = doc.title.split('.');
        gadget.type = nameArr[nameArr.length - 1];
        var subGadget;
        if (gadget.type === 'mp3' && MediaSource.isTypeSupported('audio/mpeg')) {
          subGadget = gadget.declareGadget('gadget_custom_player_controller.html', {
            element: gadget.element.querySelector('.controller')
          });
        } else {
          subGadget = gadget.declareGadget('gadget_custom_player_controller_fallback.html', {
            element: gadget.element.querySelector('.controller')
          });
        }
        return subGadget.push(function (controller) {
          gadget.controller = controller;
          return controller.render({ id: gadget.id, length: doc.length });
        });
      });
    })

  /*
    .declareService(function () {
      var gadget = this;
      gadget.mousedown = false;
      return loopEventListener(
        gadget.element.querySelector('.playhead'),
        'mousedown',
        false,
        function () {
          gadget.mousedown = true;
          gadget.play = false;
          gadget.customPlayer.querySelector('.play-btn').classList.add('ui-icon-play');
          gadget.customPlayer.querySelector('.play-btn').classList.remove('ui-icon-pause');
          gadget.audio.pause();
        },
        true
      );
    })

    .declareService(function () {
      var gadget = this;
      gadget.mousedown = false;
      return loopEventListener(
        gadget.element.querySelector('.timeline'),
        'mouseup',
        false,
        function () {
          gadget.mousedown = false;
          gadget.play = true;
          gadget.customPlayer.querySelector('.play-btn').classList.add('ui-icon-pause');
          gadget.customPlayer.querySelector('.play-btn').classList.remove('ui-icon-play');
          gadget.audio.play();
        },
        true
      );
    })

    .declareService(function () {
      var gadget = this;
      return loopEventListener(
        gadget.element.querySelector('.timeline'),
        'mousemove',
        false,
        function (evt) {
          if (gadget.mousedown) {
            var val = ((evt.offsetX / gadget.element.querySelector('.timeline').offsetWidth)) * 100;
            val = (val > 98 ? 98 : val);
            gadget.element.querySelector('.timeline').style.background = 'linear-gradient(to right, #454549 ' + (val + 1) + '%, #bcbcbc 0%';
            gadget.element.querySelector('.playhead').style.marginLeft = val + '%';
            gadget.currentTime = (val * gadget.duration) / 98;
            gadget.audio.currentTime = gadget.currentTime;
          }
        },
        true
      );
    })

    .declareService(function () {
      var gadget = this;
      return loopEventListener(
        gadget.element.querySelector('.timeline'),
        'click',
        false,
        function (evt) {
          var val = ((evt.offsetX / gadget.element.querySelector('.timeline').offsetWidth)) * 100;
          val = (val > 98 ? 98 : val);
          gadget.element.querySelector('.timeline').style.background = 'linear-gradient(to right, #454549 ' + (val + 1) + '%, #bcbcbc 0%';
          gadget.element.querySelector('.playhead').style.marginLeft = val + '%';
          gadget.audio.currentTime = (val * gadget.duration) / 98;
        },
        true
      );
    })
*/
    .declareService(function () {
      var gadget = this;
      return loopEventListener(
        gadget.element.querySelector('.pVolumn'),
        'mouseover',
        false,
        function () {
          gadget.element.querySelector('.volTimeline').style.display = /*change it to block*/'none';
        },
        true
      );
    })

    .declareService(function () {
      var gadget = this;
      return loopEventListener(
        gadget.element.querySelector('.pVolumn'),
        'mouseleave',
        false,
        function () {
          gadget.element.querySelector('.volTimeline').style.display = 'none';
        },
        true
      );
    })

    .declareService(function () {
      var gadget = this;
      return loopEventListener(
        gadget.element.querySelector('.volTimeline'),
        'mouseover',
        false,
        function () {
          gadget.element.querySelector('.volTimeline').style.display = 'block';
        },
        true
      );
    })

    .declareService(function () {
      var gadget = this;
      return loopEventListener(
        gadget.element.querySelector('.volTimeline'),
        'mouseleave',
        false,
        function () {
          gadget.element.querySelector('.volTimeline').style.display = 'none';
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
        gadget.togglePlayPause.bind(gadget),
        true
      );
    })

    .declareService(function () {
      var gadget = this;
      return RSVP.Queue()
        .push(function () {
          return loopEventListener(
            gadget.element.querySelector('.vol-btn'),
            'click',
            false,
            gadget.toggleSound.bind(gadget),
            true
          );
        });
    });
}(window, rJS, RSVP));