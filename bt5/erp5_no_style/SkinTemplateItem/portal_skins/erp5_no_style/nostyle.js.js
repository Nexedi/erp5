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

    function renderPage(page_url) {
      return new RSVP.Queue(RSVP.hash({
        xhr: ajax(page_url),
        style_gadget: gadget.getDeclaredGadget('renderer')
      }))
        .push(function (result_dict) {
          var dom_parser = (new DOMParser()).parseFromString(result_dict.xhr.responseText,
                                                             'text/html');
          return result_dict.style_gadget.render(dom_parser.body.querySelector('main').innerHTML);
        })
        .push(function () {
          window.scrollTo(0, 0);
        });
    }

    function handlePopState() {
      return renderPage(window.location.href);
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
      return renderPage(target_element.href)
        .push(function () {
          window.history.pushState(null, null, target_element.href);
        }, function () {
          // Implement support for managed error
          // (like URL is not an HTML document parsable)
          // and redirect in such case
          window.location = target_element.href;
        });
    }

    return RSVP.all([
      loopEventListener(window, 'popstate', false, handlePopState, false),
      loopEventListener(document.documentElement, 'click', false, handleClick, false),
    ]);
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