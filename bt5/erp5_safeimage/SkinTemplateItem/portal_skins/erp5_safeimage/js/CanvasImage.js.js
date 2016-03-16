/* Copyright (c) 2006-2008 MetaCarta, Inc., published under the Clear BSD
 * license.  See http://svn.openlayers.org/trunk/openlayers/license.txt for the
 * full text of the license. */


/**
 * @requires OpenLayers/Tile.js
 */

/**
 * Class: OpenLayers.Tile.CanvasImage
 * Instances of OpenLayers.Tile.CanvasImage are used to manage the image tiles
 * used by various layers.  Create a new image tile with the
 * <OpenLayers.Tile.CanvasImage> constructor.
 *
 * Inherits from:
 *  - <OpenLayers.Tile>
 */
OpenLayers.Tile.CanvasImage = OpenLayers.Class(OpenLayers.Tile, {

    /** 
     * Property: url
     * {String} The URL of the image being requested. No default. Filled in by
     * layer.getURL() function. 
     */
    url: null,
    
    /** 
     * Property: canvasType
     * {OpenLayers.Layer.Grid.ONECANVASPERLAYER|
     * OpenLayers.Layer.Grid.ONECANVASPERTILE} One canvas element per layer or per tile?
     */    
    canvasType: null,
    
    /**
     * APIProperty: crossOriginKeyword
     * The value of the crossorigin keyword to use when loading images. This is
     * only relevant when using <getCanvasContext> for tiles from remote
     * origins and should be set to either 'anonymous' or 'use-credentials'
     * for servers that send Access-Control-Allow-Origin headers with their
     * tiles.
     */
    crossOriginKeyword: null,
    /**
     * APIProperty: crossOriginKeyword
     * The value of the crossorigin keyword to use when loading images. This is
     * only relevant when using <getCanvasContext> for tiles from remote
     * origins and should be set to either 'anonymous' or 'use-credentials'
     * for servers that send Access-Control-Allow-Origin headers with their
     * tiles.
     */
    crossOriginKeyword: null,


    /**
     * Property: frame
     * {DOMElement} The canvas element is appended to the frame.  Any gutter on
     * the canvas will be hidden behind the frame. 
     */ 
    frame: null,
    
    /**
     * Property: isLoading
     * {Boolean} Indicates if the tile is currently waiting on a loading image. 
     */ 
    isLoading: false,
    
    /** 
     * Property: canvas
     * {DOMElement} The canvas element on which the image is drawn.
     */
    canvas: null,
    
    /** 
     * Property: canvasImageData
     * {ImageData} The ImageData object for the canvas.
     */
    canvasImageData: null,
    
    /** 
     * Property: lastImage
     * {Image} The last requested image object. This property is used to make sure
     *      that only the recent image is drawn.
     */
    lastImage: null,
    
    /** 
     * Property: lastBounds
     * {<OpenLayers.Bounds>} The bounds of the last requested image, needed for 
     *      VirtualCanvasImage.displayImage().
     */
    lastBounds: null,
    
    /**
     * Property: isBackBuffer
     * {Boolean} Is this tile a back buffer tile?
     */
    isBackBuffer: false,
        
    /**
     * Property: backBufferTile
     * {<OpenLayers.Tile>} A clone of the tile used to create transition
     *     effects when the tile is moved or changes resolution.
     */
    backBufferTile: null,

    /**
      *Property. transforms
      *JSON file where the transforms are written
      *
      */
    transforms: null,

    /** 
      *Property partialTile
    */
    partialTile: null,

    /**
      *Propperty partialId
      */

    partialId: null,

    /**
      *Property partialAlgorithm
      */
    partialAlgorithm: null,
    
       
    /**
      *Property partialParam1
      */
    partialParam1: null,

    /**
      *Property partialParam2
      */
    partialParam2: null,

    /**
      *Property partialNum
      */
    partialNum: 0,

    /** TBD 3.0 - reorder the parameters to the init function to remove 
     *             URL. the getUrl() function on the layer gets called on 
     *             each draw(), so no need to specify it here.
     * 
     * Constructor: OpenLayers.Tile.Image
     * Constructor for a new <OpenLayers.Tile.Image> instance.
     * 
     * Parameters:
     * layer - {<OpenLayers.Layer>} layer that the tile will go in.
     * position - {<OpenLayers.Pixel>}
     * bounds - {<OpenLayers.Bounds>}
     * url - {<String>} Deprecated. Remove me in 3.0.
     * size - {<OpenLayers.Size>}
     * canvasType - {<OpenLayers.Layer.Grid.ONECANVASPERLAYER|OpenLayers.Layer.Grid.ONECANVASPERTILE>}
     */   
    initialize: function(layer, position, bounds, url, size,transforms, canvasType) {
        OpenLayers.Tile.prototype.initialize.apply(this, arguments);
        this.url = url; //deprecated remove me
        this.canvasType = canvasType;
        this.frame = document.createElement('div'); 
        this.frame.style.overflow = 'hidden'; 
        this.frame.style.position = 'absolute'; 
        this.transforms = transforms;        
        this.events.addEventType("reprojectionProgress");
        this.events.addEventType("filterProgress");
    },

    /** 
     * APIMethod: destroy
     * nullify references to prevent circular references and memory leaks
     */
    destroy: function() {
        if ((this.frame != null) && (this.frame.parentNode == this.layer.div)) {
            this.layer.div.removeChild(this.frame);
        }
        this.frame = null;
        this.lastImage = null;
        this.canvas = null;
        this.canvasContext = null;
        // clean up the backBufferTile if it exists
        if (this.backBufferTile) {
            this.backBufferTile.destroy();
            this.backBufferTile = null;
            this.layer.events.unregister("loadend", this, this.hideBackBuffer);
        }        
        OpenLayers.Tile.prototype.destroy.apply(this, arguments);
    },

    /**
     * Method: clone
     *
     * Parameters:
     * obj - {<OpenLayers.Tile.Image>} The tile to be cloned
     *
     * Returns:
     * {<OpenLayers.Tile.Image>} An exact clone of this <OpenLayers.Tile.Image>
     */
    clone: function (obj) {
        if (obj == null) {
            obj = new OpenLayers.Tile.CanvasImage(this.layer, 
                                            this.position, 
                                            this.bounds, 
                                            this.url, 
                                            this.size,
                                            this.canvasType);        
        } 
        
        //pick up properties from superclass
        obj = OpenLayers.Tile.prototype.clone.apply(this, [obj]);
        
        // a new canvas element should be created for the clone
        obj.canvas = null;
        
        return obj;
    },
    
    /**
     * Method: draw
     * Check that a tile should be drawn, and draw it. Starts a
     * transition if the layer requests one.
     * 
     * Returns:
     * {Boolean} Always returns true.
     */
    draw: function() {
        if (this.layer != this.layer.map.baseLayer && this.layer.reproject) {
            this.bounds = this.getBoundsFromBaseLayer(this.position);
        }
        var drawTile = OpenLayers.Tile.prototype.draw.apply(this, arguments);
        
        if (this.layer.usesTransition()) {
           this.startTransition(drawTile);
        }
       
        if (!drawTile) {
          return;
        }
        
        if (this.isLoading) {
            // if we're already loading, send 'reload' instead of 'loadstart'.
            this.events.triggerEvent("reload"); 
        } else {
            this.isLoading = true;
            this.events.triggerEvent("loadstart");
        }
        return this.renderTile();  
    },
    
    /**
     * Method: renderTile
     * Creates the canvas element and sets the URL.
     * 
     * Returns:
     * {Boolean} Always returns true.
     */
    renderTile: function() {
        if (this.canvas === null) {
            this.initCanvas();
        }    
        
        if (this.layer.async) {
            // Asyncronous image requests call the asynchronous getURL method
            // on the layer to fetch an image that covers 'this.bounds', in the scope of
            // 'this', setting the 'url' property of the layer itself, and running
            // the callback 'positionFrame' when the image request returns.
             this.layer.getURLasync(this.bounds, this, "url", this.positionImage);
        } else {
            // syncronous image requests get the url and position the frame immediately,
            // and don't wait for an image request to come back.
          
          // todo: use different image url for retry, see Util.OpenLayers.Util.onImageLoadError
          
//            // needed for changing to a different server for onload error
//            if (this.layer.url instanceof Array) {
//                this.imgDiv.urls = this.layer.url.slice();
//            }
            this.url = this.layer.getURL(this.bounds);
          
            // position the frame immediately
            this.positionImage(); 
        }
        
        return true;
    },
    
    /**
     * Method: initCanvas
     * Creates the canvas element and appends it to the tile's frame.
     */
    initCanvas: function() {
        var offset = this.layer.imageOffset;
        var size = this.layer.getImageSize(this.bounds);

        // set the opacity on the tile's frame
        if(this.layer.opacity != null) {
            OpenLayers.Util.modifyDOMElement(this.frame, null, null, null,
                                             null, null, null, 
                                             this.layer.opacity);
        }
        
        this.canvas = document.createElement("canvas");
        this.canvasContext = this.canvas.getContext('2d'); 
        this.canvas.width = this.size.w;
        this.canvas.height = this.size.h;
        this.frame.appendChild(this.canvas);
        
        var id = OpenLayers.Util.createUniqueID("OpenLayersCanvas");
        OpenLayers.Util.modifyDOMElement(this.canvas, id, offset, size, "relative", null, null, true);
        
        this.layer.div.appendChild(this.frame);        
    },
    
    /**
     * Method: positionImage
     * Sets the position and size of the tile's frame and
     * canvas element.
     */
    positionImage: function() {
        // if the this layer doesn't exist at the point the image is
        // returned, do not attempt to use it for size computation
      if(this.layer == null) {
            return;
        }           
        
        // position the frame 
        OpenLayers.Util.modifyDOMElement(this.frame, 
                                      null, this.position, this.size);   
        
        // and then update the canvas size // todo: yes?   
        var size = this.layer.getImageSize(this.bounds); // difference between this.size and size?                           
        OpenLayers.Util.modifyDOMElement(this.canvas, null, null, size);    
           
        this.createImage();
    },

    /**
     * Method: createImage
     * Creates the image and starts loading it.
     */
    createImage: function() {
        // first cancel loading the last image
        if (this.lastImage !== null && !this.lastImage.complete) {
            // note that this doesn't cancel loading for WebKit, see https://bugs.webkit.org/show_bug.cgi?id=35377
            this.lastImage.src = '';
        }
        
        var image = new Image();    
        this.lastImage = image;
        this.lastBounds = this.bounds.clone();
        var context = { 
            image: image,
            tile: this,
            viewRequestID: this.layer.map.viewRequestID,
            data: null,
            bounds: this.bounds.clone() // todo: do we still need the bounds? guess no
            //urls: this.layer.url.slice() // todo: for retries?
        };        
        
        var onLoadFunctionProxy = function() {
            this.tile.onLoadFunction(this);    
        };
        
        var onErrorFunctionProxy = function() {
            this.tile.onErrorFunction(this);
        };
       
        var can = document.createElement("canvas");

        var process = false;
        var that = this;
          
             //onLoadFunctionProxy;
        image.onerror = OpenLayers.Function.bind(onErrorFunctionProxy, context);
        image.crossOrigin = ""; 
        image.src = this.url;
        this.getId();
        image.onload = OpenLayers.Function.bind(onLoadFunctionProxy,context);
   },
    
     /**
        Method: getId
       * Used to catch the tile-group and tileid from JSON file
      */
    
    getId: function(){
       aux = this.url.split('/');
       jpg = aux[7].split('.');
       this.partialTile = aux[6];
       this.partialId = jpg[0];
    },

    /**
     * Method: onLoadFunction
     * Called when an image successfully finished loading. Draws the
     * image on the canvas.
     * 
     * Parameters:
     * context - {<Object>} The context from the onload event.
     */
    onLoadFunction: function(context) {
        if ((this.layer === null) ||
                (context.viewRequestID !== this.layer.map.viewRequestID) ||
                (context.image !== this.lastImage)) {
            return;
        }   
        var image = context.image;
        var data = context.data;
        
        if (this.layer.projection.getCode() != this.layer.map.getProjection()) {
            // reproject image
            var sourceCRS = this.layer.projection;
            var targetCRS = this.layer.map.projection;
            var sourceBounds = this.layer.getReprojectedBounds(this.bounds);
            var targetBounds = this.bounds;
            var sourceSize = new OpenLayers.Size(image.width, image.height);
            var targetSize = this.layer.getImageSize(this.bounds);
            image = this.reproject(image, sourceCRS, sourceBounds, sourceSize, 
                                    targetCRS, targetBounds, targetSize);            
        } else {
            this.displayImage(image);
        }
    },
    
    /**
     * Method: displayImage
     * Takes care of resizing the canvas and then draws the 
     * canvas.
     * 
     * Parameters:
     * image - {Image/Canvas} The image to display
     */
    displayImage: function(image) {
        if (this.layer.canvasFilter && !image.filtered) {
            // if a filter is set, apply the filter first and
            // then use the result
            this.filter(image);
            return;
        } 
        
        // reset canvas (for transparent tiles)
        var size = this.layer.getImageSize(this.bounds);
        this.canvas.width = size.w;
        this.canvas.height = size.h;
        
        // when using a backbuffer, force the original tile on top
        var bringToTop = (this.backBufferTile !== null);
        
        // draw the image on the canvas
        this.drawImage(image, null, bringToTop);
        this.canvasImageData = null;
        
        if (this.backBufferTile) {
          this.setBackBuffer(image);
        }   
        this.isLoading = false; 
        this.events.triggerEvent("loadend"); 
    },
    
    /**
     * Method: drawImage
     * Draws the image on the canvas and scales the image
     * if required.
     * 
     * Parameters:
     * image - {<Image>} The image to draw
     * size - {<OpenLayers.Size>} The target size of the image
     * brintToTop - {<Boolean>} Should the tile's frame be forced to be on top?
     */
    drawImage: function(image, size, bringToTop) {
       
        /* canvas_clean created to avoid canvas "dirty" issue */
        try{
              var canvas_clean = document.createElement('canvas'); 
        }catch(ex){
              console.log("Canvas NOT SUPPORTED");
        }
            canvas_clean.width = image.width;
            canvas_clean.height = image.height;
            this.canvas.width = image.width;
            this.canvas.height = image.height;
            ctx = canvas_clean.getContext("2d");          
            ctx.drawImage(image,0,0,image.width,image.height);
        try{      
            data= ctx.getImageData(0,0,image.width,image.height);
        }catch(ex){
            console.log(ex);
        } 
       /* variable repeat is used to assure that differents algorithms could be 
        applied in the same tile. In the future should be modified.*/
       var repeat = 0;
       this.findParams(repeat);
       x = this.applyAlgorithm(data,image.width,image.height);
       while(this.partialNum > 0){
           repeat = 1;
           this.partialNum = this.partialNum-1;
           this.findParams(repeat);
           x = this.applyAlgorithm(x,image.width,image.height);
           repeat--;
      }
 
      try {
          if (size !== null) {
             this.canvasContext.putImageData(x,image.width,image.height);
          }else {
             this.canvasContext.putImageData(x, 0, 0);
          }
          if (bringToTop) {
             this.layer.div.removeChild(this.frame);
             this.layer.div.appendChild(this.frame);
          }
            this.display();
      } 
      catch (exc) {
        console.log('drawImage failed: ' + ((image) ? image.src : image)); // todo
        this.clear();
      }   
    },

    /**
      * Method: findParams
        Get the parameters from JSON 
        transform file.         
      */
     findParams: function(repeat){
         var length = this.transforms.length;
         var again = repeat;
         
         for(i=0; i<length;i++){
           if(again == 0){
             if((this.transforms[i]["tileid"] === this.partialId) && 
                                (this.transforms[i]["tilegroup"] === this.partialTile)){
               this.partialAlgorithm =this.transforms[i]["algorithm"];
               this.partialParam1 = this.transforms[i]["param1"];
               this.partialParam2 = this.transforms[i]["param2"];
               this.partialNum = this.transforms[i]["num"];
               break;
             }
            }else{
              if((this.transforms[i]["tileid"] === this.partialId) && 
                              (this.transforms[i]["tilegroup"] === this.partialTile)){
                if(this.transforms[i]["num"] === this.partialNum){
                  this.partialAlgorithm =this.transforms[i]["algorithm"];
                  this.partialParam1 = this.transforms[i]["param1"];
                  this.partialParam2 = this.transforms[i]["param2"];
                  break;
                } 
              }
           }
         }
      }, 

    /**
      *Method: applyAlgorithm
           Called to process the data
      */
      applyAlgorithm: function(data,width,height){
          switch(this.partialAlgorithm){
              case 'sepia':
                  return sepia(data,width,height);
              case 'brightness':
                  return brightness(data,width,height,this.partialParam1,this.partialParam2);
              case 'noise':
                  return noise(data,width,height);
              case 'posterize':
                  return posterize(data,width,height,this.partialParam1);
              case 'edge':
                  return edges(data,width,height);
              case 'lighten':
                  return lighten(data,width,height,this.partialParam1);
              default:
                  return data;
          }                  
      },

    /**
     * Method: onErrorFunction
     * Called when an image finished loading, but not successfully. 
     * 
     * Parameters:
     * context - {<Object>} The context from the onload event.
     */    
    onErrorFunction: function(context) {
        if (context.image !== this.lastImage) {
            /* Do not trigger 'loadend' when a new image was request
             * for this tile, because then 'reload' was triggered instead
             * of 'loadstart'.
             * If we would trigger 'loadend' now, Grid would get confused about
             * its 'numLoadingTiles'.
             */
            return;
        }
    	
        // retry? with different url?    
        console.log(this.id + ' onErrorFunction: ' + context.image.src); // todo
        this.events.triggerEvent("loadend");
    },
    
    /** 
     * Method: clear
     * Clear the tile of any bounds/position-related data so that it can 
     *     be reused in a new location. Called in <OpenLayers.Tile.draw()>.
     */
    clear: function() {
        // to be implemented by subclasses
        if (this.frame !== null) {
            this.frame.style.display = 'none';
        }
    },
    
    /** 
     * Method: display
     * Display the tile.
     */
    display: function() {
        // to be implemented by subclasses
        if (this.frame !== null) {
            this.frame.style.display = '';
        }
    },
    
    /** 
     * Method: show
     * Show the tile. Called in <OpenLayers.Tile.showTile()>.
     */
    show: function() {},
    
    /** 
     * Method: hide
     * Hide the tile.  To be implemented by subclasses (but never called).
     */
    hide: function() { },
    
    /**
     * Method: startTransition
     * Creates a backbuffer tile (if it does not exist already)
     * and then displays this tile. 
     * 
     * Parameters:
     * drawTile - {<Boolean>} Should the tile be drawn?
     */
    startTransition: function(drawTile) {
       if (drawTile) {
            //we use a clone of this tile to create a double buffer for visual
            //continuity.  The backBufferTile is used to create transition
            //effects while the tile in the grid is repositioned and redrawn
            if (!this.backBufferTile) {
                this.createBackBufferTile();
            }
            // run any transition effects
            this.showBackBufferTile();
        } else {
            // if we aren't going to draw the tile, then the backBuffer should
            // be hidden too!
            if (this.backBufferTile) {
                this.backBufferTile.clear();
            }
        }        
    },
    
    /**
     * Method: createBackBufferTile
     * Create a backbuffer tile from the current tile.
     */
    createBackBufferTile: function() {
        this.backBufferTile = this.clone();
        
        this.backBufferTile.clear();
        this.backBufferTile.isBackBuffer = true;
        this.backBufferTile.initCanvas();
        
        // clear transition back buffer tile only after all tiles in
        // this layer have loaded to avoid visual glitches
        this.layer.events.register("loadend", this, this.hideBackBuffer);       
    },
    
    /**
     * Method: setBackBuffer
     * Stores the loaded image in the backbuffer tile,
     * so that it can be used for the next request.
     * 
     * Parameters:
     * image - {<Image>} The image to use as backbuffer
     */
    setBackBuffer: function(image) {
        if (this.backBufferTile) {
            // store the image, its position, resolution and bounds
            this.backBufferTile.lastImage = image;
            this.backBufferTile.position = this.position;
            this.backBufferTile.bounds = this.bounds;
            this.backBufferTile.size = this.size;
            this.backBufferTile.imageSize = this.layer.getImageSize(this.bounds) || this.size;
            this.backBufferTile.imageOffset = this.layer.imageOffset;
            this.backBufferTile.resolution = this.layer.getResolution();
        } 
    },
    
    /**
     * Method: hideBackBuffer
     */
    hideBackBuffer: function() {
        if (this.backBufferTile) {
            this.backBufferTile.clear();
        }    
    },
    
    /**
     * Method: showBackBufferTile
     * Displays the backbuffer tile. Renders the image of 
     * the last request on the backbuffer canvas, scales the 
     * image to the currrent zoom-level and displays at the canvas 
     * at its new position.
     */
    showBackBufferTile: function() {
        // backBufferTile has to be valid and ready to use
        if (!this.backBufferTile || !this.backBufferTile.lastImage || 
                (this.backBufferTile.lastImage.src === '')) {
            return;
        }
        
        if (!this.backBufferTile.canvas) {
            this.backBufferTile.initCanvas();
        }

        // calculate the ratio of change between the current resolution of the
        // backBufferTile and the layer.  If several animations happen in a
        // row, then the backBufferTile will scale itself appropriately for
        // each request.
        var ratio = 1;
        if (this.backBufferTile.resolution) {
            ratio = this.backBufferTile.resolution / this.layer.getResolution();
        }
        
        // if the resolution is not the same as it was last time (i.e. we are
        // zooming), then we need to adjust the backBuffer tile
        if (this.backBufferTile.resolution &&
                (this.backBufferTile.resolution !== this.layer.getResolution())) {
            if (this.layer.transitionEffect == 'resize') {
                var mapExtent = this.layer.map.getExtent()
                var withinMapExtent = (mapExtent && this.backBufferTile.bounds.intersectsBounds(mapExtent, false));
                
                if (withinMapExtent) {
                    // In this case, we can just immediately resize the 
                    // backBufferTile.
                    var size = new OpenLayers.Size(this.backBufferTile.size.w * ratio, this.backBufferTile.size.h * ratio);
                    
                    this.backBufferTile.setFramePosition(size);
                    
                    var imageSize = this.backBufferTile.imageSize;
                    imageSize = new OpenLayers.Size(imageSize.w * ratio, imageSize.h * ratio);
                    var imageOffset = this.backBufferTile.imageOffset;
                    if (imageOffset) {
                        imageOffset = new OpenLayers.Pixel(imageOffset.x * ratio, imageOffset.y * ratio);
                    }
                    
                    if (!this.isTooBigCanvas(imageSize)) {
                        // set canvas size
                        this.backBufferTile.setCanvasSize(imageSize, imageOffset);
                        
                        var ctx = this.backBufferTile.canvasContext;
                        if (ctx.mozImageSmoothingEnabled) {
                            /* For Firefox images will be smoothed when they are drawn scaled. Smoothing 
                             * creates a semi-transparent border, which looks like a white line. Since
                             * Firefox 3.6 smoothing can be turned off.
                             */
                            ctx.mozImageSmoothingEnabled = false;
                        }
                        this.backBufferTile.drawImage(this.backBufferTile.lastImage, imageSize, true);
                    }
                }
            }
        } else {
            // otherwise, if the resolution has not changed (when panning), display
            // the backbuffer tile at the new position
            if (this.layer.singleTile) {
                this.backBufferTile.setFramePosition(this.size);
                this.backBufferTile.setCanvasSize(this.size, null);
                this.backBufferTile.drawImage(this.backBufferTile.lastImage, this.size, true);
            } else {
                this.backBufferTile.clear();
            }
        }   
    },
    
    /**
     * Method: setFramePosition
     * Sets the frame's position and size.
     * 
     * Parameters:
     * size - {<OpenLayers.Size>} The target size of the frame
     */
    setFramePosition: function(size) {
        var upperLeft = new OpenLayers.LonLat(this.bounds.left, this.bounds.top);
        var px = this.layer.map.getLayerPxFromLonLat(upperLeft);
        OpenLayers.Util.modifyDOMElement(this.frame, null, px, size);
    },
    
    /**
     * Method: setCanvasSize
     * Sets the canvas' size.
     * 
     * Parameters:
     * size - {<OpenLayers.Size>} The target size of the canvas element
     * imageOffset - {<OpenLayers.Pixel>} Offset
     */
    setCanvasSize: function(size, imageOffset) {
        OpenLayers.Util.modifyDOMElement(this.canvas, null, imageOffset, size);
        this.canvas.width = size.w;
        this.canvas.height = size.h;
    },
    
    /** 
     * Method: isTooBigCanvas
     * Used to avoid that the backbuffer canvas gets too big when zooming in very fast.
     * Otherwise drawing the canvas would take too long and lots of memory would be
     * required. 
     */
    isTooBigCanvas: function(size) {
        return size.w > 5000;    
    },

    /**
     * Method: getPixelData
     * Returns the ARGB values of the pixel at the given position. The
     * returned object has the attributes 'a', 'r', 'g' and 'b'.
     * 
     * Parameters:
     * x - {int} x coordinate on the canvas 
     * y - {int} y coordinate on the canvas
     * 
     * Returns:
     * {Object}
     */
    getPixelData: function(x, y) {
        if (this.cancas === null || 
            x >= this.canvas.width || y >= this.canvas.height) {
            return null;
        }
        if (this.canvasContext !== null) {
            if (this.canvasImageData === null) {
                this.canvasImageData = this.canvasContext.getImageData(0, 0, 
                                            this.canvas.width, this.canvas.height);
            }
            return OpenLayers.Tile.CanvasImage.getPixelDataFromImageData(this.canvasImageData, x, y);
        }
        return null;
    },

    /**
     * Method: filter
     * Applies a canvas filter to the image. If 'layer.canvasAsync'
     * is set, the filter is applied in a web worker.
     * 
     * Parameters:
     * image - {Image}
     */    
    filter: function(image) {
        if (!this.layer.canvasAsync || !this.layer.canvasFilter.supportsAsync()) {
            // don't use a web worker, apply the filter in the main script
            var filteredImage = this.layer.canvasFilter.process(image);
            // mark the image as filtered
            filteredImage.filtered = true;
            this.displayImage(filteredImage);
        } else {
            // apply the filter in a web worker
            // called when the filter was applied
            var handlerDone = function(resultCanvas) {
                if (this.tile.lastImage === this.image) {
                    resultCanvas.filtered = true;
                    this.tile.displayImage(resultCanvas);   
                }
            };    
            // called when the web worker reports its progress
            var handlerProgress = function(progress) {
                if (this.tile.lastImage !== this.image) {
                    // only report progress, if the tile is not used
                    // for requesting a new image
                    return;
                }
                var event = {
                    progress: progress,
                    tile: this.tile
                };
                this.tile.events.triggerEvent("filterProgress", event);
            };
            
            // called in case of an error
            var handlerError = function(error) {
                this.error = error;
                this.tile.onErrorFunction(this);
            };
            
            var context = {
                tile: this,
                // use lastImage instead of image,
                // because image may have been reprojected
                image: this.lastImage    
            };
           
            // start the web worker
            this.layer.canvasFilter.processAsync(
                image,
                OpenLayers.Function.bind(handlerDone, context),
                OpenLayers.Function.bind(handlerProgress, context),
                OpenLayers.Function.bind(handlerError, context)
            );
        }   
    },
    
    /**
     * Method: reproject
     * Calls gdalwarp-js to reproject the image.
     * 
     * Parameters:
     * image - {Image}
     * sourceCRS - {<OpenLayers.Projection>}
     * sourceBounds - {<OpenLayers.Bounds>} 
     * sourceSize - {<OpenLayers.Size>} 
     * targetCRS - {<OpenLayers.Projection>} 
     * targetBounds - {<OpenLayers.Bounds>} 
     * targetSize - {<OpenLayers.Size>} 
     * 
     * Returns:
     * {Canvas}
     */
    reproject: function(image, sourceCRS, sourceBounds, sourceSize, 
                                    targetCRS, targetBounds, targetSize) {
        
        var warper = new GDALWarp(image, sourceCRS.proj, sourceBounds, sourceSize, 
                                            targetCRS.proj, targetBounds, targetSize);
        
        if (!this.layer.canvasAsync) {
            this.displayImage(warper.reproject());
        } else {
            var handlerDone = function(resultCanvas) {
                if (this.tile.lastImage === this.image) {
                    this.tile.displayImage(resultCanvas);   
                }
            };    
            
            var handlerProgress = function(progress) {
                if (this.tile.lastImage !== this.image) {
                    // only report progress, if the tile has not
                    // requested a new image
                    return;
                }
                
                var event = {
                    progress: progress,
                    tile: this.tile
                };
                this.tile.events.triggerEvent("reprojectionProgress", event);
            };
            
            var handlerError = function(error) {
                this.error = error;
                this.tile.onErrorFunction(this);
            };
            
            var context = {
                tile: this,
                image: image    
            };
            
            if (this.layer.proj4JSPath === null || 
                this.layer.gdalwarpWebWorkerPath === null) {
                OpenLayers.Console.warn("Trying to reproject layer '" + this.layer.name + "' but" + 
                    "either the path to Proj4JS or to the gdalwarp-js web worker script is not set!"); 
                return;       
            }
            
            warper.reprojectAsync(
                this.layer.proj4JSPath,
                OpenLayers.Function.bind(handlerDone, context),
                OpenLayers.Function.bind(handlerProgress, context),
                OpenLayers.Function.bind(handlerError, context),
                this.layer.proj4JSDefinitions,
                this.layer.gdalwarpWebWorkerPath);
        }          
    },
    
    CLASS_NAME: "OpenLayers.Tile.CanvasImage"
  }
);

/**
 * Method: getPixelDataFromImageData
 * Returns the ARGB values of the pixel at the given position. The
 * returned object has the attributes 'a', 'r', 'g' and 'b'.
 * 
 * Parameters:
 * imageData - {ImageData} the ImageData object
 * x - {int} x coordinate on the canvas 
 * y - {int} y coordinate on the canvas
 * 
 * Returns:
 * {Object}
 */
OpenLayers.Tile.CanvasImage.getPixelDataFromImageData = function(imageData, x, y) {
    return {
        r: OpenLayers.Tile.CanvasImage.getPixelValue(imageData, x, y, 0),
        g: OpenLayers.Tile.CanvasImage.getPixelValue(imageData, x, y, 1),
        b: OpenLayers.Tile.CanvasImage.getPixelValue(imageData, x, y, 2),
        a: OpenLayers.Tile.CanvasImage.getPixelValue(imageData, x, y, 3)
    };    
};
    
/**
 * Method: getPixelValue
 * Returns the red, green, blue or alpha value
 * for the pixel at the given position.
 * 
 * Parameters:
 * imageData - {ImageData} the ImageData object
 * x - {int} x coordinate on the canvas 
 * y - {int} y coordinate on the canvas
 * argb - 0-3 (0: Red, 1: Green, 2: Blue, 3: Alpha)
 * 
 * Returns:
 * {int} 0-255
 */
OpenLayers.Tile.CanvasImage.getPixelValue = function(imageData, x, y, argb) {
    return imageData.data[((y*(imageData.width*4)) + (x*4)) + argb];    
};
