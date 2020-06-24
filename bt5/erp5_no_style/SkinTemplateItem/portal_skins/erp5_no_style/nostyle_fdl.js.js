/*globals window, document, RSVP, rJS*/
/*jslint indent: 2, maxlen: 80*/
(function () {
  "use strict";

  rJS(window)
    .declareAcquiredMethod("getMainInnerHTML", "getMainInnerHTML")
    .declareAcquiredMethod("showPage", "showPage")

    .declareService(function () {
      var gadget = this;
      return gadget.getMainInnerHTML()
        .push(function (main_innerhtml) {
          var div = document.createElement('div');
          div.innerHTML = main_innerhtml;
          gadget.element.querySelector('div.rjs-content-container').innerHTML = div.querySelector('div.input').firstChild.innerHTML;
                    return RSVP.delay(50);

        })

        .push(function () {
          return gadget.showPage();
        })
        .push(function () {
          var carousel = window.document.querySelector(".siema");
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
            window.componentHandler.upgradeDom();
          }
        });

    /*
    })
    .declareService(function () {
      var gadget = this,
        body = gadget.element;
      return new RSVP.Queue(RSVP.all([
          rJS.declareCSS("https://www.fdl-lef.org/material_design_lite.1.3.0.min.css", document.head),
          rJS.declareCSS("https://www.fdl-lef.org/font-awesome.5.1/font-awesome.5.1.css", document.head),
          rJS.declareCSS("https://www.fdl-lef.org/fdl_complexity.css", document.head)
        ]))
        .push(function () {
          var main = body.querySelector('main');

          body.innerHTML = '';
          body.appendChild(main);
          body.hidden = false;
        });

      console.log('aaaa');
      */
    });

}());