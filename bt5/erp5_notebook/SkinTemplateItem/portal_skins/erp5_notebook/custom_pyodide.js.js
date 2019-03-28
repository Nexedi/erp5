var initPyodide = new Promise((resolve, reject) => {

  // Loading Pyodide
  let wasmURL = `pyodide.asm.wasm`;
  let Module = {};
  window.Module = Module;

  let wasm_promise = WebAssembly.compileStreaming(fetch(wasmURL));
  Module.instantiateWasm = (info, receiveInstance) => {
    wasm_promise.then(module => WebAssembly.instantiate(module, info))
        .then(instance => receiveInstance(instance));
    return {};
  };

  var postRunPromise = new Promise((resolve, reject) => {
    Module.postRun = () => {
      resolve();
    };
  });

  Promise.all([ postRunPromise, ]).then(() => resolve());

  let data_script = document.createElement('script');
  data_script.src = `pyodide.asm.data.js`;
  data_script.onload = (event) => {
    let script = document.createElement('script');
    script.src = `pyodide.asm.js`;
    script.onload = () => {
      window.pyodide = pyodide(Module);
    };
    document.head.appendChild(script);
  };

  document.head.appendChild(data_script);
});
initPyodide
