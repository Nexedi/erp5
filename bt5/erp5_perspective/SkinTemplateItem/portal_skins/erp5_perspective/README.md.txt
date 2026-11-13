All files besides perspective_base_gadget.* have been created by using webpack with this configuration:

const PerspectivePlugin = require("@finos/perspective-webpack-plugin");

module.exports = {
    entry: "input.js",
    output: {
        filename: "out.js",
        path: "PATH",
    },
    plugins: [new PerspectivePlugin()],
    module: {
        rules: [
            {
                test: require.resolve("@finos/perspective"),
                loader: "expose-loader",
                options: {
                    exposes: ["worker","perspective"],
                },
            },
        ],
    },
};

where input.js:

const perspective = require("@finos/perspective");
-----for perspective_with_viewer-------
const perspective_viewer = require("@finos/perspective-viewer");
const perspective_viewer_datagrid = require("@finos/perspective-viewer-datagrid");
const perspective_viewer_d3fc = require("@finos/perspective-viewer-d3fc");
---------------------------------------

window.Worker = perspective.worker();

To update this, please use a bundler to expose the worker object with window.Worker = worker(). 

perspective.js only includes the perspective.worker() object, perspective_with_viewer also includes the viewer.