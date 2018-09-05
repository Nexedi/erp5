/*global window, rJS, RSVP, document, localStorage */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("updateDocument", "updateDocument")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", 'notifySubmitted')

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("render", function (options) {
      return this.changeState({
        key: options.key,
        value: options.value,
        first_render: true,
        timestamp: options.render_timestamp
      });
    })
    .onStateChange(function (modified_dict) {
      if (!this.state.value.includes('%%')) {
        this.state.value = '';
      }
      var iodideSettings = getiodideSettingsFromJsmd(this.state.value);
      if (iodideSettings && !iodideSettings.title) {
        iodideSettings.title = 'notebook-' + modified_dict.timestamp;
        var regex = /%% meta\r\n([\S\s]*?)\n%%/m;
        try {
          var capturedGroup = this.state.value.match(regex)[1];
          this.state.value = this.state.value.replace(capturedGroup, JSON.stringify(iodideSettings));
        } catch (e) {
          console.error(e);
        }
      }
      if (!iodideSettings) {
        var jsmdTitleTemplate = '%% meta\n{\n"title": ""\n}\n';
        var notebookTitle = 'notebook-' + modified_dict.timestamp;
        var positionToInsertTitle = 20;
        var jsmdNotebookTitle = [jsmdTitleTemplate.slice(0, positionToInsertTitle), notebookTitle, jsmdTitleTemplate.slice(positionToInsertTitle)].join('');
        this.state.value = jsmdNotebookTitle + this.state.value;
      }

      this.element.querySelector('script').textContent = this.state.value;

      if (!modified_dict.hasOwnProperty('first_render')) {
        throw new Error('Sorry, it is not possible to dynamically change the iodide content');
      }
      var iodide = document.createElement("script");
      iodide.src = "iodide_master.js";
      this.element.appendChild(iodide);

    })
    .declareMethod("getContent", function () {
      //prefer content since last save, fallback on autosave if it does not exist
      var dict = {};
      var notebookTitle = getiodideSettingsFromJsmd(this.state.value).title;
      var localStorageJsmd = localStorage.getItem(notebookTitle);
      if (!localStorageJsmd) {
        var autosaveString = 'AUTOSAVE: ' + notebookTitle;
        localStorageJsmd = localStorage.getItem(autosaveString);
      }
      dict[this.state.key] = localStorageJsmd;
      return dict;
    });

  function parseMetaChunk(content) {
    var metaSettings;
    try {
      metaSettings = JSON.parse(content);
    } catch (e) {
      console.error('Failed to parse notebook settings from meta cell. Using default settings.', content);
      metaSettings = {}; // set content back to empty object
    }
    return { chunkType: 'meta', iodideSettings: metaSettings };
  }

  function parseJsmdChunk(str) {
    var chunkType;
    var settings = {};
    var content;
    var firstLine;
    var firstLineBreak = str.indexOf('\n');
    if (firstLineBreak === -1) {
      // a cell with only 1 line, and hence no content
      firstLine = str;
      content = '';
    } else {
      firstLine = str.substring(0, firstLineBreak).trim();
      content = str.substring(firstLineBreak + 1).trim();
    }
    // let firstLine = str.substring(0,firstLineBreak).trim()
    var firstLineFirstSpace = firstLine.indexOf(' ');


    if (firstLineFirstSpace === -1) {
      // if there is NO space on the first line (after trimming), there are no cell settings
      chunkType = firstLine.toLowerCase();
    } else {
      // if there is a space on the first line (after trimming), there must be cell settings
      chunkType = firstLine.substring(0, firstLineFirstSpace).toLowerCase();
      // make sure the cell settings parse as JSON
    }
    var chunkObject;
    if (chunkType === 'meta') {
      chunkObject = parseMetaChunk(content);
    } else {
      console.log('not meta chunk');
    }

    return chunkObject;
  }

  function getiodideSettingsFromJsmd(jsmdString) {
    // returns iodideSettings of last found chunk and exits
    var chunkObjects = jsmdString.split('\n%%')
      .map((str, chunkNum) => {
        // if this is the first chunk, and it starts with "%%", drop those chars
        let sstr
        if (chunkNum === 0 && str.substring(0, 2) === '%%') {
          sstr = str.substring(2)
        } else {
          sstr = str
        }
        return sstr
      })
      .map(str => str.trim())
      .filter(str => str !== '');

    for (var i = (chunkObjects.length-1); i >= 0 ; i--){
      var chunk = parseJsmdChunk(chunkObjects[i]);
      if (chunk && chunk.iodideSettings) {
         return chunk.iodideSettings
      }
    }
    return '';
  }

}(window, rJS, RSVP));