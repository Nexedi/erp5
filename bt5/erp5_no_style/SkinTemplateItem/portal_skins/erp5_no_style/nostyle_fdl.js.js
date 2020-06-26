/*globals window, document, RSVP, rJS*/
/*jslint indent: 2, maxlen: 80*/
(function () {
  "use strict";

  rJS(window)
    .declareMethod("render", function (main_innerhtml) {
      var gadget = this;
      var div = document.createElement('div');
      div.innerHTML = main_innerhtml;
      gadget.element.querySelector('div.rjs-content-container').innerHTML = div.querySelector('div.input').firstChild.innerHTML;
      gadget.renderCarousel();
    })
    .declareJob("renderCarousel", function () {
      var gadget = this;
      gadget.element.querySelector('main').scrollTo(0, 0);

      var carousel = gadget.element.querySelector(".siema");
      var s;
      if (carousel) {
        s = new Siema({
          selector: carousel,
          easing: 'ease-out',
          perPage: 1,
          duration: 300,
          loop: true
        });
        document.querySelector('.prev').addEventListener('click', function () {
          s.prev();
        }, false);
        document.querySelector('.next').addEventListener('click', function () {
          s.next();
        }, false);
        // window.componentHandler.upgradeDom();
      }
    });

}());