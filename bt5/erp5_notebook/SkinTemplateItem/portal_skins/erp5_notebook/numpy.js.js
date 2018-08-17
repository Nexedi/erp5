
var Module = typeof pyodide !== 'undefined' ? pyodide : {};

if (!Module.expectedDataFileDownloads) {
  Module.expectedDataFileDownloads = 0;
  Module.finishedDataFileDownloads = 0;
}
Module.expectedDataFileDownloads++;
(function() {
 var loadPackage = function(metadata) {

    var PACKAGE_PATH;
    if (typeof window === 'object') {
      PACKAGE_PATH = window['encodeURIComponent'](window.location.pathname.toString().substring(0, window.location.pathname.toString().lastIndexOf('/')) + '/');
    } else if (typeof location !== 'undefined') {
      // worker
      PACKAGE_PATH = encodeURIComponent(location.pathname.toString().substring(0, location.pathname.toString().lastIndexOf('/')) + '/');
    } else {
      throw 'using preloaded data can only be done on a web page or in a web worker';
    }
    var PACKAGE_NAME = '/home/nexedir/pyodide/packages/numpy/build/numpy.data';
    var REMOTE_PACKAGE_BASE = 'numpy.data';
    if (typeof Module['locateFilePackage'] === 'function' && !Module['locateFile']) {
      Module['locateFile'] = Module['locateFilePackage'];
      err('warning: you defined Module.locateFilePackage, that has been renamed to Module.locateFile (using your locateFilePackage for now)');
    }
    var REMOTE_PACKAGE_NAME = Module['locateFile'] ? Module['locateFile'](REMOTE_PACKAGE_BASE, '') : REMOTE_PACKAGE_BASE;
  
    var REMOTE_PACKAGE_SIZE = metadata.remote_package_size;
    var PACKAGE_UUID = metadata.package_uuid;
  
    function fetchRemotePackage(packageName, packageSize, callback, errback) {
      var xhr = new XMLHttpRequest();
      xhr.open('GET', packageName, true);
      xhr.responseType = 'arraybuffer';
      xhr.onprogress = function(event) {
        var url = packageName;
        var size = packageSize;
        if (event.total) size = event.total;
        if (event.loaded) {
          if (!xhr.addedTotal) {
            xhr.addedTotal = true;
            if (!Module.dataFileDownloads) Module.dataFileDownloads = {};
            Module.dataFileDownloads[url] = {
              loaded: event.loaded,
              total: size
            };
          } else {
            Module.dataFileDownloads[url].loaded = event.loaded;
          }
          var total = 0;
          var loaded = 0;
          var num = 0;
          for (var download in Module.dataFileDownloads) {
          var data = Module.dataFileDownloads[download];
            total += data.total;
            loaded += data.loaded;
            num++;
          }
          total = Math.ceil(total * Module.expectedDataFileDownloads/num);
          if (Module['setStatus']) Module['setStatus']('Downloading data... (' + loaded + '/' + total + ')');
        } else if (!Module.dataFileDownloads) {
          if (Module['setStatus']) Module['setStatus']('Downloading data...');
        }
      };
      xhr.onerror = function(event) {
        throw new Error("NetworkError for: " + packageName);
      }
      xhr.onload = function(event) {
        if (xhr.status == 200 || xhr.status == 304 || xhr.status == 206 || (xhr.status == 0 && xhr.response)) { // file URLs can return 0
          var packageData = xhr.response;
          callback(packageData);
        } else {
          throw new Error(xhr.statusText + " : " + xhr.responseURL);
        }
      };
      xhr.send(null);
    };

    function handleError(error) {
      console.error('package error:', error);
    };
  
      var fetchedCallback = null;
      var fetched = Module['getPreloadedPackage'] ? Module['getPreloadedPackage'](REMOTE_PACKAGE_NAME, REMOTE_PACKAGE_SIZE) : null;

      if (!fetched) fetchRemotePackage(REMOTE_PACKAGE_NAME, REMOTE_PACKAGE_SIZE, function(data) {
        if (fetchedCallback) {
          fetchedCallback(data);
          fetchedCallback = null;
        } else {
          fetched = data;
        }
      }, handleError);
    
  function runWithFS() {

    function assert(check, msg) {
      if (!check) throw msg + new Error().stack;
    }
Module['FS_createPath']('/', 'lib', true, true);
Module['FS_createPath']('/lib', 'python3.6', true, true);
Module['FS_createPath']('/lib/python3.6', 'site-packages', true, true);
Module['FS_createPath']('/lib/python3.6/site-packages', 'numpy', true, true);
Module['FS_createPath']('/lib/python3.6/site-packages/numpy', 'f2py', true, true);
Module['FS_createPath']('/lib/python3.6/site-packages/numpy', 'polynomial', true, true);
Module['FS_createPath']('/lib/python3.6/site-packages/numpy', 'ma', true, true);
Module['FS_createPath']('/lib/python3.6/site-packages/numpy', 'compat', true, true);
Module['FS_createPath']('/lib/python3.6/site-packages/numpy', 'linalg', true, true);
Module['FS_createPath']('/lib/python3.6/site-packages/numpy', 'testing', true, true);
Module['FS_createPath']('/lib/python3.6/site-packages/numpy/testing', 'nose_tools', true, true);
Module['FS_createPath']('/lib/python3.6/site-packages/numpy', 'matrixlib', true, true);
Module['FS_createPath']('/lib/python3.6/site-packages/numpy', 'lib', true, true);
Module['FS_createPath']('/lib/python3.6/site-packages/numpy', 'fft', true, true);
Module['FS_createPath']('/lib/python3.6/site-packages/numpy', 'core', true, true);
Module['FS_createPath']('/lib/python3.6/site-packages/numpy', 'random', true, true);
Module['FS_createPath']('/lib/python3.6/site-packages/numpy', 'doc', true, true);
Module['FS_createPath']('/lib/python3.6/site-packages/numpy', 'distutils', true, true);
Module['FS_createPath']('/lib/python3.6/site-packages/numpy/distutils', 'command', true, true);
Module['FS_createPath']('/lib/python3.6/site-packages/numpy/distutils', 'fcompiler', true, true);

    function DataRequest(start, end, audio) {
      this.start = start;
      this.end = end;
      this.audio = audio;
    }
    DataRequest.prototype = {
      requests: {},
      open: function(mode, name) {
        this.name = name;
        this.requests[name] = this;
        Module['addRunDependency']('fp ' + this.name);
      },
      send: function() {},
      onload: function() {
        var byteArray = this.byteArray.subarray(this.start, this.end);
        this.finish(byteArray);
      },
      finish: function(byteArray) {
        var that = this;

        Module['FS_createPreloadedFile'](this.name, null, byteArray, true, true, function() {
          Module['removeRunDependency']('fp ' + that.name);
        }, function() {
          if (that.audio) {
            Module['removeRunDependency']('fp ' + that.name); // workaround for chromium bug 124926 (still no audio with this, but at least we don't hang)
          } else {
            err('Preloading file ' + that.name + ' failed');
          }
        }, false, true); // canOwn this data in the filesystem, it is a slide into the heap that will never change

        this.requests[this.name] = null;
      }
    };

        var files = metadata.files;
        for (var i = 0; i < files.length; ++i) {
          new DataRequest(files[i].start, files[i].end, files[i].audio).open('GET', files[i].filename);
        }

  
    function processPackageData(arrayBuffer) {
      Module.finishedDataFileDownloads++;
      assert(arrayBuffer, 'Loading data file failed.');
      assert(arrayBuffer instanceof ArrayBuffer, 'bad input to processPackageData');
      var byteArray = new Uint8Array(arrayBuffer);
      var curr;
      
        // copy the entire loaded file into a spot in the heap. Files will refer to slices in that. They cannot be freed though
        // (we may be allocating before malloc is ready, during startup).
        if (Module['SPLIT_MEMORY']) err('warning: you should run the file packager with --no-heap-copy when SPLIT_MEMORY is used, otherwise copying into the heap may fail due to the splitting');
        var ptr = Module['getMemory'](byteArray.length);
        Module['HEAPU8'].set(byteArray, ptr);
        DataRequest.prototype.byteArray = Module['HEAPU8'].subarray(ptr, ptr+byteArray.length);
  
          var files = metadata.files;
          for (var i = 0; i < files.length; ++i) {
            DataRequest.prototype.requests[files[i].filename].onload();
          }
              Module['removeRunDependency']('datafile_/home/nexedir/pyodide/packages/numpy/build/numpy.data');

    };
    Module['addRunDependency']('datafile_/home/nexedir/pyodide/packages/numpy/build/numpy.data');
  
    if (!Module.preloadResults) Module.preloadResults = {};
  
      Module.preloadResults[PACKAGE_NAME] = {fromCache: false};
      if (fetched) {
        processPackageData(fetched);
        fetched = null;
      } else {
        fetchedCallback = processPackageData;
      }
    
  }
  if (Module['calledRun']) {
    runWithFS();
  } else {
    if (!Module['preRun']) Module['preRun'] = [];
    Module["preRun"].push(runWithFS); // FS is not initialized yet, wait for it
  }

 }
 loadPackage({"files": [{"start": 0, "audio": 0, "end": 331, "filename": "/lib/python3.6/site-packages/numpy/_distributor_init.py"}, {"start": 331, "audio": 0, "end": 15061, "filename": "/lib/python3.6/site-packages/numpy/ctypeslib.py"}, {"start": 15061, "audio": 0, "end": 16361, "filename": "/lib/python3.6/site-packages/numpy/__config__.py"}, {"start": 16361, "audio": 0, "end": 17918, "filename": "/lib/python3.6/site-packages/numpy/conftest.py"}, {"start": 17918, "audio": 0, "end": 24169, "filename": "/lib/python3.6/site-packages/numpy/__init__.py"}, {"start": 24169, "audio": 0, "end": 24463, "filename": "/lib/python3.6/site-packages/numpy/version.py"}, {"start": 24463, "audio": 0, "end": 34272, "filename": "/lib/python3.6/site-packages/numpy/matlib.py"}, {"start": 34272, "audio": 0, "end": 36136, "filename": "/lib/python3.6/site-packages/numpy/dual.py"}, {"start": 36136, "audio": 0, "end": 49370, "filename": "/lib/python3.6/site-packages/numpy/_import_tools.py"}, {"start": 49370, "audio": 0, "end": 50290, "filename": "/lib/python3.6/site-packages/numpy/setup.py"}, {"start": 50290, "audio": 0, "end": 52149, "filename": "/lib/python3.6/site-packages/numpy/_globals.py"}, {"start": 52149, "audio": 0, "end": 286896, "filename": "/lib/python3.6/site-packages/numpy/add_newdocs.py"}, {"start": 286896, "audio": 0, "end": 288923, "filename": "/lib/python3.6/site-packages/numpy/f2py/__init__.py"}, {"start": 288923, "audio": 0, "end": 292575, "filename": "/lib/python3.6/site-packages/numpy/f2py/use_rules.py"}, {"start": 292575, "audio": 0, "end": 294098, "filename": "/lib/python3.6/site-packages/numpy/f2py/f2py_testing.py"}, {"start": 294098, "audio": 0, "end": 316454, "filename": "/lib/python3.6/site-packages/numpy/f2py/cb_rules.py"}, {"start": 316454, "audio": 0, "end": 321749, "filename": "/lib/python3.6/site-packages/numpy/f2py/diagnose.py"}, {"start": 321749, "audio": 0, "end": 325674, "filename": "/lib/python3.6/site-packages/numpy/f2py/setup.py"}, {"start": 325674, "audio": 0, "end": 370787, "filename": "/lib/python3.6/site-packages/numpy/f2py/cfuncs.py"}, {"start": 370787, "audio": 0, "end": 370923, "filename": "/lib/python3.6/site-packages/numpy/f2py/info.py"}, {"start": 370923, "audio": 0, "end": 380147, "filename": "/lib/python3.6/site-packages/numpy/f2py/func2subr.py"}, {"start": 380147, "audio": 0, "end": 403055, "filename": "/lib/python3.6/site-packages/numpy/f2py/f2py2e.py"}, {"start": 403055, "audio": 0, "end": 424881, "filename": "/lib/python3.6/site-packages/numpy/f2py/auxfuncs.py"}, {"start": 424881, "audio": 0, "end": 456420, "filename": "/lib/python3.6/site-packages/numpy/f2py/capi_maps.py"}, {"start": 456420, "audio": 0, "end": 514945, "filename": "/lib/python3.6/site-packages/numpy/f2py/rules.py"}, {"start": 514945, "audio": 0, "end": 643349, "filename": "/lib/python3.6/site-packages/numpy/f2py/crackfortran.py"}, {"start": 643349, "audio": 0, "end": 648379, "filename": "/lib/python3.6/site-packages/numpy/f2py/common_rules.py"}, {"start": 648379, "audio": 0, "end": 649118, "filename": "/lib/python3.6/site-packages/numpy/f2py/__main__.py"}, {"start": 649118, "audio": 0, "end": 649372, "filename": "/lib/python3.6/site-packages/numpy/f2py/__version__.py"}, {"start": 649372, "audio": 0, "end": 659222, "filename": "/lib/python3.6/site-packages/numpy/f2py/f90mod_rules.py"}, {"start": 659222, "audio": 0, "end": 716626, "filename": "/lib/python3.6/site-packages/numpy/polynomial/legendre.py"}, {"start": 716626, "audio": 0, "end": 774522, "filename": "/lib/python3.6/site-packages/numpy/polynomial/hermite.py"}, {"start": 774522, "audio": 0, "end": 830831, "filename": "/lib/python3.6/site-packages/numpy/polynomial/laguerre.py"}, {"start": 830831, "audio": 0, "end": 888917, "filename": "/lib/python3.6/site-packages/numpy/polynomial/hermite_e.py"}, {"start": 888917, "audio": 0, "end": 890057, "filename": "/lib/python3.6/site-packages/numpy/polynomial/__init__.py"}, {"start": 890057, "audio": 0, "end": 920149, "filename": "/lib/python3.6/site-packages/numpy/polynomial/_polybase.py"}, {"start": 920149, "audio": 0, "end": 920534, "filename": "/lib/python3.6/site-packages/numpy/polynomial/setup.py"}, {"start": 920534, "audio": 0, "end": 973342, "filename": "/lib/python3.6/site-packages/numpy/polynomial/polynomial.py"}, {"start": 973342, "audio": 0, "end": 1040311, "filename": "/lib/python3.6/site-packages/numpy/polynomial/chebyshev.py"}, {"start": 1040311, "audio": 0, "end": 1051840, "filename": "/lib/python3.6/site-packages/numpy/polynomial/polyutils.py"}, {"start": 1051840, "audio": 0, "end": 1053316, "filename": "/lib/python3.6/site-packages/numpy/ma/__init__.py"}, {"start": 1053316, "audio": 0, "end": 1058233, "filename": "/lib/python3.6/site-packages/numpy/ma/bench.py"}, {"start": 1058233, "audio": 0, "end": 1068617, "filename": "/lib/python3.6/site-packages/numpy/ma/testutils.py"}, {"start": 1068617, "audio": 0, "end": 1068997, "filename": "/lib/python3.6/site-packages/numpy/ma/version.py"}, {"start": 1068997, "audio": 0, "end": 1096432, "filename": "/lib/python3.6/site-packages/numpy/ma/mrecords.py"}, {"start": 1096432, "audio": 0, "end": 1112018, "filename": "/lib/python3.6/site-packages/numpy/ma/timer_comparison.py"}, {"start": 1112018, "audio": 0, "end": 1167981, "filename": "/lib/python3.6/site-packages/numpy/ma/extras.py"}, {"start": 1167981, "audio": 0, "end": 1168410, "filename": "/lib/python3.6/site-packages/numpy/ma/setup.py"}, {"start": 1168410, "audio": 0, "end": 1424253, "filename": "/lib/python3.6/site-packages/numpy/ma/core.py"}, {"start": 1424253, "audio": 0, "end": 1427890, "filename": "/lib/python3.6/site-packages/numpy/compat/py3k.py"}, {"start": 1427890, "audio": 0, "end": 1428388, "filename": "/lib/python3.6/site-packages/numpy/compat/__init__.py"}, {"start": 1428388, "audio": 0, "end": 1428759, "filename": "/lib/python3.6/site-packages/numpy/compat/setup.py"}, {"start": 1428759, "audio": 0, "end": 1436313, "filename": "/lib/python3.6/site-packages/numpy/compat/_inspect.py"}, {"start": 1436313, "audio": 0, "end": 1438645, "filename": "/lib/python3.6/site-packages/numpy/linalg/__init__.py"}, {"start": 1438645, "audio": 0, "end": 1519082, "filename": "/lib/python3.6/site-packages/numpy/linalg/linalg.py"}, {"start": 1519082, "audio": 0, "end": 1520960, "filename": "/lib/python3.6/site-packages/numpy/linalg/setup.py"}, {"start": 1520960, "audio": 0, "end": 1522158, "filename": "/lib/python3.6/site-packages/numpy/linalg/info.py"}, {"start": 1522158, "audio": 0, "end": 2892108, "filename": "/lib/python3.6/site-packages/numpy/linalg/lapack_lite.so"}, {"start": 2892108, "audio": 0, "end": 4354731, "filename": "/lib/python3.6/site-packages/numpy/linalg/_umath_linalg.so"}, {"start": 4354731, "audio": 0, "end": 4355020, "filename": "/lib/python3.6/site-packages/numpy/testing/nosetester.py"}, {"start": 4355020, "audio": 0, "end": 4357725, "filename": "/lib/python3.6/site-packages/numpy/testing/print_coercion_tables.py"}, {"start": 4357725, "audio": 0, "end": 4357855, "filename": "/lib/python3.6/site-packages/numpy/testing/noseclasses.py"}, {"start": 4357855, "audio": 0, "end": 4358330, "filename": "/lib/python3.6/site-packages/numpy/testing/__init__.py"}, {"start": 4358330, "audio": 0, "end": 4359256, "filename": "/lib/python3.6/site-packages/numpy/testing/utils.py"}, {"start": 4359256, "audio": 0, "end": 4359384, "filename": "/lib/python3.6/site-packages/numpy/testing/decorators.py"}, {"start": 4359384, "audio": 0, "end": 4360061, "filename": "/lib/python3.6/site-packages/numpy/testing/setup.py"}, {"start": 4360061, "audio": 0, "end": 4380623, "filename": "/lib/python3.6/site-packages/numpy/testing/nose_tools/nosetester.py"}, {"start": 4380623, "audio": 0, "end": 4395222, "filename": "/lib/python3.6/site-packages/numpy/testing/nose_tools/noseclasses.py"}, {"start": 4395222, "audio": 0, "end": 4395222, "filename": "/lib/python3.6/site-packages/numpy/testing/nose_tools/__init__.py"}, {"start": 4395222, "audio": 0, "end": 4470656, "filename": "/lib/python3.6/site-packages/numpy/testing/nose_tools/utils.py"}, {"start": 4470656, "audio": 0, "end": 4479247, "filename": "/lib/python3.6/site-packages/numpy/testing/nose_tools/decorators.py"}, {"start": 4479247, "audio": 0, "end": 4497533, "filename": "/lib/python3.6/site-packages/numpy/testing/nose_tools/parameterized.py"}, {"start": 4497533, "audio": 0, "end": 4530506, "filename": "/lib/python3.6/site-packages/numpy/matrixlib/defmatrix.py"}, {"start": 4530506, "audio": 0, "end": 4530796, "filename": "/lib/python3.6/site-packages/numpy/matrixlib/__init__.py"}, {"start": 4530796, "audio": 0, "end": 4531244, "filename": "/lib/python3.6/site-packages/numpy/matrixlib/setup.py"}, {"start": 4531244, "audio": 0, "end": 4545329, "filename": "/lib/python3.6/site-packages/numpy/lib/scimath.py"}, {"start": 4545329, "audio": 0, "end": 4574485, "filename": "/lib/python3.6/site-packages/numpy/lib/format.py"}, {"start": 4574485, "audio": 0, "end": 4599796, "filename": "/lib/python3.6/site-packages/numpy/lib/_datasource.py"}, {"start": 4599796, "audio": 0, "end": 4604663, "filename": "/lib/python3.6/site-packages/numpy/lib/_version.py"}, {"start": 4604663, "audio": 0, "end": 4633331, "filename": "/lib/python3.6/site-packages/numpy/lib/shape_base.py"}, {"start": 4633331, "audio": 0, "end": 4659148, "filename": "/lib/python3.6/site-packages/numpy/lib/twodim_base.py"}, {"start": 4659148, "audio": 0, "end": 4698822, "filename": "/lib/python3.6/site-packages/numpy/lib/recfunctions.py"}, {"start": 4698822, "audio": 0, "end": 4700123, "filename": "/lib/python3.6/site-packages/numpy/lib/__init__.py"}, {"start": 4700123, "audio": 0, "end": 4724618, "filename": "/lib/python3.6/site-packages/numpy/lib/financial.py"}, {"start": 4724618, "audio": 0, "end": 4757234, "filename": "/lib/python3.6/site-packages/numpy/lib/_iotools.py"}, {"start": 4757234, "audio": 0, "end": 4793574, "filename": "/lib/python3.6/site-packages/numpy/lib/utils.py"}, {"start": 4793574, "audio": 0, "end": 4876746, "filename": "/lib/python3.6/site-packages/numpy/lib/npyio.py"}, {"start": 4876746, "audio": 0, "end": 4903426, "filename": "/lib/python3.6/site-packages/numpy/lib/index_tricks.py"}, {"start": 4903426, "audio": 0, "end": 4910617, "filename": "/lib/python3.6/site-packages/numpy/lib/arrayterator.py"}, {"start": 4910617, "audio": 0, "end": 4961471, "filename": "/lib/python3.6/site-packages/numpy/lib/nanfunctions.py"}, {"start": 4961471, "audio": 0, "end": 4982038, "filename": "/lib/python3.6/site-packages/numpy/lib/arraysetops.py"}, {"start": 4982038, "audio": 0, "end": 5033895, "filename": "/lib/python3.6/site-packages/numpy/lib/arraypad.py"}, {"start": 5033895, "audio": 0, "end": 5034274, "filename": "/lib/python3.6/site-packages/numpy/lib/setup.py"}, {"start": 5034274, "audio": 0, "end": 5072846, "filename": "/lib/python3.6/site-packages/numpy/lib/polynomial.py"}, {"start": 5072846, "audio": 0, "end": 5080130, "filename": "/lib/python3.6/site-packages/numpy/lib/mixins.py"}, {"start": 5080130, "audio": 0, "end": 5086746, "filename": "/lib/python3.6/site-packages/numpy/lib/info.py"}, {"start": 5086746, "audio": 0, "end": 5094563, "filename": "/lib/python3.6/site-packages/numpy/lib/user_array.py"}, {"start": 5094563, "audio": 0, "end": 5264595, "filename": "/lib/python3.6/site-packages/numpy/lib/function_base.py"}, {"start": 5264595, "audio": 0, "end": 5273380, "filename": "/lib/python3.6/site-packages/numpy/lib/stride_tricks.py"}, {"start": 5273380, "audio": 0, "end": 5279094, "filename": "/lib/python3.6/site-packages/numpy/lib/ufunclike.py"}, {"start": 5279094, "audio": 0, "end": 5295594, "filename": "/lib/python3.6/site-packages/numpy/lib/type_check.py"}, {"start": 5295594, "audio": 0, "end": 5341653, "filename": "/lib/python3.6/site-packages/numpy/fft/fftpack.py"}, {"start": 5341653, "audio": 0, "end": 5341911, "filename": "/lib/python3.6/site-packages/numpy/fft/__init__.py"}, {"start": 5341911, "audio": 0, "end": 5379678, "filename": "/lib/python3.6/site-packages/numpy/fft/fftpack_lite.so"}, {"start": 5379678, "audio": 0, "end": 5380228, "filename": "/lib/python3.6/site-packages/numpy/fft/setup.py"}, {"start": 5380228, "audio": 0, "end": 5387463, "filename": "/lib/python3.6/site-packages/numpy/fft/info.py"}, {"start": 5387463, "audio": 0, "end": 5397055, "filename": "/lib/python3.6/site-packages/numpy/fft/helper.py"}, {"start": 5397055, "audio": 0, "end": 5413008, "filename": "/lib/python3.6/site-packages/numpy/core/setup_common.py"}, {"start": 5413008, "audio": 0, "end": 5442110, "filename": "/lib/python3.6/site-packages/numpy/core/numerictypes.py"}, {"start": 5442110, "audio": 0, "end": 5460926, "filename": "/lib/python3.6/site-packages/numpy/core/shape_base.py"}, {"start": 5460926, "audio": 0, "end": 5472358, "filename": "/lib/python3.6/site-packages/numpy/core/memmap.py"}, {"start": 5472358, "audio": 0, "end": 5513050, "filename": "/lib/python3.6/site-packages/numpy/core/einsumfunc.py"}, {"start": 5513050, "audio": 0, "end": 5516094, "filename": "/lib/python3.6/site-packages/numpy/core/__init__.py"}, {"start": 5516094, "audio": 0, "end": 5534516, "filename": "/lib/python3.6/site-packages/numpy/core/getlimits.py"}, {"start": 5534516, "audio": 0, "end": 5546748, "filename": "/lib/python3.6/site-packages/numpy/core/umath_tests.so"}, {"start": 5546748, "audio": 0, "end": 5547161, "filename": "/lib/python3.6/site-packages/numpy/core/cversions.py"}, {"start": 5547161, "audio": 0, "end": 5604426, "filename": "/lib/python3.6/site-packages/numpy/core/arrayprint.py"}, {"start": 5604426, "audio": 0, "end": 5615215, "filename": "/lib/python3.6/site-packages/numpy/core/machar.py"}, {"start": 5615215, "audio": 0, "end": 5622721, "filename": "/lib/python3.6/site-packages/numpy/core/generate_numpy_api.py"}, {"start": 5622721, "audio": 0, "end": 7444814, "filename": "/lib/python3.6/site-packages/numpy/core/multiarray.so"}, {"start": 7444814, "audio": 0, "end": 7449518, "filename": "/lib/python3.6/site-packages/numpy/core/_methods.py"}, {"start": 7449518, "audio": 0, "end": 7490995, "filename": "/lib/python3.6/site-packages/numpy/core/setup.py"}, {"start": 7490995, "audio": 0, "end": 7547836, "filename": "/lib/python3.6/site-packages/numpy/core/test_rational.so"}, {"start": 7547836, "audio": 0, "end": 7548520, "filename": "/lib/python3.6/site-packages/numpy/core/_dummy.so"}, {"start": 7548520, "audio": 0, "end": 7649157, "filename": "/lib/python3.6/site-packages/numpy/core/fromnumeric.py"}, {"start": 7649157, "audio": 0, "end": 7716526, "filename": "/lib/python3.6/site-packages/numpy/core/defchararray.py"}, {"start": 7716526, "audio": 0, "end": 7721218, "filename": "/lib/python3.6/site-packages/numpy/core/info.py"}, {"start": 7721218, "audio": 0, "end": 7725606, "filename": "/lib/python3.6/site-packages/numpy/core/struct_ufunc_test.so"}, {"start": 7725606, "audio": 0, "end": 7755699, "filename": "/lib/python3.6/site-packages/numpy/core/records.py"}, {"start": 7755699, "audio": 0, "end": 7869232, "filename": "/lib/python3.6/site-packages/numpy/core/multiarray_tests.so"}, {"start": 7869232, "audio": 0, "end": 7881572, "filename": "/lib/python3.6/site-packages/numpy/core/function_base.py"}, {"start": 7881572, "audio": 0, "end": 7967303, "filename": "/lib/python3.6/site-packages/numpy/core/numeric.py"}, {"start": 7967303, "audio": 0, "end": 7970985, "filename": "/lib/python3.6/site-packages/numpy/core/operand_flag_tests.so"}, {"start": 7970985, "audio": 0, "end": 7992801, "filename": "/lib/python3.6/site-packages/numpy/core/_internal.py"}, {"start": 7992801, "audio": 0, "end": 8757415, "filename": "/lib/python3.6/site-packages/numpy/core/umath.so"}, {"start": 8757415, "audio": 0, "end": 8762896, "filename": "/lib/python3.6/site-packages/numpy/random/__init__.py"}, {"start": 8762896, "audio": 0, "end": 9972220, "filename": "/lib/python3.6/site-packages/numpy/random/mtrand.so"}, {"start": 9972220, "audio": 0, "end": 9974532, "filename": "/lib/python3.6/site-packages/numpy/random/setup.py"}, {"start": 9974532, "audio": 0, "end": 9979731, "filename": "/lib/python3.6/site-packages/numpy/random/info.py"}, {"start": 9979731, "audio": 0, "end": 9988613, "filename": "/lib/python3.6/site-packages/numpy/doc/constants.py"}, {"start": 9988613, "audio": 0, "end": 9989187, "filename": "/lib/python3.6/site-packages/numpy/doc/__init__.py"}, {"start": 9989187, "audio": 0, "end": 9995381, "filename": "/lib/python3.6/site-packages/numpy/doc/misc.py"}, {"start": 9995381, "audio": 0, "end": 10023941, "filename": "/lib/python3.6/site-packages/numpy/doc/subclassing.py"}, {"start": 10023941, "audio": 0, "end": 10048384, "filename": "/lib/python3.6/site-packages/numpy/doc/structured_arrays.py"}, {"start": 10048384, "audio": 0, "end": 10053949, "filename": "/lib/python3.6/site-packages/numpy/doc/broadcasting.py"}, {"start": 10053949, "audio": 0, "end": 10061867, "filename": "/lib/python3.6/site-packages/numpy/doc/basics.py"}, {"start": 10061867, "audio": 0, "end": 10067294, "filename": "/lib/python3.6/site-packages/numpy/doc/ufuncs.py"}, {"start": 10067294, "audio": 0, "end": 10082963, "filename": "/lib/python3.6/site-packages/numpy/doc/indexing.py"}, {"start": 10082963, "audio": 0, "end": 10088309, "filename": "/lib/python3.6/site-packages/numpy/doc/byteswapping.py"}, {"start": 10088309, "audio": 0, "end": 10097978, "filename": "/lib/python3.6/site-packages/numpy/doc/internals.py"}, {"start": 10097978, "audio": 0, "end": 10103479, "filename": "/lib/python3.6/site-packages/numpy/doc/creation.py"}, {"start": 10103479, "audio": 0, "end": 10115850, "filename": "/lib/python3.6/site-packages/numpy/doc/glossary.py"}, {"start": 10115850, "audio": 0, "end": 10117150, "filename": "/lib/python3.6/site-packages/numpy/distutils/__config__.py"}, {"start": 10117150, "audio": 0, "end": 10122306, "filename": "/lib/python3.6/site-packages/numpy/distutils/unixccompiler.py"}, {"start": 10122306, "audio": 0, "end": 10124564, "filename": "/lib/python3.6/site-packages/numpy/distutils/msvc9compiler.py"}, {"start": 10124564, "audio": 0, "end": 10126555, "filename": "/lib/python3.6/site-packages/numpy/distutils/msvccompiler.py"}, {"start": 10126555, "audio": 0, "end": 10130846, "filename": "/lib/python3.6/site-packages/numpy/distutils/intelccompiler.py"}, {"start": 10130846, "audio": 0, "end": 10131064, "filename": "/lib/python3.6/site-packages/numpy/distutils/compat.py"}, {"start": 10131064, "audio": 0, "end": 10156265, "filename": "/lib/python3.6/site-packages/numpy/distutils/mingw32ccompiler.py"}, {"start": 10156265, "audio": 0, "end": 10165974, "filename": "/lib/python3.6/site-packages/numpy/distutils/conv_template.py"}, {"start": 10165974, "audio": 0, "end": 10173804, "filename": "/lib/python3.6/site-packages/numpy/distutils/from_template.py"}, {"start": 10173804, "audio": 0, "end": 10187047, "filename": "/lib/python3.6/site-packages/numpy/distutils/npy_pkg_config.py"}, {"start": 10187047, "audio": 0, "end": 10269326, "filename": "/lib/python3.6/site-packages/numpy/distutils/misc_util.py"}, {"start": 10269326, "audio": 0, "end": 10270414, "filename": "/lib/python3.6/site-packages/numpy/distutils/__init__.py"}, {"start": 10270414, "audio": 0, "end": 10273159, "filename": "/lib/python3.6/site-packages/numpy/distutils/log.py"}, {"start": 10273159, "audio": 0, "end": 10276671, "filename": "/lib/python3.6/site-packages/numpy/distutils/lib2def.py"}, {"start": 10276671, "audio": 0, "end": 10285334, "filename": "/lib/python3.6/site-packages/numpy/distutils/exec_command.py"}, {"start": 10285334, "audio": 0, "end": 10313881, "filename": "/lib/python3.6/site-packages/numpy/distutils/ccompiler.py"}, {"start": 10313881, "audio": 0, "end": 10336896, "filename": "/lib/python3.6/site-packages/numpy/distutils/cpuinfo.py"}, {"start": 10336896, "audio": 0, "end": 10337507, "filename": "/lib/python3.6/site-packages/numpy/distutils/setup.py"}, {"start": 10337507, "audio": 0, "end": 10337664, "filename": "/lib/python3.6/site-packages/numpy/distutils/info.py"}, {"start": 10337664, "audio": 0, "end": 10338443, "filename": "/lib/python3.6/site-packages/numpy/distutils/pathccompiler.py"}, {"start": 10338443, "audio": 0, "end": 10339143, "filename": "/lib/python3.6/site-packages/numpy/distutils/numpy_distribution.py"}, {"start": 10339143, "audio": 0, "end": 10342110, "filename": "/lib/python3.6/site-packages/numpy/distutils/extension.py"}, {"start": 10342110, "audio": 0, "end": 10350293, "filename": "/lib/python3.6/site-packages/numpy/distutils/core.py"}, {"start": 10350293, "audio": 0, "end": 10352346, "filename": "/lib/python3.6/site-packages/numpy/distutils/line_endings.py"}, {"start": 10352346, "audio": 0, "end": 10354692, "filename": "/lib/python3.6/site-packages/numpy/distutils/environment.py"}, {"start": 10354692, "audio": 0, "end": 10444193, "filename": "/lib/python3.6/site-packages/numpy/distutils/system_info.py"}, {"start": 10444193, "audio": 0, "end": 10444344, "filename": "/lib/python3.6/site-packages/numpy/distutils/__version__.py"}, {"start": 10444344, "audio": 0, "end": 10445258, "filename": "/lib/python3.6/site-packages/numpy/distutils/command/install_data.py"}, {"start": 10445258, "audio": 0, "end": 10446033, "filename": "/lib/python3.6/site-packages/numpy/distutils/command/bdist_rpm.py"}, {"start": 10446033, "audio": 0, "end": 10449160, "filename": "/lib/python3.6/site-packages/numpy/distutils/command/install.py"}, {"start": 10449160, "audio": 0, "end": 10474424, "filename": "/lib/python3.6/site-packages/numpy/distutils/command/build_ext.py"}, {"start": 10474424, "audio": 0, "end": 10475522, "filename": "/lib/python3.6/site-packages/numpy/distutils/command/__init__.py"}, {"start": 10475522, "audio": 0, "end": 10477253, "filename": "/lib/python3.6/site-packages/numpy/distutils/command/build_scripts.py"}, {"start": 10477253, "audio": 0, "end": 10481632, "filename": "/lib/python3.6/site-packages/numpy/distutils/command/config_compiler.py"}, {"start": 10481632, "audio": 0, "end": 10483680, "filename": "/lib/python3.6/site-packages/numpy/distutils/command/autodist.py"}, {"start": 10483680, "audio": 0, "end": 10484665, "filename": "/lib/python3.6/site-packages/numpy/distutils/command/install_headers.py"}, {"start": 10484665, "audio": 0, "end": 10498054, "filename": "/lib/python3.6/site-packages/numpy/distutils/command/build_clib.py"}, {"start": 10498054, "audio": 0, "end": 10499672, "filename": "/lib/python3.6/site-packages/numpy/distutils/command/build.py"}, {"start": 10499672, "audio": 0, "end": 10500471, "filename": "/lib/python3.6/site-packages/numpy/distutils/command/sdist.py"}, {"start": 10500471, "audio": 0, "end": 10501681, "filename": "/lib/python3.6/site-packages/numpy/distutils/command/build_py.py"}, {"start": 10501681, "audio": 0, "end": 10519691, "filename": "/lib/python3.6/site-packages/numpy/distutils/command/config.py"}, {"start": 10519691, "audio": 0, "end": 10520678, "filename": "/lib/python3.6/site-packages/numpy/distutils/command/egg_info.py"}, {"start": 10520678, "audio": 0, "end": 10551624, "filename": "/lib/python3.6/site-packages/numpy/distutils/command/build_src.py"}, {"start": 10551624, "audio": 0, "end": 10552939, "filename": "/lib/python3.6/site-packages/numpy/distutils/command/install_clib.py"}, {"start": 10552939, "audio": 0, "end": 10553580, "filename": "/lib/python3.6/site-packages/numpy/distutils/command/develop.py"}, {"start": 10553580, "audio": 0, "end": 10554973, "filename": "/lib/python3.6/site-packages/numpy/distutils/fcompiler/lahey.py"}, {"start": 10554973, "audio": 0, "end": 10594320, "filename": "/lib/python3.6/site-packages/numpy/distutils/fcompiler/__init__.py"}, {"start": 10594320, "audio": 0, "end": 10598429, "filename": "/lib/python3.6/site-packages/numpy/distutils/fcompiler/compaq.py"}, {"start": 10598429, "audio": 0, "end": 10600162, "filename": "/lib/python3.6/site-packages/numpy/distutils/fcompiler/vast.py"}, {"start": 10600162, "audio": 0, "end": 10602770, "filename": "/lib/python3.6/site-packages/numpy/distutils/fcompiler/nag.py"}, {"start": 10602770, "audio": 0, "end": 10604166, "filename": "/lib/python3.6/site-packages/numpy/distutils/fcompiler/g95.py"}, {"start": 10604166, "audio": 0, "end": 10610939, "filename": "/lib/python3.6/site-packages/numpy/distutils/fcompiler/intel.py"}, {"start": 10610939, "audio": 0, "end": 10612719, "filename": "/lib/python3.6/site-packages/numpy/distutils/fcompiler/mips.py"}, {"start": 10612719, "audio": 0, "end": 10614364, "filename": "/lib/python3.6/site-packages/numpy/distutils/fcompiler/sun.py"}, {"start": 10614364, "audio": 0, "end": 10615491, "filename": "/lib/python3.6/site-packages/numpy/distutils/fcompiler/pathf95.py"}, {"start": 10615491, "audio": 0, "end": 10618926, "filename": "/lib/python3.6/site-packages/numpy/distutils/fcompiler/ibm.py"}, {"start": 10618926, "audio": 0, "end": 10623139, "filename": "/lib/python3.6/site-packages/numpy/distutils/fcompiler/pg.py"}, {"start": 10623139, "audio": 0, "end": 10628706, "filename": "/lib/python3.6/site-packages/numpy/distutils/fcompiler/absoft.py"}, {"start": 10628706, "audio": 0, "end": 10629530, "filename": "/lib/python3.6/site-packages/numpy/distutils/fcompiler/none.py"}, {"start": 10629530, "audio": 0, "end": 10630949, "filename": "/lib/python3.6/site-packages/numpy/distutils/fcompiler/hpux.py"}, {"start": 10630949, "audio": 0, "end": 10650712, "filename": "/lib/python3.6/site-packages/numpy/distutils/fcompiler/gnu.py"}], "remote_package_size": 10650712, "package_uuid": "c8ad1e84-2526-4f30-84e3-2a075d42dead"});

})();
