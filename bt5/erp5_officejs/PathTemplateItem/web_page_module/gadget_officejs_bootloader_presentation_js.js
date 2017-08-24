/*global window, rJS, document*/
/*jslint nomen: true, maxlen:80, indent:2*/
(function (window, rJS, document) {
  "use strict";

  rJS(window)
    .declareMethod('render', function (options) {
      var element = this.element.querySelector("center"),
        img, div, i, header, p, loader, error, skip;

      header = document.createElement('header');
      header.textContent = "OfficeJS Installer";
      element.appendChild(header);

      for (i = 0; i < 7; i += 1) {
        element.appendChild(document.createElement('br'));
      }

      img = document.createElement('img');
      img.setAttribute('width', '100');
      img.setAttribute('height', '100');
      img.setAttribute('src', 'officejs_logo.png');
      element.appendChild(img);
      element.appendChild(document.createElement('br'));

      div = document.createElement('div');
      p = document.createElement('p');
      p.textContent = "Preparing " + options.app_name;
      div.appendChild(p);
      div.appendChild(document.createElement('br'));
      p = document.createElement('p');
      p.textContent =
        "Your application is being prepared for a 100 % offline mode";
      div.appendChild(p);
      loader = document.createElement('div');
      loader.setAttribute('class', 'loader');
      element.appendChild(div);
      div.appendChild(document.createElement('br'));
      element.appendChild(loader);
      if (options.retry > 0) {
        element.appendChild(document.createElement('br'));
        error = document.createElement('div');
        p = document.createElement('p');
        p.textContent = "Last Error: " +
          options.error.message || 'Unknow Error';
        element.appendChild(p);
        element.appendChild(document.createElement('br'));
        p = document.createElement('p');
        p.textContent = "Retry n° " + options.retry;
        element.appendChild(p);
      }
      div = document.createElement('div');
      skip = document.createElement('a');
      skip.textContent = 'Skip';
      skip.setAttribute('href', options.redirect_url);
      div.appendChild(skip);
      element.appendChild(document.createElement('br'));
      element.appendChild(skip);
      return;
    });

}(window, rJS, document));