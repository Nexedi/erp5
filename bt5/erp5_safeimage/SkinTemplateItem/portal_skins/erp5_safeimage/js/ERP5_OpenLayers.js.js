function overwrite(C, o) {
        if(typeof o.initialize === "function" &&
            C === C.prototype.initialize) {
            // OL 2.11

            var proto = C.prototype;
            var staticProps = OpenLayers.Util.extend({}, C);

            C = o.initialize;

            C.prototype = proto;
            OpenLayers.Util.extend(C, staticProps);
        }
        OpenLayers.Util.extend(C.prototype, o);
        return C;
    }


OpenLayers.Layer.Grid = overwrite(OpenLayers.Layer.Grid, {
    
    tileClass: OpenLayers.Tile.CanvasImage,
    
    useCanvas: null,

    canvas: null,

    canvasImageData: null,

    backBufferCanvas: null,

    lastResolution: null,

    lastCanvasPosition: null,

    redrawCanvas: false,

    /**
     * APIProperty: canvasFilter
     * {OpenLayers.Tile.CanvasFilter} Only used for ONECANVASPERLAYER and ONECANVASPERTILE. Can be
     *          used to manipulate the pixel data of an image (for example to adjust the
     *          brightness of a tile).
     */
    canvasFilter: null,

    /**
     * APIProperty: canvasAsync
     * {Boolean} If set to true, the canvas filter and the reprojection (for WMS layers)
     *          will be executed in a web worker. Only supported in Chrome 6+.
     */
    canvasAsync: false,

    initialize: function(name, url, params, options) {
        OpenLayers.Layer.HTTPRequest.prototype.initialize.apply(this, 
                                                                 arguments);
        this.grid = [];
        this.tileQueue = [];
      if(!this.useCanvas){
        if (this.removeBackBufferDelay === null) {
            this.removeBackBufferDelay = this.singleTile ? 0 : 2500;
        }
        
        if (this.className === null) {
            this.className = this.singleTile ? 'olLayerGridSingleTile' :
                                               'olLayerGrid';
        }

        if (!OpenLayers.Animation.isNative) {
            this.deferMoveGriddedTiles = OpenLayers.Function.bind(function() {
                this.moveGriddedTiles(true);
                this.moveTimerId = null;
            }, this);
        }
      }else{
            if (this.usesOneCanvasPerLayer()) {
              this.canvas = document.createElement("canvas");
              this.canvas.id = "Canvas_" + this.id;
              this.canvas.style.top = 0;
              this.canvas.style.left = 0;
              this.canvas.style.position = "absolute";
              this.div.appendChild(this.canvas);
             }
      }
    },

    moveTo:function(bounds, zoomChanged, dragging) {

        OpenLayers.Layer.HTTPRequest.prototype.moveTo.apply(this, arguments);

        bounds = bounds || this.map.getExtent();
    
          if(this.useCanvas){
              var forceReTile = !this.grid.length || zoomChanged ||
                                (this.usesOneCanvasPerLayer() && !dragging);

              // total bounds of the tiles
              var tilesBounds = this.getTilesBounds();
          }

          if (bounds != null) {
             
              // if grid is empty or zoom has changed, we *must* re-tile
              if(!this.usesCanvas){ 
                   var forceReTile = !this.grid.length || zoomChanged;
              }else{
                  var forceReTile = !this.grid.length || zoomChanged ||
                                (this.usesOneCanvasPerLayer() && !dragging);
              }
            // total bounds of the tiles
            var tilesBounds = this.getTilesBounds();


              // total bounds of the tiles
              var tilesBounds = this.getTilesBounds();            

              // the new map resolution
             var resolution = this.map.getResolution();

             // the server-supported resolution for the new map resolution
             var serverResolution = this.getServerResolution(resolution);

             if (this.singleTile) {
                
                  // We want to redraw whenever even the slightest part of the 
                  //  current bounds is not contained by our tile.
                  //  (thus, we do not specify partial -- its default is false)

                 if ( forceReTile ||
                       (!dragging && !tilesBounds.containsBounds(bounds))) {

                     // In single tile mode with no transition effect, we insert
                      // a non-scaled backbuffer when the layer is moved. But if
                     // a zoom occurs right after a move, i.e. before the new
                     // image is received, we need to remove the backbuffer, or
                     // an ill-positioned image will be visible during the zoom
                     // transition.

                     if(zoomChanged && this.transitionEffect !== 'resize') {
                          this.removeBackBuffer();
                     }

                     if(!zoomChanged || this.transitionEffect === 'resize') {
                          this.applyBackBuffer(serverResolution);
                    }

                    this.initSingleTile(bounds);
                }
            } else {

                // if the bounds have changed such that they are not even 
                // *partially* contained by our tiles (e.g. when user has 
                // programmatically panned to the other side of the earth on
                // zoom level 18), then moveGriddedTiles could potentially have
                // to run through thousands of cycles, so we want to reTile
                // instead (thus, partial true).  
                forceReTile = forceReTile ||
                    !tilesBounds.intersectsBounds(bounds, {
                        worldBounds: this.map.baseLayer.wrapDateLine &&
                            this.map.getMaxExtent()
                    });

                if(resolution !== serverResolution) {
                    bounds = this.map.calculateBounds(null, serverResolution);
                    if(forceReTile) {
                        // stretch the layer div
                        var scale = serverResolution / resolution;
                        this.transformDiv(scale);
                    }
                } else {
                    // reset the layer width, height, left, top, to deal with
                    // the case where the layer was previously transformed
                    this.div.style.width = '100%';
                    this.div.style.height = '100%';
                    this.div.style.left = '0%';
                    this.div.style.top = '0%';
                }

                if(forceReTile) {
                    if(zoomChanged && this.transitionEffect === 'resize') {
                        this.applyBackBuffer(serverResolution);
                    }
                    this.initGriddedTiles(bounds);
                } else {
                    this.moveGriddedTiles();
                }
           }
        }
      },
    

    /**** Specific functions for Canvas ****/

      /**
     * Method: drawCanvasTile
     * Called when a image finished loading, draws the image
     * on the canvas element.
     * 
     * Parameters:
     * image - {<Image>} The tile to draw
     * bounds - {<OpenLayers.Bounds>} The bounds of the tile.
     */
    drawCanvasTile: function(image, bounds) {
        if (this.dragging) {
            return;
        }

        // if this is the first tile of a render request, move canvas back to 
        // original position and reset background
        this.resetCanvas();

        var upperLeft = new OpenLayers.LonLat(bounds.left, bounds.top);
        var px = this.getLayerPxFromLonLat(upperLeft);

        var ctx = this.canvas.getContext('2d');
        try {
            ctx.drawImage(image, px.x, px.y);
            this.canvasImageData = null;
        } catch (exc) {
            console.log('drawImage failed: ' + image.src); // todo
        }
    },

     /**
     * Method: resetCanvas
     * Moves the canvas element back to its original position and 
     * resets the drawing surface.
     */
    resetCanvas: function() {
        if (this.redrawCanvas) {
            this.redrawCanvas = false;

            // because the layerContainerDiv has shifted position (for non canvas layers), reposition the canvas.
            this.canvas.style.left = -parseInt(this.map.layerContainerDiv.style.left) + "px";
            this.canvas.style.top = -parseInt(this.map.layerContainerDiv.style.top) + "px";

            // clear canvas by reseting the size
            // broken in Chrome 6.0.458.1:
            // http://code.google.com/p/chromium/issues/detail?id=49151
            this.canvas.width = this.map.viewPortDiv.clientWidth;
            this.canvas.height = this.map.viewPortDiv.clientHeight;

            if (this.usesTransition() && this.usesOneCanvasPerLayer()) {
                // store the current resolution and canvas position for transition
                this.lastResolution = this.map.getResolution();
                var canvasPosition = new OpenLayers.Pixel(this.canvas.style.left, this.canvas.style.top);
                this.lastCanvasPosition = this.map.getLonLatFromLayerPx(canvasPosition);
            }
        }
    },

   /**
     * Method: startTransition
     * Start the transition: create a copy of the 
     * canvas element, scale the copy and then draw the copy 
     * back on the original canvas.
     * 
     * Parameters:
     * zoomChanged - {<Boolean>}
     * dragging - {<Boolean>}
     */
    startTransition: function(zoomChanged, dragging) {
        if (!zoomChanged || dragging ||
            (this.lastResolution === null) || (this.lastCanvasPosition === null)) {
            return;
        }

        var ratio = this.lastResolution / this.map.getResolution();
        var px = this.getLayerPxFromLonLat(this.lastCanvasPosition);

        // create a scaled copy of the canvas
        if (this.backBufferCanvas == null) {
            this.backBufferCanvas = document.createElement('canvas');
            this.backBufferCanvas.style.display = 'none';
        }

        this.backBufferCanvas.width = this.canvas.width * ratio;
        this.backBufferCanvas.height = this.canvas.height * ratio;

        var zoomcontext = this.backBufferCanvas.getContext('2d');
        zoomcontext.scale(ratio, ratio);
        zoomcontext.drawImage(this.canvas, 0, 0);

        // and then draw this copy on the original canvas 
        this.resetCanvas();

        var ctx = this.canvas.getContext('2d');
        ctx.drawImage(this.backBufferCanvas, px.x, px.y);
    },

 /**
     * Method: getLayerPxFromLonLat
     * A wrapper for the <OpenLayers.Map.getLayerPxFromLonLat()> method,
     * which takes into account that the canvas element has a fixed size and 
     * it always moved back to the original position.
     * 
     * Parameters:
     * lonlat - {<OpenLayers.LonLat>}
     *
     * Returns:
     * {<OpenLayers.Pixel>} 
     */
    getLayerPxFromLonLat: function(lonlat) {
        if (this.usesOneCanvasPerLayer()) {
           var viewPortPx = this.map.getPixelFromLonLat(lonlat);
           return viewPortPx;
        } else {
            return this.map.getLayerPxFromLonLat(lonlat);
        }
    },

    /**
     * Method: getLayerPxFromLonLat
     * A wrapper for the <OpenLayers.Map.getViewPortPxFromLayerPx()> method.
     * 
     * Parameters:
     * layerPx - {<OpenLayers.Pixel>}
     * 
     * Returns:
     * {<OpenLayers.Pixel>}
     */
    getViewPortPxFromLayerPx: function(layerPx) {
        if (this.usesOneCanvasPerLayer()) {
            return layerPx;
        } else {
            return this.map.getViewPortPxFromLayerPx(layerPx);
        }
    },

   /**
     * Method: usesTransition
     * 
     * Returns:
     * {<Boolean>} True, if the layer uses a supported transition effect.
     */
    usesTransition: function() {
        return true;
        //return (OpenLayers.Util.indexOf(this.SUPPORTED_TRANSITIONS, this.transitionEffect) != -1);
    },

    /**
     * Method: usesOneCanvasPerLayer
     * 
     * Returns:
     * {<Boolean>} True, if the layer renders its tile on a single canvas element.
     */
    usesOneCanvasPerLayer: function() {
        return (this.useCanvas === OpenLayers.Layer.Grid.ONECANVASPERLAYER);
    },

  /**
     * Method: getPixelDataForViewPortPx
     * Returns the ARGB values of the pixel at the given view-port position. 
     * The returned object has the attributes 'a', 'r', 'g' and 'b'.
     * 
     * Parameters:
     * viewPortPx - {<OpenLayers.Pixel>}
     * 
     * Returns:
     * {Object}
     */
    getPixelDataForViewPortPx: function(viewPortPx) {
        if (!this.grid.length || this.grid.length === 0) {
            return null;
        }
        if (this.usesOneCanvasPerLayer()) {
            // for ONECANVASPERLAYER we can directly use the view-port pixels
            var x = viewPortPx.x;
            var y = viewPortPx.y;

            if (this.cancas === null ||
                x < 0 || x >= this.canvas.width ||
                y < 0 || y >= this.canvas.height) {
                return null;
            }

            if (this.canvasImageData === null) {
                var canvasContext = this.canvas.getContext('2d');
                this.canvasImageData = canvasContext.getImageData(0, 0,
                                            this.canvas.width, this.canvas.height);
            }

            return OpenLayers.Tile.CanvasImage.getPixelDataFromImageData(this.canvasImageData, x, y);
     /* for ONECANVASPERTILE we first have to find out the tile
             * which contains the view-port pixel
             */

            // translate the viewPort coordinates to layer coordinates
            var layerPx = this.map.getLayerPxFromViewPortPx(viewPortPx);

            // and then calculate the grid position relative to the layer container
            var upperLeftTile = this.grid[0][0];
            var gridPx = new OpenLayers.Pixel(layerPx.x - upperLeftTile.position.x, layerPx.y - upperLeftTile.position.y);

            // get the tile which covers the pixel
            var tileX = Math.floor(gridPx.x / this.tileSize.w);
            var tileY = Math.floor(gridPx.y / this.tileSize.h);

            if (tileX >= 0 && tileX < this.grid[0].length &&
            tileY >= 0 &&
            tileY < this.grid.length) {

                var tile = this.grid[tileY][tileX];

                // calculate the position of the pixel on the canvas
                var canvasX = gridPx.x - (tileX * this.tileSize.w);
                var canvasY = gridPx.y - (tileY * this.tileSize.h);

                return tile.getPixelData(canvasX, canvasY);
            }
        }

        return null;
    },

});

/**
 * Constant: NOCANVAS
 * {Integer} Constant used to mark that a layer should not be rendered
 *      on a canvas element.
 */
OpenLayers.Layer.Grid.NOCANVAS = 1;
/**
 * Constant: ONECANVASPERLAYER
 * {Integer} Constant used to render the layer on a single canvas element.
 */
OpenLayers.Layer.Grid.ONECANVASPERLAYER = 2;
/**
 * Constant: ONECANVASPERTILE
 * {Integer} Constant used to render every tile in its own canvas element.
 */
OpenLayers.Layer.Grid.ONECANVASPERTILE = 4;

OpenLayers.Layer.Zoomify = overwrite(OpenLayers.Layer.Zoomify,{
    initialize: function(name, url,transforms, size, options) {
        // initilize the Zoomify pyramid for given size
        this.initializeZoomify(size);
        this.transforms = transforms;
        OpenLayers.Layer.Grid.prototype.initialize.apply(this, [
            name, url, size, {}, options
        ]);
    },

    getURL: function (bounds) {
        bounds = this.adjustBounds(bounds);
        var res = this.map.getResolution();
        var x = Math.round((bounds.left - this.tileOrigin.lon) / (res * this.tileSize.w));
        var y = Math.round((this.tileOrigin.lat - bounds.top) / (res * this.tileSize.h));
        var z = this.map.getZoom();
        var tileIndex = x + y * this.tierSizeInTiles[z].w + this.tileCountUpToTier[z];
        var path = "TileGroup" + Math.floor( (tileIndex) / 256 ) +
            "/" + z + "-" + x + "-" + y + "/Base_download";
        var url = this.url;
        if (OpenLayers.Util.isArray(url)) {
            url = this.selectUrl(path, url);
        }
        return url + path;
    },


    addTile: function(bounds,position) {
         return new OpenLayers.Tile.CanvasImage(this,position,bounds,null,this.tileSize,this.transforms,OpenLayers.Tile.CanvasImage.ONECANVASPERTILE);
      }

});

OpenLayers.Tile = overwrite(OpenLayers.Tile,{
    clone: function (obj) {
      if (obj == null) {
        obj = new OpenLayers.Tile(this.layer,
        this.position,
        this.bounds,
        this.url,
        this.size);
      }
      // catch any randomly tagged-on properties
      OpenLayers.Util.applyDefaults(obj, this);
      return obj;
   }
});
