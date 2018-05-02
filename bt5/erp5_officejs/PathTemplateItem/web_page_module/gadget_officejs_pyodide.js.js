var languagePluginLoader = new Promise((resolve, reject) => {
    let baseURL = "";
    let wasmURL = `${baseURL}pyodide.asm.wasm`;
    let wasmXHR = new XMLHttpRequest();
    wasmXHR.open('GET', wasmURL, true);
    wasmXHR.responseType = 'arraybuffer';
    wasmXHR.onload = function() {
        let Module = {};

        if (wasmXHR.status === 200 || wasmXHR.status === 0) {
            Module.wasmBinary = wasmXHR.response;
        } else {
            console.warn(
                `Couldn't download the pyodide.asm.wasm binary.  Response was ${wasmXHR.status}`);
            reject();
        }

        Module.baseURL = baseURL;
        Module.postRun = () => {
            resolve();
        }
        let script = document.createElement('script');
        script.src = `pyodide.asm.js`;
        script.onload = () => {
            window.pyodide = pyodide(Module);
        };
        document.body.appendChild(script);
    };
    wasmXHR.send(null);
});
languagePluginLoader