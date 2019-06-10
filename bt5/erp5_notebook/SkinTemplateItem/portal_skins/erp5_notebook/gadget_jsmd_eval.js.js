/*global window, console, RSVP, document, URL, eval, XMLHttpRequest, marked, pyodide, WebAssembly, fetch*/
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window) {
  "use strict";

  var IODide = function createIODide() {
    var iodide = {
      output: {
        text: function (s, reportSideEffect) {
          var i, div, line_list;
          console.log(s);
          line_list = s.toString().split("\n");
          for (i = 0; i < line_list.length; i += 1) {
            div = sideEffectDiv("side-effect-print", reportSideEffect);
            div.textContent = line_list[i];
          }
        },
        element: function (nodeType, reportSideEffect) {
          var div, node;
          div = sideEffectDiv("side-effect-element", reportSideEffect);
          node = document.createElement(nodeType);
          div.append(node);
          return node;
        }
      }
    };
    return iodide;
  },
    JSMDCell = function createJSMDCell(type, line_list) {
      this._type = type;
      this._line_list = line_list;
    },
    split_line_regex = /[\r\n|\n|\r]/,
    cell_type_regexp = /^\%\% (\w+)\b/,
    language_type_regexp = /\{[\S\s]+\}/,
    is_pyodide_loaded = false,
    Module = {},
    packages,
    loadedPackages = [],
    py_div_id_prefix = "py_div_id_",
    py_div_id_count = 0,
    py_div_id_count_2 = 0,
    props = {},
    // Regexp for validating package name and URI
    package_name_regexp = '[a-z0-9_][a-z0-9_\-]*',
    package_uri_regexp = new RegExp('^https?://.*?(' + package_name_regexp + ').js$', 'i');

  package_name_regexp = new RegExp('^' + package_name_regexp + '$', 'i');
  window.iodide = new IODide();

  IODide.prototype.addOutputHandler = function () {
    return;
  };

  function sideEffectDiv(sideEffectClass, reportSideEffect) {
    // appends a side effect div to the side effect area
    var div = document.createElement("div");
    div.setAttribute("class", sideEffectClass);
    if (reportSideEffect === undefined) {
      div.setAttribute("style", "display:");
    }
    document.body.appendChild(div);
    return div;
  }

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

  // Pyodide package loading
  function _uri_to_package_name(package_uri) {
    // Generate a unique package name from URI
    if (package_name_regexp.test(package_uri)) {
      return package_uri;
    }

    if (package_uri_regexp.test(package_uri)) {
      var match = package_uri_regexp.exec(package_uri);
      // Get the regexp group corresponding to the package name
      return match[1];
    }

    return null;
  }

  function pyodideLoadPackage(names) {
    // DFS to find all dependencies of the requested packages
    var queue, toLoad, package_uri, package_name, k,
      subpackage, promise, packageList, script;
    packages = window.pyodide.packages.dependencies;
    queue = new Array(names);
    toLoad = [];
    while (queue.length) {
      package_uri = queue.pop();
      package_name = _uri_to_package_name(package_uri);

      if (package_name === null) {
        throw new Error("Invalid package name or URI " + package_uri);
      }

      if (package_name === package_uri) {
        package_uri = 'default channel';
      }

      if (package_name in loadedPackages) {
        if (package_uri !== loadedPackages[package_name]) {
          throw new Error(
            "URI mismatch, attempting to load package " +
            package_name + " from " + package_uri + " while it is already " +
            "loaded from " + loadedPackages[package_name] + " ! "
          );
        }
      } else {
        toLoad[package_name] = package_uri;
        if (packages.hasOwnProperty(package_name)) {
          for (k in packages[package_name]) {
            subpackage = packages[package_name][k];
            if (!(subpackage in loadedPackages) && !(subpackage in toLoad)) {
              queue.push(subpackage);
            }
          }
        } else {
          throw new Error("Unknown package " + package_name);
        }
      }
    }

    promise = new RSVP.Promise(function (resolve, reject) {
      if (Object.keys(toLoad).length === 0) {
        resolve('No new packages to load');
      }

      pyodide.monitorRunDependencies = function (n) {
        if (n === 0) {
          for (package_name in toLoad) {
            loadedPackages[package_name] = toLoad[package_name];
          }
          delete pyodide.monitorRunDependencies;
          packageList = Array.from(Object.keys(toLoad)).join(', ');
          resolve("Loaded " + packageList);
        }
      };

      function script_reject(e) {
        reject(e);
      }

      for (package_name in toLoad) {
        script = document.createElement('script');
        package_uri = toLoad[package_name];
        if (package_uri === 'default channel') {
          script.src = package_name + ".js";
        } else {
          script.src = package_uri;
        }
        script.onerror = script_reject;
        document.body.appendChild(script);
      }

      // We have to invalidate Python's import caches, or it won't
      // see the new files. This is done here so it happens in parallel
      // with the fetching over the network.
      window.pyodide.runPython('import importlib as _importlib\n' +
        '_importlib.invalidate_caches()\n');
    });
    return promise;
  }

  function parseJSMDCellList(jsmd) {
    // Split the text into a list of Iodide cells
    var line_list = jsmd.split(split_line_regex),
      i,
      len = line_list.length,
      current_line,
      current_type,
      language_type,
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
        if (next_type[1] === 'code') {
          // language detected
          language_type = JSON.parse(current_line.match(language_type_regexp)).language;
          next_type[1] = next_type[1] + '_' + language_type;
        }
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
      code,
      result;

    try {
      result = eval.call(window, text);
      renderCodeblock(result);
      return result;
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
        return ajax({
          url: url
        });
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
      marked(line_list.join('\n'), {
          renderer: renderer
        },
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

  function loadPyodide(info, receiveInstance) {
    var queue = new RSVP.Queue();
    queue.push(function () {
        return ajax({
          url: "pyodide.asm.wasm",
          dataType: "arraybuffer"
        })
      })
      .push(function (evt) {
        return WebAssembly.instantiate(evt.target.response, info);
      })
      .push(function (results) {
        return receiveInstance(results.instance);
      })
      .push(undefined, function (error) {
        console.log(error);
      });
    return queue;
  }

  function renderCodeblock(result_text) {
    var div = document.createElement('div'),
      pre = document.createElement('pre'),
      result = document.createElement('code');
    div.style.border = '1px solid #C3CCD0';
    div.style.margin = '40px 10px';
    div.style.paddingLeft = '10px';

    if (result_text !== undefined) {
      result.innerHTML = result_text;
      pre.appendChild(result);
      div.appendChild(pre);
      document.body.appendChild(div);
    }
  }

  function addPyCellStub() {
    var div = document.createElement('div'),
      pre = document.createElement('pre'),
      result = document.createElement('code');
    div.setAttribute("id", py_div_id_prefix + py_div_id_count);
    py_div_id_count += 1;

    div.style.border = '1px solid #C3CCD0';
    div.style.margin = '40px 10px';
    div.style.paddingLeft = '10px';

    result.innerHTML = "Loading pyodide";
    pre.appendChild(result);
    div.appendChild(pre);
    document.body.appendChild(div);
  }

  function executePyCell(line_list) {
    var result, code_text = line_list.join('\n');
    result = window.pyodide.runPython(code_text);
    renderCodeblock(result);
  }

  function pyodideSetting() {
    window.pyodide = pyodide(Module);
    window.pyodide.loadPackage = pyodideLoadPackage;

    var defer = RSVP.defer(),
      promise = defer.promise;

    Module.postRun = defer.resolve;
    promise.then(function () {
      console.log("postRun get called");
      delete window.Module;
    });

    return defer.promise;
  }

  Module.checkABI = function(ABI_number) {
    if (ABI_number !== parseInt('1')) {
      var ABI_mismatch_exception = `ABI numbers differ. Expected 1, got ${ABI_number}`;
      console.error(ABI_mismatch_exception);
      throw ABI_mismatch_exception;
    }
    return true;
  };

  function initPyodide() {
    var queue = new RSVP.Queue();
    queue.push(function () {
        Module.instantiateWasm = loadPyodide;
        window.Module = Module;
      })
      .push(function () {
        return loadJSResource('pyodide.asm.data.js');
      })
      .push(function () {
        return loadJSResource('pyodide.asm.js');
      })
      .push(function () {
        return pyodideSetting();
      })
      .push(function () {
        return ajax({
          url: 'packages.json'
        });
      })
      .push(function (evt) {
        return JSON.parse(evt.target.response);
      })
      .push(function (json) {
        window.pyodide._module = Module;
        window.pyodide.loadedPackages = [];
        window.pyodide._module.packages = json;
        return;
      })
      .push(undefined, function (error) {
        console.log(error);
      });
    return queue;
  }

  function executeCell(cell) {
    if (['raw', 'meta', 'plugin'].indexOf(cell._type) !== -1) {
      // Do nothing...
      return;
    }
    if (cell._type === 'js' || cell._type === 'code_js') {
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
    if (cell._type === 'code_py') {
      if (cell._line_list.length === 0) {
        // empty block, do nothing.
        return;
      }
      var queue = new RSVP.Queue();
      if (is_pyodide_loaded === false) {
        queue.push(function () {
            return initPyodide();
          })
          .push(function () {
            return pyodideLoadPackage('matplotlib');
          });
        is_pyodide_loaded = true;
      }

      queue.push(function () {
        return executePyCell(cell._line_list);
      });
      return queue
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
        var pre = document.createElement('pre');
        pre.textContent = error;
        document.body.appendChild(pre);
      });

  }, false);

}(window));