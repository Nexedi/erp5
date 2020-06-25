/*globals window, document, RSVP, rJS*/
/*jslint indent: 2, maxlen: 80*/
(function () {
  "use strict";

  // XXX Copy/paste from renderjs
  function ajax(url) {
    var xhr;
    function resolver(resolve, reject) {
      function handler() {
        try {
          if (xhr.readyState === 0) {
            // UNSENT
            reject(xhr);
          } else if (xhr.readyState === 4) {
            // DONE
            if ((xhr.status < 200) || (xhr.status >= 300) ||
                (!/^text\/html[;]?/.test(
                  xhr.getResponseHeader("Content-Type") || ""
                ))) {
              reject(xhr);
            } else {
              resolve(xhr);
            }
          }
        } catch (e) {
          reject(e);
        }
      }

      xhr = new XMLHttpRequest();
      xhr.open("GET", url);
      xhr.onreadystatechange = handler;
      xhr.setRequestHeader('Accept', 'text/html');
      xhr.withCredentials = true;
      xhr.send();
    }
    function canceller() {
      if ((xhr !== undefined) && (xhr.readyState !== xhr.DONE)) {
        xhr.abort();
      }
    }
    return new RSVP.Promise(resolver, canceller);
  }


  function listenURLChange() {
    var gadget = this;

    function renderPage() {
      return new RSVP.Queue(ajax(window.location.href))
        .push(function (xhr) {
          console.log(xhr);
          var doc = (new DOMParser()).parseFromString(xhr.responseText,
                                                      'text/html');
          return gadget.getDeclaredGadget('renderer')
            .push(function (style_gadget) {
              console.log(doc.documentElement.outerHTML);
              console.log(doc.body);
              return style_gadget.render(doc.body.querySelector('main').innerHTML);
            });

//          console.log('reload page ' + window.location.href);
//          window.location.reload();

        });
    }

    function handlePopState() {
      // console.log(evt);
      // alert('couscous');
/*
      return new RSVP.Queue()
        .push(function () {
          return extractHashAndDispatch(evt);
        });
*/
      console.log('pop state reload');
      return renderPage();
    }

    function handleClick(evt) {
      var target_element = evt.target,
        target_tag = target_element.tagName,
        base_uri = document.baseURI,
        link_url;

      if (target_tag !== 'A') {
        // Only handle link
        return;
      }
      if (target_element.target === "_blank") {
        // Open in a new tab
        return;
      }
      if (evt.altKey || evt.ctrlKey || evt.metaKey || evt.shiftKey) {
        return;
      }

      link_url = new URL(target_element.href, base_uri);
      if (link_url.href.indexOf(base_uri) !== 0) {
        // Only handle sub path of the base url
        return;
      }

      evt.preventDefault();
      window.history.pushState(null, null, target_element.href);
      console.log('push state reload');
      return renderPage();
    }

    var result = RSVP.all([
      loopEventListener(window, 'popstate', false, handlePopState, false),
      loopEventListener(document.documentElement, 'click', false, handleClick, false),
    ]);
/*
    window.history.onpushstate(function () {
      alert('nutnut');
    });
*/
/*
      event = document.createEvent("Event");
    event.initEvent('hashchange', true, true);
    event.newURL = window.location.toString();
    window.dispatchEvent(event);
*/
    return result;
  }

  rJS(window)
    .ready(function () {
      // Hide the page as fast as possible
      // this.element.hidden = true;
      this.main_element = this.element.querySelector('main');
    })
    .allowPublicAcquisition("reportServiceError", function () {
      this.element.hidden = false;
      throw rJS.AcquisitionError();
    })
    .declareJob("listenURLChange", listenURLChange)
    .declareService(function () {
      var gadget = this,
        style_gadget,
        body = gadget.element;
      // Clear the DOM
      while (body.firstChild) {
        body.firstChild.remove();
      }
      return gadget.declareGadget('nostyle_syna.html', {scope: 'renderer'})
        .push(function (result) {
          style_gadget = result;
          return style_gadget.render(gadget.main_element.innerHTML);
        })
        .push(function () {
          // Trigger URL handling
          gadget.listenURLChange();

          body.appendChild(style_gadget.element);
          gadget.element.hidden = false;
        }, function (error) {
          gadget.element.hidden = false;
          throw error;
        });
    });

}());