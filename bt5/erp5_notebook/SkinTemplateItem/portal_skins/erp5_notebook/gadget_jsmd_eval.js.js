/*global window, console, RSVP, document, URL, eval, XMLHttpRequest, marked */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window) {
  "use strict";

  var IODide = function createIODide() {
    return;
  },
    JSMDCell = function createJSMDCell(type, line_list) {
      this._type = type;
      this._line_list = line_list;
    },
    split_line_regex = /[\r\n|\n|\r]/,
    cell_type_regexp = /^\%\% (\w+)$/;

  window.iodide = new IODide();

  IODide.prototype.addOutputHandler = function () {
    return;
  };

  // Copied from jio
  function ajax(param) {
    var xhr = new XMLHttpRequest();
    return new RSVP.Promise(function (resolve, reject) {
      var k;
      xhr.open(param.type || "GET", param.url, true);
      xhr.responseType = param.dataType || "";
      if (typeof param.headers === 'object' && param.headers !== null) {
        for (k in param.headers) {
          if (param.headers.hasOwnProperty(k)) {
            xhr.setRequestHeader(k, param.headers[k]);
          }
        }
      }
      xhr.addEventListener("load", function (e) {
        if (e.target.status >= 400) {
          return reject(e);
        }
        resolve(e);
      });
      xhr.addEventListener("error", reject);
      if (typeof param.xhrFields === 'object' && param.xhrFields !== null) {
        for (k in param.xhrFields) {
          if (param.xhrFields.hasOwnProperty(k)) {
            xhr[k] = param.xhrFields[k];
          }
        }
      }
      if (param.timeout !== undefined && param.timeout !== 0) {
        xhr.timeout = param.timeout;
        xhr.ontimeout = function () {
          return reject(new Error("Gateway Timeout"));
        };
      }
      if (typeof param.beforeSend === 'function') {
        param.beforeSend(xhr);
      }
      xhr.send(param.data);
    }, function () {
      xhr.abort();
    });
  }

  function parseJSMDCellList(jsmd) {
    // Split the text into a list of Iodide cells
    var line_list = jsmd.split(split_line_regex),
      i,
      len = line_list.length,
      current_line,
      current_type,
      current_text_list,
      next_type,
      cell_list = [];

    function pushNewCell() {
      if (current_type !== undefined) {
        cell_list.push(new JSMDCell(current_type[1],
                                      current_text_list));
      }
    }

    for (i = 0; i < len; i += 1) {
      current_line = line_list[i];
      next_type = current_line.match(cell_type_regexp);
      if (next_type) {
        // New type detexted
        pushNewCell();
        current_type = next_type;
        current_text_list = [];
      } else if (current_text_list !== undefined) {
        current_text_list.push(current_line);
      }
    }
    // Push last cell
    pushNewCell();
    return cell_list;
  }

  function executeUnknownCellType(cell) {
    throw new Error('Unsupported cell: ' + cell._type);
  }

  function executeJSCell(line_list) {
    // console.info('eval', line_list);
    var text = line_list.join('\n'),
      pre,
      br,
      code;
    try {
      return eval.call(window, text);
    } catch (e) {
      console.error(e);
      pre = document.createElement('pre');
      pre.textContent = e.message;

      br = document.createElement('br');
      pre.appendChild(br);

      code = document.createElement('code');
      code.textContent = text;
      pre.appendChild(code);
      document.body.appendChild(pre);
      throw e;
    }
  }

  function executeCssCell(line_list) {
    var style = document.createElement('style');
    style.textContent = line_list.join('\n');
    document.head.appendChild(style);
  }

  function loadJSResource(url) {
    // Copied from renderJS
    return new RSVP.Promise(
      function waitForJSLoadEvent(resolve, reject) {
        var newScript;
        newScript = document.createElement('script');
        newScript.async = false;
        newScript.type = 'text/javascript';
        newScript.onload = function (evt) {
          resolve(evt.target.value);
        };
        newScript.onerror = function (error) {
          console.warn(error);
          reject(error);
        };
        newScript.src = url;
        document.head.appendChild(newScript);
      }
    );
  }

  function deferJSResourceLoading(url) {
    return function () {
      return loadJSResource(url);
    };
  }

  function loadCSSResource(url) {
    // Copied from renderJS
    return new RSVP.Promise(
      function waitForCSSLoadEvent(resolve, reject) {
        var link;
        link = document.createElement('link');
        link.rel = 'stylesheet';
        link.type = 'text/css';
        link.href = url;
        link.onload = resolve;
        link.onerror = reject;
        document.head.appendChild(link);
      }
    );
  }

  function deferCSSResourceLoading(url) {
    return function () {
      return loadCSSResource(url);
    };
  }

  function loadTextResource(line) {
    var line_split = line.split('=', 2),
      variable = line_split[0],
      url = line_split[1];
    console.log(line_split);
    return new RSVP.Queue()
      .push(function () {
        return ajax({url: url});
      })
      .push(function (evt) {
        window[variable] = evt.target.responseText;
      });
  }

  function deferTextResourceLoading(line) {
    return function () {
      return loadTextResource(line);
    };
  }

  function executeResourceCell(line_list) {
    var queue = new RSVP.Queue(),
      len = line_list.length,
      i;
    for (i = 0; i < len; i += 1) {
      if (line_list[i]) {
        queue.push(deferJSResourceLoading(line_list[i]));
      }
    }
    return queue;
  }

  function executeFetchCell(line_list) {
    var queue = new RSVP.Queue(),
      len = line_list.length,
      i,
      line;
    for (i = 0; i < len; i += 1) {
      line = line_list[i];
      if (line) {
        if (line.startsWith('js: ')) {
          queue.push(deferJSResourceLoading(line.slice(4)));
        } else if (line.startsWith('css: ')) {
          queue.push(deferCSSResourceLoading(line.slice(5)));
        } else if (line.startsWith('text: ')) {
          queue.push(deferTextResourceLoading(line.slice(6)));
        } else {
          queue.cancel();
          throw new Error('Unsupported fetch type: ' + line);
        }
      }
    }
    return queue;
  }

  function executeMarkdownCell(line_list) {
    var renderer = new marked.Renderer();
    return new RSVP.Promise(function (resolve, reject) {
      marked(line_list.join('\n'),
             {renderer: renderer},
             function (err, content) {
          if (err) {
            reject(err);
          }
          var div = document.createElement('div');
          div.classList.add('user-markdown');
          div.innerHTML = content;
          document.body.appendChild(div);
          resolve();
        });
    });
  }

  function executeCell(cell) {
    if (cell._type === 'raw') {
      // Do nothing...
      return;
    }
    if (cell._type === 'js') {
      return executeJSCell(cell._line_list);
    }
    if (cell._type === 'resource') {
      return executeResourceCell(cell._line_list);
    }
    if (cell._type === 'fetch') {
      return executeFetchCell(cell._line_list);
    }
    if (cell._type === 'md') {
      return executeMarkdownCell(cell._line_list);
    }
    if (cell._type === 'css') {
      return executeCssCell(cell._line_list);
    }
    return executeUnknownCellType(cell);
  }

  function deferCellExecution(cell) {
    return function () {
      return executeCell(cell);
    };
  }


  document.addEventListener('DOMContentLoaded', function () {

    var jsmd = document.querySelector('[type="text/x-jsmd"]').textContent,
      cell_list = parseJSMDCellList(jsmd),
      len = cell_list.length,
      i,
      queue = new RSVP.Queue();
    console.log(cell_list);

    for (i = 0; i < len; i += 1) {
      queue.push(deferCellExecution(cell_list[i]));
    }
    return queue
      .push(function () {
        console.info('JSMD executed.');
      }, function (error) {
        console.error(error);
        var pre = document.createElement('pre');
        pre.textContent = error;
        document.body.appendChild(pre);
      });

  }, false);

}(window));