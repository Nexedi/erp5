/// <reference path="./typings/babylon.3.1.d.ts" />
var ObstacleManager = /** @class */ (function () {
    //*************************************************** CONSTRUCTOR **************************************************
    function ObstacleManager(id, scene) {
        // Mesh
        this._mesh = null;
        this._controlMesh = null;
        this._colliderBackMesh = null;
        this._maxOrientation = Math.PI / 4;
        this._scene = scene;
        this._id = id;
        // Create the control mesh
        this._controlMesh = BABYLON.Mesh.CreateBox("obstacleControl_" + id, 0.01, this._scene);
        this._controlMesh.isVisible = false;
        this._controlMesh.rotation = new BABYLON.Vector3(0, Math.PI, 0);
        this._controlMesh.computeWorldMatrix(true);
        // Create the mesh from the obstacle prefab
        console.log("ObstacleManager.Prefab:", ObstacleManager.Prefab);
        this._mesh = ObstacleManager.Prefab.clone("obstacle_" + id, this._controlMesh);
        this._mesh.position = BABYLON.Vector3.Zero();
        this._mesh.isVisible = true;
        this._mesh.computeWorldMatrix(true);
        this._propellerAnimMeshes = [];
    }
    // API
    ObstacleManager.prototype._swapAxe = function (vector) {
        return new BABYLON.Vector3(vector.x, vector.z, vector.y);
    };
    Object.defineProperty(ObstacleManager.prototype, "colliderMesh", {
        //*************************************************** ACCESSOR *****************************************************
        get: function () { return this._mesh; },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(ObstacleManager.prototype, "colliderBackMesh", {
        get: function () { return this._colliderBackMesh; },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(ObstacleManager.prototype, "infosMesh", {
        get: function () { return this._controlMesh; },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(ObstacleManager.prototype, "position", {
        get: function () {
            if (this._controlMesh !== null) {
                return this._swapAxe(this._controlMesh.position);
            }
            return null;
        },
        enumerable: true,
        configurable: true
    });
    //*************************************************** FUNCTIONS ****************************************************
    // -- Starting info
    /**
     * Set the starting position of the obstacle
     * Take x,y,z coordinates as parameters
     */
    ObstacleManager.prototype.setStartingPosition = function (x, y, z) {
        this._controlMesh.position = new BABYLON.Vector3(x, y, z);
        this._controlMesh.computeWorldMatrix(true);
        this._mesh.computeWorldMatrix(true);
    };
    return ObstacleManager;
}());
