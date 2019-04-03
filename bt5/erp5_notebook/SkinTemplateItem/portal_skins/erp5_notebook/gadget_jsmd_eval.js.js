/*global window, console, RSVP, document, URL, eval, XMLHttpRequest, marked, pyodide */
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
    cell_type_regexp = /^\%\% (\w+)$/,
    is_pyodide_loaded = false;

  window.xiodide = new IODide();

  IODide.prototype.addOutputHandler = function () {
    return;
  };
  var Module = {};

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

  function loadPyodide() {
    let wasm_promise = WebAssembly.compileStreaming(fetch(`pyodide.asm.wasm`));
    Module.instantiateWasm = function (info, receiveInstance) {
      wasm_promise
      .then(module => WebAssembly.instantiate(module, info))
      .then(instance => receiveInstance(instance));
      return {};
    };
    window.Module = Module;
  }

  function executePyCell(line_list) {
    var result_text, code_text = line_list.join('\n');

    try {
      result_text = pyodide.runPython(line_list.join('\n'));
    } catch (e) {
      result_text = e.message;
    }

    if (typeof(result_text) === 'undefined') {
      result_text = 'undefined';
    }

    renderCodeblock(result_text, 'python');
  }

  function renderCodeblock(result_text, language) {
    var div = document.createElement('div'),
        pre = document.createElement('pre'),
        result = document.createElement('code');
    div.style.border = '1px solid #C3CCD0';
    div.style.margin = '40px 10px';
    div.style.paddingLeft = '10px';

    if (result_text !== 'undefined') {
      result.innerHTML = result_text;
      pre.appendChild(result);
      div.appendChild(pre);
      document.body.appendChild(div);
    }
  }

  function pyodideSetting() {
    window.pyodide = pyodide(Module);
    var defer = RSVP.defer(), promise=defer.promise;
    console.log("Setting postRun");
    window.pyodide.loadPackage = pyodideLoadPackage;

    Module.postRun = defer.resolve;
    promise.then(function() {
      console.log("postRun get called");
    });

    console.log("Setting postRun finished");
    return defer.promise;
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
    if (cell._type === 'py') {
      console.log("Py cell");

      console.log(is_pyodide_loaded);
      var queue = new RSVP.Queue();

      if (!is_pyodide_loaded) {
        console.log("Loading pyodide");
        queue.push(function() {
          console.log("Loading webassembly module");
          return loadPyodide();
        })
        .push(function () {
          console.log("Loading pyodide.asm.data.js");
          return loadJSResource(`pyodide.asm.data.js`);
        })
        .push(function () {
          console.log("Loading pyodide.asm.js");
          return loadJSResource('pyodide.asm.js');
        })
        .push(function () {
          console.log("Prepare to set postRun and pyodide");
          return pyodideSetting();
        });
        is_pyodide_loaded = true;
      }
      console.log("Fuck!");
      queue.push(function () {
        console.log("Executing Python cell");
        return executePyCell(cell._line_list);
      });
      return queue;
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

    for (i = 0; i < len; i += 1) {
      queue.push(deferCellExecution(cell_list[i]));
    }
    return queue
      .push(function () {
        console.info('JSMD executed.');
      }, function (error) {
        console.error(error);
        // do not print the error page with a non-styled pre tag
        // the Python error message will be displayed along with Python source code in above
        if (error.message.startsWith('Traceback')) {
          return;
        }
        var pre = document.createElement('pre');
        pre.textContent = error;
        document.body.appendChild(pre);
      });

  }, false);

}(window));