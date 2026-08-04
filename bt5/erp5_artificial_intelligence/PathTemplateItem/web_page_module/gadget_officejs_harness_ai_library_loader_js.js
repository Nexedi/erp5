/*global self, fetch, indexedDB, eval */

(function (self) {
  "use strict";

  var LIBRARY_CATALOG = {
    lodash: {
      url: 'https://cdn.jsdelivr.net/npm/lodash@4.17.21/lodash.min.js',
      global: '_',
      description: 'General-purpose utility library (collections, arrays, objects, functions).'
    },
    dayjs: {
      url: 'https://cdn.jsdelivr.net/npm/dayjs@1.11.13/dayjs.min.js',
      global: 'dayjs',
      description: 'Date parsing, manipulation and formatting.'
    },
    papaparse: {
      url: 'https://cdn.jsdelivr.net/npm/papaparse@5.4.1/papaparse.min.js',
      global: 'Papa',
      description: 'CSV/TSV parse and unparse.'
    },
    'js-yaml': {
      url: 'https://cdn.jsdelivr.net/npm/js-yaml@4.1.0/dist/js-yaml.min.js',
      global: 'jsyaml',
      description: 'YAML parse and dump.'
    },
    jszip: {
      url: 'https://cdn.jsdelivr.net/npm/jszip@3.10.1/dist/jszip.min.js',
      global: 'JSZip',
      description: 'Read/write .zip archives.'
    }
  };

  var LIBRARY_DB_NAME = 'gadget_chat_library_cache';
  var LIBRARY_DB_STORE = 'libs';

  function openLibraryDb() {
    return new Promise((resolve, reject) => {
      const req = indexedDB.open(LIBRARY_DB_NAME, 1);
      req.onupgradeneeded = () => { req.result.createObjectStore(LIBRARY_DB_STORE); };
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    });
  }

  function libraryDbGet(db, key) {
    return new Promise((resolve, reject) => {
      const req = db.transaction(LIBRARY_DB_STORE, 'readonly').objectStore(LIBRARY_DB_STORE).get(key);
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    });
  }

  function libraryDbPut(db, key, value) {
    return new Promise((resolve, reject) => {
      const req = db.transaction(LIBRARY_DB_STORE, 'readwrite').objectStore(LIBRARY_DB_STORE).put(value, key);
      req.onsuccess = () => resolve();
      req.onerror = () => reject(req.error);
    });
  }

  /**
   * Resolve a catalog name or a bare https:// URL into a fetchable entry.
   * Catalog entries know their UMD global ahead of time; external URLs don't,
   * so `global` is left null and loadLibraries() auto-detects it after eval.
   * `.mjs` URLs are treated as ES modules (dynamic `import()`), everything
   * else as a classic/UMD script (indirect `eval`).
   */
  function resolveEntry(nameOrUrl) {
    var catalogEntry = LIBRARY_CATALOG[nameOrUrl], file, extension, host;
    if (catalogEntry) {
      return { url: catalogEntry.url, global: catalogEntry.global, description: catalogEntry.description, kind: 'classic' };
    }
    if (!/^https:\/\//.test(nameOrUrl)) {
      throw new Error('unknown library "' + nameOrUrl + '" - use a name from library_list, or an https:// URL');
    }
    file = (nameOrUrl.split('/').pop() || 'library').split('?')[0];
    extension = (file.split('.').pop() || '').toLowerCase();
    try {
      host = new URL(nameOrUrl).host;
    } catch (ignore) {
      host = nameOrUrl;
    }
    return {
      url: nameOrUrl,
      global: null,
      description: 'external library from ' + host,
      kind: extension === 'mjs' ? 'esm' : 'classic'
    };
  }

  /** Fetch (or reuse a cached copy of) an entry's source text, keyed by URL. */
  async function fetchLibrarySource(entry) {
    const db = await openLibraryDb();
    const cached = await libraryDbGet(db, entry.url);
    if (cached) return cached.source;
    const res = await fetch(entry.url);
    if (!res.ok) throw new Error(`fetching "${entry.url}" failed: HTTP ${res.status}`);
    const source = await res.text();
    await libraryDbPut(db, entry.url, { url: entry.url, source, fetched_at: Date.now() });
    return source;
  }

  /**
   * Load libraries by catalog name or https:// URL, attaching each one onto
   * this worker's global scope (`self`) - classic/UMD bundles via indirect
   * `eval` (auto-detecting the global they attached when it isn't already
   * known), ES modules (`.mjs`) via a blob-URL dynamic `import()` - and
   * return a {name: value} map for code that prefers `lib.lodash` over the
   * bare global `_`.
   */
  async function loadLibraries(names) {
    const lib = {};
    for (const name of names || []) {
      const entry = resolveEntry(name);
      const source = await fetchLibrarySource(entry);

      if (entry.kind === 'esm') {
        const blobUrl = URL.createObjectURL(new Blob([source], { type: 'text/javascript' }));
        try {
          const mod = await import(/* webpackIgnore: true */ blobUrl);
          lib[name] = mod.default && Object.keys(mod).length === 1 ? mod.default : mod;
        } finally {
          URL.revokeObjectURL(blobUrl);
        }
        continue;
      }

      if (entry.global) {
        if (self[entry.global] === undefined) {
          (0, eval)(source); // indirect eval: runs as global-scope code, attaches onto self
        }
        lib[name] = self[entry.global];
        continue;
      }

      // Unknown global (external URL): eval and see what appeared, rather
      // than trusting a hard-coded export name.
      const before = Object.keys(self);
      (0, eval)(source);
      const appeared = Object.keys(self).filter((key) => before.indexOf(key) === -1 && self[key] !== undefined);
      if (!appeared.length) {
        throw new Error(`"${name}" attached no detectable global after loading - it may not be a UMD/IIFE `
          + 'bundle (an ES module needs an .mjs URL to be loaded correctly)');
      }
      lib[name] = self[appeared[appeared.length - 1]];
    }
    return lib;
  }

  self.ChatLibraryLoader = { LIBRARY_CATALOG: LIBRARY_CATALOG, resolveEntry: resolveEntry, loadLibraries: loadLibraries };
}(self));
