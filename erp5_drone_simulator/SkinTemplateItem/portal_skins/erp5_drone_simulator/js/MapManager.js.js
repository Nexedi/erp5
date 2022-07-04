/// <reference path="./typings/babylon.3.1.d.ts" />
var MapManager = /** @class */ (function () {
    //*************************************************** CONSTRUCTOR **************************************************
    function MapManager(scene) {
        var _this = this;
        var max = GAMEPARAMETERS.mapSize.width;
        if (GAMEPARAMETERS.mapSize.depth > max)
            max = GAMEPARAMETERS.mapSize.depth;
        if (GAMEPARAMETERS.mapSize.height > max)
            max = GAMEPARAMETERS.mapSize.height;
        max = max < GAMEPARAMETERS.mapSize.depth ? GAMEPARAMETERS.mapSize.depth : max;
        // Skybox
        var max_sky = (max * 10 < 20000) ? max * 10 : 20000,
          skybox = BABYLON.Mesh.CreateBox("skyBox", max_sky, scene);
        skybox.infiniteDistance = true;
        skybox.renderingGroupId = 0;
        var skyboxMat = new BABYLON.StandardMaterial("skybox", scene);
        skyboxMat.backFaceCulling = false;
        skyboxMat.disableLighting = true;
        skyboxMat.reflectionTexture = new BABYLON.CubeTexture("./assets/skybox/sky", scene);
        skyboxMat.reflectionTexture.coordinatesMode = BABYLON.Texture.SKYBOX_MODE;
        skyboxMat.infiniteDistance = true;
        skybox.material = skyboxMat;
        // Plane from bottom
        var largeGroundMat = new BABYLON.StandardMaterial("largeGroundMat", scene);
        largeGroundMat.specularColor = BABYLON.Color3.Black();
        largeGroundMat.alpha = 0.4;
        var largeGroundBottom = BABYLON.Mesh.CreatePlane("largeGroundBottom", max * 11, scene);
        largeGroundBottom.position.y = -0.01;
        largeGroundBottom.rotation.x = -Math.PI / 2;
        largeGroundBottom.rotation.y = Math.PI;
        largeGroundBottom.material = largeGroundMat;
        // Camera
        scene.activeCamera.upperRadiusLimit = max * 4;
        // Terrain
        var width = GAMEPARAMETERS.mapSize.width,
          depth = GAMEPARAMETERS.mapSize.depth,
          height = GAMEPARAMETERS.mapSize.height,
          terrain = scene.getMeshByName("terrain001");
        terrain.isVisible = true;
        terrain.position = BABYLON.Vector3.Zero();
        terrain.scaling = new BABYLON.Vector3(depth / 50000, depth / 50000, width / 50000);
        // Goals
        this._rGoal = BABYLON.Mesh.CreateSphere("rightGoal", 32, GAMEPARAMETERS.goalDiameter, scene);
        var rGoalMat = new BABYLON.StandardMaterial("rGoalMat", scene);
        rGoalMat.alpha = 0.0;
        rGoalMat.diffuseColor = BABYLON.Color3.Red();
        this._rGoal.material = rGoalMat;
        this._rGoal.position = new BABYLON.Vector3(GAMEPARAMETERS.goalPositionRightTeam.x, GAMEPARAMETERS.goalPositionRightTeam.y, GAMEPARAMETERS.goalPositionRightTeam.z);
        this._rGoal.computeWorldMatrix(true);
        this._lGoal = BABYLON.Mesh.CreateSphere("leftGoal", 32, GAMEPARAMETERS.goalDiameter, scene);
        goal_x = GAMEPARAMETERS.goalPositionLeftTeam.x;
        goal_y = GAMEPARAMETERS.goalPositionLeftTeam.y;
        goal_z = GAMEPARAMETERS.goalPositionLeftTeam.z;
        this._lGoal.position = new BABYLON.Vector3(goal_x, goal_y, goal_z);
        var lGoalMat = new BABYLON.StandardMaterial("lGoalMat", scene);
        lGoalMat.alpha = 0.0;
        lGoalMat.diffuseColor = BABYLON.Color3.Blue();
        this._lGoal.material = lGoalMat;
        this._lGoal.computeWorldMatrix(true);
        //base is now a boat (special object)
        ObstacleManager.Prefab.rotation = new BABYLON.Vector3(20.4, 0, 0);
        ObstacleManager.Prefab.scaling = new BABYLON.Vector3(15, 15, 15);
        goalPart1 = new ObstacleManager("goal_1", scene);
        goalPart1.setStartingPosition(goal_x, goal_y, goal_z);
        goalPart2 = BABYLON.MeshBuilder.CreateBox("goal_2", { 'size': 1 }, scene);
        goalPart2.position = new BABYLON.Vector3(goal_x - 0.5, goal_y + 1.5, goal_z + 1.5);
        goalPart2.rotation = new BABYLON.Vector3(0, 0, 0);
        goalPart2.scaling =   new BABYLON.Vector3(2, 2, 1.5);
        goalPart3 = BABYLON.MeshBuilder.CreateCylinder("goal_3", {
                        'diameterBottom': 1.5,
                        'diameterTop': 1.5,
                        'height': 1
                    }, scene);
        goalPart3.position = new BABYLON.Vector3(goal_x + 2.5, goal_y + 1.5, goal_z + 1.5);
        goalPart3.rotation = new BABYLON.Vector3(0, 0, 0);
        goalPart3.scaling = new BABYLON.Vector3(1.5, 3.5, 1.5);

        // Obstacles
        var count = 0;
        this._obstacles = [];
        GAMEPARAMETERS.obstacles.forEach(function (obs) {
            var newObj;
            switch (obs.type) {
                case "box":
                    newObj = BABYLON.MeshBuilder.CreateBox("obs_" + count, { 'size': 1 }, scene);
                    break;
                case "cylinder":
                    newObj = BABYLON.MeshBuilder.CreateCylinder("obs_" + count, {
                        'diameterBottom': obs.diameterBottom,
                        'diameterTop': obs.diameterTop,
                        'height': 1
                    }, scene);
                    break;
                case "sphere":
                    newObj = BABYLON.MeshBuilder.CreateSphere("obs_" + count, {
                        'diameterX': obs.scale.x,
                        'diameterY': obs.scale.y,
                        'diameterZ': obs.scale.z
                    }, scene);
                    break;
                case "boat":
                    ObstacleManager.Prefab.rotation = new BABYLON.Vector3(obs.rotation.x, obs.rotation.y, obs.rotation.z);
                    ObstacleManager.Prefab.scaling = new BABYLON.Vector3(obs.scale.x * 2, obs.scale.y * 2, obs.scale.z * 2);
                    newObj = new ObstacleManager("obs_" + count, scene);
                    newObj.setStartingPosition(obs.position.x, obs.position.y, obs.position.z);
                    break;
                default:
                    return;
            }
            newObj["obsType"] = obs.type;
            var convertion = Math.PI / 180;
            if ("position" in obs)
                newObj.position = new BABYLON.Vector3(obs.position.x, obs.position.y, obs.position.z);
            if ("rotation" in obs)
                newObj.rotation = new BABYLON.Vector3(obs.rotation.x * convertion, obs.rotation.y * convertion, obs.rotation.z * convertion);
            if ("scale" in obs)
                newObj.scaling = new BABYLON.Vector3(obs.scale.x, obs.scale.y, obs.scale.z);
            if ("color" in obs) {
              var material = new BABYLON.StandardMaterial(scene);
              material.alpha = 1;
              material.diffuseColor = new BABYLON.Color3(obs.color.r, obs.color.g, obs.color.b);
              newObj.material = material;
            }
            _this._obstacles.push(newObj);
        });
    }
    Object.defineProperty(MapManager.prototype, "lGoal", {
        get: function () { return this._lGoal; },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(MapManager.prototype, "rGoal", {
        get: function () { return this._rGoal; },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(MapManager.prototype, "obstacles", {
        get: function () { return this._obstacles; },
        enumerable: true,
        configurable: true
    });
    return MapManager;
}());
